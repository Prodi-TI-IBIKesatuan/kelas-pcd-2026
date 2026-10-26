"""Bangkitkan empat notebook Colab untuk repo proyek kelompok, disesuaikan per topik.

Dipakai oleh tools/buat_repo_proyek.py; tidak dijalankan langsung.

    01_dataset_preprocessing.ipynb  Tahap 1: statistik, cek anotasi, preprocessing, sebelum–sesudah
    02_metode_klasik.ipynb          Tahap 2: metode klasik + metrik
    03_metode_modern.ipynb          Tahap 2: model pralatih + metrik
    04_evaluasi.ipynb               Tahap 2: tabel README, uji ablasi, kasus gagal
"""
from __future__ import annotations

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

NAMA = ["01_dataset_preprocessing.ipynb", "02_metode_klasik.ipynb", "03_metode_modern.ipynb", "04_evaluasi.ipynb"]

SIAPKAN = '''# Siapkan lingkungan: salin repo ini dan hubungkan Google Drive kelompok.
import pathlib
import subprocess
import sys

import cv2
import numpy as np

REPO = "{org}/{repo}"
try:
    import google.colab  # noqa: F401
    DI_COLAB = True
except ImportError:
    DI_COLAB = False

if DI_COLAB:
    AKAR = pathlib.Path("/content/repo")
    if AKAR.exists():
        subprocess.run(["git", "-C", str(AKAR), "pull", "-q"], check=False)
    else:
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{{REPO}}.git", str(AKAR)], check=True)
    from google.colab import drive
    drive.mount("/content/drive")
    FOLDER_KERJA = pathlib.Path("/content/drive/MyDrive/{repo}")
    if not FOLDER_KERJA.exists():
        raise FileNotFoundError(f"{{FOLDER_KERJA}} tidak ada. Tambahkan pintasan folder Drive kelompok ke Drive Saya (lihat PANDUAN.md).")
else:  # dijalankan di komputer sendiri dari folder notebooks/
    AKAR = pathlib.Path.cwd().resolve().parent
    FOLDER_KERJA = AKAR / "data"
sys.path.insert(0, str(AKAR))

from pcd_proyek import evaluasi as ev, metrik, util  # noqa: E402

FOLDER_CITRA = FOLDER_KERJA / "citra" if (FOLDER_KERJA / "citra").exists() else AKAR / "data" / "sample"
BERKAS_ANOTASI = FOLDER_KERJA / "anotasi.csv"
FOLDER_FIGUR = FOLDER_KERJA / "figures"
BERKAS_HASIL = FOLDER_KERJA / "hasil_metode.json"
KOLOM_ANOTASI = {kolom}
JUMLAH_ANGGOTA = {anggota}
print("Citra   :", FOLDER_CITRA)
print("Anotasi :", BERKAS_ANOTASI, "(ada)" if BERKAS_ANOTASI.exists() else "(belum ada)")'''

BACA_ANOTASI = '''anotasi = util.baca_anotasi(BERKAS_ANOTASI, KOLOM_ANOTASI)
UJI_CEPAT = None  # isi angka (mis. 20) saat mencoba-coba agar cepat; kembalikan ke None untuk hasil akhir
print(len(anotasi), "baris anotasi")'''

SIMPAN_COLAB = (
    "## Simpan ke GitHub\n\n"
    "1. **Runtime → Restart session and run all**, pastikan tidak ada error.\n"
    "2. **File → Save a copy in GitHub** → repo `{org}/{repo}` → **branch Anda** (bukan `main`) → path tetap `notebooks/{nama}`.\n"
    "3. Buka *pull request* ke `main` di github.com. Langkah lengkap: `PANDUAN.md`."
)

# ---------------------------------------------------------------- per topik

# Kerangka DUMMY: hanya memperkecil ukuran agar notebook bisa dijalankan. Langkah preprocessing
# yang sebenarnya adalah pekerjaan kelompok (dinilai 30% di Tahap 1), jadi sengaja tidak disediakan.
_PRAPROSES_DUMMY = '''def praproses(citra):
    """DUMMY — ganti dengan langkah preprocessing kelompok Anda.

    Saran untuk topik ini ada di sel markdown di atas. Saat ini fungsi hanya memperkecil ukuran
    sehingga gambar sebelum–sesudah masih identik.
    """
    return util.ubah_ukuran_maks(citra, 1024)'''

