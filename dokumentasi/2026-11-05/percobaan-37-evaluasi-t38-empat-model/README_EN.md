# Experiment 37 — T38, offline evaluation on OP3 frames

Four fixed checkpoints were evaluated offline on the same reviewed OP3 images, without activating a camera, ROS, servos, or gait. The main set contains 200 target frames and 60 negative frames; 50 partial-goal frames are analyzed separately and excluded from the main table. Images come from one collection sequence and labels were reviewed by Bhre after Pure KD-assisted pre-labeling. This is retrospective and does not establish independent generalization across scenes.

| Model | mAP50 | mAP50–95 | Macro precision | Macro recall | Macro F1 | Negative frames with FP |
|---|---:|---:|---:|---:|---:|---:|
| Teacher YOLO11n | 0.7058 | 0.5004 | 0.8690 | 0.6833 | 0.6829 | 2/60 |
| KD Hybrid full seed 1337 | 0.7526 | 0.4885 | 0.6836 | 0.5583 | 0.5121 | 21/60 |
| Supervised seed 1337 | 0.7045 | 0.4414 | 0.7855 | 0.5729 | 0.6054 | 0/60 |
| Pure KD seed 42 | 0.6301 | 0.4218 | 0.7386 | 0.4729 | 0.5008 | 0/60 |

Settings: 640-pixel input, CPU FP32, NMS IoU 0.7; AP confidence floor 0.001; P/R/F1 at confidence >0.25 and matching IoU ≥0.5. The manifest and full Hybrid/Supervised results exactly match T34. All checkpoint hashes match the registry.

See [T38 with class metrics](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md), [English summary graph](grafik_t38_empat_model_en_hd.png), [English class and negative-frame graph](grafik_t38_kelas_negatif_en_hd.png), and [provenance audit](audit_t38.json). Full per-frame and per-session artifacts are local under `runs/op3_multi_session_eval/20261105_empat_model_primary260_v1/`.
