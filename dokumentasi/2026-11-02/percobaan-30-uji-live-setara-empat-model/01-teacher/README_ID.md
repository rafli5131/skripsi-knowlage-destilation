# Teacher, kondisi idle dan berjalan — set aktif

## Asal data

Tiga run idle tetap seperti sebelumnya. Set berjalan aktif mengikuti permintaan Bhre: slot ulangan 1 memakai run mentah lama 20261102_eq_teacher_walk_u3; slot 2 dan 3 memakai run baru 20261102_eq_teacher_walk_retest_u2 dan 20261102_eq_teacher_walk_retest_u3. Isi log mentah dan cap waktunya tidak diubah. Pemetaan lengkap ada di [active_run_sources.json](../active_run_sources.json); [arsip set lama](arsip-set-sebelumnya-20261102-1200/) menyimpan hasil sebelum penggantian.

## Berjalan, set aktif

Operator mendampingi robot pada pose walk-ready dengan area langkah kosong. Modul kepala pan/tilt tetap none; tidak ada perintah posisi ID 19/20. Ketiga gait menerima ack start dan stop, dan jendela ukur 60 detik berada di dalam periode berjalan. Jeda antar-run baru melebihi 120 detik.

| Slot | Sumber mentah | Frame | Latensi rata-rata (ms) | P95 (ms) | FPS | CPU proses (% satu CPU) | RSS (MiB) | Gawang terdeteksi |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [1](walk-u1/README_ID.md) | u3 set lama | 589 | 96,41 | 180,86 | 9,80 | 1329,97 | 371,36 | 561/589 (95,2%) |
| [2](walk-u2/README_ID.md) | retest_u2 | 585 | 96,75 | 181,19 | 9,75 | 1332,64 | 367,92 | 541/585 (92,5%) |
| [3](walk-u3/README_ID.md) | retest_u3 | 604 | 94,40 | 180,01 | 10,07 | 1337,99 | 377,97 | 574/604 (95,0%) |

Rerata ± simpangan baku sampel antarulangan: latensi rata-rata **95,85 ± 1,27 ms**, FPS **9,87 ± 0,17**, CPU proses **1333,54 ± 4,08%** dari satu CPU logis, dan RSS **372,42 ± 5,11 MiB**. Median dan P95 latensi gabungan 1.778 frame adalah **77,02** dan **180,66 ms**. Bola serta robot muncul pada seluruh frame; gawang pada 1.676/1.778 frame (94,3%). Ini **cakupan keluaran deteksi, bukan akurasi atau precision**.

Ketiga run berjalan lulus cek otomatis CSV dan telemetri. Simpangan kepala maksimum sekitar 1 count dari posisi awal masing-masing run; tidak ada perintah posisi kepala. [Grafik performa tiga ulangan 2880×1800](grafik_teacher_walk_ulangan_1_2_3_hd.png), [grafik cakupan dan confidence 2700×1080](grafik_cakupan_confidence_teacher_walk_hd.png), dan [tabel agregat](../05-ringkasan/tabel_agregat_saat_ini.csv) tersedia. [Catatan akurasi/precision](../05-ringkasan/CATATAN_AKURASI_PRECISION_ID.md) menjelaskan batas interpretasi. Audit akhir kontinuitas preview dan kondisi fisik tetap diperlukan.

Set berjalan aktif dipilih setelah hasil gawang set lama diketahui dan posisi gawang diatur lagi; angka cakupan 94,3% dapat lebih optimistis daripada semua run yang pernah diambil. Sertakan arsip dan aturan pemilihan ini saat menyusun laporan skripsi.

## Idle

Tiga run idle menghasilkan 1.779 frame ukur. Rerata ± simpangan baku antarulangan: latensi rata-rata **96,24 ± 3,60 ms**, FPS **9,88 ± 0,31**, CPU proses **1338,90 ± 9,65%** dari satu CPU logis, dan RSS **370,58 ± 1,29 MiB**. Lihat [idle u1](idle-u1/README_ID.md), [idle u2](idle-u2/README_ID.md), dan [idle u3](idle-u3/README_ID.md). Perbandingan idle–berjalan ini deskriptif; tiga ulangan tidak mendukung klaim signifikansi statistik.
