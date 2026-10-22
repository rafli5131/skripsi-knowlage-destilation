# Prompt percobaan KD Hybrid full pada ROBOTIS OP3

> Salin bagian **Prompt siap pakai** ke agen yang bekerja langsung pada komputer OP3. Gunakan setelah repo terbaru tersedia di robot. Fokus percobaan: checkpoint Hybrid full seed 1337, deteksi dan tracking `ball`, `gawang`, `robot`, lalu pengukuran kamera OP3 saat servo idle dan saat berjalan. Jangan menganggap hasil lab/server sebagai hasil robot.

## Prompt siap pakai

Bertindak sebagai engineer ROS 2 dan peneliti evaluasi deteksi objek. Jalankan percobaan **KD Hybrid full seed 1337** pada ROBOTIS OP3 menggunakan PyTorch CPU FP32 dan checkpoint `.pt` yang terdaftar. Kerjakan berurutan, simpan artefak per sesi, dan laporkan hasil yang benar-benar terukur. Jangan melatih model di OP3, memasang OpenVINO/QAT/INT8, atau mengirim perintah servo, gait, maupun motor. Operator robot menyiapkan serta memverifikasi kondisi fisik `servo_idle` atau `walking`.

### 1. Audit sebelum membuka kamera

Di root repo, baca `OP3_PYTORCH_RUNTIME.md`, `configs/model_registry.yaml`, `scripts/model_registry.py`, `scripts/op3_pytorch_detector.py`, dan prompt ini. Catat commit, `git status`, waktu, OS/Python/ROS, CPU, RAM, versi PyTorch/Ultralytics/OpenCV, serta topic kamera dan QoS aktual. Gunakan venv OP3 yang sudah disiapkan; jangan memasang paket ke Python sistem. Periksa dengan perintah berikut dan simpan output penting:

```bash
git rev-parse HEAD
git status --short
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
ros2 topic list
ros2 topic info /thesis/image_raw
ros2 topic hz /thesis/image_raw
sha256sum runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt
```

Hash kandidat harus `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`, sama dengan entri `hybrid_full_seed1337` di registry. Kelas harus `0: ball`, `1: gawang`, `2: robot`. Verifikasi topic benar-benar `sensor_msgs/msg/Image` dari kamera OP3; jika berbeda, pakai nama aktual yang telah dibuktikan. Satu publisher kamera saja. Bila file, hash, kelas, dependency, atau topic tidak cocok, hentikan tahap yang bergantung padanya dan laporkan bukti kegagalan.

Runtime repo terbaru sudah memetakan `model_variant:=hybrid` ke `hybrid_full_seed1337` dan memvalidasi prefiks serta SHA-256 checkpoint. `op3_default` tetap KD murni. Pastikan checkout OP3 memuat pemetaan tersebut sebelum sesi kamera; jika belum, tarik pembaruan repo dan ulangi audit. Jangan menjalankan checkpoint Hybrid dengan `model_variant:=kd`, karena itu salah menamai metode.

### 2. Uji fungsi live pada kondisi diam

Minta operator memastikan robot **servo menyala dan diam**. Jika kondisi tidak terverifikasi, catat `unknown`; jangan menamainya `servo_idle`. Tentukan `run_id` baru yang belum ada, misalnya `20261022_hybrid1337_idle_01_live` (ganti tanggal/nomor sesuai sesi). Jalankan satu node detektor dengan checkpoint Hybrid yang terdaftar:

```bash
python scripts/op3_pytorch_detector.py --ros-args \
  -p input_topic:=/thesis/image_raw \
  -p model_variant:=hybrid \
  -p model_path:=runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt \
  -p run_id:=20261022_hybrid1337_idle_01_live \
  -p experiment_condition:=servo_idle \
  -p imgsz:=640 \
  -p confidence_threshold:=0.25 \
  -p iou_threshold:=0.45 \
  -p enable_tracking:=true \
  -p tracker_config:=botsort.yaml \
  -p log_detections:=true \
  -p publish_debug_image:=true
```

Ganti topic, `run_id`, dan kondisi pada perintah jika hasil audit menuntutnya. Di terminal desktop/X11 lain, jalankan `python scripts/view_op3_debug_image.py --topic /vision/debug_image`. Viewer hanya membaca overlay; ia tidak menjalankan inferensi kedua. Perlihatkan `ball`, `gawang`, dan `robot` satu per satu atau bersama. Periksa kelas dan kotak secara visual; periksa ID track pada urutan frame saat objek bergerak relatif terhadap kamera. Catat objek terlewat, kelas salah, kotak melompat, ID hilang/berpindah, jeda kamera, dan error. Adanya ID saja belum membuktikan tracking akurat.

Saat monitoring berjalan, rekam **frame mentah** dari topic kamera yang sama, bukan `/vision/debug_image`, memakai terminal ketiga dan `session_id` baru. Contoh:

```bash
python scripts/capture_op3_frames.py \
  --session-id 20261022_hybrid1337_idle_01 \
  --condition servo_idle \
  --topic /thesis/image_raw \
  --max-frames 120 --interval-sec 1 --duration-sec 300
```

Sertakan objek pada jarak/posisi/cahaya berbeda, oklusi, dan frame tanpa objek. Jangan memilih frame hanya saat model berhasil mendeteksi. Hentikan detektor dengan `Ctrl-C` agar metadata selesai. Simpan `runs/op3_pytorch/<run_id>.json`, `.csv`, `_detections.csv`, dan `data/op3_camera_eval/sessions/<session_id>/` tanpa menimpa sesi lama. **Sesi dengan viewer + capture adalah bukti fungsi dan sumber gambar, bukan benchmark latency/FPS.** Jika viewer tidak tersedia, catat bahwa pemeriksaan visual belum lengkap.

