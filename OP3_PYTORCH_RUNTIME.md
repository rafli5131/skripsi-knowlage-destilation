# Inferensi PyTorch pada ROBOTIS OP3

Node `scripts/op3_pytorch_detector.py` membaca `sensor_msgs/Image`, menjalankan checkpoint student KD dengan Ultralytics di CPU FP32, lalu menerbitkan `vision_msgs/Detection2DArray` pada `/vision/detections`. Node hanya menerima gambar dan menerbitkan hasil deteksi; tidak ada antarmuka servo atau gerak.

Checkpoint yang dipakai adalah `models/weights/kd_student_best.pt`. Node memeriksa checkpoint, mapping dari `configs/data_train_val.yaml`, dan mapping yang tersimpan di checkpoint. Urutan kelas harus tetap `0: ball`, `1: gawang`, `2: robot`. Input dipertahankan rasio aspeknya dan diproses lewat letterbox Ultralytics pada ukuran 640 secara default.

## Runtime

Gunakan satu interpreter Python yang dapat mengimpor ROS 2 Jazzy (`rclpy`, `cv_bridge`, `vision_msgs`) sekaligus PyTorch, Ultralytics, OpenCV, psutil, dan PyYAML. Jangan memasang paket ke Python sistem. Workspace ini memiliki `.venv-op3-pytorch` berbasis Python 3.12.3 dengan akses ke modul ROS sistem.

Binary uv 0.13.1 terpasang di `/home/humanoid/.local/bin/uv`.

Untuk membuat ulang environment:

```bash
/home/humanoid/.local/bin/uv venv --clear --system-site-packages --python /usr/bin/python3 .venv-op3-pytorch
/home/humanoid/.local/bin/uv pip install --python .venv-op3-pytorch/bin/python --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-op3-pytorch.txt
```

Aktifkan setelah memuat environment ROS agar modul dan shared library ROS terlihat:

```bash
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
```

Sebelum menjalankan node, hidupkan publisher kamera sesuai setup OP3 dan periksa topic aktual:

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic list
ros2 topic info /thesis/image_raw
```

`/thesis/image_raw` adalah topic kamera yang tercatat pada uji ROS OP3 di workspace lokal. Setup USB camera di bringup robot memetakan `/image_raw` ke topic kamera tersendiri; gunakan nama yang benar benar terlihat pada robot melalui parameter `input_topic`. Node tidak membuka `/dev/video*` secara langsung dan tidak menebak device kamera.

## Menjalankan

Dengan environment aktif dan publisher kamera berjalan:

```bash
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
python scripts/op3_pytorch_detector.py --ros-args \
  -p input_topic:=/thesis/image_raw \
  -p experiment_condition:=unknown \
  -p publish_debug_image:=true
```

`experiment_condition` adalah label yang diisi operator; node tidak membaca telemetry gerak dan tidak dapat mendeteksi apakah robot sedang berjalan. Gunakan `unknown` jika kondisi fisik belum diverifikasi. Label `servo_idle` atau `walking` hanya boleh dipakai setelah operator memverifikasi kondisi secara terpisah. Node tidak mengaktifkan atau menghentikan servo. Hentikan node dengan `Ctrl-C`.

Parameter ROS:

| Parameter | Default | Kegunaan |
| --- | --- | --- |
| `model_path` | `models/weights/kd_student_best.pt` | Checkpoint `.pt` |
| `data_config` | `configs/data_train_val.yaml` | Validasi mapping kelas |
| `input_topic` | `/thesis/image_raw` | Topic `sensor_msgs/Image` yang tersedia |
| `imgsz` | `640` | Ukuran sisi input model |
| `confidence_threshold` | `0.25` | Ambang confidence runtime |
| `iou_threshold` | `0.45` | Ambang IoU NMS runtime |
| `experiment_condition` | `unknown` | `unknown`, `servo_idle`, atau `walking`; label operator, bukan deteksi otomatis |
| `publish_debug_image` | `false` | Terbitkan preview beranotasi |
| `debug_image_topic` | `/vision/debug_image` | Topic preview |
| `output_dir` | `runs/op3_pytorch` | Direktori log |
| `run_id` | waktu UTC saat mulai | Nama dasar berkas hasil |

Threshold runtime 0.25/0.45 merupakan parameter eksplisit dan berbeda tujuan dari confidence floor/NMS protokol evaluasi offline. Catat nilai yang dipakai; jangan menafsirkan hasil tampilan sebagai akurasi kamera.

## Log dan batas pengukuran

Setiap peluncuran membuat `<run_id>.json` berisi konfigurasi aktual, hash checkpoint, mapping kelas, versi runtime, kondisi, dan status; `<run_id>.csv` mencatat timestamp frame ROS, resolusi, tahap preprocess/inference/postprocess, end-to-end callback, FPS berjalan, CPU/RAM proses, jumlah deteksi, dan error. Ultralytics menangani letterbox dan postprocess/NMS; `Results.speed` menyediakan waktu tiga tahap tersebut. CSV di-flush setelah setiap frame.

QoS kamera menggunakan best-effort, `KEEP_LAST` dengan kedalaman 1, dan callback serial. Frame lama dapat dilewati saat inferensi tertinggal; antrian tidak dimaksudkan untuk menyimpan seluruh frame. Preview mati secara default karena rendering menambah beban. Log menyatakan waktu proses dan sumber timestamp camera-header; FPS dan latensi berlaku untuk runtime host yang benar benar dipakai.

Jalankan pengukuran `servo_idle` dan `walking` sebagai dua sesi terpisah dengan checkpoint, input, ukuran, dan threshold identik. Hasil ini belum mengukur akurasi kamera: evaluasi akurasi memerlukan frame berlabel serta pembandingan ground truth. Jangan menulis angka performa OP3 sebelum sesi fisik benar benar dijalankan dan lognya diperiksa.
