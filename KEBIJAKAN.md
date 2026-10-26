# Kebijakan proyek kelompok

## Privasi

- Repo kelompok (`pcd2026-*`) **publik** sejak dibuat. Siapa pun bisa melihat isinya.
- `ANGGOTA.yml` hanya berisi username GitHub, nama panggilan, dan peran. Pemeriksaan `cek` menolak kolom `nim`, `email`, `hp`, atau `telepon`.
- Pemetaan NIM ↔ username GitHub hanya disimpan di Moodle, formulir pendaftaran, dan berkas lokal dosen, tidak pernah di repo (UU No. 27/2022 tentang Pelindungan Data Pribadi). Berkas `kelompok*.csv` dan `rekap-*.csv` sudah di-*gitignore*.
- Dataset lengkap disimpan di folder Google Drive kelompok dengan akses **terbatas** (anggota + email dosen). Repo hanya memuat ≤ 20 gambar sampel yang sudah disensor:
  - wajah orang diburamkan;
  - struk tanpa nomor kartu, nama, dan nomor telepon;
  - pelat nomor di `data/sample/` diburamkan sebagian.
- Anotasi (teks pelat, isi struk) disimpan di Drive, bukan di repo.
- Citra: foto sendiri atau data terbuka berlisensi jelas. Dilarang memakai foto/data rahasia perusahaan atau wajah orang tanpa izin.

## Keamanan

- Pemilik organisasi dan asisten wajib memakai autentikasi dua faktor (2FA).
- Jangan menulis token, kata sandi, atau kunci API di repo atau notebook. Rahasia yang sempat ter-*commit* dianggap bocor: cabut, buat ulang, laporkan ke dosen. Menghapus commit saja tidak cukup.
- Aplikasi pihak ketiga yang disetujui untuk organisasi: Google Colaboratory (menyimpan notebook ke GitHub).

## Penggunaan AI

| Pekerjaan | AI boleh? | Syarat |
| --- | --- | --- |
| Memahami materi, menjelaskan pesan galat | Ya | — |
| Kode proyek | Ya, terbatas | Tulis di README bagian *Sumber dan atribusi*; wajib lulus verifikasi lisan untuk bagian peran masing-masing |
| Analisis dan kesimpulan di README | Ya, terbatas | Angka dan contoh harus berasal dari hasil kelompok sendiri |

Sinyal yang ditinjau dosen: satu commit berisi pekerjaan lengkap tanpa riwayat, foto yang sama dengan kelompok lain (`tools/cek_duplikat_citra.py`), dan hasil verifikasi lisan acak.

Sanksi: pelanggaran pertama berarti nilai 0 untuk komponen tersebut dan wajib verifikasi lisan; pelanggaran kedua diteruskan ke Kaprodi.
