# T07. selisih berpasangan

Status: Lengkap untuk lima metrik keseluruhan pada tiga pasangan seed.

| seed | comparison | metric | delta_kd_minus_supervised [0-1] | sample_SD [0-1] | mAP50_95_retention_vs_teacher [%] |
| --- | --- | --- | --- | --- | --- |
| 42 | Pure KD - Supervised student | test_precision | -0,1122 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 42 | Pure KD - Supervised student | test_recall | -0,0072 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 42 | Pure KD - Supervised student | test_F1 | -0,0700 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 42 | Pure KD - Supervised student | test_mAP50 | -0,0104 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 42 | Pure KD - Supervised student | test_mAP50_95 | -0,0458 | [TIDAK BERLAKU: satu pasangan] | 86,47 |
| 1337 | Pure KD - Supervised student | test_precision | -0,1228 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 1337 | Pure KD - Supervised student | test_recall | -0,0041 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 1337 | Pure KD - Supervised student | test_F1 | -0,0750 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 1337 | Pure KD - Supervised student | test_mAP50 | -0,0175 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 1337 | Pure KD - Supervised student | test_mAP50_95 | -0,0734 | [TIDAK BERLAKU: satu pasangan] | 83,73 |
| 2025 | Pure KD - Supervised student | test_precision | -0,0836 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 2025 | Pure KD - Supervised student | test_recall | -0,0090 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 2025 | Pure KD - Supervised student | test_F1 | -0,0528 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 2025 | Pure KD - Supervised student | test_mAP50 | -0,0184 | [TIDAK BERLAKU: satu pasangan] | [TIDAK BERLAKU] |
| 2025 | Pure KD - Supervised student | test_mAP50_95 | -0,0592 | [TIDAK BERLAKU: satu pasangan] | 84,83 |
| mean_3_seed | Pure KD - Supervised student | test_precision | -0,1062 | 0,020301 | [TIDAK BERLAKU] |
| mean_3_seed | Pure KD - Supervised student | test_recall | -0,0068 | 0,002515 | [TIDAK BERLAKU] |
| mean_3_seed | Pure KD - Supervised student | test_F1 | -0,0660 | 0,011642 | [TIDAK BERLAKU] |
| mean_3_seed | Pure KD - Supervised student | test_mAP50 | -0,0154 | 0,004400 | [TIDAK BERLAKU] |
| mean_3_seed | Pure KD - Supervised student | test_mAP50_95 | -0,0595 | 0,013799 | 85,01 |

Sumber: [paired_seed_deltas.csv](../../artifacts/thesis_analysis_final_corrected/paired_seed_deltas.csv), [paired_summary.csv](../../artifacts/thesis_analysis_final_corrected/paired_summary.csv), dan [per_model.csv](../../artifacts/thesis_analysis_final_corrected/per_model.csv).

Retensi mAP50–95 = 100 × mAP50–95 KD / mAP50–95 teacher pada TEST. Nilai mean_3_seed adalah rerata retensi tiga checkpoint KD; SD pasangan dihitung pada delta KD dikurangi supervised.
