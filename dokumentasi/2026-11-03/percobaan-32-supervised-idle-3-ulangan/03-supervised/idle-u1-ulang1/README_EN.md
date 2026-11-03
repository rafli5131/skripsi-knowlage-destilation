# Supervised idle slot 1 — first replacement

Run `20261103_eq_sup1337_idle_u1_ulang1` was recorded because the [original repetition](../idle-u1/README_EN.md) requires review. Inference and preview settings were unchanged; the window was 06:10:45–06:11:45 UTC. No robot motion command was sent.

| Measure | Result |
|---|---:|
| Measured frames / errors | 744 / 0 |
| Mean / P95 latency | 72.13 / 162.88 ms |
| Effective FPS | 12.41 frames/s |
| Process CPU | 1301.13% of one logical CPU |
| Process RSS | 353.32 MiB |
| Maximum sampled head / body deviation | 1 / 3 counts |

Automated status: **`perlu_audit`**. Right shoulder pitch shifted three counts in the first mid-window and first post-window samples. This replacement also exceeds the two-count idle limit, so it does not replace slot 1 in the main table. All three classes had model outputs in 744/744 frames; **output coverage is not labeled accuracy**.

Evidence: [overlay](frame_deteksi_sesudah_jendela.png), [metrics](summary_metrics.json), [performance table](performance_table.csv), [detection table](detection_table.csv), [runtime graph](grafik_runtime_hd.png), [CPU/RAM graph](cpu_ram_graph_en.png), and [pre](telemetry_pre.txt), [mid-1](telemetry_mid1.txt), [mid-2](telemetry_mid2.txt), [post-1](telemetry_after.txt), [post-2](telemetry_after2.txt) telemetry. Local raw logs: `runs/op3_pytorch/20261103_eq_sup1337_idle_u1_ulang1.*`.
