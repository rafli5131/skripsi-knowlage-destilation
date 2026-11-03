# Supervised seed 1337 — idle repetition 1

Run `20261103_eq_sup1337_idle_u1` used the OP3 640×480 camera, CPU FP32, BoT-SORT, confidence 0.25, NMS IoU 0.45, four intra-op and two inter-op threads, 30 warm-up frames, and an active SSH-X preview. The 60-second measurement window was 05:59:09–06:00:09 UTC. No robot motion command was sent.

| Measure | Result |
|---|---:|
| Measured frames / errors | 729 / 0 |
| Mean / P95 callback latency | 72.50 / 159.81 ms |
| Effective FPS | 12.15 frames/s |
| Mean process CPU | 1296.01% of one logical CPU |
| Mean process RSS | 355.58 MiB |
| Maximum sampled head deviation | 0.001534 rad (1 count) |
| Maximum sampled body deviation | 0.006139 rad (4 counts) |

All three classes had model outputs in 729/729 measured frames. This is **output coverage, not labeled accuracy**. The right shoulder pitch changed by four counts in the second **post-window** sample, so the automated status is `perlu_audit`. Both mid-window samples had at most one count of body movement. The original run is retained and must not be treated as a valid repetition without resolving the deviation.

Evidence: [post-window overlay](frame_deteksi_sesudah_jendela.png), [metrics](summary_metrics.json), [performance table](performance_table.csv), [detection table](detection_table.csv), [runtime graph](grafik_runtime_hd.png), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class-output graph](class_outputs_graph_en.png), and [pre](telemetry_pre.txt), [mid-1](telemetry_mid1.txt), [mid-2](telemetry_mid2.txt), [post-1](telemetry_after.txt), [post-2](telemetry_after2.txt) telemetry. Local raw logs: `runs/op3_pytorch/20261103_eq_sup1337_idle_u1.*`.
