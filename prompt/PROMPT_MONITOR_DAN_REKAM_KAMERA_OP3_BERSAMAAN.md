# Prompt gabungan: monitor deteksi live dan rekam frame kamera OP3

> Gunakan prompt ini bila ingin **melihat deteksi dan tracking secara langsung sambil mengumpulkan frame mentah**. Kedua proses berlangganan topic kamera yang sama pada waktu bersamaan. Pra-label dilakukan setelah perekaman selesai; peninjauan manusia tetap wajib sebelum menghitung akurasi.

## Prompt siap pakai

Bertindak sebagai engineer ROS 2 pada ROBOTIS OP3. Dari root repository `bre`, jalankan satu sesi kamera yang memperlihatkan kotak deteksi dan ID tracking untuk `ball`, `gawang`, serta `robot`, sekaligus menyimpan sampel frame kamera mentah untuk anotasi. Gunakan checkpoint student KD `models/weights/kd_student_best.pt` (alias `op3_default`) dan konfigurasi yang tercatat di repository. Jangan mengirim perintah servo/gait/motor. Operator robot menentukan dan memverifikasi kondisi `servo_idle` atau `walking`; bila tidak pasti, pakai `unknown`.

### 1. Prasyarat

Pastikan repository pada OP3 sudah memuat `scripts/op3_pytorch_detector.py`, `scripts/view_op3_debug_image.py`, `scripts/capture_op3_frames.py`, dan `scripts/prelabel_op3_frames.py`. Catat commit dan cek bahwa working tree tidak mempunyai perubahan yang memengaruhi runtime. Aktifkan publisher kamera melalui prosedur OP3 yang sudah berlaku, lalu periksa topic yang benar:

```bash
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
ros2 topic list
ros2 topic info /thesis/image_raw
ros2 topic hz /thesis/image_raw
sha256sum models/weights/kd_student_best.pt
```

Bandingkan SHA-256 dengan `configs/model_registry.yaml`; kelas wajib `0: ball`, `1: gawang`, `2: robot`. Ganti `/thesis/image_raw` dalam semua perintah di bawah hanya jika topic aktual berbeda. Jangan membuka kamera kedua atau menjalankan dua publisher untuk perangkat kamera yang sama. Jika topic, checkpoint, ROS, atau dependency tidak tersedia, berhenti dan laporkan bukti kegagalannya.

### 2. Jalankan tiga terminal secara bersamaan

Semua terminal berada di root repository dan memakai environment ROS serta venv yang sama. **Terminal A — detektor dan tracker**. Gunakan `run_id` baru agar tidak menimpa log lama:

```bash
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
python scripts/op3_pytorch_detector.py --ros-args \
  -p input_topic:=/thesis/image_raw \
  -p run_id:=20261022_idle_01_live \
  -p experiment_condition:=servo_idle \
  -p model_variant:=kd \
  -p imgsz:=640 \
  -p confidence_threshold:=0.25 \
  -p iou_threshold:=0.45 \
  -p enable_tracking:=true \
  -p tracker_config:=botsort.yaml \
  -p log_detections:=true \
  -p publish_debug_image:=true
```

**Terminal B — jendela pemantau**. Jalankan di desktop robot atau terminal SSH dengan X11 forwarding dan `$DISPLAY` tersedia. Penampil ini hanya membaca `/vision/debug_image`; ia **tidak menjalankan inferensi kedua**:

```bash
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
python scripts/view_op3_debug_image.py --topic /vision/debug_image
```

Pastikan jendela benar-benar menampilkan gambar beranotasi dan ID pada objek yang terlacak. Tekan `q` atau Esc untuk menutup jendela. Jika `$DISPLAY` tidak tersedia, buka viewer dari desktop/SSH X11 yang berfungsi; deteksi dan capture dapat tetap berlangsung, tetapi jangan klaim monitoring visual berhasil.

**Terminal C — rekam frame mentah dari topic kamera asli**, bukan dari `/vision/debug_image`. Jalankan setelah tampilan live terbukti berjalan, memakai `session_id` baru yang sesuai dengan `run_id`:

