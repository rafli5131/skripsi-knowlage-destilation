# KD Hybrid full seed 1337 — tiga ulangan idle

Ketiga run memakai checkpoint KD Hybrid full seed 1337 yang sama, kamera OP3 640×480, CPU FP32, BoT-SORT, confidence 0,25, IoU NMS 0,45, preview SSH-X aktif, 30 frame warm-up, dan jendela ukur 60 detik. Robot tanpa gait, `op3_manager` aktif, ID 19/20 tidak diberi perintah posisi. Jeda antar-run lebih dari 120 detik. Semua run lulus pemeriksaan otomatis CSV/telemetri; audit protokol akhir masih menunggu pemeriksaan kontinuitas preview dan kondisi fisik.

| Ulangan | Frame | Latensi rata-rata (ms) | P95 (ms) | FPS | CPU proses (% satu CPU) | RSS (MiB) | Gawang terdeteksi |
|---|---:|---:|---:|---:|---:|---:|---:|
| [1](idle-u1/README_ID.md) | 792 | 66,82 | 157,52 | 13,20 | 1303,85 | 358,63 | 784/792 (99,0%) |
| [2](idle-u2/README_ID.md) | 825 | 63,08 | 161,77 | 13,75 | 1302,47 | 357,76 | 816/825 (98,9%) |
| [3](idle-u3/README_ID.md) | 830 | 64,21 | 162,58 | 13,85 | 1311,58 | 360,21 | 821/830 (98,9%) |

Rerata ± simpangan baku sampel antartiga ulangan: latensi rata-rata **64,70 ± 1,92 ms**, FPS **13,60 ± 0,35**, CPU proses **1305,97 ± 4,91%** dari satu CPU logis, dan RSS **358,87 ± 1,24 MiB**. Median dan P95 latensi gabungan 2.447 frame adalah **50,53 ms** dan **161,76 ms**. Bola serta robot muncul pada semua frame; gawang pada **2.421/2.447 frame (98,9%)**. Ini adalah cakupan keluaran model, **bukan akurasi/precision berlabel**.

Lihat [grafik performa ulangan 1–3 2880×1800](grafik_hybrid1337_idle_ulangan_1_2_3_hd.png), [grafik cakupan dan confidence 2700×1080](grafik_cakupan_confidence_hybrid1337_idle_hd.png), [tabel agregat sesi](../05-ringkasan/tabel_agregat_saat_ini.csv), dan [matriks 24 run](../05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png). Grafik confidence tidak menunjukkan precision. Log mentah tetap lokal di `runs/op3_pytorch/20261102_eq_hybrid1337_idle_u{1,2,3}.*`.
