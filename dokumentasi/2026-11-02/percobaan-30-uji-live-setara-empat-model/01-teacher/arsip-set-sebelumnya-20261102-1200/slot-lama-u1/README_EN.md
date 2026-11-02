# Teacher, walking run 1

Run `20261102_eq_teacher_walk_u1` used the FP32 teacher, 640×480 OP3 camera, BoT-SORT tracking, and SSH-X preview. The 60-second measurement window began two seconds after the `Start walking` acknowledgment at 11:34:11.772 UTC. The stop command was sent 63 seconds after that acknowledgment and acknowledged at 11:35:14.787 UTC.

| Measure | Result |
|---|---:|
| Frames in window | 611 |
| Frame errors | 0 |
| Mean callback latency | 90.88 ms |
| P95 callback latency | 181.31 ms |
| Effective camera FPS | 10.19 frames/s |
| Mean process CPU | 1338.94% of one logical CPU |
| Mean process RSS | 375.68 MiB |
| Maximum head displacement | 0.001534 rad (about one encoder count) |
| Maximum body joint displacement | 0.389631 rad |

Output coverage was ball 611/611 frames (100%), goal 112/611 (18.3%), and robot 611/611 (100%). This measures model output frequency, **not labeled accuracy**. The goal was frequently missed during walking; the visual cause has not been established.

[Head and leg guard samples](head_guard_samples.csv) include samples around 20 and 40 seconds. Two post-stop joint samples show stable legs. [Gait guard](gait_guard.json) records acknowledgments and the head movement bound. The [metric summary](summary_metrics.json) passed automatic CSV and telemetry checks; final audit of preview continuity, temperature, and physical conditions remains.

See the [2160×1800 runtime graph](grafik_runtime_hd.png) and [2880×1800 run matrix](../../05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png). The [later monitoring preview](preview_setelah_u1.png) was taken **after this run's detector stopped**, so a screenshot between the end of the window and detector exit was not captured. Local raw logs: `runs/op3_pytorch/20261102_eq_teacher_walk_u1.csv`, `.json`, and `_detections.csv`.
