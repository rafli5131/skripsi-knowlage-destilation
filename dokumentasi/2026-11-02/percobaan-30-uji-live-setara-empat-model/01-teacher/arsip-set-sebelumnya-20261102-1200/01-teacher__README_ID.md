# Teacher, kondisi idle dan berjalan

Run u1, u2 pengganti, dan u3 telah direkam. U2 pertama diganti atas permintaan Bhre setelah deteksi gawang sering terlewat. Ketiga run terbaru menghasilkan deteksi ketiga kelas pada seluruh 1.779 frame jendela ukur.

| Run | Frame | Latensi rata-rata (ms) | P95 (ms) | FPS efektif | CPU proses (% satu CPU logis) | RAM RSS (MiB) | Kepala maks. (rad) | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| u1 | 584 | 98,91 | 180,21 | 9,72 | 1329,91 | 370,03 | 0 | Lulus cek otomatis; audit akhir tertunda |
| u2 pengganti | 614 | 92,15 | 181,84 | 10,24 | 1349,11 | 369,66 | 0 | Lulus cek otomatis; audit akhir tertunda |
| u3 | 581 | 97,67 | 181,73 | 9,69 | 1337,67 | 372,06 | 0,001534 | Lulus cek otomatis; audit akhir tertunda |

Rerata ± simpangan baku antarulangan: latensi rata-rata **96,24 ± 3,60 ms**, FPS efektif **9,88 ± 0,31**, CPU proses **1338,90 ± 9,65%** dari satu CPU logis, dan RSS **370,58 ± 1,29 MiB**. Ini ringkasan deskriptif tiga ulangan, bukan uji signifikansi.

Lihat [run u1](idle-u1/README_ID.md), [run u2](idle-u2/README_ID.md), [run u3](idle-u3/README_ID.md), [cek deteksi u1/u2](cek_deteksi_u1_u2.md), dan [grafik matriks 24 run](../05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png). Tidak ada klaim akurasi tanpa ground truth.

## Berjalan

Operator memastikan robot berada di lantai pada pose walk-ready, area langkah kosong, dan mendampingi setiap run. Hanya badan yang memakai `walking_module`; modul pan/tilt kepala `none`. Tidak ada perintah posisi ID 19/20. Ketiga gait menerima ack start dan stop, berlangsung sekitar 63 detik, dan jendela ukur 60 detik berada di dalam periode berjalan. Jeda antar-run melebihi 120 detik.

| Run | Frame | Latensi rata-rata (ms) | P95 (ms) | FPS efektif | CPU proses (% satu CPU logis) | RAM RSS (MiB) | Gawang terdeteksi | Kepala maks. (rad) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [u1](walk-u1/README_ID.md) | 611 | 90,88 | 181,31 | 10,19 | 1338,94 | 375,68 | 112/611 (18,3%) | 0,001534 |
| [u2](walk-u2/README_ID.md) | 574 | 98,79 | 180,36 | 9,56 | 1322,74 | 371,13 | 362/574 (63,1%) | 0,001534 |
| [u3](walk-u3/README_ID.md) | 589 | 96,41 | 180,86 | 9,80 | 1329,97 | 371,36 | 561/589 (95,2%) | 0,001534 |

Rerata ± simpangan baku sampel antarulangan: latensi rata-rata **95,36 ± 4,06 ms**, FPS **9,85 ± 0,32**, CPU proses **1330,55 ± 8,11%** dari satu CPU logis, dan RSS **372,73 ± 2,56 MiB**. Median dan P95 latensi gabungan 1.774 frame adalah **76,67 ms** dan **180,85 ms**. Bola serta robot muncul pada seluruh 1.774 frame; gawang pada 1.035 frame (58,3%). Ini adalah cakupan keluaran deteksi, bukan akurasi.

Semua run lulus cek otomatis CSV dan telemetri, dengan simpangan kepala maksimum sekitar 1 count. [Grafik tiga ulangan 2880×1800](grafik_teacher_walk_ulangan_1_2_3_hd.png) dan [grafik matriks 24 run](../05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png) tersedia. U1 tidak memiliki screenshot overlay antara akhir jendela ukur dan akhir detektor; lihat [log penyimpangan](../log_penyimpangan.md). Status akhir protokol masih memerlukan audit kontinuitas preview, suhu, dan kondisi fisik. Dengan tiga ulangan, analisis ini deskriptif tanpa klaim signifikansi statistik.

Posisi relatif gawang dan cakupan keluarannya tidak terbukti identik antarulangan, sehingga perbedaan runtime antar-run tidak boleh diatribusikan hanya pada kondisi gerak. Setelah run ketiga, pan kepala sama dengan awal run pertama; tilt berbeda 0,001534 rad (sekitar 1 count). Preview pemantauan teacher tetap aktif dan gait telah berhenti.
