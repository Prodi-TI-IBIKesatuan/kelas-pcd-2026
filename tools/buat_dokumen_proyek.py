"""Bangkitkan proyek/TOPIK.md dari proyek/topik.json agar rincian topik selalu sinkron.

Pemakaian:
    python tools/buat_dokumen_proyek.py          # tulis ulang proyek/TOPIK.md
    python tools/buat_dokumen_proyek.py --cek    # gagal bila TOPIK.md tidak sinkron
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

AKAR = pathlib.Path(__file__).resolve().parents[1]
SUMBER = AKAR / "proyek" / "topik.json"
TUJUAN = AKAR / "proyek" / "TOPIK.md"


def bangun(data: dict) -> str:
    umum = data["umum"]
    teks = [
        "# Rincian topik proyek",
        "",
        "Berkas ini dibangkitkan dari `proyek/topik.json` oleh `tools/buat_dokumen_proyek.py`. Jangan diedit manual.",
        "",
        f"Semua topik: {umum['citra_per_anggota']} citra per anggota (termasuk {umum['foto_sendiri_per_anggota']} foto sendiri), "
        f"{umum['metode_klasik']['3']} metode klasik ({umum['metode_klasik']['5']} untuk kelompok 5 orang), "
        f"dan {umum['metode_modern']} metode modern berbasis model pralatih. Metode di bawah adalah pilihan yang disarankan; "
        "metode lain yang setara boleh dipakai asal dijelaskan di README.",
        "",
        "| Kode | Topik | Metrik utama |",
        "| --- | --- | --- |",
    ]
    for t in data["topik"]:
        teks.append(f"| [{t['kode'].upper()}](#{t['kode']}) | {t['judul']} | {', '.join(m['nama'] for m in t['metrik'])} |")
    for t in data["topik"]:
        teks += [
            "",
            f'<a id="{t["kode"]}"></a>',
            "",
            f"## {t['kode'].upper()} — {t['judul']}",
            "",
            f"**Fokus:** {t['fokus']}",
            "",
            f"**Batas:** {t['batas']}",
            "",
            f"**Contoh lingkup:** {', '.join(t['lingkup_contoh'])}.",
            "",
            "**Metode klasik (pilih sesuai jumlah wajib):**",
            "",
            *[f"- {m}" for m in t["klasik"]],
            "",
            "**Metode modern:**",
            "",
            *[f"- {m}" for m in t["modern"]],
            "",
            "**Metrik:**",
            "",
            *[f"- **{m['nama']}**: {m['keterangan']} (`pcd_proyek.metrik.{m['fungsi']}`)" for m in t["metrik"]],
            "",
            f"**Anotasi (Tahap 1):** {t['anotasi']} Kolom `anotasi.csv`: `{', '.join(t['kolom_anotasi'])}`.",
            "",
            f"**Contoh preprocessing:** {', '.join(t['preprocessing'])}.",
            "",
            f"**Dataset:** {t['dataset']}",
            "",
            f"**Etika:** {t['etika']}",
            "",
            f"**Demo (Tahap 2):** {t['demo']}",
        ]
    return "\n".join(teks) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cek", action="store_true")
    arg = parser.parse_args(argv)
    isi = bangun(json.loads(SUMBER.read_text(encoding="utf-8")))
    if arg.cek:
        if not TUJUAN.exists() or TUJUAN.read_text(encoding="utf-8") != isi:
            print("proyek/TOPIK.md tidak sinkron (jalankan tools/buat_dokumen_proyek.py)")
            return 1
        print("proyek/TOPIK.md sinkron.")
        return 0
    TUJUAN.write_text(isi, encoding="utf-8")
    print(f"ditulis {TUJUAN.relative_to(AKAR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
