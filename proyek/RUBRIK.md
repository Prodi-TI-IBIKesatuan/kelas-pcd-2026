# Rubrik Proyek Kelompok

Nilai diambil dari isi repo **pada tag Release** (`tahap-1` atau `tahap-2`), bukan dari `main` sesudahnya. Tag terkunci: setelah Release dibuat, isinya tidak bisa diganti. Karena itu, sebelum membuat Release, buka tab *Actions* → run **Cek proyek** terakhir di `main` dan pastikan ringkasannya menulis **Siap tahap-1** (atau **Siap tahap-2**). Pemeriksaan yang sama dijalankan lagi pada Release; hasil merah menjadi catatan bagi penilai.

## Tahap 1 (UTS) — total 100

| Kriteria | Skor | Penuh bila | Bukti |
| --- | --- | --- | --- |
| Dataset | 30 | Jumlah citra ≥ 50 × anggota, foto sendiri ≥ 15 per anggota, sumber dan lisensi data tambahan jelas | `data/README.md`, Drive kelompok, riwayat commit `data/sample/` |
| Anotasi | 25 | Seluruh citra beranotasi sesuai `data/format_anotasi.csv`, konsisten, siap dipakai metrik Tahap 2 | Berkas anotasi di Drive, ringkasan di `data/README.md` |
| Preprocessing | 30 | `01_dataset_preprocessing.ipynb` berjalan dari awal sampai akhir, langkahnya beralasan untuk topik, parameter dijelaskan | Notebook beserta keluarannya |
| Sebelum–sesudah | 15 | ≥ 10 pasangan gambar yang menunjukkan efek tiap langkah | `outputs/figures/` |

## Tahap 2 (UAS) — total 100

| Kriteria | Skor | Penuh bila | Bukti |
| --- | --- | --- | --- |
| Metode klasik | 30 | 2 metode (3 untuk 5 orang) diterapkan dengan benar, parameter dijelaskan, metrik dihitung pada seluruh data uji | `02_metode_klasik.ipynb`, tabel Hasil |
| Metode modern | 20 | Model pralatih dijalankan pada data yang sama, sumber model dicantumkan | `03_metode_modern.ipynb`, bagian Sumber |
| Perbandingan | 25 | Tabel klasik vs modern dengan metrik topik, 1 uji ablasi, ≥ 3 kasus gagal dianalisis | `04_evaluasi.ipynb`, README bagian Hasil |
| Demo | 25 | Aplikasi Gradio publik berjalan, mudah dipakai, memakai metode terbaik kelompok | Tautan Hugging Face Spaces di README |

Dosen dapat melakukan **verifikasi lisan** acak di sesi Meet: anggota diminta menjelaskan kode di bagian perannya.

## Nilai individu

Nilai individu = nilai kelompok, dengan dua pengecualian:

1. Anggota **tanpa satu pun commit atau *pull request* atas namanya** pada suatu tahap tidak mendapat nilai kelompok untuk tahap itu, kecuali dapat menunjukkan kontribusinya saat verifikasi lisan.
2. Pada Tahap 1, anggota yang menyumbang **kurang dari 15 foto sendiri** dari akunnya mendapat pengurangan proporsional pada komponen Dataset.

Rekap kontribusi dibuat otomatis dari riwayat GitHub dengan `tools/kumpulkan_proyek.py`.

## Keterlambatan

Waktu Release dicatat server GitHub. Release yang dibuat setelah tenggat dikurangi **10 poin per 24 jam** (dihitung per 24 jam yang dimulai). Setelah **3 hari**, tahap itu tidak dinilai. Kendala teknis dilaporkan sebelum tenggat lewat issue **Kendala Lab**.
