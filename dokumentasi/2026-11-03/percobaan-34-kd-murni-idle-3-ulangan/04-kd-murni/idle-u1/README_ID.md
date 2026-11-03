# KD murni seed 42 — idle ulangan 1

Run `20261103_eq_kd42_idle_u1` menggunakan kamera OP3 640×480, CPU FP32, BoT-SORT, confidence 0,25, IoU 0,45, 30 frame warm-up dan preview SSH-X. Tidak ada perintah gerak robot.

Jendela ukur 60 detik berisi 728 frame tanpa error. Latensi rata-rata/P95 **72,90/164,94 ms**, FPS **12,13**, CPU proses **1297,43% satu CPU logis**, dan RSS **350,73 MiB**. Deviasi kepala dan badan pada sampel masing-masing satu count. Status `lulus_cek_otomatis`; audit protokol akhir masih terbuka. Ketiga kelas memiliki keluaran pada 728/728 frame, yang merupakan cakupan prediksi dan bukan akurasi berlabel.

[Overlay sebelum](preview_sebelum_run.png), [overlay sesudah](frame_deteksi_sesudah_jendela.png), [telemetry sebelum](telemetry_pre.txt), [ringkasan](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), dan [grafik runtime](grafik_runtime_hd.png) tersedia. Log mentah lokal: `runs/op3_pytorch/20261103_eq_kd42_idle_u1.*`.
