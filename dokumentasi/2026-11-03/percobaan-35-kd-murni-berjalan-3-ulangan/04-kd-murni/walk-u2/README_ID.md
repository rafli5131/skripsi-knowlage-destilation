# KD murni berjalan — ulangan 2

Run `20261103_eq_kd42_walk_u2` dilakukan setelah konfirmasi operator dengan preview SSH-X aktif. Gait menerima ack mulai 10:22:44 UTC dan berhenti 10:23:47 UTC. ID 19/20 tidak diberi perintah posisi; guard mencatat simpangan maksimum satu count.

Jendela ukur 60 detik berisi **731 frame tanpa error**. Latensi rata-rata/P95 **73,39/162,35 ms**, FPS **12,17**, CPU proses **1296,56% satu CPU logis**, RSS **355,69 MiB**. Status `lulus_cek_otomatis`; audit protokol akhir masih diperlukan. [Tabel deteksi](tabel_deteksi.csv) mencatat keluaran model, bukan akurasi berlabel.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah](frame_deteksi_sesudah_jendela.png), [ringkasan](summary_metrics.json), [guard gait](gait_guard.json), [tabel performa](tabel_performa.csv), [grafik runtime](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [telemetry sebelum](telemetry_pre.txt), [sesudah](telemetry_after.txt), [sesudah kedua](telemetry_after2.txt), serta [sampel kepala dan kaki](head_guard_samples.csv). Log mentah lokal: `runs/op3_pytorch/20261103_eq_kd42_walk_u2.*`.
