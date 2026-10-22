# OP3 head pose hold

Package baru ini menggunakan `op3_servo_torque_control` sebagai shared package untuk koneksi dan pembacaan servo. Package lama tidak diubah. Operasi tulis package ini dibatasi ke ID 19/20: saat torque mati, ia menyalin posisi aktual ke `Goal_Position`, memverifikasi target, lalu menyalakan torque agar kepala menahan arah kamera saat ini. Jika pembacaan posisi bergeser paling banyak 1 count setelah torque-on, target diselaraskan sekali lagi dengan posisi terkini agar servo tidak mengejar nilai lama. Ia tidak mengirim pose init, gait, atau perintah untuk servo ID 1–18.

Jalankan dari root `bre_skripsi`:

```bash
source /opt/ros/jazzy/setup.bash
export PYTHONPATH="$PWD/ros2_packages/op3_head_pose_hold:$PWD/ros2_packages/op3_servo_torque_control:$PYTHONPATH"
python3 -m op3_head_pose_hold.cli --preflight
python3 -m op3_head_pose_hold.cli --dry-run
python3 -m op3_head_pose_hold.cli --hold-current-pose --confirm-current-camera-pose
```

Preflight dan dry-run hanya membaca hardware. Aktivasi mensyaratkan persetujuan operator pada saat pemanggilan. Laporan JSON disimpan di `runs/op3_head_pose_hold/`; bila target/posisi bergeser lebih dari 1 count, operasi berhenti dengan error dan menyimpan laporan jika tahap tulis sudah dimulai.

Untuk menyalakan controller OP3 tanpa pose awal otomatis, gunakan launch manager existing dengan `auto_start_init_pose:=false`. Jangan jalankan init-pose setelah posisi kepala ditahan.