_DEGRADASI_DUMMY = '''def degradasi(citra, jenis="gauss", seed=0):
    """DUMMY — ganti dengan pembuat kerusakan sintetis (noise, blur, kompresi JPEG).

    Catat jenis dan parameter setiap kerusakan di anotasi.csv. Saat ini citra dikembalikan apa adanya.
    """
    return citra.copy()


def praproses(citra):
    """DUMMY — untuk restorasi, 'preprocessing' Tahap 1 adalah membuat versi rusak dari citra bersih."""
    return degradasi(util.ubah_ukuran_maks(citra, 1024), "gauss")'''

PRAPROSES = {"t1": _PRAPROSES_DUMMY, "t2": _PRAPROSES_DUMMY, "t3": _DEGRADASI_DUMMY,
             "t4": _PRAPROSES_DUMMY, "t5": _PRAPROSES_DUMMY}

STUB_KLASIK = {
    "t1": ("citra_bgr", "(kotak, teks)", "kotak = (x, y, w, h) pelat atau None; teks = karakter pelat"),
    "t2": ("citra_bgr", "citra_hasil_bgr", "citra hasil perbaikan, ukuran boleh berbeda (otomatis disamakan)"),
    "t3": ("citra_bgr", "citra_hasil_bgr", "citra hasil restorasi"),
    "t4": ("citra_bgr", "(teks, isian)", 'teks lengkap dan dict {"tanggal": ..., "total": ...}'),
    "t5": ("citra_bgr", "vektor_fitur", "vektor 1D numpy, mis. histogram warna yang diratakan"),
}

PANGGIL_EVALUASI = {
    "t1": "ev.evaluasi_pelat({fungsi}, anotasi, FOLDER_CITRA, batas=UJI_CEPAT)",
    "t2": 'ev.evaluasi_berreferensi({fungsi}, anotasi, FOLDER_CITRA, "berkas_gelap", "berkas_referensi", batas=UJI_CEPAT)',
    "t3": 'ev.evaluasi_berreferensi({fungsi}, anotasi, FOLDER_CITRA, "berkas_rusak", "berkas_bersih", batas=UJI_CEPAT)',
    "t4": "ev.evaluasi_ocr({fungsi}, anotasi, FOLDER_CITRA, batas=UJI_CEPAT)",
    "t5": "ev.evaluasi_temu_kembali({fungsi}, anotasi, FOLDER_CITRA, k=5, batas=UJI_CEPAT)",
}

# (kunci rincian untuk kasus gagal, makin kecil makin baik?)
KASUS_GAGAL = {"t1": ("IoU", False), "t2": ("SSIM", False), "t3": ("SSIM", False), "t4": ("CER", True), "t5": ("AP", False)}

CONTOH_MODERN = {
    "t1": '''# Contoh: YOLO untuk lokalisasi + EasyOCR untuk membaca. Sesuaikan dengan model pilihan kelompok.
# !pip install -q ultralytics easyocr
# from ultralytics import YOLO
# import easyocr
# detektor = YOLO("<bobot pelat pralatih, tulis sumbernya di README>")
# pembaca = easyocr.Reader(["en"])''',
    "t2": '''# Contoh: model low-light pralatih (mis. Zero-DCE) dari repositori resminya. Tulis sumbernya di README.
# !pip install -q torch torchvision
# !git clone <url repositori model> /content/model''',
    "t3": '''# Contoh: Real-ESRGAN pralatih. Tulis sumber dan versi bobot di README.
# !pip install -q realesrgan basicsr''',
    "t4": '''# Contoh: bandingkan Tesseract dengan EasyOCR (atau PaddleOCR).
# !apt-get -qq install -y tesseract-ocr tesseract-ocr-ind
# !pip install -q pytesseract easyocr''',
    "t5": '''# Contoh: embedding CLIP lewat open_clip. Tulis nama model dan bobotnya di README.
# !pip install -q open_clip_torch faiss-cpu''',
}

ABLASI = {
    "t1": ("ukuran kernel morfologi", "[3, 5, 7, 9]"),
    "t2": ("nilai gamma", "[0.4, 0.6, 0.8]"),
    "t3": ("ukuran jendela filter", "[3, 5, 7]"),
    "t4": ("ukuran blok binarisasi adaptif", "[15, 31, 51]"),
    "t5": ("jumlah bin histogram", "[4, 8, 16]"),
}


