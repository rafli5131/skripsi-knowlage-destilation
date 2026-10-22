# Prompt uji KD Hybrid full dan teacher pada ROBOTIS OP3

> Versi 2, 22 Oktober 2026. Menggantikan prompt lama untuk persiapan teknis karena runtime kini mendukung override teacher lokal, batas thread, warm-up, durasi terukur, dan FPS efektif. Prompt ini belum dijalankan di robot. Bobot teacher tetap harus dipindahkan secara privat oleh operator; jangan commit atau push artefak robot.

## Prompt siap pakai

Bertindak sebagai engineer ROS 2 dan pencatat eksperimen pada ROBOTIS OP3. Tujuan sesi adalah menguji fungsi deteksi/tracking dan mengukur runtime CPU FP32 untuk `hybrid_full_seed1337` serta `teacher_fp32` pada kamera onboard. Model kelasnya `ball`, `gawang`, dan `robot`. Baca prompt ini, `OP3_PYTORCH_RUNTIME.md`, dan `docs/TRANSFER_TEACHER_KE_OP3.md` lebih dahulu.

Jangan melatih model, mengganti alias `op3_default`, memasang OpenVINO/QAT/INT8, mengubah governor CPU, atau mengirim perintah servo/gait/motor. Operator bertanggung jawab atas kondisi fisik robot dan semua gerak. Jangan melakukan `git commit` atau `git push` dari robot. Semua gambar, label, video, dan log robot tetap lokal sampai operator memilih jalur pemindahan yang disetujui.

### 1. Audit awal dan prasyarat

Di root repository, catat waktu lokal/UTC, commit, `git status --short`, OS, Python, ROS, PyTorch, Ultralytics, OpenCV, CPU, RAM, governor CPU (baca saja), status `op3_manager`, serta topic kamera, tipe pesannya, QoS, publisher, dan laju aktual. Pastikan satu publisher saja memiliki kamera. Aktifkan environment sesuai `OP3_PYTORCH_RUNTIME.md`; jangan memasang paket ke Python sistem.

```bash
git rev-parse HEAD
git status --short
cat /etc/os-release
python3 --version
printenv ROS_DISTRO
lscpu
free -h
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || true
ros2 node list
ros2 topic list -t
ros2 topic info /thesis/image_raw -v
ros2 topic hz /thesis/image_raw
```

Gunakan `source /opt/ros/jazzy/setup.bash` dan `.venv-op3-pytorch` seperti dokumentasi. Verifikasi bahwa topic aktual bertipe `sensor_msgs/msg/Image`; ganti `/thesis/image_raw` pada seluruh perintah jika audit membuktikan nama topic berbeda.

Verifikasi checkpoint yang akan dipakai dan kelasnya sebelum membuka kamera:

```bash
sha256sum runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt
sha256sum runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt
sha256sum models_local/teacher_fp32_best.pt
```

Hash Hybrid seed 1337 harus `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`; supervised seed 1337 harus `d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041`; teacher harus `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`. Cocokkan juga SHA-256 dengan `configs/model_registry.yaml`. Pastikan `configs/model_registry_local.yaml` lokal berisi:

```yaml
teacher_fp32: models_local/teacher_fp32_best.pt
```

Jalankan hanya model yang file dan hash-nya sudah lolos. Bila teacher belum dipindahkan atau hash tidak cocok, jangan jalankan teacher dan jangan mengklaim perbandingan KD-teacher selesai. Jangan menyalin bobot teacher ke GitHub.

Pastikan urutan kelas `0: ball`, `1: gawang`, `2: robot`. Bila `op3_manager` tidak aktif, topic tidak tersedia, hash/dependency tidak cocok, working tree memiliki perubahan runtime yang tidak diketahui, atau kondisi perangkat tidak aman, hentikan tahap terkait dan laporkan bukti. Jangan menjalankan perintah yang mengubah gerak robot.

### 2. Sesi 0: pemilihan jumlah thread

Sesi ini menentukan `torch_num_threads` sebelum benchmark. Operator memastikan robot berada pada kondisi `servo_idle`. Gunakan thread antar-operasi PyTorch pada default (`torch_interop_threads:=0`) untuk semua model agar hanya jumlah thread intra-operasi yang disapu. Matikan preview, gunakan tracking yang sama dengan sesi utama, confidence `0.25`, NMS IoU `0.45`, warm-up 30 frame, dan durasi 60 detik sesudah warm-up.

Jalankan satu sesi untuk tiap kandidat `2`, `4`, `6`, dan `8`, masing-masing dengan `run_id` baru dan `torch_num_threads` sesuai kandidat. Contoh kandidat 2:

```bash
python scripts/op3_pytorch_detector.py --ros-args \
  -p input_topic:=/thesis/image_raw \
  -p model_variant:=hybrid \
  -p run_id:=YYYYMMDD_threads2_01 \
  -p experiment_condition:=servo_idle \
  -p imgsz:=640 -p confidence_threshold:=0.25 -p iou_threshold:=0.45 \
  -p enable_tracking:=true -p tracker_config:=botsort.yaml \
  -p publish_debug_image:=false \
  -p torch_num_threads:=2 -p torch_interop_threads:=0 \
  -p warmup_frames:=30 -p duration_s:=60
```

