# Supervised seed 1337 — idle repetition 2

Run `20261103_eq_sup1337_idle_u2` used the same checkpoint, OP3 camera, CPU FP32, BoT-SORT, confidence 0.25, NMS IoU 0.45, 30 warm-up frames, and an active SSH-X preview. The 60-second window was 06:03:01–06:04:01 UTC. No robot motion command was sent.

| Measure | Result |
|---|---:|
| Measured frames / errors | 749 / 0 |
| Mean / P95 callback latency | 69.39 / 158.52 ms |
| Effective FPS | 12.47 frames/s |
| Mean process CPU | 1295.37% of one logical CPU |
| Mean process RSS | 359.63 MiB |
| Maximum sampled head / body deviation | 1 / about 2 encoder counts |

All five JointState samples contained 20 joints. The CSV/telemetry check returned `lulus_cek_otomatis`; final protocol review remains open. Ball, goal, and robot each appeared in 749/749 measured frames according to model output. **Output coverage is not labeled accuracy.**

Evidence: [pre-run overlay](preview_sebelum_run.png), [post-window overlay](frame_deteksi_sesudah_jendela.png), [metrics](summary_metrics.json), [performance table](performance_table.csv), [detection table](detection_table.csv), [runtime graph](grafik_runtime_hd.png), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class-output graph](class_outputs_graph_en.png), and [pre](telemetry_pre.txt), [mid-1](telemetry_mid1.txt), [mid-2](telemetry_mid2.txt), [post-1](telemetry_after.txt), [post-2](telemetry_after2.txt) telemetry. Local raw logs: `runs/op3_pytorch/20261103_eq_sup1337_idle_u2.*`.
