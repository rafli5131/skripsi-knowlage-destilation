# Experiment 35 — Pure KD walking

**Latest update:** [replacement repetition 3](04-kd-murni/walk-u3-ulang1/README_EN.md) passed automated checks and is now the active slot. The previous run and the summary below are retained as historical audit context. Across the three active runs: **72.65 ± 2.55 ms**, **12.21 ± 0.15 FPS**, **1295.65 ± 1.35% CPU of one logical CPU**, and **360.18 ± 4.69 MiB RSS**. All 24 active campaign slots pass automated checks; final protocol audit remains open.

Three Pure KD seed-42 walking repetitions were completed after operator confirmation for each run. All walking starts and stops were acknowledged; no head position commands were sent and maximum guard deviation was one encoder count. Runs [1](04-kd-murni/walk-u1/README_EN.md) and [2](04-kd-murni/walk-u2/README_EN.md) passed automated checks. Run [3](04-kd-murni/walk-u3/README_EN.md) remains **`perlu_audit`**: two automatically selected middle samples were close to baseline, although all 60 guard samples within the gait window show knee ranges of approximately 0.66 rad.

The three-run descriptive mean ± sample SD is **74.07 ± 0.68 ms latency**, **12.13 ± 0.03 FPS**, **1296.89 ± 0.81% process CPU of one logical CPU**, and **358.98 ± 5.26 MiB RSS**, over 2,183 frames without frame errors. These aggregates remain provisional pending audit of repetition 3. Detection output coverage is not labeled accuracy.

See the [Indonesian summary](README_ID.md), [three-run table](05-ringkasan/tabel_3_run.csv), and [English HD graph](04-kd-murni/graph_kd42_walk_repetitions_1_2_3_hd.png). All 24 slots have measurements; 23 pass automated checks and one requires audit.
