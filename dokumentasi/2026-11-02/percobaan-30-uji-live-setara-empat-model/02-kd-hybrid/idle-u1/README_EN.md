# KD Hybrid full seed 1337 — idle repetition 1

Raw run `20261102_eq_hybrid1337_idle_u1` used the 640×480 OP3 camera, CPU FP32, BoT-SORT, confidence 0.25, NMS IoU 0.45, and active SSH-X preview. The robot received no gait or head position commands. The measured 60-second window was 12:44:04.464–12:45:04.464 UTC after 30 warm-up frames.

| Measure | Result |
|---|---:|
| Measured frames / errors | 792 / 0 |
| Mean / P95 callback latency | 66.82 / 157.52 ms |
| Effective FPS | 13.20 frames/s |
| Mean process CPU | 1303.85% of one logical CPU |
| Mean process RSS | 358.63 MiB |
| Maximum head displacement | 0.001534 rad (about one count) |
| Maximum body displacement | 0.001535 rad |

Detection output coverage was ball 792/792 frames (100%), goal 784/792 (99.0%), and robot 792/792 (100%). This is not labeled accuracy, precision, or recall. Five joint samples (`pre`, two mid-run, two post-window) and their [capture times](sampling_times.json) were saved. Automatic CSV/joint checks passed; final preview-continuity and physical-condition audit remains.

Evidence: [pre-run overlay](preview_sebelum_run.png), [post-window overlay](frame_deteksi_sesudah_jendela.png), [metric summary](summary_metrics.json), [performance table](performance_table.csv), [detection table](detection_table.csv), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), and [class-output graph](class_outputs_graph_en.png). Local raw logs: `runs/op3_pytorch/20261102_eq_hybrid1337_idle_u1.*`.
