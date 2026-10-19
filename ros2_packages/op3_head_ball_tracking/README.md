# OP3 ball tracking dengan servo kepala 19/20

Paket baru ini memakai gambar ROS `/thesis/image_raw` dan model `op3_default` dari registry repo. Hanya deteksi kelas `ball` dengan confidence >= 0,5 dan track ID stabil tiga frame yang boleh menghasilkan target. Target diperbarui paling cepat setiap 200 ms, dengan deadband 0,08 lebar/tinggi gambar, langkah sudut maksimal 0,025 rad per pembaruan, dan perjalanan maksimal ±12° dari posisi awal kepala. Mode awal adalah simulasi tanpa gerak. Tampilan OpenCV menggunakan X11, tanpa web dan tanpa menyimpan gambar/video kamera. Metadata percobaan tersimpan dalam `runs/op3_head_ball_tracking/`.

Paket ini memakai `op3_live_monitor` melalui import. Kode paket lama tidak diubah. Untuk kendali perangkat keras, U2D2 diakses langsung pada port dan baud dari `op3_manager/config/OP3.robot`; karena itu `op3_manager` harus berhenti. Penulisan hanya diizinkan untuk ID 19 (`head_pan`) dan 20 (`head_tilt`). Paket tidak menghidupkan daya bus OpenCR dan tidak memberi perintah gait atau menulis ID 1–18. Preflight memerlukan daya bus aktif, kedua servo dapat dibaca, mode posisi 3, tanpa hardware error, tegangan 10–15 V, suhu <65°C, dan posisi awal dalam batas kepala. Saat selesai, paket mengembalikan kedua sendi ke posisi awal dan mengembalikan status torque yang diubahnya.

Jalankan dari root repo setelah ROS Jazzy dan venv diaktifkan. Paket baru dapat dijalankan langsung dengan `PYTHONPATH` berikut sebelum dipasang melalui `colcon`:

```bash
export PYTHONPATH="$PWD/ros2_packages/op3_live_monitor:$PWD/ros2_packages/op3_head_ball_tracking:$PYTHONPATH"
export YOLO_CONFIG_DIR=/tmp/Ultralytics
python -m op3_head_ball_tracking.bus --probe-controller
python -m op3_head_ball_tracking.tracking --duration 25
python -m op3_head_ball_tracking.tracking --duration 30 --enable-motion
```

Perintah terakhir hanya dipakai sesudah `--probe-controller` menampilkan `dynamixel_power: 1` serta ping ID 19/20 berhasil dan area gerak kepala sudah bebas. Jendela X11 dapat ditutup dengan `q` atau Esc. `--no-preview` tersedia untuk pengujian tanpa tampilan.

Jika memasang paket dengan `colcon`, jalankan `python -m colcon build ...` dari venv proyek. Perintah `/usr/bin/colcon` membuat entry point dengan Python sistem, yang tidak memiliki `ultralytics`; entry point hasil build venv dapat dijalankan lewat `ros2 run op3_head_ball_tracking op3-head-ball-tracking` setelah `setup.bash` install diaktifkan.

Referensi pemetaan ID dan batas kepala: [ROBOTIS OP3 e-Manual](https://emanual.robotis.com/docs/en/platform/op3/tutorials/), `op3_manager/config/OP3.robot`, dan `op3_head_control_module` pada workspace ROS lokal.
