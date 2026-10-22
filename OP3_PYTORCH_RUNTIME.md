# Inferensi PyTorch pada ROBOTIS OP3

Node `scripts/op3_pytorch_detector.py` membaca `sensor_msgs/Image`, menjalankan checkpoint student KD dengan Ultralytics di CPU FP32, lalu menerbitkan `vision_msgs/Detection2DArray` pada `/vision/detections`. Mode tracking aktif secara default menggunakan BoT-SORT. Setiap deteksi membawa ID sesi pada `Detection2D.id` dengan bentuk `ball:ID`, `gawang:ID`, atau `robot:ID`. ID hanya berlaku selama satu proses node dan dapat berubah setelah objek tertutup atau tracker direset. Node hanya menerima gambar dan menerbitkan hasil deteksi/tracking; tidak ada antarmuka servo atau gerak.

Checkpoint bawaan adalah alias `op3_default` pada `configs/model_registry.yaml`, saat ini `models/weights/kd_student_best.pt`. Node memeriksa SHA-256 checkpoint melalui registry, mapping dari `configs/data_train_val.yaml`, dan mapping yang tersimpan di checkpoint. Urutan kelas harus tetap `0: ball`, `1: gawang`, `2: robot`. Input dipertahankan rasio aspeknya dan diproses lewat letterbox Ultralytics pada ukuran 640 secara default.

## Runtime

Gunakan satu interpreter Python yang dapat mengimpor ROS 2 Jazzy (`rclpy`, `cv_bridge`, `vision_msgs`) sekaligus PyTorch, Ultralytics, OpenCV, psutil, dan PyYAML. Jangan memasang paket ke Python sistem. Workspace ini memiliki `.venv-op3-pytorch` berbasis Python 3.12.3 dengan akses ke modul ROS sistem.

Binary uv 0.13.1 terpasang di `/home/humanoid/.local/bin/uv`.

Jika environment belum tersedia, buat tanpa menghapus environment yang mungkin sudah ada lalu pasang seluruh dependensi. Jika venv OP3 yang sudah dipakai tersedia, pasang hanya dependensi tracker yang baru diperlukan agar paket lain tidak berubah:

```bash
if [ ! -x .venv-op3-pytorch/bin/python ]; then
  /home/humanoid/.local/bin/uv venv --system-site-packages --python /usr/bin/python3 .venv-op3-pytorch
  /home/humanoid/.local/bin/uv pip install --python .venv-op3-pytorch/bin/python --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-op3-pytorch.txt
else
  /home/humanoid/.local/bin/uv pip install --python .venv-op3-pytorch/bin/python lap==0.5.12
fi
```

Paket `lap==0.5.12` diperlukan Ultralytics untuk asosiasi BoT-SORT/ByteTrack. Node mengecek versinya saat startup dan berhenti dengan pesan yang jelas jika paket belum terpasang; mode tracking tidak akan gagal diam-diam pada setiap frame.

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
  -p enable_tracking:=true \
  -p tracker_config:=botsort.yaml \
  -p log_detections:=true \
  -p publish_debug_image:=true
