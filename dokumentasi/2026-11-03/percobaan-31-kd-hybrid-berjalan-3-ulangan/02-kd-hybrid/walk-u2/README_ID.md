# KD Hybrid berjalan — ulangan 2 (3 November 2026)

Checkpoint dan parameter inferensi sama dengan ulangan 1. Preview SSH-X diperiksa sebelum gait: frame terbaru masuk tanpa error dan bola, gawang, serta robot muncul pada 50/50 frame. Gait mendapat ack start **05:08:07,795 UTC** dan ack stop **05:09:10,810 UTC**. Kepala ID 19/20 tetap pada modul `none`, tanpa perintah posisi; deviasi maksimum **1 count**. Status CSV/telemetry: `lulus_cek_otomatis`.

| Frame ukur | Latensi rata-rata | P95 | FPS efektif | CPU proses | RSS | Output gawang |
|---:|---:|---:|---:|---:|---:|---:|
| 758 | 71,72 ms | 160,74 ms | 12,64 | 1307,51% dari satu CPU logis | 354,03 MiB | 745/758 frame (98,3%) |

Bola dan robot muncul pada 758/758 frame. Jeda terbesar antarframe 0,519 detik dan tidak ada error frame. Output kelas **bukan ukuran akurasi**. Bukti: [overlay](frame_deteksi_sesudah_jendela.png), [grafik runtime HD](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [grafik kelas](grafik_keluaran_kelas_id.png), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [telemetry sebelum](telemetry_pre.txt) dan [sesudah stop](telemetry_after.txt), [ringkasan](summary_metrics.json), serta [guard gait](gait_guard.json). Log mentah lokal: `runs/op3_pytorch/20261103_eq_hybrid1337_walk_u2.*`.
