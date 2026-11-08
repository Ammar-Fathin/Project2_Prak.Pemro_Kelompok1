import csv
from pathlib import Path

from .entities import Peralatan, Kategori, KondisiAlat


class PeralatanManager:
    def __init__(self):
        self.data: dict[str, Peralatan] = {}
        self.kategori: dict[str, Kategori] = {}
        self.adaDalamTransaksiAktif = lambda kode: False
        self.folder_csv = Path(__file__).resolve().parent.parent
        self.file_kategori = self.folder_csv / "kategori.csv"
        self.file_peralatan = self.folder_csv / "peralatan.csv"
        self.muat_csv()

    def simpan_csv(self) -> None:
        """Menyimpan kategori dan peralatan ke dua file CSV."""

        with self.file_kategori.open("w", newline="", encoding="utf-8-sig") as file:
            kolom = ["idKategori", "namaKategori"]
            writer = csv.DictWriter(file, fieldnames=kolom)
            writer.writeheader()
            for kategori in self.kategori.values():
                writer.writerow({
                    "idKategori": kategori.idKategori,
                    "namaKategori": kategori.namaKategori,
                })

        with self.file_peralatan.open("w", newline="", encoding="utf-8-sig") as file:
            kolom = ["kodeAlat", "namaAlat", "idKategori", "kondisi",
                     "dipinjam", "totalDipinjam", "dalamPemeliharaan"]
            writer = csv.DictWriter(file, fieldnames=kolom)
            writer.writeheader()
            for alat in self.data.values():
                writer.writerow({
                    "kodeAlat": alat.kodeAlat,
                    "namaAlat": alat.namaAlat,
                    "idKategori": alat.kategori.idKategori,
                    "kondisi": alat.kondisi.value,
                    "dipinjam": alat.dipinjam,
                    "totalDipinjam": alat.totalDipinjam,
                    "dalamPemeliharaan": alat.dalamPemeliharaan,
                })

    def muat_csv(self) -> None:
        """Memuat kategori terlebih dahulu, kemudian peralatan."""
        if self.file_kategori.exists():
            with self.file_kategori.open("r", newline="", encoding="utf-8-sig") as file:
                for row in csv.DictReader(file):
                    id_kategori = row.get("idKategori", "").strip()
                    nama = row.get("namaKategori", "").strip()
                    if id_kategori and nama:
                        self.kategori[id_kategori] = Kategori(id_kategori, nama)

        if self.file_peralatan.exists():
            with self.file_peralatan.open("r", newline="", encoding="utf-8-sig") as file:
                for row in csv.DictReader(file):
                    kode = row.get("kodeAlat", "").strip()
                    nama = row.get("namaAlat", "").strip()
                    kategori = self.kategori.get(row.get("idKategori", "").strip())
                    if not kode or not nama or kategori is None:
                        continue
                    try:
                        kondisi = KondisiAlat(row.get("kondisi", KondisiAlat.BAIK.value))
                    except ValueError:
                        kondisi = KondisiAlat.BAIK
                    self.data[kode] = Peralatan(
                        kodeAlat=kode,
                        namaAlat=nama,
                        kategori=kategori,
                        kondisi=kondisi,
                        dipinjam=row.get("dipinjam", "False").lower() == "true",
                        totalDipinjam=int(row.get("totalDipinjam") or 0),
                        dalamPemeliharaan=row.get("dalamPemeliharaan", "False").lower() == "true",
                    )

    def tambahKategori(self, idKategori: str, namaKategori: str) -> bool:
        idKategori, namaKategori = idKategori.strip(), namaKategori.strip()
        if not idKategori or not namaKategori or idKategori in self.kategori:
            return False
        self.kategori[idKategori] = Kategori(idKategori, namaKategori)
        self.simpan_csv()
        return True

    def getKategori(self, idKategori: str) -> Kategori | None:
        return self.kategori.get(idKategori)

    def tambahAlat(self, kode: str, nama: str, idKategori: str) -> bool:
        kode, nama = kode.strip(), nama.strip()
        kategori = self.getKategori(idKategori)
        if not kode or not nama or kode in self.data or not kategori:
            return False
        self.data[kode] = Peralatan(kode, nama, kategori)
        self.simpan_csv()
        return True

    def editAlat(self, kode: str, nama: str, idKategori: str) -> bool:
        alat, kategori = self.data.get(kode), self.getKategori(idKategori)
        if not alat or not kategori or not nama.strip() or alat.dipinjam:
            return False
        alat.ubahData(nama.strip(), kategori)
        self.simpan_csv()
        return True

    def hapusAlat(self, kode: str) -> bool:
        alat = self.data.get(kode)
        if not alat or alat.dipinjam or self.adaDalamTransaksiAktif(kode):
            return False
        del self.data[kode]
        self.simpan_csv()
        return True

    def cariAlat(self, kataKunci: str) -> list[Peralatan]:
        kunci = kataKunci.strip().casefold()
        return [a for a in self.data.values()
                if kunci in a.kodeAlat.casefold()
                or kunci in a.namaAlat.casefold()
                or kunci in a.kategori.namaKategori.casefold()]

    def daftarTersedia(self) -> list[Peralatan]:
        return [a for a in self.data.values() if a.isTersedia()]

    def daftarDipinjam(self) -> list[Peralatan]:
        return [a for a in self.data.values() if a.dipinjam]

    def daftarRusak(self) -> list[Peralatan]:
        return [a for a in self.data.values()
                if a.kondisi != KondisiAlat.BAIK or a.dalamPemeliharaan]

    def daftarSemua(self) -> list[Peralatan]:
        return list(self.data.values())

    def selesaikanPemeliharaan(self, kode: str) -> bool:
        alat = self.data.get(kode)
        if not alat or not alat.dalamPemeliharaan or alat.dipinjam:
            return False
        alat.kondisi = KondisiAlat.BAIK
        alat.dalamPemeliharaan = False
        self.simpan_csv()
        return True
