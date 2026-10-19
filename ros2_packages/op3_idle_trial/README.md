# OP3 servo-idle trial

Paket baru ini memakai `CameraNode`, validasi checkpoint, dan renderer dari `op3_live_monitor` tanpa mengubah kode paket tersebut. Hanya metadata `summary.json`, `frames.csv`, dan `detections.csv` yang ditulis ke folder run unik; gambar/video tidak disimpan. Jendela X11 menampilkan deteksi selama sesi. Robot tidak dikendalikan. Label `servo_idle` berasal dari verifikasi operator, bukan telemetri.

Jalankan dari root repo setelah publisher `/thesis/image_raw` aktif dan `$DISPLAY` tersedia:

```bash
source /opt/ros/jazzy/setup.bash
source /home/humanoid/ros2_jazzy/install/setup.bash
source .venv-op3-pytorch/bin/activate
export PYTHONPATH="$PWD/ros2_packages/op3_live_monitor:$PWD/ros2_packages/op3_idle_trial:$PYTHONPATH"
python -m op3_idle_trial.trial --duration 60 --condition servo_idle
```

Sesi baru selalu membuat direktori unik di `runs/op3_idle_trial/`. `--no-preview` tersedia untuk terminal tanpa X11. Menekan `q`/Esc menghentikan sesi lebih awal. Confidence bukan akurasi live; evaluasi akurasi memerlukan ground truth.
