# KD Hybrid full seed 1337 — idle repetition 3

Raw run `20261102_eq_hybrid1337_idle_u3` used the 640×480 OP3 camera, CPU FP32, BoT-SORT, confidence 0.25, NMS IoU 0.45, and active SSH-X preview. The robot received no gait or head position commands. The 60-second measurement window was 12:51:40.572–12:52:40.572 UTC after 30 warm-up frames; the gap from the previous run exceeded 120 seconds.

| Measure | Result |
|---|---:|
| Measured frames / errors | 830 / 0 |
| Mean / P95 callback latency | 64.21 / 162.58 ms |
| Effective FPS | 13.85 frames/s |
| Mean process CPU | 1311.58% of one logical CPU |
| Mean process RSS | 360.21 MiB |
| Maximum head displacement | 0.001534 rad (about one count) |
| Maximum body displacement | 0.001535 rad |

Detection output coverage was ball 830/830 frames (100%), goal 821/830 (98.9%), and robot 830/830 (100%). This is not labeled accuracy or precision. Five joint samples and their [capture times](sampling_times.json) were saved. Automatic CSV/joint checks passed; final preview-continuity and physical-condition audit remains.

Evidence: [pre-run overlay](preview_sebelum_run.png), [post-window overlay](frame_deteksi_sesudah_jendela.png), [metric summary](summary_metrics.json), [performance table](performance_table.csv), [detection table](detection_table.csv), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), and [class-output graph](class_outputs_graph_en.png). Local raw logs: `runs/op3_pytorch/20261102_eq_hybrid1337_idle_u3.*`.
