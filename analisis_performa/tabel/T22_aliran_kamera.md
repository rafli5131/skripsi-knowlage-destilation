# T22. aliran kamera dan frame yang diproses

Laju kamera mentah dan throughput detektor adalah besaran berbeda. Log benchmark 22 Oktober menyimpan timestamp frame yang diproses, tetapi tidak menyimpan subscriber counter independen atau laju publish topic selama run. Karena itu angka di bawah adalah laju frame terproses dan capture gap, bukan FPS kamera mentah.

| Run | Kondisi | Frame ukur | Laju frame diproses (FPS) | Gap p50/p95 (ms) | Gap max (s) | Jeda >1 s | Model/preview |
|---|---|---:|---:|---:|---:|---:|---|
| 20261022_kd_pure_matched_idle_preview_01 | servo_idle | 780 | 13.011 | 68.00/163.97 | 0.500 | 0 | yes; kd_seed42 |
| 20261022_kd_pure_matched_walking_preview_01 | walking | 743 | 12.365 | 68.00/167.97 | 0.204 | 0 | yes; kd_seed42 |
| 20261022_kd_hybrid_idle_final_01 | servo_idle | 744 | 12.390 | 67.99/167.96 | 0.368 | 0 | yes; hybrid_full_seed1337 |
| 20261022_kd_hybrid_walking_final_01 | walking | 734 | 12.196 | 68.00/167.98 | 0.300 | 0 | yes; hybrid_full_seed1337 |
| 20261022_kd_hybrid_servo_idle_after_opencr_recovery_01 | servo_idle | 708 | 11.795 | 68.00/167.99 | 0.300 | 0 | yes; hybrid_full_seed1337 |

Probe lama tanpa detektor mencatat 360 sampel dalam 12 detik (estimasi 30 Hz), tetapi bukan sesi berpasangan dan tidak menyimpan timestamp mentah. Semua data/run tersedia di [CSV](T22_aliran_kamera.csv). Belum ada perbandingan kausal kamera-saja vs detektor.
