# Supervised walking — repetition 1

The operator confirmed readiness before `20261103_eq_sup1337_walk_u1`. The test used SSH-X preview, the 640×480 OP3 camera, CPU FP32, and BoT-SORT. Walking start and stop were acknowledged at 09:47:48 and 09:48:51 UTC. Head joints 19/20 received no position command; maximum sampled deviation was one encoder count.

The 60-second window contained 742 frames and zero errors: mean/P95 latency 71.65/161.84 ms, effective FPS 12.36, process CPU 1296.41% of one logical CPU, and RSS 361.63 MiB. Automated CSV/telemetry checks passed; final protocol review remains open. Class output coverage in the [detection table](detection_table.csv) is not labeled accuracy.

Evidence: [before overlay](preview_sebelum_run.png), [after overlay](frame_deteksi_sesudah_jendela.png), [metrics](summary_metrics.json), [gait guard](gait_guard.json), [performance table](performance_table.csv), [latency graph](latency_graph_en.png), [CPU/RAM graph](cpu_ram_graph_en.png), and [joint samples](head_guard_samples.csv).
