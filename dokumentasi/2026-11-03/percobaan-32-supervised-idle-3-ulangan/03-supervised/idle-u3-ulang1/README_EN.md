# Supervised idle slot 3 — first replacement

Run `20261103_eq_sup1337_idle_u3_ulang1` was recorded because the [original slot-3 run](../idle-u3/README_EN.md) exceeded the body deviation limit. Checkpoint, camera, BoT-SORT, thresholds, threads, warm-up, and preview were unchanged. The window was 06:14:19–06:15:19 UTC; no robot motion command was sent.

| Measure | Result |
|---|---:|
| Measured frames / errors | 717 / 0 |
| Mean / P95 latency | 75.48 / 161.49 ms |
| Effective FPS | 11.94 frames/s |
| Process CPU | 1301.47% of one logical CPU |
| Process RSS | 353.19 MiB |
| Maximum sampled head / body deviation | 1 / 2 counts |

Automated status: **`lulus_cek_otomatis`**. This run replaces repetition 3 in the active matrix, while the original remains available for audit. Ball, goal, and robot each had model outputs in 717/717 frames. **Output coverage is not labeled accuracy.** Final protocol review remains open.

Evidence: [pre-run overlay](preview_sebelum_run.png), [post-window overlay](frame_deteksi_sesudah_jendela.png), [metrics](summary_metrics.json), [performance table](performance_table.csv), [detection table](detection_table.csv), [runtime graph](grafik_runtime_hd.png), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class-output graph](class_outputs_graph_en.png), and [pre](telemetry_pre.txt), [mid-1](telemetry_mid1.txt), [mid-2](telemetry_mid2.txt), [post-1](telemetry_after.txt), [post-2](telemetry_after2.txt) telemetry. Local raw logs: `runs/op3_pytorch/20261103_eq_sup1337_idle_u3_ulang1.*`.
