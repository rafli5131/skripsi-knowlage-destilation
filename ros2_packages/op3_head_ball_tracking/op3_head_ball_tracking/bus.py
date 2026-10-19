"""Read-only U2D2 preflight for OP3 head servo IDs 19 and 20."""

from __future__ import annotations

import argparse
import math
import time
import json
from pathlib import Path

from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler

DEVICE = Path('/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FT7W960L-if00-port0')
BAUD = 2_000_000
HEAD = {19: 'head_pan', 20: 'head_tilt'}


class HeadBus:
    def __init__(self, device: Path = DEVICE) -> None:
        self.device = device
        self.port = PortHandler(str(device))
        self.packet = PacketHandler(2.0)
        self.open = False
        self.write_count = 0

    def __enter__(self):
        if not self.device.exists():
            raise FileNotFoundError(self.device)
        if not self.port.openPort():
            raise RuntimeError(f'Cannot open {self.device}')
        self.open = True
        if not self.port.setBaudRate(BAUD):
            self.close()
            raise RuntimeError(f'Cannot set {BAUD} baud')
        return self

    def close(self) -> None:
        if self.open:
            self.port.closePort()
            self.open = False

    def __exit__(self, *_exc) -> None:
        self.close()

    def read(self, servo_id: int, address: int, width: int) -> int:
        if servo_id not in HEAD:
            raise ValueError('Only head servo IDs 19/20 are permitted')
        method = {1: self.packet.read1ByteTxRx, 2: self.packet.read2ByteTxRx,
                  4: self.packet.read4ByteTxRx}[width]
        value, result, error = method(self.port, servo_id, address)
        if result != COMM_SUCCESS or error:
            raise RuntimeError(f'ID {servo_id} read {address}: {self.packet.getTxRxResult(result)} / {self.packet.getRxPacketError(error)}')
        return value

    def ping(self, servo_id: int) -> int:
        if servo_id not in HEAD:
            raise ValueError('Only head servo IDs 19/20 are permitted')
        model, result, error = self.packet.ping(self.port, servo_id)
        if result != COMM_SUCCESS or error:
            raise RuntimeError(f'ID {servo_id} ping: {self.packet.getTxRxResult(result)} / {self.packet.getRxPacketError(error)}')
        return model

    def inspect(self) -> dict:
        result = {}
        for servo_id, name in HEAD.items():
            try:
                result[name] = self.inspect_one(servo_id)
            except Exception as error:
                result[name] = {"id": servo_id, "error": str(error)}
        return result

    def inspect_one(self, servo_id: int) -> dict:
        model = self.ping(servo_id)
        operating_mode = self.read(servo_id, 11, 1)
        torque = self.read(servo_id, 64, 1)
        hardware_error = self.read(servo_id, 70, 1)
        goal = self.read(servo_id, 116, 4)
        present = self.read(servo_id, 132, 4)
        voltage = self.read(servo_id, 144, 2)
        temperature = self.read(servo_id, 146, 1)
        return {'id': servo_id, 'model': model, 'operating_mode': operating_mode,
                'torque_enabled': torque, 'hardware_error': hardware_error,
                'goal_raw': goal, 'present_raw': present,
                'voltage_v': voltage / 10, 'temperature_c': temperature}

    def controller_power(self) -> int:
        value, tx, error = self.packet.read1ByteTxRx(self.port, 200, 24)
        if tx != COMM_SUCCESS or error:
            raise RuntimeError('OpenCR dynamixel_power read failed')
        return value

    def write(self, servo_id: int, address: int, width: int, value: int) -> None:
        if servo_id not in HEAD:
            raise ValueError('Writes are restricted to servo IDs 19/20')
        method = {1: self.packet.write1ByteTxRx, 4: self.packet.write4ByteTxRx}[width]
        tx, error = method(self.port, servo_id, address, value)
        if tx != COMM_SUCCESS or error:
            raise RuntimeError(f'ID {servo_id} write {address}: {self.packet.getTxRxResult(tx)} / {self.packet.getRxPacketError(error)}')
        self.write_count += 1


RAW_PER_RAD = 2048 / math.pi
HARD_LIMITS = {19: (-math.radians(80), math.radians(80)),
               20: (-math.radians(70), math.radians(25))}


def raw_to_rad(raw: int) -> float:
    return (raw - 2048) / RAW_PER_RAD


def rad_to_raw(rad: float) -> int:
    return round(2048 + rad * RAW_PER_RAD)


