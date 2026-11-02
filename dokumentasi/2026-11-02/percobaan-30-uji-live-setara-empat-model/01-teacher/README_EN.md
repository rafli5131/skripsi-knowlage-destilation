# Teacher: idle and walking — active set

## Data provenance

The three idle runs remain as previously recorded. At Bhre's request, walking display slot 1 uses previous raw run 20261102_eq_teacher_walk_u3; slots 2 and 3 use new raw runs 20261102_eq_teacher_walk_retest_u2 and 20261102_eq_teacher_walk_retest_u3. Raw run IDs and timestamps were not changed. See [active_run_sources.json](../active_run_sources.json) and the [previous-set archive](arsip-set-sebelumnya-20261102-1200/).

## Walking, active set

The operator attended the robot in walk-ready pose with the step area clear. Head pan/tilt modules remained none and received no position commands. All three gait runs received start and stop acknowledgments; each 60-second measurement window was inside the walking period. The new runs were spaced by more than 120 seconds.

| Slot | Raw source | Frames | Mean latency (ms) | P95 (ms) | FPS | Process CPU (% of one CPU) | RSS (MiB) | Goal output |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [1](walk-u1/README_EN.md) | previous u3 | 589 | 96.41 | 180.86 | 9.80 | 1329.97 | 371.36 | 561/589 (95.2%) |
| [2](walk-u2/README_EN.md) | retest_u2 | 585 | 96.75 | 181.19 | 9.75 | 1332.64 | 367.92 | 541/585 (92.5%) |
| [3](walk-u3/README_EN.md) | retest_u3 | 604 | 94.40 | 180.01 | 10.07 | 1337.99 | 377.97 | 574/604 (95.0%) |

Across three repetitions, mean ± sample SD was **95.85 ± 1.27 ms** for mean latency, **9.87 ± 0.17 FPS**, **1333.54 ± 4.08%** of one logical CPU for process CPU, and **372.42 ± 5.11 MiB** RSS. Pooled median and P95 latency across 1,778 frames were **77.02** and **180.66 ms**. Ball and robot appeared in every measured frame; goal appeared in 1,676/1,778 (94.3%). These are **detection output coverage, not accuracy or precision**.

All three walking runs passed automatic CSV and joint-sample checks. Maximum head displacement was about one encoder count from each run's starting pose; no head position command was sent. See the [2880×1800 three-run performance chart](graph_teacher_walk_repetitions_1_2_3_hd.png), [2700×1080 coverage and confidence chart](graph_output_coverage_confidence_teacher_walk_hd.png), [aggregate table](../05-ringkasan/tabel_agregat_saat_ini.csv), and [accuracy/precision interpretation](../05-ringkasan/ACCURACY_PRECISION_NOTE_EN.md). Final preview-continuity and physical-condition audit remains.

The active walking set was selected after the old goal-output results were known and the goal was repositioned. Its 94.3% output coverage may therefore be optimistic relative to all runs collected. Include the archive and selection rule in the thesis.

## Idle

The three idle runs contain 1,779 measured frames. Mean ± sample SD across repetitions was **96.24 ± 3.60 ms** mean latency, **9.88 ± 0.31 FPS**, **1338.90 ± 9.65%** of one logical CPU for process CPU, and **370.58 ± 1.29 MiB** RSS. See [idle run 1](idle-u1/README_ID.md), [idle run 2](idle-u2/README_ID.md), and [idle run 3](idle-u3/README_ID.md). Idle-versus-walking comparisons are descriptive; three repetitions do not support a claim of statistical significance.
