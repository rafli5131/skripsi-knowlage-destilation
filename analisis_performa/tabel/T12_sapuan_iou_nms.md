# T12 sapuan iou nms

Status: Lengkap untuk tiga model representatif (teacher, KD seed 42, supervised seed 42) pada VAL. Confidence floor 0,001 untuk AP; precision dan recall adalah keluaran validator Ultralytics pada titik F1 internalnya, bukan operating point confidence 0,25. Jumlah duplikat memakai confidence >0,25 dan IoU pencocokan 0,50. Waktu postprocess adalah rerata per gambar dari validator CPU server, bukan latensi OP3. Grid ini bersifat diagnosis VAL; seed 1337/2025 tidak disapu.

| model | split | nms_iou_threshold | mAP50 | mAP50_95 | precision | recall | duplicate_count | postprocess_ms | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| teacher_fp32 | val | 0,3000 | 0,9676 | 0,7609 | 0,9506 | 0,9604 | 0 | 0,6985 | runs/val_sweeps/official_split_20261020/nms_teacher_fp32_0.30.json |
| teacher_fp32 | val | 0,4500 | 0,9722 | 0,7659 | 0,9499 | 0,9611 | 2 | 0,8781 | runs/val_sweeps/official_split_20261020/nms_teacher_fp32_0.45.json |
| teacher_fp32 | val | 0,5000 | 0,9748 | 0,7695 | 0,9472 | 0,9612 | 13 | 0,3626 | runs/val_sweeps/official_split_20261020/nms_teacher_fp32_0.50.json |
| teacher_fp32 | val | 0,6000 | 0,9745 | 0,7737 | 0,9467 | 0,9557 | 69 | 0,5454 | runs/val_sweeps/official_split_20261020/nms_teacher_fp32_0.60.json |
| teacher_fp32 | val | 0,7000 | 0,9734 | 0,7783 | 0,9474 | 0,9465 | 163 | 1,0140 | runs/val_sweeps/official_split_20261020/nms_teacher_fp32_0.70.json |
| kd_seed42 | val | 0,3000 | 0,9651 | 0,6624 | 0,9060 | 0,9504 | 0 | 0,2613 | runs/val_sweeps/official_split_20261020/nms_kd_seed42_0.30.json |
| kd_seed42 | val | 0,4500 | 0,9685 | 0,6662 | 0,9029 | 0,9473 | 5 | 0,4023 | runs/val_sweeps/official_split_20261020/nms_kd_seed42_0.45.json |
| kd_seed42 | val | 0,5000 | 0,9699 | 0,6688 | 0,8984 | 0,9469 | 13 | 0,3289 | runs/val_sweeps/official_split_20261020/nms_kd_seed42_0.50.json |
| kd_seed42 | val | 0,6000 | 0,9685 | 0,6767 | 0,8961 | 0,9318 | 84 | 0,2736 | runs/val_sweeps/official_split_20261020/nms_kd_seed42_0.60.json |
| kd_seed42 | val | 0,7000 | 0,9620 | 0,6826 | 0,8739 | 0,9124 | 240 | 0,4353 | runs/val_sweeps/official_split_20261020/nms_kd_seed42_0.70.json |
| supervised_seed42 | val | 0,3000 | 0,9703 | 0,7042 | 0,9363 | 0,9557 | 0 | 0,2594 | runs/val_sweeps/official_split_20261020/nms_supervised_seed42_0.30.json |
| supervised_seed42 | val | 0,4500 | 0,9732 | 0,7086 | 0,9362 | 0,9547 | 5 | 0,3404 | runs/val_sweeps/official_split_20261020/nms_supervised_seed42_0.45.json |
| supervised_seed42 | val | 0,5000 | 0,9729 | 0,7114 | 0,9344 | 0,9551 | 18 | 0,5347 | runs/val_sweeps/official_split_20261020/nms_supervised_seed42_0.50.json |
| supervised_seed42 | val | 0,6000 | 0,9741 | 0,7161 | 0,9303 | 0,9538 | 64 | 0,2394 | runs/val_sweeps/official_split_20261020/nms_supervised_seed42_0.60.json |
| supervised_seed42 | val | 0,7000 | 0,9733 | 0,7189 | 0,9347 | 0,9428 | 134 | 0,6150 | runs/val_sweeps/official_split_20261020/nms_supervised_seed42_0.70.json |
