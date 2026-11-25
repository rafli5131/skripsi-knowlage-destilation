"""Preview deteksi OP3 dan grafik dalam jendela X11 yang bisa fullscreen."""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "ros2_packages" / "op3_live_monitor"))

import cv2
import numpy as np
import rclpy
import torch
from cv_bridge import CvBridge
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image

from model_registry import (checkpoint_for_variant, load_local_overrides, load_registry,
                            resolve_registered_path, validate_checkpoint)
from op3_live_monitor.monitor import BG, InferenceWorker, SharedState, label, render
from .recorder import PreviewRecorder

WINDOW = "OP3 Preview Deteksi - F fullscreen - Q keluar"
MODELS = {
    "hybrid": ("KD HYBRID FULL seed 1337", "hybrid"),
    "supervised": ("SUPERVISED seed 1337", None),
    "kd": ("KD MURNI seed 42", "kd"),
    "teacher": ("TEACHER YOLO11n", "teacher"),
}


def resolve_model(choice: str) -> tuple[Path, str]:
    variant = MODELS[choice][1]
    if variant:
        name, checkpoint = checkpoint_for_variant(variant)
    else:
        name = "supervised_seed1337"
        registry = load_registry()
        checkpoint = load_local_overrides(registry).get(name)
        if checkpoint is None:
            checkpoint = resolve_registered_path(registry["models"][name]["checkpoint"])
    _, entry = validate_checkpoint(checkpoint, label=name)
    return checkpoint, str(entry["sha256"])


class CameraSubscriber(Node):
    def __init__(self, state: SharedState, topic: str, reliable: bool) -> None:
        super().__init__("op3_fullscreen_preview")
        self.state = state
        self.bridge = CvBridge()
        reliability = ReliabilityPolicy.RELIABLE if reliable else ReliabilityPolicy.BEST_EFFORT
        self.subscription = self.create_subscription(
            Image, topic, self.on_image, QoSProfile(depth=1, reliability=reliability)
        )

    def on_image(self, message: Image) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            if frame is None or frame.size == 0:
                raise ValueError("Frame kamera kosong")
            stamp = int(message.header.stamp.sec) * 1_000_000_000 + int(message.header.stamp.nanosec)
            self.state.accept(frame, stamp)
        except Exception as error:
            self.state.record_error(error)


def dashboard(frame, metrics: dict, history: deque, model: str, topic: str):
    # Gunakan ulang grafik dan tata letak monitor lama, tanpa metrik TEST model lain.
    canvas = render(frame, metrics, history, {}, topic)
    cv2.rectangle(canvas, (0, 0), (960, 39), BG, -1)
    label(canvas, f"OP3  /  {model}", 18, 30, 0.70, thickness=2)
    cv2.rectangle(canvas, (0, 678), (1099, 719), BG, -1)
    label(canvas, "Confidence bukan akurasi | CPU/RAM: proses preview + inferensi", 18, 699, 0.43)
    label(canvas, "1: kamera  2: grafik  F: fullscreen  Q: keluar", 650, 699, 0.38)
    return canvas


def camera_view(frame, metrics: dict):
    """Tampilkan frame deteksi saja; tandai jika aliran sudah tidak live."""
    if frame is None:
        canvas = np.full((480, 640, 3), BG, dtype=np.uint8)
        label(canvas, "Menunggu frame kamera...", 150, 240, 0.7)
        return canvas
    if metrics["status"] != "LIVE":
        canvas = frame.copy()
        cv2.rectangle(canvas, (0, 0), (canvas.shape[1], 38), BG, -1)
        label(canvas, "FRAME TERHENTI - menunggu kamera", 10, 26, 0.6, (71, 188, 255), 2)
        return canvas
    return frame


