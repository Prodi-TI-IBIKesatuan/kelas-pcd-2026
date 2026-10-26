# Panduan Dosen

Spesifikasi untuk mahasiswa ada di [proyek/README.md](../proyek/README.md), rincian topik di [proyek/TOPIK.md](../proyek/TOPIK.md), rubrik di [proyek/RUBRIK.md](../proyek/RUBRIK.md). Repo kelompok **publik**, sehingga ruleset dan GitHub Actions berjalan di paket GitHub Free tanpa verifikasi GitHub Education.

## 1. Siapkan laptop (sekali)

Butuh Python 3.10+, git, dan [gh CLI](https://cli.github.com).

```bash
gh auth login -s workflow            # akun owner organisasi; izin workflow wajib
git config --global user.name "Nama Anda"
git config --global user.email "email@kampus"
gh repo clone Prodi-TI-IBIKesatuan/kelas-pcd-2026
cd kelas-pcd-2026
pip install -r requirements-dev.txt
```

Sudah login tanpa izin `workflow`? Jalankan `gh auth refresh -h github.com -s workflow`. Skrip menolak berjalan tanpa izin itu, karena berkas `.github/workflows` tidak bisa didorong.

## 2. Uji coba dengan satu kelompok

Lakukan sekali sebelum membuat repo mahasiswa. Repo uji `pcd2026-uji-t1` sudah dibuat dan diisi simulasi kerja kelompok dengan kode dummy (lihat [bagian 8](#8-repo-uji-coba)). Untuk mengulang dari nol:

```bash
printf 'kelas,topik,anggota\nuji,t1,<username Anda>;<asisten 1>;<asisten 2>\n' > uji.csv
python tools/buat_repo_proyek.py uji.csv                    # atau --tanpa-undangan
```

Periksa di repo uji:

1. Tab *Actions*: run **Cek proyek** hijau.
2. *Settings → Rules → Rulesets*: ada `lindungi-main` dan `kunci-tag-tahap`.
3. Tombol *Open in Colab* di README membuka notebook.
4. Di Colab: *File → Save a copy in GitHub* → pilih repo uji. Langkah ini memicu permintaan akses organisasi untuk aplikasi Colab; setujui (bagian 3).

Hapus repo uji setelah selesai: *Settings → Delete this repository*.

## 3. Izinkan Google Colab di organisasi (sekali)

Saat seseorang pertama kali memakai *Save a copy in GitHub*, Colab meminta akses ke organisasi. Pemilik organisasi menerima email; setujui aplikasi **Colaboratory** di pengaturan organisasi bagian akses aplikasi pihak ketiga (*Third-party Access → OAuth app policy*). Cukup sekali untuk semua repo kelompok.

## 4. Tetapkan kelompok dan topik

1. Kumpulkan pendaftaran lewat formulir: kelas, nama, NIM, username GitHub tiap anggota (3–5 orang), dan 3 pilihan topik berurutan.
2. Urutkan berdasarkan waktu pengisian. Kelompok pertama mendapat pilihan pertamanya; bila topik itu sudah diambil di kelas yang sama, pakai pilihan berikutnya.
3. Susun `kelompok.csv` di laptop Anda (bukan di repo). Hanya username, tanpa NIM:
   ```csv
   kelas,topik,anggota
   ka,t1,andi-dev;budi99;citra-s
   ka,t4,dewi;eko;fajar;gita;hana
   kb,t1,mira;nina;opa
   ```
   Kode kelas bebas (huruf kecil/angka, maks. 10 karakter) dan menjadi bagian nama repo: `pcd2026-ka-t1`.

## 5. Buat repo kelompok

```bash
python tools/buat_repo_proyek.py kelompok.csv --dry-run     # validasi CSV + daftar perintah, tanpa mengubah apa pun
python tools/buat_repo_proyek.py kelompok.csv               # buat semua repo
```

Skrip memeriksa CSV dulu (topik ganda dalam satu kelas, jumlah anggota, username tidak sah, mahasiswa di dua kelompok) dan berhenti sebelum mengubah apa pun bila ada masalah. Untuk setiap kelompok, skrip:

1. merakit isi repo dari `proyek/template/` untuk topik dan jumlah anggotanya;
2. membuat repo publik (atau mengisi repo yang sudah Anda buat manual tetapi masih kosong);
3. memasang ruleset dan label;
4. mengundang anggota sebagai kolaborator (izin *push*).

| Ruleset | Aturan |
| --- | --- |
| `lindungi-main` | Wajib *pull request*, 1 persetujuan, pemeriksaan `cek` hijau; tidak bisa dihapus atau di-*force push*. Owner organisasi bisa *bypass* |
| `kunci-tag-tahap` | Tag `tahap-*` tidak bisa dihapus atau dipindah setelah dibuat (owner organisasi bisa *bypass*) |

Aman dijalankan ulang: repo yang sudah berisi tidak disentuh, ruleset yang sudah ada dilewati, undangan dikirim ulang. Undangan kedaluwarsa setelah 7 hari; jalankan ulang perintah yang sama untuk mengirim ulang.

Umumkan tautan repo tiap kelompok di Moodle: `https://github.com/Prodi-TI-IBIKesatuan/pcd2026-<kelas>-<topik>`.

## 6. Selama semester

- Ringkasan **Cek proyek** di tab *Actions* tiap repo menunjukkan kekurangan dan status *Siap tahap-1 / tahap-2*.
- Perbaikan pada pemeriksaan atau alat bantu: ubah `proyek/template/`, merge, lalu dorong ke semua repo tanpa menyentuh pekerjaan mahasiswa:
  ```bash
  python tools/buat_repo_proyek.py kelompok.csv --perbarui   # hanya .github/, pcd_proyek/, tes bawaan, PANDUAN.md
  ```
- Mengubah topik atau aturan jumlah: edit `proyek/topik.json`, lalu `python tools/buat_dokumen_proyek.py` untuk memperbarui `TOPIK.md`. Validasi CI memastikan keduanya sinkron.
- Kendala teknis dari mahasiswa masuk sebagai issue **Kendala Lab** di repo ini.

## 7. Merekap dan menilai

```bash
python tools/kumpulkan_proyek.py --tahap 1 --klon ~/proyek-uts -o rekap-tahap1.csv
python tools/kumpulkan_proyek.py --tahap 2 --tenggat "2027-01-10 23:59" --klon ~/proyek-uas -o rekap-tahap2.csv
```

Per repo: tautan dan waktu Release (WIB, dari server GitHub), jam terlambat dan denda sesuai rubrik, hasil `cek` pada commit tag, commit dan PR per anggota `ANGGOTA.yml`, serta anggota tanpa kontribusi. Dengan `--klon`, repo diklon pada tag dan diperiksa ulang memakai `cek_proyek.py` versi repo ini, sehingga perubahan `.github/` oleh kelompok tidak memengaruhi penilaian. Tenggat Tahap 1 bawaan diambil dari `proyek/topik.json`; tenggat Tahap 2 diisi di sana atau lewat `--tenggat`.

Mendeteksi foto yang dipakai ulang antarkelompok (unduh folder Drive tiap kelompok ke satu folder induk, satu subfolder per kelompok):

```bash
python tools/cek_duplikat_citra.py unduhan/ -o duplikat.csv
```

Hasilnya kandidat (dHash, tahan resize, kompresi, dan perubahan kecerahan); periksa manual sebelum menyimpulkan.

## 8. Repo uji coba

[`pcd2026-uji-t1`](https://github.com/Prodi-TI-IBIKesatuan/pcd2026-uji-t1) berisi simulasi satu kelompok T1 dengan **kode dummy** (metode mengembalikan masukan apa adanya; citra sintetis acak, bukan foto). Isinya menunjukkan seluruh alur: *pull request* yang lolos `cek`, Release `tahap-1` dan `tahap-2`, serta hasil `kumpulkan_proyek.py`. Anggota uji di `ANGGOTA.yml` tidak diundang. Hapus repo ini sebelum semester berjalan bila tidak diperlukan lagi.

## 9. Akhir semester

Arsipkan repo kelompok (*Settings → Archive this repository*). Repo tetap publik sebagai portofolio mahasiswa; arsip membuatnya hanya-baca. `kumpulkan_proyek.py` melewati repo yang diarsipkan.
