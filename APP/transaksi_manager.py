import csv
from collections import OrderedDict
from datetime import date, timedelta
from pathlib import Path

from .entities import Transaksi, ItemPinjam, StatusTransaksi, KondisiAlat


class TransaksiManager:
    def __init__(self, mahasiswaMgr, alatMgr):
        self.data: dict[str, Transaksi] = {}
        self.mhsMgr = mahasiswaMgr
        self.alatMgr = alatMgr
        self.counter = 1
        self.file_csv = Path(__file__).resolve().parent.parent / "transaksi.csv"
        self.muat_csv()

    def simpan_csv(self) -> None:
        """Menyimpan transaksi; satu baris CSV mewakili satu item alat."""
        kolom = ["idTransaksi", "nim", "tanggalPinjam", "batasKembali",
                 "status", "kodeAlat", "tanggalKembali", "kondisiKembali"]
        with self.file_csv.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=kolom)
            writer.writeheader()
            for trx in self.data.values():
                for item in trx.daftarItem:
                    writer.writerow({
                        "idTransaksi": trx.idTransaksi,
                        "nim": trx.mahasiswa.nim,
                        "tanggalPinjam": trx.tanggalPinjam.isoformat(),
                        "batasKembali": trx.batasKembali.isoformat(),
                        "status": trx.status.value,
                        "kodeAlat": item.alat.kodeAlat,
                        "tanggalKembali": item.tanggalKembali.isoformat() if item.tanggalKembali else "",
                        "kondisiKembali": item.kondisiKembali.value if item.kondisiKembali else "",
                    })

    def muat_csv(self) -> None:
        """Membangun kembali objek transaksi dan relasinya dari CSV."""
        if not self.file_csv.exists():
            return

        transaksi_sementara = OrderedDict()
        with self.file_csv.open("r", newline="", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                id_trx = row.get("idTransaksi", "").strip()
                mahasiswa = self.mhsMgr.getByNim(row.get("nim", "").strip())
                alat = self.alatMgr.data.get(row.get("kodeAlat", "").strip())
                if not id_trx or mahasiswa is None or alat is None:
                    continue

                if id_trx not in transaksi_sementara:
                    try:
                        tanggal_pinjam = date.fromisoformat(row["tanggalPinjam"])
                        batas_kembali = date.fromisoformat(row["batasKembali"])
                        status = StatusTransaksi(row["status"])
                    except (ValueError, KeyError):
                        continue
                    transaksi_sementara[id_trx] = Transaksi(
                        idTransaksi=id_trx,
                        mahasiswa=mahasiswa,
                        daftarItem=[],
                        tanggalPinjam=tanggal_pinjam,
                        batasKembali=batas_kembali,
                        status=status,
                    )

                tanggal_kembali = None
                kondisi_kembali = None
                if row.get("tanggalKembali"):
                    try:
                        tanggal_kembali = date.fromisoformat(row["tanggalKembali"])
                        kondisi_kembali = KondisiAlat(row["kondisiKembali"])
                    except ValueError:
                        tanggal_kembali = None
                        kondisi_kembali = None

                transaksi_sementara[id_trx].daftarItem.append(
                    ItemPinjam(alat, tanggal_kembali, kondisi_kembali)
                )

        self.data = dict(transaksi_sementara)
        for trx in self.data.values():
            if trx.isAktif():
                trx.mahasiswa.tambahTransaksiAktif(trx.idTransaksi)
            for item in trx.daftarItem:
                # Status alat diselaraskan dengan riwayat item transaksi.
                if not item.sudahKembali():
                    item.alat.dipinjam = True
                else:
                    item.alat.dipinjam = False
                    if item.kondisiKembali is not None:
                        item.alat.kondisi = item.kondisiKembali
                        item.alat.dalamPemeliharaan = item.kondisiKembali != KondisiAlat.BAIK

        nomor = [int(id_trx[3:]) for id_trx in self.data
                 if id_trx.startswith("TRX") and id_trx[3:].isdigit()]
        self.counter = max(nomor, default=0) + 1
        # Simpan ulang agar status alat yang telah direkonstruksi konsisten.
        self.alatMgr.simpan_csv()

    def buatTransaksi(self, nim: str, listKodeAlat: list[str], lamaHari: int = 7):
        mahasiswa = self.mhsMgr.getByNim(nim)
        if mahasiswa is None:
            return None, "Mahasiswa tidak ditemukan."
        if not mahasiswa.bisaMeminjam():
            return None, "Mahasiswa sudah memiliki maksimal 2 transaksi aktif."
        if not listKodeAlat:
            return None, "Pilih minimal satu alat."
        if len(set(listKodeAlat)) != len(listKodeAlat):
            return None, "Kode alat tidak boleh duplikat dalam satu transaksi."
        if not isinstance(lamaHari, int) or not 1 <= lamaHari <= 7:
            return None, "Lama peminjaman harus antara 1 sampai 7 hari."

        alat_dipilih = []
        for kode in listKodeAlat:
            alat = self.alatMgr.data.get(kode)
            if alat is None:
                return None, f"Alat {kode} tidak ditemukan."
            if not alat.isTersedia():
                return None, f"Alat {kode} tidak tersedia untuk dipinjam."
            alat_dipilih.append(alat)

        hari_ini = date.today()
        id_trx = f"TRX{self.counter:03d}"
        transaksi = Transaksi(
            idTransaksi=id_trx, mahasiswa=mahasiswa,
            daftarItem=[ItemPinjam(a) for a in alat_dipilih],
            tanggalPinjam=hari_ini, batasKembali=hari_ini + timedelta(days=lamaHari)
        )
        self.data[id_trx] = transaksi
        self.counter += 1
        mahasiswa.tambahTransaksiAktif(id_trx)
        for alat in alat_dipilih:
            alat.tandaiDipinjam()

        self.simpan_csv()
        self.alatMgr.simpan_csv()
        return transaksi, "Transaksi berhasil dibuat."

    def prosesPengembalian(self, idTrx: str, kodeAlat: str, kondisi: KondisiAlat):
        transaksi = self.data.get(idTrx)
        if transaksi is None or not transaksi.isAktif():
            return False, "Transaksi aktif tidak ditemukan."
        if not isinstance(kondisi, KondisiAlat):
            return False, "Kondisi alat tidak valid."
        for item in transaksi.daftarItem:
            if item.alat.kodeAlat == kodeAlat and not item.sudahKembali():
                item.kembalikan(kondisi, date.today())
                transaksi.perbaruiStatus()
                self.simpan_csv()
                self.alatMgr.simpan_csv()
                return True, "Pengembalian alat berhasil dicatat."
        return False, "Alat tidak ditemukan pada transaksi atau sudah dikembalikan."

    def tampilSemua(self) -> list[Transaksi]:
        return list(self.data.values())

    def cariByMahasiswa(self, nim: str) -> list[Transaksi]:
        return [t for t in self.data.values() if t.mahasiswa.nim == nim]

    def riwayatMahasiswa(self, nim: str) -> list[Transaksi]:
        return self.cariByMahasiswa(nim)

    def adaAlatDalamTransaksiAktif(self, kodeAlat: str) -> bool:
        return any(t.isAktif() and any(i.alat.kodeAlat == kodeAlat for i in t.daftarItem)
                   for t in self.data.values())

    def statistik(self) -> dict:
        hitung_alat, hitung_mhs = {}, {}
        for trx in self.data.values():
            nim = trx.mahasiswa.nim
            hitung_mhs[nim] = hitung_mhs.get(nim, 0) + 1
            for item in trx.daftarItem:
                kode = item.alat.kodeAlat
                hitung_alat[kode] = hitung_alat.get(kode, 0) + 1
        return {
            "alat": hitung_alat,
            "mahasiswa": hitung_mhs,
            "selesai": sum(t.status == StatusTransaksi.SELESAI for t in self.data.values()),
            "aktif": sum(t.isAktif() for t in self.data.values()),
        }
