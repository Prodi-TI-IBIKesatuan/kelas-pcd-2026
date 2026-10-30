"""Buat repo proyek kelompok PCD 2026 di organisasi GitHub dari proyek/template.

Untuk setiap kelompok di berkas CSV:
  1. Rakit isi repo dari proyek/template untuk topiknya (README, ANGGOTA.yml, 4 notebook Colab, app Gradio, cek).
  2. Buat repo PUBLIK <awalan>-<kelas>-<topik> di organisasi dan dorong commit awal.
  3. Pasang ruleset: main wajib PR + 1 persetujuan + cek hijau; tag tahap-* tidak bisa dihapus/dipindah.
  4. Undang anggota sebagai kolaborator (izin push) dan buat label peran.

Format CSV (tanpa NIM; simpan di komputer Anda, bukan di repo):

    kelas,topik,anggota
    ka,t1,andi-dev;budi99;citra-s
    ka,t4,dewi;eko;fajar;gita;hana

Hanya memakai REST API GitHub (gh api) dan git. Repo yang sudah dibuat manual tetapi masih kosong
akan diisi; repo yang sudah berisi tidak disentuh kecuali dengan --perbarui.

Pemakaian (gh CLI login sebagai owner organisasi):
    python tools/buat_repo_proyek.py kelompok.csv --dry-run      # periksa CSV dan tampilkan perintah
    python tools/buat_repo_proyek.py kelompok.csv                # jalankan sungguhan
    python tools/buat_repo_proyek.py kelompok.csv --rakit build/ # hanya rakit folder repo, tanpa GitHub
    python tools/buat_repo_proyek.py kelompok.csv --perbarui     # dorong ulang .github/ dan pcd_proyek/ ke repo yang sudah ada
    python tools/buat_repo_proyek.py uji.csv --tanpa-undangan    # repo uji coba tanpa mengundang siapa pun

Anggota yang username GitHub-nya belum diketahui ditulis '?': dihitung dalam jumlah anggota
(beban tugas tetap sesuai), tetapi belum diundang. Isi kemudian dengan --isi-tertunda:
    python tools/buat_repo_proyek.py --baris "ti23pa,t1,username-baru" --isi-tertunda

Aman dijalankan berulang: repo, ruleset, label, dan undangan yang sudah ada dilewati.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import notebook_proyek  # noqa: E402

AKAR = pathlib.Path(__file__).resolve().parents[1]
PROYEK = AKAR / "proyek"
TEMPLATE = PROYEK / "template"
POLA_USERNAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")
POLA_KELAS = re.compile(r"^[a-z0-9]{1,10}$")
TERTUNDA = "?"  # anggota yang username GitHub-nya belum diketahui: dihitung, tetapi belum diundang
TEKS = {".md", ".py", ".yml", ".yaml", ".txt", ".csv", ".cfg", ".toml", ".json", ""}
# Berkas yang dikelola dosen: ditimpa oleh --perbarui. Berkas lain milik kelompok.
DIKELOLA = (".github/", "pcd_proyek/", "tests/test_pcd_proyek.py", "tests/test_evaluasi.py", "PANDUAN.md")
LABEL = {
    "data": ("0e8a16", "Akuisisi data dan anotasi"),
    "klasik": ("1f6feb", "Preprocessing dan metode klasik"),
    "modern": ("8250df", "Metode modern (model pralatih)"),
    "evaluasi": ("d93f0b", "Evaluasi, demo, README hasil"),
    "tahap-1": ("c5def5", "Pekerjaan Tahap 1 (UTS)"),
    "tahap-2": ("fbca04", "Pekerjaan Tahap 2 (UAS)"),
}


def muat_topik() -> dict:
    return json.loads((PROYEK / "topik.json").read_text(encoding="utf-8"))


@dataclass(frozen=True)
class Kelompok:
    kelas: str
    topik: str
    anggota: tuple[str, ...]

    def nama_repo(self, awalan: str) -> str:
        return f"{awalan}-{self.kelas}-{self.topik}"


def baca_kelompok(teks: str, data_topik: dict) -> list[Kelompok]:
    """Baca dan validasi CSV kelompok. Semua masalah dikumpulkan dulu, lalu dilaporkan sekaligus."""
    umum = data_topik["umum"]
    kode_sah = {t["kode"] for t in data_topik["topik"]}
    pembaca = csv.DictReader(io.StringIO(teks.lstrip("﻿")))
    kolom = [c.strip().lower() for c in (pembaca.fieldnames or [])]
    if kolom[:3] != ["kelas", "topik", "anggota"]:
        raise SystemExit("CSV harus berkolom: kelas,topik,anggota")
    hasil, masalah, dipakai, topik_kelas = [], [], {}, set()
    for no, baris in enumerate(pembaca, start=2):
        baris = {k.strip().lower(): (v or "").strip() for k, v in baris.items() if k}
        if not any(baris.values()):
            continue
        kelas, topik = baris["kelas"].lower(), baris["topik"].lower()
        anggota = tuple(a for a in (bersihkan_username(x) for x in re.split(r"[;\s]+", baris["anggota"])) if a)
        if not POLA_KELAS.match(kelas):
            masalah.append(f"baris {no}: kode kelas '{kelas}' harus huruf kecil/angka, maks. 10 karakter")
        if topik not in kode_sah:
            masalah.append(f"baris {no}: topik '{topik}' tidak dikenal (pilih {', '.join(sorted(kode_sah))})")
        if (kelas, topik) in topik_kelas:
            masalah.append(f"baris {no}: topik {topik} sudah diambil kelompok lain di kelas {kelas}")
        topik_kelas.add((kelas, topik))
        if not umum["anggota_min"] <= len(anggota) <= umum["anggota_max"]:
            masalah.append(f"baris {no}: {len(anggota)} anggota; harus {umum['anggota_min']}–{umum['anggota_max']}")
        for a in anggota:
            if a == TERTUNDA:
                continue
            if not POLA_USERNAME.match(a):
                masalah.append(f"baris {no}: username GitHub '{a}' tidak sah")
            elif a.lower() in dipakai:
                masalah.append(f"baris {no}: @{a} sudah terdaftar di baris {dipakai[a.lower()]}")
            else:
                dipakai[a.lower()] = no
        hasil.append(Kelompok(kelas, topik, anggota))
    if masalah:
        raise SystemExit("CSV kelompok bermasalah:\n  " + "\n  ".join(masalah))
    if not hasil:
        raise SystemExit("CSV kelompok kosong")
    return hasil


def baca_tambahan(teks: str) -> list[Kelompok]:
    """Untuk --isi-tertunda: kelas,topik,username-baru (jumlah anggota tidak diperiksa)."""
    hasil = []
    for baris in csv.DictReader(io.StringIO(teks.lstrip("\ufeff"))):
        baris = {k.strip().lower(): (v or "").strip() for k, v in baris.items() if k}
        anggota = tuple(a for a in (bersihkan_username(x) for x in re.split(r"[;\s]+", baris.get("anggota", ""))) if a)
        salah = [a for a in anggota if not POLA_USERNAME.match(a)]
        if not anggota or salah:
            raise SystemExit(f"username tidak sah: {salah or 'kosong'}")
        hasil.append(Kelompok(baris["kelas"].lower(), baris["topik"].lower(), anggota))
    return hasil


def bersihkan_username(teks: str) -> str:
    """Buang '@', spasi, dan karakter tak terlihat (mis. U+2068/U+2069 dari salin-tempel ponsel)."""
    teks = re.sub(r"[\u200b-\u200f\u2060-\u206f\ufeff\s]", "", teks or "")
    return teks.lstrip("@")


def username_aktif(anggota) -> list[str]:
    """Anggota yang sudah punya username (tanpa penanda tertunda)."""
    return [a for a in anggota if a != TERTUNDA]


def username_tidak_ada(kelompok: list[Kelompok], jalankan=subprocess.run) -> list[str]:
    """Username yang tidak ditemukan di GitHub (cek lewat REST API users/<nama>)."""
    hilang = []
    for kel in kelompok:
        for a in username_aktif(kel.anggota):
            hasil = jalankan(["gh", "api", f"users/{a}", "--silent"], text=True, capture_output=True)
            if hasil.returncode != 0:
                hilang.append(f"@{a} ({kel.kelas}-{kel.topik})")
    return hilang


def teks_dari_baris(baris: str) -> str:
    """Ubah 'ka,t1,a;b;c | kb,t2,d e f' (atau dipisah baris baru) menjadi teks CSV berheader."""
    isi = [b.strip() for b in re.split(r"[|\n]", baris) if b.strip()]
    return "kelas,topik,anggota\n" + "\n".join(isi) + "\n"


# ---------------------------------------------------------------- rakit


def konteks(kelompok: Kelompok, data_topik: dict) -> dict:
    umum = data_topik["umum"]
    topik = next(t for t in data_topik["topik"] if t["kode"] == kelompok.topik)
    n = len(kelompok.anggota)
    return {
        "org": umum["organisasi"], "repo": kelompok.nama_repo(umum["awalan_repo"]), "kelas": kelompok.kelas,
        "repo_kelas": umum["repo_kelas"],
        "topik": topik, "anggota": n, "citra": umum["citra_per_anggota"] * n,
        "foto": umum["foto_sendiri_per_anggota"] * n, "klasik": umum["metode_klasik"][str(n)],
    }


def pengganti(k: dict) -> dict[str, str]:
    t = k["topik"]
    baris_hasil = [f"| [isi: nama metode klasik {i}] | klasik | [isi] | [isi] |" for i in range(1, k["klasik"] + 1)]
    baris_hasil.append("| [isi: nama model] | modern | [isi] | [isi] |")
    return {
        "{{ORG}}": k["org"], "{{REPO}}": k["repo"], "{{REPO_KELAS}}": k["repo_kelas"], "{{KELAS}}": k["kelas"], "{{KODE}}": t["kode"],
        "{{KODE_BESAR}}": t["kode"].upper(), "{{JUDUL}}": t["judul"], "{{SINGKAT}}": t["singkat"],
        "{{FOKUS}}": t["fokus"], "{{DEMO}}": t["demo"], "{{ETIKA}}": t["etika"], "{{ANOTASI}}": t["anotasi"],
        "{{MODE_APP}}": t["mode_app"], "{{LINGKUP_CONTOH}}": t["lingkup_contoh"][0],
        "{{METRIK_1}}": t["metrik"][0]["nama"], "{{METRIK_2}}": t["metrik"][1]["nama"],
        "{{JUMLAH_CITRA}}": str(k["citra"]), "{{JUMLAH_FOTO}}": str(k["foto"]), "{{JUMLAH_KLASIK}}": str(k["klasik"]),
        "{{BARIS_HASIL}}": "\n".join(baris_hasil),
    }


def isi_anggota(kelompok: Kelompok, k: dict) -> str:
    baris = [
        "# Anggota kelompok. Repo ini PUBLIK: jangan menulis NIM, email, atau nomor HP di sini.",
        "# nama : nama panggilan",
        "# peran: data, klasik, modern, evaluasi (boleh lebih dari satu, pisahkan dengan koma).",
        f"#        Keempat peran harus ada yang memegang. Lihat proyek/README.md di repo {k['repo_kelas']}.",
        f"kelas: {k['kelas']}",
        f"topik: {k['topik']['kode']}",
        "anggota:",
    ]
    for gh in kelompok.anggota:
        if gh == TERTUNDA:
            baris += ['  - github: "[isi: username GitHub, akan diisi dosen]"', '    nama: "[isi]"', '    peran: "[isi]"']
        else:
            baris += [f"  - github: {gh}", '    nama: "[isi]"', '    peran: "[isi]"']
    return "\n".join(baris) + "\n"


def isi_format_anotasi(topik: dict) -> str:
    keluaran = io.StringIO()
    penulis = csv.writer(keluaran, lineterminator="\n")
    penulis.writerow(topik["kolom_anotasi"])
    penulis.writerows(topik["contoh_anotasi"])
    return keluaran.getvalue()


def rakit(kelompok: Kelompok, data_topik: dict, tujuan: pathlib.Path) -> pathlib.Path:
    """Rakit folder repo lengkap untuk satu kelompok di tujuan/<nama repo>/."""
    k = konteks(kelompok, data_topik)
    folder = tujuan / k["repo"]
    if folder.exists():
        shutil.rmtree(folder)
    shutil.copytree(TEMPLATE, folder, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))
    ganti = pengganti(k)
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix in TEKS:
            teks = p.read_text(encoding="utf-8")
            for lama, baru in ganti.items():
                teks = teks.replace(lama, baru)
            sisa = re.findall(r"\{\{[A-Z_0-9]+\}\}", teks)
            if sisa:
                raise RuntimeError(f"placeholder tidak dikenal di {p.relative_to(folder)}: {sorted(set(sisa))}")
            p.write_text(teks, encoding="utf-8")
    (folder / "ANGGOTA.yml").write_text(isi_anggota(kelompok, k), encoding="utf-8")
    (folder / "data" / "format_anotasi.csv").write_text(isi_format_anotasi(k["topik"]), encoding="utf-8")
    (folder / "notebooks").mkdir(exist_ok=True)  # notebook dibangkitkan; folder ini tidak ada di template
    for nama, isi in notebook_proyek.bangun_semua(k).items():
        (folder / "notebooks" / nama).write_text(isi, encoding="utf-8")
    return folder


# ---------------------------------------------------------------- GitHub


def ruleset_main() -> dict:
    return {
        "name": "lindungi-main",
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [{"actor_id": 1, "actor_type": "OrganizationAdmin", "bypass_mode": "always"}],
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": 1, "dismiss_stale_reviews_on_push": False,
                "require_code_owner_review": False, "require_last_push_approval": False,
                "required_review_thread_resolution": False}},
            {"type": "required_status_checks", "parameters": {
                "strict_required_status_checks_policy": False,
                "required_status_checks": [{"context": "cek"}]}},
        ],
    }


def ruleset_tag() -> dict:
    return {
        "name": "kunci-tag-tahap",
        "target": "tag",
        "enforcement": "active",
        "bypass_actors": [{"actor_id": 1, "actor_type": "OrganizationAdmin", "bypass_mode": "always"}],
        "conditions": {"ref_name": {"include": ["refs/tags/tahap-*"], "exclude": []}},
        "rules": [{"type": "deletion"}, {"type": "update"}, {"type": "non_fast_forward"}],
    }


class GitHub:
    """Pembungkus gh/git. Dengan dry_run=True perintah hanya dicetak (dan dicatat di self.log)."""

    def __init__(self, dry_run: bool = False, keluaran=print):
        self.dry_run = dry_run
        self.log: list[list[str]] = []
        self.cetak = keluaran

    def jalankan(self, *perintah: str, masukan: str | None = None, ubah: bool = True) -> str:
        perintah = [str(p) for p in perintah]
        self.log.append(perintah)
        if self.dry_run and ubah:
            self.cetak("[dry-run] " + " ".join(perintah))
            return ""
        hasil = subprocess.run(perintah, input=masukan, text=True, capture_output=True)
        if hasil.returncode != 0:
            raise RuntimeError(f"gagal: {' '.join(perintah)}\n{hasil.stderr.strip()}")
        return hasil.stdout

    def ada(self, *perintah: str) -> bool:
        if self.dry_run:
            return False
        try:
            self.jalankan(*perintah, ubah=False)
            return True
        except RuntimeError:
            return False

    def api_json(self, path: str):
        keluaran = self.jalankan("gh", "api", path, ubah=False) if not self.dry_run else "[]"
        return json.loads(keluaran or "null")


def commit_awal(gh: GitHub, folder: pathlib.Path, pesan: str):
    gh.jalankan("git", "-C", folder, "init", "-q", "-b", "main")
    gh.jalankan("git", "-C", folder, "add", "-A")
    gh.jalankan("git", "-C", folder, "commit", "-q", "-m", pesan)


def pasang_ruleset(gh: GitHub, nama_penuh: str):
    ada = {r.get("name") for r in (gh.api_json(f"repos/{nama_penuh}/rulesets") or [])}
    for aturan in (ruleset_main(), ruleset_tag()):
        if aturan["name"] in ada:
            gh.cetak(f"  ruleset {aturan['name']} sudah ada")
            continue
        gh.jalankan("gh", "api", "-X", "POST", f"repos/{nama_penuh}/rulesets", "--input", "-", masukan=json.dumps(aturan))


def pasang_label(gh: GitHub, nama_penuh: str):
    for nama, (warna, ket) in LABEL.items():
        try:
            gh.jalankan("gh", "api", "-X", "POST", f"repos/{nama_penuh}/labels", "-f", f"name={nama}",
                        "-f", f"color={warna}", "-f", f"description={ket}", "--silent")
        except RuntimeError:  # label sudah ada: samakan warna dan keterangannya
            gh.jalankan("gh", "api", "-X", "PATCH", f"repos/{nama_penuh}/labels/{nama}",
                        "-f", f"color={warna}", "-f", f"description={ket}", "--silent")


def undang(gh: GitHub, nama_penuh: str, anggota):
    tertunda = len(anggota) - len(username_aktif(anggota))
    if tertunda:
        gh.cetak(f"  {tertunda} anggota tertunda (username belum diketahui) belum diundang")
    for a in username_aktif(anggota):
        gh.jalankan("gh", "api", "-X", "PUT", f"repos/{nama_penuh}/collaborators/{a}", "-f", "permission=push")


def perbarui_dikelola(gh: GitHub, folder_baru: pathlib.Path, nama_penuh: str, kerja: pathlib.Path):
    klon = kerja / f"klon-{folder_baru.name}"
    gh.jalankan("git", "clone", "-q", f"https://github.com/{nama_penuh}.git", klon)
    if gh.dry_run:
        return
    for rel in DIKELOLA:
        sumber, tujuan = folder_baru / rel, klon / rel
        if sumber.is_dir():
            shutil.rmtree(tujuan, ignore_errors=True)
            shutil.copytree(sumber, tujuan)
        elif sumber.is_file():
            tujuan.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sumber, tujuan)
    gh.jalankan("git", "-C", klon, "add", "-A")
    if not gh.jalankan("git", "-C", klon, "status", "--porcelain", ubah=False).strip():
        gh.cetak(f"  {nama_penuh}: berkas dikelola sudah mutakhir")
        return
    gh.jalankan("git", "-C", klon, "commit", "-q", "-m", "dosen: perbarui pemeriksaan cek dan alat bantu")
    gh.jalankan("git", "-C", klon, "push", "-q", "origin", "HEAD:main")
    gh.cetak(f"  {nama_penuh}: berkas dikelola diperbarui")


def status_repo(gh: GitHub, nama_penuh: str) -> str:
    """'tidak_ada', 'kosong' (sudah dibuat tetapi belum ada commit), atau 'berisi'. Hanya REST API."""
    if not gh.ada("gh", "api", f"repos/{nama_penuh}", "--silent"):
        return "tidak_ada"
    return "berisi" if gh.ada("gh", "api", f"repos/{nama_penuh}/commits?per_page=1", "--silent") else "kosong"


def dorong_awal(gh: GitHub, folder: pathlib.Path, nama_penuh: str, pesan: str):
    commit_awal(gh, folder, pesan)
    gh.jalankan("git", "-C", folder, "remote", "add", "origin", f"https://github.com/{nama_penuh}.git")
    gh.jalankan("git", "-C", folder, "push", "-q", "-u", "origin", "main")


def atur_repo(gh: GitHub, nama_penuh: str, deskripsi: str):
    gh.jalankan("gh", "api", "-X", "PATCH", f"repos/{nama_penuh}", "-f", f"description={deskripsi}",
                "-F", "has_wiki=false", "-F", "has_projects=false", "-F", "delete_branch_on_merge=true", "--silent")


PENANDA_TERTUNDA = '"[isi: username GitHub, akan diisi dosen]"'


def isi_tertunda(kelompok: list[Kelompok], data_topik: dict, gh: GitHub):
    """Ganti anggota tertunda di ANGGOTA.yml dengan username yang baru diketahui, lalu undang.

    Di sini `kelompok.anggota` berisi username BARU saja. Didorong langsung ke main (owner bypass ruleset).
    """
    org, awalan = data_topik["umum"]["organisasi"], data_topik["umum"]["awalan_repo"]
    with tempfile.TemporaryDirectory() as tmp:
        for kel in kelompok:
            nama_penuh = f"{org}/{kel.nama_repo(awalan)}"
            baru = username_aktif(kel.anggota)
            gh.cetak(f"\n== {nama_penuh}: isi anggota tertunda dengan {', '.join('@' + b for b in baru)}")
            klon = pathlib.Path(tmp) / kel.nama_repo(awalan)
            gh.jalankan("git", "clone", "-q", "--depth", "1", f"https://github.com/{nama_penuh}.git", klon)
            if gh.dry_run:
                undang(gh, nama_penuh, baru)
                continue
            berkas = klon / "ANGGOTA.yml"
            teks = berkas.read_text(encoding="utf-8")
            if teks.count(PENANDA_TERTUNDA) < len(baru):
                raise SystemExit(f"{nama_penuh}: hanya {teks.count(PENANDA_TERTUNDA)} anggota tertunda, "
                                 f"tetapi {len(baru)} username diberikan")
            for b in baru:
                teks = teks.replace(PENANDA_TERTUNDA, b, 1)
            berkas.write_text(teks, encoding="utf-8")
            gh.jalankan("git", "-C", klon, "add", "ANGGOTA.yml")
            gh.jalankan("git", "-C", klon, "commit", "-q", "-m", f"dosen: isi username anggota tertunda ({', '.join(baru)})")
            gh.jalankan("git", "-C", klon, "push", "-q", "origin", "HEAD:main")
            undang(gh, nama_penuh, baru)


def siapkan(kelompok: list[Kelompok], data_topik: dict, gh: GitHub, perbarui: bool = False, undangan: bool = True):
    org, awalan = data_topik["umum"]["organisasi"], data_topik["umum"]["awalan_repo"]
    with tempfile.TemporaryDirectory() as tmp:
        kerja = pathlib.Path(tmp)
        for kel in kelompok:
            nama = kel.nama_repo(awalan)
            nama_penuh = f"{org}/{nama}"
            gh.cetak(f"\n== {nama_penuh} ({len(kel.anggota)} anggota: {', '.join(kel.anggota)})")
            folder = rakit(kel, data_topik, kerja)
            topik = next(t for t in data_topik["topik"] if t["kode"] == kel.topik)
            deskripsi = f"Proyek kelompok PCD 2026 kelas {kel.kelas}: {topik['judul']}"
            pesan = f"proyek: repo awal {nama} dari {data_topik['umum']['repo_kelas']}"
            status = status_repo(gh, nama_penuh)
            if status == "berisi":
                if perbarui:
                    perbarui_dikelola(gh, folder, nama_penuh, kerja)
                else:
                    gh.cetak("  repo sudah berisi (pakai --perbarui untuk mendorong ulang berkas dikelola)")
            else:
                if status == "tidak_ada":
                    gh.jalankan("gh", "api", "-X", "POST", f"orgs/{org}/repos", "-f", f"name={nama}",
                                "-F", "private=false", "-f", f"description={deskripsi}", "--silent")
                else:
                    gh.cetak("  repo sudah dibuat tetapi masih kosong: isi awal didorong")
                dorong_awal(gh, folder, nama_penuh, pesan)
                atur_repo(gh, nama_penuh, deskripsi)
            pasang_ruleset(gh, nama_penuh)
            pasang_label(gh, nama_penuh)
            if undangan:
                undang(gh, nama_penuh, kel.anggota)
            else:
                gh.cetak("  undangan dilewati (--tanpa-undangan)")


def cek_izin_gh(jalankan=subprocess.run):
    """Pastikan token gh sah dan (untuk token classic) punya scope 'workflow' agar .github/workflows bisa didorong.

    Memakai `gh api -i user`, bukan `gh auth status`, karena `gh auth status` gagal untuk token
    yang sah tetapi tanpa scope read:org, padahal read:org tidak dibutuhkan skrip ini.
    """
    if not shutil.which("gh"):
        raise SystemExit("gh CLI belum terpasang: https://cli.github.com")
    hasil = jalankan(["gh", "api", "-i", "user"], text=True, capture_output=True)
    if hasil.returncode != 0:
        raise SystemExit("Token gh tidak sah atau belum login. Periksa secret ORG_ADMIN_TOKEN, "
                         "atau jalankan: gh auth login -s workflow\n" + (hasil.stderr or "").strip())
    cocok = re.search(r"^x-oauth-scopes:\s*(.*)$", hasil.stdout or "", re.IGNORECASE | re.MULTILINE)
    if cocok and "workflow" not in cocok.group(1):
        raise SystemExit("Token classic belum punya scope 'workflow' (dibutuhkan untuk mendorong .github/workflows).\n"
                         "Tambahkan scope workflow pada token, atau: gh auth refresh -h github.com -s workflow")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", type=pathlib.Path, nargs="?", help="berkas kelompok (kelas,topik,anggota)")
    parser.add_argument("--baris", help="kelompok tanpa berkas: 'ka,t1,andi;budi;cici | ka,t2,…' (baris dipisah | atau baris baru)")
    parser.add_argument("--dry-run", action="store_true", help="hanya tampilkan perintah")
    parser.add_argument("--rakit", type=pathlib.Path, metavar="FOLDER", help="hanya rakit isi repo ke FOLDER, tanpa GitHub")
    parser.add_argument("--perbarui", action="store_true", help="dorong ulang berkas dikelola ke repo yang sudah ada")
    parser.add_argument("--tanpa-undangan", action="store_true", help="jangan undang anggota (untuk repo uji coba)")
    parser.add_argument("--isi-tertunda", action="store_true",
                        help="ganti anggota '?' di repo yang sudah ada dengan username di kolom anggota, lalu undang")
    arg = parser.parse_args(argv)
    data = muat_topik()
    if bool(arg.csv) == bool(arg.baris):
        parser.error("berikan berkas CSV atau --baris (salah satu)")
    teks = arg.csv.read_text(encoding="utf-8") if arg.csv else teks_dari_baris(arg.baris)
    kelompok = baca_tambahan(teks) if arg.isi_tertunda else baca_kelompok(teks, data)
    print(f"{len(kelompok)} kelompok valid.")
    if arg.rakit:
        arg.rakit.mkdir(parents=True, exist_ok=True)
        for kel in kelompok:
            print(rakit(kel, data, arg.rakit))
        return 0
    if not arg.dry_run or os.environ.get("GH_TOKEN"):
        if not arg.dry_run:
            cek_izin_gh()
        hilang = username_tidak_ada(kelompok)
        if hilang:
            raise SystemExit("Username GitHub tidak ditemukan (tidak ada yang diubah):\n  " + "\n  ".join(hilang))
        print("Semua username ditemukan di GitHub.")
    if not arg.dry_run:
        subprocess.run(["gh", "auth", "setup-git"], check=False)  # git push memakai login gh
    if arg.isi_tertunda:
        isi_tertunda(kelompok, data, GitHub(dry_run=arg.dry_run))
        return 0
    siapkan(kelompok, data, GitHub(dry_run=arg.dry_run), perbarui=arg.perbarui, undangan=not arg.tanpa_undangan)
    print("\nSelesai. Bagikan tautan repo ke tiap kelompok; anggota harus menerima undangan kolaborator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
