"""Konversi posisi XM430-W350 sesuai deskripsi device ROBOTIS yang terpasang."""

import math


def rad_to_count(radian: float) -> int:
    if not math.isfinite(radian):
        raise ValueError("Posisi kepala tidak berhingga")
    # Konversi controller: [2048,4095] pada [0,pi], [0,2048] pada [-pi,0].
    count = round(2048 + radian * (2047 if radian >= 0 else 2048) / 3.14159265)
    if not 0 <= count <= 4095:
        raise ValueError("Posisi kepala di luar rentang satu putaran")
    return count
