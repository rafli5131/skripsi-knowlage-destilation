#!/usr/bin/env python3
"""Ekstrak log jendela ukur run live OP3 dari log mentah, hanya dengan pustaka standar.

Skrip ini dijalankan di komputer OP3 dari root repositori robot. Skrip hanya
membaca log mentah di ``runs/op3_pytorch/`` dan menulis ke direktori keluaran
baru yang harus belum ada (direktori kerja sementara). Tidak ada berkas di
repositori robot yang ditulis, dipindahkan, atau dihapus.

Untuk setiap run:

* SHA-256 log mentah (``<run_id>.csv``) dan metadata (``<run_id>.json``) wajib
  sama dengan T36; bila tidak, run dilewati.
* Baris dengan ``receive_time_utc`` di antara ``window_start_utc`` dan
  ``window_end_utc`` T36 (inklusif) ditulis ke ``<run_id>/jendela_runtime.csv``
  dengan kolom dan urutan kolom log mentah, akhir baris LF.
* Baris log deteksi yang ``frame_index``-nya ada di jendela ditulis ke
  ``<run_id>/jendela_deteksi.csv``, sama dengan ``write_run_details`` di
  ``op3_equal_live_report``.
* Jumlah baris, jumlah error, rerata ``end_to_end_ms``, dan FPS dicocokkan dengan
  T36 (toleransi 1e-6). Bila ada yang gagal, berkas jendela run itu dihapus dari
  direktori keluaran dan selisihnya dicatat.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import platform
import socket
import subprocess
import sys
from pathlib import Path

TOLERANSI = 1e-6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def info_berkas(path: Path) -> dict:
    return {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}


def waktu(text: str) -> dt.datetime:
    value = dt.datetime.fromisoformat(text)
    if value.tzinfo is None:
        raise ValueError(f"Timestamp tanpa zona waktu: {text}")
    return value


def cari_lokasi_lain(search_root: Path, run_id: str) -> list[str]:
    try:
        result = subprocess.run(["find", str(search_root), "-name", f"{run_id}*"],
                                capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [f"find gagal: {type(exc).__name__}: {exc}"]
    return sorted(line for line in result.stdout.splitlines() if line)


def tulis_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def ekstrak(run: dict, repo: Path, out: Path, search_root: Path) -> dict:
    run_id = run["run_id"]
    base = repo / "runs/op3_pytorch"
    raw, meta, det = base / f"{run_id}.csv", base / f"{run_id}.json", base / f"{run_id}_detections.csv"
    record: dict = {"run_id": run_id, "t36": {k: run[k] for k in (
        "window_start_utc", "window_end_utc", "frames", "error_frames", "latency_mean_ms", "fps",
        "raw_csv_sha256", "metadata_sha256")}, "sumber": {}, "keluaran": {}, "pemeriksaan": {}}

    missing = [p.name for p in (raw, meta) if not p.is_file()]
    if missing:
        record["status"] = "tidak_ditemukan"
        record["berkas_hilang"] = missing
        # Lokasi lain hanya dicatat; tidak dipakai tanpa pencocokan hash.
        record["hasil_find"] = cari_lokasi_lain(search_root, run_id)
        return record

    record["sumber"]["log_mentah"] = info_berkas(raw)
    record["sumber"]["metadata"] = info_berkas(meta)
    if det.is_file():
        record["sumber"]["log_deteksi"] = info_berkas(det)
    hash_raw_ok = record["sumber"]["log_mentah"]["sha256"] == run["raw_csv_sha256"]
    hash_meta_ok = record["sumber"]["metadata"]["sha256"] == run["metadata_sha256"]
    record["pemeriksaan"]["hash_log_mentah_cocok"] = hash_raw_ok
    record["pemeriksaan"]["hash_metadata_cocok"] = hash_meta_ok
    if not (hash_raw_ok and hash_meta_ok):
        record["status"] = "hash_tidak_cocok"
        return record

    start, stop = waktu(run["window_start_utc"]), waktu(run["window_end_utc"])
    with raw.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    selected = [r for r in rows if start <= waktu(r["receive_time_utc"]) <= stop]
    clean = [r for r in selected if not r["error"]]

    checks = record["pemeriksaan"]
    checks["jumlah_baris"] = {"t36": int(run["frames"]), "jendela": len(selected),
                              "lulus": len(selected) == int(run["frames"])}
    n_error = len(selected) - len(clean)
    checks["jumlah_error"] = {"t36": int(run["error_frames"]), "jendela": n_error,
                              "lulus": n_error == int(run["error_frames"])}
    if clean:
        mean = sum(float(r["end_to_end_ms"]) for r in clean) / len(clean)
        diff = mean - float(run["latency_mean_ms"])
        checks["rerata_end_to_end_ms"] = {"t36": float(run["latency_mean_ms"]), "jendela": mean,
                                          "selisih": diff, "lulus": abs(diff) <= TOLERANSI}
    else:
        checks["rerata_end_to_end_ms"] = {"lulus": False, "alasan": "tidak ada baris tanpa error"}
    stamps = [int(r["capture_stamp_ns"]) for r in clean]
    if len(stamps) >= 2 and stamps[-1] > stamps[0]:
        fps = (len(stamps) - 1) * 1e9 / (stamps[-1] - stamps[0])
        diff = fps - float(run["fps"])
        checks["fps"] = {"t36": float(run["fps"]), "jendela": fps, "selisih": diff,
                         "lulus": abs(diff) <= TOLERANSI}
    else:
        checks["fps"] = {"lulus": False, "alasan": "timestamp kamera kurang atau tidak naik"}

    run_out = out / run_id
    run_out.mkdir()
    window_path = run_out / "jendela_runtime.csv"
    tulis_csv(window_path, fieldnames, selected)
    record["keluaran"]["jendela_runtime"] = {"path": f"{run_id}/jendela_runtime.csv",
                                             "sha256": sha256(window_path), "baris": len(selected)}
    if det.is_file():
        indices = {int(r["frame_index"]) for r in selected}
        with det.open(newline="", encoding="utf-8") as stream:
            det_reader = csv.DictReader(stream)
            det_fields = list(det_reader.fieldnames or [])
            det_rows = [r for r in det_reader if int(r["frame_index"]) in indices]
        if det_rows:
            det_path = run_out / "jendela_deteksi.csv"
            tulis_csv(det_path, det_fields, det_rows)
            record["keluaran"]["jendela_deteksi"] = {"path": f"{run_id}/jendela_deteksi.csv",
                                                     "sha256": sha256(det_path), "baris": len(det_rows)}

    names = ("jumlah_baris", "jumlah_error", "rerata_end_to_end_ms", "fps")
    if all(checks[name]["lulus"] for name in names):
        record["status"] = "diekstrak"
    else:
        record["status"] = "pemeriksaan_gagal"
        # Berkas jendela run yang gagal tidak dipakai.
        for item in record["keluaran"].values():
            (out / item["path"]).unlink()
        run_out.rmdir()
        record["keluaran_dibuang"] = record.pop("keluaran")
        record["keluaran"] = {}
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=Path, required=True, help="JSON daftar run beserta nilai T36")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Root repositori robot (baca saja)")
    parser.add_argument("--out", type=Path, required=True, help="Direktori keluaran baru di luar repositori")
    parser.add_argument("--search-root", type=Path, default=Path("/home/humanoid"))
    args = parser.parse_args()

    repo, out = args.repo.resolve(), args.out.resolve()
    if out.exists():
        raise SystemExit(f"Direktori keluaran sudah ada dan tidak akan ditimpa: {out}")
    if out == repo or repo in out.parents:
        raise SystemExit("Direktori keluaran tidak boleh berada di dalam repositori robot")
    runs = json.loads(args.runs.read_text(encoding="utf-8"))
    out.mkdir(parents=True)

    started = dt.datetime.now(dt.timezone.utc)
    records = [ekstrak(run, repo, out, args.search_root) for run in runs]
    status = {
        "dibuat_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "mulai_utc": started.isoformat(timespec="seconds"),
        "hostname": socket.gethostname(),
        "python": platform.python_version(),
        "repo": str(repo),
        "skrip": str(Path(__file__).resolve()),
        "skrip_sha256": sha256(Path(__file__).resolve()),
        "masukan_runs_sha256": sha256(args.runs),
        "toleransi": TOLERANSI,
        "ringkasan": {s: sum(r["status"] == s for r in records)
                      for s in sorted({r["status"] for r in records})},
        "runs": records,
    }
    (out / "status_ekstraksi.json").write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n",
                                               encoding="utf-8")
    print(json.dumps(status["ringkasan"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
