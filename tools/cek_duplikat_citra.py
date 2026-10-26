"""Deteksi citra yang sama atau hampir sama antarkelompok (perceptual hash).

Taruh dataset tiap kelompok di subfolder terpisah, mis. hasil unduhan folder Drive
atau folder data/sample/ dari klon repo:

    unduhan/
    ├── pcd2026-ka-t1/   (citra kelompok 1, boleh bersubfolder)
    ├── pcd2026-ka-t2/
    └── ...

    python tools/cek_duplikat_citra.py unduhan/ -o duplikat.csv
    python tools/cek_duplikat_citra.py unduhan/ --ambang 4 --dalam-kelompok

Setiap citra diringkas menjadi dHash 64 bit (tahan terhadap resize, kompresi, dan
perubahan kecerahan ringan). Pasangan dengan jarak Hamming <= ambang dilaporkan.
Hasilnya adalah kandidat: periksa manual sebelum menyimpulkan plagiarisme.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys

import cv2
import numpy as np

EKSTENSI = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def dhash(citra_bgr: np.ndarray, ukuran: int = 8) -> np.ndarray:
    """Difference hash: ukuran*ukuran bit (bool) dari gradien horizontal citra keabuan kecil."""
    abu = cv2.cvtColor(citra_bgr, cv2.COLOR_BGR2GRAY) if citra_bgr.ndim == 3 else citra_bgr
    kecil = cv2.resize(abu, (ukuran + 1, ukuran), interpolation=cv2.INTER_AREA).astype(np.int16)
    return (kecil[:, 1:] > kecil[:, :-1]).ravel()


def baca(path: pathlib.Path) -> np.ndarray | None:
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None


def kumpulkan(akar: pathlib.Path):
    """[(kelompok, path relatif, hash)] untuk semua citra di subfolder akar."""
    hasil, gagal = [], []
    for kelompok in sorted(p for p in akar.iterdir() if p.is_dir()):
        for p in sorted(kelompok.rglob("*")):
            if p.suffix.lower() not in EKSTENSI:
                continue
            citra = baca(p)
            if citra is None:
                gagal.append(p)
                continue
            hasil.append((kelompok.name, p.relative_to(kelompok).as_posix(), dhash(citra)))
    return hasil, gagal


def pasangan_mirip(data, ambang: int = 6, dalam_kelompok: bool = False):
    """[(jarak, kelompok_a, berkas_a, kelompok_b, berkas_b)] terurut dari yang paling mirip."""
    if len(data) < 2:
        return []
    bit = np.array([h for _, _, h in data], dtype=bool)
    kelompok = np.array([k for k, _, _ in data])
    hasil = []
    for i in range(len(data) - 1):
        jarak = np.count_nonzero(bit[i + 1:] != bit[i], axis=1)
        calon = np.nonzero(jarak <= ambang)[0] + i + 1
        for j in calon:
            if not dalam_kelompok and kelompok[i] == kelompok[j]:
                continue
            hasil.append((int(np.count_nonzero(bit[i] != bit[j])), data[i][0], data[i][1], data[j][0], data[j][1]))
    return sorted(hasil)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("akar", type=pathlib.Path, help="folder berisi satu subfolder per kelompok")
    parser.add_argument("--ambang", type=int, default=6, help="jarak Hamming maksimum dari 64 bit (bawaan 6)")
    parser.add_argument("--dalam-kelompok", action="store_true", help="laporkan juga duplikat di dalam satu kelompok")
    parser.add_argument("-o", "--keluaran", type=pathlib.Path)
    arg = parser.parse_args(argv)
    if not arg.akar.is_dir():
        raise SystemExit(f"{arg.akar} bukan folder")
    data, gagal = kumpulkan(arg.akar)
    hasil = pasangan_mirip(data, arg.ambang, arg.dalam_kelompok)
    tujuan = open(arg.keluaran, "w", newline="", encoding="utf-8") if arg.keluaran else sys.stdout
    try:
        penulis = csv.writer(tujuan)
        penulis.writerow(["jarak", "kelompok_a", "berkas_a", "kelompok_b", "berkas_b"])
        penulis.writerows(hasil)
    finally:
        if arg.keluaran:
            tujuan.close()
    print(f"{len(data)} citra dari {len({k for k, _, _ in data})} kelompok; {len(hasil)} pasangan mirip; "
          f"{len(gagal)} berkas gagal dibaca.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
