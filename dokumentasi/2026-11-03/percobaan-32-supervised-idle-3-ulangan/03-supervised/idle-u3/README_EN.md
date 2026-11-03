# Supervised seed 1337 — idle repetition 3

Run `20261103_eq_sup1337_idle_u3` used the same protocol as repetitions 1–2: OP3 640×480 camera, CPU FP32, BoT-SORT, confidence 0.25, NMS IoU 0.45, 30 warm-up frames, a 60-second measurement window, and an active SSH-X preview. The window was 06:06:35–06:07:35 UTC. No robot motion command was sent.

| Measure | Result |
|---|---:|
| Measured frames / errors | 746 / 0 |
| Mean / P95 callback latency | 71.47 / 159.53 ms |
| Effective FPS | 12.43 frames/s |
| Mean process CPU | 1300.11% of one logical CPU |
| Mean process RSS | 360.00 MiB |
| Maximum sampled head / body deviation | 1 / 3 encoder counts |

Automated status: **`perlu_audit`**. Right shoulder pitch shifted about 0.004604 rad (three counts) in both mid-window samples and the first post-window sample, exceeding the two-count idle limit. The original run is retained and must not be treated as a valid repetition without further review. Class output is in the [detection table](detection_table.csv); output coverage **is not labeled accuracy**.

Evidence: [pre-run overlay](preview_sebelum_run.png), [post-window overlay](frame_deteksi_sesudah_jendela.png), [metrics](summary_metrics.json), [performance table](performance_table.csv), [runtime graph](grafik_runtime_hd.png), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class-output graph](class_outputs_graph_en.png), and [pre](telemetry_pre.txt), [mid-1](telemetry_mid1.txt), [mid-2](telemetry_mid2.txt), [post-1](telemetry_after.txt), [post-2](telemetry_after2.txt) telemetry. Local raw logs: `runs/op3_pytorch/20261103_eq_sup1337_idle_u3.*`.
