"""Jalankan gait terbatas sambil memantau kepala, kamera dan proses preview."""

import argparse
import json
import os
import signal
import time
from datetime import datetime, timezone
from pathlib import Path

import rclpy
import yaml
from rclpy.qos import qos_profile_sensor_data
from robotis_controller_msgs.srv import GetJointModule
from sensor_msgs.msg import Image
from op3_t43_walk_ready.__main__ import HEAD, LEGS, get_modules
from op3_walk_video_guard.__main__ import CountGuard, alive


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline-pan", type=float, required=True)
    p.add_argument("--baseline-tilt", type=float, required=True)
    p.add_argument("--preview-pid", type=int, required=True)
    p.add_argument("--duration", type=float, default=30)
    p.add_argument("--topic", default="/thesis/image_raw")
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    if not 0 < a.duration <= 63:
        p.error("Durasi harus lebih dari nol dan tidak melebihi 63 detik")
    cmdline = Path(f"/proc/{a.preview_pid}/cmdline")
    if not alive(a.preview_pid) or b"op3_walk_video_guard.preview" not in cmdline.read_bytes().split(b"\0"):
        p.error("Preview KD Hybrid yang disiapkan tidak aktif")
    offsets = yaml.safe_load(Path('/home/humanoid/ros2_jazzy/install/op3_manager/share/op3_manager/config/offset.yaml').read_text())['offset']
    if any(offsets.get(k) != 0 for k in HEAD):
        p.error("Offset kepala tidak nol; konversi count perlu ditinjau")
    a.out_dir.mkdir(parents=True, exist_ok=False)
    report = {"start_utc": datetime.now(timezone.utc).isoformat(), "duration_requested_sec": a.duration,
              "limit_counts": 2, "manual_laptop_recording": True, "head_commanded": False,
              "gait_start_sent": False, "preview_pid": a.preview_pid}
    rclpy.init()
    node = CountGuard(a.baseline_pan, a.baseline_tilt, a.out_dir / 'head_samples.csv')
    node.get_client = node.create_client(GetJointModule, '/robotis/get_present_joint_ctrl_modules')
    node.violation = False
    last_camera = [None]
    def on_camera(_msg):
        last_camera[0] = time.monotonic()
    camera_sub = node.create_subscription(Image, a.topic, on_camera, qos_profile_sensor_data)
    started = False
    def interrupt(_sig, _frame): raise KeyboardInterrupt('operator interrupted')
    signal.signal(signal.SIGTERM, interrupt)
    try:
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=.05)
            if node.head_violation: raise RuntimeError('Kepala melewati dua count sebelum gait')
            if node.last_joint_monotonic and last_camera[0] and node.publisher.get_subscription_count() > 0: break
        if not node.last_joint_monotonic or not last_camera[0] or node.publisher.get_subscription_count() < 1:
            raise RuntimeError('Telemetry, kamera atau subscriber gait tidak tersedia')
        if not node.get_client.wait_for_service(timeout_sec=5): raise RuntimeError('Service modul tidak tersedia')
        modules = get_modules(node, (*HEAD, *LEGS))
        report['modules_before'] = modules
        if any(modules.get(k) != 'none' for k in HEAD): raise RuntimeError('Modul kepala bukan none')
        if any(modules.get(k) != 'walking_module' for k in LEGS): raise RuntimeError('Modul kaki belum siap')
        if node.head_violation: raise RuntimeError('Kepala melewati dua count sebelum gait')
        if not alive(a.preview_pid): raise RuntimeError('Preview tertutup')
        if time.monotonic()-last_camera[0] > 2: raise RuntimeError('Frame kamera terhenti')
        node.command('start'); started = True; report['gait_start_sent'] = True
        report['gait_start_command_utc'] = datetime.now(timezone.utc).isoformat()
        deadline = time.monotonic()+3
        while node.ack_utc is None and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=.05)
            if node.head_violation: raise RuntimeError('Kepala melewati dua count')
        if node.ack_utc is None: raise RuntimeError('Ack start gait tidak diterima')
        report['gait_start_ack_utc'] = node.ack_utc.isoformat()
        print('GAIT MULAI - OPERATOR SILAKAN REKAM - STOP OTOMATIS',flush=True)
        while time.monotonic() < node.ack_monotonic+a.duration:
            rclpy.spin_once(node, timeout_sec=.05)
            if node.head_violation: raise RuntimeError('Kepala melewati dua count')
            if not node.last_joint_monotonic or time.monotonic()-node.last_joint_monotonic > 1:
                raise RuntimeError('Telemetry sendi terputus')
            if not last_camera[0] or time.monotonic()-last_camera[0] > 2:
                raise RuntimeError('Frame kamera terputus')
            if not alive(a.preview_pid): raise RuntimeError('Preview tertutup')
            if node.stop_ack_utc is not None: raise RuntimeError('Gait berhenti sebelum durasi berakhir')
        report['status']='completed'
    except BaseException as exc:
        report['status']='failed'; report['error']=f'{type(exc).__name__}: {exc}'
    finally:
        if started:
            node.command('stop'); report['stop_command_utc']=datetime.now(timezone.utc).isoformat()
            end=time.monotonic()+4
            while node.stop_ack_utc is None and time.monotonic()<end:
                try:rclpy.spin_once(node,timeout_sec=.05)
                except Exception:break
            report['stop_ack_utc']=node.stop_ack_utc.isoformat() if node.stop_ack_utc else None
            if node.stop_ack_utc is None:
                node.command('stop'); report['status']='failed';report['stop_error']='Stop dikirim ulang, ack tidak diterima'
        report['max_head_delta_counts']=node.max_count_delta
        report['head_violation']=node.head_violation
        report['finish_utc']=datetime.now(timezone.utc).isoformat()
        node.sample_stream.close()
        with (a.out_dir/'gait_guard.json').open('x') as f: json.dump(report,f,indent=2);f.write('\n')
        print(json.dumps(report,indent=2),flush=True)
        node.destroy_subscription(camera_sub);node.destroy_node();rclpy.shutdown()
    return 0 if report['status']=='completed' else 1


if __name__ == '__main__': raise SystemExit(main())
