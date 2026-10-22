# T17. konfigurasi thread yang tercatat pada benchmark OP3

**Status: konfigurasi aktual terdokumentasi; sapuan thread terkontrol belum dilakukan.** Tabel ini menginventarisasi konfigurasi dari sesi yang sudah terjadi. Jumlah thread berjalan bersama perubahan kondisi, preview, dan/atau waktu sesi; perbedaan performa tidak dapat diatribusikan hanya kepada jumlah thread.

| Run | Model | Kondisi | Preview | Thread intra/inter | Frame | FPS | Callback median/P95 (ms) | CPU median (% satu logical CPU) | RSS median (MiB) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 20261022_kd_pure_servo_idle_01 | kd_seed42 | servo_idle | False | 12/12 | 880 | 14.6488 | 44.296/156.726 | 1267.55 | 357.18 |
| 20261022_kd_pure_matched_idle_preview_01 | kd_seed42 | servo_idle | True | 4/2 | 780 | 13.0113 | 49.745/157.849 | 1237.25 | 359.57 |
| 20261022_kd_pure_matched_walking_preview_01 | kd_seed42 | walking | True | 4/2 | 743 | 12.3652 | 55.084/161.789 | 1238.20 | 352.43 |
| 20261022_kd_hybrid_idle_final_01 | hybrid_full_seed1337 | servo_idle | True | 4/2 | 744 | 12.3903 | 49.601/158.148 | 1233.15 | 361.40 |
| 20261022_kd_hybrid_walking_final_01 | hybrid_full_seed1337 | walking | True | 4/2 | 734 | 12.1964 | 56.388/163.167 | 1257.35 | 362.43 |
| 20261022_kd_hybrid_servo_idle_after_opencr_recovery_01 | hybrid_full_seed1337 | servo_idle | True | 4/2 | 708 | 11.7951 | 53.219/159.874 | 1233.90 | 357.26 |

Rincian run ID dan sumber CSV/JSON ada di [CSV](T17_sapuan_thread.csv). CPU adalah nilai mentah psutil, sehingga 100% berarti satu logical CPU; NUC memiliki 16 logical CPU.

**Batas:** satu sesi KD murni idle memakai 12/12 thread tanpa preview; benchmark perbandingan memakai 4/2 thread dengan preview. Karena preview dan protokol juga berubah, keduanya bukan eksperimen thread-only. Sapuan thread dengan gambar tetap, model, preview, kondisi sistem, dan jumlah pengulangan terkendali masih belum tersedia.
