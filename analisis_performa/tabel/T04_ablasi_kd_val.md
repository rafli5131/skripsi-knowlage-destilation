# T04 ablasi kd val

Status: Sebagian. Tiga baris ini adalah kondisi kontrol pure_v4 teacher-only pada VAL, satu per seed. Epoch terbaik berasal dari log T03; mAP/P/R berasal dari manifest evaluasi checkpoint terbaik, sehingga nilai mAP dapat sedikit berbeda dari maksimum log per epoch. Tabel belum menjadi ablasi karena belum ada kondisi objective/bobot/temperatur alternatif yang dilatih dan dinilai. Tidak ada training baru saat tabel ini dibuat.

| model | seed | mode | feature_weight | box_weight | class_weight | temperature | best_epoch | val_mAP50 | val_mAP50_95 | val_precision | val_recall | source_run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kd_seed42 | 42 | pure_v4 baseline | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 90 | 0,9620 | 0,6825 | 0,8741 | 0,9121 | runs/kd/yolo11_tiny_pure_kd_v4_locked_seed42/manifest.json |
| kd_seed1337 | 1337 | pure_v4 baseline | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 96 | 0,9509 | 0,6757 | 0,8615 | 0,9119 | runs/kd/yolo11_tiny_pure_kd_v4_seed1337/manifest.json |
| kd_seed2025 | 2025 | pure_v4 baseline | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 88 | 0,9628 | 0,6789 | 0,8916 | 0,9269 | runs/kd/yolo11_tiny_pure_kd_v4_seed2025/manifest.json |
