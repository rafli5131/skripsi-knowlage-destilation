# Prompt evaluasi eksternal OP3 — Jalur Pertama

> Versi 1.1, 22 Oktober 2026. Prompt ini untuk sesi OP3 baru setelah robot siap. Evaluasi membandingkan KD Hybrid full seed 1337 dengan kontrol supervised seed 1337 pada frame kamera dan label akhir yang ditinjau manusia. Auto-label boleh dipakai sebagai draf untuk mempercepat anotasi; Bhre memeriksa setiap frame dan mengoreksinya. Ini bukti tambahan di domain robot; tidak menghapus riwayat penggunaan TEST Advance Vision atau kekurangan provenance teacher. Prompt ini belum dijalankan.

## Prompt siap pakai

Bertindak sebagai engineer ROS 2 dan pencatat eksperimen untuk evaluasi eksternal pada ROBOTIS OP3. Baca `agent.md`, prompt ini, `OP3_PYTORCH_RUNTIME.md`, `configs/analysis.yaml`, `configs/model_registry.yaml`, dan README package OP3 yang akan digunakan sebelum bertindak.

### Tujuan dan batas penelitian

- Bandingkan `hybrid_full_seed1337` dengan `supervised_seed1337`. Keduanya memakai arsitektur student yang sama; perbandingan ini menilai objective training pada frame kamera OP3.
- Pakai sesi/frame baru yang belum digunakan untuk memilih model atau threshold. Evaluasi dua checkpoint pada **gambar dan label final yang identik**.
- Laporkan kondisi `servo_idle` dan `walking` terpisah. Operator harus memverifikasi kondisi fisik; agen tidak mengendalikan servo, motor, gait, atau gerakan robot. Jika kondisi tidak terverifikasi, catat `unknown` dan jangan klaim itu idle atau walking.
- Pisahkan pemeriksaan live/tracking, benchmark runtime, dan evaluasi akurasi offline. Jumlah deteksi atau ID tracker bukan metrik akurasi.
- Jangan melatih model, mengganti alias `op3_default`, mengubah parameter berdasarkan set evaluasi final, memasang OpenVINO/QAT/INT8, mengubah CPU governor, atau melakukan `git commit`/`git push`.
- Semua gambar, label, video, dan log OP3 tetap lokal. Jangan unggah atau menyalinnya ke repo publik. Jangan menimpa atau menghapus sesi dan artefak lama.

### 1. Audit awal dan kesiapan

Mulai dengan pemeriksaan baca-saja. Jangan menjalankan `git pull` otomatis karena checkout robot mungkin memiliki perubahan lokal. Catat tanggal/jam lokal dan UTC, commit, status working tree, OS, Python, ROS, PyTorch, Ultralytics, OpenCV, CPU, RAM, governor (baca saja), node OP3, topic kamera, tipe pesan, QoS, publisher, dan laju kamera.