Ulangi perintah dengan `torch_num_threads:=4`, `6`, dan `8`, serta `run_id` unik. Jangan jalankan viewer, capture, pra-label, atau inferensi lain selama sesi ini. Dari CSV, buang baris `is_warmup=true`; hitung median `end_to_end_ms` pada baris ukur dan ambil `effective_fps_after_warmup` dari JSON akhir. Pilih kandidat dengan jumlah thread terkecil yang median latensinya paling banyak 10% di atas kandidat terbaik dan FPS efektifnya sekurang-kurangnya 95% FPS terbaik. Jika tidak ada kandidat yang memenuhi kedua syarat, laporkan hasil dan jangan memilih berdasarkan tebakan.

Catat semua hasil dan kandidat pilihan kepada Bhre. **Tunggu konfirmasi Bhre atas jumlah thread terpilih sebelum sesi benchmark utama.** Gunakan nilai yang disetujui sama untuk semua model dan kondisi.

### 3. Sesi A: fungsi live, tracking, dan pengumpulan frame

Operator memverifikasi kondisi robot. Jika servo menyala dan robot diam, beri label `servo_idle`; jika tidak terverifikasi, gunakan `unknown`. Jalankan detektor Hybrid dengan `model_variant:=hybrid`, thread yang telah disetujui, `confidence_threshold:=0.25`, `iou_threshold:=0.45`, tracking `botsort.yaml`, preview aktif, `warmup_frames:=30`, dan `duration_s:=0` (berjalan sampai dihentikan operator). Gunakan `run_id` baru.

Di terminal lain, tampilkan overlay:

```bash
python scripts/view_op3_debug_image.py --topic /vision/debug_image
```

Di terminal ketiga, rekam frame mentah dari topic kamera yang sama, bukan topic debug:

```bash
python scripts/capture_op3_frames.py \
  --session-id YYYYMMDD_hybrid_idle_01 \
  --condition servo_idle \
  --topic /thesis/image_raw \
  --max-frames 120 --interval-sec 1 --duration-sec 300
```

Ganti tanggal, ID, topic, dan kondisi sesuai audit. Operator harus memperlihatkan bola, gawang, dan robot satu per satu atau bersama, termasuk variasi jarak/posisi dan frame tanpa objek. Catat salah kelas, objek terlewat, kotak melompat, perubahan/hilangnya ID, serta gangguan kamera. ID yang muncul tidak dengan sendirinya membuktikan tracking akurat. Hentikan node dengan `Ctrl-C` setelah capture berakhir. Sesi dengan viewer dan capture adalah bukti fungsi, **bukan benchmark**.

Sesudah seluruh sesi live selesai, buat draf label:

```bash
python scripts/prelabel_op3_frames.py \
  --session-id YYYYMMDD_hybrid_idle_01 \
  --model runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt \
  --imgsz 640 --conf 0.25 --iou 0.45
```

Draf tersimpan di `data/op3_camera_eval/sessions/<session_id>/labels_auto/`. Pra-label dari model mana pun bukan ground truth. Tinjau manual setiap gambar, termasuk label kosong, koreksi objek hilang/palsu, kelas, dan kotak; simpan hasil pada `labels_reviewed/` dan buat log peninjauan yang menyebut peninjau sebenarnya. Jangan menghitung akurasi dari `labels_auto/`.

### 4. Sesi B: benchmark runtime bersih

Lakukan sesi hanya setelah nilai thread sesi 0 disetujui Bhre. Setiap pengukuran memakai `warmup_frames:=30` dan `duration_s:=60`, preview mati, tanpa viewer/capture/pra-label, satu node detektor, confidence `0.25`, NMS IoU `0.45`, tracking aktif dengan `botsort.yaml`, ukuran 640, dan jumlah thread yang sama. Jalankan:

- `hybrid_full_seed1337` dan `teacher_fp32`;
- kondisi `servo_idle` dan `walking`;
- tiga ulangan per kombinasi model-kondisi.

Gunakan urutan bergantian dalam tiap kondisi, misalnya Hybrid, teacher, teacher, Hybrid, Hybrid, teacher. Beri jeda sekurang-kurangnya dua menit di antara sesi; catat temperatur CPU sebelum dan sesudah tiap sesi, serta beban proses lain. `walking` hanya boleh diberi label setelah operator mengonfirmasi kondisi dan menjalankan prosedur gerak robot yang telah disepakati dengan pembimbing. Agen tidak boleh memulai/ menghentikan gait atau menjalankan `op3_head_ball_tracking`. Jika definisi atau kondisi berjalan belum disepakati/diverifikasi, tunda semua sesi walking dan tulis `[BELUM DIUKUR]`.

Contoh sesi Hybrid idle:

