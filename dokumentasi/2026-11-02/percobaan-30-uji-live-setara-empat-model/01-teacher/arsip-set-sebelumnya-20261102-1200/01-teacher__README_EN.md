# Teacher: idle and walking

Three idle repetitions and three walking repetitions were recorded on 2 November 2026 using the FP32 teacher, 640×480 OP3 camera, BoT-SORT, and SSH-X preview. No head position command was sent: the walking module controlled body joints, while head pan/tilt modules remained `none`.

| Condition / run | Frames | Mean latency (ms) | P95 (ms) | Effective FPS | Process CPU (% of one CPU) | RSS (MiB) | Goal output |
|---|---:|---:|---:|---:|---:|---:|---:|
| [Idle 1](idle-u1/README_ID.md) | 584 | 98.91 | 180.21 | 9.72 | 1329.91 | 370.03 | 584/584 |
| [Idle 2 replacement](idle-u2/README_ID.md) | 614 | 92.15 | 181.84 | 10.24 | 1349.11 | 369.66 | 614/614 |
| [Idle 3](idle-u3/README_ID.md) | 581 | 97.67 | 181.73 | 9.69 | 1337.67 | 372.06 | 581/581 |
| [Walking 1](walk-u1/README_EN.md) | 611 | 90.88 | 181.31 | 10.19 | 1338.94 | 375.68 | 112/611 |
| [Walking 2](walk-u2/README_EN.md) | 574 | 98.79 | 180.36 | 9.56 | 1322.74 | 371.13 | 362/574 |
| [Walking 3](walk-u3/README_EN.md) | 589 | 96.41 | 180.86 | 9.80 | 1329.97 | 371.36 | 561/589 |

Across the three walking runs, mean ± sample SD was **95.36 ± 4.06 ms** for mean latency, **9.85 ± 0.32 FPS**, **1330.55 ± 8.11%** of one logical CPU for process CPU, and **372.73 ± 2.56 MiB** RSS. Pooled median and P95 latency across 1,774 measured frames were **76.67 ms** and **180.85 ms**. Ball and robot appeared in every measured walking frame; goal appeared in 1,035/1,774 (58.3%). Output coverage is **not labeled accuracy**.

All three walking runs passed automatic CSV and sampled-joint checks. Maximum head displacement was about one encoder count. Walking run 1 lacks an overlay screenshot after its measurement window and before detector exit; see the [deviation log](../log_penyimpangan.md). Final protocol audit still needs preview continuity, temperature, and physical-condition review. These three repetitions support descriptive results only; they do not establish statistical significance. See the [2880×1800 three-run chart](graph_teacher_walk_repetitions_1_2_3_hd.png) and [24-run matrix](../05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png).

The goal's relative position and output coverage were not proven identical across repetitions, so between-run runtime differences cannot be attributed solely to robot motion. After run 3, head pan matched the initial run-1 reading; tilt differed by 0.001534 rad (about one count). Walking has stopped and the teacher monitoring preview remains active.
