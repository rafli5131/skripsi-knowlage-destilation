# Trial 30: matched live OP3 evaluation

As of **3 November 2026, 12 of 24 planned slots** have been measured. Teacher idle/walking and KD Hybrid full seed 1337 idle were completed on 2 November; [three KD Hybrid walking runs](../../2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/README_EN.md) were completed on 3 November. **Twelve Supervised and pure-KD slots** remain. The tests used a 640×480 OP3 camera, BoT-SORT, and active SSH-X preview. No labeled detection accuracy was measured for these live runs.

At Bhre's request, the active teacher walking set was rearranged: displayed repetition 1 uses the previous raw repetition-3 run, followed by two newly recorded repetitions. The [source mapping](active_run_sources.json) preserves raw IDs and timestamps. The [previous-set archive](01-teacher/arsip-set-sebelumnya-20261102-1200/) retains the old artifacts. No raw log was overwritten or relabeled internally.

| Model / condition | Completed repetitions | Remaining |
|---|---:|---:|
| Teacher idle | 3 | 0 |
| Teacher walking | 3 | 0 |
| KD Hybrid idle | 3 | 0 |
| KD Hybrid walking, 3 November | 3 | 0 |
| Four Supervised/pure-KD pairs | 0 | 12 |

See the [teacher summary](01-teacher/README_EN.md), [24-run schedule](jadwal_run.csv), [24-slot table](05-ringkasan/tabel_24_run.csv), [2880×1800 matrix](05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png), [three-run walking chart](01-teacher/graph_teacher_walk_repetitions_1_2_3_hd.png), and [accuracy/precision note](05-ringkasan/ACCURACY_PRECISION_NOTE_EN.md). Blue matrix points passed automatic CSV and joint-sample checks; × denotes an unmeasured slot. Final protocol audit still needs preview-continuity, temperature, and physical-condition review. All active gait runs received stop acknowledgments; the KD Hybrid monitoring preview was relaunched after the final idle run. Check process status before resuming.

The [KD Hybrid idle summary](02-kd-hybrid/README_EN.md) and [3 November walking summary](../../2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/02-kd-hybrid/README_EN.md) contain three-run tables, HD graphs, and per-run image evidence. The last verified preview after the walking tests used **KD Hybrid**.

The [2 November progress log](log_progres.md) records the first nine measurement windows and raw IDs; the [3 November log](../../2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/log_penyimpangan.md) records the next three walking runs. The [2 November memory](../../../memory/2026-11-02-uji-live-setara-op3-9-dari-24.md) is a historical 9/24 snapshot; the [3 November memory](../../../memory/2026-11-03-kd-hybrid-berjalan-12-dari-24.md) records the 12/24 status.
