# Confusion matrix offline OP3

Package baru ini memakai fungsi bersama `op3_camera_eval` dan `op3_multi_session_eval`, tanpa mengubah package tersebut. Ia membaca label yang sudah ditinjau dan prediksi T38 yang tersimpan; tidak mengaktifkan kamera, ROS, atau motor.

```bash
PYTHONPATH=ros2_packages/op3_camera_eval:ros2_packages/op3_multi_session_eval:ros2_packages/op3_confusion_matrix \
  .venv-op3-pytorch/bin/python -m op3_confusion_matrix --output /tmp/confusion_matrix_op3_baru
```

Lokasi keluaran harus belum ada. Perhitungan memverifikasi hash input, inventaris frame, dan kecocokan TP/FP/FN T38 sebelum menerbitkan matriks. Prediksi dan label mentah bersifat lokal, sehingga tidak semua input tersedia pada checkout GitHub publik. Pencocokan memprioritaskan kelas yang sama menurut T38, kemudian memasangkan label dan prediksi sisa yang berbeda kelas dengan IoU tertinggi ≥0,5. Metode ini menjaga TP/FP/FN T38; ini **bukan** keluaran confusion matrix bawaan Ultralytics yang menggunakan aturan asosiasi berbeda.
