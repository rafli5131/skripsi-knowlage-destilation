# KD Hybrid berjalan — ulangan 1 (3 November 2026)

Model KD Hybrid full seed 1337, kamera OP3 640×480, CPU FP32, BoT-SORT, preview SSH-X aktif, 30 frame warm-up, dan jendela ukur 60 detik. Gait mendapat ack start **05:00:43,821 UTC** dan ack stop **05:01:46,834 UTC**. ID 19/20 tidak diberi perintah posisi; deviasi maksimum kepala **1 count**. Status CSV/telemetry: `lulus_cek_otomatis`; audit protokol akhir tetap terpisah.

| Frame ukur | Latensi rata-rata | P95 | FPS efektif | CPU proses | RSS | Output gawang |
|---:|---:|---:|---:|---:|---:|---:|
| 772 | 68,37 ms | 158,92 ms | 12,87 | 1299,77% dari satu CPU logis | 358,13 MiB | 721/772 frame (93,4%) |

Bola dan robot muncul pada 772/772 frame ukur. Keluaran kelas dan confidence **bukan akurasi/precision**. Jeda terbesar antarframe yang diterima adalah 0,556 detik; viewer SSH-X tetap terbuka dan CSV terus bertambah selama run. Bukti visual: [overlay setelah jendela](frame_deteksi_sesudah_jendela.png). Grafik: [runtime HD](grafik_runtime_hd.png), [latensi](grafik_latensi_id.png), [CPU/RAM](grafik_cpu_ram_id.png), [keluaran kelas](grafik_keluaran_kelas_id.png). Data: [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [ringkasan JSON](summary_metrics.json), [guard gait](gait_guard.json), dan [sampel sendi tiap detik](head_guard_samples.csv). Log frame mentah tetap lokal pada `runs/op3_pytorch/20261103_eq_hybrid1337_walk_u1.*`.

**Catatan provenance:** [telemetry prajalan](telemetry_pre.txt) ditransformasikan dari sampel guard asli pada 05:00:21,193 UTC, sekitar 22 detik sebelum ack gait. Sampel itu memuat kepala dan empat sendi kaki, bukan seluruh 20 sendi; [metadata transformasi](telemetry_pre_provenance.json) disimpan. Dua sampel [setelah stop](telemetry_after.txt) dan [lima detik kemudian](telemetry_after2.txt) memuat JointState penuh. Perbedaan ini harus disebut saat audit akhir dan tidak boleh disajikan sebagai snapshot pra-gait 20 sendi.
