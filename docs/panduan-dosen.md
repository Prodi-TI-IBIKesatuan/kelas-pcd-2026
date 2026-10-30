# Panduan Dosen

Spesifikasi untuk mahasiswa ada di [proyek/README.md](../proyek/README.md), rincian topik di [proyek/TOPIK.md](../proyek/TOPIK.md), rubrik di [proyek/RUBRIK.md](../proyek/RUBRIK.md). Repo kelompok **publik**, sehingga ruleset dan GitHub Actions berjalan di paket GitHub Free tanpa verifikasi GitHub Education.

## 1. Token untuk otomatisasi (sekali)

Repo kelompok dibuat oleh workflow **Kelola repo kelompok** di repo ini, yang berjalan di server GitHub. Workflow butuh satu token milik owner organisasi, disimpan sebagai secret:

1. github.com → foto profil → *Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token*.
   - *Resource owner*: **Prodi-TI-IBIKesatuan**
   - *Expiration*: sampai akhir semester (mis. 31 Januari 2027)
   - *Repository access*: **All repositories**
   - *Repository permissions*: **Administration**, **Contents**, **Workflows**, **Issues**: *Read and write* (Metadata otomatis *Read-only*)
2. Salin token, lalu buka repo ini → *Settings → Secrets and variables → Actions → New repository secret*. Nama: `ORG_ADMIN_TOKEN`, isi: token tadi.
3. Bila organisasi mewajibkan persetujuan token *fine-grained*, setujui di pengaturan organisasi bagian *Personal access tokens → Pending requests*.

Token ini setara akses owner untuk semua repo organisasi. Hanya dosen yang boleh punya akses tulis ke repo `kelas-pcd-2026`, dan hapus token di akhir semester.

## 2. Uji coba dengan satu kelompok

