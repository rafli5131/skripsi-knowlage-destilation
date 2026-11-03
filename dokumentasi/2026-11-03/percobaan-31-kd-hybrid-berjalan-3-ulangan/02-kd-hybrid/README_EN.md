# KD Hybrid full seed 1337 — three walking repetitions

The 3 November 2026 measurements used the OP3 C920 camera at 640×480, CPU FP32, BoT-SORT, confidence 0.25, NMS IoU 0.45, four intra-op and two inter-op threads, 30 warm-up frames, a 60-second analysis window, and an active SSH-X preview. `op3_manager` ran with `auto_start_init_pose=false`; the head module stayed `none`. No position command was sent to IDs 19/20. Before **each** run the operator confirmed walk-ready pose, a clear step area, and attendance. Gait-stop intervals exceeded 120 seconds.

| Repetition | Frames | Mean latency (ms) | P95 (ms) | Effective FPS | Process CPU (% of one logical CPU) | RSS (MiB) | Frames with goal output |
|---|---:|---:|---:|---:|---:|---:|---:|
| [1](walk-u1/README_EN.md) | 772 | 68.37 | 158.92 | 12.87 | 1299.77 | 358.13 | 721/772 (93.4%) |
| [2](walk-u2/README_EN.md) | 758 | 71.72 | 160.74 | 12.64 | 1307.51 | 354.03 | 745/758 (98.3%) |
| [3](walk-u3/README_EN.md) | 726 | 74.32 | 161.78 | 12.12 | 1304.03 | 356.76 | 717/726 (98.8%) |

Mean ± sample SD across the **three run means**: latency **71.47 ± 2.98 ms**, FPS **12.54 ± 0.38**, process CPU **1303.77 ± 3.88%** of one logical CPU, and RSS **356.31 ± 2.09 MiB**. The runs contain 2,256 analyzed frames. Ball and robot outputs appeared in 2,256/2,256 frames; goal output appeared in 2,183/2,256 (**96.8%**). Output coverage is **not precision, recall, or mAP**. All three runs had zero frame errors, received-frame maximum gaps of 0.556/0.519/0.539 seconds, acknowledged gait stops, and at most one encoder count of head movement.

See the [2880×1800 three-run chart](graph_hybrid1337_walk_repetitions_1_2_3_hd.png), [2700×1080 output/confidence chart](graph_output_coverage_confidence_hybrid1337_walk_hd.png), [three-run table](../05-ringkasan/tabel_3_run.csv), and [aggregate](../05-ringkasan/tabel_agregat_saat_ini.csv). The [cross-day 12/24 matrix](../../../2026-11-02/percobaan-30-uji-live-setara-empat-model/05-ringkasan/tabel_24_run.csv) combines these runs with the nine runs from 2 November.

**Audit limits:** Repetition 1 uses a real six-joint pre-gait guard sample rather than a full JointState; see its [provenance](walk-u1/telemetry_pre_provenance.json). Repetitions 2/3 have full 20-joint pre-gait snapshots. CPU temperature was sampled from sysfs before each run; head-servo temperature was not monitored during gait, and OpenCR voltage was measured only during preparation. The viewer was not screen-recorded; fresh CSV frames, frame gaps, and an open viewer support the preview-continuity observation. Automatic checks passing does not establish final scene or protocol equivalence.
