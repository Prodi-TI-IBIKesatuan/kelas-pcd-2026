"""Tes alat proyek kelompok: topik.json, perakitan repo, pemeriksaan cek, GitHub (tiruan), rekap, dan duplikat."""
from __future__ import annotations

import ast
import base64
import datetime as dt
import importlib.util
import json
import os
import pathlib
import re
import sys

import cv2
import nbformat
import numpy as np
import pytest
import yaml

ALAT = pathlib.Path(__file__).resolve().parents[1]
AKAR = ALAT.parent
sys.path.insert(0, str(ALAT))

import buat_dokumen_proyek  # noqa: E402
import buat_repo_proyek as brp  # noqa: E402
import cek_duplikat_citra  # noqa: E402
import kumpulkan_proyek as kp  # noqa: E402
import notebook_proyek  # noqa: E402

DATA = brp.muat_topik()
KODE = [t["kode"] for t in DATA["topik"]]
CSV_CONTOH = "kelas,topik,anggota\nka,t1,andi-dev;budi99;citra-s\nka,t2,dewi;eko;fajar;gita;hana\nka,t3,ika;joko;kiki;lala\nkb,t1,mira;nina;opa\nkb,t4,qq;rr;ss\nkb,t5,tt;uu;vv\n"


def _modul(path: pathlib.Path, nama: str):
    spec = importlib.util.spec_from_file_location(nama, path)
    modul = importlib.util.module_from_spec(spec)
    sys.modules[nama] = modul
    spec.loader.exec_module(modul)
    return modul


CEK = _modul(brp.TEMPLATE / ".github" / "scripts" / "cek_proyek.py", "cek_proyek")
sys.path.insert(0, str(brp.TEMPLATE))
from pcd_proyek import evaluasi as ev_template, metrik as metrik_template  # noqa: E402


@pytest.fixture(scope="module")
def kelompok():
    return brp.baca_kelompok(CSV_CONTOH, DATA)


@pytest.fixture()
def repo(tmp_path, kelompok):
    """Repo kelompok 5 orang topik t2 yang baru dirakit."""
    return brp.rakit(kelompok[1], DATA, tmp_path)


# ---------------------------------------------------------------- topik.json dan dokumen


def test_topik_lengkap_dan_konsisten():
    assert KODE == ["t1", "t2", "t3", "t4", "t5"]
    nama_evaluator = {"t1": "evaluasi_pelat", "t2": "evaluasi_berreferensi", "t3": "evaluasi_berreferensi",
                      "t4": "evaluasi_ocr", "t5": "evaluasi_temu_kembali"}
    for t in DATA["topik"]:
        assert len(t["metrik"]) == 2 and t["mode_app"] in {"gambar_teks", "gambar_gambar", "galeri"}
        for m in t["metrik"]:
            assert hasattr(metrik_template, m["fungsi"]), m
        assert all(len(b) == len(t["kolom_anotasi"]) for b in t["contoh_anotasi"])
        for kamus in (notebook_proyek.PRAPROSES, notebook_proyek.STUB_KLASIK, notebook_proyek.PANGGIL_EVALUASI,
                      notebook_proyek.KASUS_GAGAL, notebook_proyek.CONTOH_MODERN, notebook_proyek.ABLASI):
            assert t["kode"] in kamus
        assert nama_evaluator[t["kode"]] in notebook_proyek.PANGGIL_EVALUASI[t["kode"]]
        for kolom in ("judul", "demo", "singkat"):  # disisipkan ke string Python di app.py
            assert '"' not in t[kolom] and "\\" not in t[kolom]
    umum = DATA["umum"]
    assert {int(n) for n in umum["metode_klasik"]} == set(range(umum["anggota_min"], umum["anggota_max"] + 1))
    assert all(CEK.jumlah_klasik_wajib(int(n)) == v for n, v in umum["metode_klasik"].items())
    assert list(umum["peran"]) == list(CEK.PERAN)
    assert (umum["anggota_min"], umum["anggota_max"]) == (CEK.ANGGOTA_MIN, CEK.ANGGOTA_MAKS)


