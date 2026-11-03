# KD Hybrid berjalan — ulangan 3 (3 November 2026)

Checkpoint dan parameter inferensi sama dengan dua ulangan sebelumnya. Preview SSH-X sebelum gait menerima frame baru tanpa error; tiga objek muncul pada 50/50 frame. Gait mendapat ack start **05:11:52,970 UTC** dan ack stop **05:12:55,979 UTC**. Kepala ID 19/20 tidak diberi perintah posisi; deviasi maksimum **1 count**. Status CSV/telemetry: `lulus_cek_otomatis`.

| Frame ukur | Latensi rata-rata | P95 | FPS efektif | CPU proses | RSS | Output gawang |
|---:|---:|---:|---:|---:|---:|---:|
| 726 | 74,32 ms | 161,78 ms | 12,12 | 1304,03% dari satu CPU logis | 356,76 MiB | 717/726 frame (98,8%) |

Bola dan robot muncul pada 726/726 frame. Jeda terbesar antarframe 0,539 detik dan tidak ada error frame. Output kelas **bukan ukuran akurasi**. Bukti: [overlay](frame_deteksi_sesudah_jendela.png), [grafik runtime HD](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [grafik kelas](grafik_keluaran_kelas_id.png), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [telemetry sebelum](telemetry_pre.txt) dan [sesudah stop](telemetry_after.txt), [ringkasan](summary_metrics.json), serta [guard gait](gait_guard.json). Log mentah lokal: `runs/op3_pytorch/20261103_eq_hybrid1337_walk_u3.*`.