def spin_until_shutdown(node: Node) -> None:
    try:
        rclpy.spin(node)
    except ExternalShutdownException:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=MODELS, default="hybrid")
    parser.add_argument("--topic", default="/thesis/image_raw")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--reliable", action="store_true", help="Gunakan QoS reliable bila diperlukan")
    parser.add_argument("--windowed", action="store_true", help="Mulai dalam jendela, bukan fullscreen")
    parser.add_argument("--view", choices=("camera", "dashboard"), default="camera",
                        help="Tampilan awal: kamera saja atau dashboard grafik")
    parser.add_argument("--threads", type=int, default=4, help="Jumlah thread PyTorch CPU")
    parser.add_argument("--preview-fps", type=float, default=5.0, help="Batas pembaruan jendela X11")
    parser.add_argument("--record-dir", type=Path, help="Folder unik untuk rekaman keluaran deteksi")
    parser.add_argument("--record-duration", type=float, default=10.0)
    parser.add_argument("--record-fps", type=float, default=10.0)
    args = parser.parse_args()
    if (args.imgsz <= 0 or not 0 <= args.conf <= 1 or not 0 <= args.iou <= 1
            or args.threads <= 0 or not 0 < args.preview_fps <= 60
            or args.record_duration <= 0 or not 0 < args.record_fps <= 60):
        parser.error("Periksa imgsz, threads, conf, iou, preview-fps, record-duration dan record-fps")
    if not os.environ.get("DISPLAY"):
        parser.error("DISPLAY kosong; sambungkan ulang dengan ssh -X")
    try:
        checkpoint, digest = resolve_model(args.model)
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))
    print(f"Model: {MODELS[args.model][0]}\nCheckpoint: {checkpoint}\nSHA-256: {digest}", flush=True)
    torch.set_num_threads(args.threads)
    state = SharedState()
    worker = InferenceWorker(state, checkpoint, args)
    rclpy.init()
    node = CameraSubscriber(state, args.topic, args.reliable)
    spin_thread = threading.Thread(target=spin_until_shutdown, args=(node,), daemon=True)
    recorder = (PreviewRecorder(state, args.record_dir, args.record_duration, args.record_fps)
                if args.record_dir else None)
    history: deque = deque(maxlen=60)
    last_history = 0.0
    reported_live = False
    reported_errors = 0
    fullscreen = not args.windowed
    view = args.view
    window_open = False
    try:
        cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
        window_open = True
        cv2.resizeWindow(WINDOW, 1100, 720)
        spin_thread.start()
        worker.start()
        if recorder:
            recorder.start()
        print(f"Preview aktif: {args.topic} | threads={args.threads} | preview_fps={args.preview_fps:g} | "
              "1: kamera | 2: grafik | F: fullscreen | Q/Esc: keluar", flush=True)
        apply_initial_fullscreen = fullscreen
        while rclpy.ok() and state.running.is_set():
            frame, metrics = state.snapshot()
            if metrics["processed_frames"] and not reported_live:
                print("Frame kamera pertama selesai diproses; preview LIVE.", flush=True)
                reported_live = True
            if metrics["errors"] > reported_errors:
                print(f"Kesalahan preview: {metrics['last_error']}", file=sys.stderr, flush=True)
                reported_errors = metrics["errors"]
            now = time.monotonic()
            if now - last_history >= 1:
                history.append(metrics)
                last_history = now
            image = (camera_view(frame, metrics) if view == "camera" else
                     dashboard(frame, metrics, history, MODELS[args.model][0], args.topic))
            cv2.imshow(WINDOW, image)
            if apply_initial_fullscreen:
                # Qt/X11 perlu menampilkan jendela sebelum meminta fullscreen ke window manager.
                cv2.waitKey(1)
                cv2.setWindowProperty(WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                apply_initial_fullscreen = False
            key = cv2.waitKey(max(1, round(1000 / args.preview_fps))) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
            if key == ord("1"):
                view = "camera"
                print("Tampilan: kamera dan kotak deteksi", flush=True)
            if key == ord("2"):
                view = "dashboard"
                print("Tampilan: dashboard dan grafik", flush=True)
            if key in (ord("f"), ord("F")):
                fullscreen = not fullscreen
                cv2.setWindowProperty(WINDOW, cv2.WND_PROP_FULLSCREEN,
                                      cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL)
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
        if recorder and recorder.is_alive():
            recorder.join(timeout=35)
        if window_open:
            cv2.destroyWindow(WINDOW)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