def test_nama_metrik_sama_dengan_keluaran_evaluator(tmp_path):
    """Kolom tabel README (topik.json) harus sama dengan kunci metrik evaluator, agar tabel_markdown terisi."""
    citra = np.full((20, 20, 3), 100, np.uint8)
    cv2.imwrite(str(tmp_path / "a.png"), citra)
    cv2.imwrite(str(tmp_path / "b.png"), citra)
    keluaran = {
        "t1": ev_template.evaluasi_pelat(lambda c: ((0, 0, 5, 5), "A"), [{"berkas": "a.png", "x": "0", "y": "0", "w": "5", "h": "5", "teks_pelat": "A"}], tmp_path),
        "t2": ev_template.evaluasi_berreferensi(lambda c: c, [{"berkas_gelap": "a.png", "berkas_referensi": "b.png"}], tmp_path, "berkas_gelap", "berkas_referensi"),
        "t3": ev_template.evaluasi_berreferensi(lambda c: c, [{"berkas_rusak": "a.png", "berkas_bersih": "b.png"}], tmp_path, "berkas_rusak", "berkas_bersih"),
        "t4": ev_template.evaluasi_ocr(lambda c: ("A", {}), [{"berkas": "a.png", "teks_lengkap": "A", "tanggal": "", "total": ""}], tmp_path),
        "t5": ev_template.evaluasi_temu_kembali(lambda c: c.mean(axis=(0, 1)), [{"berkas": "a.png", "kategori": "x"}, {"berkas": "b.png", "kategori": "x"}], tmp_path),
    }
    for t in DATA["topik"]:
        for m in t["metrik"]:
            assert m["nama"] in keluaran[t["kode"]]["metrik"], (t["kode"], m["nama"])


def test_dokumen_topik_sinkron():
    assert buat_dokumen_proyek.main(["--cek"]) == 0
    isi = buat_dokumen_proyek.bangun(DATA)
    assert all(f"## {k.upper()} — " in isi for k in KODE)


# ---------------------------------------------------------------- CSV kelompok


def test_baca_kelompok_valid(kelompok):
    assert [k.nama_repo("pcd2026") for k in kelompok] == [
        "pcd2026-ka-t1", "pcd2026-ka-t2", "pcd2026-ka-t3", "pcd2026-kb-t1", "pcd2026-kb-t4", "pcd2026-kb-t5"]
    assert kelompok[1].anggota == ("dewi", "eko", "fajar", "gita", "hana")
    spasi = brp.baca_kelompok("﻿Kelas,Topik,Anggota\nKA,T1,@a1 a2;a3\n\n", DATA)
    assert spasi == [brp.Kelompok("ka", "t1", ("a1", "a2", "a3"))]


@pytest.mark.parametrize("csv_teks, pesan", [
    ("kelas,topik,anggota\nka,t1,a;b;c\nka,t1,d;e;f\n", "sudah diambil"),
    ("kelas,topik,anggota\nka,t9,a;b;c\n", "tidak dikenal"),
    ("kelas,topik,anggota\nka,t1,a;b\n", "2 anggota"),
    ("kelas,topik,anggota\nka,t1,a;b;c;d;e;f\n", "6 anggota"),
    ("kelas,topik,anggota\nka,t1,a;b;-salah\n", "tidak sah"),
    ("kelas,topik,anggota\nka,t1,a;b;c\nkb,t1,C;d;e\n", "sudah terdaftar"),
    ("kelas,topik,anggota\nKelas A,t1,a;b;c\n", "kode kelas"),
    ("nama,topik\nx,t1\n", "berkolom"),
    ("kelas,topik,anggota\n", "kosong"),
])
def test_baca_kelompok_menolak_masalah(csv_teks, pesan):
    with pytest.raises(SystemExit, match=pesan):
        brp.baca_kelompok(csv_teks, DATA)


# ---------------------------------------------------------------- perakitan repo


def test_rakit_semua_topik(tmp_path, kelompok):
    for kel in kelompok:
        folder = brp.rakit(kel, DATA, tmp_path)
        for p in folder.rglob("*"):
            if p.is_file() and p.suffix in {".md", ".py", ".yml", ".csv", ".ipynb", ""}:
                teks = p.read_text(encoding="utf-8")
                assert not re.findall(r"\{\{[A-Z_0-9]+\}\}", teks), p
        anggota = yaml.safe_load((folder / "ANGGOTA.yml").read_text(encoding="utf-8"))
        assert [a["github"] for a in anggota["anggota"]] == list(kel.anggota)
        assert anggota["topik"] == kel.topik and anggota["kelas"] == kel.kelas
        for nb in sorted((folder / "notebooks").glob("*.ipynb")):
            isi = nbformat.read(nb, as_version=4)
            nbformat.validate(isi)
            for sel in isi.cells:
                if sel.cell_type == "code":
                    ast.parse(sel.source)
            assert f"{brp.muat_topik()['umum']['organisasi']}/{folder.name}" in nb.read_text(encoding="utf-8")
        ast.parse((folder / "app" / "app.py").read_text(encoding="utf-8"))
        readme = (folder / "README.md").read_text(encoding="utf-8")
        jumlah_klasik = 3 if len(kel.anggota) == 5 else 2
        assert readme.count("| klasik |") == jumlah_klasik and readme.count("| modern |") == 1
        assert f"colab.research.google.com/github/Prodi-TI-IBIKesatuan/{folder.name}/blob/main/notebooks/01_" in readme
        assert CEK.main(["--akar", str(folder)]) == 0


