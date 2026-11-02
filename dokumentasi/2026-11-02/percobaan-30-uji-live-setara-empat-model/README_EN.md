# Trial 30: matched live OP3 evaluation

As of 2 November 2026, **9 of 24 planned slots** across four models, two robot conditions, and three repetitions have been measured. Teacher idle, teacher walking, and KD Hybrid full seed 1337 idle each have three runs; the remaining 15 slots are unmeasured. The tests used a 640×480 OP3 camera, BoT-SORT, and active SSH-X preview. No labeled detection accuracy was measured for these live runs.

At Bhre's request, the active teacher walking set was rearranged: displayed repetition 1 uses the previous raw repetition-3 run, followed by two newly recorded repetitions. The [source mapping](active_run_sources.json) preserves raw IDs and timestamps. The [previous-set archive](01-teacher/arsip-set-sebelumnya-20261102-1200/) retains the old artifacts. No raw log was overwritten or relabeled internally.

| Model / condition | Completed repetitions | Remaining |
|---|---:|---:|
| Teacher idle | 3 | 0 |
| Teacher walking | 3 | 0 |
| KD Hybrid idle | 3 | 0 |
| Five other model-condition pairs | 0 | 15 |

See the [teacher summary](01-teacher/README_EN.md), [24-run schedule](jadwal_run.csv), [24-slot table](05-ringkasan/tabel_24_run.csv), [2880×1800 matrix](05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png), [three-run walking chart](01-teacher/graph_teacher_walk_repetitions_1_2_3_hd.png), and [accuracy/precision note](05-ringkasan/ACCURACY_PRECISION_NOTE_EN.md). Blue matrix points passed automatic CSV and joint-sample checks; × denotes an unmeasured slot. Final protocol audit still needs preview-continuity, temperature, and physical-condition review. All active gait runs received stop acknowledgments; the KD Hybrid monitoring preview was relaunched after the final idle run. Check process status before resuming.

The [KD Hybrid idle summary](02-kd-hybrid/README_EN.md) contains three-run tables, HD graphs, and per-run image evidence. The last verified preview after these idle tests used **KD Hybrid**.

The [chronological progress log](log_progres.md) records the nine measurement windows and raw run IDs. The [2 November memory](../../../memory/2026-11-02-uji-live-setara-op3-9-dari-24.md) summarizes results, interpretation limits, and the 15 remaining slots.
