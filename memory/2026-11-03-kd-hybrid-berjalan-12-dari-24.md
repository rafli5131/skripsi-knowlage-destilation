# Memory — KD Hybrid berjalan tiga ulangan, 3 November 2026

## Status eksperimen

- Pengguna meminta preview KD Hybrid full seed 1337 melalui SSH-X, lalu **tiga ulangan berjalan** dengan konfirmasi sebelum setiap run, pemeriksaan frame baru/objek, dan dokumentasi. Model yang dimuat adalah `runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt` (hash registri `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`). Tidak ada kode package lama yang diubah.
- Ketiga gait KD Hybrid berjalan selesai pada 3 November dan memperoleh ack start/stop. Guard menghentikan gait otomatis setelah sekitar 63 detik; kepala ID 19/20 tidak diberi perintah posisi dan menyimpang paling banyak **1 encoder count**. Ketiganya berstatus `lulus_cek_otomatis` pada CSV/telemetry, sementara audit protokol akhir masih terbuka.
- Kampanye empat model × dua kondisi × tiga ulangan sekarang **12/24 slot**: teacher idle/berjalan 6, KD Hybrid idle/berjalan 6. **12 slot Supervised dan KD murni** (idle/berjalan, masing-masing tiga ulangan) belum diukur. [Matriks lintas hari](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/05-ringkasan/tabel_24_run.csv) dan [grafik 24 slot](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png) sudah diperbarui. T36/T37 final dan T38 empat model pada set OP3 berlabel identik belum ada.

## KD Hybrid berjalan: angka dan bukti

| Ulangan | Raw run ID | Frame ukur | Latensi rata-rata | FPS efektif | CPU proses | RSS | Output gawang |
|---|---|---:|---:|---:|---:|---:|---:|
| [1](../dokumentasi/2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/02-kd-hybrid/walk-u1/README_ID.md) | `20261103_eq_hybrid1337_walk_u1` | 772 | 68,37 ms | 12,87 | 1299,77% | 358,13 MiB | 721/772 |
| [2](../dokumentasi/2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/02-kd-hybrid/walk-u2/README_ID.md) | `20261103_eq_hybrid1337_walk_u2` | 758 | 71,72 ms | 12,64 | 1307,51% | 354,03 MiB | 745/758 |
| [3](../dokumentasi/2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/02-kd-hybrid/walk-u3/README_ID.md) | `20261103_eq_hybrid1337_walk_u3` | 726 | 74,32 ms | 12,12 | 1304,03% | 356,76 MiB | 717/726 |

Rerata ± simpangan baku sampel **tiga run**: latensi **71,47 ± 2,98 ms**, FPS **12,54 ± 0,38**, CPU **1303,77 ± 3,88%** dari satu CPU logis, RSS **356,31 ± 2,09 MiB**. Total 2.256 frame ukur; bola/robot muncul pada semua frame, gawang pada 2.183/2.256 (96,8%). Ini cakupan **keluaran model, bukan akurasi/precision**. [Grafik tiga run ID 2880×1800](../dokumentasi/2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/02-kd-hybrid/grafik_hybrid1337_walk_ulangan_1_2_3_hd.png) dan [tabel sumber](../dokumentasi/2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/05-ringkasan/tabel_3_run.csv) tersedia. Log CSV mentah berada di `runs/op3_pytorch/` pada checkout robot.

## Kondisi dan batas audit

- Pada awal sesi `dynamixel_power=0`; setelah operator memastikan badan/kepala ditopang, bus diaktifkan pada 12,6–12,7 V. Semua 20 servo lolos preflight baca-saja (mode posisi 3, hardware error 0, torque awal mati). Manager dimulai dengan `auto_start_init_pose=false`. Kepala tetap modul `none`, posisi tidak berubah saat startup/pemetaan; modul kaki siap untuk gait. Jangan membuka U2D2 langsung selama manager aktif.
- Preview SSH-X aktif sebelum setiap run. Ketiga objek tampak pada 50/50 frame cek masing-masing run. Maksimum gap frame yang diterima selama run 0,556/0,519/0,539 detik; nol error frame. Viewer tidak direkam sebagai video layar, jadi kontinuitas tampilan yang dilihat operator tidak diaudit frame demi frame. Setelah u3, preview KD Hybrid kembali aktif dan CSV menerima frame baru pada pemeriksaan terakhir. Gait berhenti; manager dan torque masih aktif pada akhir sesi ini. **Periksa ulang keadaan nyata saat melanjutkan.**
- Ulangan 1 tidak memiliki snapshot prajalan 20 sendi; [sampel guard enam sendi asli](../dokumentasi/2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/02-kd-hybrid/walk-u1/telemetry_pre_provenance.json) dipakai dengan provenance terbuka. Ulangan 2/3 mempunyai snapshot 20 sendi. Suhu CPU pra-run dari sysfs 80/84/75 °C; suhu servo kepala tidak dipantau selama gait, tegangan OpenCR hanya dicek saat persiapan. [Log kondisi/penyimpangan](../dokumentasi/2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/log_penyimpangan.md) wajib dibaca sebelum menafsirkan hasil.
- Run teacher dan Hybrid idle berasal dari 2 November; Hybrid berjalan 3 November. Urutan model aktual berupa blok, tidak digilir sesuai prompt. Perbandingan antarmodel dan idle–berjalan bersifat **deskriptif**, tanpa klaim kausal atau signifikansi dari tiga ulangan.

## Lanjutkan

1. Periksa kamera, preview, OpenCR, manager, head, kondisi fisik, dan operator lagi sebelum uji berikutnya. Jaga ID 19/20 tanpa perintah posisi. Dapatkan konfirmasi operator per run berjalan.
2. Ukur Supervised seed 1337 idle/berjalan dan KD murni seed 42 idle/berjalan, tiga ulangan per pasangan, dengan dokumentasi terpisah tiap run. Total tersisa 12 slot.
3. Setelah 24 slot lengkap dan audit akhir selesai, susun T36/T37. Evaluasi T38 pada 260 frame OP3 berlabel identik bersifat retrospektif; akurasi TEST resmi tetap dilaporkan terpisah dari cakupan deteksi live.
