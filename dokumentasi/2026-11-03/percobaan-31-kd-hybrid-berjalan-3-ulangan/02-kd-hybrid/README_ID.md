# KD Hybrid full seed 1337 — tiga ulangan berjalan

Pengukuran 3 November 2026 memakai kamera C920 OP3 640×480, CPU FP32, BoT-SORT, confidence 0,25, IoU NMS 0,45, empat thread intra-op dan dua inter-op, 30 frame warm-up, jendela ukur 60 detik, serta preview SSH-X aktif. `op3_manager` memakai `auto_start_init_pose=false`; modul kepala tetap `none`. Hanya sendi kaki/badan yang didukung memakai `walking_module`, tanpa perintah posisi ke ID 19/20. Operator mengonfirmasi walk-ready, area kosong, dan pendampingan sebelum **setiap** run. Jeda sejak stop gait sebelumnya lebih dari 120 detik.

| Ulangan | Frame | Latensi rata-rata (ms) | P95 (ms) | FPS efektif | CPU proses (% satu CPU logis) | RSS (MiB) | Gawang ada pada frame |
|---|---:|---:|---:|---:|---:|---:|---:|
| [1](walk-u1/README_ID.md) | 772 | 68,37 | 158,92 | 12,87 | 1299,77 | 358,13 | 721/772 (93,4%) |
| [2](walk-u2/README_ID.md) | 758 | 71,72 | 160,74 | 12,64 | 1307,51 | 354,03 | 745/758 (98,3%) |
| [3](walk-u3/README_ID.md) | 726 | 74,32 | 161,78 | 12,12 | 1304,03 | 356,76 | 717/726 (98,8%) |

Rerata ± simpangan baku sampel dari **tiga angka per-run**: latensi **71,47 ± 2,98 ms**, FPS **12,54 ± 0,38**, CPU **1303,77 ± 3,88%** dari satu CPU logis, RSS **356,31 ± 2,09 MiB**. Total 2.256 frame ukur. Bola dan robot muncul pada 2.256/2.256 frame; gawang pada 2.183/2.256 (**96,8%**). Angka cakupan ini adalah **keluaran model, bukan precision/recall/mAP**. Ketiga run tanpa error frame, gap terbesar antarpenerimaan frame masing-masing 0,556/0,519/0,539 detik. Ketiga gait menerima ack stop; deviasi kepala maksimum satu count.

[Grafik tiga ulangan 2880×1800](grafik_hybrid1337_walk_ulangan_1_2_3_hd.png) dan [grafik cakupan/confidence 2700×1080](grafik_cakupan_confidence_hybrid1337_walk_hd.png) memberi label sumbu berbahasa Indonesia. [Tabel tiga run](../05-ringkasan/tabel_3_run.csv) dan [agregat](../05-ringkasan/tabel_agregat_saat_ini.csv) menyimpan angka penuh. [Matriks lintas hari 12/24](../../../2026-11-02/percobaan-30-uji-live-setara-empat-model/05-ringkasan/tabel_24_run.csv) menggabungkan run ini dengan sembilan run 2 November.

**Batas audit:** ulangan 1 memakai snapshot prajalan dari enam sendi yang tercatat guard, bukan JointState penuh; lihat [provenance](walk-u1/telemetry_pre_provenance.json). Ulangan 2/3 mempunyai JointState prajalan 20 sendi. Suhu CPU pra-run dibaca dari `/sys/class/thermal`, tetapi suhu servo kepala tidak dipantau selama gait dan tegangan OpenCR hanya diukur saat persiapan. Preview tidak direkam sebagai video layar; kelancaran didukung oleh frame CSV segar, gap antarframe, dan viewer yang tetap terbuka. Status `lulus_cek_otomatis` menyatakan cek data, bukan pengesahan akhir kesetaraan adegan atau protokol.
