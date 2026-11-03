# Experiment 32 — Supervised idle, three active repetitions

Three Supervised seed-1337 idle slots were measured on 3 November 2026 with SSH-X preview and no robot motion commands. The active runs passed automated CSV and sampled telemetry checks. Earlier runs exceeding the joint-deviation limit remain available in the [deviation log](log_penyimpangan.md); replacements were selected by protocol criteria.

Across the three active runs, mean ± sample SD was **73.12 ± 3.27 ms latency**, **12.14 ± 0.29 FPS**, **1299.18 ± 3.32% process CPU of one logical CPU**, and **355.93 ± 3.32 MiB RSS**, across 2,185 measured frames with zero frame errors. Detection coverage is not labeled accuracy. See the [Indonesian summary](README_ID.md), [English HD graph](03-supervised/graph_sup1337_idle_repetitions_1_2_3_hd.png), and [source table](05-ringkasan/tabel_3_run.csv).

The campaign has **15 of 24 slots measured and passing automatic checks**; nine remain. Final protocol audit remains open: torque was not directly read while the manager owned the bus, and external scene photographs, distances, and raw before/after reference frames were not collected for this session.
