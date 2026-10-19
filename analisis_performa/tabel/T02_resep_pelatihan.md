# T02. resep pelatihan

Status: Lengkap dari manifest dan args.yaml run yang sudah ada.

| model | seed | objective | epochs_configured [epoch] | epochs_completed [epoch] | batch [image/batch] | optimizer | lr0 | lrf | weight_decay | warmup_epochs [epoch] | AMP | augmentation | KD feature/box/class weight | KD temperature | training duration [s] | source run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kd_seed1337 | 1337 | pure FP32 teacher-only distillation; no supervised training loss and no QAT | 100 | 100 | 16 | AdamW | 0.001 | 0.01 | 0.0005 | 3 | 0 | mosaic=1.0; mixup=0.0; copy_paste=0.0; close_mosaic=10 | 1.0/1.0/1.0 | 2 | [BELUM DIUKUR] | runs/kd/yolo11_tiny_pure_kd_v4_seed1337 |
| kd_seed2025 | 2025 | pure FP32 teacher-only distillation; no supervised training loss and no QAT | 100 | 100 | 16 | AdamW | 0.001 | 0.01 | 0.0005 | 3 | 0 | mosaic=1.0; mixup=0.0; copy_paste=0.0; close_mosaic=10 | 1.0/1.0/1.0 | 2 | [BELUM DIUKUR] | runs/kd/yolo11_tiny_pure_kd_v4_seed2025 |
| kd_seed42 | 42 | pure FP32 teacher-only distillation; no supervised training loss and no QAT | 100 | 100 | 16 | AdamW | 0.001 | 0.01 | 0.0005 | 3 | 0 | mosaic=1.0; mixup=0.0; copy_paste=0.0; close_mosaic=10 | 1.0/1.0/1.0 | 2 | [BELUM DIUKUR] | runs/kd/yolo11_tiny_pure_kd_v4_locked_seed42 |
| supervised_seed1337 | 1337 | student-only supervised detection baseline; separate from pure KD | 100 | 100 | 16 | AdamW | 0.001 | 0.01 | 0.0005 | 3 | 0 | mosaic=1.0; mixup=0.0; copy_paste=0.0; close_mosaic=10 | not applicable | not applicable | [BELUM DIUKUR] | runs/supervised/yolo11_tiny_supervised_seed1337 |
| supervised_seed2025 | 2025 | student-only supervised detection baseline; separate from pure KD | 100 | 100 | 16 | AdamW | 0.001 | 0.01 | 0.0005 | 3 | 0 | mosaic=1.0; mixup=0.0; copy_paste=0.0; close_mosaic=10 | not applicable | not applicable | [BELUM DIUKUR] | runs/supervised/yolo11_tiny_supervised_seed2025 |
| supervised_seed42 | 42 | student-only supervised detection baseline; separate from pure KD | 100 | 100 | 16 | AdamW | 0.001 | 0.01 | 0.0005 | 3 | 0 | mosaic=1.0; mixup=0.0; copy_paste=0.0; close_mosaic=10 | not applicable | not applicable | [BELUM DIUKUR] | runs/supervised/yolo11_tiny_supervised_seed42_retry1 |

Sumber: run manifest, args.yaml, dan results.csv
