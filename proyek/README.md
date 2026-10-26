# Proyek Kelompok PCD 2026

Proyek kelompok menggantikan UTS (30%) dan UAS (30%) pada semester ganjil 2026/2027. Setiap kelompok mengerjakan **satu topik** di **satu repo GitHub publik** yang dibuat dosen di organisasi `Prodi-TI-IBIKesatuan`, dan seluruh kode dikerjakan di **Google Colab**.

| Saya… | Baca |
| --- | --- |
| Mahasiswa | Berkas ini, [TOPIK.md](TOPIK.md), [RUBRIK.md](RUBRIK.md), lalu `PANDUAN.md` di repo kelompok Anda |
| Dosen / asisten | [docs/panduan-dosen.md](../docs/panduan-dosen.md) |

## Aturan kelompok

- 3–5 orang per kelompok. Setiap topik hanya diambil **satu kelompok per kelas**.
- Pendaftaran: isi formulir dengan nama, NIM, dan username GitHub setiap anggota serta **3 pilihan topik berurutan**. Topik ditetapkan berdasarkan urutan pendaftaran.
- Repo bernama `pcd2026-<kelas>-<topik>`, misalnya `pcd2026-ka-t1`. Anggota mendapat akses tulis; branch `main` dikunci dan hanya bisa diubah lewat *pull request* yang disetujui satu anggota lain.

## Lima topik

| Kode | Topik | Fokus |
| --- | --- | --- |
| T1 | Deteksi dan Pengenalan Pelat Nomor Kendaraan | Menemukan pelat di foto jalanan, lalu membaca karakternya |
| T2 | Penyelarasan Warna dan Perbaikan Citra Malam Hari | Memperbaiki pencahayaan dan warna foto gelap |
| T3 | Restorasi Citra Terdegradasi | Membersihkan noise, blur, dan artefak kompresi |
| T4 | Digitalisasi Dokumen: OCR Struk dan Nota Belanja | Meluruskan foto struk, lalu membaca teks dan isiannya |
| T5 | Aplikasi Rekomendasi Citra Serupa | Merekomendasikan gambar yang mirip secara visual |

Rincian metode, metrik, dan anotasi tiap topik: [TOPIK.md](TOPIK.md). Lingkup di dalam topik (misalnya motor atau mobil untuk T1) ditentukan kelompok dan ditulis di README repo.

## Beban mengikuti jumlah anggota

| Komponen | 3 orang | 4 orang | 5 orang |
| --- | --- | --- | --- |
| Jumlah citra minimal | 150 | 200 | 250 |
| Foto sendiri (15 per anggota, di-commit dari akun masing-masing) | 45 | 60 | 75 |
| Metode klasik | 2 | 2 | 3 |
| Metode modern (model pralatih, cukup inferensi) | 1 | 1 | 1 |

## Peran

Setiap anggota memegang minimal satu peran, dan keempat peran harus terisi. Peran ditulis di `ANGGOTA.yml`.

| Peran | Tugas | 5 orang | 4 orang | 3 orang |
| --- | --- | --- | --- | --- |
| `data` | Akuisisi data, anotasi, `data/README.md` | A1 | A1 | A1 |
| `klasik` | Preprocessing dan metode klasik 1 | A2 | A2 | A2 |
| `klasik` | Metode klasik 2 (dan 3) | A3 | A2 | A2 |
| `modern` | Metode modern | A4 | A3 | A3 |
| `evaluasi` | Evaluasi, demo, README hasil | A5 | A4 | A1 + A3 |

## Tahap 1 (UTS): dataset dan preprocessing

Tenggat **Minggu, 8 November 2026 pukul 23.59 WIB**. Dikumpulkan sebagai GitHub Release bertag `tahap-1`.

| Komponen | Isi | Bobot |
| --- | --- | --- |
| Dataset | 50 citra per anggota, termasuk 15 foto sendiri per anggota, tersimpan di Google Drive kelompok | 30% |
| Anotasi | Label yang dibutuhkan metrik di Tahap 2, dengan format sesuai `data/format_anotasi.csv` | 25% |
| Preprocessing | `notebooks/01_dataset_preprocessing.ipynb` yang lolos *Restart and run all* di Colab | 30% |
| Sebelum–sesudah | Minimal 10 contoh di `outputs/figures/` | 15% |

## Tahap 2 (UAS): metode, perbandingan, dan demo

Dikumpulkan sebagai GitHub Release bertag `tahap-2`. Tenggat diumumkan di Moodle.

| Komponen | Isi | Bobot |
| --- | --- | --- |
| Metode klasik | 2 metode (3 untuk kelompok 5 orang) beserta metriknya | 30% |
| Metode modern | Inferensi 1 model pralatih beserta metriknya | 20% |
| Perbandingan | Tabel metrik klasik vs modern, 1 uji ablasi, analisis kasus gagal | 25% |
| Demo | Aplikasi Gradio di Hugging Face Spaces, tautannya di README | 25% |

Tidak ada laporan tertulis: **README repo adalah dokumentasi hasil**. Rubrik penilaian, aturan kontribusi individu, dan keterlambatan: [RUBRIK.md](RUBRIK.md).

## Alur kerja singkat

1. Buat branch di github.com (menu branch → ketik nama, mis. `t1-preprocessing-andi` → *Create branch*).
2. Buka notebook dari tombol **Open in Colab** di README repo, kerjakan, lalu *Runtime → Restart and run all*.
3. *File → Save a copy in GitHub* → pilih repo kelompok dan **branch Anda** (bukan `main`).
4. Buka *pull request* ke `main`, minta satu anggota menyetujui, tunggu pemeriksaan **cek** hijau, lalu *Merge*.
5. Saat tenggat: satu anggota membuat Release `tahap-1` atau `tahap-2`, lalu menempelkan tautannya di tugas Moodle.

Langkah lengkap, termasuk dari ponsel dan cara memberi izin Colab ke organisasi, ada di `PANDUAN.md` di repo kelompok.

## Aturan main

- **Dataset lengkap tidak masuk repo.** Simpan di folder Google Drive kelompok dengan akses terbatas (anggota + email dosen). Repo hanya berisi `data/sample/` (≤ 20 gambar yang sudah disensor).
- **Data pribadi disensor**: wajah diburamkan, struk tanpa nomor kartu/nama/telepon, pelat di `data/sample/` diburamkan sebagian. **Jangan menulis NIM, email, atau nomor HP di repo**; repo ini publik ([KEBIJAKAN.md](../KEBIJAKAN.md)).
- **Atribusi**: kode atau model dari internet, kelompok lain, atau AI boleh dipakai asal sumbernya ditulis di bagian *Sumber dan atribusi* README. Tanpa sumber berarti plagiarisme.
- **Kontribusi dari akun sendiri**: nilai individu memakai riwayat commit dan *pull request*. Pekerjaan yang di-commit dari akun teman tidak dihitung untuk Anda.
