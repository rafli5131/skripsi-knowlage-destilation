"""Enable head-servo torque while holding the measured pan/tilt positions."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from dynamixel_sdk import COMM_SUCCESS

from op3_servo_torque_control.cli import ServoBus

HEAD_IDS = (19, 20)
BODY_IDS = tuple(range(1, 19))
GOAL_POSITION = 116
TORQUE_ENABLE = 64
MAX_POSITION = 4095


def validate(snapshot: dict) -> None:
    if snapshot["controller_dynamixel_power"] != 1:
        raise RuntimeError("Daya bus Dynamixel OpenCR tidak aktif")
    servos = snapshot["servos"]
    for servo_id in (*BODY_IDS, *HEAD_IDS):
        item = servos[str(servo_id)]
        if item["model"] != 1020:
            raise RuntimeError(f"ID {servo_id}: model tidak sesuai (didapat {item['model']})")
        if item["operating_mode"] != 3:
            raise RuntimeError(f"ID {servo_id}: bukan mode posisi 3")
        if item["hardware_error"] != 0:
            raise RuntimeError(f"ID {servo_id}: hardware_error={item['hardware_error']}")
        if not 0 <= item["present_position"] <= MAX_POSITION:
            raise RuntimeError(f"ID {servo_id}: posisi aktual di luar rentang")
    if any(servos[str(sid)]["torque_enabled"] != 1 for sid in BODY_IDS):
        raise RuntimeError("Torque badan ID 1–18 harus sudah aktif; package ini hanya menangani 19/20")


def write_goal(bus: ServoBus, servo_id: int, position: int) -> None:
    if servo_id not in HEAD_IDS or not 0 <= position <= MAX_POSITION:
        raise ValueError("Penulisan Goal_Position dibatasi ke ID 19/20 dan rentang 0–4095")
    result, error = bus.packet.write4ByteTxRx(bus.port, servo_id, GOAL_POSITION, position)
    if result != COMM_SUCCESS or error:
        raise RuntimeError(
            f"Write Goal_Position ID {servo_id} gagal: "
            f"{bus.packet.getTxRxResult(result)} / {bus.packet.getRxPacketError(error)}"
        )


def write_torque(bus: ServoBus, servo_id: int, enabled: int) -> None:
    if servo_id not in HEAD_IDS or enabled not in (0, 1):
        raise ValueError("Penulisan torque dibatasi ke ID 19/20")
    result, error = bus.packet.write1ByteTxRx(bus.port, servo_id, TORQUE_ENABLE, enabled)
    if result != COMM_SUCCESS or error:
        raise RuntimeError(
            f"Write Torque_Enable ID {servo_id} gagal: "
            f"{bus.packet.getTxRxResult(result)} / {bus.packet.getRxPacketError(error)}"
        )


def report_path() -> Path:
    root = Path("runs/op3_head_pose_hold")
    root.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    path = root / f"{stamp}.json"
    suffix = 1
    while path.exists():
        path = root / f"{stamp}_{suffix:02d}.json"
        suffix += 1
    return path


def save_report(report: dict) -> Path:
    report["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    path = report_path()
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true", help="Read-only inspection")
    mode.add_argument("--dry-run", action="store_true", help="Show current-position hold targets; no writes")
    mode.add_argument("--hold-current-pose", action="store_true", help="Set target=current, then torque-on IDs 19/20")
    parser.add_argument(
        "--confirm-current-camera-pose",
        action="store_true",
        help="Confirm the visible camera angle is the one to hold",
    )
    args = parser.parse_args()
    if args.hold_current_pose and not args.confirm_current_camera_pose:
        parser.error("--hold-current-pose requires --confirm-current-camera-pose")

    with ServoBus() as bus:
        before = bus.inspect_all()
        validate(before)
        head_before = {str(sid): before["servos"][str(sid)] for sid in HEAD_IDS}
        targets = {str(sid): head_before[str(sid)]["present_position"] for sid in HEAD_IDS}
        report = {
            "status": "preflight_only" if args.preflight else "dry_run" if args.dry_run else "starting",
            "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "operation": "hold_present_position_then_enable_head_torque" if args.hold_current_pose else "read_only",
            "touched_servo_ids": list(HEAD_IDS) if args.hold_current_pose else [],
            "position_register_write": "Goal_Position := measured Present_Position before torque-on; after torque-on, resynchronize once to the current reading if it changes by at most 1 count",
            "hold_targets": targets,
            "before": before,
        }

        if args.hold_current_pose:
            try:
                for sid in HEAD_IDS:
                    item = head_before[str(sid)]
                    if item["torque_enabled"] == 1 and abs(item["goal_position"] - item["present_position"]) > 1:
                        raise RuntimeError(
                            f"ID {sid} torque is already on and goal differs from present by more than 1 count; "
                            "refusing to alter a moving target"
                        )
                for sid in HEAD_IDS:
                    if head_before[str(sid)]["torque_enabled"] == 0:
                        write_goal(bus, sid, targets[str(sid)])
                staged = {str(sid): bus.inspect(sid) for sid in HEAD_IDS}
                if any(staged[str(sid)]["goal_position"] != targets[str(sid)] for sid in HEAD_IDS):
                    raise RuntimeError("Goal_Position staging failed; torque was not enabled")
                if any(
                    abs(staged[str(sid)]["present_position"] - targets[str(sid)]) > 1 for sid in HEAD_IDS
                ):
                    raise RuntimeError("Head position changed during staging; torque was not enabled")
                for sid in HEAD_IDS:
                    if staged[str(sid)]["torque_enabled"] == 0:
                        write_torque(bus, sid, 1)
                time.sleep(0.1)
                after_enable = {str(sid): bus.inspect(sid) for sid in HEAD_IDS}
                settled_targets = {}
                for sid in HEAD_IDS:
                    item = after_enable[str(sid)]
                    if abs(item["present_position"] - targets[str(sid)]) > 1:
                        raise RuntimeError(f"ID {sid}: posisi bergeser lebih dari 1 count saat torque-on")
                    settled_targets[str(sid)] = item["present_position"]
                    if item["goal_position"] != item["present_position"]:
                        write_goal(bus, sid, item["present_position"])
                report["hold_targets"] = {sid: settled_targets[sid] for sid in settled_targets}
                report["after_enable_before_resync"] = after_enable
                time.sleep(0.05)
                after = bus.inspect_all()
                validate(after)
                for sid in HEAD_IDS:
                    item = after["servos"][str(sid)]
                    if item["torque_enabled"] != 1:
                        raise RuntimeError(f"ID {sid}: torque-on tidak terverifikasi")
                    if item["goal_position"] != settled_targets[str(sid)]:
                        raise RuntimeError(f"ID {sid}: Goal_Position berubah setelah torque-on")
                    if abs(item["present_position"] - settled_targets[str(sid)]) > 1:
                        raise RuntimeError(f"ID {sid}: posisi aktual bergeser lebih dari 1 count")
                report.update({"status": "completed", "staged": staged, "after": after})
            except Exception as error:
                report.update({"status": "failed", "error": repr(error)})
                try:
                    report["failure_snapshot"] = bus.inspect_all()
                except Exception as snapshot_error:
                    report["failure_snapshot_error"] = repr(snapshot_error)
                save_report(report)
                raise

        path = save_report(report)
        print(json.dumps(report, indent=2))
        print(f"report={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