def test_rakit_menolak_placeholder_asing(tmp_path, kelompok, monkeypatch):
    template = tmp_path / "template"
    import shutil
    shutil.copytree(brp.TEMPLATE, template)
    (template / "CATATAN.md").write_text("halo {{TIDAK_ADA}}\n", encoding="utf-8")
    monkeypatch.setattr(brp, "TEMPLATE", template)
    with pytest.raises(RuntimeError, match="TIDAK_ADA"):
        brp.rakit(kelompok[0], DATA, tmp_path / "keluaran")


# ---------------------------------------------------------------- pemeriksaan cek


def _isi_lengkap(folder: pathlib.Path, n_figur: int = 10, n_sample: int = 5):
    """Isi semua [isi…] seolah kelompok sudah menyelesaikan tahap 1 dan 2."""
    data = yaml.safe_load((folder / "ANGGOTA.yml").read_text(encoding="utf-8"))
    peran = ["data", "klasik", "klasik, evaluasi", "modern", "evaluasi"]
    for i, a in enumerate(data["anggota"]):
        a["nama"] = f"Anggota {i}"
        a["peran"] = peran[i % len(peran)] if len(data["anggota"]) >= 4 else ["data, klasik", "modern", "evaluasi"][i]
    (folder / "ANGGOTA.yml").write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    readme = (folder / "README.md").read_text(encoding="utf-8")
    readme = re.sub(r"\*\*Lingkup kelompok kami:\*\* \[isi[^\]]*\]", "**Lingkup kelompok kami:** foto jalan malam", readme)
    readme = re.sub(r"\[isi: tautan https://huggingface.co/spaces/\.\.\.\]", "https://huggingface.co/spaces/kel/demo-pcd", readme)
    readme = re.sub(r"\[isi[^\]]*\]", "terisi", readme)
    (folder / "README.md").write_text(readme, encoding="utf-8")
    data_readme = (folder / "data" / "README.md").read_text(encoding="utf-8")
    data_readme = data_readme.replace("[isi: https://drive.google.com/drive/folders/...]", "https://drive.google.com/drive/folders/abc123")
    (folder / "data" / "README.md").write_text(re.sub(r"\[isi[^\]]*\]", "terisi", data_readme), encoding="utf-8")
    kecil = np.zeros((8, 8, 3), np.uint8)
    for i in range(n_sample):
        cv2.imwrite(str(folder / "data" / "sample" / f"s{i}.jpg"), kecil)
    for i in range(n_figur):
        cv2.imwrite(str(folder / "outputs" / "figures" / f"f{i}.png"), kecil)
    for nb in (folder / "notebooks").glob("*.ipynb"):
        isi = json.loads(nb.read_text(encoding="utf-8"))
        for n, sel in enumerate(c for c in isi["cells"] if c["cell_type"] == "code"):
            sel["execution_count"] = n + 1
            sel["outputs"] = [{"output_type": "stream", "name": "stdout", "text": ["ok\n"]}]
        nb.write_text(json.dumps(isi), encoding="utf-8")


def _galat(folder, tahap):
    temuan, _ = CEK.periksa(folder, tahap)
    return [t.pesan for t in temuan if t.tingkat == "galat"]


def test_cek_lulus_setelah_lengkap(repo, tmp_path):
    assert _galat(repo, 1) and _galat(repo, 2)
    _isi_lengkap(repo)
    assert _galat(repo, 1) == [] and _galat(repo, 2) == []
    ringkasan = tmp_path / "ringkasan.md"
    assert CEK.main(["--akar", str(repo), "--ringkasan", str(ringkasan)]) == 0
    teks = ringkasan.read_text(encoding="utf-8")
    assert "Siap tahap-1" in teks and "Siap tahap-2" in teks


def test_cek_kesiapan_tahap2_tidak_mengulang_tahap1(repo):
    _, info = CEK.periksa(repo, 0)
    assert info["kesiapan"]["tahap-1"] and info["kesiapan"]["tahap-2"]
    assert not set(info["kesiapan"]["tahap-1"]) & set(info["kesiapan"]["tahap-2"])
    teks = CEK.ringkasan_markdown([], info, 0)
    assert "Belum siap tahap-2" in teks and "Selain kekurangan tahap-1" in teks