```bash
git rev-parse HEAD
git status --short
date --iso-8601=seconds
date -u --iso-8601=seconds
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

Gunakan topic kamera yang benar-benar terdeteksi; `/thesis/image_raw` hanya nilai default. Pastikan tipe `sensor_msgs/msg/Image`, publisher kamera berfungsi, dan environment sesuai `OP3_PYTORCH_RUNTIME.md`. Jangan memasang paket ke Python sistem. Jika robot belum siap, kamera/topic tidak tersedia, kondisi tidak aman, atau environment tidak cocok, selesaikan hanya audit baca-saja lalu laporkan blocker. Jangan mengarang hasil atau mencoba menyalakan aktuator.

### 2. Verifikasi dan bekukan checkpoint

Checkpoint utama dipilih dari VAL sebelum evaluasi TEST Hybrid:

| Peran | Registry | Path relatif repo | SHA-256 |
| --- | --- | --- | --- |
| KD Hybrid full | `hybrid_full_seed1337` | `runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt` | `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363` |
| Kontrol supervised | `supervised_seed1337` | `runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt` | `d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041` |

Sebelum membuka kamera, pastikan kedua file ada, hash cocok dengan tabel dan `configs/model_registry.yaml`, serta mapping kelas checkpoint adalah `0: ball`, `1: gawang`, `2: robot`.

```bash
sha256sum runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt
sha256sum runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt
```

Jika salah satu checkpoint belum ada pada OP3, jangan mengambil model lain sebagai pengganti dan jangan mengunduh atau mengunggah bobot secara otomatis. Minta operator memindahkan checkpoint melalui jalur privat yang disetujui, lalu verifikasi SHA-256 kembali. Jangan mengubah `op3_default`; runtime harus menerima model melalui `model_variant` dan path eksplisit. Catat path, hash, ukuran berkas, dan versi repo dalam manifest sesi.

### 3. Periksa keputusan protokol sebelum pengambilan data final

Periksa `configs/analysis.yaml` dan keputusan yang berlaku. Jangan menganggap nilai `temporary` atau `MENUNGGU PERSETUJUAN PENGGUNA` sebagai protokol final. Sebelum mengumpulkan set evaluasi final, pastikan protokol mencatat:

1. parameter runtime live yang sama untuk kedua model;
2. ukuran input dan jumlah thread yang sama;
3. jumlah sesi/ulangan dan durasi benchmark tiap kombinasi model-kondisi;
4. jumlah frame final per kondisi dan aturan pemilihan frame;
5. aturan anotasi, pembagian frame kalibrasi versus evaluasi final, dan metrik yang akan dilaporkan.

Gunakan konfigurasi runtime yang tercatat (default saat ini: `imgsz=640`, confidence `0.25`, NMS IoU `0.45`) hanya jika sudah dikunci untuk eksperimen ini. Sapuan jumlah thread, jika diperlukan, harus memakai data kalibrasi terpisah; tetapkan satu nilai sebelum benchmark final dan gunakan nilai yang sama untuk semua model dan kondisi. Jangan memilih threshold, checkpoint, jumlah thread, atau frame berdasarkan hasil set evaluasi final.

Pisahkan parameter **runtime live** dari **evaluator akurasi offline**. Pada evaluator saat ini, mAP memakai confidence floor `0.001`; precision/recall/F1 memakai confidence `>0.25`, NMS IoU `0.7`, dan IoU matching `0.5`. Catat nilai sesuai kode yang benar-benar dijalankan dan gunakan setelan identik untuk kedua checkpoint. Jangan mengubahnya setelah melihat hasil set evaluasi final.

Jika protokol final belum dikunci, lakukan audit kesiapan dan pemeriksaan fungsi kamera saja. Catat keputusan yang masih terbuka dan usulan dari `configs/analysis.yaml`; berhenti sebelum menyebut capture/benchmark sebagai evaluasi final. `max_frames=120` pada skrip capture adalah batas teknis contoh, bukan ukuran sampel penelitian yang telah disetujui.

### 4. Pisahkan set kalibrasi dan set evaluasi OP3

- Buat `session_id` baru dan unik untuk setiap kondisi/sesi. Jangan memakai ulang gambar dari T27 atau sesi OP3 lama.
- Pisahkan sesi kalibrasi (bila dipakai untuk memilih konfigurasi runtime) dari sesi evaluasi final. Catat aturan sampling dan jumlah frame sebelum capture.
- Untuk evaluasi akurasi, simpan frame mentah dari topic kamera, tanpa overlay deteksi. Jangan menyeleksi frame karena model berhasil/gagal mendeteksi objek.
- Sertakan variasi jarak, posisi, pencahayaan dan frame tanpa objek; usahakan ketiga kelas `ball`, `gawang`, dan `robot` muncul. Catat bila suatu kelas tidak muncul; jangan membuat metrik untuk kelas yang tidak memiliki ground truth.
- Simpan manifest capture, waktu ROS, resolusi, kondisi yang diverifikasi operator, lokasi pengambilan, dan catatan gangguan. Jangan simpan data ke Git.

Contoh capture setelah jumlah frame dan kondisi dikunci. Ganti semua nilai contoh dengan ID, topic, dan jumlah yang sudah dicatat; jangan jalankan placeholder literal.

```bash
python scripts/capture_op3_frames.py \
  --session-id YYYYMMDD_eval_servo_idle_01 \
  --condition servo_idle \
  --topic /thesis/image_raw \
  --max-frames JUMLAH_FRAME_YANG_DIKUNCI \
  --interval-sec 1 \
  --duration-sec 900
