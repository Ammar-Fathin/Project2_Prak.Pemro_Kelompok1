import os
import sys

LEBAR = 72

_WARNA_AKTIF = sys.stdout.isatty() and "NO_COLOR" not in os.environ
if _WARNA_AKTIF and os.name == "nt":
    os.system("")

_KODE = {
    "tebal": "1", "merah": "31", "hijau": "32", "kuning": "33",
    "biru": "34", "magenta": "35", "cyan": "36", "abu": "90",
}


def warna(teks: str, *gaya: str) -> str:
    if not _WARNA_AKTIF or not gaya:
        return teks
    return f"\033[{';'.join(_KODE[g] for g in gaya)}m{teks}\033[0m"


def sukses(pesan: str) -> None:
    print(warna(f"  ✔ {pesan}", "hijau"))


def gagal(pesan: str) -> None:
    print(warna(f"  ✘ {pesan}", "merah"))


def peringatan(pesan: str) -> None:
    print(warna(f"  ! {pesan}", "kuning"))


def info(pesan: str) -> None:
    print(warna(f"  ℹ {pesan}", "cyan"))


def kosong(pesan: str) -> None:
    print(warna(f"  (i) {pesan}", "abu"))


def banner(judul: str, subjudul: str = "") -> None:
    dalam = LEBAR - 2
    print()
    print(warna("╔" + "═" * dalam + "╗", "cyan"))
    print(warna("║", "cyan") + warna(judul.center(dalam), "tebal") + warna("║", "cyan"))
    if subjudul:
        print(warna("║", "cyan") + warna(subjudul.center(dalam), "abu") + warna("║", "cyan"))
    print(warna("╚" + "═" * dalam + "╝", "cyan"))


def subjudul(teks: str) -> None:
    sisa = max(LEBAR - len(teks) - 5, 3)
    print("\n" + warna(f"── {teks} " + "─" * sisa, "cyan", "tebal"))


def kotak_menu(judul: str, butir: list[tuple[str, str]]) -> None:
    """Cetak menu berkotak. butir = [(nomor, label), ...]; nomor '0' dibuat redup."""
    isi = [f"[{n}] {label}" for n, label in butir]
    lebar = max(len(judul) + 2, *(len(t) for t in isi)) + 2
    print()
    print(warna("┌─ " + judul + " " + "─" * (lebar - len(judul) - 3) + "┐", "cyan", "tebal"))
    for (n, label), teks in zip(butir, isi):
        pad = " " * (lebar - len(teks) - 1)
        nomor = warna(f"[{n}]", "abu" if n == "0" else "kuning")
        print(warna("│", "cyan") + " " + nomor + " " + label + pad + warna("│", "cyan"))
    print(warna("└" + "─" * lebar + "┘", "cyan"))


def _teks(sel) -> str:
    return sel[0] if isinstance(sel, tuple) else str(sel)


def _gaya(sel) -> tuple:
    if not isinstance(sel, tuple):
        return ()
    g = sel[1]
    return (g,) if isinstance(g, str) else tuple(g)


def tabel(kolom: list[str], baris: list[list], rata: list[str] | None = None,
          indent: int = 2) -> None:
    """Cetak tabel berbingkai. Sel dapat berupa teks atau (teks, gaya_warna)."""
    rata = rata or ["kiri"] * len(kolom)
    lebar = [max([len(k)] + [len(_teks(b[i])) for b in baris])
             for i, k in enumerate(kolom)]
    pad = " " * indent

    def garis(kiri, tengah, kanan):
        return pad + warna(kiri + tengah.join("─" * (w + 2) for w in lebar) + kanan, "abu")

    def ratakan(teks, w, mode):
        return teks.rjust(w) if mode == "kanan" else teks.center(w) if mode == "tengah" else teks.ljust(w)

    bar = warna("│", "abu")
    print(garis("┌", "┬", "┐"))
    print(pad + bar + bar.join(
        " " + warna(ratakan(k, w, "tengah"), "tebal") + " " for k, w in zip(kolom, lebar)) + bar)
    print(garis("├", "┼", "┤"))
    for b in baris:
        sel = [" " + warna(ratakan(_teks(c), w, r), *_gaya(c)) + " "
               for c, w, r in zip(b, lebar, rata)]
        print(pad + bar + bar.join(sel) + bar)
    print(garis("└", "┴", "┘"))


def bar_horizontal(nilai: int, maksimum: int, panjang: int = 20) -> str:
    isi = round(panjang * nilai / maksimum) if maksimum else 0
    return warna("█" * isi, "hijau") + warna("░" * (panjang - isi), "abu")


def tanya(label: str) -> str:
    return input(warna(f"  {label}: ", "tebal")).strip()


def tanya_menu(label: str = "Pilih menu") -> str:
    return input(warna(f"\n  {label} ❯ ", "kuning", "tebal")).strip()
