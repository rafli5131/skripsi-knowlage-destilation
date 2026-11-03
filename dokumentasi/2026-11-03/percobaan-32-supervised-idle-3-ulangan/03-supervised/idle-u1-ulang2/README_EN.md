# Supervised idle slot 1 — second replacement, active run

Run `20261103_eq_sup1337_idle_u1_ulang2` was recorded after the [original repetition](../idle-u1/README_EN.md) and [first replacement](../idle-u1-ulang1/README_EN.md) exceeded the body deviation limit. Checkpoint, camera, BoT-SORT, thresholds, threads, warm-up, and preview were unchanged. The window was 06:17:51–06:18:51 UTC; no robot motion command was sent.

| Measure | Result |
|---|---:|
| Measured frames / errors | 719 / 0 |
| Mean / P95 latency | 74.48 / 161.82 ms |
| Effective FPS | 12.00 frames/s |
| Process CPU | 1300.69% of one logical CPU |
| Process RSS | 354.96 MiB |
| Maximum sampled head / body deviation | 0 / 1 count |

Automated status: **`lulus_cek_otomatis`**. This is the active slot-1 run based on telemetry criteria, not performance values. The earlier runs remain preserved. Ball, goal, and robot each had model outputs in 719/719 frames; **output coverage is not labeled accuracy**. Final protocol review remains open.

Evidence: [pre-run overlay](preview_sebelum_run.png), [post-window overlay](frame_deteksi_sesudah_jendela.png), [metrics](summary_metrics.json), [performance table](performance_table.csv), [detection table](detection_table.csv), [runtime graph](grafik_runtime_hd.png), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class-output graph](class_outputs_graph_en.png), and [pre](telemetry_pre.txt), [mid-1](telemetry_mid1.txt), [mid-2](telemetry_mid2.txt), [post-1](telemetry_after.txt), [post-2](telemetry_after2.txt) telemetry. Local raw logs: `runs/op3_pytorch/20261103_eq_sup1337_idle_u1_ulang2.*`.
