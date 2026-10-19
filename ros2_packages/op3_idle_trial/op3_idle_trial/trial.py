"""Record metadata for a read-only OP3 live tracking trial."""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import cv2
import psutil
import rclpy
import torch
import ultralytics
from ultralytics import YOLO

from op3_live_monitor.monitor import (
    CameraNode, COLORS, NAMES, REPO_ROOT, SharedState, render, validate_model, WINDOW,
)

FRAME_COLUMNS = [
    "frame_index", "capture_stamp_ns", "processed_at_utc", "camera_age_ms",
    "preprocess_ms", "inference_ms", "postprocess_ms", "processing_ms",
    "fps_window", "process_cpu_percent", "system_cpu_percent",
    "process_ram_mib", "system_ram_percent", "received_frames",
    "overwritten_frames", "detection_count", "tracked_count",
    "ball_count", "gawang_count", "robot_count",
]
DETECTION_COLUMNS = [
    "frame_index", "class_id", "class_name", "confidence", "track_id",
    "x1", "y1", "x2", "y2",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TrialWorker(threading.Thread):
    def __init__(self, state: SharedState, checkpoint: Path, args: argparse.Namespace,
                 frame_writer: csv.DictWriter, detection_writer: csv.DictWriter,
                 frame_file, detection_file) -> None:
        super().__init__(name="op3-trial-inference", daemon=True)
        self.state = state
        self.args = args
        self.frame_writer = frame_writer
        self.detection_writer = detection_writer
        self.frame_file = frame_file
        self.detection_file = detection_file
        self.model = YOLO(str(checkpoint), task="detect")
        if {int(key): str(value) for key, value in self.model.names.items()} != NAMES:
            raise ValueError("Mapping kelas checkpoint tidak cocok")
        self.model.to("cpu")
        self.model.model.float()
        self.model.model.eval()
        self.process = psutil.Process()
        self.process.cpu_percent(interval=None)
        psutil.cpu_percent(interval=None)
        self.resources = {}
        self.last_resource_update = 0.0
        self.frame_index = 0

    def run(self) -> None:
        while self.state.running.is_set():
            if not self.state.new_frame.wait(0.5):
                continue
            item = self.state.take_latest()
            if item is None:
                continue
            frame, stamp_ns = item
            started = time.perf_counter()
            try:
                result = self.model.track(
                    source=frame, imgsz=self.args.imgsz, batch=1, device="cpu",
                    conf=self.args.conf, iou=self.args.iou, tracker="botsort.yaml",
                    persist=True, verbose=False, save=False, plots=False,
                    stream=False, max_det=300,
                )[0]
                annotated = frame.copy()
                counts = {name: 0 for name in NAMES.values()}
                detections = []
                detection_rows = []
                next_index = self.frame_index + 1
                if result.boxes is not None:
                    for box in result.boxes:
                        class_id = int(box.cls.item())
                        name = NAMES[class_id]
                        score = float(box.conf.item())
                        track_id = int(box.id.item()) if box.id is not None else None
                        x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
                        counts[name] += 1
                        detections.append({"class": name, "confidence": round(score, 4),
                                           "track_id": track_id})
                        detection_rows.append({
                            "frame_index": next_index, "class_id": class_id,
                            "class_name": name, "confidence": round(score, 6),
                            "track_id": track_id if track_id is not None else "",
                            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                        })
                        color = COLORS[name]
                        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                        label = f"{name} #{track_id}" if track_id is not None else name
                        label += f"  {score:.2f}"
                        top = max(0, y1 - 25)
                        cv2.rectangle(annotated, (x1, top),
                                      (min(x2 + 45, annotated.shape[1] - 1), y1), color, -1)
                        cv2.putText(annotated, label, (x1 + 3, max(y1 - 7, 16)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (15, 21, 29), 1, cv2.LINE_AA)
                now = time.monotonic()
                if now - self.last_resource_update >= 1:
                    self.resources = {
                        "process_cpu_percent": round(self.process.cpu_percent(interval=None), 1),
                        "system_cpu_percent": round(psutil.cpu_percent(interval=None), 1),
                        "process_ram_mib": round(self.process.memory_info().rss / (1024 * 1024), 1),
                        "system_ram_percent": round(psutil.virtual_memory().percent, 1),
                    }
                    self.last_resource_update = now
                camera_age = (time.time_ns() - stamp_ns) / 1_000_000 if stamp_ns > 0 else None
                if camera_age is not None and not 0 <= camera_age < 3_600_000:
                    camera_age = None
                processing_ms = (time.perf_counter() - started) * 1000
                values = {
                    "counts": counts, "detections": detections,
                    "inference_ms": round(float(result.speed.get("inference", 0)), 2),
                    "preprocess_ms": round(float(result.speed.get("preprocess", 0)), 2),
                    "postprocess_ms": round(float(result.speed.get("postprocess", 0)), 2),
                    "end_to_end_ms": round(processing_ms, 2),
                    "camera_age_ms": round(camera_age, 1) if camera_age is not None else None,
                    **self.resources,
                }
                self.state.record(annotated, values)
                _, metrics = self.state.snapshot()
                self.frame_index = next_index
                self.frame_writer.writerow({
                    "frame_index": next_index, "capture_stamp_ns": stamp_ns,
                    "processed_at_utc": utc_now(), "camera_age_ms": values["camera_age_ms"],
                    "preprocess_ms": values["preprocess_ms"],
                    "inference_ms": values["inference_ms"],
                    "postprocess_ms": values["postprocess_ms"],
                    "processing_ms": values["end_to_end_ms"],
                    "fps_window": round(metrics["fps"], 2),
                    "process_cpu_percent": metrics["process_cpu_percent"],
                    "system_cpu_percent": metrics["system_cpu_percent"],
                    "process_ram_mib": metrics["process_ram_mib"],
                    "system_ram_percent": metrics["system_ram_percent"],
                    "received_frames": metrics["received_frames"],
                    "overwritten_frames": metrics["overwritten_frames"],
                    "detection_count": len(detection_rows),
                    "tracked_count": sum(row["track_id"] != "" for row in detection_rows),
                    "ball_count": counts["ball"], "gawang_count": counts["gawang"],
                    "robot_count": counts["robot"],
                })
                self.detection_writer.writerows(detection_rows)
                self.frame_file.flush()
                self.detection_file.flush()
            except Exception as error:
                self.state.record_error(error)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--topic", default="/thesis/image_raw")
    parser.add_argument("--run-root", type=Path, default=REPO_ROOT / "runs/op3_idle_trial")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--condition", choices=("servo_idle", "unknown"), default="unknown")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--no-preview", action="store_true")
    args = parser.parse_args()
    if args.duration <= 0 or args.imgsz <= 0 or not 0 <= args.conf <= 1 or not 0 <= args.iou <= 1:
        parser.error("duration/imgsz harus positif; conf/iou harus antara 0 dan 1")
    if not args.no_preview and not os.environ.get("DISPLAY"):
        parser.error("DISPLAY kosong; jalankan dari SSH -X atau gunakan --no-preview")
    checkpoint, digest, offline = validate_model(args.repo_root.resolve())
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:6]
    run_dir = args.run_root.resolve() / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    meta_path = run_dir / "summary.json"
    meta = {
        "status": "starting", "run_id": run_id, "started_at_utc": utc_now(),
        "condition": args.condition,
        "condition_source": "operator_verified" if args.condition == "servo_idle" else "unverified",
        "topic": args.topic, "checkpoint": str(checkpoint),
        "checkpoint_sha256": digest, "class_names": NAMES,
        "device": "cpu", "precision": "FP32", "tracker": "botsort.yaml",
        "imgsz": args.imgsz, "confidence_threshold": args.conf, "iou_threshold": args.iou,
        "requested_duration_s": args.duration, "preview_enabled": not args.no_preview,
        "queue_policy": "reliable_depth_5_latest_frame_only",
        "python": sys.version.split()[0], "platform": platform.platform(),
        "torch": torch.__version__, "ultralytics": ultralytics.__version__,
        "opencv": cv2.__version__, "psutil": psutil.__version__,
        "frames_csv": str(run_dir / "frames.csv"),
        "detections_csv": str(run_dir / "detections.csv"),
        "no_image_video_saved": True,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    state = SharedState()
    window_open = False
    spin_thread = None
    worker = None
    node = None
    initialized = False
    history: deque[dict] = deque(maxlen=60)
    last_history = 0.0
    start = None
    stop_reason = "startup_error"
    try:
        with (run_dir / "frames.csv").open("x", newline="") as frame_file, \
             (run_dir / "detections.csv").open("x", newline="") as detection_file:
            frame_writer = csv.DictWriter(frame_file, fieldnames=FRAME_COLUMNS)
            detection_writer = csv.DictWriter(detection_file, fieldnames=DETECTION_COLUMNS)
            frame_writer.writeheader()
            detection_writer.writeheader()
            frame_file.flush()
            detection_file.flush()
            worker = TrialWorker(state, checkpoint, args, frame_writer, detection_writer,
                                 frame_file, detection_file)
            rclpy.init()
            initialized = True
            node = CameraNode(state, args.topic)
            spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
            if not args.no_preview:
                cv2.namedWindow(WINDOW + " | SERVO IDLE TRIAL", cv2.WINDOW_NORMAL)
                cv2.resizeWindow(WINDOW + " | SERVO IDLE TRIAL", 1100, 720)
                window_open = True
            spin_thread.start()
            worker.start()
            meta["status"] = "running"
            meta_path.write_text(json.dumps(meta, indent=2) + "\n")
            print(f"Trial: {run_dir}; condition={args.condition}; duration={args.duration}s", flush=True)
            start = time.monotonic()
            stop_reason = "duration_elapsed"
            try:
                while time.monotonic() - start < args.duration:
                    frame, metrics = state.snapshot()
                    now = time.monotonic()
                    if now - last_history >= 1:
                        history.append(metrics)
                        last_history = now
                    if window_open:
                        cv2.imshow(WINDOW + " | SERVO IDLE TRIAL",
                                   render(frame, metrics, history, offline, args.topic))
                        if cv2.waitKey(90) & 0xFF in (ord("q"), 27):
                            stop_reason = "operator_stopped"
                            break
                        if cv2.getWindowProperty(WINDOW + " | SERVO IDLE TRIAL",
                                                  cv2.WND_PROP_VISIBLE) < 1:
                            stop_reason = "window_closed"
                            break
                    else:
                        time.sleep(0.1)
            finally:
                state.running.clear()
                state.new_frame.set()
                worker.join()
    except KeyboardInterrupt:
        stop_reason = "keyboard_interrupt"
    except Exception as error:
        stop_reason = "fatal_error"
        state.record_error(error)
        meta["fatal_error"] = repr(error)
        raise
    finally:
        state.running.clear()
        state.new_frame.set()
        if initialized and rclpy.ok():
            rclpy.shutdown()
        if spin_thread and spin_thread.is_alive():
            spin_thread.join(timeout=3)
        if node is not None:
            node.destroy_node()
        if worker and worker.is_alive():
            worker.join(timeout=5)
        if window_open:
            cv2.destroyAllWindows()
        _, metrics = state.snapshot()
        meta.update({
            "status": "completed" if metrics["processed_frames"] > 0 and
                      metrics["errors"] == 0 and stop_reason == "duration_elapsed"
                      else "stopped_early" if stop_reason in
                      {"operator_stopped", "window_closed", "keyboard_interrupt"}
                      else "incomplete",
            "stop_reason": stop_reason,
            "actual_loop_duration_s": round(time.monotonic() - start, 2) if start is not None else None,
            "stopped_at_utc": utc_now(), "received_frames": metrics["received_frames"],
            "processed_frames": metrics["processed_frames"],
            "overwritten_frames": metrics["overwritten_frames"],
            "errors": metrics["errors"], "last_error": metrics["last_error"],
        })
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
        print(f"Selesai: {run_dir}; processed={metrics['processed_frames']}; errors={metrics['errors']}", flush=True)
    return 0 if meta["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
