"""Aktifkan hanya daya bus Dynamixel OpenCR setelah pemeriksaan baca-saja."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from dynamixel_sdk import COMM_SUCCESS
from op3_servo_torque_control.cli import ServoBus

CONTROLLER_ID = 200
POWER_ADDRESS = 24
VOLTAGE_ADDRESS = 31
REPORT_DIR = Path("runs/op3_opencr_bus_power")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enable-power", action="store_true")
    parser.add_argument("--confirm-area-clear", action="store_true")
    args = parser.parse_args()
    if args.enable_power and not args.confirm_area_clear:
        parser.error("--enable-power memerlukan --confirm-area-clear")

    report = {"started_at_utc": datetime.now(timezone.utc).isoformat(), "operation": "power_on" if args.enable_power else "preflight"}
    try:
        with ServoBus() as bus:
            report["controller_model"] = bus.ping(CONTROLLER_ID)
            report["power_before"] = bus.read(CONTROLLER_ID, POWER_ADDRESS)
            report["input_voltage_v"] = bus.read(CONTROLLER_ID, VOLTAGE_ADDRESS) / 10
            if not 10 <= report["input_voltage_v"] <= 15:
                raise RuntimeError("Tegangan OpenCR di luar 10–15 V")
            if report["power_before"] not in (0, 1):
                raise RuntimeError("Status daya bus OpenCR tidak dikenal")
            if args.enable_power and report["power_before"] == 0:
                result, error = bus.packet.write1ByteTxRx(bus.port, CONTROLLER_ID, POWER_ADDRESS, 1)
                if result != COMM_SUCCESS or error:
                    raise RuntimeError(f"Gagal mengaktifkan daya bus: {bus.packet.getTxRxResult(result)} / {bus.packet.getRxPacketError(error)}")
            report["power_after"] = bus.read(CONTROLLER_ID, POWER_ADDRESS)
            if args.enable_power and report["power_after"] != 1:
                raise RuntimeError("Daya bus belum aktif sesudah perintah")
        report["status"] = "completed"
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = str(exc)
        raise
    finally:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = REPORT_DIR / f"{stamp}.json"
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        print(f"report={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
