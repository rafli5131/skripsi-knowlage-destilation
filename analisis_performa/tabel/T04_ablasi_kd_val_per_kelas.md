# T04. ablasi KD pada VAL per kelas

Rincian tiga kelas untuk empat checkpoint pada T04. Precision, recall, dan F1
memakai confidence >0,25 dan IoU 0,50; AP memakai confidence floor 0,001
dan NMS IoU 0,7. Seluruh angka berasal dari 1.213 gambar VAL resmi.

| model | seed | mode | class | ground_truth_count | val_AP50 | val_AP50_95 | val_precision_conf025 | val_recall_conf025 | val_F1_conf025 | source_run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kd_seed42 | 42 | pure_v4 | ball | 182 | 0,9748 | 0,7334 | 0,7739 | 0,9780 | 0,8641 | runs/val_ablation/pure_weighted_20261020/kd_seed42_val.json |
| kd_seed42 | 42 | pure_v4 | gawang | 1048 | 0,9374 | 0,5798 | 0,7509 | 0,9494 | 0,8386 | runs/val_ablation/pure_weighted_20261020/kd_seed42_val.json |
| kd_seed42 | 42 | pure_v4 | robot | 295 | 0,9738 | 0,7346 | 0,8448 | 0,9593 | 0,8984 | runs/val_ablation/pure_weighted_20261020/kd_seed42_val.json |
| kd_seed1337 | 1337 | pure_v4 | ball | 182 | 0,9616 | 0,7303 | 0,7639 | 0,9780 | 0,8578 | runs/val_ablation/pure_weighted_20261020/kd_seed1337_val.json |
| kd_seed1337 | 1337 | pure_v4 | gawang | 1048 | 0,9300 | 0,5771 | 0,7536 | 0,9427 | 0,8376 | runs/val_ablation/pure_weighted_20261020/kd_seed1337_val.json |
| kd_seed1337 | 1337 | pure_v4 | robot | 295 | 0,9610 | 0,7205 | 0,8140 | 0,9492 | 0,8764 | runs/val_ablation/pure_weighted_20261020/kd_seed1337_val.json |
| kd_seed2025 | 2025 | pure_v4 | ball | 182 | 0,9758 | 0,7294 | 0,8551 | 0,9725 | 0,9100 | runs/val_ablation/pure_weighted_20261020/kd_seed2025_val.json |
| kd_seed2025 | 2025 | pure_v4 | gawang | 1048 | 0,9384 | 0,5747 | 0,7670 | 0,9485 | 0,8481 | runs/val_ablation/pure_weighted_20261020/kd_seed2025_val.json |
| kd_seed2025 | 2025 | pure_v4 | robot | 295 | 0,9742 | 0,7318 | 0,8261 | 0,9661 | 0,8906 | runs/val_ablation/pure_weighted_20261020/kd_seed2025_val.json |
| pure_weighted_seed42 | 42 | pure_weighted | ball | 182 | 0,8382 | 0,7044 | 0,0021 | 1,0000 | 0,0042 | runs/val_ablation/pure_weighted_20261020/pure_weighted_seed42_val.json |
| pure_weighted_seed42 | 42 | pure_weighted | gawang | 1048 | 0,7942 | 0,4914 | 0,1203 | 0,9752 | 0,2143 | runs/val_ablation/pure_weighted_20261020/pure_weighted_seed42_val.json |
| pure_weighted_seed42 | 42 | pure_weighted | robot | 295 | 0,6940 | 0,5762 | 0,0195 | 0,9966 | 0,0383 | runs/val_ablation/pure_weighted_20261020/pure_weighted_seed42_val.json |
