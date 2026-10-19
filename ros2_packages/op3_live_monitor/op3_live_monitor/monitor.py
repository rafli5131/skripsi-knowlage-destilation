"""Show live OP3 camera tracking and performance in an X11 window."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import threading
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import psutil
import rclpy
import yaml
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image
from ultralytics import YOLO


REPO_ROOT = Path(__file__).resolve().parents[3]
NAMES = {0: "ball", 1: "gawang", 2: "robot"}
COLORS = {"ball": (36, 187, 255), "gawang": (112, 224, 123), "robot": (255, 154, 87)}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_offline_metrics(repo_root: Path, checkpoint_hash: str) -> dict[str, float]:
    path = repo_root / "artifacts/thesis_analysis_final_corrected/per_model.csv"
    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row.get("model") == "kd_seed42" and row.get("checkpoint_sha256") == checkpoint_hash:
                return {
                    "precision": float(row["test_precision"]),
                    "recall": float(row["test_recall"]),
                    "f1": float(row["test_F1"]),
                    "map50": float(row["test_mAP50"]),
                    "map50_95": float(row["test_mAP50_95"]),
                }
    return {}


def validate_model(repo_root: Path) -> tuple[Path, str, dict[str, float]]:
    registry = yaml.safe_load((repo_root / "configs/model_registry.yaml").read_text(encoding="utf-8"))
    alias = registry["aliases"]["op3_default"]
    checkpoint = repo_root / alias["checkpoint"]
    if not checkpoint.is_file():
        raise FileNotFoundError(f"Checkpoint tidak ada: {checkpoint}")
    digest = sha256_file(checkpoint)
    if digest != alias["sha256"]:
        raise ValueError("SHA-256 checkpoint berbeda dari registry op3_default")
    data = yaml.safe_load((repo_root / "configs/data_train_val.yaml").read_text(encoding="utf-8"))
    if {int(key): str(value) for key, value in data["names"].items()} != NAMES:
        raise ValueError("Mapping kelas dataset tidak cocok")
    return checkpoint, digest, load_offline_metrics(repo_root, digest)


class SharedState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.latest_input: tuple[np.ndarray, int] | None = None
        self.new_frame = threading.Event()
        self.running = threading.Event()
        self.running.set()
        self.display_frame: np.ndarray | None = None
        self.frame_times: deque[float] = deque(maxlen=120)
        self.last_processed = 0.0
        self.metrics = {
            "received_frames": 0, "processed_frames": 0, "overwritten_frames": 0,
            "errors": 0, "last_error": "", "fps": 0.0, "inference_ms": 0.0,
            "preprocess_ms": 0.0, "postprocess_ms": 0.0, "end_to_end_ms": 0.0,
            "camera_age_ms": None, "process_cpu_percent": 0.0,
            "system_cpu_percent": 0.0, "process_ram_mib": 0.0,
            "system_ram_percent": 0.0,
            "counts": {name: 0 for name in NAMES.values()}, "detections": [],
        }

    def accept(self, frame: np.ndarray, stamp_ns: int) -> None:
        with self.lock:
            self.metrics["received_frames"] += 1
            if self.latest_input is not None:
                self.metrics["overwritten_frames"] += 1
            self.latest_input = (frame, stamp_ns)
            self.new_frame.set()

    def take_latest(self) -> tuple[np.ndarray, int] | None:
        with self.lock:
            item = self.latest_input
            self.latest_input = None
            self.new_frame.clear()
            return item

    def record_error(self, error: Exception) -> None:
        with self.lock:
            self.metrics["errors"] += 1
            self.metrics["last_error"] = str(error)[:150]

    def record(self, frame: np.ndarray, values: dict) -> None:
        with self.lock:
            now = time.monotonic()
            self.frame_times.append(now)
            while self.frame_times and now - self.frame_times[0] > 3.0:
                self.frame_times.popleft()
            fps = 0.0
            if len(self.frame_times) > 1:
                fps = (len(self.frame_times) - 1) / (self.frame_times[-1] - self.frame_times[0])
            self.metrics.update(values)
            self.metrics["processed_frames"] += 1
            self.metrics["fps"] = fps
            self.last_processed = now
            self.display_frame = frame

    def snapshot(self) -> tuple[np.ndarray | None, dict]:
        with self.lock:
            data = dict(self.metrics)
            data["counts"] = dict(self.metrics["counts"])
            data["detections"] = list(self.metrics["detections"])
            data["status"] = "LIVE" if self.last_processed and time.monotonic() - self.last_processed < 3 else "MENUNGGU"
            if data["status"] != "LIVE":
                data["fps"] = 0.0
            return self.display_frame, data


class CameraNode(Node):
    def __init__(self, state: SharedState, topic: str) -> None:
        super().__init__("op3_live_monitor")
        self.state = state
        self.bridge = CvBridge()
        qos = QoSProfile(depth=5, reliability=ReliabilityPolicy.RELIABLE)
        self.subscription = self.create_subscription(Image, topic, self.on_image, qos)

    def on_image(self, message: Image) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            if frame is None or frame.size == 0:
                raise ValueError("Frame kamera kosong")
            stamp_ns = int(message.header.stamp.sec) * 1_000_000_000 + int(message.header.stamp.nanosec)
            self.state.accept(frame, stamp_ns)
        except Exception as error:
            self.state.record_error(error)


class InferenceWorker(threading.Thread):
    def __init__(self, state: SharedState, checkpoint: Path, args: argparse.Namespace) -> None:
        super().__init__(name="op3-live-inference", daemon=True)
        self.state = state
        self.args = args
        self.model = YOLO(str(checkpoint), task="detect")
        if {int(key): str(value) for key, value in self.model.names.items()} != NAMES:
            raise ValueError("Mapping kelas checkpoint tidak cocok")
        self.model.to("cpu")
        self.model.model.float()
        self.model.model.eval()
        self.process = psutil.Process()
        self.process.cpu_percent(interval=None)
        psutil.cpu_percent(interval=None)
        self.last_resource_update = 0.0
        self.resources = {}

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
                    source=frame,
                    imgsz=self.args.imgsz,
                    batch=1,
                    device="cpu",
                    conf=self.args.conf,
                    iou=self.args.iou,
                    tracker="botsort.yaml",
                    persist=True,
                    verbose=False,
                    save=False,
                    plots=False,
                    stream=False,
                    max_det=300,
                )[0]
                annotated = frame.copy()
                counts = {name: 0 for name in NAMES.values()}
                detections = []
                if result.boxes is not None:
                    for box in result.boxes:
                        name = NAMES[int(box.cls.item())]
                        score = float(box.conf.item())
                        track_id = int(box.id.item()) if box.id is not None else None
                        x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
                        counts[name] += 1
                        detections.append({"class": name, "confidence": round(score, 4), "track_id": track_id})
                        color = COLORS[name]
                        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                        label = f"{name} #{track_id}" if track_id is not None else name
                        label += f"  {score:.2f}"
                        top = max(0, y1 - 25)
                        cv2.rectangle(annotated, (x1, top), (min(x2 + 45, annotated.shape[1] - 1), y1), color, -1)
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
                self.state.record(annotated, {
                    "counts": counts,
                    "detections": detections,
                    "inference_ms": round(float(result.speed.get("inference", 0)), 2),
                    "preprocess_ms": round(float(result.speed.get("preprocess", 0)), 2),
                    "postprocess_ms": round(float(result.speed.get("postprocess", 0)), 2),
                    "end_to_end_ms": round((time.perf_counter() - started) * 1000, 2),
                    "camera_age_ms": round(camera_age, 1) if camera_age is not None else None,
                    **self.resources,
                })
            except Exception as error:
                self.state.record_error(error)


BG = (21, 26, 34)
TEXT = (231, 236, 241)
MUTED = (155, 167, 180)
WINDOW = "OP3 Live Tracking - q/Esc keluar"


def label(canvas: np.ndarray, value: str, x: int, y: int, size: float = 0.5,
          color: tuple[int, int, int] = TEXT, thickness: int = 1) -> None:
    cv2.putText(canvas, value, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                size, color, thickness, cv2.LINE_AA)


def graph(canvas: np.ndarray, history: deque[dict], key: str,
          x: int, title: str, color: tuple[int, int, int], minimum: float, unit: str) -> None:
    y, width, height = 570, 255, 105
    cv2.rectangle(canvas, (x, y), (x + width, y + height), (32, 40, 51), -1)
    cv2.line(canvas, (x + 10, y + height - 17),
             (x + width - 10, y + height - 17), (71, 83, 96), 1)
    values = [float(point.get(key, 0) or 0) for point in history]
    last = values[-1] if values else 0.0
    label(canvas, f"{title}  {last:.1f}{unit}", x + 10, y + 20, 0.46, color)
    if len(values) < 2:
        return
    top, bottom = y + 32, y + height - 17
    maximum = max(minimum, max(values) * 1.15)
    points = np.array([
        (x + 10 + round(i * (width - 20) / (len(values) - 1)),
         bottom - round(min(value / maximum, 1) * (bottom - top)))
        for i, value in enumerate(values)
    ], dtype=np.int32)
    cv2.polylines(canvas, [points], False, color, 2, cv2.LINE_AA)


def render(frame: np.ndarray | None, m: dict, history: deque[dict],
           offline: dict[str, float], topic: str) -> np.ndarray:
    canvas = np.full((720, 1100, 3), BG, dtype=np.uint8)
    label(canvas, "OP3  /  LIVE CAMERA TRACKING", 18, 30, 0.75, TEXT, 2)
    label(canvas, m["status"], 968, 30, 0.65,
          (97, 221, 141) if m["status"] == "LIVE" else (71, 188, 255), 2)
    if frame is not None:
        h, w = frame.shape[:2]
        scale = min(640 / w, 480 / h)
        image = cv2.resize(frame, (round(w * scale), round(h * scale)))
        x0 = 18 + (640 - image.shape[1]) // 2
        y0 = 47 + (480 - image.shape[0]) // 2
        canvas[y0:y0 + image.shape[0], x0:x0 + image.shape[1]] = image
    else:
        label(canvas, "Menunggu frame kamera...", 170, 290, 0.7)
    cv2.rectangle(canvas, (18, 47), (658, 527), (91, 104, 119), 1)
    x = 680
    label(canvas, "DETEKSI & TRACKING", x, 70, 0.62, TEXT, 2)
    label(canvas, "Confidence per kotak, bukan akurasi live", x, 95, 0.42, MUTED)
    for i, name in enumerate(NAMES.values()):
        label(canvas, f"{name}: {m['counts'][name]}", x, 128 + 26 * i, 0.57, COLORS[name])
    for i, detection in enumerate(m["detections"][:4]):
        track = f"#{detection['track_id']}" if detection['track_id'] is not None else "tanpa ID"
        label(canvas, f"{detection['class']} {track}  {detection['confidence'] * 100:.1f}%",
              x, 219 + 22 * i, 0.48)
    label(canvas, "PERFORMA", x, 326, 0.62, TEXT, 2)
    age = m["camera_age_ms"]
    rows = [
        f"FPS: {m['fps']:.1f}   inferensi: {m['inference_ms']:.1f} ms",
        f"Total: {m['end_to_end_ms']:.1f} ms   umur kamera: {age:.0f} ms" if age is not None else
        f"Total: {m['end_to_end_ms']:.1f} ms   umur kamera: N/A",
        f"CPU proses: {m['process_cpu_percent']:.0f}%   sistem: {m['system_cpu_percent']:.0f}%",
        f"RAM proses: {m['process_ram_mib']:.0f} MiB   sistem: {m['system_ram_percent']:.0f}%",
        f"Frame masuk: {m['received_frames']}   diproses: {m['processed_frames']}",
        f"Tertimpa: {m['overwritten_frames']}   error: {m['errors']}",
    ]
    for i, row in enumerate(rows):
        label(canvas, row, x, 355 + 26 * i, 0.46)
    if m["last_error"]:
        label(canvas, m["last_error"][:48], x, 525, 0.37, (86, 117, 255))
    label(canvas, "GRAFIK REALTIME  /  60 detik terakhir", 18, 556, 0.57, TEXT, 2)
    graph(canvas, history, "fps", 18, "FPS", (102, 218, 130), 30, "")
    graph(canvas, history, "inference_ms", 286, "Inferensi", (68, 189, 252), 50, " ms")
    graph(canvas, history, "process_cpu_percent", 554, "CPU proses", (234, 183, 115), 100, "%")
    graph(canvas, history, "process_ram_mib", 822, "RAM proses", (226, 127, 212), 500, " MiB")
    if offline:
        info = (f"TEST offline: P {offline['precision'] * 100:.1f}%  R {offline['recall'] * 100:.1f}%  "
                f"F1 {offline['f1'] * 100:.1f}%  mAP50 {offline['map50'] * 100:.1f}%  "
                f"mAP50-95 {offline['map50_95'] * 100:.1f}%")
    else:
        info = "Metrik TEST offline tidak tersedia"
    label(canvas, info, 18, 699, 0.43, MUTED)
    label(canvas, f"{topic}  |  q/Esc keluar  |  tanpa rekaman", 677, 699, 0.37, MUTED)
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--topic", default="/thesis/image_raw")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    args = parser.parse_args()
    if args.imgsz <= 0 or not 0 <= args.conf <= 1 or not 0 <= args.iou <= 1:
        parser.error("imgsz harus positif; conf dan iou harus antara 0 dan 1")
    if not os.environ.get("DISPLAY"):
        parser.error("DISPLAY kosong. Jalankan dari terminal SSH -X dengan X11 forwarding aktif.")
    checkpoint, digest, offline = validate_model(args.repo_root.resolve())
    state = SharedState()
    worker = InferenceWorker(state, checkpoint, args)
    rclpy.init()
    node = CameraNode(state, args.topic)
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), name="op3-live-ros", daemon=True)
    history: deque[dict] = deque(maxlen=60)
    last_history = 0.0
    window_open = False
    try:
        cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
        window_open = True
        cv2.resizeWindow(WINDOW, 1100, 720)
        spin_thread.start()
        worker.start()
        print(f"Jendela X11: {args.topic}; CPU FP32; BoT-SORT; SHA-256={digest}", flush=True)
        while state.running.is_set():
            frame, metrics = state.snapshot()
            now = time.monotonic()
            if now - last_history >= 1:
                history.append(metrics)
                last_history = now
            cv2.imshow(WINDOW, render(frame, metrics, history, offline, args.topic))
            if cv2.waitKey(90) & 0xFF in (ord("q"), 27):
                break
            if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                break
    except KeyboardInterrupt:
        pass
    finally:
        state.running.clear()
        state.new_frame.set()
        if rclpy.ok():
            rclpy.shutdown()
        if spin_thread.is_alive():
            spin_thread.join(timeout=3)
        node.destroy_node()
        if worker.is_alive():
            worker.join(timeout=3)
        if window_open:
            cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
