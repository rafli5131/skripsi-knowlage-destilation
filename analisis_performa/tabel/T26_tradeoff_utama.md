# T26. Trade-off akurasi TEST dan runtime OP3

| Model | Metode | TEST mAP50–95 | TEST F1 | Latensi frame tetap (ms) | FPS idle | FPS walking | CPU median idle | RSS median idle (MiB) | Parameter | GFLOPs@640 | Cakupan runtime |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| kd_seed42 | Pure KD | 0.674424 | 0.839511 | [BELUM DIUKUR] | 13.9422 | 11.8385 | 79.013% of 16 logical CPUs | 357.379 | 810649 | 2.429 | OP3 preview aktif; manager mati saat idle, aktif saat walking; gait terverifikasi telemetry |
| supervised_seed42 | Supervised student | 0.720267 | 0.909509 | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | 810649 | 2.429 | offline TEST only |
| teacher_fp32 | Teacher | 0.77998 | 0.928979 | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | 2590425 | 6.502 | offline TEST only |
| hybrid_full_seed1337 | KD Hybrid full | 0.7468 | 0.9065 | [BELUM DIUKUR] | 12.0888 | 11.7550 | 80.241% of 16 logical CPUs | 363.121 | 810649 | 2.429 | OP3 preview aktif; manager aktif saat idle/walking; gait terverifikasi telemetry |
| supervised_seed1337 | Supervised student | 0.7265 | 0.9123 | [BELUM DIUKUR] | 12.0553 | 12.3147 | 78.344% of 16 logical CPUs | 362.986 | 810649 | 2.429 | OP3 preview aktif; manager aktif saat idle/walking; gait terverifikasi telemetry |

Sumber lengkap ada di [CSV](T26_tradeoff_utama.csv). Akurasi TEST berasal dari dataset Advance Vision, **bukan kamera OP3**; T30 menjadi sumber TEST Hybrid full dan supervised seed 1337. Runtime terbaru berasal dari [percobaan 25 Supervised](../../dokumentasi/2026-10-22/percobaan-25-supervised-retest-head-locked/README_ID.md), [26 KD murni](../../dokumentasi/2026-10-23/percobaan-26-uji-ulang-kd-murni/README_ID.md), dan [27 KD Hybrid](../../dokumentasi/2026-10-23/percobaan-27-uji-ulang-kd-hybrid/README_ID.md). CPU dinormalisasi terhadap 16 CPU logis.

Angka tiap model adalah satu run per kondisi dan adegan/waktu tidak identik. Khusus KD murni, manager mati saat idle tetapi aktif saat berjalan; status ini mengganggu perbandingan idle–walking yang terkontrol. Tidak ada latensi fixed-frame OP3 untuk model mana pun, sehingga kolom tersebut tetap `[BELUM DIUKUR]`. Evaluasi akurasi eksploratif pada 260 frame OP3 dengan Hybrid dan Supervised seed 1337 dilaporkan terpisah di [T34](T34_akurasi_op3_hybrid_supervised_seed1337.md), karena set dan definisi metriknya berbeda dari TEST Advance Vision.
