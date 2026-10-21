# Evaluasi eksploratif kamera OP3

Package baru ini menghitung mAP50–95/mAP50 dan precision, recall, F1 pada frame kamera yang sudah ditinjau manusia. Ia membaca file lokal saja, tanpa ROS, kamera, atau perintah robot. Setiap run harus memakai folder keluaran baru.

```bash
PYTHONPATH=ros2_packages/op3_camera_eval .venv-op3-pytorch/bin/python -m op3_camera_eval \
  --session-dir data/op3_camera_eval/sessions/20261021_idle_01 \
  --output-dir runs/op3_camera_eval/20261021_idle_01_exploratory_reproduction \
  --models kd=models/weights/kd_student_best.pt \
           supervised=runs/supervised/yolo11_tiny_supervised_seed42_retry1/weights/best.pt
```

Evaluasi memakai FP32 CPU, input 640, NMS IoU 0,7, dan mAP dari confidence floor 0,001. Precision/recall/F1 memakai confidence **>0,25**, pencocokan IoU 0,5, dan macro-average tiga kelas. `input_manifest.json` menyimpan hash setiap input. Data sesi dan artefak evaluasi bersifat lokal; hasil satu sesi servo idle ini bukan angka final T27.

Run pertama `20261021_idle_01_exploratory` berhenti sebelum menghitung metrik karena YAML dataset belum memiliki kunci `train`; hasil lengkap pertama ada di `20261021_idle_01_exploratory_retry1`. Kunci `train` pada dataset sementara menunjuk ke gambar yang sama semata-mata karena format validator Ultralytics mensyaratkannya; evaluator hanya menjalankan `split=val` dan tidak melatih model.

Grafik statis dibuat dari `metrics.json` tanpa mengulang inferensi:

```bash
PYTHONPATH=ros2_packages/op3_camera_eval .venv-op3-pytorch/bin/python -m op3_camera_eval.plot \
  --metrics runs/op3_camera_eval/20261021_idle_01_exploratory_retry1/metrics.json \
  --output dokumentasi/2026-10-21/percobaan-01-monitor-rekam-servo-idle/grafik_evaluasi_eksploratif.png
```

Contoh kotak deteksi pada tiga JPEG tersimpan (inferensi offline, bukan tangkapan layar live):

```bash
PYTHONPATH=ros2_packages/op3_camera_eval .venv-op3-pytorch/bin/python -m op3_camera_eval.sample_overlay \
  --session-dir data/op3_camera_eval/sessions/20261021_idle_01 \
  --model models/weights/kd_student_best.pt \
  --output dokumentasi/2026-10-21/percobaan-01-monitor-rekam-servo-idle/contoh_deteksi_kd_offline.png
```