```

Jalankan sesi `walking` hanya jika operator memverifikasi robot benar-benar berjalan dan prosedur geraknya sudah disetujui. Agen tidak boleh memulai atau menghentikan gerakan. Jika kondisi berjalan tidak dapat diverifikasi secara independen, catat sebagai `unknown` dan jangan masukkan sebagai hasil walking.

### 5. Susun label akhir dengan bantuan auto-label

- Auto-label boleh digunakan sebagai draf untuk menghemat waktu. Simpan di `labels_auto/`; catat checkpoint/hash dan confidence/NMS yang menghasilkan draf. Auto-label sendiri bukan label akhir.
- Bhre adalah evaluator manusia. Tinjau **satu per satu semua gambar dan semua kotak** dengan membandingkan draf terhadap gambar asli: tambahkan objek yang terlewat, hapus deteksi palsu, koreksi kelas dan posisi kotak, dan periksa gambar yang drafnya kosong. Simpan hasil tinjauan di `labels_reviewed/`.
- Jalankan peninjau dengan identitas `bhre` agar `review_log.jsonl` mencatat nama yang benar dan waktu tinjauan. Jangan mengubah metadata identitas. File kosong di `labels_reviewed/` berarti Bhre telah memeriksa frame dan menyimpulkan tidak ada objek target.
- Jika draf dibuat oleh salah satu model yang sedang dibandingkan, ada risiko bias jangkar: kotak yang diajukan dapat memengaruhi peninjauan. Kurangi dengan memeriksa seluruh gambar asli, termasuk area tanpa kotak, dan tidak menerima kotak hanya karena tersedia. Catat sumber draf apa adanya. Jika mudah dilakukan, gunakan draf dari checkpoint yang tidak sedang dibandingkan atau minta peninjau kedua memeriksa sebagian label; ini langkah pengendalian bias, bukan syarat untuk mempercepat alur.
- Sebelum evaluasi, pastikan setiap gambar memiliki label yang sudah ditinjau, kelas sesuai mapping, tidak ada label invalid/orphan, serta semua frame dicantumkan pada manifest hash. Evaluasi hanya `labels_reviewed/`, jangan `labels_auto/`.
- Evaluator saat ini mensyaratkan nama reviewer `bhre`, sesuai evaluator manusia Bhre, tetapi menulis status `exploratory_single_servo_idle_session`. Untuk sesi baru, pertahankan identitas `bhre` dan siapkan penyesuaian status/provenance evaluator agar melaporkan kondisi serta cakupan baru dengan akurat. Jangan membiarkan laporan baru berlabel eksploratif/servo-idle bila cakupannya berbeda. Jika metadata evaluator belum disesuaikan, jangan klaim laporan sebagai evaluasi final.

### 6. Pemeriksaan live detection/tracking

Lakukan pemeriksaan fungsi secara terpisah dari benchmark: tampilkan objek target satu per satu/seperlunya, pastikan output kelas dan bounding box masuk akal, dan periksa ID tracking lintas frame. Catat salah kelas, objek terlewat, kotak tidak stabil, ID berganti, atau error. Pengamatan visual dan ID tracker hanya bukti fungsi eksploratif, bukan akurasi berlabel.

Jalankan satu model per sesi dengan `run_id` baru, tracking tetap sama, preview aktif hanya untuk pemeriksaan ini. Gunakan path eksplisit agar supervised yang dipakai benar-benar seed 1337:

```bash
python scripts/op3_pytorch_detector.py --ros-args \
  -p input_topic:=/thesis/image_raw \
  -p model_variant:=hybrid \
  -p model_path:=runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt \
  -p run_id:=YYYYMMDD_hybrid_function_01 \
  -p experiment_condition:=servo_idle \
  -p imgsz:=640 -p confidence_threshold:=0.25 -p iou_threshold:=0.45 \
  -p enable_tracking:=true -p tracker_config:=botsort.yaml \
  -p publish_debug_image:=true \
  -p warmup_frames:=30 -p duration_s:=0
```

Ulangi dengan `model_variant:=supervised`, `model_path:=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt`, dan `run_id` berbeda. Terapkan threshold dan kondisi hanya sesuai protokol yang telah dikunci. Bila ROS menolak model/path/hash, hentikan dan laporkan; jangan melewati validasi checkpoint.

### 7. Benchmark runtime bersih

Benchmark terpisah dari capture frame dan preview. Gunakan satu node detektor, preview mati, tracking dan seluruh parameter identik, satu model per sesi, serta kondisi fisik yang sama untuk pasangan model. Jangan menjalankan viewer, labeler, atau capture bersamaan.

Untuk setiap kondisi yang disetujui (`servo_idle`, dan `walking` hanya bila aman serta terverifikasi), jalankan jumlah ulangan yang telah dikunci untuk kedua model. Gunakan urutan bergantian antarmodel untuk mengurangi bias pemanasan, dan buat `run_id` unik. Contoh perintah Hybrid:

```bash
python scripts/op3_pytorch_detector.py --ros-args \
  -p input_topic:=/thesis/image_raw \
  -p model_variant:=hybrid \
  -p model_path:=runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt \
  -p run_id:=YYYYMMDD_hybrid_idle_rep01 \
  -p experiment_condition:=servo_idle \
  -p imgsz:=640 -p confidence_threshold:=0.25 -p iou_threshold:=0.45 \
  -p enable_tracking:=true -p tracker_config:=botsort.yaml \
  -p publish_debug_image:=false \
  -p torch_num_threads:=JUMLAH_THREAD_TERKUNCI -p torch_interop_threads:=0 \
  -p warmup_frames:=30 -p duration_s:=60
