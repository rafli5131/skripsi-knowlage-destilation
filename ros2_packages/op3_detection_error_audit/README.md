# Audit kesalahan deteksi OP3

Package baru ini membaca log prediksi `op3_multi_session_eval` serta label manusia dengan memakai `read_labels`, `iou_xyxy`, dan `sha256` dari package `op3_camera_eval` sebagai shared code. Ia tidak menjalankan model, kamera, ROS, tracking, atau motor. Package yang sudah ada tidak diubah.

Dari root repository:

```bash
source .venv-op3-pytorch/bin/activate
PYTHONPATH="$PWD/ros2_packages/op3_camera_eval:$PWD/ros2_packages/op3_detection_error_audit" \
python -m op3_detection_error_audit \
  --run-dir runs/op3_multi_session_eval/20261021_primary260_partial50_v1 \
  --session-root data/op3_camera_eval/sessions \
  --output-dir runs/op3_detection_error_audit/NAMA_RUN_BARU
```

Audit memeriksa hash gambar dan label terhadap manifest evaluasi, lalu mengelompokkan setiap kotak ground truth sebagai cocok, prediksi kelas sama dengan kotak meleset, kelas keliru, atau tanpa prediksi yang sesuai. Prediksi yang tidak cocok juga dikelompokkan. `cases.csv` memuat setiap objek pada 80 frame prioritas; `geometry_recheck.csv` hanya memuat IoU kelas sama pada rentang 0,4–0,6 sebagai kandidat pemeriksaan visual, bukan keputusan otomatis untuk mengubah label. Empat lembar gambar memperlihatkan semua 40 frame per sesi untuk kedua model. Hijau ialah label manusia; merah ialah prediksi pada confidence >0,25. Semua output lokal dan label sumber tidak diubah.
