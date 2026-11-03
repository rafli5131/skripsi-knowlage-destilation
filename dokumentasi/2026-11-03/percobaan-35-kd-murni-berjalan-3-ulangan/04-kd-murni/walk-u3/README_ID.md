# KD murni berjalan — ulangan 3

> Run ini disimpan sebagai riwayat; [penggantinya](../walk-u3-ulang1/README_ID.md) menjadi slot aktif setelah lulus cek otomatis.

Run `20261103_eq_kd42_walk_u3` dilakukan setelah konfirmasi operator dengan preview SSH-X aktif. Gait menerima ack mulai 10:26:20 UTC dan berhenti 10:27:23 UTC. ID 19/20 tidak diberi perintah posisi; guard mencatat simpangan maksimum satu count.

Jendela ukur 60 detik berisi **727 frame tanpa error**. Latensi rata-rata/P95 **74,07/161,28 ms**, FPS **12,12**, CPU proses **1297,81% satu CPU logis**, RSS **356,21 MiB**. Status otomatis **`perlu_audit`** karena dua sampel kaki terdekat detik ke-20 dan ke-40 berbeda maksimal 0,01687 rad dari baseline, di bawah ambang 0,03 rad.

Pemeriksaan 60 sampel guard selama jendela gait menunjukkan rentang `l_knee` **0,6630 rad** dan `r_knee` **0,6688 rad**, dengan simpangan maksimum dari baseline masing-masing 0,4850 dan 0,4893 rad. Ini merupakan bukti gerak sendi selama jendela, sedangkan dua sampel yang dipakai pemeriksaan otomatis berdekatan dengan posisi awal. Penjelasan fase langkah adalah dugaan; status otomatis dipertahankan hingga audit protokol memutuskan validitas run.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah](frame_deteksi_sesudah_jendela.png), [ringkasan](summary_metrics.json), [guard gait](gait_guard.json), [sampel kepala dan kaki](head_guard_samples.csv), [telemetry sebelum](telemetry_pre.txt), [sesudah](telemetry_after.txt), [sesudah kedua](telemetry_after2.txt), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), dan [grafik runtime](grafik_runtime_hd.png). Keluaran deteksi bukan akurasi berlabel. Log mentah lokal: `runs/op3_pytorch/20261103_eq_kd42_walk_u3.*`.
