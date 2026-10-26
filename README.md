# Kelas Pengolahan Citra Digital 2026 — Proyek Kelompok

[![Validasi](https://github.com/Prodi-TI-IBIKesatuan/kelas-pcd-2026/actions/workflows/validasi.yml/badge.svg)](https://github.com/Prodi-TI-IBIKesatuan/kelas-pcd-2026/actions/workflows/validasi.yml)

Repo ini mengelola proyek kelompok UTS dan UAS mata kuliah Pengolahan Citra Digital, Program Studi Teknologi Informasi, IBI Kesatuan, semester ganjil 2026/2027. Setiap kelompok mengerjakan proyeknya di **repo publiknya sendiri** (`pcd2026-<kelas>-<topik>`), yang dibuat dari template di sini oleh satu skrip.

```text
Prodi-TI-IBIKesatuan/
├── kelas-pcd-2026      ← repo ini: aturan, template, dan alat dosen
├── pcd2026-ka-t1       ← repo kelompok (dibuat skrip)
├── pcd2026-ka-t2
└── ...                 ← satu repo per kelompok
```

## Mulai dari sini

| Saya… | Baca |
| --- | --- |
| Mahasiswa | [proyek/README.md](proyek/README.md), [proyek/TOPIK.md](proyek/TOPIK.md), [proyek/RUBRIK.md](proyek/RUBRIK.md), lalu `PANDUAN.md` di repo kelompok Anda |
| Dosen / asisten | [docs/panduan-dosen.md](docs/panduan-dosen.md) |
| Semua | [KEBIJAKAN.md](KEBIJAKAN.md) — privasi, keamanan, dan penggunaan AI |
| Ada kendala teknis | [Buka issue Kendala Lab](https://github.com/Prodi-TI-IBIKesatuan/kelas-pcd-2026/issues/new/choose) |

## Isi repo

```text
proyek/README.md        aturan proyek untuk mahasiswa
proyek/RUBRIK.md        rubrik Tahap 1 (UTS) dan Tahap 2 (UAS), nilai individu, keterlambatan
proyek/topik.json       sumber tunggal topik, metrik, anotasi, dan aturan jumlah
proyek/TOPIK.md         rincian topik (dibangkitkan dari topik.json)
proyek/template/        isi repo kelompok: README, PANDUAN, notebook Colab, pcd_proyek, demo Gradio, pemeriksaan cek
tools/                  alat dosen: buat repo kelompok, rekap pengumpulan, cek duplikat citra
docs/panduan-dosen.md   penyiapan, uji coba, pembuatan repo, dan penilaian
```

## Pemeriksaan mutu

Setiap *push* dan *pull request* menjalankan [validasi](.github/workflows/validasi.yml): tes template, tes alat (termasuk merakit repo kelima topik dan menjalankan keempat notebook-nya ujung ke ujung), dan memastikan `TOPIK.md` sinkron dengan `topik.json`.

```bash
pip install -r requirements-dev.txt
MPLBACKEND=Agg python -m pytest -q tools/tests proyek/template/tests
python tools/buat_dokumen_proyek.py --cek
```

Kode metode di template sengaja **dummy**: langkah preprocessing, metode klasik, dan metode modern adalah pekerjaan kelompok. Yang disediakan hanya kerangka, metrik, dan evaluator yang sama untuk semua kelompok.

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