def test_cek_menolak_pelanggaran(repo):
    _isi_lengkap(repo)
    (repo / "data" / "dataset_lengkap").mkdir()
    cv2.imwrite(str(repo / "data" / "dataset_lengkap" / "x.jpg"), np.zeros((4, 4, 3), np.uint8))
    for i in range(21):
        cv2.imwrite(str(repo / "data" / "sample" / f"lebih{i}.jpg"), np.zeros((4, 4, 3), np.uint8))
    (repo / "bobot.bin").write_bytes(b"0" * 10_500_000)
    data = yaml.safe_load((repo / "ANGGOTA.yml").read_text(encoding="utf-8"))
    data["anggota"][0]["nim"] = "2401"
    data["anggota"][1]["peran"] = "penulis"
    data["anggota"][2]["github"] = data["anggota"][3]["github"]
    (repo / "ANGGOTA.yml").write_text(yaml.safe_dump(data), encoding="utf-8")
    galat = " | ".join(_galat(repo, 0))
    for kata in ("di luar folder", "data/sample/ berisi 26", "bobot.bin berukuran", "hapus 'nim'", "peran tidak dikenal", "username ganda"):
        assert kata in galat, kata


def test_cek_tahap2_jumlah_metode_dan_notebook_error(repo):
    _isi_lengkap(repo)
    readme = (repo / "README.md").read_text(encoding="utf-8")
    baris_klasik = [b for b in readme.splitlines() if "| klasik |" in b]
    readme = readme.replace(baris_klasik[-1] + "\n", "", 1).replace("| modern |", "| lain |")
    (repo / "README.md").write_text(readme, encoding="utf-8")
    nb = repo / "notebooks" / "03_metode_modern.ipynb"
    isi = json.loads(nb.read_text(encoding="utf-8"))
    next(c for c in isi["cells"] if c["cell_type"] == "code")["outputs"] = [{"output_type": "error", "ename": "NotImplementedError", "evalue": "", "traceback": []}]
    nb.write_text(json.dumps(isi), encoding="utf-8")
    galat = " | ".join(_galat(repo, 2))
    assert "2 metode klasik; wajib 3" in galat
    assert "belum memuat metode modern" in galat
    assert "masih ada error NotImplementedError" in galat
    assert _galat(repo, 1) == []


def test_cek_anggota_dan_notebook_rusak(repo):
    (repo / "ANGGOTA.yml").write_text("anggota: [\n", encoding="utf-8")
    assert any("bukan YAML" in g for g in _galat(repo, 0))
    (repo / "ANGGOTA.yml").write_text("anggota:\n  - github: a\n", encoding="utf-8")
    assert any("jumlah anggota 1" in g for g in _galat(repo, 0))
    (repo / "notebooks" / "02_metode_klasik.ipynb").write_text("{rusak", encoding="utf-8")
    assert any("02_metode_klasik.ipynb rusak" in g for g in _galat(repo, 0))
    (repo / "app" / "app.py").unlink()
    assert any("berkas wajib tidak ada: app/app.py" in g for g in _galat(repo, 0))


# ---------------------------------------------------------------- GitHub (tiruan)


class GitHubTiruan(brp.GitHub):
    def __init__(self, repo_ada=(), ruleset_ada=(), repo_kosong=(), label_ada=()):
        super().__init__(dry_run=False, keluaran=lambda *a: None)
        self.repo_ada, self.ruleset_ada, self.masukan = set(repo_ada), list(ruleset_ada), []
        self.repo_kosong, self.label_ada = set(repo_kosong), set(label_ada)

    def jalankan(self, *perintah, masukan=None, ubah=True):
        perintah = [str(p) for p in perintah]
        self.log.append(perintah)
        if masukan:
            self.masukan.append(json.loads(masukan))
        if perintah[:2] == ["gh", "api"] and perintah[2].startswith("repos/") and perintah[3:] == ["--silent"]:
            nama = perintah[2][len("repos/"):]
            if nama.endswith("/commits?per_page=1"):
                if nama[: -len("/commits?per_page=1")] not in self.repo_ada:
                    raise RuntimeError("Git Repository is empty.")
                return ""
            if nama not in self.repo_ada | self.repo_kosong:
                raise RuntimeError("Not Found")
            return "{}"
        if perintah[:4] == ["gh", "api", "-X", "POST"] and perintah[4].endswith("/labels"):
            if perintah[6].split("=", 1)[1] in self.label_ada:
                raise RuntimeError("already_exists")
        if perintah[:2] == ["gh", "api"] and perintah[2].endswith("/rulesets") and len(perintah) == 3:
            return json.dumps([{"name": n} for n in self.ruleset_ada])
        if perintah[:3] == ["git", "-C", perintah[2]] and perintah[3:4] == ["status"]:
            return " M .github/scripts/cek_proyek.py\n"
        if perintah[:2] == ["git", "clone"]:
            import shutil
            shutil.copytree(self.sumber_klon, perintah[-1])
        return ""


