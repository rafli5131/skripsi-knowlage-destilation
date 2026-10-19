# Pra-uji live kamera dan tracking OP3 — 2026-10-19

**Status dokumen:** catatan pra-uji dan pemulihan publisher, sebelum package percobaan baru dijalankan. Subscriber detector lama kehilangan hampir semua frame dengan QoS `best_effort`; package baru memakai subscriber `reliable`. Hasil inferensi dan tracking live berikutnya dicatat dalam `dokumentasi/2026-10-19/percobaan-04-live-tracking-servo-idle/` dan `percobaan-05-head-ball-tracking/`. Bagian di bawah mempertahankan riwayat pemeriksaan sebelum kamera aktif.

## Workspace dan runtime

- Direktori: `/home/humanoid/bre_skripsi`; branch `main`; commit `62f801048b1fcd836a80c269dd0c6d43410c03e1`.
- Perubahan lokal sebelum uji: `memory/2026-10-19.md` telah dimodifikasi; tidak disentuh oleh uji ini.
- File node, registry, konfigurasi kelas, checkpoint, requirements, dan panduan runtime yang diminta prompt tersedia.
- SHA-256 `models/weights/kd_student_best.pt`: `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3`, cocok dengan alias `op3_default` pada registry.
- Mapping pada konfigurasi dataset dan checkpoint sama: `0=ball`, `1=gawang`, `2=robot`.
- Ubuntu 24.04.5 LTS; Python 3.12.3; ROS 2 Jazzy; PyTorch 2.4.1+cpu; Ultralytics 8.4.130; OpenCV 4.11.0; psutil 7.2.2. Impor `rclpy`, `cv_bridge`, dan `vision_msgs` berhasil.
- `lap==0.5.12` semula belum terpasang. Versi itu dipasang hanya ke `.venv-op3-pytorch` melalui `uv pip install --python .venv-op3-pytorch/bin/python lap==0.5.12`; verifikasi versi sesudah pemasangan berhasil.

## Pemeriksaan kamera

Setelah memuat `/opt/ros/jazzy/setup.bash` dan overlay `/home/humanoid/ros2_jazzy/install/setup.bash`:

- `ros2 topic list -t` hanya menampilkan `/parameter_events` dan `/rosout`.
- `ros2 topic info /thesis/image_raw --verbose` menghasilkan `Unknown topic '/thesis/image_raw'`.
- `timeout 6s ros2 topic hz /thesis/image_raw` tidak menerima frame dan mencetak `WARNING: topic [/thesis/image_raw] does not appear to be published yet`.
- `ros2 node list` tidak menampilkan node aktif. Variabel `ROS_DOMAIN_ID` tidak disetel pada shell pemeriksaan.
- Saat setup overlay dimuat, ada peringatan hook `op3_advanced_detector` yang mengarah ke path build lama yang tidak ada. Penyebab tidak adanya publisher kamera belum ditentukan.

## Dampak dan langkah berikutnya

Node deteksi/tracking tidak dijalankan. Tidak ada log run JSON/CSV baru, overlay, atau pemeriksaan ID lintas frame. Ketiga kelas dan kondisi `servo_idle`/`walking` pada kode tracking terbaru berstatus **[BELUM DIVERIFIKASI]**. Tidak ada perintah servo/gait, gambar/video yang disimpan, commit, atau push dari uji ini.

Operator perlu menjalankan publisher kamera OP3 sesuai setup yang berlaku dan memastikan topic `sensor_msgs/Image` terlihat serta mengalir melalui `ros2 topic info` dan `ros2 topic hz`. Periksa domain ROS bila publisher berjalan di domain lain. Setelah kamera tersedia, ulangi tahap 1 lalu jalankan sesi idle dengan kondisi yang diverifikasi operator. Sesi walking tetap terpisah dan hanya dilakukan bila operator menyiapkannya.

## Pemeriksaan ulang pukul 17:31 WIB

