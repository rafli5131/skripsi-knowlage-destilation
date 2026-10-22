# Experiment 26 — OP3 pure KD retest

**Status: complete.** The sessions cover idle, verified walking gait, and moving-ball tracking. The pure KD live detection preview remains on after testing.

## Results by session

| Session | Main result | Documentation |
|---|---|---|
| Idle | 60.27 s; 839 measured frames; 13.94 FPS; callback latency P50 46.87 ms and P95 159.14 ms; 0 frame errors. | [Report, graphs, tables, and screenshot](01-idle/README_EN.md) · [Bahasa Indonesia](01-idle/README_ID.md) |
| Walking | 57 s of verified gait; 675 frames; 11.84 FPS; callback latency P50 59.05 ms and P95 167.24 ms; 0 frame errors. | [Report, graphs, tables, telemetry, and screenshot](02-berjalan/README_EN.md) · [Bahasa Indonesia](02-berjalan/README_ID.md) |
| Ball tracking | 29.84 s; 357 frames; 11.93 FPS; ball output on 353/357 frames (98.9%); 3 ball track IDs and 2 ID transitions. | [Report, trajectory graphs, tables, and screenshot](03-tracking/README_EN.md) · [Bahasa Indonesia](03-tracking/README_ID.md) |

## Configuration and interpretation limits

All sessions used the pure KD `kd_seed42` model (`models/weights/kd_student_best.pt`, SHA-256 `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3`), the 640×480 `/thesis/image_raw` camera, CPU FP32, confidence 0.25, IoU 0.45, and BoT-SORT. The SSH-X preview was published on `/vision/debug_image`.

Detection counts and confidence are model outputs for the tested scenes, **not accuracy**. There is no frame-aligned ground truth to calculate precision, recall, F1, mAP, or tracking accuracy. Idle and walking are not a fully controlled comparison: `op3_manager` was unavailable during idle measurement and active during walking. The robot's physical state during tracking is recorded as `unknown`; no gait or servo command was sent. The first walking attempt is retained as diagnostic evidence but excluded because joint-module mapping was not active.

## Raw data

- Idle: runtime log (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_idle_retest_01.csv`) · detection log (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_idle_retest_01_detections.csv`) · metadata (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_idle_retest_01.json`)
- Walking: runtime log (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_walking_retest_02.csv`) · detection log (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_walking_retest_02_detections.csv`) · metadata (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_walking_retest_02.json`)
- Tracking: runtime log (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_tracking_moving_ball_01.csv`) · detection log (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_tracking_moving_ball_01_detections.csv`) · metadata (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_tracking_moving_ball_01.json`)

The post-test live preview is still running as `20261023_kd_pure_live_preview_post_tracking_01`; this monitoring run is excluded from the benchmarks. Preview metadata (lokal: `../../../runs/op3_pytorch/20261023_kd_pure_live_preview_post_tracking_01.json`).
