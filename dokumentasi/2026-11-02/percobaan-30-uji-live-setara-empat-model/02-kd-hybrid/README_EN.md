# KD Hybrid full seed 1337 — three idle repetitions

All three runs used the same KD Hybrid full seed 1337 checkpoint, 640×480 OP3 camera, CPU FP32, BoT-SORT, confidence 0.25, NMS IoU 0.45, active SSH-X preview, 30 warm-up frames, and a 60-second measurement window. The robot received no gait or head position commands; `op3_manager` was active. Runs were spaced by over 120 seconds. All passed automatic CSV/joint checks; final protocol audit of preview continuity and physical conditions remains.

| Repetition | Frames | Mean latency (ms) | P95 (ms) | FPS | Process CPU (% of one CPU) | RSS (MiB) | Goal output |
|---|---:|---:|---:|---:|---:|---:|---:|
| [1](idle-u1/README_EN.md) | 792 | 66.82 | 157.52 | 13.20 | 1303.85 | 358.63 | 784/792 (99.0%) |
| [2](idle-u2/README_EN.md) | 825 | 63.08 | 161.77 | 13.75 | 1302.47 | 357.76 | 816/825 (98.9%) |
| [3](idle-u3/README_EN.md) | 830 | 64.21 | 162.58 | 13.85 | 1311.58 | 360.21 | 821/830 (98.9%) |

Mean ± sample SD across repetitions was **64.70 ± 1.92 ms** mean latency, **13.60 ± 0.35 FPS**, **1305.97 ± 4.91%** of one logical CPU for process CPU, and **358.87 ± 1.24 MiB** RSS. Pooled median and P95 latency across 2,447 frames were **50.53 ms** and **161.76 ms**. Ball and robot appeared in every frame; goal in **2,421/2,447 (98.9%)**. This is model output coverage, **not labeled accuracy or precision**.

See the [2880×1800 three-run performance chart](graph_hybrid1337_idle_repetitions_1_2_3_hd.png), [2700×1080 output coverage and confidence chart](graph_output_coverage_confidence_hybrid1337_idle_hd.png), [session aggregate table](../05-ringkasan/tabel_agregat_saat_ini.csv), and [24-run matrix](../05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png). Confidence is not precision. Local raw logs remain in `runs/op3_pytorch/20261102_eq_hybrid1337_idle_u{1,2,3}.*`.
