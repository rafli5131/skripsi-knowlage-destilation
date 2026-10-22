# OP3 body-servo torque control

Package terpisah ini menyediakan preflight baca-saja dan aktivasi torque selektif. Ia hanya menulis register Torque Enable untuk ID 1–18; ID kepala 19/20 selalu dikecualikan. Ia tidak menulis goal position, tidak mengubah mode servo, dan tidak mengendalikan gait. Sebelum aktivasi, package memeriksa daya bus, respons seluruh ID 1–20, mode posisi, error perangkat keras, serta kesesuaian goal dan posisi saat ini (maksimal selisih 8 count). Status awal harus menunjukkan torque ID 19/20 mati.

Aktifkan environment ROS dan pertahankan seluruh path ROS saat menambahkan package:

```bash
cd /home/humanoid/bre_skripsi
source /opt/ros/jazzy/setup.bash
export PYTHONPATH="$PWD/ros2_packages/op3_servo_torque_control:$PYTHONPATH"
python3 -m op3_servo_torque_control.cli --preflight
python3 -m op3_servo_torque_control.cli --enable-body --confirm-current-pose
```

Opsi aktivasi menganggap operator sudah memastikan robot boleh menahan posisi sendi saat ini dan area aman. Laporan tiap operasi tersimpan di `runs/op3_servo_torque_control/`. Apabila preflight gagal, package tidak mengirim perintah torque.
