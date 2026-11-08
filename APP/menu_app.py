from datetime import date

from . import tampilan as t
from .entities import KondisiAlat, StatusTransaksi
from .mahasiswa_manager import MahasiswaManager
from .peralatan_manager import PeralatanManager
from .transaksi_manager import TransaksiManager


class MenuApp:
    def __init__(self):
        self.mhsMgr = MahasiswaManager()
        self.alatMgr = PeralatanManager()
        self.trxMgr = TransaksiManager(self.mhsMgr, self.alatMgr)
        self.alatMgr.adaDalamTransaksiAktif = self.trxMgr.adaAlatDalamTransaksiAktif
        self._data_awal()

    def _data_awal(self):
        # Kategori bawaan hanya ditambahkan jika belum tersimpan di CSV.
        # Method tambahKategori() otomatis menyimpan perubahan ke kategori.csv.
        self.alatMgr.tambahKategori("K01", "Alat Komputasi")
        self.alatMgr.tambahKategori("K02", "Alat Jaringan")
        self.alatMgr.tambahKategori("K03", "Alat Multimedia")

    def jalankan(self):
        t.banner("SISTEM PEMINJAMAN PERALATAN LABORATORIUM")
        aksi = {
            "1": self.menuMahasiswa,
            "2": self.menuAlat,
            "3": self.menuTransaksi,
            "4": lambda: self.tampilkanTransaksi(self.trxMgr.tampilSemua()),
            "5": self.menuPengembalian,
            "6": self.cariTransaksi,
            "7": lambda: self.tampilkanAlat(self.alatMgr.daftarTersedia(), "ALAT TERSEDIA"),
            "8": lambda: self.tampilkanAlat(self.alatMgr.daftarDipinjam(), "ALAT SEDANG DIPINJAM"),
            "9": lambda: self.tampilkanAlat(self.alatMgr.daftarRusak(), "ALAT RUSAK / PEMELIHARAAN"),
            "10": self.riwayatMahasiswa,
            "11": self.menuStatistik,
            "12": self.menuPemeliharaan,
        }
        while True:
            t.kotak_menu("MENU UTAMA", [
                ("1", "Kelola data Mahasiswa"),
                ("2", "Kelola data Peralatan"),
                ("3", "Buat Transaksi Peminjaman"),
                ("4", "Tampilkan Transaksi"),
                ("5", "Pengembalian alat"),
                ("6", "Cari transaksi berdasarkan mahasiswa"),
                ("7", "Tampilkan alat tersedia"),
                ("8", "Tampilkan alat sedang dipinjam"),
                ("9", "Tampilkan kondisi alat rusak/pemeliharaan"),
                ("10", "Riwayat peminjaman mahasiswa"),
                ("11", "Statistik peminjaman"),
                ("12", "Selesaikan pemeliharaan alat"),
                ("0", "Keluar"),
            ])
            pilihan = t.tanya_menu()
            if pilihan == "0":
                print()
                t.sukses("Terima kasih. Program selesai.")
                break
            try:
                if pilihan in aksi:
                    aksi[pilihan]()
                else:
                    t.gagal("Pilihan tidak valid.")
            except (ValueError, KeyError) as e:
                t.gagal(f"Input tidak valid: {e}")

    def menuMahasiswa(self):
        while True:
            t.kotak_menu("KELOLA MAHASISWA", [
                ("1", "Tambah"), ("2", "Edit"), ("3", "Hapus"),
                ("4", "Cari"), ("5", "Tampilkan semua"), ("0", "Kembali"),
            ])
            p = t.tanya_menu("Pilih")
            if p == "1":
                nim, nama, hp = t.tanya("NIM"), t.tanya("Nama"), t.tanya("No. HP")
                if self.mhsMgr.tambah(nim, nama, hp):
                    t.sukses("Mahasiswa berhasil ditambahkan.")
                else:
                    t.gagal("Gagal: NIM sudah digunakan atau ada kolom yang kosong.")
            elif p == "2":
                nim = t.tanya("NIM yang diedit")
                nama, hp = t.tanya("Nama baru"), t.tanya("No. HP baru")
                if self.mhsMgr.edit(nim, nama, hp):
                    t.sukses("Data mahasiswa diperbarui.")
                else:
                    t.gagal("Gagal: mahasiswa tidak ditemukan atau ada kolom yang kosong.")
            elif p == "3":
                nim = t.tanya("NIM yang dihapus")
                if self.mhsMgr.hapus(nim):
                    t.sukses("Data mahasiswa dihapus.")
                else:
                    t.gagal("Gagal: tidak ditemukan atau masih punya transaksi aktif.")
            elif p == "4":
                self.tampilkanMahasiswa(self.mhsMgr.cari(t.tanya("Kata kunci NIM/nama")),
                                        "HASIL PENCARIAN MAHASISWA")
            elif p == "5":
                self.tampilkanMahasiswa(self.mhsMgr.tampilkanSemua())
            elif p == "0":
                return
            else:
                t.gagal("Pilihan tidak valid.")

    def menuAlat(self):
        while True:
            t.kotak_menu("KELOLA PERALATAN", [
                ("1", "Tambah alat"), ("2", "Edit alat"), ("3", "Hapus alat"),
                ("4", "Cari alat"), ("5", "Tampilkan semua"),
                ("6", "Tambah kategori"), ("7", "Tampilkan kategori"), ("0", "Kembali"),
            ])
            p = t.tanya_menu("Pilih")
            if p == "1":
                self.tampilkanKategori()
                kode, nama, kat = t.tanya("Kode alat"), t.tanya("Nama alat"), t.tanya("ID kategori")
                if self.alatMgr.tambahAlat(kode, nama, kat):
                    t.sukses("Alat berhasil ditambahkan.")
                else:
                    t.gagal("Gagal: kode sudah ada, kolom kosong, atau kategori tidak ditemukan.")
            elif p == "2":
                kode = t.tanya("Kode alat")
                nama, kat = t.tanya("Nama baru"), t.tanya("ID kategori baru")
                if self.alatMgr.editAlat(kode, nama, kat):
                    t.sukses("Data alat diperbarui.")
                else:
                    t.gagal("Gagal: alat/kategori tidak ditemukan atau alat sedang dipinjam.")
            elif p == "3":
                if self.alatMgr.hapusAlat(t.tanya("Kode alat")):
                    t.sukses("Alat dihapus.")
                else:
                    t.gagal("Gagal: alat tidak ditemukan, sedang dipinjam, atau tercatat pada transaksi aktif.")
            elif p == "4":
                self.tampilkanAlat(self.alatMgr.cariAlat(t.tanya("Cari kode/nama/kategori")),
                                   "HASIL PENCARIAN ALAT")
            elif p == "5":
                self.tampilkanAlat(self.alatMgr.daftarSemua())
            elif p == "6":
                idk, nama = t.tanya("ID kategori baru"), t.tanya("Nama kategori")
                if self.alatMgr.tambahKategori(idk, nama):
                    t.sukses("Kategori ditambahkan.")
                else:
                    t.gagal("Gagal: ID kategori sudah digunakan atau kolom kosong.")
            elif p == "7":
                self.tampilkanKategori()
            elif p == "0":
                return
            else:
                t.gagal("Pilihan tidak valid.")

    def menuTransaksi(self):
        t.subjudul("BUAT TRANSAKSI PEMINJAMAN")
        nim = t.tanya("NIM peminjam")
        mhs = self.mhsMgr.getByNim(nim)
        if mhs is None:
            t.gagal("Mahasiswa tidak ditemukan.")
            return
        t.info(f"Peminjam: {mhs.nama} (transaksi aktif: {mhs.jumlahTransaksiAktif()}/2)")
        self.tampilkanAlat(self.alatMgr.daftarTersedia(), "ALAT TERSEDIA")
        kode_input = t.tanya("Kode alat (pisahkan dengan koma)")
        kode = [x.strip() for x in kode_input.split(",") if x.strip()]
        try:
            lama = int(t.tanya("Lama pinjam (1-7 hari)"))
        except ValueError:
            t.gagal("Lama hari harus berupa angka.")
            return
        trx, pesan = self.trxMgr.buatTransaksi(nim, kode, lama)
        if trx:
            t.sukses(pesan)
            self.tampilkanTransaksi([trx], judul=None)
        else:
            t.gagal(pesan)

    def menuPengembalian(self):
        aktif = [x for x in self.trxMgr.tampilSemua() if x.isAktif()]
        self.tampilkanTransaksi(aktif, "TRANSAKSI AKTIF")
        if not aktif:
            return
        id_trx = t.tanya("ID transaksi").upper()
        trx = self.trxMgr.data.get(id_trx)
        if not trx:
            t.gagal("Transaksi tidak ditemukan.")
            return
        t.subjudul("ALAT YANG BELUM DIKEMBALIKAN")
        t.tabel(["Kode", "Nama alat"],
                [[a.kodeAlat, a.namaAlat] for a in trx.alatBelumKembali()])
        kode = t.tanya("Kode alat yang dikembalikan")
        print("  Kondisi: " + t.warna("1 BAIK", "hijau") + "   "
              + t.warna("2 RUSAK_RINGAN", "kuning") + "   "
              + t.warna("3 RUSAK_BERAT", "merah"))
        mapping = {"1": KondisiAlat.BAIK, "2": KondisiAlat.RUSAK_RINGAN, "3": KondisiAlat.RUSAK_BERAT}
        pilihan = t.tanya("Pilih kondisi")
        if pilihan not in mapping:
            t.gagal("Pilihan kondisi tidak valid.")
            return
        ok, pesan = self.trxMgr.prosesPengembalian(id_trx, kode, mapping[pilihan])
        (t.sukses if ok else t.gagal)(pesan)
        if ok:
            t.info(f"Status transaksi {id_trx}: {trx.status.value}")
            if mapping[pilihan] != KondisiAlat.BAIK:
                t.peringatan(f"Alat {kode} masuk pemeliharaan (menu 12 setelah diperbaiki).")

    def cariTransaksi(self):
        nim = t.tanya("NIM mahasiswa")
        self.tampilkanTransaksi(self.trxMgr.cariByMahasiswa(nim), f"TRANSAKSI MAHASISWA {nim}")

    def riwayatMahasiswa(self):
        nim = t.tanya("NIM mahasiswa")
        self.tampilkanTransaksi(self.trxMgr.riwayatMahasiswa(nim), f"RIWAYAT PEMINJAMAN {nim}")

    def menuStatistik(self):
        s = self.trxMgr.statistik()
        t.subjudul("STATISTIK PEMINJAMAN")
        t.tabel(["Ringkasan", "Jumlah"], [
            ["Total transaksi", len(self.trxMgr.data)],
            ["Transaksi aktif", (str(s["aktif"]), "kuning")],
            ["Transaksi selesai", (str(s["selesai"]), "hijau")],
            ["Mahasiswa terdaftar", len(self.mhsMgr.data)],
            ["Alat terdaftar", len(self.alatMgr.data)],
        ], rata=["kiri", "kanan"])

        def peringkat(judul, kolomId, hitung, namaDari, satuan):
            if not hitung:
                return
            urut = sorted(hitung.items(), key=lambda x: (-x[1], x[0]))[:5]
            tertinggi = urut[0][1]
            t.subjudul(judul)
            t.tabel(["#", kolomId, "Nama", satuan, "Grafik"],
                    [[i, k, namaDari(k), j, t.bar_horizontal(j, tertinggi)]
                     for i, (k, j) in enumerate(urut, 1)],
                    rata=["tengah", "kiri", "kiri", "kanan", "kiri"])

        peringkat("5 ALAT PALING SERING DIPINJAM", "Kode", s["alat"],
                  lambda k: self.alatMgr.data[k].namaAlat if k in self.alatMgr.data else "(dihapus)",
                  "Kali")
        peringkat("5 MAHASISWA PALING SERING MEMINJAM", "NIM", s["mahasiswa"],
                  lambda k: self.mhsMgr.data[k].nama if k in self.mhsMgr.data else "(dihapus)",
                  "Transaksi")
        if not s["alat"]:
            t.kosong("Belum ada transaksi, sehingga belum ada peringkat.")

    def menuPemeliharaan(self):
        dalam_pemeliharaan = [a for a in self.alatMgr.daftarRusak() if a.dalamPemeliharaan]
        self.tampilkanAlat(dalam_pemeliharaan, "ALAT DALAM PEMELIHARAAN")
        if not dalam_pemeliharaan:
            return
        kode = t.tanya("Kode alat yang sudah selesai diperbaiki")
        if self.alatMgr.selesaikanPemeliharaan(kode):
            t.sukses("Alat kembali tersedia.")
        else:
            t.gagal("Alat tidak ditemukan dalam pemeliharaan.")

    def tampilkanMahasiswa(self, daftar, judul="DAFTAR MAHASISWA"):
        t.subjudul(f"{judul} ({len(daftar)})")
        if not daftar:
            t.kosong("Data mahasiswa kosong.")
            return
        t.tabel(["No", "NIM", "Nama", "No. HP", "Transaksi aktif"],
                [[i, m.nim, m.nama, m.noHp,
                  (f"{m.jumlahTransaksiAktif()}/2", "kuning" if m.jumlahTransaksiAktif() else "abu")]
                 for i, m in enumerate(daftar, 1)],
                rata=["tengah", "kiri", "kiri", "kiri", "tengah"])

    def tampilkanKategori(self):
        daftar = list(self.alatMgr.kategori.values())
        t.subjudul(f"KATEGORI ({len(daftar)})")
        if not daftar:
            t.kosong("Belum ada kategori.")
            return
        jumlah = {k.idKategori: 0 for k in daftar}
        for a in self.alatMgr.data.values():
            jumlah[a.kategori.idKategori] = jumlah.get(a.kategori.idKategori, 0) + 1
        t.tabel(["ID", "Nama kategori", "Jumlah alat"],
                [[k.idKategori, k.namaKategori, jumlah[k.idKategori]] for k in daftar],
                rata=["kiri", "kiri", "kanan"])

    @staticmethod
    def _status_alat(a):
        if a.dipinjam:
            return ("DIPINJAM", "kuning")
        if a.dalamPemeliharaan:
            return ("PEMELIHARAAN", "merah")
        if a.isTersedia():
            return ("TERSEDIA", "hijau")
        return (a.kondisi.value, "merah")

    @staticmethod
    def _warna_kondisi(kondisi):
        return {KondisiAlat.BAIK: "hijau", KondisiAlat.RUSAK_RINGAN: "kuning"}.get(kondisi, "merah")

    def tampilkanAlat(self, daftar, judul="DAFTAR ALAT"):
        t.subjudul(f"{judul} ({len(daftar)})")
        if not daftar:
            t.kosong("Tidak ada data alat.")
            return
        t.tabel(["No", "Kode", "Nama alat", "Kategori", "Kondisi", "Status", "Total pinjam"],
                [[i, a.kodeAlat, a.namaAlat, a.kategori.namaKategori,
                  (a.kondisi.value, self._warna_kondisi(a.kondisi)),
                  self._status_alat(a), a.totalDipinjam]
                 for i, a in enumerate(daftar, 1)],
                rata=["tengah", "kiri", "kiri", "kiri", "kiri", "kiri", "kanan"])

    def tampilkanTransaksi(self, daftar, judul="DAFTAR TRANSAKSI"):
        if judul:
            t.subjudul(f"{judul} ({len(daftar)})")
        if not daftar:
            t.kosong("Tidak ada transaksi.")
            return
        warna_status = {StatusTransaksi.DIPINJAM: "kuning",
                        StatusTransaksi.SEBAGIAN_DIKEMBALIKAN: "magenta",
                        StatusTransaksi.SELESAI: "hijau"}
        for trx in daftar:
            terlambat = trx.isAktif() and date.today() > trx.batasKembali
            lencana = t.warna(f"[{trx.status.value}]", warna_status[trx.status], "tebal")
            if terlambat:
                lencana += " " + t.warna(f"[TERLAMBAT {(date.today() - trx.batasKembali).days} HARI]",
                                         "merah", "tebal")
            print(f"\n  {t.warna(trx.idTransaksi, 'tebal', 'cyan')}  {lencana}")
            print(f"  Mahasiswa : {trx.mahasiswa.nim} - {trx.mahasiswa.nama}")
            print(f"  Pinjam    : {trx.tanggalPinjam:%d-%m-%Y}    "
                  f"Batas kembali: {trx.batasKembali:%d-%m-%Y}")
            baris = []
            for i, item in enumerate(trx.daftarItem, 1):
                if item.sudahKembali():
                    baris.append([i, item.alat.kodeAlat, item.alat.namaAlat,
                                  ("Dikembalikan", "hijau"), f"{item.tanggalKembali:%d-%m-%Y}",
                                  (item.kondisiKembali.value, self._warna_kondisi(item.kondisiKembali))])
                else:
                    baris.append([i, item.alat.kodeAlat, item.alat.namaAlat,
                                  ("Masih dipinjam", "kuning"), "-", "-"])
            t.tabel(["No", "Kode", "Nama alat", "Status item", "Tgl kembali", "Kondisi"],
                    baris, rata=["tengah", "kiri", "kiri", "kiri", "tengah", "kiri"])
