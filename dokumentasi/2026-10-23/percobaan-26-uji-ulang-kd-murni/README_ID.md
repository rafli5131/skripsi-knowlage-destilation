# Percobaan 26 — Uji ulang KD murni pada OP3

**Status: selesai.** Sesi mencakup pengukuran idle, gait berjalan, dan tracking bola bergerak. Preview deteksi KD murni tetap dinyalakan setelah pengujian.

## Hasil per sesi

| Sesi | Hasil utama | Dokumentasi |
|---|---|---|
| Idle | 60,27 detik; 839 frame ukur; 13,94 FPS; latensi callback P50 46,87 ms dan P95 159,14 ms; 0 error frame. | [Laporan, grafik, tabel, dan screenshot](01-idle/README_ID.md) · [English](01-idle/README_EN.md) |
| Berjalan | 57 detik gait terverifikasi; 675 frame; 11,84 FPS; latensi callback P50 59,05 ms dan P95 167,24 ms; 0 error frame. | [Laporan, grafik, tabel, telemetry, dan screenshot](02-berjalan/README_ID.md) · [English](02-berjalan/README_EN.md) |
| Tracking bola | 29,84 detik; 357 frame; 11,93 FPS; bola muncul pada 353/357 frame (98,9%); 3 ID track bola dan 2 pergantian ID. | [Laporan, grafik lintasan, tabel, dan screenshot](03-tracking/README_ID.md) · [English](03-tracking/README_EN.md) |

## Konfigurasi dan batas interpretasi

Semua sesi memakai model KD murni `kd_seed42` (`models/weights/kd_student_best.pt`, SHA-256 `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3`), kamera `/thesis/image_raw` 640×480, CPU FP32, confidence 0,25, IoU 0,45, dan tracker BoT-SORT. Preview SSH-X dipublikasikan pada `/vision/debug_image`.

Angka deteksi dan confidence adalah keluaran model pada adegan yang diuji, **bukan akurasi**; tidak tersedia ground truth per frame untuk menghitung precision, recall, F1, mAP, atau akurasi tracking. Sesi idle dan berjalan juga tidak sepenuhnya sebanding: `op3_manager` tidak aktif saat pengukuran idle, sedangkan manager aktif ketika robot berjalan. Uji tracking hanya mencatat kondisi fisik robot sebagai `unknown`; tidak ada perintah gait atau servo selama sesi itu. Run walking pertama disimpan sebagai bukti diagnostik, tetapi tidak dipakai karena mapping modul sendi belum aktif.

## Berkas data mentah

- Idle: log runtime (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_idle_retest_01.csv`) · log deteksi (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_idle_retest_01_detections.csv`) · metadata (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_idle_retest_01.json`)
- Berjalan: log runtime (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_walking_retest_02.csv`) · log deteksi (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_walking_retest_02_detections.csv`) · metadata (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_walking_retest_02.json`)
- Tracking: log runtime (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_tracking_moving_ball_01.csv`) · log deteksi (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_tracking_moving_ball_01_detections.csv`) · metadata (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_tracking_moving_ball_01.json`)

Preview live pascauji masih berjalan dengan run `20261023_kd_pure_live_preview_post_tracking_01`; run pemantauan ini tidak dimasukkan ke hasil benchmark. Metadata preview (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_live_preview_post_tracking_01.json`).