Lakukan sekali sebelum membuat repo mahasiswa. Repo uji `pcd2026-uji-t1` dibuat lewat workflow dengan `tanpa_undangan` dan diisi simulasi kerja kelompok berkode dummy (lihat [bagian 8](#8-repo-uji-coba)). Yang diperiksa:

1. Tab *Actions* repo uji: run **Cek proyek** hijau.
2. *Settings → Rules → Rulesets*: ada `lindungi-main` dan `kunci-tag-tahap`.
3. Tombol *Open in Colab* di README membuka notebook.
4. Di Colab: *File → Save a copy in GitHub* → pilih repo uji. Langkah ini memicu permintaan akses organisasi untuk aplikasi Colab; setujui (bagian 3).

## 3. Izinkan Google Colab di organisasi (sekali)

Saat seseorang pertama kali memakai *Save a copy in GitHub*, Colab meminta akses ke organisasi. Pemilik organisasi menerima email; setujui aplikasi **Colaboratory** di pengaturan organisasi bagian akses aplikasi pihak ketiga (*Third-party Access → OAuth app policy*). Cukup sekali untuk semua repo kelompok.

## 4. Tetapkan kelompok dan topik

1. Kumpulkan pendaftaran lewat formulir: kelas, nama, NIM, username GitHub tiap anggota (3–5 orang), dan 3 pilihan topik berurutan.
2. Urutkan berdasarkan waktu pengisian. Kelompok pertama mendapat pilihan pertamanya; bila topik itu sudah diambil di kelas yang sama, pakai pilihan berikutnya.
3. Tulis daftar kelompok dengan format `kelas,topik,anggota` (anggota dipisah `;`), satu kelompok per baris. Hanya username, tanpa NIM. Kode kelas bebas (huruf kecil/angka, maks. 10 karakter) dan menjadi bagian nama repo: `pcd2026-ka-t1`.

## 5. Buat repo kelompok

Buka repo ini → *Actions → Kelola repo kelompok → Run workflow*, lalu isi:

| Isian | Contoh |
| --- | --- |
| kelompok | `ka,t1,andi-dev;budi99;citra-s \| ka,t4,dewi;eko;fajar;gita;hana` |
| mode | `periksa` dulu, lalu jalankan lagi dengan `buat` |
| tanpa_undangan | kosongkan untuk kelompok sungguhan |

Isian `kelompok` muncul di log workflow repo publik ini, jadi hanya isi username GitHub, tanpa NIM atau nama.

Sebelum mengubah apa pun, workflow memeriksa bahwa setiap username benar-benar ada di GitHub; bila ada yang tidak ditemukan, tidak ada repo yang dibuat. Anggota yang username-nya belum diketahui atau tidak sah ditulis `?`: ia tetap dihitung dalam jumlah anggota (beban tugas tetap sesuai), tetapi belum diundang. Setelah username-nya diketahui, jalankan workflow dengan mode `isi-tertunda` dan isian `kelas,topik,username-baru`, misalnya `ti23pa,t1,username-baru`.

Workflow memeriksa daftar kelompok dulu (topik ganda dalam satu kelas, jumlah anggota, username tidak sah, mahasiswa di dua kelompok) dan berhenti sebelum mengubah apa pun bila ada masalah. Untuk setiap kelompok, skrip:

1. merakit isi repo dari `proyek/template/` untuk topik dan jumlah anggotanya;
2. membuat repo publik (atau mengisi repo yang sudah Anda buat manual tetapi masih kosong);
3. memasang ruleset dan label;
4. mengundang anggota sebagai kolaborator (izin *push*).

| Ruleset | Aturan |
| --- | --- |
| `lindungi-main` | Wajib *pull request*, 1 persetujuan, pemeriksaan `cek` hijau; tidak bisa dihapus atau di-*force push*. Owner organisasi bisa *bypass* |
| `kunci-tag-tahap` | Tag `tahap-*` tidak bisa dihapus atau dipindah setelah dibuat (owner organisasi bisa *bypass*) |

Aman dijalankan ulang: repo yang sudah berisi tidak disentuh, ruleset yang sudah ada dilewati, undangan dikirim ulang. Undangan kedaluwarsa setelah 7 hari; jalankan ulang workflow dengan isian yang sama untuk mengirim ulang.

Umumkan tautan repo tiap kelompok di Moodle: `https://github.com/Prodi-TI-IBIKesatuan/pcd2026-<kelas>-<topik>`.

## 6. Selama semester

- Ringkasan **Cek proyek** di tab *Actions* tiap repo menunjukkan kekurangan dan status *Siap tahap-1 / tahap-2*.
- Perbaikan pada pemeriksaan atau alat bantu: ubah `proyek/template/`, merge, lalu jalankan workflow dengan mode `perbarui`. Hanya `.github/`, `pcd_proyek/`, tes bawaan, dan `PANDUAN.md` yang ditimpa; pekerjaan mahasiswa tidak disentuh.
- Mengubah topik atau aturan jumlah: edit `proyek/topik.json`, lalu `python tools/buat_dokumen_proyek.py` untuk memperbarui `TOPIK.md`. Validasi CI memastikan keduanya sinkron.
- Kendala teknis dari mahasiswa masuk sebagai issue **Kendala Lab** di repo ini.
- Kelompok terkendala teknis dan Anda mengizinkan pengumpulan dari isi `main` saat itu: *Actions → Rilis atas nama kelompok → Run workflow* (isi nama repo, tahap, dan alasan). Release yang sudah ada tidak pernah diganti.
- Setiap run workflow kelola dan rilis dicatat di issue **Log kelola repo kelompok** di repo ini.

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

[`pcd2026-uji-t1`](https://github.com/Prodi-TI-IBIKesatuan/pcd2026-uji-t1) berisi simulasi satu kelompok T1 dengan **kode dummy** (metode tidak mendeteksi apa pun) dan 6 citra sintetis acak, bukan foto. Anggota uji di `ANGGOTA.yml` tidak diundang. Alur yang sudah diuji di repo itu:

| Langkah | Hasil |
| --- | --- |
| Workflow *Kelola repo kelompok* membuat repo, ruleset, dan label | Berhasil |
| PR #1 Tahap 1 dan PR #2 Tahap 2 | `cek` hijau; status *blocked* sampai ada persetujuan (ruleset aktif), di-merge dengan hak owner |
| Release `tahap-1` dan `tahap-2` lewat *Rilis atas nama kelompok* | Berhasil; `cek` mode tahap pada Release hijau |
| Rilis ulang `tahap-1` | Ditolak, karena Release sudah ada |
| `kumpulkan_proyek.py` dengan `--klon` | Waktu Release, denda, `cek_github` dan `cek_dosen` lulus, kontribusi per anggota, 2 anggota uji tanpa kontribusi ditandai |
| `cek_duplikat_citra.py` | Satu salinan foto antarkelompok terdeteksi (jarak 0) |

Hapus repo ini sebelum semester berjalan bila tidak diperlukan lagi.

## 9. Akhir semester

Arsipkan repo kelompok (*Settings → Archive this repository*). Repo tetap publik sebagai portofolio mahasiswa; arsip membuatnya hanya-baca. `kumpulkan_proyek.py` melewati repo yang diarsipkan.

## Lampiran: menjalankan alat dari laptop

Semua langkah di atas bisa juga dijalankan dari laptop dengan [gh CLI](https://cli.github.com) (login sebagai owner organisasi dengan izin `workflow`):

```bash
gh auth login -s workflow
gh repo clone Prodi-TI-IBIKesatuan/kelas-pcd-2026 && cd kelas-pcd-2026
pip install -r requirements-dev.txt
python tools/buat_repo_proyek.py kelompok.csv --dry-run      # atau --baris "ka,t1,a;b;c"
python tools/buat_repo_proyek.py kelompok.csv
python tools/kumpulkan_proyek.py --tahap 1 --klon ~/proyek-uts -o rekap-tahap1.csv
```
