import csv
from pathlib import Path

from .entities import Mahasiswa


class MahasiswaManager:
    def __init__(self):
        self.data: dict[str, Mahasiswa] = {}
        self.file_csv = Path(__file__).resolve().parent.parent / "mahasiswa.csv"
        self.muat_csv()

    def simpan_csv(self) -> None:
        """Menyimpan seluruh data mahasiswa ke file CSV."""
        with self.file_csv.open("w", newline="", encoding="utf-8-sig") as file:
            kolom = ["nim", "nama", "noHp"]
            writer = csv.DictWriter(file, fieldnames=kolom)
            writer.writeheader()
            for mahasiswa in self.data.values():
                writer.writerow({
                    "nim": mahasiswa.nim,
                    "nama": mahasiswa.nama,
                    "noHp": mahasiswa.noHp,
                })

    def muat_csv(self) -> None:
        """Memuat data mahasiswa dari CSV ke Dictionary."""
        if not self.file_csv.exists():
            return
        with self.file_csv.open("r", newline="", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                nim = row.get("nim", "").strip()
                nama = row.get("nama", "").strip()
                no_hp = row.get("noHp", "").strip()
                if nim and nama and no_hp:
                    self.data[nim] = Mahasiswa(nim, nama, no_hp)

    def tambah(self, nim: str, nama: str, noHp: str) -> bool:
        nim, nama, noHp = nim.strip(), nama.strip(), noHp.strip()
        if not nim or not nama or not noHp or nim in self.data:
            return False
        self.data[nim] = Mahasiswa(nim, nama, noHp)
        self.simpan_csv()
        return True

    def edit(self, nim: str, nama: str, noHp: str) -> bool:
        mhs = self.getByNim(nim)
        if not mhs or not nama.strip() or not noHp.strip():
            return False
        mhs.ubahData(nama.strip(), noHp.strip())
        self.simpan_csv()
        return True

    def hapus(self, nim: str) -> bool:
        mhs = self.getByNim(nim)
        if not mhs or mhs.statusAktifPeminjaman():
            return False
        del self.data[nim]
        self.simpan_csv()
        return True

    def cari(self, kataKunci: str) -> list[Mahasiswa]:
        kunci = kataKunci.strip().casefold()
        return [m for m in self.data.values()
                if kunci in m.nim.casefold() or kunci in m.nama.casefold()]

    def getByNim(self, nim: str) -> Mahasiswa | None:
        return self.data.get(nim)

    def tampilkanSemua(self) -> list[Mahasiswa]:
        return list(self.data.values())