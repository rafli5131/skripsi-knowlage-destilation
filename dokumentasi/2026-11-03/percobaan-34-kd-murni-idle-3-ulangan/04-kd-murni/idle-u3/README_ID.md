# KD murni seed 42 — idle ulangan 3

Run `20261103_eq_kd42_idle_u3` memakai parameter dan preview sama dengan ulangan sebelumnya, tanpa perintah gerak robot. Jendela ukur 60 detik berisi 723 frame tanpa error. Latensi rata-rata/P95 **74,78/163,25 ms**, FPS **12,05**, CPU proses **1301,21% satu CPU logis**, dan RSS **362,52 MiB**. Deviasi kepala dan badan pada sampel masing-masing satu count. Status `lulus_cek_otomatis`; audit akhir masih terbuka.

Ketiga kelas memiliki keluaran pada 723/723 frame; ini cakupan prediksi, bukan akurasi berlabel. Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah](frame_deteksi_sesudah_jendela.png), [telemetry](telemetry_pre.txt), [ringkasan](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), dan [grafik runtime](grafik_runtime_hd.png). Log mentah lokal: `runs/op3_pytorch/20261103_eq_kd42_idle_u3.*`.
