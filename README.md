# Sistem Peminjaman Alat LAB

Aplikasi terminal (CLI) untuk mengelola peminjaman alat laboratorium. Dibuat dengan Python memakai konsep OOP, `dict`, `list`, dan modul `csv`.

| Tahap | Penyimpanan data | Keterangan |
|-------|------------------|------------|
| **Proyek 1** | Sementara (memori) | Data hilang saat program ditutup |
| **Proyek 2** | Permanen (file CSV) | Data tetap ada saat program dibuka lagi |

---

## 1. Anggota Kelompok

| No | Nama                    | NIM      |
|----|-------------------------|----------|
| 1  | Fathma Daniswara T.P    | K3525060 |
| 2  | Muhammad Ammar Fathin   | K3525065 |
| 3  | Sheva Jalu Atmaja       | K3525073 |

---

## 2. Deskripsi Sistem

Sistem ini membantu pengelola lab mencatat mahasiswa, alat, serta peminjaman dan pengembalian alat lewat menu bernomor di terminal.

**Fitur utama**
- **Mahasiswa:** tambah, ubah, hapus, cari, dan tampilkan. NIM harus unik. Mahasiswa yang masih punya transaksi aktif tidak bisa dihapus.
- **Alat dan kategori:** tambah, ubah, hapus, cari, dan tampilkan. Kategori bawaan: `K01` Alat Komputasi, `K02` Alat Jaringan, `K03` Alat Multimedia.
- **Peminjaman:** satu transaksi bisa memuat banyak alat. Lama pinjam 1–7 hari, maksimal 2 transaksi aktif per mahasiswa, dan ID dibuat otomatis (`TRX001`, `TRX002`, ...).
- **Pengembalian:** alat dikembalikan satu per satu dengan kondisi `BAIK`, `RUSAK_RINGAN`, atau `RUSAK_BERAT`. Status transaksi berubah otomatis: `DIPINJAM` → `SEBAGIAN_DIKEMBALIKAN` → `SELESAI`. Transaksi yang lewat batas ditandai `TERLAMBAT`.
- **Pemeliharaan:** alat yang dikembalikan dalam keadaan rusak tidak bisa dipinjam sampai diselesaikan lewat menu pemeliharaan.
- **Laporan:** daftar alat tersedia/dipinjam/rusak, riwayat per mahasiswa, dan statistik (5 alat dan 5 mahasiswa paling sering meminjam).

---

## 3. Struktur Program

```text
Project1_Prak.Pemro_Kelompok1/
├── main.py                  # titik masuk aplikasi
├── README.md
├── App/
│   ├── entities.py          # model data dan enum
│   ├── mahasiswa_manager.py # kelola mahasiswa + CSV
│   ├── peralatan_manager.py # kelola alat dan kategori + CSV
│   ├── transaksi_manager.py # peminjaman, pengembalian, statistik + CSV
│   ├── tampilan.py          # tampilan terminal
│   └── menu_app.py          # menu dan alur aplikasi
├── mahasiswa.csv            # dibuat otomatis
├── kategori.csv             # dibuat otomatis
├── peralatan.csv            # dibuat otomatis
└── transaksi.csv            # dibuat otomatis
```

Hubungan antar class:

```text
MenuApp
 ├── MahasiswaManager ──► Mahasiswa
 ├── PeralatanManager ──► Peralatan ──► Kategori
 └── TransaksiManager ──► Transaksi ──► ItemPinjam ──► Peralatan
                              └──────► Mahasiswa
```

Menu utama: **1** Kelola mahasiswa, **2** Kelola peralatan, **3** Buat transaksi, **4** Tampilkan transaksi, **5** Pengembalian alat, **6** Cari transaksi per mahasiswa, **7** Alat tersedia, **8** Alat dipinjam, **9** Alat rusak/pemeliharaan, **10** Riwayat mahasiswa, **11** Statistik, **12** Selesaikan pemeliharaan, **0** Keluar.

---

## 4. Cara Menjalankan

**Syarat:** Python 3.10 atau lebih baru.

1. Buka terminal di folder yang berisi `main.py`.
2. Jalankan:
   ```bash
   python main.py
   ```
   (atau `python3 main.py` di Linux/macOS)
3. Pilih menu dengan mengetik nomor lalu tekan **Enter**. Ketik `0` untuk keluar.

Contoh alur: tambah mahasiswa (menu 1) → tambah alat (menu 2) → buat transaksi (menu 3) → kembalikan alat (menu 5) → lihat statistik (menu 11). Setelah program ditutup dan dibuka lagi, semua data tetap ada.

---

## 5. Dari Penyimpanan Sementara ke Permanen

**Sebelumnya (Proyek 1).** Semua data disimpan di memori dalam `dict`. Cara ini sederhana, tetapi data hilang setiap program ditutup sehingga harus diinput ulang.

**Sekarang (Proyek 2).** Data disimpan ke file CSV. Setiap manager mendapat dua method baru, tanpa mengubah aturan dan menu yang sudah ada:

| Method | Fungsi |
|--------|--------|
| `muat_csv()` | Membaca CSV saat program dibuka, lalu mengisi `dict` |
| `simpan_csv()` | Menulis isi `dict` ke CSV setiap ada perubahan yang berhasil |

Karena disimpan setiap ada perubahan (bukan hanya saat keluar), data tetap aman walaupun program tertutup paksa.

**File CSV** (disimpan di folder yang sama dengan `main.py`, tidak membuat folder baru):

| File | Isi |
|------|-----|
| `mahasiswa.csv` | NIM, nama, no. HP |
| `kategori.csv` | ID dan nama kategori |
| `peralatan.csv` | Data alat, kategori, kondisi, status pinjam, jumlah pinjam, status pemeliharaan |
| `transaksi.csv` | Data transaksi, satu baris untuk setiap alat yang dipinjam |

`kategori.csv` dan `peralatan.csv` muncul saat program pertama dijalankan (kategori bawaan langsung disimpan). `mahasiswa.csv` dan `transaksi.csv` muncul setelah ada data pertama.

## 6. Pembagian Kontribusi Anggota

| Nama | NIM | Kontribusi |
|------|-----|------------|
| Fathma Daniswara T.P | K3525060 | `peralatan_manager.py` |
| Muhammad Ammar Fathin | K3525065 | `mahasiswa_manager.py` |
| Sheva Jalu Atmaja | K3525073 | `transaksi_manager.py` |