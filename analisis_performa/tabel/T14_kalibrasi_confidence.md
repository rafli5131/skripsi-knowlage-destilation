# T14 kalibrasi confidence

Status: Lengkap dari diagnosis tujuh checkpoint pada VAL Roboflow resmi.

| model | split | confidence_bin_lower | confidence_bin_upper | mean_confidence | empirical_precision | detection_count | ECE_10bin | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| teacher_fp32 | val | 0,0000 | 0,1000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | val | 0,1000 | 0,2000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | val | 0,2000 | 0,3000 | 0,2697 | 0,1515 | 99 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | val | 0,3000 | 0,4000 | 0,3488 | 0,3333 | 159 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | val | 0,4000 | 0,5000 | 0,4493 | 0,6076 | 158 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | val | 0,5000 | 0,6000 | 0,5560 | 0,8250 | 160 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | val | 0,6000 | 0,7000 | 0,6497 | 0,8854 | 192 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | val | 0,7000 | 0,8000 | 0,7546 | 0,9615 | 260 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | val | 0,8000 | 0,9000 | 0,8559 | 0,9919 | 491 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | val | 0,9000 | 1,0000 | 0,9277 | 0,9962 | 265 | 0,1492 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| kd_seed42 | val | 0,0000 | 0,1000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | val | 0,1000 | 0,2000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | val | 0,2000 | 0,3000 | 0,2735 | 0,1905 | 84 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | val | 0,3000 | 0,4000 | 0,3502 | 0,2864 | 199 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | val | 0,4000 | 0,5000 | 0,4487 | 0,5143 | 175 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | val | 0,5000 | 0,6000 | 0,5479 | 0,6748 | 163 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | val | 0,6000 | 0,7000 | 0,6541 | 0,7882 | 203 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | val | 0,7000 | 0,8000 | 0,7544 | 0,9048 | 315 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | val | 0,8000 | 0,9000 | 0,8524 | 0,9792 | 432 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | val | 0,9000 | 1,0000 | 0,9438 | 0,9875 | 319 | 0,1032 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed1337 | val | 0,0000 | 0,1000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | val | 0,1000 | 0,2000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | val | 0,2000 | 0,3000 | 0,2727 | 0,1552 | 116 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | val | 0,3000 | 0,4000 | 0,3498 | 0,3436 | 163 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | val | 0,4000 | 0,5000 | 0,4541 | 0,5463 | 205 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | val | 0,5000 | 0,6000 | 0,5475 | 0,6806 | 191 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | val | 0,6000 | 0,7000 | 0,6553 | 0,8162 | 234 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | val | 0,7000 | 0,8000 | 0,7515 | 0,9303 | 244 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | val | 0,8000 | 0,9000 | 0,8529 | 0,9628 | 349 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | val | 0,9000 | 1,0000 | 0,9395 | 0,9741 | 386 | 0,1017 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed2025 | val | 0,0000 | 0,1000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | val | 0,1000 | 0,2000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | val | 0,2000 | 0,3000 | 0,2737 | 0,1889 | 90 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | val | 0,3000 | 0,4000 | 0,3486 | 0,2809 | 178 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | val | 0,4000 | 0,5000 | 0,4514 | 0,5595 | 168 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | val | 0,5000 | 0,6000 | 0,5538 | 0,7039 | 152 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | val | 0,6000 | 0,7000 | 0,6520 | 0,8010 | 201 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | val | 0,7000 | 0,8000 | 0,7504 | 0,9272 | 261 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | val | 0,8000 | 0,9000 | 0,8529 | 0,9776 | 402 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | val | 0,9000 | 1,0000 | 0,9472 | 0,9899 | 396 | 0,1103 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| supervised_seed42 | val | 0,0000 | 0,1000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | val | 0,1000 | 0,2000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | val | 0,2000 | 0,3000 | 0,2767 | 0,1139 | 79 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | val | 0,3000 | 0,4000 | 0,3505 | 0,3333 | 144 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | val | 0,4000 | 0,5000 | 0,4517 | 0,6099 | 182 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | val | 0,5000 | 0,6000 | 0,5480 | 0,7460 | 189 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | val | 0,6000 | 0,7000 | 0,6530 | 0,9222 | 257 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | val | 0,7000 | 0,8000 | 0,7509 | 0,9914 | 350 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | val | 0,8000 | 0,9000 | 0,8442 | 0,9979 | 467 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | val | 0,9000 | 1,0000 | 0,9182 | 0,9906 | 106 | 0,1772 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed1337 | val | 0,0000 | 0,1000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | val | 0,1000 | 0,2000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | val | 0,2000 | 0,3000 | 0,2749 | 0,1613 | 93 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | val | 0,3000 | 0,4000 | 0,3479 | 0,4545 | 187 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | val | 0,4000 | 0,5000 | 0,4494 | 0,5799 | 169 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | val | 0,5000 | 0,6000 | 0,5498 | 0,7725 | 189 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | val | 0,6000 | 0,7000 | 0,6528 | 0,9147 | 211 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | val | 0,7000 | 0,8000 | 0,7521 | 0,9927 | 410 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | val | 0,8000 | 0,9000 | 0,8457 | 0,9928 | 418 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | val | 0,9000 | 1,0000 | 0,9205 | 1,0000 | 102 | 0,1788 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed2025 | val | 0,0000 | 0,1000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | val | 0,1000 | 0,2000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | val | 0,2000 | 0,3000 | 0,2752 | 0,0957 | 94 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | val | 0,3000 | 0,4000 | 0,3500 | 0,3671 | 158 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | val | 0,4000 | 0,5000 | 0,4482 | 0,6127 | 173 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | val | 0,5000 | 0,6000 | 0,5501 | 0,7444 | 180 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | val | 0,6000 | 0,7000 | 0,6526 | 0,9324 | 222 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | val | 0,7000 | 0,8000 | 0,7530 | 0,9873 | 393 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | val | 0,8000 | 0,9000 | 0,8446 | 0,9977 | 433 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | val | 0,9000 | 1,0000 | 0,9332 | 0,9922 | 129 | 0,1746 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| hybrid_feature_seed42 | val | 0,0000 | 0,1000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_feature_seed42 | val | 0,1000 | 0,2000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_feature_seed42 | val | 0,2000 | 0,3000 | 0,2763 | 0,2258 | 124 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_feature_seed42 | val | 0,3000 | 0,4000 | 0,3472 | 0,4640 | 222 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_feature_seed42 | val | 0,4000 | 0,5000 | 0,4510 | 0,6135 | 163 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_feature_seed42 | val | 0,5000 | 0,6000 | 0,5474 | 0,8141 | 156 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_feature_seed42 | val | 0,6000 | 0,7000 | 0,6524 | 0,8848 | 191 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_feature_seed42 | val | 0,7000 | 0,8000 | 0,7583 | 0,9743 | 311 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_feature_seed42 | val | 0,8000 | 0,9000 | 0,8496 | 0,9910 | 446 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_feature_seed42 | val | 0,9000 | 1,0000 | 0,9287 | 0,9947 | 187 | 0,1596 | runs/val_diagnostics/official_split_20261020/hybrid_feature_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,0000 | 0,1000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,1000 | 0,2000 | [TIDAK ADA DETEKSI] | [TIDAK ADA DETEKSI] | 0 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,2000 | 0,3000 | 0,2752 | 0,1792 | 106 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,3000 | 0,4000 | 0,3535 | 0,3218 | 174 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,4000 | 0,5000 | 0,4494 | 0,6425 | 179 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,5000 | 0,6000 | 0,5506 | 0,7440 | 207 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,6000 | 0,7000 | 0,6523 | 0,8947 | 228 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,7000 | 0,8000 | 0,7531 | 0,9867 | 300 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,8000 | 0,9000 | 0,8435 | 0,9956 | 457 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |
| hybrid_full_seed42 | val | 0,9000 | 1,0000 | 0,9283 | 0,9944 | 178 | 0,1623 | runs/val_diagnostics/official_split_20261020/hybrid_full_seed42_predictions.json |

Sumber setiap baris: JSON prediksi VAL pada kolom `source`. Bin [bawah, atas), bin terakhir inklusif; hanya prediksi confidence >0,25. Kebenaran deteksi memakai TP IoU 0,50 dari validator. ECE = jumlah proporsi bin × |rerata confidence − precision empiris|. ECE pada tabel diulang per baris model dan tidak menilai kalibrasi probabilitas kelas secara penuh.
