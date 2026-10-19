# Prompt Uji Langsung Kamera dan Tracking ROBOTIS OP3

> Prompt untuk langkah operasional berikutnya setelah perubahan node deteksi dan tracker siap dijalankan di komputer OP3. Uji ini memeriksa alur kamera, deteksi visual, ID tracking, dan pencatatan log. Uji ini bukan pengukuran akurasi berlabel.

---

## Prompt

Bertindak sebagai engineer computer vision dan ROS 2. Jalankan verifikasi langsung node deteksi student KD pada kamera ROBOTIS OP3 menggunakan isi repository yang tersedia di komputer OP3. Ikuti pemeriksaan di bawah secara berurutan dan laporkan bukti dari terminal serta berkas log.

### Tujuan

Pastikan node dapat menerima gambar kamera OP3 dan mendeteksi serta melacak ketiga kelas berikut:

```text
0: ball
1: gawang
2: robot
```

Model runtime adalah checkpoint student KD `.pt`, PyTorch CPU FP32, dengan tracking BoT-SORT. Keberhasilan berarti ketiga kelas terlihat benar pada overlay/data keluaran dan ID mengikuti objek yang sama pada frame berurutan. Jangan menyebut pemeriksaan ini sebagai nilai akurasi atau mAP.

### Batas kerja

- Kerjakan uji runtime pada OP3. Jangan mengubah kode, checkpoint, registry, atau konfigurasi eksperimen selama sesi pengukuran. Bila ditemukan masalah kode, hentikan uji terkait dan laporkan reproduksi serta lognya untuk diperbaiki terpisah.
- Jangan melatih model, memilih checkpoint lain, mengubah threshold, mengubah konfigurasi tracker, atau memasang OpenVINO, ONNX, QAT, maupun INT8.
- Jangan mengirim perintah servo/gait, menyalakan atau menghentikan motor, atau mengubah konfigurasi perangkat. Operator yang bertanggung jawab atas robot mengatur dan memverifikasi kondisi fisiknya secara terpisah.
- Jangan menyimpan gambar/video. Node hanya perlu membuat log CSV/JSON yang memang dirancang untuk menyimpan metadata dan hasil deteksi.
- Jangan menghapus atau menimpa log lama. Pakai `run_id` baru untuk setiap sesi.
- Jangan melakukan `git commit`, `git push`, atau mengunggah log. Jika kode yang diperlukan belum tersedia di OP3, berhenti dan laporkan prasyarat tersebut.

### Tahap 1: verifikasi workspace dan runtime

1. Catat direktori kerja, branch/commit bila tersedia, waktu, dan status perubahan repository. Jangan menjalankan perintah Git yang mengubah repository.
2. Pastikan file berikut tersedia: `scripts/op3_pytorch_detector.py`, `configs/model_registry.yaml`, `configs/data_train_val.yaml`, `models/weights/kd_student_best.pt`, `requirements-op3-pytorch.txt`, dan `OP3_PYTORCH_RUNTIME.md`.
3. Baca instruksi runtime di `OP3_PYTORCH_RUNTIME.md`. Periksa checksum checkpoint melalui registry dan pastikan mapping kelas model serta konfigurasi sama dengan `ball`, `gawang`, `robot`.
4. Periksa OS, Python, ROS 2, versi PyTorch/Ultralytics/OpenCV, serta impor `rclpy`, `cv_bridge`, `vision_msgs`, `lap`, dan `psutil` di environment yang akan menjalankan node. Gunakan venv proyek yang telah disiapkan; jangan memasang paket ke Python sistem.
5. Jika venv proyek sudah ada tetapi `lap==0.5.12` belum tersedia, ikuti instruksi runtime untuk memasang hanya versi tersebut ke venv. Jika instalasi memerlukan jaringan/izin operator atau gagal, berhenti dan laporkan; jangan mengganti dependency atau menonaktifkan tracking.
6. Periksa publisher kamera dan format topic aktual. Verifikasi `/thesis/image_raw` dengan `ros2 topic list`, `ros2 topic info`, dan `ros2 topic hz`. Bila topic aktual berbeda, gunakan topic kamera yang benar dan catat namanya. Jangan menebak atau membuka device kamera lain.

**Titik berhenti 1:** Jika file/checkpoint, ROS, dependency tracking, atau publisher kamera tidak tersedia, jangan lanjutkan ke klaim berhasil. Laporkan pemeriksaan yang gagal, keluaran terminal, dan langkah prasyarat yang dibutuhkan.

### Tahap 2: uji visual dan tracking saat robot diam

1. Mulai dengan robot dalam kondisi diam. Isi `experiment_condition:=servo_idle` hanya setelah operator memverifikasi kondisi tersebut; jika belum dapat dipastikan, gunakan `unknown`.
2. Jalankan node sesuai dokumentasi runtime, dengan tracking dan CSV per deteksi aktif serta preview diaktifkan untuk pemeriksaan visual. Pertahankan nilai bawaan `imgsz=640`, confidence `0.25`, IoU `0.45`, dan `botsort.yaml`.

Contoh perintah, setelah topic kamera dikonfirmasi:

```bash
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
python scripts/op3_pytorch_detector.py --ros-args \
  -p input_topic:=/thesis/image_raw \
  -p experiment_condition:=servo_idle \
  -p enable_tracking:=true \
  -p tracker_config:=botsort.yaml \
  -p log_detections:=true \
  -p publish_debug_image:=true
```

