"""Jalankan gait 63 detik setelah warm-up sambil menjaga posisi kepala."""

from __future__ import annotations

import argparse
import csv
import json
import math
import signal
import time
from datetime import datetime, timezone
from pathlib import Path

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from robotis_controller_msgs.msg import StatusMsg
from sensor_msgs.msg import JointState
from std_msgs.msg import String

HEAD_LIMIT_RAD = 2 * math.pi / 2048  # dua encoder count


def first_measure_time(path: Path) -> datetime | None:
    if not path.is_file():
        return None
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row.get("is_warmup", "").lower() == "false":
                return datetime.fromisoformat(row["receive_time_utc"])
    return None


class Guard(Node):
    def __init__(self, baseline_pan: float, baseline_tilt: float, sample_path: Path) -> None:
        super().__init__("op3_equal_live_walk_guard")
        self.baseline = {"head_pan": baseline_pan, "head_tilt": baseline_tilt}
        self.max_head_delta = 0.0
        self.head_violation = False
        self.last_joint_monotonic = None
        self.last_sample_monotonic = 0.0
        self.ack_utc = None
        self.ack_monotonic = None
        self.stop_ack_utc = None
        self.publisher = self.create_publisher(String, "/robotis/walking/command", 10)
        self.joint_sub = self.create_subscription(JointState, "/robotis/present_joint_states", self.on_joint, qos_profile_sensor_data)
        self.status_sub = self.create_subscription(StatusMsg, "/robotis/status", self.on_status, 10)
        self.sample_stream = sample_path.open("x", newline="", encoding="utf-8")
        self.sample_writer = csv.writer(self.sample_stream)
        self.sample_writer.writerow(["receive_time_utc", "head_pan_rad", "head_tilt_rad", "head_delta_rad", "l_hip_pitch_rad", "l_knee_rad", "r_hip_pitch_rad", "r_knee_rad"])

    def on_joint(self, msg: JointState) -> None:
        state = dict(zip(msg.name, msg.position))
        if not all(j in state for j in (*self.baseline, "l_hip_pitch", "l_knee", "r_hip_pitch", "r_knee")):
            return
        self.last_joint_monotonic = time.monotonic()
        delta = max(abs(state[j] - value) for j, value in self.baseline.items())
        self.max_head_delta = max(self.max_head_delta, delta)
        if delta > HEAD_LIMIT_RAD:
            self.head_violation = True
        if self.last_joint_monotonic - self.last_sample_monotonic >= 1.0:
            self.sample_writer.writerow([datetime.now(timezone.utc).isoformat(), state["head_pan"], state["head_tilt"], delta, state["l_hip_pitch"], state["l_knee"], state["r_hip_pitch"], state["r_knee"]])
            self.sample_stream.flush()
            self.last_sample_monotonic = self.last_joint_monotonic

    def on_status(self, msg: StatusMsg) -> None:
        if msg.module_name.lower() != "walking":
            return
        if msg.status_msg == "Start walking" and self.ack_utc is None:
            self.ack_utc = datetime.now(timezone.utc)
            self.ack_monotonic = time.monotonic()
        elif msg.status_msg == "Stop walking":
            self.stop_ack_utc = datetime.now(timezone.utc)

    def command(self, value: str) -> None:
        self.publisher.publish(String(data=value))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--baseline-pan", type=float, required=True)
    parser.add_argument("--baseline-tilt", type=float, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.out_dir / "gait_guard.json"
    if report_path.exists() or (args.out_dir / "head_guard_samples.csv").exists():
        parser.error("Artefak gait guard sudah ada; gunakan run_id baru")
    report = {"run_csv": str(args.csv), "started_at_utc": datetime.now(timezone.utc).isoformat(), "baseline_pan_rad": args.baseline_pan, "baseline_tilt_rad": args.baseline_tilt, "head_limit_rad": HEAD_LIMIT_RAD}
    rclpy.init()
    node = Guard(args.baseline_pan, args.baseline_tilt, args.out_dir / "head_guard_samples.csv")
    started = False
    stopped = False

    def interrupt(_signal, _frame) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, interrupt)
    try:
        deadline = time.monotonic() + 120
        tw = None
        while tw is None:
            rclpy.spin_once(node, timeout_sec=0.05)
            if node.head_violation:
                raise RuntimeError("Kepala bergeser sebelum gait")
            if time.monotonic() > deadline:
                raise TimeoutError("Tidak ada frame sesudah warm-up")
            tw = first_measure_time(args.csv)
        report["t_w_utc"] = tw.isoformat()
        target = tw.timestamp() + 3
        while time.time() < target:
            rclpy.spin_once(node, timeout_sec=0.05)
            if node.head_violation:
                raise RuntimeError("Kepala bergeser sebelum gait")
        if time.time() > tw.timestamp() + 10:
            raise RuntimeError("Gait terlambat; jendela tidak sah")
        if node.publisher.get_subscription_count() < 1 or node.last_joint_monotonic is None:
            raise RuntimeError("Walking subscriber atau telemetry sendi tidak tersedia")
        node.command("start")
        started = True
        report["start_command_utc"] = datetime.now(timezone.utc).isoformat()
        ack_deadline = time.monotonic() + 3
        while node.ack_utc is None and time.monotonic() < ack_deadline:
            rclpy.spin_once(node, timeout_sec=0.05)
        if node.ack_utc is None:
            raise RuntimeError("Ack Start walking tidak diterima")
        report["start_ack_receive_utc"] = node.ack_utc.isoformat()
        (args.out_dir / "gait_start_ack_utc.txt").write_text(node.ack_utc.isoformat() + "\n", encoding="utf-8")
        print("GAIT_STARTED", node.ack_utc.isoformat(), flush=True)
        while time.monotonic() < node.ack_monotonic + 63:
            rclpy.spin_once(node, timeout_sec=0.05)
            if node.head_violation:
                raise RuntimeError("Posisi kepala melewati dua count; gait dihentikan")
            if node.last_joint_monotonic is None or time.monotonic() - node.last_joint_monotonic > 2.0:
                raise RuntimeError("Telemetry sendi terputus; gait dihentikan")
        node.command("stop")
        stopped = True
        report["stop_command_utc"] = datetime.now(timezone.utc).isoformat()
        (args.out_dir / "gait_stop_sent_utc.txt").write_text(report["stop_command_utc"] + "\n", encoding="utf-8")
        stop_deadline = time.monotonic() + 3
        while node.stop_ack_utc is None and time.monotonic() < stop_deadline:
            rclpy.spin_once(node, timeout_sec=0.05)
        report["stop_ack_receive_utc"] = node.stop_ack_utc.isoformat() if node.stop_ack_utc else None
        report["status"] = "completed" if node.stop_ack_utc else "stop_sent_no_ack"
    except BaseException as exc:
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if started and not stopped:
            node.command("stop")
            report["emergency_stop_utc"] = datetime.now(timezone.utc).isoformat()
            for _ in range(10):
                rclpy.spin_once(node, timeout_sec=0.05)
        report["max_head_delta_rad"] = node.max_head_delta
        report["head_violation"] = node.head_violation
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        node.sample_stream.close()
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        node.destroy_node()
        rclpy.shutdown()
        print(json.dumps(report, indent=2), flush=True)
    return 0 if report["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
