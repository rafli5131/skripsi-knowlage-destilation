"""Summarize metadata-only OP3 trial logs and draw performance plots."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def describe(values: list[float]) -> dict[str, float]:
    return {"mean": round(statistics.mean(values), 2),
            "median": round(statistics.median(values), 2),
            "p95": round(percentile(values, 0.95), 2),
            "max": round(max(values), 2)}


def longest_consecutive(values: list[int]) -> int:
    best = current = 0
    previous = None
    for value in values:
        current = current + 1 if previous is not None and value == previous + 1 else 1
        best = max(best, current)
        previous = value
    return best


def analyze(run_dir: Path, output_dir: Path) -> dict:
    meta = json.loads((run_dir / "summary.json").read_text())
    with (run_dir / "frames.csv").open(newline="") as stream:
        frames = list(csv.DictReader(stream))
    with (run_dir / "detections.csv").open(newline="") as stream:
        detections = list(csv.DictReader(stream))
    if not frames or [int(r["frame_index"]) for r in frames] != list(range(1, len(frames) + 1)):
        raise ValueError("Indeks frame tidak lengkap/berurutan")
    if len(frames) != meta["processed_frames"]:
        raise ValueError("Jumlah frame tidak cocok dengan summary.json")
    if len(detections) != sum(int(r["detection_count"]) for r in frames):
        raise ValueError("Jumlah baris deteksi tidak cocok dengan frame")
    t0 = datetime.fromisoformat(frames[0]["processed_at_utc"])
    time_s = [(datetime.fromisoformat(r["processed_at_utc"]) - t0).total_seconds() for r in frames]
    duration = time_s[-1]
    data = {
        "run_id": meta["run_id"], "status": meta["status"],
        "condition": meta["condition"], "checkpoint_sha256": meta["checkpoint_sha256"],
        "processed_frames": len(frames), "received_frames": meta["received_frames"],
        "overwritten_frames": meta["overwritten_frames"], "errors": meta["errors"],
        "total_detections": len(detections),
        "observed_window_s": round(duration, 2),
        "processed_fps": round((len(frames) - 1) / duration, 2),
        "measurements": {}, "classes": {},
    }
    keys = ("preprocess_ms", "inference_ms", "postprocess_ms", "processing_ms",
            "camera_age_ms", "process_cpu_percent", "system_cpu_percent",
            "process_ram_mib", "system_ram_percent")
    for key in keys:
        values = [float(r[key]) for r in frames if r[key]]
        data["measurements"][key] = describe(values)
    for class_name in ("ball", "gawang", "robot"):
        rows = [r for r in detections if r["class_name"] == class_name]
        by_id = Counter(r["track_id"] for r in rows if r["track_id"])
        frame_indices = sorted({int(r["frame_index"]) for r in rows})
        frame_index_set = set(frame_indices)
        missing = [i for i in range(1, len(frames) + 1) if i not in frame_index_set]
        confidence = [float(r["confidence"]) for r in rows]
        data["classes"][class_name] = {
            "detections": len(rows), "frames_with_detection": len(frame_indices),
            "frames_without_detection": len(frames) - len(frame_indices),
            "track_ids": dict(by_id),
            "blank_track_ids": sum(not r["track_id"] for r in rows),
            "longest_consecutive_detection_frames": longest_consecutive(frame_indices),
            "longest_consecutive_missing_frames": longest_consecutive(missing),
            "confidence_mean": round(statistics.mean(confidence), 3) if confidence else None,
            "confidence_median": round(statistics.median(confidence), 3) if confidence else None,
        }
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "summary_metrics.json").write_text(json.dumps(data, indent=2) + "\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
    plots = (
        ("fps_window", "FPS (jendela 3 detik)", "FPS", "#42a66c"),
        ("processing_ms", "Waktu pemrosesan per frame", "ms", "#de8d32"),
        ("camera_age_ms", "Umur frame pada akhir inferensi", "ms", "#337dcc"),
        ("process_cpu_percent", "CPU proses (% per inti logis)", "%", "#9c65ba"),
    )
    for ax, (key, title, unit, color) in zip(axes.flat, plots):
        ax.plot(time_s, [float(r[key]) if r[key] else float("nan") for r in frames],
                lw=0.8, color=color)
        ax.set(title=title, ylabel=unit)
        ax.grid(alpha=0.2)
    for ax in axes[1]:
        ax.set_xlabel("Detik sejak frame pertama")
    fig.suptitle(f"OP3 servo idle — {meta['run_id']} (metadata kamera)")
    fig.tight_layout()
    fig.savefig(output_dir / "grafik_performa.png", dpi=150)
    plt.close(fig)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    result = analyze(args.run_dir, args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
