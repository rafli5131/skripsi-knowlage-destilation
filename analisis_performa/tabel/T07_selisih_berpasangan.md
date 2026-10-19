# T07. selisih berpasangan

Status: Lengkap untuk selisih KD-supervised; perbandingan teacher diturunkan dari tabel sumber.

| seed | comparison | metric | KD minus supervised [0-1] | retention versus teacher [%] |
| --- | --- | --- | --- | --- |
| 42 | KD - supervised | mAP50-95 | -0.045843 | [BELUM DIUKUR per seed] |
| 1337 | KD - supervised | mAP50-95 | -0.073435 | [BELUM DIUKUR per seed] |
| 2025 | KD - supervised | mAP50-95 | -0.059163 | [BELUM DIUKUR per seed] |
| mean ± SD | Pure KD minus supervised student | test_mAP50_95 | -0.05948024571944466 ± 0.013798749953926106 | [BELUM DIUKUR] |
| mean ± SD | Pure KD minus supervised student | test_precision | -0.10618845517881126 ± 0.02030095929065215 | [BELUM DIUKUR] |
| mean ± SD | Pure KD minus supervised student | test_recall | -0.006756644742022792 ± 0.002514951229457758 | [BELUM DIUKUR] |
| mean ± SD | Pure KD minus supervised student | test_F1 | -0.06596198061363916 ± 0.011641786095616133 | [BELUM DIUKUR] |
| 1337 | KD - teacher | mAP50-95 | -0.126921 | 83.72763 |
| 2025 | KD - teacher | mAP50-95 | -0.118354 | 84.826007 |
| 42 | KD - teacher | mAP50-95 | -0.105555 | 86.466926 |

Sumber: paired_seed_deltas.csv, paired_summary.csv, dan per_model.csv
