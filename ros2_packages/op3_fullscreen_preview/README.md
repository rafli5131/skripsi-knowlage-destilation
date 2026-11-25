# Preview deteksi OP3 fullscreen

Penampil SSH-X untuk kamera OP3 dengan dua tampilan: **kamera dengan kotak deteksi** dan **dashboard dengan grafik realtime** FPS, latensi inferensi, CPU, serta RAM. Keduanya menampilkan kelas, confidence, dan ID tracking jika tersedia. Package ini memakai `SharedState`, `InferenceWorker`, dan grafik dari `op3_live_monitor` sebagai fungsi bersama; package lama tidak diubah. Kedua tampilan memakai **satu model dan satu aliran inferensi** pada CPU.

Tidak ada perintah servo atau gerak, dan aplikasi ini tidak merekam video. Confidence bukan akurasi. FPS dan grafik adalah pengamatan proses preview beserta inferensi, bukan hasil benchmark yang setara dengan pengujian terdahulu; encoding video dan SSH-X dapat menambah beban.

## Menjalankan

Pastikan publisher kamera sudah aktif, topik benar, dan terminal SSH memiliki `DISPLAY` dari `ssh -X`. Dari root repositori:

```bash
cd /home/humanoid/bre_skripsi
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
export PYTHONPATH="$PWD/ros2_packages/op3_fullscreen_preview:$PYTHONPATH"
python -m op3_fullscreen_preview.preview --model hybrid --topic /thesis/image_raw
```

Model dapat dipilih dengan `--model hybrid`, `--model supervised`, `--model kd`, atau `--model teacher`. Masing-masing menggunakan Hybrid full seed 1337, supervised seed 1337, KD murni seed 42, dan teacher YOLO11n yang terdaftar. Path dan SHA-256 checkpoint diverifikasi sebelum memuat model; override lokal registry digunakan bila tersedia. Untuk berpindah model, tutup aplikasi lalu jalankan kembali dengan pilihan lain.

Jendela dimulai fullscreen dengan tampilan kamera. Tekan **1** untuk kamera saja atau **2** untuk dashboard; klik dahulu jendela agar menerima tombol. Tekan **F** untuk berganti fullscreen/jendela, **Q** atau **Esc** untuk keluar. Kedua mode dapat direkam secara terpisah setelah konfirmasi operator. Untuk langsung membuka dashboard gunakan `--view dashboard`; untuk mulai berjendela, tambahkan `--windowed`. Opsi lain: `--imgsz`, `--conf`, `--iou`, dan `--reliable` untuk publisher yang memerlukan QoS reliable. Jika status tetap `MENUNGGU` atau muncul peringatan frame terhenti, periksa publisher, topik, QoS, dan error.

Untuk mengurangi beban, default menggunakan `--threads 4` untuk PyTorch dan `--preview-fps 5` sebagai batas pembaruan jendela. Ini adalah pengaturan preview, bukan protokol benchmark; pembatasan jendela berbeda dari FPS inferensi pada grafik. Sesuaikan kedua opsi bila diperlukan.

### Rekam keluaran deteksi langsung

Setelah operator mengonfirmasi perekaman, jalankan preview dengan tambahan `--record-dir <folder-baru> --record-duration 10 --record-fps 10`. Perekam menggunakan frame beranotasi dari proses inferensi yang sama dan tidak merekam desktop atau dashboard; tidak ada detektor kedua. Video, log FFmpeg, dan `recording_stats.json` disimpan dalam folder itu. Stats mencatat frame yang diulang, durasi dan status agar laju video tidak disamakan dengan laju inferensi. Jangan menganggap frame berulang sebagai frame inferensi baru. Pilih folder unik untuk setiap sesi; video lama tidak ditimpa.

Untuk rekaman layar jendela setelah operator siap, ikuti [prompt preview dan rekam layar](../../prompt/PROMPT_PREVIEW_DETEKSI_REKAM_LAYAR_SSH_X_OP3_2026-11-25.md). Jalankan rekaman secara terpisah hanya setelah konfirmasi operator.
