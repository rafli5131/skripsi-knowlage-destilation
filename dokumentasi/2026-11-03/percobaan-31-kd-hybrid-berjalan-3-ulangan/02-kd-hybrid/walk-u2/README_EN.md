# KD Hybrid walking — repetition 2 (3 November 2026)

Checkpoint and inference settings matched repetition 1. The SSH-X preview had fresh, error-free frames, with ball, goal, and robot outputs in 50/50 pre-run frames. Gait start was acknowledged at **05:08:07.795 UTC** and stop at **05:09:10.810 UTC**. Head IDs 19/20 remained on module `none` without position commands; maximum deviation was **one count**. Automatic CSV/joint checks passed.

| Measured frames | Mean latency | P95 | Effective FPS | Process CPU | RSS | Goal output |
|---:|---:|---:|---:|---:|---:|---:|
| 758 | 71.72 ms | 160.74 ms | 12.64 | 1307.51% of one logical CPU | 354.03 MiB | 745/758 frames (98.3%) |

Ball and robot outputs appeared in all 758 frames. The largest received-frame gap was 0.519 seconds and no frame error was recorded. Output frequency is **not labeled accuracy**. See the [overlay](frame_deteksi_sesudah_jendela.png), [HD runtime chart](grafik_runtime_hd.png), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class-output graph](class_outputs_graph_en.png), [performance table](performance_table.csv), [detection table](detection_table.csv), [pre-gait JointState](telemetry_pre.txt), [post-stop JointState](telemetry_after.txt), [summary](summary_metrics.json), and [gait guard](gait_guard.json). Raw frame logs remain local at `runs/op3_pytorch/20261103_eq_hybrid1337_walk_u2.*`.
