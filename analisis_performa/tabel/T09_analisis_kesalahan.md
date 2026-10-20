# T09 analisis kesalahan

Status: Lengkap dari diagnosis tujuh checkpoint pada VAL Roboflow resmi.

| model | split | confidence_threshold | match_iou_threshold | false_positives_per_image | fp_background_count | fp_wrong_class_count | fp_localization_count | fp_duplicate_count | fn_small_count | fn_medium_count | fn_large_count | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| teacher_fp32 | val | 0,2500 | 0,5000 | 0,2613 | 75 | 0 | 79 | 163 | 3 | 21 | 34 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| kd_seed42 | val | 0,2500 | 0,5000 | 0,3578 | 126 | 0 | 68 | 240 | 7 | 23 | 39 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed1337 | val | 0,2500 | 0,5000 | 0,3644 | 122 | 0 | 89 | 231 | 8 | 27 | 44 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed2025 | val | 0,2500 | 0,5000 | 0,3232 | 132 | 0 | 63 | 197 | 7 | 21 | 41 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| supervised_seed42 | val | 0,2500 | 0,5000 | 0,2556 | 107 | 0 | 69 | 134 | 5 | 23 | 33 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed1337 | val | 0,2500 | 0,5000 | 0,2622 | 106 | 0 | 81 | 131 | 5 | 18 | 41 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed2025 | val | 0,2500 | 0,5000 | 0,2638 | 106 | 0 | 81 | 133 | 3 | 23 | 37 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |

Sumber setiap baris: JSON prediksi VAL pada kolom `source`. Matching kelas sama dilakukan satu-ke-satu pada IoU ≥0,50, urut confidence. Prediksi sisa yang cocok dengan kelas lain diberi kategori wrong class; sisanya duplicate bila IoU kelas sama ≥0,50, localization bila 0,10–<0,50, dan background selain itu. FN dihitung pada GT tanpa pasangan benar menurut luas kotak pada piksel input. Kategori FP saling eksklusif.
