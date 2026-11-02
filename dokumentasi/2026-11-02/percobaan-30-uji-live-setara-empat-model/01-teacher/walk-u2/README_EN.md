# Teacher, walking repetition 2 in the replacement set

Raw run `20261102_eq_teacher_walk_retest_u2` was recorded on 2 November 2026 with the FP32 teacher, 640×480 OP3 camera, BoT-SORT, and SSH-X preview. Walking start was acknowledged at 12:04:09.891 UTC and stop at 12:05:12.899 UTC. The 60-second measured window was `[t_g + 2 s, t_g + 62 s]`.

| Measure | Result |
|---|---:|
| Measured frames / errors | 585 / 0 |
| Mean / P95 callback latency | 96.75 / 181.19 ms |
| Effective FPS | 9.75 frames/s |
| Mean process CPU | 1332.64% of one logical CPU |
| Mean process RSS | 367.92 MiB |
| Maximum head displacement | 0.001534 rad (about one count) |
| Maximum body joint displacement | 0.276251 rad |

Ball and robot each appeared in 585/585 measured frames (100%); goal in 541/585 (92.5%). This is **output coverage**, not labeled accuracy or precision. Median confidence and tracker ID counts are in the [detection table](detection_table.csv). Gait guard, two mid-gait samples, and two post-stop samples support leg motion and bounded head movement. Initial CPU package temperature was 81 °C. A 50 °C reading at 12:11:36 UTC is saved as a delayed diagnostic, **not** an end-of-run temperature.

Evidence: [during gait](frame_deteksi_saat_gait.png), [after the window](frame_deteksi_sesudah_jendela.png), [metric summary](summary_metrics.json), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class output graph](class_outputs_graph_en.png), `gait_guard.json`, and `head_guard_samples.csv`. Local raw logs: `runs/op3_pytorch/20261102_eq_teacher_walk_retest_u2.*`. Final preview-continuity and physical-condition audit remains.
