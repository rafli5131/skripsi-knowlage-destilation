# T23. kepatuhan tenggat pada sesi live

Proporsi dihitung ulang dari frame ukur dalam CSV. Batas 33,3 ms dan 66,7 ms masing-masing setara tenggat nominal 30 FPS dan 15 FPS per frame; ini metrik latensi per callback, bukan bukti bahwa stream memenuhi laju tersebut secara konsisten.

| Run | Kondisi | Ukuran | n | ≤33,3 ms | ≤66,7 ms |
|---|---|---|---:|---:|---:|
| 20261022_kd_pure_matched_idle_preview_01 | servo_idle | stage_total | 780 | 53.46% | 83.97% |
| 20261022_kd_pure_matched_idle_preview_01 | servo_idle | callback_end_to_end | 780 | 0.00% | 80.64% |
| 20261022_kd_pure_matched_walking_preview_01 | walking | stage_total | 743 | 46.03% | 81.97% |
| 20261022_kd_pure_matched_walking_preview_01 | walking | callback_end_to_end | 743 | 0.00% | 75.37% |
| 20261022_kd_hybrid_idle_final_01 | servo_idle | stage_total | 744 | 49.60% | 80.24% |
| 20261022_kd_hybrid_idle_final_01 | servo_idle | callback_end_to_end | 744 | 0.40% | 76.21% |
| 20261022_kd_hybrid_walking_final_01 | walking | stage_total | 734 | 38.56% | 80.25% |
| 20261022_kd_hybrid_walking_final_01 | walking | callback_end_to_end | 734 | 0.00% | 72.34% |
| 20261022_kd_hybrid_servo_idle_after_opencr_recovery_01 | servo_idle | stage_total | 708 | 39.41% | 78.11% |
| 20261022_kd_hybrid_servo_idle_after_opencr_recovery_01 | servo_idle | callback_end_to_end | 708 | 0.00% | 72.32% |

Semua sesi historis dan hasil hitung lengkap ada di [CSV](T23_kepatuhan_tenggat.csv). `stage_total` menjumlah preprocess, inference, postprocess; `callback_end_to_end` adalah ukuran callback penuh. Benchmark fixed-frame belum ada.
