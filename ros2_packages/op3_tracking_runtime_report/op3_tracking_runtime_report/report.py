"""Calculate runtime and observed track continuity from a completed OP3 run."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

CLASSES = ("ball", "gawang", "robot")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def percentiles(values: list[float]) -> dict:
    if not values:
        return {"median": None, "p95": None, "min": None, "max": None}
    data = np.asarray(values, dtype=float)
    return {"median": float(np.median(data)), "p95": float(np.percentile(data, 95)),
            "min": float(np.min(data)), "max": float(np.max(data))}


def iso_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def summarize_tracks(records: list[dict], frame_count: int) -> dict:
    result = {}
    for name in CLASSES:
        rows = [row for row in records if row["class_name"] == name]
        rows.sort(key=lambda row: (int(row["frame_index"]), -float(row["confidence"])))
        frames = defaultdict(list)
        for row in rows:
            frames[int(row["frame_index"])].append(row)
        # A single trajectory can be assessed only when at most one detection of this class appears per frame.
        single = all(len(items) <= 1 for items in frames.values())
        representative = [items[0] for _, items in sorted(frames.items())]
        ids = [row["track_id"] for row in rows if row["track_id"]]
        transitions = []
        gaps = []
        longest_contiguous = 0
        current_contiguous = 0
        previous = None
        for row in representative:
            frame = int(row["frame_index"])
            track_id = row["track_id"]
            if previous is None:
                current_contiguous = 1
            else:
                prior_frame = int(previous["frame_index"])
                gap = frame - prior_frame - 1
                if gap:
                    gaps.append({"after_frame": prior_frame, "before_frame": frame,
                                 "missing_frames": gap, "previous_id": previous["track_id"],
                                 "next_id": track_id})
                if track_id and previous["track_id"] and track_id != previous["track_id"]:
                    transitions.append({"after_frame": prior_frame, "before_frame": frame,
                                        "missing_frames": gap, "from_id": previous["track_id"],
                                        "to_id": track_id})
                current_contiguous = current_contiguous + 1 if gap == 0 and track_id == previous["track_id"] else 1
            longest_contiguous = max(longest_contiguous, current_contiguous)
            previous = row
        centers_x = [(float(row["x1_px"]) + float(row["x2_px"])) / 2 for row in rows]
        centers_y = [(float(row["y1_px"]) + float(row["y2_px"])) / 2 for row in rows]
        result[name] = {
            "detections": len(rows), "frames_with_detection": len(frames),
            "frame_coverage": len(frames) / frame_count if frame_count else None,
            "max_detections_in_one_frame": max((len(x) for x in frames.values()), default=0),
            "single_target_assumption": single,
            "detections_with_track_id": len(ids),
            "id_coverage": len(ids) / len(rows) if rows else None,
            "id_counts": dict(Counter(ids)),
            "id_transitions": transitions,
            "immediate_id_changes": sum(x["missing_frames"] == 0 for x in transitions),
            "reidentifications_after_gap": sum(x["missing_frames"] > 0 for x in transitions),
            "detection_gaps": gaps,
            "longest_contiguous_frames_same_id": longest_contiguous,
            "center_x_span_px": max(centers_x) - min(centers_x) if centers_x else None,
            "center_y_span_px": max(centers_y) - min(centers_y) if centers_y else None,
            "confidence": percentiles([float(row["confidence"]) for row in rows]),
        }
    return result


def plot_runtime(frames: list[dict], times: list[float], summary: dict, output: Path) -> None:
    end_to_end = [float(row["end_to_end_ms"]) for row in frames]
    cpu = [float(row["process_cpu_percent"]) for row in frames]
    rss = [float(row["process_rss_bytes"]) / 1048576 for row in frames]
    bins = np.arange(0, max(times) + 2, 1)
    counts, _ = np.histogram(times, bins=bins)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    axes[0, 0].plot(times, end_to_end, linewidth=.6)
    axes[0, 0].axhline(summary["runtime"]["callback_ms"]["p95"], color="red", linestyle="--", label="p95")
    axes[0, 0].set_ylabel("Callback (ms)")
    axes[0, 0].legend()
    axes[0, 1].plot(bins[:-1], counts, linewidth=1)
    axes[0, 1].set_ylabel("Frame diproses per detik")
    axes[1, 0].plot(times, cpu, linewidth=.6)
    axes[1, 0].set_ylabel("CPU proses (%)")
    axes[1, 1].plot(times, rss, linewidth=.8)
    axes[1, 1].set_ylabel("RSS proses (MiB)")
    for ax in axes.flat:
        ax.set_xlabel("Detik sejak frame pertama")
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Runtime detektor OP3: satu sesi live dengan viewer SSH-X")
    fig.tight_layout()
    fig.savefig(output, dpi=170)
    plt.close(fig)


def plot_tracking(records: list[dict], frame_count: int, output: Path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(11, 7), sharex=True)
    colors = {"ball": "#d98119", "gawang": "#2786a5", "robot": "#8350a8"}
    for name, ax in zip(CLASSES, axes):
        rows = [row for row in records if row["class_name"] == name]
        ids = sorted({row["track_id"] for row in rows if row["track_id"]}, key=lambda x: int(x) if x.isdigit() else x)
        for track_id in ids:
            part = [row for row in rows if row["track_id"] == track_id]
            frame = [int(row["frame_index"]) for row in part]
            x = [(float(row["x1_px"]) + float(row["x2_px"])) / 2 for row in part]
            ax.scatter(frame, x, s=2, label=f"ID {track_id}")
        ax.set_ylabel(f"{name}: x (px)")
        ax.set_xlim(1, frame_count)
        ax.set_ylim(0, 640)
        ax.legend(loc="upper right", markerscale=3)
        ax.spines[["top", "right"]].set_visible(False)
    axes[-1].set_xlabel("Nomor frame diproses")
    fig.suptitle("Posisi horizontal pusat kotak menurut ID tracker")
    fig.tight_layout()
    fig.savefig(output, dpi=170)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir
    if output.exists():
        parser.error(f"Output exists: {output}")
    files = {"metadata": args.run_dir / f"{args.run_id}.json",
             "frames": args.run_dir / f"{args.run_id}.csv",
             "detections": args.run_dir / f"{args.run_id}_detections.csv"}
    metadata = json.loads(files["metadata"].read_text())
    if metadata.get("run_id") != args.run_id or metadata.get("status") != "stopped":
        raise ValueError("Run metadata must be stopped and match run ID")
    frames = list(csv.DictReader(files["frames"].open()))
    detections = list(csv.DictReader(files["detections"].open()))
    if not frames or len(frames) != metadata["processed_frames"] + metadata["frame_errors"]:
        raise ValueError("Frame CSV count differs from finalized metadata")
    valid = [row for row in frames if not row["error"]]
    if len(valid) != metadata["processed_frames"]:
        raise ValueError("Successful frame count differs from metadata")
    indices = {int(row["frame_index"]) for row in valid}
    if len(indices) != len(valid) or indices != set(range(1, len(valid) + 1)):
        raise ValueError("Successful frame index is not contiguous")
    by_frame = Counter(int(row["frame_index"]) for row in detections)
    if any(int(row["detection_count"]) != by_frame.get(int(row["frame_index"]), 0) for row in valid):
        raise ValueError("Per-frame detection counts differ from detection CSV")
    if any(row["class_name"] not in CLASSES for row in detections):
        raise ValueError("Unknown class in detection log")
    first = iso_time(valid[0]["receive_time_utc"])
    last = iso_time(valid[-1]["receive_time_utc"])
    times = [(iso_time(row["receive_time_utc"]) - first).total_seconds() for row in valid]
    interval_ms = [(b - a) * 1000 for a, b in zip(times, times[1:])]
    camera_age_ms = [(iso_time(row["receive_time_utc"]).timestamp() - int(row["capture_stamp_ns"]) / 1e9) * 1000
                     for row in valid if int(row["capture_stamp_ns"]) > 0]
    wall_duration = (iso_time(metadata["stopped_at_utc"]) - iso_time(metadata["started_at_utc"])).total_seconds()
    runtime = {
        "wall_duration_s": wall_duration,
        "processed_fps": len(valid) / wall_duration,
        "frame_receive_span_s": times[-1],
        "inter_processed_frame_interval_ms": percentiles(interval_ms),
        "camera_stamp_to_callback_start_ms": percentiles(camera_age_ms),
        "preprocess_ms": percentiles([float(row["preprocess_ms"]) for row in valid]),
        "inference_ms": percentiles([float(row["inference_ms"]) for row in valid]),
        "postprocess_ms": percentiles([float(row["postprocess_ms"]) for row in valid]),
        "callback_ms": percentiles([float(row["end_to_end_ms"]) for row in valid]),
        "process_cpu_percent": percentiles([float(row["process_cpu_percent"]) for row in valid]),
        "process_rss_mib": percentiles([float(row["process_rss_bytes"]) / 1048576 for row in valid]),
    }
    summary = {"status": "completed_runtime_log_analysis",
               "created_at_utc": datetime.now(timezone.utc).isoformat(),
               "run_id": args.run_id, "condition": metadata["condition"],
               "checkpoint_sha256": metadata["checkpoint_sha256"],
               "settings": {key: metadata[key] for key in ("input_topic", "output_topic", "device", "precision", "imgsz", "confidence_threshold", "iou_threshold", "tracking_enabled", "tracker_config", "preview_enabled")},
               "input_files": {name: {"path": str(path.resolve()), "sha256": sha256(path)}
                               for name, path in files.items()},
               "processed_frames": len(valid), "frame_errors": metadata["frame_errors"],
               "detection_rows": len(detections), "runtime": runtime,
               "tracking": summarize_tracks(detections, len(valid)),
               "interpretation_limit": "Track ID continuity is observed from detections only; no frame-by-frame human identity ground truth or MOTA/IDF1."}
    output.mkdir(parents=True)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    plot_runtime(valid, times, summary, output / "grafik_runtime.png")
    plot_tracking(detections, len(valid), output / "grafik_tracking.png")
    print(json.dumps({"frames": summary["processed_frames"], "runtime": runtime,
                      "tracking": summary["tracking"]}, indent=2))
    return 0
