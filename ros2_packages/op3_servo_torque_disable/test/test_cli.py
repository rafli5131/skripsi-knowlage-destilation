import unittest

from op3_servo_torque_disable.cli import ALL_IDS, disable_all_torque, validate_preflight


def snapshot():
    return {
        "controller_dynamixel_power": 1,
        "servos": {
            str(sid): {
                "id": sid,
                "model": 1020,
                "torque_enabled": 1,
                "operating_mode": 3,
                "hardware_error": 0,
                "present_position": 2048,
                "goal_position": 2048,
            }
            for sid in ALL_IDS
        },
    }


class FakePacket:
    def __init__(self, bus):
        self.bus = bus

    def write1ByteTxRx(self, _port, servo_id, address, value):
        self.bus.writes.append((servo_id, address, value))
        self.bus.state["servos"][str(servo_id)]["torque_enabled"] = value
        return 0, 0

    @staticmethod
    def getTxRxResult(_result):
        return "ok"

    @staticmethod
    def getRxPacketError(_error):
        return "ok"


class FakeBus:
    def __init__(self):
        self.state = snapshot()
        self.writes = []
        self.packet = FakePacket(self)
        self.port = object()

    def write_torque(self, servo_id, value):
        self.writes.append((servo_id, 64, value))
        self.state["servos"][str(servo_id)]["torque_enabled"] = value

    def read(self, servo_id, _address):
        return self.state["servos"][str(servo_id)]["torque_enabled"]


class TorqueDisableTests(unittest.TestCase):
    def test_preflight_rejects_position_mismatch(self):
        state = snapshot()
        state["servos"]["20"]["goal_position"] += 9
        with self.assertRaises(RuntimeError):
            validate_preflight(state)

    def test_disables_all_ids_only_at_torque_register(self):
        bus = FakeBus()
        changed = disable_all_torque(bus, bus.state)
        self.assertEqual(changed, list(ALL_IDS))
        self.assertEqual(bus.writes, [(sid, 64, 0) for sid in ALL_IDS])
        self.assertTrue(all(item["torque_enabled"] == 0 for item in bus.state["servos"].values()))

    def test_failed_preflight_sends_no_writes(self):
        bus = FakeBus()
        bus.state["controller_dynamixel_power"] = 0
        with self.assertRaises(RuntimeError):
            disable_all_torque(bus, bus.state)
        self.assertEqual(bus.writes, [])


if __name__ == "__main__":
    unittest.main()
