# Interval bootstrap per model pada TEST

Nilai dan interval berasal dari evaluasi TEST terkunci yang sudah ada. Unit resampling adalah gambar TEST; 1.000 replikasi dengan pengembalian. Interval ini berlaku untuk checkpoint yang diuji dan tidak mencakup variasi antar-seed.

| model | method | seed | metric | value | ci95_lower | ci95_upper | valid_replicates | sampling_unit | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kd_seed42 | Pure KD | 42 | test_precision | 0,7451 | 0,7074 | 0,7894 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed42_metrics.json |
| kd_seed42 | Pure KD | 42 | test_recall | 0,9613 | 0,9452 | 0,9762 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed42_metrics.json |
| kd_seed42 | Pure KD | 42 | test_F1 | 0,8395 | 0,8148 | 0,8677 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed42_metrics.json |
| kd_seed42 | Pure KD | 42 | test_mAP50 | 0,9481 | 0,9318 | 0,9642 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed42_metrics.json |
| kd_seed42 | Pure KD | 42 | test_mAP50_95 | 0,6744 | 0,6553 | 0,7005 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed42_metrics.json |
| kd_seed1337 | Pure KD | 1337 | test_precision | 0,7404 | 0,7034 | 0,7877 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed1337_metrics.json |
| kd_seed1337 | Pure KD | 1337 | test_recall | 0,9632 | 0,9467 | 0,9783 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed1337_metrics.json |
| kd_seed1337 | Pure KD | 1337 | test_F1 | 0,8372 | 0,8119 | 0,8682 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed1337_metrics.json |
| kd_seed1337 | Pure KD | 1337 | test_mAP50 | 0,9403 | 0,9239 | 0,9569 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed1337_metrics.json |
| kd_seed1337 | Pure KD | 1337 | test_mAP50_95 | 0,6531 | 0,6343 | 0,6834 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed1337_metrics.json |
| kd_seed2025 | Pure KD | 2025 | test_precision | 0,7787 | 0,7389 | 0,8238 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed2025_metrics.json |
| kd_seed2025 | Pure KD | 2025 | test_recall | 0,9648 | 0,9498 | 0,9782 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed2025_metrics.json |
| kd_seed2025 | Pure KD | 2025 | test_F1 | 0,8618 | 0,8357 | 0,8899 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed2025_metrics.json |
| kd_seed2025 | Pure KD | 2025 | test_mAP50 | 0,9455 | 0,9285 | 0,9617 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed2025_metrics.json |
| kd_seed2025 | Pure KD | 2025 | test_mAP50_95 | 0,6616 | 0,6362 | 0,6916 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/kd_seed2025_metrics.json |
| supervised_seed42 | Supervised student | 42 | test_precision | 0,8573 | 0,8395 | 0,8795 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed42_metrics.json |
| supervised_seed42 | Supervised student | 42 | test_recall | 0,9685 | 0,9534 | 0,9818 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed42_metrics.json |
| supervised_seed42 | Supervised student | 42 | test_F1 | 0,9095 | 0,8974 | 0,9240 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed42_metrics.json |
| supervised_seed42 | Supervised student | 42 | test_mAP50 | 0,9585 | 0,9469 | 0,9714 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed42_metrics.json |
| supervised_seed42 | Supervised student | 42 | test_mAP50_95 | 0,7203 | 0,7044 | 0,7429 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed42_metrics.json |
| supervised_seed1337 | Supervised student | 1337 | test_precision | 0,8632 | 0,8434 | 0,8872 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed1337_metrics.json |
| supervised_seed1337 | Supervised student | 1337 | test_recall | 0,9673 | 0,9521 | 0,9808 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed1337_metrics.json |
| supervised_seed1337 | Supervised student | 1337 | test_F1 | 0,9123 | 0,8981 | 0,9273 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed1337_metrics.json |
| supervised_seed1337 | Supervised student | 1337 | test_mAP50 | 0,9578 | 0,9436 | 0,9722 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed1337_metrics.json |
| supervised_seed1337 | Supervised student | 1337 | test_mAP50_95 | 0,7265 | 0,7081 | 0,7493 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed1337_metrics.json |
| supervised_seed2025 | Supervised student | 2025 | test_precision | 0,8622 | 0,8370 | 0,8873 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed2025_metrics.json |
| supervised_seed2025 | Supervised student | 2025 | test_recall | 0,9738 | 0,9603 | 0,9851 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed2025_metrics.json |
| supervised_seed2025 | Supervised student | 2025 | test_F1 | 0,9146 | 0,8993 | 0,9296 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed2025_metrics.json |
| supervised_seed2025 | Supervised student | 2025 | test_mAP50 | 0,9639 | 0,9494 | 0,9756 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed2025_metrics.json |
| supervised_seed2025 | Supervised student | 2025 | test_mAP50_95 | 0,7208 | 0,7026 | 0,7433 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/supervised_seed2025_metrics.json |
| teacher_fp32 | Teacher | teacher | test_precision | 0,8915 | 0,8717 | 0,9112 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/teacher_fp32_metrics.json |
| teacher_fp32 | Teacher | teacher | test_recall | 0,9697 | 0,9557 | 0,9823 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/teacher_fp32_metrics.json |
| teacher_fp32 | Teacher | teacher | test_F1 | 0,9290 | 0,9140 | 0,9428 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/teacher_fp32_metrics.json |
| teacher_fp32 | Teacher | teacher | test_mAP50 | 0,9642 | 0,9530 | 0,9755 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/teacher_fp32_metrics.json |
| teacher_fp32 | Teacher | teacher | test_mAP50_95 | 0,7800 | 0,7623 | 0,7974 | 1000 | TEST image | runs/final_test/pure_kd_official_split_locked_retry1/teacher_fp32_metrics.json |

Sumber: [per_model.csv](../../artifacts/thesis_analysis_final_corrected/per_model.csv) dan [manifest evaluasi TEST terkunci](../../runs/final_test/pure_kd_official_split_locked_retry1/manifest.json).