### 3. Sesi berjalan dan pengukuran runtime yang bersih

Sesi `walking` hanya dilakukan ketika operator menyiapkan serta mengendalikan robot lewat prosedur yang sudah berlaku; agen tidak boleh menggerakkan robot. Gunakan `run_id` dan `session_id` berbeda, label `walking` hanya bila benar-benar terverifikasi. Ulangi pemeriksaan live dan capture dengan model, topic, resolusi, threshold, tracker, serta prosedur yang sama. Jika berjalan belum tersedia, tulis `[BELUM DIUKUR]`.

Untuk latency/FPS/CPU/RAM, jalankan **sesi terpisah** per kondisi dengan `publish_debug_image:=false` dan tanpa viewer, capture, pra-label, atau proses inferensi lain. Pakai `run_id` baru dan durasi/warm-up yang sama. Catat durasi aktual, jumlah frame diterima/diproses bila tersedia, QoS, versi runtime, beban CPU lain, resolusi, `imgsz=640`, confidence 0,25, NMS 0,45, tracking, thread CPU, dan kondisi robot. Pertama ukur Hybrid seed 1337; jika kontrol tersedia, ukur supervised seed 1337 pada kondisi dan protokol yang sama dengan `model_variant:=supervised` dan path registry `runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt`. Ulangi sesi bila waktu memungkinkan; jangan menggabungkan run yang beda kode/QoS/preview.

Hitung FPS efektif dari timestamp **frame yang diproses** setelah warm-up bila tersedia, laporkan latency end-to-end dan per tahap (median/p95), CPU proses, dan RSS RAM dari CSV/JSON. Nyatakan jumlah sampel, definisi warm-up, serta waktu operasi. `1000 / mean latency` hanya FPS turunan, bukan FPS kamera. CPU% `psutil` dapat melebihi 100% karena beberapa core; tulis CPU mentah dan jumlah logical CPU sebelum menghitung persentase ternormalisasi. Benchmark frame tetap/sapuan thread T16–T17 memerlukan alat dan sesi tersendiri; jika belum tersedia, tandai `[BELUM DIUKUR]`, jangan mengisi dari benchmark L40 atau log live.

### 4. Pra-label dan akurasi kamera OP3

Setelah capture dan benchmark selesai, buat draf label untuk **setiap** sesi kamera, tanpa menambah beban CPU selama benchmark:

```bash
python scripts/prelabel_op3_frames.py \
  --session-id 20261022_hybrid1337_idle_01 \
  --model runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt \
  --imgsz 640 --conf 0.25 --iou 0.45
```

Hasilnya di `data/op3_camera_eval/sessions/<session_id>/labels_auto/`; file `.txt` di sana hanyalah **prediksi draf**. Tinjau manual **semua** gambar, termasuk yang berlabel kosong. Perbaiki kelas, kotak, objek terlewat, dan prediksi palsu; simpan anotasi akhir di `labels_reviewed/` beserta `review_log.jsonl` yang jujur mencatat peninjau tiap gambar. Jangan mengarang nama peninjau. Evaluator `ros2_packages/op3_camera_eval` saat ini mensyaratkan metadata peninjau `bhre`; jika peninjau nyata berbeda, perbaiki validasi evaluator agar menerima metadata sebenarnya secara terdokumentasi, jangan memalsukan log. Jangan menilai mAP/P/R/F1 sebelum seluruh label final lengkap.

Evaluasi Hybrid dan supervised seed 1337 pada **frame serta label final yang sama**, terpisah untuk `servo_idle` dan `walking`. Baca `ros2_packages/op3_camera_eval/README.md` dan gunakan folder keluaran baru per sesi. Contoh setelah review lengkap:

```bash
PYTHONPATH=ros2_packages/op3_camera_eval .venv-op3-pytorch/bin/python -m op3_camera_eval \
  --session-dir data/op3_camera_eval/sessions/20261022_hybrid1337_idle_01 \
  --output-dir runs/op3_camera_eval/20261022_hybrid1337_idle_01_reviewed_v1 \
  --models hybrid=runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt \
           supervised=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt
```

Evaluator ini memakai FP32 CPU, input 640, mAP pada confidence floor 0,001/NMS IoU 0,7, serta precision/recall/F1 pada confidence **>0,25** dan pencocokan IoU 0,5. Catat jumlah gambar dan objek per kelas, hash gambar/label/model, nilai keseluruhan dan per kelas, khususnya `gawang`. Jangan menyamakan angka ini dengan TEST Advance Vision atau observasi kotak live. Jika satu kelas tidak hadir dalam ground truth, jelaskan dampaknya pada metrik dan jangan mengklaim performa tiga kelas penuh.

### 5. Laporan akhir sesi

Susun laporan bertanggal di `dokumentasi/` dan perbarui T15–T27 hanya untuk angka yang benar-benar bersumber dari OP3. Cantumkan commit/diff runtime, SHA-256 checkpoint, topic/QoS, kelas, versi software, kondisi yang diverifikasi operator, `run_id`/`session_id`, jumlah frame, bukti overlay dan track ID, status anotasi, metrik akurasi bila label final ada, latency/FPS/CPU/RAM dari sesi bersih, serta path setiap artefak. Pisahkan hasil `servo_idle` dan `walking`, Hybrid dan supervised, serta observasi dan pengukuran. Untuk yang belum tersedia, tulis `[BELUM DIUKUR]` beserta alasannya.

Jangan melakukan `git commit`, `git push`, atau mengunggah gambar/video/label/log robot dari sesi ini. Biarkan artefak robot lokal sampai operator memilih cara transfer atau publikasinya.
