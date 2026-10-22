"""Enable torque on OP3 body IDs 1-18 while keeping head IDs 19/20 off."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler

DEVICE = "/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FT7W960L-if00-port0"
BAUD = 2_000_000
CONTROLLER_ID = 200
BODY_IDS = tuple(range(1, 19))
HEAD_IDS = (19, 20)


class ServoBus:
    def __init__(self) -> None:
        self.port = PortHandler(DEVICE)
        self.packet = PacketHandler(2.0)

    def __enter__(self) -> "ServoBus":
        if not self.port.openPort():
            raise RuntimeError(f"Tidak dapat membuka U2D2 {DEVICE}")
        if not self.port.setBaudRate(BAUD):
            self.port.closePort()
            raise RuntimeError(f"Tidak dapat menyetel baud rate {BAUD}")
        return self

    def __exit__(self, *_args: object) -> None:
        self.port.closePort()

    def read(self, servo_id: int, address: int, width: int = 1) -> int:
        method = {1: self.packet.read1ByteTxRx, 4: self.packet.read4ByteTxRx}[width]
        value, result, error = method(self.port, servo_id, address)
        if result != COMM_SUCCESS or error:
            raise RuntimeError(
                f"Baca ID {servo_id}, alamat {address} gagal: "
                f"{self.packet.getTxRxResult(result)} / "
                f"{self.packet.getRxPacketError(error)}"
            )
        return value

    def ping(self, servo_id: int) -> int:
        model, result, error = self.packet.ping(self.port, servo_id)
        if result != COMM_SUCCESS or error:
            raise RuntimeError(
                f"Ping ID {servo_id} gagal: {self.packet.getTxRxResult(result)} / "
                f"{self.packet.getRxPacketError(error)}"
            )
        return model

    def write_torque(self, servo_id: int, enabled: int) -> None:
        if servo_id not in BODY_IDS:
            raise ValueError("Penulisan torque dibatasi ke ID 1-18")
        result, error = self.packet.write1ByteTxRx(self.port, servo_id, 64, enabled)
        if result != COMM_SUCCESS or error:
            raise RuntimeError(
                f"Write torque ID {servo_id} gagal: "
                f"{self.packet.getTxRxResult(result)} / "
                f"{self.packet.getRxPacketError(error)}"
            )

    def inspect(self, servo_id: int) -> dict:
        model = self.ping(servo_id)
        return {
            "id": servo_id,
            "model": model,
            "torque_enabled": self.read(servo_id, 64),
            "operating_mode": self.read(servo_id, 11),
            "hardware_error": self.read(servo_id, 70),
            "present_position": self.read(servo_id, 132, 4),
            "goal_position": self.read(servo_id, 116, 4),
        }

    def inspect_all(self) -> dict:
        power = self.read(CONTROLLER_ID, 24)
        return {
            "controller_dynamixel_power": power,
            "servos": {str(sid): self.inspect(sid) for sid in (*BODY_IDS, *HEAD_IDS)},
        }


def validate(snapshot: dict) -> None:
    if snapshot["controller_dynamixel_power"] != 1:
        raise RuntimeError("Daya bus Dynamixel OpenCR tidak aktif")
    servos = snapshot["servos"]
    for sid in (*BODY_IDS, *HEAD_IDS):
        item = servos[str(sid)]
        if item["operating_mode"] != 3:
            raise RuntimeError(f"ID {sid}: bukan mode posisi (mode 3)")
        if item["hardware_error"] != 0:
            raise RuntimeError(f"ID {sid}: hardware_error={item['hardware_error']}")
        if abs(item["goal_position"] - item["present_position"]) > 8:
            raise RuntimeError(
                f"ID {sid}: goal dan posisi aktual berbeda lebih dari 8 count; "
                "tidak mengaktifkan torque untuk mencegah lompatan posisi"
            )
    for sid in HEAD_IDS:
        if servos[str(sid)]["torque_enabled"] != 0:
            raise RuntimeError(f"ID kepala {sid} sudah torque-on; tidak diubah")


def write_report(data: dict) -> Path:
    root = Path("runs/op3_servo_torque_control")
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preflight or enable torque on OP3 servo IDs 1-18; IDs 19/20 are excluded."
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--preflight", action="store_true", help="Read-only inspection")
    action.add_argument("--enable-body", action="store_true", help="Enable torque on IDs 1-18")
    parser.add_argument(
        "--confirm-current-pose",
        action="store_true",
        help="Confirm the robot is clear and may hold its current joint positions",
    )
    args = parser.parse_args()
    if args.enable_body and not args.confirm_current_pose:
        parser.error("--enable-body requires --confirm-current-pose")

    with ServoBus() as bus:
        before = bus.inspect_all()
        validate(before)
        report = {"started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "before": before}
        if args.enable_body:
            enabled = []
            for servo_id in BODY_IDS:
                if before["servos"][str(servo_id)]["torque_enabled"] == 0:
                    bus.write_torque(servo_id, 1)
                    if bus.read(servo_id, 64) != 1:
                        raise RuntimeError(f"ID {servo_id}: torque tidak terverifikasi setelah write")
                    enabled.append(servo_id)
            after = bus.inspect_all()
            if after["controller_dynamixel_power"] != 1:
                raise RuntimeError("Daya bus berubah selama aktivasi")
            if any(after["servos"][str(sid)]["torque_enabled"] != 1 for sid in BODY_IDS):
                raise RuntimeError("Tidak semua torque ID 1-18 terverifikasi aktif")
            if any(after["servos"][str(sid)]["torque_enabled"] != 0 for sid in HEAD_IDS):
                raise RuntimeError("Pemeriksaan akhir gagal: torque kepala 19/20 harus tetap mati")
            report.update({"enabled_ids": enabled, "after": after})
        report["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        report_path = write_report(report)
        print(json.dumps(report, indent=2))
        print(f"report={report_path}")


if __name__ == "__main__":
    main()
