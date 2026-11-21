import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_bukti_kebutuhan.py"


def test_bukti_kebutuhan_reproducible(tmp_path):
    out = tmp_path / "bukti"
    subprocess.run([sys.executable, str(SCRIPT), "--output", str(out)], check=True, cwd=ROOT,
                   capture_output=True)
    manifest = json.loads((out / "manifest_bukti_sha256.json").read_text(encoding="utf-8"))
    assert manifest["status"]["KF-01"] == "Lulus"
    assert manifest["status"]["KNF-01"] == "Lulus"
    committed = json.loads((ROOT / "bukti_kebutuhan/manifest_bukti_sha256.json").read_text(encoding="utf-8"))
    for name, info in manifest["keluaran"].items():
        if name == "README.md":
            continue  # memuat hash commit saat dibangkitkan
        assert committed["keluaran"][name]["sha256"] == info["sha256"], name


def test_refuses_existing_folder_without_manifest(tmp_path):
    out = tmp_path / "lain"
    out.mkdir()
    result = subprocess.run([sys.executable, str(SCRIPT), "--output", str(out), "--replace"], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode != 0
