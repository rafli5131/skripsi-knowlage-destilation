# T06. akurasi per kelas

Status: Lengkap dari hasil TEST terkunci yang sudah ada.

| method | class | ground_truth_objects [object] | AP50 mean | AP50 SD | AP50-95 mean | AP50-95 SD | precision mean | precision SD | recall mean | recall SD | F1 mean | F1 SD | n_models [model] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pure KD | ball | 83 | 0.955998 | 0.008379 | 0.730215 | 0.019003 | 0.744663 | 0.043069 | 0.963855 | 0 | 0.839742 | 0.027192 | 3 |
| Pure KD | gawang | 532 | 0.913864 | 0.003412 | 0.538239 | 0.004075 | 0.737141 | 0.005432 | 0.931078 | 0.002871 | 0.822822 | 0.002334 | 3 |
| Pure KD | robot | 119 | 0.964044 | 0.006048 | 0.720654 | 0.015135 | 0.782377 | 0.02411 | 0.994398 | 0.004852 | 0.87563 | 0.016667 | 3 |
| Supervised student | ball | 83 | 0.975962 | 0.004588 | 0.824078 | 0.003986 | 0.941531 | 0.010678 | 0.967871 | 0.006956 | 0.954469 | 0.003143 | 3 |
| Supervised student | gawang | 532 | 0.926621 | 0.008613 | 0.548595 | 0.000375 | 0.753058 | 0.008294 | 0.941729 | 0.003759 | 0.836878 | 0.005926 | 3 |
| Supervised student | robot | 119 | 0.977639 | 0.004676 | 0.794877 | 0.006242 | 0.888158 | 0.011395 | 1 | 0 | 0.940741 | 0.006415 | 3 |
| Teacher | ball | 83 | 0.984762 | [BELUM DIUKUR] | 0.913056 | [BELUM DIUKUR] | 0.964706 | [BELUM DIUKUR] | 0.987952 | [BELUM DIUKUR] | 0.97619 | [BELUM DIUKUR] | 1 |
| Teacher | gawang | 532 | 0.923388 | [BELUM DIUKUR] | 0.568424 | [BELUM DIUKUR] | 0.734904 | [BELUM DIUKUR] | 0.93797 | [BELUM DIUKUR] | 0.824112 | [BELUM DIUKUR] | 1 |
| Teacher | robot | 119 | 0.984581 | [BELUM DIUKUR] | 0.858459 | [BELUM DIUKUR] | 0.975 | [BELUM DIUKUR] | 0.983193 | [BELUM DIUKUR] | 0.979079 | [BELUM DIUKUR] | 1 |

Sumber: per_model.csv dan metrik per kelas dari TEST terkunci; jumlah objek diperiksa pada hasil seed 42
