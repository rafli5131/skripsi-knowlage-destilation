# KD murni seed 42 — idle ulangan 2

Run `20261103_eq_kd42_idle_u2` menggunakan kamera, checkpoint, threshold, BoT-SORT, thread, warm-up dan preview yang sama seperti ulangan 1. Tidak ada perintah gerak robot. Jendela ukur 60 detik berisi 721 frame tanpa error.

Latensi rata-rata/P95 **74,60/163,53 ms**, FPS **12,04**, CPU proses **1301,98% satu CPU logis**, dan RSS **357,65 MiB**. Deviasi kepala dan badan pada sampel masing-masing satu count. Status `lulus_cek_otomatis`; audit akhir masih terbuka. Ketiga kelas memiliki keluaran pada 721/721 frame; ini cakupan prediksi, bukan akurasi berlabel.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah](frame_deteksi_sesudah_jendela.png), [telemetry](telemetry_pre.txt), [ringkasan](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), dan [grafik runtime](grafik_runtime_hd.png). Log mentah lokal: `runs/op3_pytorch/20261103_eq_kd42_idle_u2.*`.
