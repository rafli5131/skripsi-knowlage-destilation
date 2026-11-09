# Audit of 24 OP3 runs

> Update, 5 November 2026: [T38 for four models on 260 OP3 frames](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) is complete; the T38 status in this 3 November audit is historical.

**Decision:** the user accepted these runs for descriptive runtime analysis with the documented limitations. Supervisor approval has not been recorded; physical equivalence is not established. See [the user's decision](KEPUTUSAN_PENGGUNA.md).

All 24 active runs passed the checks performed on raw logs and available sampled telemetry. The audit verifies checkpoint hashes, inference settings, measurement windows, timestamps and reported metrics; all 12 walking runs have start/stop acknowledgments. This does not establish full physical equivalence across sessions.

Results: [per-run T36](../../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md), [summary T37](../../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md), [English HD graph](grafik_runtime_24_run_en_hd.png), [telemetry audit](audit_telemetry.csv), and [inactive/replaced runs](T36_lampiran_run_tidak_aktif.csv).

Runs were collected in model blocks over two days. Some teacher walking runs were selected after observing goal coverage; two teacher idle runs lack the specified post-window screenshot, and one Hybrid walking pre-snapshot contains six joints. Direct torque verification, screen video, complete scene measurements and some temperatures are unavailable. Results are descriptive and final protocol review remains open.

The 200 primary, 60 negative and 50 partial images match their recorded image/label hashes; review logs cover all manifest frames with reviewer `bhre`. Initial annotations were assisted by Pure KD; the 50 partial-goal frames are excluded from the main 260-frame analysis. T34 compares two models on that exploratory set; a four-model T38 has not been run in this audit.