def _sel(daftar):
    nb = new_notebook(cells=daftar)
    for i, s in enumerate(nb.cells):
        s["id"] = f"sel-{i:02d}"
    return nb


def _metadata(nb, nama):
    nb.metadata = {
        "colab": {"provenance": [], "name": nama},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    }
    nbformat.validate(nb)
    return nb


def _badge(k, nama):
    return (f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
            f"(https://colab.research.google.com/github/{k['org']}/{k['repo']}/blob/main/notebooks/{nama})")


def _siapkan(k):
    return new_code_cell(SIAPKAN.format(org=k["org"], repo=k["repo"], kolom=repr(k["topik"]["kolom_anotasi"]), anggota=k["anggota"]))


def _stub(kode, nama_fungsi, judul):
    masukan, keluaran, ket = STUB_KLASIK[kode]
    return (f'def {nama_fungsi}({masukan}):\n'
            f'    """{judul}.\n\n'
            f'    Masukan: citra BGR uint8. Keluaran: {keluaran} — {ket}.\n'
            f'    """\n'
            f'    raise NotImplementedError("tulis {judul.lower()} di sini")')


def nb_01(k):
    t, nama = k["topik"], NAMA[0]
    kolom_berkas = [c for c in t["kolom_anotasi"] if c.startswith("berkas")]
    sel = [
        new_markdown_cell(
            f"# {t['judul']} — Tahap 1: dataset dan preprocessing\n\n{_badge(k, nama)}\n\n"
            f"Kelompok `{k['repo']}` · {k['anggota']} anggota · minimal **{k['citra']} citra** "
            f"(termasuk {k['foto']} foto sendiri).\n\n"
            "Notebook ini membaca dataset dari folder Google Drive kelompok, memeriksa anotasi, menerapkan "
            "preprocessing, dan menyimpan gambar sebelum–sesudah. Jalankan dari atas ke bawah."),
        _siapkan(k),
        new_markdown_cell("## 1. Statistik dataset"),
        new_code_cell(
            "berkas = util.daftar_citra(FOLDER_CITRA)\n"
            "if not berkas:\n"
            "    raise RuntimeError(f\"Tidak ada citra di {FOLDER_CITRA}\")\n"
            "stat = util.statistik_dataset(berkas)\n"
            f"print(f\"{{stat['jumlah']}} citra ({{stat['terbaca']}} terbaca); minimal {k['citra']} untuk kelompok ini\")\n"
            "print(\"Lebar :\", stat.get(\"lebar\"))\n"
            "print(\"Tinggi:\", stat.get(\"tinggi\"))\n"
            "if stat[\"gagal\"]:\n"
            "    print(\"Gagal dibaca (hapus atau ganti):\", *stat[\"gagal\"][:10], sep=\"\\n  \")\n"
            "util.tampil(*[util.baca_citra(p) for p in berkas[:8]], judul=[p.name for p in berkas[:8]], kolom=4)"),
        new_markdown_cell(
            f"## 2. Cek anotasi\n\n{t['anotasi']}\n\n"
            f"Kolom `anotasi.csv` (persis): `{', '.join(t['kolom_anotasi'])}`. Contoh baris ada di `data/format_anotasi.csv`."),
        new_code_cell(
            f"KOLOM_BERKAS = {kolom_berkas!r}\n"
            "if BERKAS_ANOTASI.exists():\n"
            "    anotasi = util.baca_anotasi(BERKAS_ANOTASI, KOLOM_ANOTASI)\n"
            "    cek = util.cek_anotasi(anotasi, FOLDER_CITRA, KOLOM_BERKAS)\n"
            "    print(len(anotasi), \"baris anotasi\")\n"
            "    print(\"Disebut di anotasi tetapi berkasnya tidak ada:\", cek[\"hilang\"][:20])\n"
            "    print(\"Citra belum beranotasi:\", len(cek[\"tanpa_anotasi\"]), cek[\"tanpa_anotasi\"][:10])\n"
            "else:\n"
            "    print(\"anotasi.csv belum ada di\", BERKAS_ANOTASI)"),
        new_markdown_cell(
            "## 3. Preprocessing\n\nSaran untuk topik ini: " + "; ".join(t["preprocessing"]) + ".\n\n"
            "Sel kode di bawah hanya **kerangka dummy**. Ganti dengan langkah preprocessing kelompok, lalu tulis "
            "**alasan setiap langkah** dan parameternya di sel markdown sesudahnya."),
        new_code_cell(PRAPROSES[t["kode"]]),
        new_markdown_cell("**Alasan langkah preprocessing:** [isi: jelaskan setiap langkah dan parameternya]"),
        new_markdown_cell("## 4. Gambar sebelum–sesudah\n\nSel ini menyimpan 12 contoh ke folder `figures/` di Drive. Unggah minimal 10 ke `outputs/figures/` di repo (lihat `PANDUAN.md`)."),
        new_code_cell(
            "FOLDER_FIGUR.mkdir(parents=True, exist_ok=True)\n"
            "for p in berkas[:12]:\n"
            "    asli = util.ubah_ukuran_maks(util.baca_citra(p), 1024)\n"
            "    util.simpan_sebelum_sesudah(asli, praproses(asli), FOLDER_FIGUR / f\"pra_{p.stem}.png\")\n"
            "contoh = sorted(FOLDER_FIGUR.glob(\"pra_*.png\"))[:3]\n"
            "print(len(list(FOLDER_FIGUR.glob(\"pra_*.png\"))), \"gambar di\", FOLDER_FIGUR)\n"
            "util.tampil(*[util.baca_citra(f) for f in contoh], kolom=1, ukuran=7)"),
        new_markdown_cell(SIMPAN_COLAB.format(org=k["org"], repo=k["repo"], nama=nama)),
    ]
    return _metadata(_sel(sel), nama)