def test_siapkan_repo_baru(kelompok):
    gh = GitHubTiruan()
    brp.siapkan(kelompok[:1], DATA, gh)
    perintah = [" ".join(p) for p in gh.log]
    buat = next(p for p in gh.log if p[:5] == ["gh", "api", "-X", "POST", "orgs/Prodi-TI-IBIKesatuan/repos"])
    assert "name=pcd2026-ka-t1" in buat and "private=false" in buat
    assert any("git -C" in p and "commit" in p for p in perintah)
    assert any(p.endswith("remote add origin https://github.com/Prodi-TI-IBIKesatuan/pcd2026-ka-t1.git") for p in perintah)
    assert any(p.endswith("push -q -u origin main") for p in perintah)
    assert any("PATCH repos/Prodi-TI-IBIKesatuan/pcd2026-ka-t1 " in p and "delete_branch_on_merge=true" in p for p in perintah)
    assert sum("collaborators/" in p and "permission=push" in p for p in perintah) == 3
    assert sum(p[:4] == ["gh", "api", "-X", "POST"] and p[4].endswith("/labels") for p in gh.log) == len(brp.LABEL)
    assert not any(p[:2] == ["gh", "repo"] or p[:2] == ["gh", "label"] for p in gh.log)  # REST saja
    main_rs, tag_rs = gh.masukan
    assert main_rs["name"] == "lindungi-main" and tag_rs["name"] == "kunci-tag-tahap"
    aturan_main = {r["type"]: r for r in main_rs["rules"]}
    assert aturan_main["pull_request"]["parameters"]["required_approving_review_count"] == 1
    assert aturan_main["required_status_checks"]["parameters"]["required_status_checks"] == [{"context": "cek"}]
    assert {r["type"] for r in tag_rs["rules"]} == {"deletion", "update", "non_fast_forward"}
    assert tag_rs["conditions"]["ref_name"]["include"] == ["refs/tags/tahap-*"]


def test_siapkan_repo_sudah_ada_tidak_dibuat_ulang(kelompok):
    gh = GitHubTiruan(repo_ada={"Prodi-TI-IBIKesatuan/pcd2026-ka-t1"}, ruleset_ada=["lindungi-main", "kunci-tag-tahap"])
    brp.siapkan(kelompok[:1], DATA, gh)
    assert not any("orgs/Prodi-TI-IBIKesatuan/repos" in p for p in gh.log)
    assert not any("push" in p for p in gh.log)  # isi kelompok tidak disentuh
    assert gh.masukan == []  # ruleset tidak dipasang ulang


def test_siapkan_repo_kosong_diisi_tanpa_undangan(kelompok):
    nama = "Prodi-TI-IBIKesatuan/pcd2026-ka-t1"
    gh = GitHubTiruan(repo_kosong={nama}, label_ada={"data", "tahap-1"})
    brp.siapkan(kelompok[:1], DATA, gh, undangan=False)
    perintah = [" ".join(p) for p in gh.log]
    assert not any("orgs/Prodi-TI-IBIKesatuan/repos" in p for p in perintah)  # tidak dibuat ulang
    assert any(p.endswith("push -q -u origin main") for p in perintah)
    assert not any("collaborators/" in p for p in perintah)
    assert sum(p.startswith(f"gh api -X PATCH repos/{nama}/labels/") for p in perintah) == 2
    assert brp.status_repo(gh, nama) == "kosong" and brp.status_repo(GitHubTiruan(repo_ada={nama}), nama) == "berisi"
    assert brp.status_repo(GitHubTiruan(), nama) == "tidak_ada"


def test_perbarui_hanya_berkas_dikelola(kelompok, tmp_path):
    lama = brp.rakit(kelompok[0], DATA, tmp_path / "lama")
    (lama / "README.md").write_text("README milik kelompok\n", encoding="utf-8")
    (lama / ".github" / "scripts" / "cek_proyek.py").write_text("# diubah kelompok\n", encoding="utf-8")
    gh = GitHubTiruan(repo_ada={"Prodi-TI-IBIKesatuan/pcd2026-ka-t1"}, ruleset_ada=["lindungi-main", "kunci-tag-tahap"])
    gh.sumber_klon = lama
    klon_terakhir = {}
    asli = gh.jalankan

    def catat(*p, **kw):
        if p[:2] == ("git", "clone"):
            klon_terakhir["path"] = pathlib.Path(str(p[-1]))
        hasil = asli(*p, **kw)
        if p[:2] == ("git", "-C") and "push" in p:
            klon = klon_terakhir["path"]
            klon_terakhir["readme"] = (klon / "README.md").read_text(encoding="utf-8")
            klon_terakhir["cek"] = (klon / ".github" / "scripts" / "cek_proyek.py").read_text(encoding="utf-8")
        return hasil

    gh.jalankan = catat
    brp.siapkan(kelompok[:1], DATA, gh, perbarui=True)
    assert klon_terakhir["readme"] == "README milik kelompok\n"
    assert klon_terakhir["cek"] == (brp.TEMPLATE / ".github" / "scripts" / "cek_proyek.py").read_text(encoding="utf-8")


