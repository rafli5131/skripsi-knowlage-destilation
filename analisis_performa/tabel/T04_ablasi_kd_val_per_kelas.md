# T04. ablasi KD pada VAL per kelas

Rincian tiga kelas untuk delapan checkpoint pada T04, termasuk hybrid_full tiga seed. Precision, recall, dan F1
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
| hybrid_feature_seed42 | 42 | hybrid_feature | ball | 182 | 0,9816 | 0,8458 | 0,9278 | 0,9890 | 0,9574 | runs/val_ablation/hybrid_20261022/hybrid_feature_seed42_val.json |
| hybrid_feature_seed42 | 42 | hybrid_feature | gawang | 1048 | 0,9425 | 0,5900 | 0,7702 | 0,9466 | 0,8493 | runs/val_ablation/hybrid_20261022/hybrid_feature_seed42_val.json |
| hybrid_feature_seed42 | 42 | hybrid_feature | robot | 295 | 0,9833 | 0,7949 | 0,8994 | 0,9695 | 0,9331 | runs/val_ablation/hybrid_20261022/hybrid_feature_seed42_val.json |
| hybrid_full_seed42 | 42 | hybrid_full | ball | 182 | 0,9887 | 0,8531 | 0,9476 | 0,9945 | 0,9705 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed42_val.json |
| hybrid_full_seed42 | 42 | hybrid_full | gawang | 1048 | 0,9491 | 0,5950 | 0,7627 | 0,9599 | 0,8500 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed42_val.json |
| hybrid_full_seed42 | 42 | hybrid_full | robot | 295 | 0,9797 | 0,7982 | 0,9060 | 0,9797 | 0,9414 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed42_val.json |
| hybrid_full_seed1337 | 1337 | hybrid_full | ball | 182 | 0,9908 | 0,8593 | 0,9427 | 0,9945 | 0,9679 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed1337_val.json |
| hybrid_full_seed1337 | 1337 | hybrid_full | gawang | 1048 | 0,9511 | 0,5989 | 0,7691 | 0,9532 | 0,8513 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed1337_val.json |
| hybrid_full_seed1337 | 1337 | hybrid_full | robot | 295 | 0,9783 | 0,7986 | 0,8941 | 0,9729 | 0,9318 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed1337_val.json |
| hybrid_full_seed2025 | 2025 | hybrid_full | ball | 182 | 0,9900 | 0,8554 | 0,9372 | 0,9835 | 0,9598 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed2025_val.json |
| hybrid_full_seed2025 | 2025 | hybrid_full | gawang | 1048 | 0,9487 | 0,5924 | 0,7893 | 0,9437 | 0,8596 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed2025_val.json |
| hybrid_full_seed2025 | 2025 | hybrid_full | robot | 295 | 0,9835 | 0,8038 | 0,9167 | 0,9695 | 0,9423 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed2025_val.json |