```bash
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
python scripts/capture_op3_frames.py \
  --session-id 20261022_idle_01 \
  --condition servo_idle \
  --topic /thesis/image_raw \
  --max-frames 120 \
  --interval-sec 1 \
  --duration-sec 300
```

Sesuaikan tanggal dan nomor sesi dengan waktu pelaksanaan. Jika operator belum memastikan status servo, ubah **keduanya** menjadi `unknown`. Untuk kondisi berjalan, gunakan sesi lain, misalnya `20261022_walking_01`, hanya ketika operator siap dan memverifikasi robot berjalan. Agen tidak boleh menggerakkan robot.

Selama sesi, hadirkan ketiga kelas, variasikan jarak/posisi/cahaya/oklusi, dan sertakan frame tanpa target. Periksa apakah kelas dan kotak sesuai objek serta ID mengikuti objek pada frame berturutan. Catat objek yang terlewat, kelas salah, ID yang berpindah/hilang, dan gangguan kamera. Capture tidak memilih frame berdasarkan keberhasilan prediksi.

### 3. Akhiri sesi dan buat pra-label

Setelah Terminal C selesai, hentikan detektor di Terminal A dengan `Ctrl-C` agar metadata log berstatus selesai. Tutup jendela Terminal B. Jangan hapus hasil sesi. Jalankan pra-label **setelah** sesi live selesai supaya inferensi pra-label tidak menambah beban CPU saat monitoring:

```bash
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
python scripts/prelabel_op3_frames.py \
  --session-id 20261022_idle_01 \
  --model models/weights/kd_student_best.pt \
  --imgsz 640 --conf 0.25 --iou 0.45
```

Jika ingin memakai teacher untuk pra-label, pindahkan folder sesi ke lab/server sesuai prosedur operator dan gunakan path checkpoint teacher di `configs/model_registry.yaml`. Jangan menimpa `labels_auto/` dari model lain.

Hasil berada di:

```text
runs/op3_pytorch/20261022_idle_01_live.json          # metadata runtime
runs/op3_pytorch/20261022_idle_01_live.csv           # log frame detektor
runs/op3_pytorch/20261022_idle_01_live_detections.csv
data/op3_camera_eval/sessions/20261022_idle_01/images/
data/op3_camera_eval/sessions/20261022_idle_01/labels_auto/
data/op3_camera_eval/sessions/20261022_idle_01/labels_reviewed/  # dibuat setelah pemeriksaan manusia
```

`labels_auto/` adalah prediksi draf, bukan ground truth. Periksa **setiap** gambar, termasuk file label kosong; perbaiki objek terlewat, kelas, dan kotak, lalu simpan hasilnya di `labels_reviewed/`. Jangan menghitung mAP, precision, recall, atau F1 dari label otomatis yang belum ditinjau.

### 4. Batas interpretasi dan laporan

Tiga subscriber/proses aktif dapat menambah beban CPU dan mengubah FPS/latensi. Log detektor sesi gabungan dipakai untuk memeriksa fungsi, bukan angka benchmark OP3 yang dibandingkan dengan model lain. Untuk tabel performa runtime, lakukan sesi pengukuran terpisah dengan beban proses dan protokol yang dikunci. Detektor juga dapat melewatkan frame yang masih tertangkap perekam; jangan menganggap satu baris log detektor mewakili setiap JPEG. Akurasi frame OP3 dihitung kemudian dari inferensi pada frame tersimpan dengan `labels_reviewed` yang sudah diperiksa.

Laporkan commit, hash checkpoint, topic kamera, kondisi fisik yang diverifikasi, `run_id`, `session_id`, jumlah frame dan tiga kelas yang benar-benar tampil, hasil monitoring kelas/ID, path log/gambar/label, status review label, serta error. Tandai bagian yang belum dilakukan sebagai `[BELUM DIUKUR]`. Jangan melakukan `git commit`, `git push`, atau mengunggah gambar/video/log robot dari sesi ini.