```

Ulangi untuk supervised dengan `model_variant:=supervised`, path seed 1337, dan `run_id` berbeda. Jangan gunakan jumlah thread atau durasi contoh jika berbeda dari protokol terkunci. Dari JSON/CSV laporkan setidaknya: hash checkpoint, threshold, input size, thread, kondisi, jumlah frame ukur, durasi, median/p95 latensi end-to-end, FPS efektif setelah warm-up, CPU, RSS RAM, suhu awal/akhir bila tersedia, dan error/drop. FPS efektif berasal dari log frame; jangan menggantinya dengan `1000 / latency`. Jika benchmark gagal atau kondisi berubah, simpan log dan tandai ulangan invalid beserta alasannya.

### 8. Evaluasi akurasi berpasangan secara offline

Jalankan hanya setelah seluruh label akhir di `labels_reviewed/` selesai ditinjau Bhre. Evaluasi semua model pada gambar dan label yang sama, dengan evaluator/config identik. Gunakan folder output baru:

```bash
PYTHONPATH=ros2_packages/op3_camera_eval .venv-op3-pytorch/bin/python -m op3_camera_eval \
  --session-dir data/op3_camera_eval/sessions/SESSION_EVALUASI_FINAL \
  --output-dir runs/op3_camera_eval/SESSION_EVALUASI_FINAL_paired_v1 \
  --models hybrid=runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt \
           supervised=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt
```

Pastikan evaluator membaca `labels_reviewed/`, bukan `labels_auto/`. Jika layout sesi atau evaluator tidak memenuhi syarat ini, berhenti sebelum menghitung metrik dan laporkan perubahan yang dibutuhkan. Simpan hash gambar, label, checkpoint, evaluator, dan konfigurasi. Laporkan mAP50, mAP50–95, precision, recall, F1 sesuai definisi evaluator, per kelas serta agregat; nyatakan jumlah ground truth setiap kelas dan batas ukuran/sesi sampel. Bandingkan Hybrid dengan supervised secara berpasangan. Jangan memilih ulang model atau threshold dari hasil ini. Dalam metodologi, sebut label sebagai hasil anotasi berbantuan auto-label yang ditinjau dan dikoreksi Bhre; jangan menyamarkannya sebagai anotasi yang dibuat tanpa bantuan model.

### 9. Artefak dan laporan

Simpan frame di `data/op3_camera_eval/sessions/<session_id>/`, log runtime di `runs/op3_pytorch/`, dan hasil evaluasi baru di direktori unik `runs/op3_camera_eval/`. Buat manifest yang memuat commit repo, timestamp, perangkat/runtime, topic/QoS, kondisi dan siapa yang memverifikasinya, konfigurasi, hash model, jumlah gambar, hash gambar/label, status review, serta alasan data/ulangan dikeluarkan.

Setelah data dipindah secara privat ke lab/server, perbarui tabel OP3 dan laporan dari manifest/CSV/JSON sumber. Pisahkan hasil baru dari T27 eksploratif yang labelnya berawal dari draft KD. Jelaskan bahwa evaluasi ini menambah bukti domain robot, tetapi tidak membersihkan penggunaan ulang TEST Advance Vision, tidak membuktikan ulang provenance teacher, dan tidak membenarkan klaim generalisasi adegan baru pada dataset Advance Vision.

Di akhir, laporkan perintah yang dijalankan, hasil preflight, checkpoint/hash, `session_id`/`run_id`, lokasi artefak lokal, tabel yang dapat diperbarui, error, kondisi yang belum terukur, serta langkah berikutnya. Jangan commit/push atau mengirim artefak robot.
