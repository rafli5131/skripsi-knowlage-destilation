# T24. pengamatan preview pada benchmark OP3

**Status: ada pengamatan preview aktif/nonaktif, tetapi pengaruh preview belum dapat diisolasi.** Dua run KD murni idle berikut sama-sama memakai kamera OP3, tetapi jumlah thread dan sesi berbeda. Angka ini melengkapi tabel sebagai bukti observasional, bukan estimasi kausal dampak preview.

| Run | Preview | Thread intra/inter | Frame | FPS | Callback median/P95 (ms) | CPU median raw (%) | RSS median (MiB) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20261022_kd_pure_servo_idle_01 | False | 12/12 | 880 | 14.6488 | 44.296/156.726 | 1267.55 | 357.18 |
| 20261022_kd_pure_matched_idle_preview_01 | True | 4/2 | 780 | 13.0113 | 49.745/157.849 | 1237.25 | 359.57 |

Sumber rinci: [CSV](T24_pengaruh_preview.csv); laporan [preview mati](../../dokumentasi/2026-10-22/percobaan-16-benchmark-kd-murni-servo-idle/README_ID.md) dan [preview aktif](../../dokumentasi/2026-10-22/percobaan-18-benchmark-kd-murni-setara-preview/README_ID.md). Untuk mengisolasi pengaruh preview perlu pengulangan berpasangan dengan model, thread, kondisi kamera, durasi, dan adegan sama.
