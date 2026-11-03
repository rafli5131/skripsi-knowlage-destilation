# T37 — Ringkasan runtime live OP3

Rata-rata ± SD sampel atas tiga rerata run. CPU adalah % satu CPU logis; RSS adalah memori resident proses. Pengguna menerima hasil untuk analisis deskriptif dengan keterbatasan audit. Perbandingan lintas hari tidak membuktikan sebab akibat atau kesetaraan fisik; persetujuan pembimbing belum dicatat.

| Model | Kondisi | Latensi (ms) | FPS | CPU (%) | RSS (MiB) | P95 gabungan (ms) |
|---|---|---:|---:|---:|---:|---:|
| teacher | idle | 96.24 ± 3.60 | 9.88 ± 0.31 | 1338.90 ± 9.65 | 370.58 ± 1.29 | 181.31 |
| hybrid1337 | idle | 64.70 ± 1.92 | 13.60 ± 0.35 | 1305.97 ± 4.91 | 358.87 ± 1.24 | 161.76 |
| sup1337 | idle | 73.12 ± 3.27 | 12.14 ± 0.29 | 1299.18 ± 3.32 | 355.93 ± 3.32 | 160.70 |
| kd42 | idle | 74.09 ± 1.04 | 12.07 ± 0.05 | 1300.21 ± 2.44 | 356.97 ± 5.92 | 163.75 |
| teacher | walk | 95.85 ± 1.27 | 9.87 ± 0.17 | 1333.54 ± 4.08 | 372.42 ± 5.11 | 180.66 |
| hybrid1337 | walk | 71.47 ± 2.98 | 12.54 ± 0.38 | 1303.77 ± 3.88 | 356.31 ± 2.09 | 160.72 |
| sup1337 | walk | 70.80 ± 2.71 | 12.64 ± 0.52 | 1301.13 ± 6.03 | 359.16 ± 4.76 | 161.10 |
| kd42 | walk | 72.65 ± 2.55 | 12.21 ± 0.15 | 1295.65 ± 1.35 | 360.18 ± 4.69 | 161.23 |

[CSV lengkap](T37_runtime_live_setara_ringkasan.csv) · [Grafik Indonesia](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/grafik_runtime_24_run_id_hd.png) · [English](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/grafik_runtime_24_run_en_hd.png).
