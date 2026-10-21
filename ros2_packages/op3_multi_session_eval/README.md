# Evaluasi deteksi OP3 multi-sesi

Package ini menggabungkan sesi kamera OP3 yang sudah ditinjau manusia. Ia memakai `read_labels`, `iou_xyxy`, kelas, dan fungsi hash dari package `op3_camera_eval` sebagai shared code; package lama tidak diubah. Evaluasi hanya membaca JPEG dan label lokal, tanpa ROS, kamera, tracking, atau perintah robot.

Jalankan dari root repository dengan environment yang sudah tersedia:

```bash
source .venv-op3-pytorch/bin/activate
PYTHONPATH="$PWD/ros2_packages/op3_camera_eval:$PWD/ros2_packages/op3_multi_session_eval" \
python -m op3_multi_session_eval \
  --primary-session data/op3_camera_eval/sessions/20261021_robot_ball_01 \
  --primary-session data/op3_camera_eval/sessions/20261021_robot_gawang_01 \
  --primary-session data/op3_camera_eval/sessions/20261021_robot_ball_moving_01 \
  --primary-session data/op3_camera_eval/sessions/20261021_ball_moving_candidate_01 \
  --primary-session data/op3_camera_eval/sessions/20261021_all_three_position_01 \
  --primary-session data/op3_camera_eval/sessions/20261021_all_three_position_02 \
  --primary-session data/op3_camera_eval/sessions/20261021_all_three_position_03 \
  --primary-session data/op3_camera_eval/sessions/20261021_all_three_position_04 \
  --negative-session data/op3_camera_eval/sessions/20261021_negative_candidate_01 \
  --partial-session data/op3_camera_eval/sessions/20261021_gawang_ball_01 \
  --partial-session data/op3_camera_eval/sessions/20261021_all_three_position_05 \
  --output-dir runs/op3_multi_session_eval/NAMA_RUN_BARU \
  --models kd=models/weights/kd_student_best.pt \
           supervised=runs/supervised/yolo11_tiny_supervised_seed42_retry1/weights/best.pt
```

Argumen `--primary-session` menerima sesi objek dengan label gawang yang konsisten, `--negative-session` menerima frame tanpa target, dan `--partial-session` menerima gawang satu tiang yang dilaporkan terpisah. Nama gambar di snapshot dataset diberi awalan nama sesi; setiap input dan checkpoint di-hash dalam `input_manifest.json`. Output harus menuju folder yang belum ada.

Metrik AP memakai validasi Ultralytics pada `imgsz=640`, FP32 CPU, confidence floor 0,001, NMS IoU 0,7. Precision, recall, dan F1 dihitung dari prediksi dengan confidence >0,25 dan pencocokan kelas serta IoU ≥0,5. Prediksi tanpa ground truth dihitung sebagai false positive, sedangkan kelas tanpa ground truth diberi nilai metrik `null` dan tidak masuk rata-rata macro. Set negatif menghasilkan jumlah frame dan kotak false positive, bukan accuracy. Set parsial mempunyai AP sendiri yang tidak digabung ke AP utama. Semua angka adalah evaluasi eksploratif dari satu sesi pengambilan data, bukan generalisasi ke kondisi lain.