def test_main_dry_run_dan_rakit(tmp_path, capsys):
    berkas = tmp_path / "kel.csv"
    berkas.write_text(CSV_CONTOH, encoding="utf-8")
    assert brp.main([str(berkas), "--dry-run"]) == 0
    keluaran = capsys.readouterr().out
    assert "[dry-run] gh api -X POST orgs/Prodi-TI-IBIKesatuan/repos -f name=pcd2026-kb-t5" in keluaran
    assert brp.main([str(berkas), "--rakit", str(tmp_path / "build")]) == 0
    assert len(list((tmp_path / "build").iterdir())) == 6


# ---------------------------------------------------------------- rekap pengumpulan


class GhTiruan(kp.Gh):
    def __init__(self, respons):
        self.respons = respons

    def api(self, path):
        return self.respons.get(path)

    def api_halaman(self, path, per_halaman=100):
        return self.respons.get(path, [])


def _respons_repo(repo, waktu_release, anotasi=True):
    anggota = "anggota:\n  - github: Andi\n  - github: budi\n  - github: cici\n"
    return {
        f"repos/{repo}/releases/tags/tahap-1": {"html_url": f"https://github.com/{repo}/releases/tag/tahap-1", "published_at": waktu_release},
        f"repos/{repo}/git/ref/tags/tahap-1": {"object": {"type": "tag", "sha": "t1"}} if anotasi else {"object": {"type": "commit", "sha": "c9"}},
        f"repos/{repo}/git/tags/t1": {"object": {"type": "commit", "sha": "c9"}},
        f"repos/{repo}/commits/c9/check-runs": {"check_runs": [{"name": "cek", "conclusion": "failure", "completed_at": "2026-11-08T10:00:00Z"},
                                                              {"name": "cek", "conclusion": "success", "completed_at": "2026-11-08T11:00:00Z"}]},
        f"repos/{repo}/contents/ANGGOTA.yml?ref=c9": {"content": base64.b64encode(anggota.encode()).decode()},
        f"repos/{repo}/commits?sha=c9": [{"author": {"login": "andi"}}, {"author": {"login": "andi"}}, {"author": {"login": "budi"}}, {"author": None}],
        f"repos/{repo}/pulls?state=closed": [{"merged_at": "2026-11-07T00:00:00Z", "user": {"login": "budi"}},
                                             {"merged_at": "2026-11-20T00:00:00Z", "user": {"login": "cici"}},
                                             {"merged_at": None, "user": {"login": "cici"}}],
    }


def test_denda_dan_waktu():
    tenggat = kp.baca_waktu("2026-11-08 23:59")
    assert tenggat.utcoffset() == dt.timedelta(hours=7)
    assert kp.denda(kp.baca_waktu("2026-11-08T16:00:00Z"), tenggat, 10, 3) == (0.0, 0)
    assert kp.denda(kp.baca_waktu("2026-11-09 05:59"), tenggat, 10, 3) == (6.0, 10)
    assert kp.denda(kp.baca_waktu("2026-11-10 06:00"), tenggat, 10, 3)[1] == 20
    assert kp.denda(kp.baca_waktu("2026-11-12 00:00"), tenggat, 10, 3)[1] is None


def test_rekap_repo_lengkap():
    repo = "Prodi-TI-IBIKesatuan/pcd2026-ka-t1"
    gh = GhTiruan(_respons_repo(repo, "2026-11-09T02:00:00Z"))
    baris = kp.rekap_repo(gh, repo, 1, kp.baca_waktu("2026-11-08 23:59"), DATA["umum"])
    assert baris["kelas"] == "ka" and baris["topik"] == "t1"
    assert baris["waktu_release_wib"] == "2026-11-09 09:00" and baris["denda"] == 10
    assert baris["cek_github"] == "success"
    assert baris["kontribusi"] == "Andi: 2 commit, 0 PR; budi: 1 commit, 1 PR; cici: 0 commit, 0 PR"
    assert baris["tanpa_kontribusi"] == "cici"


