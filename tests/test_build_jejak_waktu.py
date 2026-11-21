import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_jejak_waktu.py"


def test_jejak_waktu_matches_committed(tmp_path):
    out = tmp_path / "jejak"
    subprocess.run([sys.executable, str(SCRIPT), "--output", str(out)], check=True, cwd=ROOT, capture_output=True)
    fresh = json.loads((out / "manifest_jejak_waktu_sha256.json").read_text(encoding="utf-8"))["keluaran"]
    committed = json.loads((ROOT / "jejak_waktu/manifest_jejak_waktu_sha256.json").read_text(encoding="utf-8"))["keluaran"]
    for name in ("kronologi_kegiatan.csv", "training_per_epoch.csv", "timestamp_frame_live_24_run.csv"):
        assert fresh[name] == committed[name], name