Pada commit `62f8010`, status repo masih memuat perubahan lokal `memory/2026-10-19.md` dan laporan ini. Setelah environment ROS utama serta overlay dimuat, `ros2 node list` tidak menampilkan node; `ros2 topic list -t` hanya menampilkan `/parameter_events` dan `/rosout`. `ros2 topic info /thesis/image_raw --verbose` kembali menghasilkan `Unknown topic '/thesis/image_raw'`. Perintah `timeout 6s ros2 topic hz /thesis/image_raw` berakhir tanpa sampel dan mencetak `WARNING: topic [/thesis/image_raw] does not appear to be published yet`. Karena publisher kamera masih tidak tersedia, titik berhenti 1 tetap berlaku; tidak ada run atau log deteksi baru.

## Pemeriksaan ulang pukul 17:33 WIB

ROS masih hanya menampilkan `/parameter_events` dan `/rosout`; `/thesis/image_raw` tidak dikenal dan tidak menerima frame selama pemeriksaan enam detik. Pada host ini, `ls -l /dev/video*` menghasilkan `No such file or directory`, `v4l2-ctl --list-devices` menghasilkan `Cannot open device /dev/video0`, dan `lsusb` hanya menampilkan root hub, Intel AX211 Bluetooth, serta FT232H; webcam C920 tidak terdaftar. Dengan demikian perangkat kamera yang dipakai pada percobaan lama juga belum terdeteksi oleh OS pada pemeriksaan ini. Perlu memastikan kamera terhubung ke host OP3 ini, lalu memverifikasi kemunculan device dan publisher ROS sebelum menjalankan uji live. Tidak ada inferensi atau log run baru.

## Pemeriksaan ulang pukul 17:37 WIB

Webcam C920 kini terdeteksi oleh OS: `v4l2-ctl --list-devices` menampilkan `/dev/video0`, `/dev/video1`, dan `/dev/media0`; kedua device video ada. Namun `ros2 topic list -t` masih hanya menampilkan `/parameter_events` dan `/rosout`, `ros2 topic info /thesis/image_raw --verbose` menjawab `Unknown topic`, dan `timeout 6s ros2 topic hz /thesis/image_raw` tidak menerima frame. Prasyarat perangkat fisik sudah terpenuhi, sedangkan publisher ROS belum berjalan. Uji tracking tetap berhenti pada titik berhenti 1; tidak ada node inferensi atau log run baru. Langkah berikutnya adalah menjalankan publisher kamera dari setup OP3 yang berlaku dan mengonfirmasi topic gambar aktual.

## Pemulihan publisher pukul 17:39–17:48 WIB

Package `usb_cam` yang sudah terpasang dijalankan pada C920 `/dev/video0` dengan format YUYV 640×480, 30 FPS diminta, dan remap `image_raw:=/thesis/image_raw`. `ros2 topic info /thesis/image_raw --verbose` kemudian menunjukkan satu publisher `/usb_cam` bertipe `sensor_msgs/msg/Image`; satu pesan yang diterima membawa `frame_id: camera` dan encoding `rgb8`. Node melaporkan file kalibrasi `thesis_camera.yaml` belum tersedia, tetapi tetap menerbitkan gambar.

Pengukuran subscriber ROS selama 12 detik, dengan dua subscription aktif pada saat yang sama, menghasilkan **360 frame** pada QoS `reliable` dan **1 frame** pada QoS `best_effort`. Percobaan subscriber `best_effort` terpisah sebelumnya hanya menerima **2 frame dalam 12 detik**. Node `scripts/op3_pytorch_detector.py` pada commit ini memakai `ReliabilityPolicy.BEST_EFFORT` untuk topic kamera (baris 161); karena itu aliran yang diterimanya belum memadai untuk menilai tracking lintas frame. Ini adalah temuan reproduksi pada subscriber, bukan bukti kegagalan publisher. Tidak ada kode package atau konfigurasi eksperimen yang diubah, dan tidak ada log inferensi baru.
