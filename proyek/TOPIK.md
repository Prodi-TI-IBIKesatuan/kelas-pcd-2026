# Rincian topik proyek

Berkas ini dibangkitkan dari `proyek/topik.json` oleh `tools/buat_dokumen_proyek.py`. Jangan diedit manual.

Semua topik: 50 citra per anggota (termasuk 15 foto sendiri), 2 metode klasik (3 untuk kelompok 5 orang), dan 1 metode modern berbasis model pralatih. Metode di bawah adalah pilihan yang disarankan; metode lain yang setara boleh dipakai asal dijelaskan di README.

| Kode | Topik | Metrik utama |
| --- | --- | --- |
| [T1](#t1) | Deteksi dan Pengenalan Pelat Nomor Kendaraan | IoU, CER |
| [T2](#t2) | Penyelarasan Warna dan Perbaikan Citra Malam Hari | PSNR, SSIM |
| [T3](#t3) | Restorasi Citra Terdegradasi | PSNR, SSIM |
| [T4](#t4) | Digitalisasi Dokumen: OCR Struk dan Nota Belanja | CER, Akurasi isian |
| [T5](#t5) | Aplikasi Rekomendasi Citra Serupa | Presisi@5, mAP |

<a id="t1"></a>

## T1 — Deteksi dan Pengenalan Pelat Nomor Kendaraan

**Fokus:** Menemukan letak pelat nomor pada foto kendaraan di lingkungan nyata, lalu membaca karakternya.

**Batas:** Objeknya foto pemandangan (jalan, parkiran). Membaca dokumen adalah T4.

**Contoh lingkup:** pelat motor, pelat mobil, kondisi malam atau hujan.

**Metode klasik (pilih sesuai jumlah wajib):**

- Lokalisasi pelat: deteksi tepi (Sobel/Canny) + morfologi (closing) + analisis kontur dengan rasio aspek
- Segmentasi karakter: binarisasi Otsu + komponen terhubung
- Pengenalan karakter dengan template matching

**Metode modern:**

- Detektor objek pralatih untuk lokalisasi pelat (mis. YOLO)
- OCR pralatih untuk membaca karakter (mis. EasyOCR)

**Metrik:**

- **IoU**: ketepatan kotak pelat; deteksi dihitung benar bila IoU ≥ 0,5 (`pcd_proyek.metrik.iou`)
- **CER**: character error rate teks pelat (makin kecil makin baik) (`pcd_proyek.metrik.cer`)

**Anotasi (Tahap 1):** Kotak lokasi pelat (x, y, lebar, tinggi dalam piksel) dan teks pelat tanpa spasi. Kolom `anotasi.csv`: `berkas, x, y, w, h, teks_pelat`.

**Contoh preprocessing:** grayscale, resize seragam (mis. sisi terpanjang 1024 px), peningkatan kontras (CLAHE) atau penajaman tepi.

**Dataset:** Foto sendiri di parkiran atau jalan. Boleh ditambah dataset terbuka berlisensi jelas; sebutkan sumbernya.

**Etika:** Wajah orang wajib diburamkan. Di data/sample, sebagian karakter pelat diburamkan. Teks pelat lengkap hanya disimpan di Drive.

**Demo (Tahap 2):** Unggah foto kendaraan, tampilkan kotak pelat dan teks yang terbaca.

<a id="t2"></a>

## T2 — Penyelarasan Warna dan Perbaikan Citra Malam Hari

**Fokus:** Memperbaiki pencahayaan dan keseimbangan warna foto yang diambil dalam kondisi gelap.

**Batas:** Hanya masalah cahaya dan warna. Noise, blur, dan artefak kompresi adalah T3.

**Contoh lingkup:** lingkungan jalan, dalam ruangan, perbandingan kamera ponsel.

**Metode klasik (pilih sesuai jumlah wajib):**

- Koreksi gamma
- CLAHE pada kanal L (LAB) atau V (HSV)
- Retinex (single-scale atau multi-scale)
- White balance gray-world

**Metode modern:**

- Model low-light enhancement pralatih (mis. Zero-DCE)

**Metrik:**

- **PSNR**: pada pasangan berreferensi (dB, makin besar makin baik) (`pcd_proyek.metrik.psnr`)
- **SSIM**: kemiripan struktur dengan referensi (0–1) (`pcd_proyek.metrik.ssim`)

**Anotasi (Tahap 1):** Pasangan citra gelap–terang sebagai referensi (mis. dataset LOL) dan foto malam sendiri. Foto sendiri tanpa pasangan dinilai dengan metrik tanpa referensi (NIQE/BRISQUE, opsional lewat paket pyiqa). Kolom `anotasi.csv`: `berkas_gelap, berkas_referensi, sumber`.

**Contoh preprocessing:** resize seragam, konversi ruang warna ke LAB atau HSV, pemisahan kanal luminans dan warna.

**Dataset:** Dataset LOL (Low-Light) untuk pasangan berreferensi, ditambah foto malam sendiri.

**Etika:** Wajah orang wajib diburamkan di data/sample.

**Demo (Tahap 2):** Unggah foto gelap, tampilkan hasil perbaikan berdampingan dengan aslinya.

<a id="t3"></a>

## T3 — Restorasi Citra Terdegradasi

**Fokus:** Memulihkan citra yang rusak oleh noise, blur, atau artefak kompresi JPEG.

**Batas:** Bukan masalah pencahayaan (itu T2).

**Contoh lingkup:** noise ISO tinggi, blur gerak, foto lama hasil pindai.

**Metode klasik (pilih sesuai jumlah wajib):**

- Filter median
- Filter bilateral
- Non-local means
- Dekonvolusi Wiener untuk blur

**Metode modern:**

- Model restorasi atau super-resolusi pralatih (mis. Real-ESRGAN)

**Metrik:**

- **PSNR**: terhadap citra bersih (dB, makin besar makin baik) (`pcd_proyek.metrik.psnr`)
- **SSIM**: kemiripan struktur dengan citra bersih (0–1) (`pcd_proyek.metrik.ssim`)

**Anotasi (Tahap 1):** Citra bersih sebagai acuan dan versi rusak sintetis; jenis dan parameter degradasi dicatat. Kolom `anotasi.csv`: `berkas_bersih, berkas_rusak, jenis_degradasi, parameter`.

**Contoh preprocessing:** skrip pembuat degradasi dengan seed tetap, resize atau crop seragam, konversi ke float [0, 1] untuk perhitungan.

**Dataset:** Foto sendiri yang tajam sebagai citra bersih; boleh ditambah dataset terbuka (mis. DIV2K).

**Etika:** Wajah orang wajib diburamkan di data/sample.

**Demo (Tahap 2):** Unggah foto rusak, tampilkan hasil restorasi berdampingan dengan aslinya.

<a id="t4"></a>

## T4 — Digitalisasi Dokumen: OCR Struk dan Nota Belanja

**Fokus:** Meluruskan dan membersihkan foto struk, lalu membaca teks dan mengambil isian penting.

**Batas:** Objeknya dokumen, bukan pemandangan (pelat nomor adalah T1).

**Contoh lingkup:** struk minimarket, nota tulisan tangan, tiket atau karcis parkir.

**Metode klasik (pilih sesuai jumlah wajib):**

- Deteksi tepi dokumen + koreksi perspektif (homografi)
- Deskew (koreksi kemiringan)
- Binarisasi adaptif (Otsu, Sauvola)

**Metode modern:**

- OCR pralatih: bandingkan Tesseract dengan EasyOCR atau PaddleOCR

**Metrik:**

- **CER**: character error rate teks lengkap (makin kecil makin baik) (`pcd_proyek.metrik.cer`)
- **Akurasi isian**: fraksi isian tanggal dan total yang terbaca benar (`pcd_proyek.metrik.akurasi_isian`)

**Anotasi (Tahap 1):** Transkrip teks lengkap dan isian tanggal serta total. Kolom `anotasi.csv`: `berkas, teks_lengkap, tanggal, total`.

**Contoh preprocessing:** crop area dokumen, koreksi perspektif, deskew, grayscale + binarisasi.

**Dataset:** Foto struk sendiri; boleh ditambah dataset struk terbuka (mis. SROIE).

**Etika:** Sensor nomor kartu, nama, dan nomor telepon pada struk sebelum diunggah ke data/sample.

**Demo (Tahap 2):** Unggah foto struk, tampilkan dokumen yang sudah diluruskan, teks, tanggal, dan total.

<a id="t5"></a>

## T5 — Aplikasi Rekomendasi Citra Serupa

**Fokus:** Mencari dan merekomendasikan gambar yang paling mirip secara visual dari basis data citra (CBIR).

**Batas:** Fokus pada kemiripan visual, bukan klasifikasi.

**Contoh lingkup:** motif batik, produk UMKM, makanan nusantara.

**Metode klasik (pilih sesuai jumlah wajib):**

- Histogram warna (HSV)
- Tekstur GLCM
- HOG

**Metode modern:**

- Embedding model pralatih (CLIP atau ResNet) + pencarian tetangga terdekat (mis. FAISS)

**Metrik:**

- **Presisi@5**: fraksi 5 hasil teratas yang kategorinya sama dengan query (`pcd_proyek.metrik.presisi_at_k`)
- **mAP**: rata-rata average precision seluruh query (`pcd_proyek.metrik.mean_average_precision`)

**Anotasi (Tahap 1):** Label kategori setiap citra; dua citra dianggap relevan bila kategorinya sama. Kolom `anotasi.csv`: `berkas, kategori`.

**Contoh preprocessing:** resize seragam, normalisasi warna, penghapusan duplikat.

**Dataset:** Foto sendiri; boleh ditambah dataset terbuka berlisensi jelas.

**Etika:** Wajah orang wajib diburamkan di data/sample.

**Demo (Tahap 2):** Unggah satu citra, tampilkan galeri citra paling mirip beserta skornya.
