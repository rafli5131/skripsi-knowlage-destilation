# T18. sesi live historis dan benchmark OP3

Tabel CSV menghimpun enam run lama serta lima benchmark 22 Oktober yang memakai preview aktif dan mencatat hasil per kelas. Baris dengan protokol berbeda tetap diberi catatan; jangan gabungkan untuk estimasi efek kondisi. Lima run terbaru memakai warm-up 30 frame dan sekitar 60 detik pengukuran, sebagaimana dijelaskan pada laporan eksperimen 18–21.

| Run | Model/kondisi | Frame ukur | FPS efektif | Callback median/P95 (ms) | CPU median raw (%) | RSS median (MiB) | Catatan |
|---|---|---:|---:|---:|---:|---:|---|
| 20261022_kd_pure_matched_idle_preview_01 | 2026-10-22 matched preview benchmark / servo_idle | 780 | 13.011 | 49.75 / 157.85 | 1237.2 | 359.6 | operator condition label; walking is gait request, not independently inferred |
| 20261022_kd_pure_matched_walking_preview_01 | 2026-10-22 matched preview benchmark / walking | 743 | 12.365 | 55.08 / 161.79 | 1238.2 | 352.4 | operator condition label; walking is gait request, not independently inferred |
| 20261022_kd_hybrid_idle_final_01 | 2026-10-22 matched preview benchmark / servo_idle | 744 | 12.390 | 49.60 / 158.15 | 1233.2 | 361.4 | operator condition label; walking is gait request, not independently inferred |
| 20261022_kd_hybrid_walking_final_01 | 2026-10-22 matched preview benchmark / walking | 734 | 12.196 | 56.39 / 163.17 | 1257.3 | 362.4 | operator condition label; walking is gait request, not independently inferred |
| 20261022_kd_hybrid_servo_idle_after_opencr_recovery_01 | 2026-10-22 matched preview benchmark / servo_idle | 708 | 11.795 | 53.22 / 159.87 | 1233.9 | 357.3 | servo idle verified: joint velocity zero before/after; no gait command |

Seluruh baris, termasuk sesi historis, ada di [CSV](T18_sesi_live_historis.csv). FPS dan gap memakai timestamp capture yang diterima node. Nilai CPU pada tabel ini mentah (100% = satu CPU logis); T19 menampilkan normalisasi terhadap 16 CPU logis. Frame dan kotak deteksi bukan label ground truth.

Sumber benchmark: [KD murni, idle/walking](../../dokumentasi/2026-10-22/percobaan-18-benchmark-kd-murni-setara-preview/README_ID.md), [KD Hybrid, idle/walking](../../dokumentasi/2026-10-22/percobaan-19-benchmark-kd-hybrid-setara-preview/README_ID.md), [KD Hybrid, idle setelah OpenCR pulih](../../dokumentasi/2026-10-22/percobaan-21-kd-hybrid-servo-idle-opencr-pulih/README_ID.md).
