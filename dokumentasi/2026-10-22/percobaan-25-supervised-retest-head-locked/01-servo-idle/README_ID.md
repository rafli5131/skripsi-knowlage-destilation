# Uji Supervised — robot diam, torque aktif

Run 20261022_supervised_retest_head_held_idle_01 merekam 724 frame ukur selama 60.03 detik setelah 30 frame warm-up. Throughput efektif 12.06 FPS; error frame 0. Preview SSH-X aktif.

Contoh deteksi langsung (lokal: `frame_deteksi.png`)

## Performa runtime

| Metrik | Median | P95 | Satuan |
|---|---:|---:|---|
| Pra-pemrosesan | 3.65 | 12.91 | ms/frame |
| Inferensi | 30.82 | 135.23 | ms/frame |
| Pascapemrosesan | 0.80 | 1.02 | ms/frame |
| Callback end-to-end | 52.13 | 163.95 | ms/frame |
| CPU proses | 1253.50 | 1388.11 | % satu CPU logis |
| CPU host (16 CPU logis) | 78.34 | 86.76 | % kapasitas host |
| RAM RSS | 362.99 | 365.69 | MiB |

![Grafik performa per frame](grafik_performa.png)

## Keluaran deteksi

| Kelas | Frame terdeteksi | Cakupan | Median confidence | ID tracker |
|---|---:|---:|---:|---|
| Bola | 724/724 | 100.0% | 0.847 | 1 |
| Gawang | 724/724 | 100.0% | 0.365 | 3 |
| Robot | 724/724 | 100.0% | 0.642 | 2 |

![Cakupan deteksi per kelas](grafik_deteksi.png)

Cakupan dan confidence adalah keluaran model, bukan akurasi. Tidak tersedia ground truth frame untuk menghitung precision, recall, F1, atau mAP.

## Servo kepala

Torque ID19/20 aktif dan Goal/Present register cocok pada preflight sebelum manager. Manager dijalankan dengan auto_start_init_pose=false; tidak ada perintah Goal_Position atau pose kepala sepanjang sesi. Feedback ROS selama sesi berada dekat pembacaan awal. Rinciannya ada pada [telemetry kepala](../head_pose_telemetry.json) dan [tabel status kepala](../tabel_status_kepala.csv).

## Konfigurasi dan sumber

- Kondisi: Diam, gait off; waktu: 23:49:05 WIB–23:50:08 WIB.
- Model: supervised_seed1337; CPU FP32; PyTorch 2.4.1+cpu; Ultralytics 8.4.130.
- Kamera 640×480 dari /thesis/image_raw; imgsz 640; confidence 0,25; IoU 0,45; BoT-SORT; 4 intra-op dan 2 inter-op.
- [Ringkasan JSON](summary_metrics.json) · [tabel runtime](tabel_performa.csv) · [tabel deteksi](tabel_deteksi_per_kelas.csv).
- CSV frame mentah (lokal: `../../../../runs/op3_pytorch/20261022_supervised_retest_head_held_idle_01.csv`) · CSV deteksi/ID (lokal: `../../../../runs/op3_pytorch/20261022_supervised_retest_head_held_idle_01_detections.csv`) · metadata run (lokal: `../../../../runs/op3_pytorch/20261022_supervised_retest_head_held_idle_01.json`).
- Video tidak direkam; bukti visual berupa frame anotasi dan data kontinu pada CSV.
