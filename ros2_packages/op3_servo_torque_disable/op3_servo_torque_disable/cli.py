"""Disable OP3 servo torque without changing position goals or servo modes."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from dynamixel_sdk import COMM_SUCCESS
from op3_servo_torque_control.cli import BODY_IDS, HEAD_IDS, ServoBus

ALL_IDS = (*BODY_IDS, *HEAD_IDS)
TORQUE_ENABLE_ADDRESS = 64
MAX_GOAL_POSITION_DELTA = 8


def validate_preflight(snapshot: dict) -> None:
    """Fail closed unless every servo is readable, healthy, and at its goal."""
    if snapshot.get("controller_dynamixel_power") != 1:
        raise RuntimeError("Daya bus Dynamixel OpenCR tidak aktif")

    servos = snapshot.get("servos", {})
    missing = [sid for sid in ALL_IDS if str(sid) not in servos]
    if missing:
        raise RuntimeError(f"Status servo tidak lengkap; ID tidak terbaca: {missing}")

    for servo_id in ALL_IDS:
        item = servos[str(servo_id)]
        if item["model"] != 1020:
            raise RuntimeError(f"ID {servo_id}: model servo tidak dikenal ({item['model']})")
        if item["operating_mode"] != 3:
            raise RuntimeError(f"ID {servo_id}: bukan mode posisi (mode 3)")
        if item["hardware_error"] != 0:
            raise RuntimeError(f"ID {servo_id}: hardware_error={item['hardware_error']}")
        if item["torque_enabled"] not in (0, 1):
            raise RuntimeError(f"ID {servo_id}: nilai torque tidak valid")
        delta = abs(item["goal_position"] - item["present_position"])
        if delta > MAX_GOAL_POSITION_DELTA:
            raise RuntimeError(
                f"ID {servo_id}: goal dan posisi aktual berbeda {delta} count; "
                "tidak mengubah torque"
            )


def _write_torque_off(bus: ServoBus, servo_id: int) -> None:
    # Reuse the existing body's guarded helper; head IDs remain excluded there.
    if servo_id in BODY_IDS:
        bus.write_torque(servo_id, 0)
    else:
        # This dedicated shutdown package only writes 0 to the torque register
        # for the two head IDs; it never writes a goal position or mode.
        result, error = bus.packet.write1ByteTxRx(
            bus.port, servo_id, TORQUE_ENABLE_ADDRESS, 0
        )
        if result != COMM_SUCCESS or error:
            raise RuntimeError(
                f"Write torque-off ID {servo_id} gagal: "
                f"{bus.packet.getTxRxResult(result)} / "
                f"{bus.packet.getRxPacketError(error)}"
            )

    actual = bus.read(servo_id, TORQUE_ENABLE_ADDRESS)
    if actual != 0:
        raise RuntimeError(f"ID {servo_id}: torque-off tidak terverifikasi (nilai={actual})")


def disable_all_torque(bus: ServoBus, before: dict) -> list[int]:
    """Turn torque off on IDs 1–20, verifying each write immediately."""
    validate_preflight(before)
    changed = []
    for servo_id in ALL_IDS:
        if before["servos"][str(servo_id)]["torque_enabled"] == 1:
            _write_torque_off(bus, servo_id)
            changed.append(servo_id)
    return changed


def _write_report(report: dict) -> Path:
    root = Path("runs/op3_servo_torque_disable")
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Disable torque on OP3 IDs 1–20 after verifying supported robot state."
    )
    parser.add_argument(
        "--disable-all", action="store_true", required=True,
        help="Disable torque on IDs 1–20; does not move joints or change operating modes",
    )
    parser.add_argument(
        "--confirm-robot-supported", action="store_true", required=True,
        help="Confirm an operator is physically supporting the robot and the area is clear",
    )
    args = parser.parse_args()
    if not args.disable_all or not args.confirm_robot_supported:
        parser.error("Torque-off requires --disable-all and --confirm-robot-supported")

    report = {
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "operation": "disable_torque_ids_1_to_20",
        "operator_confirmed_robot_supported": True,
        "position_or_mode_writes": 0,
    }
    failure = None
    try:
        with ServoBus() as bus:
            report["before"] = bus.inspect_all()
            validate_preflight(report["before"])
            report["changed_ids"] = disable_all_torque(bus, report["before"])
            report["after"] = bus.inspect_all()
            validate_preflight(report["after"])
            remaining = [
                sid for sid in ALL_IDS
                if report["after"]["servos"][str(sid)]["torque_enabled"] != 0
            ]
            if remaining:
                raise RuntimeError(f"Torque masih aktif pada ID: {remaining}")
    except Exception as exc:  # Preserve partial evidence if a bus write fails.
        failure = exc
        report["error"] = f"{type(exc).__name__}: {exc}"
    report["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    path = _write_report(report)
    print(json.dumps(report, indent=2))
    print(f"report={path}")
    if failure is not None:
        raise SystemExit(2) from failure


if __name__ == "__main__":
    main()