def test_rekap_tanpa_release_dan_main(tmp_path, capsys):
    repo_a, repo_b = "Prodi-TI-IBIKesatuan/pcd2026-ka-t1", "Prodi-TI-IBIKesatuan/pcd2026-ka-t2"
    respons = _respons_repo(repo_a, "2026-11-08T10:00:00Z", anotasi=False)
    respons["orgs/Prodi-TI-IBIKesatuan/repos?type=all"] = [
        {"name": "pcd2026-ka-t1", "full_name": repo_a}, {"name": "pcd2026-ka-t2", "full_name": repo_b},
        {"name": "pcd2026-kb-t1", "full_name": "x/pcd2026-kb-t1"}, {"name": "kelas-pcd-2026", "full_name": "x/y"},
        {"name": "pcd2026-ka-t3", "full_name": "x/arsip", "archived": True}]
    keluaran = tmp_path / "rekap.csv"
    assert kp.main(["--tahap", "1", "--kelas", "ka", "-o", str(keluaran)], gh=GhTiruan(respons)) == 0
    teks = keluaran.read_text(encoding="utf-8").splitlines()
    assert len(teks) == 3 and teks[0].startswith("repo,kelas,topik,release")
    assert "BELUM ADA" in teks[2] and ",0," in teks[1]
    assert "1 belum membuat Release" in capsys.readouterr().err


# ---------------------------------------------------------------- duplikat citra


def test_duplikat_antarkelompok(tmp_path):
    rng = np.random.default_rng(3)
    asli = cv2.GaussianBlur(rng.integers(0, 256, (120, 160, 3), dtype=np.uint8), (0, 0), 6)
    lain = cv2.GaussianBlur(rng.integers(0, 256, (120, 160, 3), dtype=np.uint8), (0, 0), 6)
    for kel in ("k1", "k2"):
        (tmp_path / kel / "sub").mkdir(parents=True)
    cv2.imwrite(str(tmp_path / "k1" / "asli.png"), asli)
    cv2.imwrite(str(tmp_path / "k1" / "salinan_sendiri.png"), asli)
    salinan = cv2.convertScaleAbs(cv2.resize(asli, (80, 60)), alpha=1.0, beta=15)
    cv2.imwrite(str(tmp_path / "k2" / "sub" / "salinan.jpg"), salinan, [cv2.IMWRITE_JPEG_QUALITY, 60])
    cv2.imwrite(str(tmp_path / "k2" / "lain.png"), lain)
    (tmp_path / "k2" / "rusak.jpg").write_bytes(b"x")
    data, gagal = cek_duplikat_citra.kumpulkan(tmp_path)
    assert len(data) == 4 and len(gagal) == 1
    pasangan = cek_duplikat_citra.pasangan_mirip(data, ambang=6)
    assert {(p[1], p[2], p[3], p[4]) for p in pasangan} == {("k1", "asli.png", "k2", "sub/salinan.jpg"),
                                                           ("k1", "salinan_sendiri.png", "k2", "sub/salinan.jpg")}
    dalam = cek_duplikat_citra.pasangan_mirip(data, ambang=6, dalam_kelompok=True)
    assert ("k1", "asli.png", "k1", "salinan_sendiri.png") in {(p[1], p[2], p[3], p[4]) for p in dalam}
    assert cek_duplikat_citra.pasangan_mirip(data[:1]) == []
    keluaran = tmp_path / "dup.csv"
    assert cek_duplikat_citra.main([str(tmp_path), "-o", str(keluaran)]) == 0
    assert len(keluaran.read_text(encoding="utf-8").splitlines()) == 3


# ---------------------------------------------------------------- menjalankan notebook (opsional)

JAWABAN_STUB = {
    "t1": 'return (0, 0, 10, 10), "F1234AB"',
    "t2": "return citra_bgr",
    "t3": "return cv2.GaussianBlur(citra_bgr, (3, 3), 0)",
    "t4": 'return "TOTAL 45.500", {"tanggal": "2026-10-21", "total": "45500"}',
    "t5": "return citra_bgr.reshape(-1, 3).mean(axis=0)",
}


def _anotasi(topik, berkas):
    baris = []
    for i, b in enumerate(berkas):
        nilai = {"berkas": b, "x": "2", "y": "2", "w": "10", "h": "10", "teks_pelat": "F1234AB", "berkas_gelap": b,
                 "berkas_referensi": berkas[(i + 1) % len(berkas)] if i % 2 == 0 else "", "sumber": "sendiri",
                 "berkas_bersih": b, "berkas_rusak": berkas[(i + 1) % len(berkas)], "jenis_degradasi": "gauss",
                 "parameter": "sigma=25", "teks_lengkap": "TOTAL 45.500", "tanggal": "2026-10-21", "total": "45500",
                 "kategori": "ab"[i % 2]}
        baris.append(",".join(nilai[k] for k in topik["kolom_anotasi"]))
    return ",".join(topik["kolom_anotasi"]) + "\n" + "\n".join(baris) + "\n"


