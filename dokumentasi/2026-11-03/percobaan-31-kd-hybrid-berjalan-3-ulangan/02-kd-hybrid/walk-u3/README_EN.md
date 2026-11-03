# KD Hybrid walking — repetition 3 (3 November 2026)

Checkpoint and inference settings matched the previous repetitions. The SSH-X preview received fresh, error-free frames before gait, with all three object outputs in 50/50 frames. Gait start was acknowledged at **05:11:52.970 UTC** and stop at **05:12:55.979 UTC**. No position command was sent to head IDs 19/20; maximum deviation was **one count**. Automatic CSV/joint checks passed.

| Measured frames | Mean latency | P95 | Effective FPS | Process CPU | RSS | Goal output |
|---:|---:|---:|---:|---:|---:|---:|
| 726 | 74.32 ms | 161.78 ms | 12.12 | 1304.03% of one logical CPU | 356.76 MiB | 717/726 frames (98.8%) |

Ball and robot outputs appeared in all 726 frames. The largest received-frame gap was 0.539 seconds and no frame error was recorded. Output frequency is **not labeled accuracy**. See the [overlay](frame_deteksi_sesudah_jendela.png), [HD runtime chart](grafik_runtime_hd.png), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class-output graph](class_outputs_graph_en.png), [performance table](performance_table.csv), [detection table](detection_table.csv), [pre-gait JointState](telemetry_pre.txt), [post-stop JointState](telemetry_after.txt), [summary](summary_metrics.json), and [gait guard](gait_guard.json). Raw frame logs remain local at `runs/op3_pytorch/20261103_eq_hybrid1337_walk_u3.*`.