def nb_02(k):
    t, nama = k["topik"], NAMA[1]
    kode = t["kode"]
    sel = [
        new_markdown_cell(
            f"# {t['judul']} — Tahap 2: metode klasik\n\n{_badge(k, nama)}\n\n"
            f"Kelompok ini wajib **{k['klasik']} metode klasik**. Pilihan yang disarankan:\n\n"
            + "\n".join(f"- {m}" for m in t["klasik"])
            + "\n\nSetiap metode adalah satu fungsi. Evaluasi memakai `pcd_proyek.evaluasi`, sehingga metrik sama dengan kelompok lain."),
        _siapkan(k),
        new_code_cell(BACA_ANOTASI),
    ]
    for i in range(1, k["klasik"] + 1):
        sel += [
            new_markdown_cell(f"## Metode klasik {i}\n\n**Nama metode dan alasannya:** [isi]"),
            new_code_cell(_stub(kode, f"metode_klasik_{i}", f"Metode klasik {i}")),
            new_code_cell(
                f"hasil_{i} = {PANGGIL_EVALUASI[kode].format(fungsi=f'metode_klasik_{i}')}\n"
                f"print(hasil_{i}['metrik'])\n"
                f"NAMA_{i} = \"Metode klasik {i}\"  # ganti dengan nama metode, mis. \"CLAHE + kontur\"\n"
                f"if UJI_CEPAT is None:\n"
                f"    ev.simpan_hasil(BERKAS_HASIL, NAMA_{i}, \"klasik\", hasil_{i})"),
        ]
    sel.append(new_markdown_cell(SIMPAN_COLAB.format(org=k["org"], repo=k["repo"], nama=nama)))
    return _metadata(_sel(sel), nama)


def nb_03(k):
    t, nama = k["topik"], NAMA[2]
    kode = t["kode"]
    sel = [
        new_markdown_cell(
            f"# {t['judul']} — Tahap 2: metode modern\n\n{_badge(k, nama)}\n\n"
            "Gunakan **model pralatih** (cukup inferensi, tanpa training dari nol). Pilihan yang disarankan:\n\n"
            + "\n".join(f"- {m}" for m in t["modern"])
            + "\n\nAktifkan GPU bila perlu: *Runtime → Change runtime type → T4 GPU*. "
              "Tulis nama model, sumber, dan lisensinya di README bagian *Sumber dan atribusi*."),
        _siapkan(k),
        new_code_cell(BACA_ANOTASI),
        new_markdown_cell("## Pasang dan muat model"),
        new_code_cell(CONTOH_MODERN[kode]),
        new_markdown_cell("## Metode modern\n\n**Nama model dan sumbernya:** [isi]"),
        new_code_cell(_stub(kode, "metode_modern", "Metode modern")),
        new_code_cell(
            f"hasil_modern = {PANGGIL_EVALUASI[kode].format(fungsi='metode_modern')}\n"
            "print(hasil_modern['metrik'])\n"
            "NAMA_MODERN = \"Metode modern\"  # ganti dengan nama model\n"
            "if UJI_CEPAT is None:\n"
            "    ev.simpan_hasil(BERKAS_HASIL, NAMA_MODERN, \"modern\", hasil_modern)"),
        new_markdown_cell(SIMPAN_COLAB.format(org=k["org"], repo=k["repo"], nama=nama)),
    ]
    return _metadata(_sel(sel), nama)


