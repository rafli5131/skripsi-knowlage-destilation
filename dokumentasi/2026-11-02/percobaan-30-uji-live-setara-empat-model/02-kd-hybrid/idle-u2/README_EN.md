# KD Hybrid full seed 1337 — idle repetition 2

Raw run `20261102_eq_hybrid1337_idle_u2` used the 640×480 OP3 camera, CPU FP32, BoT-SORT, confidence 0.25, NMS IoU 0.45, and active SSH-X preview. The robot received no gait or head position commands. The 60-second measurement window was 12:47:50.865–12:48:50.865 UTC after 30 warm-up frames; the gap from the previous run exceeded 120 seconds.

| Measure | Result |
|---|---:|
| Measured frames / errors | 825 / 0 |
| Mean / P95 callback latency | 63.08 / 161.77 ms |
| Effective FPS | 13.75 frames/s |
| Mean process CPU | 1302.47% of one logical CPU |
| Mean process RSS | 357.76 MiB |
| Maximum sampled head displacement | 0 rad |
| Maximum body displacement | 0.001535 rad |

Detection output coverage was ball 825/825 frames (100%), goal 816/825 (98.9%), and robot 825/825 (100%). This is not labeled accuracy or precision. Five joint samples and their [capture times](sampling_times.json) were saved. Automatic CSV/joint checks passed; final preview-continuity and physical-condition audit remains.

Evidence: [pre-run overlay](preview_sebelum_run.png), [post-window overlay](frame_deteksi_sesudah_jendela.png), [metric summary](summary_metrics.json), [performance table](performance_table.csv), [detection table](detection_table.csv), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), and [class-output graph](class_outputs_graph_en.png). Local raw logs: `runs/op3_pytorch/20261102_eq_hybrid1337_idle_u2.*`.
