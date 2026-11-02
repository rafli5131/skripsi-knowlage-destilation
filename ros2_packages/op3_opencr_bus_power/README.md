# OpenCR bus power

Package ini hanya mengubah register `dynamixel_power` (ID 200, alamat 24). Tidak menulis register servo atau posisi. Jalankan preflight sebelum aktivasi, dan gunakan package torque badan/kepala terpisah sesudah daya bus terverifikasi.

```bash
source /opt/ros/jazzy/setup.bash
export PYTHONPATH="$PWD/ros2_packages/op3_opencr_bus_power:$PWD/ros2_packages/op3_servo_torque_control:$PYTHONPATH"
python3 -m op3_opencr_bus_power.cli
python3 -m op3_opencr_bus_power.cli --enable-power --confirm-area-clear
```

Laporan lokal disimpan di `runs/op3_opencr_bus_power/`.