class HeadActuator:
    """Bounded head-only writes; never changes OpenCR bus power or IDs 1-18."""

    def __init__(self, bus: HeadBus, max_excursion_rad: float = math.radians(12)) -> None:
        self.bus = bus
        self.max_excursion_rad = max_excursion_rad
        self.initial_raw: dict[int, int] = {}
        self.initial_torque: dict[int, int] = {}
        self.goal_raw: dict[int, int] = {}
        self.prepared = False
        self.enabled_by_us: set[int] = set()
        self.restore_report: dict = {}

    def prepare(self) -> dict:
        if self.bus.controller_power() != 1:
            raise RuntimeError('OpenCR dynamixel_power=0; bus servo is off. No writes sent.')
        info = self.bus.inspect()
        if any('error' in item for item in info.values()):
            raise RuntimeError(f'Head servo preflight failed: {info}')
        for servo_id, name in HEAD.items():
            item = info[name]
            rad = raw_to_rad(item['present_raw'])
            lower, upper = HARD_LIMITS[servo_id]
            if item['operating_mode'] != 3 or item['hardware_error'] != 0:
                raise RuntimeError(f'{name}: mode/error unsafe: {item}')
            if not 0 <= item['present_raw'] <= 4095 or not lower < rad < upper:
                raise RuntimeError(f'{name}: position outside guarded range: {item}')
            if not 10.0 <= item['voltage_v'] <= 15.0 or item['temperature_c'] >= 65:
                raise RuntimeError(f'{name}: voltage/temperature unsafe: {item}')
            self.initial_raw[servo_id] = item['present_raw']
            self.initial_torque[servo_id] = item['torque_enabled']
            self.goal_raw[servo_id] = item['present_raw']
        # Avoid a jump if head torque was off: seed its goal at measured position first.
        try:
            for servo_id in HEAD:
                if self.initial_torque[servo_id] == 0:
                    self.bus.write(servo_id, 116, 4, self.initial_raw[servo_id])
                    self.bus.write(servo_id, 64, 1, 1)
                    self.enabled_by_us.add(servo_id)
        except Exception:
            for servo_id in self.enabled_by_us:
                try:
                    self.bus.write(servo_id, 64, 1, 0)
                except Exception:
                    pass
            raise
        self.prepared = True
        return info

    def command(self, pan_rad: float, tilt_rad: float) -> dict:
        if not self.prepared:
            raise RuntimeError('Head actuator not prepared')
        result = {}
        for servo_id, requested in ((19, pan_rad), (20, tilt_rad)):
            lower, upper = HARD_LIMITS[servo_id]
            initial = raw_to_rad(self.initial_raw[servo_id])
            bounded = max(lower, min(upper, initial + max(-self.max_excursion_rad,
                                                      min(self.max_excursion_rad, requested - initial))))
            target = rad_to_raw(bounded)
            step = max(-16, min(16, target - self.goal_raw[servo_id]))
            next_raw = self.goal_raw[servo_id] + step
            if next_raw != self.goal_raw[servo_id]:
                self.bus.write(servo_id, 116, 4, next_raw)
                self.goal_raw[servo_id] = next_raw
            result[HEAD[servo_id]] = raw_to_rad(self.goal_raw[servo_id])
        return result

    def restore(self) -> None:
        if not self.prepared:
            return
        try:
            # Return only head joints to their starting positions in bounded steps.
            for _ in range(260):
                if all(abs(self.goal_raw[i] - self.initial_raw[i]) <= 2 for i in HEAD):
                    break
                self.command(raw_to_rad(self.initial_raw[19]), raw_to_rad(self.initial_raw[20]))
                time.sleep(0.08)
            time.sleep(0.25)
            self.restore_report['before_torque_off'] = {
                HEAD[i]: {'goal_raw': self.bus.read(i, 116, 4),
                          'present_raw': self.bus.read(i, 132, 4)} for i in HEAD}
        finally:
            try:
                for servo_id in self.enabled_by_us:
                    self.bus.write(servo_id, 64, 1, 0)
                self.restore_report['after_torque_off'] = {
                    HEAD[i]: {'goal_raw': self.bus.read(i, 116, 4),
                              'present_raw': self.bus.read(i, 132, 4),
                              'torque_enabled': self.bus.read(i, 64, 1)} for i in HEAD}
            finally:
                self.prepared = False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', type=Path, default=DEVICE)
    parser.add_argument('--scan-baud', action='store_true', help='Ping IDs 19/20 at common baud rates; read-only')
    parser.add_argument('--probe-controller', action='store_true', help='Ping OpenCR ID 200 at configured baud; read-only')
    args = parser.parse_args()
    with HeadBus(args.device) as bus:
        if args.probe_controller:
            model, tx, err = bus.packet.ping(bus.port, 200)
            result = {'id': 200, 'model': model, 'tx_result': bus.packet.getTxRxResult(tx),
                      'device_error': bus.packet.getRxPacketError(err)}
            if tx == COMM_SUCCESS and not err:
                power, power_tx, power_err = bus.packet.read1ByteTxRx(bus.port, 200, 24)
                voltage, voltage_tx, voltage_err = bus.packet.read1ByteTxRx(bus.port, 200, 31)
                result['dynamixel_power'] = power if power_tx == COMM_SUCCESS and not power_err else None
                result['input_voltage_v'] = voltage / 10 if voltage_tx == COMM_SUCCESS and not voltage_err else None
                for servo_id in (1, 18, 19, 20):
                    servo_model, servo_tx, servo_err = bus.packet.ping(bus.port, servo_id)
                    result[f'ping_{servo_id}'] = servo_model if servo_tx == COMM_SUCCESS and not servo_err else bus.packet.getTxRxResult(servo_tx)
        elif args.scan_baud:
            result = {}
            for baud in (57600, 115200, 1000000, 2000000, 3000000, 4000000):
                if not bus.port.setBaudRate(baud):
                    result[str(baud)] = {'port_error': 'setBaudRate failed'}
                    continue
                result[str(baud)] = {}
                for servo_id in HEAD:
                    try:
                        result[str(baud)][str(servo_id)] = bus.ping(servo_id)
                    except Exception as error:
                        result[str(baud)][str(servo_id)] = str(error)
        else:
            result = bus.inspect()
    print(json.dumps(result, indent=2))
    if args.probe_controller:
        if result["tx_result"] != "[TxRxResult] Communication success!":
            raise SystemExit(1)
        return
    if not args.scan_baud and any("error" in item for item in result.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