```bash
python scripts/op3_pytorch_detector.py --ros-args \
  -p input_topic:=/thesis/image_raw -p model_variant:=hybrid \
  -p run_id:=YYYYMMDD_hybrid_idle_01 \
  -p experiment_condition:=servo_idle \
  -p imgsz:=640 -p confidence_threshold:=0.25 -p iou_threshold:=0.45 \
  -p enable_tracking:=true -p tracker_config:=botsort.yaml \
  -p publish_debug_image:=false \
  -p torch_num_threads:=N -p torch_interop_threads:=0 \
  -p warmup_frames:=30 -p duration_s:=60
```

Ganti `N` dengan jumlah thread yang telah disetujui. Jalankan teacher dengan `model_variant:=teacher` dan `run_id` baru; biarkan `model_path` kosong agar runtime mengambil override lokal, lalu pastikan JSON mencatat `checkpoint_local_override_used: true` dan hash registry teacher. Untuk walking, ubah kondisi hanya bila operator telah memverifikasinya. Jangan memakai preview/capture. Jika model atau sesi gagal, simpan log error dan jangan mengarang nilai.

Laporkan per model-kondisi median dan p95 latency end-to-end, FPS efektif dari timestamp kamera sesudah warm-up, CPU, RSS RAM, jumlah frame ukur, durasi aktual, jumlah thread aktual, status/hash checkpoint, temperatur awal/akhir, serta jumlah ulangan yang valid. CSV/JSON sesi adalah sumber angka. Pisahkan angka fungsi live dari benchmark bersih. Jangan mengganti FPS efektif dengan `1000 / latency`.

Supervised seed 1337 boleh diukur sebagai kontrol tambahan, satu sesi per kondisi, hanya bila Bhre meminta dan bobotnya tersedia serta hash-nya benar. Ini tidak menggantikan pembandingan utama Hybrid dan teacher.

### 5. Sesi C: evaluasi akurasi frame kamera secara offline

Jalankan hanya setelah set gambar dan label final tersedia. Audit set lama yang berjumlah 260 gambar target/negatif dan set parsial 50 gambar gawang: pastikan sumber, manifest/hash, cakupan kelas, dan status review diketahui. Jangan menyebut set parsial sebagai label final atau menggabungkannya tanpa dokumentasi. Bila label lama dibuat dari draf prediksi KD, nyatakan bias itu dan minta tinjauan manusia sebelum menggunakannya sebagai ground truth.

Untuk sesi baru, gunakan `labels_reviewed/` setelah seluruh gambar diperiksa. Jalankan evaluator yang sama, pengaturan yang sama, dan gambar serta label identik untuk Hybrid, teacher, serta supervised seed 1337 bila checkpoint tersedia. Contoh:

```bash
PYTHONPATH=ros2_packages/op3_camera_eval .venv-op3-pytorch/bin/python -m op3_camera_eval \
  --session-dir data/op3_camera_eval/sessions/YYYYMMDD_hybrid_idle_01 \
  --output-dir runs/op3_camera_eval/YYYYMMDD_idle01_reviewed_v1 \
  --models hybrid=runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt \
           teacher=models_local/teacher_fp32_best.pt \
           supervised=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt
```

Pastikan folder label yang dibaca evaluator memang berisi anotasi final yang ditinjau; bila evaluator tidak mendukung layout `labels_reviewed/`, hentikan sebelum evaluasi dan laporkan perubahan kode/dataset yang diperlukan. Jangan mengubah evaluator atau menyamarkan draft label sebagai final. Catat hash gambar, label, dan semua checkpoint; laporkan metrik per kelas dan keseluruhan, termasuk jika suatu kelas tidak memiliki ground truth. Hasil ini evaluasi kamera OP3 dan harus dibedakan dari Advance Vision.

### 6. Penyimpanan dan laporan

Simpan log runtime di `runs/op3_pytorch/`, gambar sesi di `data/op3_camera_eval/sessions/<session_id>/`, serta laporan bukti robot di `dokumentasi/<tanggal>/`. Jangan menimpa sesi lama. Jangan commit/push gambar, video, label, log, metadata privat, atau checkpoint teacher. Pemindahan data ke lab server harus menggunakan jalur privat yang disetujui operator, disertai manifest SHA-256.

Perbarui T15, T18, T19, T20, T21, T23, T26, dan T27 hanya dari bukti robot yang cocok. Cantumkan commit, konfigurasi, hash, topic/QoS, kondisi yang diverifikasi, `run_id`/`session_id`, jumlah frame, hasil visual tiga kelas/tracking, hash set evaluasi, status tinjauan label, metrik, serta batasan. Sajikan runtime sebagai median dan p95 dari tiga ulangan valid per model-kondisi. Untuk semua data yang belum ada, tulis `[BELUM DIUKUR]` beserta alasannya.

Pada akhir setiap fase, laporkan perintah yang dijalankan, path artefak, hasil terukur, kegagalan, serta langkah berikutnya. Jangan melanjutkan ke gerakan robot, transfer teacher, atau pemindahan data tanpa operator menjalankan dan mengonfirmasi tindakan yang diperlukan.
