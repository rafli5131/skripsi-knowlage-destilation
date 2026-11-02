# Teacher, walking repetition 3 in the replacement set

Raw run `20261102_eq_teacher_walk_retest_u3` was recorded on 2 November 2026 with the FP32 teacher, 640×480 OP3 camera, BoT-SORT, and SSH-X preview. Walking start was acknowledged at 12:10:04.931 UTC and stop at 12:11:07.939 UTC. The 60-second measured window was `[t_g + 2 s, t_g + 62 s]`.

| Measure | Result |
|---|---:|
| Measured frames / errors | 604 / 0 |
| Mean / P95 callback latency | 94.40 / 180.01 ms |
| Effective FPS | 10.07 frames/s |
| Mean process CPU | 1337.99% of one logical CPU |
| Mean process RSS | 377.97 MiB |
| Maximum head displacement | 0.001534 rad (about one count) |
| Maximum body joint displacement | 0.490874 rad |

Ball and robot each appeared in 604/604 measured frames (100%); goal in 574/604 (95.0%). This is **output coverage**, not labeled accuracy or precision. Median confidence and tracker ID counts are in the [detection table](detection_table.csv). Gait guard, two mid-gait samples, and two post-stop samples support leg motion and bounded head movement. CPU package temperature was 81 °C before the run and 51 °C at a reading about 19 seconds after detector exit; the latter is not the temperature at the final gait instant.

Evidence: [during gait](frame_deteksi_saat_gait.png), [after the window](frame_deteksi_sesudah_jendela.png), [metric summary](summary_metrics.json), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class output graph](class_outputs_graph_en.png), `gait_guard.json`, and `head_guard_samples.csv`. Local raw logs: `runs/op3_pytorch/20261102_eq_teacher_walk_retest_u3.*`. Final preview-continuity and physical-condition audit remains.