```

`experiment_condition` adalah label yang diisi operator; node tidak membaca telemetry gerak dan tidak dapat mendeteksi apakah robot sedang berjalan. Gunakan `unknown` jika kondisi fisik belum diverifikasi. Label `servo_idle` atau `walking` hanya boleh dipakai setelah operator memverifikasi kondisi secara terpisah. Node tidak mengaktifkan atau menghentikan servo. Hentikan node dengan `Ctrl-C`.

Parameter ROS:

| Parameter | Default | Kegunaan |
| --- | --- | --- |
| `model_variant` | `kd` | Pilihan checkpoint bawaan: `kd`, `hybrid` (Hybrid full seed 1337), `supervised`, atau `teacher` |
| `model_path` | kosong | Gunakan checkpoint bawaan variant; path eksplisit harus terdaftar dengan hash yang cocok |
| `model_registry` | `configs/model_registry.yaml` | Path dan SHA-256 checkpoint tepercaya |
| `data_config` | `configs/data_train_val.yaml` | Validasi mapping kelas |
| `input_topic` | `/thesis/image_raw` | Topic `sensor_msgs/Image` yang tersedia |
| `imgsz` | `640` | Ukuran sisi input model |
| `confidence_threshold` | `0.25` | Ambang confidence runtime |
| `iou_threshold` | `0.45` | Ambang IoU NMS runtime |
| `enable_tracking` | `true` | Asosiasi deteksi lintas frame |
| `tracker_config` | `botsort.yaml` | Tracker Ultralytics; `bytetrack.yaml` dapat dipilih untuk konfigurasi lebih ringan |
| `log_detections` | `true` | CSV per deteksi berisi kelas, confidence, bbox, dan ID tracker |
| `experiment_condition` | `unknown` | `unknown`, `servo_idle`, atau `walking`; label operator, bukan deteksi otomatis |
| `publish_debug_image` | `false` | Terbitkan preview beranotasi |
| `debug_image_topic` | `/vision/debug_image` | Topic preview |
| `output_dir` | `runs/op3_pytorch` | Direktori log |
| `run_id` | waktu UTC saat mulai | Nama dasar berkas hasil |

Threshold runtime 0.25/0.45 merupakan parameter eksplisit dan berbeda tujuan dari confidence floor/NMS protokol evaluasi offline. Catat nilai yang dipakai; jangan menafsirkan hasil tampilan sebagai akurasi kamera.

## Log dan batas pengukuran

Setiap peluncuran membuat `<run_id>.json` berisi konfigurasi aktual, hash checkpoint, mapping kelas, versi runtime, kondisi, dan status; `<run_id>.csv` mencatat timestamp frame ROS, resolusi, tahap preprocess/inference/postprocess, end-to-end callback, FPS berjalan, CPU/RAM proses, jumlah deteksi, jumlah track, jumlah per kelas, dan error. Ultralytics menangani letterbox dan postprocess/NMS; `Results.speed` menyediakan waktu tiga tahap tersebut. CSV di-flush setelah setiap frame.
Jika `log_detections` aktif, `<run_id>_detections.csv` mencatat kelas, confidence, bbox, dan ID tracker tiap kotak. CSV frame juga menyimpan jumlah deteksi per kelas dan jumlah kotak yang memiliki track ID. Log tidak menyimpan gambar atau video.

QoS kamera menggunakan best-effort, `KEEP_LAST` dengan kedalaman 1, dan callback serial. Frame lama dapat dilewati saat inferensi tertinggal; antrian tidak dimaksudkan untuk menyimpan seluruh frame. Preview mati secara default karena rendering menambah beban. Log menyatakan waktu proses dan sumber timestamp camera-header; FPS dan latensi berlaku untuk runtime host yang benar benar dipakai.

Jalankan pengukuran `servo_idle` dan `walking` sebagai dua sesi terpisah dengan checkpoint, input, ukuran, dan threshold identik. Hasil ini belum mengukur akurasi kamera: evaluasi akurasi memerlukan frame berlabel serta pembandingan ground truth. Jangan menulis angka performa OP3 sebelum sesi fisik benar benar dijalankan dan lognya diperiksa.

Pada uji offline, satu citra VAL untuk masing-masing kelas terdeteksi pada confidence 0,25 dan ID BoT-SORT tetap pada frame berulang setelah konfirmasi track. Ini hanya memverifikasi alur model dan tracker dengan citra statis. Sesudah uji offline itu, paket terpisah `ros2_packages/op3_idle_trial/` menjalankan satu sesi kamera `servo_idle` dengan subscriber `reliable`: ketiga kelas tercatat dan ID tetap pada objek yang relatif diam. Angka serta batas pengamatannya ada di `dokumentasi/2026-10-19/percobaan-04-live-tracking-servo-idle/README.md`. Sesi tersebut tidak memakai node lama di dokumen ini, yang masih berlangganan kamera dengan QoS `best_effort`; hasil kedua jalur tidak boleh disamakan. Kondisi `walking` belum diukur.

Lihat overlay pada `/vision/debug_image` dan data bertanda ID pada `/vision/detections`. Tracking memakai frame berurutan dari satu stream. ID tidak permanen antar-run dan dapat berganti setelah oklusi; kualitas deteksi dan kestabilan ID tetap harus diperiksa pada kamera OP3 dalam kondisi idle dan walking.

Untuk memeriksa overlay dan identitas hasil saat uji kamera, jalankan di terminal lain:

```bash
ros2 topic hz /vision/detections
ros2 topic echo /vision/detections --field detections
```

Pastikan setiap `class_id` yang terlihat sesuai objek pada gambar, dan `id` berbentuk `ball:...`, `gawang:...`, atau `robot:...` saat objek terlacak. Overlay menampilkan kotak dan kelas; CSV `<run_id>_detections.csv` merekam ID serta bbox. Tiga kelas harus diuji satu per satu bila tidak tampak bersamaan pada kamera. Tiga log kamera awal berasal dari sebelum perubahan tracking dan tidak dapat membuktikan ID lintas frame. Sesi `op3_idle_trial` yang lebih baru membuktikan hanya konsistensi ID pada objek relatif diam dalam satu run; kualitas tracking objek bergerak masih perlu diuji.