Ganti `input_topic` hanya jika pemeriksaan tahap 1 menunjukkan nama topic kamera lain. Gunakan `experiment_condition:=unknown` bila status idle belum diverifikasi.

3. Di terminal terpisah, periksa keluaran dan preview:

```bash
ros2 topic hz /vision/detections
ros2 topic echo /vision/detections --field detections
```

Gunakan penampil ROS yang sudah tersedia untuk melihat `/vision/debug_image`. Jangan memasang penampil baru tanpa kebutuhan yang jelas. Jika preview tidak dapat ditampilkan, catat bahwa verifikasi visual belum lengkap.

4. Hadirkan bola, gawang, dan robot ke bidang pandang kamera satu per satu atau bersamaan. Jangan menggerakkan robot. Untuk memeriksa tracking, biarkan tiap objek tampil selama rangkaian frame dan gerakkan objek/orang di lingkungan secara aman agar dapat dilihat apakah kotak dan ID mengikuti objek.
5. Periksa overlay dan pesan/CSV untuk setiap kelas. ID dapat kosong pada beberapa frame awal saat tracker mengonfirmasi objek. Setelah muncul, catat apakah ID tetap terkait dengan objek yang sama sepanjang rangkaian frame. ID hanya berlaku selama satu sesi node dan dapat berubah setelah oklusi.
6. Catat objek yang tidak terdeteksi, kelas yang salah, kotak yang melompat, ID yang sering berganti/hilang, keterlambatan kamera, error node, dan apakah ketiga kelas benar-benar diuji. Jangan mengubah threshold untuk membuat hasil terlihat lebih baik.
7. Hentikan node dengan `Ctrl-C` setelah semua kelas diperiksa. Simpan path tiga log baru yang dibuat: `<run_id>.json`, `<run_id>.csv`, dan `<run_id>_detections.csv` di `runs/op3_pytorch/`.

### Tahap 3: sesi kondisi berjalan, bila operator siap

Uji ini terpisah dan bukan prasyarat untuk memeriksa fungsi dasar kamera. Lakukan hanya jika operator memilih dan mengendalikan kondisi berjalan melalui prosedur robot yang sudah berlaku. Agen tidak boleh mengirim perintah gerak.

- Jalankan sesi baru dengan `run_id` unik dan konfigurasi model, topic, ukuran gambar, threshold, serta tracker yang sama.
- Isi `experiment_condition:=walking` hanya setelah operator memastikan robot benar-benar berjalan selama sesi; selain itu gunakan `unknown`.
- Jika operator belum menyiapkan kondisi berjalan dengan aman, lewati tahap ini dan tandai belum diukur.
- Hentikan node dengan `Ctrl-C`; jangan gabungkan log `servo_idle` dan `walking`.

### Tahap 4: periksa log dan buat laporan hasil

Untuk setiap sesi yang selesai:

1. Pastikan JSON berstatus selesai, CSV berisi frame, tidak ada collision nama `run_id`, dan CSV per deteksi mencatat nama kelas, confidence, bounding box, serta `track_id`.
2. Ringkas jumlah frame, durasi, frekuensi frame yang diproses, jumlah deteksi per kelas, jumlah ID yang teramati per kelas, confidence deskriptif, jumlah error, serta jeda timestamp kamera. Hitung hanya dari kolom yang benar-benar tersedia; sertakan skrip/perintah dan path sumber setiap angka.
3. Periksa ID per kelas pada rangkaian frame. Bedakan ID kosong pada fase konfirmasi awal dari ID yang hilang di tengah urutan. Jangan menyimpulkan tracking baik hanya dari adanya ID; tinjau juga overlay atau keluaran frame secara kronologis.
4. Catat temuan ke laporan sesi baru di `analisis_performa/` atau dokumentasi runtime tanpa mengubah log mentah. Perbarui T18/T22/T25 hanya jika kolom dan kondisi yang dibutuhkan benar-benar tersedia. Beri label hasil ini sebagai observasi runtime, bukan akurasi.
5. Bila data atau bukti visual tidak cukup, tulis `[BELUM DIVERIFIKASI]` dan jelaskan apa yang kurang. Jangan mengarang angka atau menganggap kelas terdeteksi hanya dari uji offline.

### Hasil yang harus dilaporkan

Laporkan secara ringkas:

1. Commit/versi repository dan hash checkpoint yang diuji.
2. Lingkungan OP3, nama topic kamera aktual, konfigurasi runtime, serta kondisi sesi yang terverifikasi.
3. Untuk masing-masing `ball`, `gawang`, dan `robot`: apakah muncul di gambar kamera, apakah kelas/kotaknya benar menurut pemeriksaan operator, apakah ID tracking muncul, dan apakah ID mengikuti objek pada urutan frame.
4. Path log JSON/CSV, ringkasan metrik yang bisa dihitung, error, dan bukti yang belum tersedia.
5. Kesimpulan terpisah untuk sesi `servo_idle` dan `walking`; sesi yang dilewati tetap `[BELUM DIUKUR]`.
6. Langkah setelah uji operasional: lanjut ke Fase B pada `PROMPT_PERBAIKAN_KODE_DAN_ANALISIS_PERFORMA.md`, yaitu diagnosis objective KD pada split VAL dan usulan mode loss pure KD untuk dibahas pada TH-B. Jangan mulai training baru sebelum titik keputusan berikutnya disetujui.

Mulai dari Tahap 1. Berhenti pada titik berhenti jika ada prasyarat yang gagal dan laporkan bukti terminalnya.
