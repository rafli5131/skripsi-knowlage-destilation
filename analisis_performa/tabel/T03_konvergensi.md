# T03. konvergensi

Status: Lengkap dari log enam run training.

| model | seed | run_sample [run] | VAL mAP50-95 @ epoch 10 [0-1] | VAL mAP50-95 @ epoch 25 [0-1] | VAL mAP50-95 @ epoch 50 [0-1] | VAL mAP50-95 @ epoch 75 [0-1] | VAL mAP50-95 @ epoch 100 [0-1] | best_epoch [epoch] | best_VAL_mAP50-95 [0-1] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kd_seed1337 | 1337 | 1 | 0,4001 | 0,5867 | 0,6426 | 0,6709 | 0,6749 | 96 | 0,6756 |
| kd_seed2025 | 2025 | 1 | 0,3833 | 0,6019 | 0,6605 | 0,6727 | 0,6724 | 88 | 0,6784 |
| kd_seed42 | 42 | 1 | 0,3523 | 0,5910 | 0,6592 | 0,6760 | 0,6808 | 90 | 0,6831 |
| supervised_seed1337 | 1337 | 1 | 0,4915 | 0,6141 | 0,6750 | 0,7030 | 0,7168 | 99 | 0,7179 |
| supervised_seed2025 | 2025 | 1 | 0,4772 | 0,6193 | 0,6839 | 0,7101 | 0,7236 | 99 | 0,7250 |
| supervised_seed42 | 42 | 1 | 0,4532 | 0,5989 | 0,6796 | 0,7071 | 0,7190 | 100 | 0,7190 |

Sumber: results.csv pada direktori setiap run yang tercantum dalam [registri model](../../configs/model_registry.yaml).

best_epoch dan best_VAL_mAP50-95 adalah maksimum pada results.csv, bukan hasil evaluasi ulang checkpoint.