@pytest.mark.parametrize("kode", KODE)
def test_notebook_berjalan_ujung_ke_ujung(tmp_path, kode):
    """Jalankan keempat notebook seperti di komputer sendiri (tanpa Colab) dengan stub yang sudah diisi."""
    nbclient = pytest.importorskip("nbclient")
    pytest.importorskip("ipykernel")
    pytest.importorskip("matplotlib")
    kel = brp.Kelompok("ka", kode, ("a1", "a2", "a3", "a4"))
    folder = brp.rakit(kel, DATA, tmp_path)
    topik = next(t for t in DATA["topik"] if t["kode"] == kode)
    rng = np.random.default_rng(0)
    berkas = []
    for i in range(6):
        citra = cv2.GaussianBlur(rng.integers(0, 256, (48, 64, 3), dtype=np.uint8), (0, 0), 2)
        cv2.imwrite(str(folder / "data" / "sample" / f"c{i}.png"), citra)
        berkas.append(f"c{i}.png")
    (folder / "data" / "anotasi.csv").write_text(_anotasi(topik, berkas), encoding="utf-8")
    os.environ.setdefault("MPLBACKEND", "Agg")
    for nama in notebook_proyek.NAMA:
        path = folder / "notebooks" / nama
        nb = nbformat.read(path, as_version=4)
        for sel in nb.cells:
            if sel.cell_type == "code" and "raise NotImplementedError" in sel.source:
                sel.source = re.sub(r"raise NotImplementedError\([^)]*\)", JAWABAN_STUB[kode], sel.source)
        nbclient.NotebookClient(nb, timeout=120, kernel_name="python3",
                                resources={"metadata": {"path": str(folder / "notebooks")}}).execute()
        nbformat.write(nb, path)
    figur = list((folder / "data" / "figures").glob("pra_*.png"))
    assert len(figur) == 6
    hasil = json.loads((folder / "data" / "hasil_metode.json").read_text(encoding="utf-8"))
    assert [v["jenis"] for v in hasil.values()].count("klasik") == 2 and "Metode modern" in hasil
    keluaran_04 = json.dumps(nbformat.read(folder / "notebooks" / "04_evaluasi.ipynb", as_version=4).cells, ensure_ascii=False)
    for m in topik["metrik"]:
        assert f"| {m['nama']}" in keluaran_04 or f"{m['nama']} |" in keluaran_04
    for nama in notebook_proyek.NAMA:
        ok, alasan = CEK.notebook_dijalankan(folder / "notebooks" / nama)
        assert ok, (nama, alasan)


def test_cek_izin_gh(monkeypatch):
    from types import SimpleNamespace as NS
    monkeypatch.setattr(brp.shutil, "which", lambda _: "/usr/bin/gh")
    classic = "HTTP/2.0 200 OK\nX-Oauth-Scopes: repo, workflow\n\n{\"login\":\"dosen\"}"
    brp.cek_izin_gh(lambda *a, **k: NS(returncode=0, stdout=classic, stderr=""))
    halus = "HTTP/2.0 200 OK\nX-Github-Request-Id: 1\n\n{}"  # token fine-grained: tanpa header scope
    brp.cek_izin_gh(lambda *a, **k: NS(returncode=0, stdout=halus, stderr=""))
    with pytest.raises(SystemExit, match="workflow"):
        brp.cek_izin_gh(lambda *a, **k: NS(returncode=0, stdout=classic.replace(", workflow", ""), stderr=""))
    with pytest.raises(SystemExit, match="tidak sah"):
        brp.cek_izin_gh(lambda *a, **k: NS(returncode=1, stdout="", stderr="Bad credentials (HTTP 401)"))
    monkeypatch.setattr(brp.shutil, "which", lambda _: None)
    with pytest.raises(SystemExit, match="belum terpasang"):
        brp.cek_izin_gh()



def test_baris_tanpa_berkas(tmp_path, capsys):
    teks = brp.teks_dari_baris(" uji,t1,a1;a2;a3 | kb,t5,b1 b2 b3\nkb,t2,c1;c2;c3 ")
    assert [k.nama_repo("x") for k in brp.baca_kelompok(teks, DATA)] == ["x-uji-t1", "x-kb-t5", "x-kb-t2"]
    assert brp.main(["--baris", "uji,t1,a1;a2;a3", "--dry-run"]) == 0
    assert "repos -f name=pcd2026-uji-t1" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        brp.main(["--dry-run"])
