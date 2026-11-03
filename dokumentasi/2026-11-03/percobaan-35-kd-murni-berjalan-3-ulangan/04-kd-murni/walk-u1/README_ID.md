# KD murni berjalan — ulangan 1

Run `20261103_eq_kd42_walk_u1` dilakukan setelah konfirmasi operator dengan preview SSH-X aktif, kamera OP3 640×480, CPU FP32 dan BoT-SORT. Gait menerima ack mulai 10:19:05 UTC dan berhenti 10:20:08 UTC. ID 19/20 tidak diberi perintah posisi; guard mencatat simpangan maksimum satu count.

Jendela ukur 60 detik berisi **725 frame tanpa error**. Latensi rata-rata/P95 **74,75/162,51 ms**, FPS **12,10**, CPU proses **1296,29% satu CPU logis**, RSS **365,05 MiB**. Status `lulus_cek_otomatis`; audit protokol akhir masih diperlukan. [Tabel deteksi](tabel_deteksi.csv) mencatat keluaran model, bukan akurasi berlabel.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah](frame_deteksi_sesudah_jendela.png), [ringkasan](summary_metrics.json), [guard gait](gait_guard.json), [tabel performa](tabel_performa.csv), [grafik runtime](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [telemetry sebelum](telemetry_pre.txt), [sesudah](telemetry_after.txt), [sesudah kedua](telemetry_after2.txt), serta [sampel kepala dan kaki](head_guard_samples.csv). Log mentah lokal: `runs/op3_pytorch/20261103_eq_kd42_walk_u1.*`.