def nb_04(k):
    t, nama = k["topik"], NAMA[3]
    kode = t["kode"]
    metrik_readme = [m["nama"] for m in t["metrik"]]
    kunci, kecil_baik = KASUS_GAGAL[kode]
    param, nilai = ABLASI[kode]
    sel = [
        new_markdown_cell(
            f"# {t['judul']} — Tahap 2: evaluasi dan perbandingan\n\n{_badge(k, nama)}\n\n"
            "Notebook ini menyusun tabel untuk README bagian *Hasil*, menjalankan satu uji ablasi, "
            "dan menampilkan kasus gagal. Jalankan setelah notebook 02 dan 03 menyimpan hasilnya."),
        _siapkan(k),
        new_code_cell(BACA_ANOTASI),
        new_markdown_cell("## 1. Tabel perbandingan untuk README\n\nSalin tabel yang tercetak ke README bagian **Hasil (Tahap 2)**."),
        new_code_cell(
            "semua = ev.baca_hasil(BERKAS_HASIL)\n"
            "if not semua:\n"
            "    raise RuntimeError(\"Belum ada hasil. Jalankan notebook 02 dan 03 dengan UJI_CEPAT = None.\")\n"
            f"print(ev.tabel_markdown(semua, {metrik_readme!r}))"),
        new_markdown_cell(
            f"## 2. Uji ablasi\n\nUbah satu hal dan ukur pengaruhnya, misalnya **{param}** dengan nilai {nilai}. "
            "Salin fungsi metode terbaik dari notebook 02/03 ke sel di bawah dan beri parameter."),
        new_code_cell(
            _stub(kode, "metode_terbaik", "Metode terbaik dengan satu parameter yang diuji").replace(
                "(citra_bgr):", "(citra_bgr, parameter):", 1)),
        new_code_cell(
            f"NILAI_PARAMETER = {nilai}\n"
            "ablasi = {}\n"
            "for p in NILAI_PARAMETER:\n"
            f"    hasil = {PANGGIL_EVALUASI[kode].format(fungsi='lambda c: metode_terbaik(c, p)')}\n"
            "    ablasi[p] = hasil['metrik']\n"
            "    print(p, hasil['metrik'])"),
        new_markdown_cell("**Kesimpulan ablasi:** [isi]"),
        new_markdown_cell(f"## 3. Kasus gagal\n\nTiga citra dengan skor **{kunci}** terburuk dari metode terbaik. Analisis penyebabnya dan simpan gambarnya."),
        new_code_cell(
            f"hasil_terbaik = {PANGGIL_EVALUASI[kode].format(fungsi='lambda c: metode_terbaik(c, NILAI_PARAMETER[0])')}\n"
            f"gagal = ev.terburuk(hasil_terbaik, {kunci!r}, n=3, makin_kecil_makin_baik={kecil_baik})\n"
            "FOLDER_FIGUR.mkdir(parents=True, exist_ok=True)\n"
            "for r in gagal:\n"
            "    print(r)\n"
            "    citra = util.baca_citra(FOLDER_CITRA / r['berkas'])\n"
            "    util.simpan_citra(FOLDER_FIGUR / f\"gagal_{pathlib.Path(r['berkas']).stem}.png\", util.ubah_ukuran_maks(citra, 1024))\n"
            "util.tampil(*[util.baca_citra(FOLDER_CITRA / r['berkas']) for r in gagal], judul=[r['berkas'] for r in gagal])"),
        new_markdown_cell("**Analisis kasus gagal:** [isi: untuk tiap citra, apa yang membuat metode gagal?]"),
        new_markdown_cell(SIMPAN_COLAB.format(org=k["org"], repo=k["repo"], nama=nama)),
    ]
    return _metadata(_sel(sel), nama)


def bangun_semua(konteks: dict) -> dict[str, str]:
    """{nama berkas: isi JSON} untuk keempat notebook."""
    return {nama: nbformat.writes(f(konteks)) + "\n" for nama, f in zip(NAMA, (nb_01, nb_02, nb_03, nb_04))}
