# T20. sumber daya dan callback pertama saat startup

**Status: lengkap untuk data yang benar-benar dicatat; waktu load model tetap tidak direkam.** `first_frame_latency` di run lama mencakup callback awal menurut logger lama. Untuk benchmark 22 Oktober nilainya adalah callback citra pertama yang masuk log; timer tidak mengukur proses load checkpoint/model.

| Run | Protokol/model | Callback pertama (ms) | RSS median/puncak (MiB) | CPU median/P95 (%, satu CPU logis) | Frame tercatat |
|---|---|---:|---:|---:|---:|
| 20261022_kd_pure_matched_idle_preview_01 | 2026-10-22 live benchmark; preview=True | 539.57 | 359.5 / 363.2 | 1239.3 / 1396.7 | 810 |
| 20261022_kd_pure_matched_walking_preview_01 | 2026-10-22 live benchmark; preview=True | 512.48 | 352.4 / 362.3 | 1236.8 / 1353.8 | 773 |
| 20261022_kd_hybrid_idle_final_01 | 2026-10-22 live benchmark; preview=True | 536.69 | 361.1 / 362.9 | 1233.5 / 1396.6 | 774 |
| 20261022_kd_hybrid_walking_final_01 | 2026-10-22 live benchmark; preview=True | 825.47 | 362.4 / 366.8 | 1255.3 / 1360.7 | 764 |
| 20261022_kd_hybrid_servo_idle_after_opencr_recovery_01 | 2026-10-22 live benchmark; preview=True | 523.09 | 357.3 / 362.6 | 1234.8 / 1376.7 | 738 |

Angka lengkap ada di [CSV](T20_sumber_daya_startup.csv). CPU memakai definisi psutil per logical CPU dan dapat melebihi 100%; sumber baris baru adalah CSV frame mentah, termasuk warm-up. Waktu inisialisasi model dari proses mulai hingga siap menerima frame harus diukur terpisah jika akan dilaporkan.
