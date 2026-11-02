# Teacher, walking run 2

Run `20261102_eq_teacher_walk_u2` used the FP32 teacher, 640×480 camera, BoT-SORT, and SSH-X preview. Walking started at the 11:45:45.059 UTC acknowledgment and stopped at the 11:46:48.067 UTC acknowledgment. The measured `[t_g + 2 s, t_g + 62 s]` window spans 60 seconds.

| Measure | Result |
|---|---:|
| Measured frames / errors | 574 / 0 |
| Mean / P95 callback latency | 98.79 / 180.36 ms |
| Effective FPS | 9.56 frames/s |
| Mean process CPU | 1322.74% of one logical CPU |
| Mean process RSS | 371.13 MiB |
| Maximum head displacement | 0.001534 rad (about one count) |
| Maximum body joint displacement | 0.483440 rad |

Detection output coverage was ball 574/574 frames (100%), goal 362/574 (63.1%), and robot 574/574 (100%). This is **not labeled accuracy**. Two mid-gait samples, two post-stop samples, and approximately one-second head/leg guard samples were saved. Automatic CSV and post-stop leg stability checks passed. CPU package temperature was 74 °C before and 81 °C at a reading about 24 seconds after detector exit; the latter is not an exact end-of-run temperature.

Evidence: [during gait](frame_deteksi_saat_gait.png), [after the window but before detector exit](frame_deteksi_sesudah_jendela.png), [metric summary](summary_metrics.json), [performance table](performance_table.csv), [class output table](detection_table.csv), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class output graph](class_outputs_graph_en.png), `gait_guard.json`, `head_guard_samples.csv`, and `telemetry_*.txt`. Local raw logs: `runs/op3_pytorch/20261102_eq_teacher_walk_u2.*`. Final audit of preview continuity and physical conditions remains.
