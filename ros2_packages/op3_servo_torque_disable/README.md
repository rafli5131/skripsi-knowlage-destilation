# OP3 servo torque disable

Package terpisah ini mematikan torque ID 1–20 sebelum inisialisasi ulang
controller OP3. Ini diperlukan ketika controller menolak mengubah indirect
address EEPROM karena torque masih aktif. Package menggunakan koneksi bus
`op3_servo_torque_control` yang sudah ada; package lama tidak diubah.

Operasi hanya menulis register Torque Enable (alamat 64) dengan nilai 0. Ia
tidak menulis goal position, tidak mengubah mode servo, dan tidak mematikan daya
bus OpenCR. Sebelum menulis, seluruh ID 1–20 harus terdeteksi, modelnya cocok,
mode posisi aktif, tidak ada hardware error, dan goal-position berada maksimal
8 count dari posisi saat ini. Robot harus ditopang operator dan area gerak
kosong.

```bash
cd /home/humanoid/bre_skripsi
export PYTHONPATH="$PWD/ros2_packages/op3_servo_torque_control:$PWD/ros2_packages/op3_servo_torque_disable:$PYTHONPATH"
python3 -m op3_servo_torque_disable.cli --disable-all --confirm-robot-supported
```

Setiap operasi membuat JSON di `runs/op3_servo_torque_disable/`. Periksa hasil
dan status torque sebelum melanjutkan startup manager.
