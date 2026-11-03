# KD Hybrid walking — repetition 1 (3 November 2026)

KD Hybrid full seed 1337 ran on the OP3 640×480 camera with CPU FP32, BoT-SORT, active SSH-X preview, 30 warm-up frames, and a 60-second measurement window. Gait start was acknowledged at **05:00:43.821 UTC** and stop at **05:01:46.834 UTC**. No position command was sent to head IDs 19/20; maximum head deviation was **one encoder count**. Automatic CSV/joint checks passed; final protocol audit remains open.

| Measured frames | Mean latency | P95 | Effective FPS | Process CPU | RSS | Goal output |
|---:|---:|---:|---:|---:|---:|---:|
| 772 | 68.37 ms | 158.92 ms | 12.87 | 1299.77% of one logical CPU | 358.13 MiB | 721/772 frames (93.4%) |

Ball and robot outputs appeared in all 772 frames. Output frequency and confidence are **not labeled accuracy or precision**. The largest received-frame gap was 0.556 seconds; the SSH-X viewer remained open and the frame CSV advanced during gait. See the [post-window overlay](frame_deteksi_sesudah_jendela.png), [HD runtime chart](grafik_runtime_hd.png), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), [class-output graph](class_outputs_graph_en.png), [performance table](performance_table.csv), [detection table](detection_table.csv), [summary](summary_metrics.json), and [gait guard](gait_guard.json). Raw frame logs remain local at `runs/op3_pytorch/20261103_eq_hybrid1337_walk_u1.*`.

**Provenance limitation:** The [pre-gait telemetry](telemetry_pre.txt) was converted from a real guard sample at 05:00:21.193 UTC, about 22 seconds before gait acknowledgment. It contains the head and four leg joints, rather than all 20 joints; the [conversion metadata](telemetry_pre_provenance.json) is retained. The two post-stop JointState samples are complete. Do not describe the pre-gait file as a full 20-joint snapshot.
