# Teacher, walking repetition 1 in the replacement set

**Provenance:** this display slot uses raw run `20261102_eq_teacher_walk_u3`, which was repetition 3 in the previous set. Bhre requested it as repetition 1 on 2 November 2026. Its raw ID and timestamps remain unchanged; the [previous set archive](../arsip-set-sebelumnya-20261102-1200/) preserves the old numbering.

Run `20261102_eq_teacher_walk_u3` used the FP32 teacher, 640×480 camera, BoT-SORT, and SSH-X preview. Walking started at the 11:49:36.483 UTC acknowledgment and stopped at the 11:50:39.490 UTC acknowledgment. The measured `[t_g + 2 s, t_g + 62 s]` window spans 60 seconds.

| Measure | Result |
|---|---:|
| Measured frames / errors | 589 / 0 |
| Mean / P95 callback latency | 96.41 / 180.86 ms |
| Effective FPS | 9.80 frames/s |
| Mean process CPU | 1329.97% of one logical CPU |
| Mean process RSS | 371.36 MiB |
| Maximum head displacement | 0.001534 rad (about one count) |
| Maximum body joint displacement | 0.377544 rad |

Detection output coverage was ball 589/589 frames (100%), goal 561/589 (95.2%), and robot 589/589 (100%). This is **not labeled accuracy**. Two mid-gait samples, two post-stop samples, and approximately one-second head/leg guard samples were saved. Automatic CSV and post-stop leg stability checks passed. CPU package temperature was 74 °C before and 71 °C at a reading about 10 seconds after detector exit.

Evidence: [during gait](frame_deteksi_saat_gait.png), [after the window but before detector exit](frame_deteksi_sesudah_jendela.png), [metric summary](summary_metrics.json), [performance table](performance_table.csv), [class output table](detection_table.csv), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class output graph](class_outputs_graph_en.png), `gait_guard.json`, `head_guard_samples.csv`, and `telemetry_*.txt`. Local raw logs: `runs/op3_pytorch/20261102_eq_teacher_walk_u3.*`. Final audit of preview continuity and physical conditions remains.
