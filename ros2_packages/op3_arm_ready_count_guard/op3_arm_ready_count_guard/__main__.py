"""Gunakan prosedur bahu bersama dengan batas dua count dari posisi awal."""

import argparse
import math
import sys

from op3_t43_walk_ready.__main__ import Monitor
from op3_walk_video_guard.counts import rad_to_count
import op3_t43_arm_ready.__main__ as arm_ready


def monitor_for_anchor(anchor):
    class CountMonitor(Monitor):
        def callback(self, msg):
            previous_violation = self.violation
            super().callback(msg)
            state = dict(zip(msg.name, msg.position))
            try:
                if not all(name in state and math.isfinite(state[name]) for name in anchor):
                    raise ValueError('Telemetry kepala tidak lengkap')
                delta = max(abs(rad_to_count(state[name]) - count) for name, count in anchor.items())
                self.violation = previous_violation or delta > 2
            except (ValueError, KeyError):
                self.violation = True
    return CountMonitor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pan-count', type=int, required=True)
    parser.add_argument('--tilt-count', type=int, required=True)
    args = parser.parse_args()
    if not 0 <= args.pan_count <= 4095 or not 0 <= args.tilt_count <= 4095:
        parser.error('Posisi acuan harus dalam rentang encoder')
    anchor = {'head_pan': args.pan_count, 'head_tilt': args.tilt_count}
    print(f'Acuan kepala {anchor}, batas 2 count; tidak mengirim start gait', flush=True)
    arm_ready.Monitor = monitor_for_anchor(anchor)
    return arm_ready.main()


if __name__ == '__main__':
    raise SystemExit(main())
