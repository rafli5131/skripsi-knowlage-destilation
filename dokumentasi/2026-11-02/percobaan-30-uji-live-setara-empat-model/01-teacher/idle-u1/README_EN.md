# Teacher idle repetition 1

Run ID `20261102_eq_teacher_idle_u1`, 2 November 2026. The FP32 teacher ran on the 640×480 OP3 camera with BoT-SORT and SSH-X preview; manager automatic init pose was disabled. The 60-second analysis window followed 30 warm-up frames.

All 584 measured frames had ball, goal, and robot detections and no processing errors. Mean total callback latency was 98.91 ms, P95 180.21 ms, effective camera FPS 9.72, mean process CPU 1329.91% of one logical CPU, and mean RSS 370.03 MiB. Head displacement across four sampled JointState messages was 0 rad; maximum sampled body displacement was 0.001535 rad.

Evidence: [summary_metrics.json](summary_metrics.json), [2160×1800 runtime plot](grafik_runtime_hd.png), four `telemetry_*.txt` files, and raw `runs/op3_pytorch/20261102_eq_teacher_idle_u1.*` logs. No run-specific overlay screenshot was saved. Automatic CSV/joint checks passed; preview continuity and temperature need final review. Detection coverage is not labeled accuracy.
