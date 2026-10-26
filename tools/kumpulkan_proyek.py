"""Rekap pengumpulan proyek kelompok: waktu Release, keterlambatan, hasil cek, dan kontribusi anggota.

Untuk setiap repo <awalan>-* di organisasi:
  - cari Release bertag tahap-1 / tahap-2 dan waktu pembuatannya (dicatat server GitHub),
  - hitung keterlambatan dan denda sesuai proyek/topik.json,
  - ambil hasil pemeriksaan "cek" pada commit tag,
  - hitung commit dan pull request (yang di-merge sebelum Release) per anggota di ANGGOTA.yml,
  - (opsional --klon) klon repo pada tag dan jalankan ulang cek_proyek.py versi dosen,
    sehingga perubahan .github/ oleh kelompok tidak memengaruhi penilaian.

Pemakaian:
    python tools/kumpulkan_proyek.py --tahap 1 -o rekap-tahap1.csv
    python tools/kumpulkan_proyek.py --tahap 2 --tenggat "2027-01-10 23:59" --kelas ka --klon ~/proyek-uas
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import json
import math
import pathlib
import subprocess
import sys

AKAR = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = AKAR / "proyek" / "template" / ".github" / "scripts" / "cek_proyek.py"
WIB = dt.timezone(dt.timedelta(hours=7))


class Gh:
    """Panggilan gh api. Bisa diganti tiruan di tes."""

    def api(self, path: str):
        hasil = subprocess.run(["gh", "api", path], text=True, capture_output=True)
        if hasil.returncode != 0:
            if "Not Found" in hasil.stderr or "404" in hasil.stderr:
                return None
            raise RuntimeError(f"gh api {path} gagal: {hasil.stderr.strip()}")
        return json.loads(hasil.stdout or "null")

    def api_halaman(self, path: str, per_halaman: int = 100) -> list:
        semua, halaman = [], 1
        pemisah = "&" if "?" in path else "?"
        while True:
            data = self.api(f"{path}{pemisah}per_page={per_halaman}&page={halaman}") or []
            semua += data
            if len(data) < per_halaman:
                return semua
            halaman += 1


def baca_waktu(teks: str) -> dt.datetime:
    """'2026-11-08 23:59' (dianggap WIB) atau ISO 8601 dengan zona waktu."""
    waktu = dt.datetime.fromisoformat(teks.strip().replace("Z", "+00:00"))
    return waktu if waktu.tzinfo else waktu.replace(tzinfo=WIB)


def denda(waktu_release: dt.datetime, tenggat: dt.datetime, per_24_jam: int, batas_hari: int) -> tuple[float, int | None]:
    """(jam terlambat, denda poin). Denda None = melewati batas, tahap tidak dinilai."""
    jam = (waktu_release - tenggat).total_seconds() / 3600
    if jam <= 0:
        return 0.0, 0
    hari = math.ceil(jam / 24)
    return round(jam, 2), (None if hari > batas_hari else hari * per_24_jam)


def sha_tag(gh: Gh, repo: str, tag: str) -> str | None:
    ref = gh.api(f"repos/{repo}/git/ref/tags/{tag}")
    if not ref:
        return None
    obj = ref["object"]
    while obj["type"] == "tag":  # tag beranotasi: ikuti ke commit
        obj = gh.api(f"repos/{repo}/git/tags/{obj['sha']}")["object"]
    return obj["sha"]


def anggota_pada(gh: Gh, repo: str, sha: str) -> list[str]:
    isi = gh.api(f"repos/{repo}/contents/ANGGOTA.yml?ref={sha}")
    if not isi:
        return []
    teks = base64.b64decode(isi["content"]).decode("utf-8")
    try:
        import yaml
        data = yaml.safe_load(teks) or {}
        return [str(a.get("github", "")).lstrip("@") for a in data.get("anggota", []) if isinstance(a, dict)]
    except Exception:  # noqa: BLE001 - YAML rusak: tetap ambil baris github:
        return [b.split(":", 1)[1].strip().lstrip("@") for b in teks.splitlines() if b.strip().startswith("- github:")]


def kontribusi(gh: Gh, repo: str, sha: str, sebelum: dt.datetime) -> dict[str, dict[str, int]]:
    hasil: dict[str, dict[str, int]] = {}

    def tambah(login, kunci):
        if login:
            d = hasil.setdefault(login.lower(), {"commit": 0, "pr": 0})
            d[kunci] += 1

    for c in gh.api_halaman(f"repos/{repo}/commits?sha={sha}"):
        tambah((c.get("author") or {}).get("login"), "commit")
    for p in gh.api_halaman(f"repos/{repo}/pulls?state=closed"):
        if p.get("merged_at") and baca_waktu(p["merged_at"]) <= sebelum:
            tambah((p.get("user") or {}).get("login"), "pr")
    return hasil


def status_cek(gh: Gh, repo: str, sha: str) -> str:
    data = gh.api(f"repos/{repo}/commits/{sha}/check-runs") or {}
    runs = [r for r in data.get("check_runs", []) if r.get("name") == "cek"]
    if not runs:
        return "tidak ada"
    terbaru = max(runs, key=lambda r: r.get("completed_at") or r.get("started_at") or "")
    return terbaru.get("conclusion") or terbaru.get("status") or "?"


def cek_dosen(repo: str, tag: str, tahap: int, folder: pathlib.Path) -> str:
    tujuan = folder / repo.split("/")[1]
    if not tujuan.exists():
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", tag, f"https://github.com/{repo}.git", str(tujuan)], check=True)
    hasil = subprocess.run([sys.executable, str(VALIDATOR), "--akar", str(tujuan), "--tahap", str(tahap)], text=True, capture_output=True)
    galat = [b.split("::", 2)[2] for b in hasil.stdout.splitlines() if b.startswith("::error")]
    return "lulus" if hasil.returncode == 0 else "gagal: " + " | ".join(galat)


def rekap_repo(gh: Gh, repo: str, tahap: int, tenggat: dt.datetime | None, aturan: dict, folder_klon=None) -> dict:
    tag = f"tahap-{tahap}"
    nama = repo.split("/")[1]
    bagian = nama.split("-")
    baris = {"repo": repo, "kelas": bagian[1] if len(bagian) > 2 else "", "topik": bagian[-1], "release": "",
             "waktu_release_wib": "", "jam_terlambat": "", "denda": "", "cek_github": "", "cek_dosen": "",
             "anggota": "", "kontribusi": "", "tanpa_kontribusi": ""}
    release = gh.api(f"repos/{repo}/releases/tags/{tag}")
    if not release:
        baris["release"] = "BELUM ADA"
        return baris
    waktu = baca_waktu(release.get("published_at") or release["created_at"])
    baris["release"] = release.get("html_url", "")
    baris["waktu_release_wib"] = waktu.astimezone(WIB).strftime("%Y-%m-%d %H:%M")
    if tenggat:
        jam, poin = denda(waktu, tenggat, aturan["denda_terlambat_per_24_jam"], aturan["batas_terlambat_hari"])
        baris["jam_terlambat"] = jam
        baris["denda"] = "tidak dinilai" if poin is None else poin
    sha = sha_tag(gh, repo, tag)
    if not sha:
        baris["cek_github"] = "tag tidak ditemukan"
        return baris
    baris["cek_github"] = status_cek(gh, repo, sha)
    anggota = anggota_pada(gh, repo, sha)
    kontrib = kontribusi(gh, repo, sha, waktu)
    baris["anggota"] = " ".join(anggota)
    baris["kontribusi"] = "; ".join(
        f"{a}: {kontrib.get(a.lower(), {}).get('commit', 0)} commit, {kontrib.get(a.lower(), {}).get('pr', 0)} PR" for a in anggota)
    baris["tanpa_kontribusi"] = " ".join(a for a in anggota if not any(kontrib.get(a.lower(), {}).values()))
    if folder_klon:
        baris["cek_dosen"] = cek_dosen(repo, tag, tahap, pathlib.Path(folder_klon))
    return baris


def daftar_repo(gh: Gh, org: str, awalan: str, kelas: str | None) -> list[str]:
    semua = gh.api_halaman(f"orgs/{org}/repos?type=all")
    pola = f"{awalan}-{kelas}-" if kelas else f"{awalan}-"
    return sorted(r["full_name"] for r in semua if r["name"].startswith(pola) and not r.get("archived"))


def main(argv=None, gh: Gh | None = None) -> int:
    data = json.loads((AKAR / "proyek" / "topik.json").read_text(encoding="utf-8"))
    umum = data["umum"]
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tahap", type=int, choices=[1, 2], required=True)
    parser.add_argument("--tenggat", help="mis. '2026-11-08 23:59' (WIB). Bawaan: proyek/topik.json")
    parser.add_argument("--kelas", help="hanya kelas ini, mis. ka")
    parser.add_argument("--repo", action="append", help="repo tertentu (org/nama), boleh berulang")
    parser.add_argument("--klon", type=pathlib.Path, help="folder klon untuk menjalankan ulang cek versi dosen")
    parser.add_argument("-o", "--keluaran", type=pathlib.Path, default=None, help="berkas CSV (bawaan: layar)")
    arg = parser.parse_args(argv)
    gh = gh or Gh()
    teks_tenggat = arg.tenggat or umum["tenggat"].get(f"tahap-{arg.tahap}")
    tenggat = baca_waktu(teks_tenggat) if teks_tenggat else None
    if tenggat is None:
        print("Peringatan: tenggat belum diatur; keterlambatan tidak dihitung.", file=sys.stderr)
    if arg.klon:
        arg.klon.mkdir(parents=True, exist_ok=True)
    repo = arg.repo or daftar_repo(gh, umum["organisasi"], umum["awalan_repo"], arg.kelas)
    baris = [rekap_repo(gh, r, arg.tahap, tenggat, umum, arg.klon) for r in repo]
    kolom = list(baris[0]) if baris else ["repo"]
    tujuan = open(arg.keluaran, "w", newline="", encoding="utf-8") if arg.keluaran else sys.stdout
    try:
        penulis = csv.DictWriter(tujuan, fieldnames=kolom)
        penulis.writeheader()
        penulis.writerows(baris)
    finally:
        if arg.keluaran:
            tujuan.close()
    belum = [b["repo"] for b in baris if b.get("release") == "BELUM ADA"]
    print(f"{len(baris)} repo direkap; {len(belum)} belum membuat Release tahap-{arg.tahap}.", file=sys.stderr)
    for b in belum:
        print(f"  belum: {b}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
