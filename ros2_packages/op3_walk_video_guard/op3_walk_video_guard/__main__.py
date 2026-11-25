"""Guard berjalan dengan batas dua count sebenarnya dan perekam yang disiapkan."""

import argparse
import json
import math
import os
import signal
import time
from datetime import datetime, timezone
from pathlib import Path

import rclpy
import yaml
from op3_equal_live_walk.guard import Guard
from op3_t43_walk_ready.__main__ import HEAD, LEGS, get_modules
from .counts import rad_to_count


class CountGuard(Guard):
    def __init__(self, pan, tilt, path):
        super().__init__(pan, tilt, path)
        self.initial_counts = {name: rad_to_count(value) for name, value in self.baseline.items()}
        self.max_count_delta = 0

    def on_joint(self, msg):
        state = dict(zip(msg.name, msg.position))
        previous_violation = self.head_violation
        try:
            delta = max(abs(rad_to_count(state[name]) - count)
                        for name, count in self.initial_counts.items())
        except (ValueError, KeyError):
            self.head_violation = True
            return
        super().on_joint(msg)
        self.max_count_delta = max(self.max_count_delta, delta)
        # Pertahankan pelanggaran sebelumnya; tepat dua count masih diizinkan.
        self.head_violation = previous_violation or delta > 2


def alive(pid):
    try:
        return Path(f"/proc/{pid}/stat").read_text().split()[2] != "Z"
    except (OSError, IndexError):
        return False


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline-pan", type=float, required=True)
    p.add_argument("--baseline-tilt", type=float, required=True)
    p.add_argument("--preview-pid", type=int, required=True)
    p.add_argument("--record-dir", type=Path, required=True)
    p.add_argument("--report-dir", type=Path, required=True)
    args = p.parse_args()
    for value in (args.baseline_pan, args.baseline_tilt):
        if not math.isfinite(value): p.error("Baseline harus berhingga")
    cmdline = Path(f"/proc/{args.preview_pid}/cmdline")
    command = cmdline.read_bytes().split(b"\0") if alive(args.preview_pid) else []
    if (b"op3_walk_video_guard.preview" not in command or b"--record-dir" not in command
            or os.fsencode(str(args.record_dir)) not in command):
        p.error("PID preview siaga tidak sesuai")
    if args.record_dir.joinpath("recording_stats.json").exists():
        p.error("Folder rekaman sudah pernah dipakai")
    offsets = yaml.safe_load(Path('/home/humanoid/ros2_jazzy/install/op3_manager/share/op3_manager/config/offset.yaml').read_text())['offset']
    if any(offsets.get(name) != 0 for name in HEAD):
        p.error("Offset kepala tidak nol; konversi count perlu ditinjau ulang")
    args.report_dir.mkdir(parents=True, exist_ok=False)
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "limit_counts": 2,
              "preview_pid": args.preview_pid, "record_dir": str(args.record_dir),
              "head_commanded": False, "gait_start_sent": False}
    rclpy.init()
    node = CountGuard(args.baseline_pan, args.baseline_tilt, args.report_dir / "head_samples.csv")
    started = False
    try:
        end = time.monotonic() + 8
        while (node.last_joint_monotonic is None or node.publisher.get_subscription_count() < 1) and time.monotonic() < end:
            rclpy.spin_once(node, timeout_sec=.05)
            if node.head_violation: raise RuntimeError("Kepala melewati dua count sebelum gait")
        if node.last_joint_monotonic is None or node.publisher.get_subscription_count() < 1:
            raise RuntimeError("Telemetry atau subscriber gait tidak tersedia")
        client = node.create_client(__import__('robotis_controller_msgs.srv',fromlist=['GetJointModule']).GetJointModule,
                                    '/robotis/get_present_joint_ctrl_modules')
        if not client.wait_for_service(timeout_sec=5): raise RuntimeError("Service modul tidak tersedia")
        # Gunakan helper bersama; adapter memaparkan get_client/violation yang diharapkan.
        node.get_client = client
        node.violation = False
        modules = get_modules(node, (*HEAD, *LEGS))
        report['modules_before'] = modules
        if any(modules.get(name) != 'none' for name in HEAD): raise RuntimeError("Modul kepala bukan none")
        if any(modules.get(name) != 'walking_module' for name in LEGS): raise RuntimeError("Modul kaki belum siap")
        if node.head_violation: raise RuntimeError("Kepala melewati dua count sebelum gait")
        if not alive(args.preview_pid): raise RuntimeError("Preview tertutup")
        node.command("start"); started = True; report["gait_start_sent"] = True
        report["gait_start_command_utc"] = datetime.now(timezone.utc).isoformat()
        end = time.monotonic() + 3
        while node.ack_utc is None and time.monotonic() < end:
            rclpy.spin_once(node, timeout_sec=.05)
            if node.head_violation: raise RuntimeError("Kepala melewati dua count")
        if node.ack_utc is None: raise RuntimeError("Ack start gait tidak diterima")
        report["gait_start_ack_utc"] = node.ack_utc.isoformat()
        os.kill(args.preview_pid, signal.SIGUSR1)
        report["record_trigger_utc"] = datetime.now(timezone.utc).isoformat()
        print("GAIT MULAI; PEREKAMAN DIPICU", flush=True)
        deadline = time.monotonic() + 16
        stats_path = args.record_dir / "recording_stats.json"
        stats = None
        while time.monotonic() < deadline and stats is None:
            rclpy.spin_once(node, timeout_sec=.05)
            if node.head_violation: raise RuntimeError("Kepala melewati dua count; gait dihentikan")
            if node.last_joint_monotonic is None or time.monotonic()-node.last_joint_monotonic > 1:
                raise RuntimeError("Telemetry terputus; gait dihentikan")
            if not alive(args.preview_pid): raise RuntimeError("Preview tertutup; gait dihentikan")
            if node.stop_ack_utc is not None: raise RuntimeError("Gait berhenti sebelum rekaman selesai")
            if stats_path.is_file():
                try: stats = json.loads(stats_path.read_text())
                except (json.JSONDecodeError, OSError): pass
        if stats is None: raise TimeoutError("Rekaman tidak selesai dalam batas waktu")
        if stats.get("status") != "completed": raise RuntimeError("Rekaman gagal atau terhenti")
        report["recording_stats"] = stats
        report["status"] = "completed"
    except BaseException as exc:
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if started:
            node.command("stop")
            report["stop_command_utc"] = datetime.now(timezone.utc).isoformat()
            end = time.monotonic()+4
            while node.stop_ack_utc is None and time.monotonic() < end:
                try: rclpy.spin_once(node, timeout_sec=.05)
                except Exception: break
            report["stop_ack_utc"] = node.stop_ack_utc.isoformat() if node.stop_ack_utc else None
            if node.stop_ack_utc is None:
                node.command("stop")
                report["status"] = "failed"
                report["stop_error"] = "Ack stop tidak diterima; stop dikirim ulang"
        report["max_head_delta_counts"] = node.max_count_delta
        report["head_violation"] = node.head_violation
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        node.sample_stream.close()
        (args.report_dir / "gait_guard.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps(report,indent=2),flush=True)
        node.destroy_node();rclpy.shutdown()
    return 0 if report["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
