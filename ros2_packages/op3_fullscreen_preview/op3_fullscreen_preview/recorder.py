"""Rekam frame beranotasi dari inferensi preview yang sama, tanpa screen grab."""

from __future__ import annotations

import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np


class PreviewRecorder(threading.Thread):
    def __init__(self, state, directory: Path, duration: float, fps: float):
        super().__init__(name="preview-recorder", daemon=True)
        self.state = state
        self.directory = directory
        self.duration = duration
        self.fps = fps
        self.finished = threading.Event()

    def run(self):
        process = None
        log = None
        frames = 0
        repeated = 0
        last_sequence = None
        first_sequence = None
        end_sequence = None
        started = None
        start_iso = None
        error = None
        reason = "completed"
        try:
            deadline = time.monotonic() + 30
            while self.state.running.is_set():
                frame, metrics = self.state.snapshot()
                if frame is not None and metrics["status"] == "LIVE":
                    break
                if time.monotonic() >= deadline:
                    raise TimeoutError("Tidak ada frame deteksi LIVE dalam 30 detik")
                time.sleep(0.05)
            else:
                raise RuntimeError("Preview berhenti sebelum perekaman")
            h, w = frame.shape[:2]
            self.directory.mkdir(parents=True, exist_ok=True)
            output = self.directory / "preview_deteksi_langsung.mp4"
            log = (self.directory / "ffmpeg.log").open("x", encoding="utf-8")
            process = subprocess.Popen([
                "ffmpeg", "-hide_banner", "-loglevel", "warning", "-nostdin", "-n",
                "-f", "rawvideo", "-pixel_format", "bgr24", "-video_size", f"{w}x{h}",
                "-framerate", str(self.fps), "-i", "pipe:0", "-an", "-c:v", "libx264",
                "-threads", "2", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", str(output),
            ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
            start_iso = datetime.now().astimezone().isoformat(timespec="seconds")
            started = time.monotonic()
            next_frame = started
            print(f"PEREKAMAN MULAI: {self.duration:g} detik | {output}", flush=True)
            while self.state.running.is_set() and time.monotonic() - started < self.duration:
                wait = next_frame - time.monotonic()
                if wait > 0:
                    time.sleep(wait)
                if time.monotonic() - started >= self.duration:
                    break
                frame, metrics = self.state.snapshot()
                if frame is None or metrics["status"] != "LIVE":
                    reason = "preview_stalled"
                    break
                if frame.shape[:2] != (h, w):
                    raise ValueError("Ukuran frame berubah selama perekaman")
                sequence = metrics["processed_frames"]
                first_sequence = sequence if first_sequence is None else first_sequence
                end_sequence = sequence
                if sequence == last_sequence:
                    repeated += 1
                last_sequence = sequence
                process.stdin.write(np.ascontiguousarray(frame).tobytes())
                frames += 1
                next_frame = max(next_frame + 1.0 / self.fps, time.monotonic())
            if not self.state.running.is_set():
                reason = "preview_stopped"
            process.stdin.close()
            if process.wait(timeout=30) != 0:
                raise RuntimeError("FFmpeg gagal; lihat ffmpeg.log")
        except Exception as exc:
            error = str(exc)
            reason = "error"
            if process is not None and process.poll() is None:
                if process.stdin and not process.stdin.closed:
                    process.stdin.close()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        finally:
            if log:
                log.close()
            wall = round(time.monotonic() - started, 3) if started is not None else None
            stats = {
                "status": reason, "error": error, "start_local": start_iso,
                "requested_duration_seconds": self.duration, "elapsed_seconds_including_finalize": wall,
                "encoded_frames": frames, "configured_fps": self.fps,
                "nominal_video_seconds": round(frames / self.fps, 3),
                "repeated_previous_inference_frame": repeated,
                "first_processed_frame_sequence": first_sequence,
                "last_processed_frame_sequence": end_sequence,
                "type": "annotated_preview_output_not_desktop_screen_record",
            }
            self.directory.mkdir(parents=True, exist_ok=True)
            with (self.directory / "recording_stats.json").open("x", encoding="utf-8") as stream:
                json.dump(stats, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
            print(f"PEREKAMAN SELESAI: status={reason}, frame={frames}, berulang={repeated}", flush=True)
            self.finished.set()
