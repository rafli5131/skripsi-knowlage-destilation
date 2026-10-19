# OP3 Live Monitor (SSH X11)

Paket ROS 2 baru ini membaca `/thesis/image_raw` sebagai subscriber `reliable`, menjalankan checkpoint KD seed 42 di CPU FP32 dengan BoT-SORT, lalu membuka **jendela OpenCV langsung melalui SSH -X**. Paket ROS lama tidak diubah. Tidak ada perintah gerak robot dan tidak ada penyimpanan gambar/video.

Di jendela, kotak menunjukkan kelas, ID tracking, dan confidence. Confidence bukan akurasi live; akurasi live memerlukan anotasi ground truth. Baris `TEST offline` menampilkan precision, recall, F1, mAP50, dan mAP50-95 dari hasil pengujian tersimpan yang cocok dengan hash checkpoint. Grafik berjalan menampilkan FPS, latensi inferensi, CPU proses, dan RAM proses; metrik lain ada di panel kanan. CPU proses dapat melebihi 100% karena dihitung relatif terhadap satu inti logis.

Jalankan dari **terminal SSH -X yang memiliki `$DISPLAY`**, setelah publisher kamera aktif:

```bash
cd /home/humanoid/bre_skripsi
source /opt/ros/jazzy/setup.bash
source /home/humanoid/ros2_jazzy/install/setup.bash
source .venv-op3-pytorch/bin/activate
export PYTHONPATH="$PWD/ros2_packages/op3_live_monitor:$PYTHONPATH"
python -m op3_live_monitor.monitor --topic /thesis/image_raw
```

Tekan `q`/Esc atau tutup jendela untuk berhenti. Opsi: `--imgsz`, `--conf`, `--iou`. Bila `$DISPLAY` kosong, periksa X11 forwarding pada koneksi SSH.
