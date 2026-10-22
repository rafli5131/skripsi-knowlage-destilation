# T25. observasi keluaran deteksi live OP3

Tabel ini merangkum keluaran per kelas untuk lima benchmark terbaru. `detections_per_frame` adalah jumlah kotak dibagi jumlah frame ukur; p10/median/p90 dihitung dari confidence kotak yang keluar; `count_change_fraction` adalah proporsi pasangan frame ukur berurutan dengan jumlah kotak kelas berubah.

| Run | Kondisi | Kelas | Frame | Kotak | Kotak/frame | Confidence p10/median/p90 | Perubahan hitungan | ID tracker yang terlihat |
|---|---|---|---:|---:|---:|---|---:|---|
| 20261022_kd_pure_matched_idle_preview_01 | servo_idle | ball | 780 | 780 | 1.0000 | 0.8473/0.8539/0.8604 | 0.0000 | 1 |
| 20261022_kd_pure_matched_idle_preview_01 | servo_idle | gawang | 780 | 780 | 1.0000 | 0.4057/0.4341/0.4614 | 0.0000 | 3 |
| 20261022_kd_pure_matched_idle_preview_01 | servo_idle | robot | 780 | 771 | 0.9885 | 0.3438/0.4413/0.5354 | 0.0205 | 2 |
| 20261022_kd_pure_matched_walking_preview_01 | walking | ball | 743 | 743 | 1.0000 | 0.8752/0.8995/0.9116 | 0.0000 | 1 |
| 20261022_kd_pure_matched_walking_preview_01 | walking | gawang | 743 | 743 | 1.0000 | 0.3771/0.4425/0.4878 | 0.0000 | 3 |
| 20261022_kd_pure_matched_walking_preview_01 | walking | robot | 743 | 606 | 0.8156 | 0.3286/0.5116/0.6443 | 0.2372 | 2 |
| 20261022_kd_hybrid_idle_final_01 | servo_idle | ball | 744 | 744 | 1.0000 | 0.7940/0.7990/0.8040 | 0.0000 | 1 |
| 20261022_kd_hybrid_idle_final_01 | servo_idle | gawang | 744 | 0 | 0.0000 | [TIDAK ADA KOTAK]/[TIDAK ADA KOTAK]/[TIDAK ADA KOTAK] | 0.0000 | none |
| 20261022_kd_hybrid_idle_final_01 | servo_idle | robot | 744 | 743 | 0.9987 | 0.3629/0.4323/0.4966 | 0.0027 | 2 |
| 20261022_kd_hybrid_walking_final_01 | walking | ball | 734 | 734 | 1.0000 | 0.7656/0.7884/0.8260 | 0.0000 | 1 |
| 20261022_kd_hybrid_walking_final_01 | walking | gawang | 734 | 504 | 0.6866 | 0.2727/0.3617/0.4690 | 0.3915 | 4 |
| 20261022_kd_hybrid_walking_final_01 | walking | robot | 734 | 646 | 0.8801 | 0.2983/0.4122/0.5518 | 0.1637 | 2 |
| 20261022_kd_hybrid_servo_idle_after_opencr_recovery_01 | servo_idle | ball | 708 | 708 | 1.0000 | 0.8363/0.8422/0.8582 | 0.0000 | 1 |
| 20261022_kd_hybrid_servo_idle_after_opencr_recovery_01 | servo_idle | gawang | 708 | 708 | 1.0000 | 0.3679/0.4094/0.4509 | 0.0000 | 3 |
| 20261022_kd_hybrid_servo_idle_after_opencr_recovery_01 | servo_idle | robot | 708 | 708 | 1.0000 | 0.4408/0.5331/0.5765 | 0.0000 | 2 |

Semua baris lama dan baru, termasuk sumber, ada di [CSV](T25_observasi_deteksi_live.csv). Run terbaru pasca-pemulihan OpenCR menunjukkan ketiga kelas muncul pada semua frame ukur, selaras dengan laporan [Percobaan 21](../../dokumentasi/2026-10-22/percobaan-21-kd-hybrid-servo-idle-opencr-pulih/README_ID.md). Ini adalah frekuensi keluaran model; confidence, jumlah kotak, dan ID tracker tidak membuktikan akurasi.
