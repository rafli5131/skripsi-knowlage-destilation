# T08 akurasi ukuran objek

Status: Lengkap untuk VAL pada tujuh checkpoint. Luas kotak dinormalisasi ke sisi referensi 640 piksel; kecil <1024 px², sedang 1024–9216 px², besar >9216 px². Recall memakai confidence >0,25 dan IoU 0,50. AP adalah rerata 10 ambang IoU 0,50–0,95, dengan pencocokan satu-ke-satu berdasarkan IoU; deteksi objek kelas sama di luar kelompok ukuran diabaikan. Definisi diagnostik ini tidak identik dengan evaluasi area COCO. Angka ini berasal dari VAL Advance Vision, bukan kamera OP3.

| model | method | split | class | size_category | ground_truth_objects_count | recall_iou50_conf025 | AP50_95 | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| teacher_fp32 | Teacher | val | ball | small | 59 | 0,9661 | 0,7571 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | Teacher | val | ball | medium | 40 | 1,0000 | 0,8814 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | Teacher | val | ball | large | 83 | 1,0000 | 0,9408 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | Teacher | val | gawang | small | 0 | [TIDAK ADA GT] | [TIDAK ADA GT] | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | Teacher | val | gawang | medium | 89 | 0,5506 | 0,1248 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | Teacher | val | gawang | large | 959 | 0,8519 | 0,5698 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | Teacher | val | robot | small | 28 | 0,8571 | 0,5107 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | Teacher | val | robot | medium | 136 | 0,9632 | 0,7801 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| teacher_fp32 | Teacher | val | robot | large | 131 | 0,9847 | 0,8775 | runs/val_diagnostics/official_split_20261020/teacher_fp32_predictions.json |
| kd_seed42 | Pure KD | val | ball | small | 59 | 0,8983 | 0,4576 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | Pure KD | val | ball | medium | 40 | 0,9750 | 0,6931 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | Pure KD | val | ball | large | 83 | 1,0000 | 0,8039 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | Pure KD | val | gawang | small | 0 | [TIDAK ADA GT] | [TIDAK ADA GT] | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | Pure KD | val | gawang | medium | 89 | 0,5955 | 0,0933 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | Pure KD | val | gawang | large | 959 | 0,8206 | 0,5340 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | Pure KD | val | robot | small | 28 | 0,7500 | 0,2470 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | Pure KD | val | robot | medium | 136 | 0,9265 | 0,6514 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed42 | Pure KD | val | robot | large | 131 | 0,9924 | 0,7934 | runs/val_diagnostics/official_split_20261020/kd_seed42_predictions.json |
| kd_seed1337 | Pure KD | val | ball | small | 59 | 0,8983 | 0,4321 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | Pure KD | val | ball | medium | 40 | 0,9750 | 0,6498 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | Pure KD | val | ball | large | 83 | 1,0000 | 0,7989 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | Pure KD | val | gawang | small | 0 | [TIDAK ADA GT] | [TIDAK ADA GT] | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | Pure KD | val | gawang | medium | 89 | 0,5056 | 0,0865 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | Pure KD | val | gawang | large | 959 | 0,8092 | 0,5315 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | Pure KD | val | robot | small | 28 | 0,7500 | 0,2497 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | Pure KD | val | robot | medium | 136 | 0,9191 | 0,6312 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed1337 | Pure KD | val | robot | large | 131 | 0,9847 | 0,7777 | runs/val_diagnostics/official_split_20261020/kd_seed1337_predictions.json |
| kd_seed2025 | Pure KD | val | ball | small | 59 | 0,8644 | 0,4681 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | Pure KD | val | ball | medium | 40 | 0,9750 | 0,7094 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | Pure KD | val | ball | large | 83 | 1,0000 | 0,7761 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | Pure KD | val | gawang | small | 0 | [TIDAK ADA GT] | [TIDAK ADA GT] | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | Pure KD | val | gawang | medium | 89 | 0,5618 | 0,0880 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | Pure KD | val | gawang | large | 959 | 0,7977 | 0,5267 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | Pure KD | val | robot | small | 28 | 0,7857 | 0,2877 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | Pure KD | val | robot | medium | 136 | 0,9191 | 0,6355 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| kd_seed2025 | Pure KD | val | robot | large | 131 | 0,9771 | 0,7786 | runs/val_diagnostics/official_split_20261020/kd_seed2025_predictions.json |
| supervised_seed42 | Supervised student | val | ball | small | 59 | 0,9322 | 0,6199 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | Supervised student | val | ball | medium | 40 | 0,9250 | 0,7332 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | Supervised student | val | ball | large | 83 | 1,0000 | 0,8657 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | Supervised student | val | gawang | small | 0 | [TIDAK ADA GT] | [TIDAK ADA GT] | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | Supervised student | val | gawang | medium | 89 | 0,5618 | 0,0837 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | Supervised student | val | gawang | large | 959 | 0,8384 | 0,5510 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | Supervised student | val | robot | small | 28 | 0,8214 | 0,3567 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | Supervised student | val | robot | medium | 136 | 0,9706 | 0,6806 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed42 | Supervised student | val | robot | large | 131 | 0,9771 | 0,8520 | runs/val_diagnostics/official_split_20261020/supervised_seed42_predictions.json |
| supervised_seed1337 | Supervised student | val | ball | small | 59 | 0,8644 | 0,5510 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | Supervised student | val | ball | medium | 40 | 0,9250 | 0,7285 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | Supervised student | val | ball | large | 83 | 0,9880 | 0,8736 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | Supervised student | val | gawang | small | 0 | [TIDAK ADA GT] | [TIDAK ADA GT] | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | Supervised student | val | gawang | medium | 89 | 0,5056 | 0,0832 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | Supervised student | val | gawang | large | 959 | 0,8300 | 0,5485 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | Supervised student | val | robot | small | 28 | 0,8214 | 0,3891 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | Supervised student | val | robot | medium | 136 | 0,9632 | 0,6887 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed1337 | Supervised student | val | robot | large | 131 | 0,9847 | 0,8443 | runs/val_diagnostics/official_split_20261020/supervised_seed1337_predictions.json |
| supervised_seed2025 | Supervised student | val | ball | small | 59 | 0,9661 | 0,6669 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | Supervised student | val | ball | medium | 40 | 0,9250 | 0,7372 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | Supervised student | val | ball | large | 83 | 1,0000 | 0,8838 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | Supervised student | val | gawang | small | 0 | [TIDAK ADA GT] | [TIDAK ADA GT] | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | Supervised student | val | gawang | medium | 89 | 0,5281 | 0,0934 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | Supervised student | val | gawang | large | 959 | 0,8415 | 0,5431 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | Supervised student | val | robot | small | 28 | 0,7857 | 0,3875 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | Supervised student | val | robot | medium | 136 | 0,9632 | 0,7008 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
| supervised_seed2025 | Supervised student | val | robot | large | 131 | 0,9847 | 0,8280 | runs/val_diagnostics/official_split_20261020/supervised_seed2025_predictions.json |
