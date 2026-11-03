# T36 — Runtime live OP3 per run

Status: 24 log dan telemetry lulus cek terukur; pengguna menerima hasil untuk analisis deskriptif dengan keterbatasan. Persetujuan pembimbing belum dicatat dan kesetaraan fisik belum terbukti. CSV menyimpan hash sumber dan waktu UTC. Lihat [audit dan keputusan](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md).

Enam run yang diganti atau tidak aktif dicantumkan secara terpisah dalam [lampiran](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/T36_lampiran_run_tidak_aktif.csv); angka mereka tidak masuk agregat aktif.

| Model | Kondisi | Ulangan | Frame | Latensi rata-rata (ms) | P95 (ms) | FPS | CPU (% satu CPU logis) | RSS (MiB) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| teacher | idle | 1 | 584 | 98.91 | 180.21 | 9.72 | 1329.91 | 370.03 |
| teacher | idle | 2 | 614 | 92.15 | 181.84 | 10.24 | 1349.11 | 369.66 |
| teacher | idle | 3 | 581 | 97.67 | 181.73 | 9.69 | 1337.67 | 372.06 |
| hybrid1337 | idle | 1 | 792 | 66.82 | 157.52 | 13.20 | 1303.85 | 358.63 |
| hybrid1337 | idle | 2 | 825 | 63.08 | 161.77 | 13.75 | 1302.47 | 357.76 |
| hybrid1337 | idle | 3 | 830 | 64.21 | 162.58 | 13.85 | 1311.58 | 360.21 |
| sup1337 | idle | 1 | 719 | 74.48 | 161.82 | 12.00 | 1300.69 | 354.96 |
| sup1337 | idle | 2 | 749 | 69.39 | 158.52 | 12.47 | 1295.37 | 359.63 |
| sup1337 | idle | 3 | 717 | 75.48 | 161.49 | 11.94 | 1301.47 | 353.19 |
| kd42 | idle | 1 | 728 | 72.90 | 164.94 | 12.13 | 1297.43 | 350.73 |
| kd42 | idle | 2 | 721 | 74.60 | 163.53 | 12.04 | 1301.98 | 357.65 |
| kd42 | idle | 3 | 723 | 74.78 | 163.25 | 12.05 | 1301.21 | 362.52 |
| teacher | walk | 1 | 589 | 96.41 | 180.86 | 9.80 | 1329.97 | 371.36 |
| teacher | walk | 2 | 585 | 96.75 | 181.19 | 9.75 | 1332.64 | 367.92 |
| teacher | walk | 3 | 604 | 94.40 | 180.01 | 10.07 | 1337.99 | 377.97 |
| hybrid1337 | walk | 1 | 772 | 68.37 | 158.92 | 12.87 | 1299.77 | 358.13 |
| hybrid1337 | walk | 2 | 758 | 71.72 | 160.74 | 12.64 | 1307.51 | 354.03 |
| hybrid1337 | walk | 3 | 726 | 74.32 | 161.78 | 12.12 | 1304.03 | 356.76 |
| sup1337 | walk | 1 | 742 | 71.65 | 161.84 | 12.36 | 1296.41 | 361.63 |
| sup1337 | walk | 2 | 794 | 67.77 | 159.98 | 13.23 | 1307.93 | 362.18 |
| sup1337 | walk | 3 | 739 | 72.99 | 161.70 | 12.31 | 1299.04 | 353.68 |
| kd42 | walk | 1 | 725 | 74.75 | 162.51 | 12.10 | 1296.29 | 365.05 |
| kd42 | walk | 2 | 731 | 73.39 | 162.35 | 12.17 | 1296.56 | 355.69 |
| kd42 | walk | 3 | 742 | 69.82 | 159.18 | 12.38 | 1294.10 | 359.81 |
