from datetime import date
from enum import Enum
from typing import Optional


class StatusTransaksi(Enum):
    DIPINJAM = "DIPINJAM"
    SEBAGIAN_DIKEMBALIKAN = "SEBAGIAN_DIKEMBALIKAN"
    SELESAI = "SELESAI"


class KondisiAlat(Enum):
    BAIK = "BAIK"
    RUSAK_RINGAN = "RUSAK_RINGAN"
    RUSAK_BERAT = "RUSAK_BERAT"


class Kategori:
    idKategori: str
    namaKategori: str

    def __init__(self, idKategori: str, namaKategori: str):
        self.idKategori = idKategori
        self.namaKategori = namaKategori

    def getNama(self) -> str:
        return self.namaKategori


class Mahasiswa:
    nim: str
    nama: str
    noHp: str
    transaksiAktif: list[str]

    def __init__(self, nim: str, nama: str, noHp: str,
                 transaksiAktif: Optional[list[str]] = None):
        self.nim = nim
        self.nama = nama
        self.noHp = noHp
        self.transaksiAktif = transaksiAktif if transaksiAktif is not None else []

    def statusAktifPeminjaman(self) -> bool:
        return bool(self.transaksiAktif)

    def jumlahTransaksiAktif(self) -> int:
        return len(self.transaksiAktif)

    def bisaMeminjam(self) -> bool:
        return self.jumlahTransaksiAktif() < 2

    def tambahTransaksiAktif(self, idTrx: str) -> None:
        if idTrx not in self.transaksiAktif:
            self.transaksiAktif.append(idTrx)

    def hapusTransaksiAktif(self, idTrx: str) -> None:
        if idTrx in self.transaksiAktif:
            self.transaksiAktif.remove(idTrx)

    def ubahData(self, nama: str, noHp: str) -> None:
        self.nama, self.noHp = nama, noHp


class Peralatan:
    kodeAlat: str
    namaAlat: str
    kategori: Kategori
    kondisi: KondisiAlat
    dipinjam: bool
    totalDipinjam: int
    dalamPemeliharaan: bool

    def __init__(self, kodeAlat: str, namaAlat: str, kategori: Kategori,
                 kondisi: KondisiAlat = KondisiAlat.BAIK,
                 dipinjam: bool = False, totalDipinjam: int = 0,
                 dalamPemeliharaan: bool = False):
        self.kodeAlat = kodeAlat
        self.namaAlat = namaAlat
        self.kategori = kategori
        self.kondisi = kondisi
        self.dipinjam = dipinjam
        self.totalDipinjam = totalDipinjam
        self.dalamPemeliharaan = dalamPemeliharaan

    def isTersedia(self) -> bool:
        return (self.kondisi == KondisiAlat.BAIK and not self.dipinjam
                and not self.dalamPemeliharaan)

    def tandaiDipinjam(self) -> None:
        self.dipinjam = True
        self.totalDipinjam += 1

    def terimaKembali(self, kondisi: KondisiAlat) -> None:
        self.dipinjam = False
        self.kondisi = kondisi
        self.dalamPemeliharaan = kondisi != KondisiAlat.BAIK

    def ubahData(self, nama: str, kategori: Kategori) -> None:
        self.namaAlat, self.kategori = nama, kategori


class ItemPinjam:
    alat: Peralatan
    tanggalKembali: Optional[date]
    kondisiKembali: Optional[KondisiAlat]

    def __init__(self, alat: Peralatan,
                 tanggalKembali: Optional[date] = None,
                 kondisiKembali: Optional[KondisiAlat] = None):
        self.alat = alat
        self.tanggalKembali = tanggalKembali
        self.kondisiKembali = kondisiKembali

    def sudahKembali(self) -> bool:
        return self.tanggalKembali is not None

    def kembalikan(self, kondisi: KondisiAlat, tanggal: date) -> None:
        if self.sudahKembali():
            raise ValueError("Alat ini sudah tercatat dikembalikan.")
        self.kondisiKembali = kondisi
        self.tanggalKembali = tanggal
        self.alat.terimaKembali(kondisi)


class Transaksi:
    idTransaksi: str
    mahasiswa: Mahasiswa
    daftarItem: list[ItemPinjam]
    tanggalPinjam: date
    batasKembali: date
    status: StatusTransaksi

    def __init__(self, idTransaksi: str, mahasiswa: Mahasiswa,
                 daftarItem: list[ItemPinjam], tanggalPinjam: date,
                 batasKembali: date,
                 status: StatusTransaksi = StatusTransaksi.DIPINJAM):
        self.idTransaksi = idTransaksi
        self.mahasiswa = mahasiswa
        self.daftarItem = daftarItem
        self.tanggalPinjam = tanggalPinjam
        self.batasKembali = batasKembali
        self.status = status

    def tambahItem(self, alat: Peralatan) -> None:
        self.daftarItem.append(ItemPinjam(alat))

    def isAktif(self) -> bool:
        return self.status != StatusTransaksi.SELESAI

    def memuatAlat(self, kodeAlat: str) -> bool:
        return any(i.alat.kodeAlat == kodeAlat and not i.sudahKembali()
                   for i in self.daftarItem)

    def alatBelumKembali(self) -> list[Peralatan]:
        return [i.alat for i in self.daftarItem if not i.sudahKembali()]

    def perbaruiStatus(self) -> None:
        belum = sum(not i.sudahKembali() for i in self.daftarItem)
        sudah = len(self.daftarItem) - belum
        if belum == 0:
            self.status = StatusTransaksi.SELESAI
            self.mahasiswa.hapusTransaksiAktif(self.idTransaksi)
        elif sudah:
            self.status = StatusTransaksi.SEBAGIAN_DIKEMBALIKAN
        else:
            self.status = StatusTransaksi.DIPINJAM
