# T26. tradeoff utama

Status: Sebagian; akurasi TEST offline ada, runtime OP3 hanya KD seed 42 idle; walking dan benchmark frame tetap belum ada.

| model | method | TEST_mAP50_95 | TEST_F1 | fixed_frame_latency_median [ms] | servo_idle_effective_FPS [frame/s] | walking_effective_FPS [frame/s] | servo_idle_CPU_median [percent] | servo_idle_RSS_median [MiB] | parameters [count] | GFLOPs_640 | runtime_scope | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kd_seed42 | Pure KD | 0,674424 | 0,839511 | [BELUM DIUKUR] | 24,901 | [BELUM DIUKUR] | 1022,2 | 381,7 | 810649 | 2,429 | OP3 idle protocol only for KD seed42 | artifacts/thesis_analysis_final_corrected/per_model.csv; runs/op3_idle_trial/20261019T123737Z_023704/frames.csv |
| supervised_seed42 | Supervised student | 0,720267 | 0,909509 | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | 810649 | 2,429 | offline TEST only | artifacts/thesis_analysis_final_corrected/per_model.csv |
| teacher_fp32 | Teacher | 0,77998 | 0,928979 | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | 2590425 | 6,502 | offline TEST only | artifacts/thesis_analysis_final_corrected/per_model.csv |

Sumber: artifacts/thesis_analysis_final_corrected/per_model.csv; runs/op3_idle_trial/20261019T123737Z_023704/frames.csv; runs/op3_idle_trial/20261019T123737Z_023704/summary.json

Metrik TEST berasal dari dataset berlabel, bukan akurasi kamera OP3. FPS/CPU/RSS hanya dari sesi servo_idle KD seed42 dengan preview X11; belum ada basis untuk membandingkan runtime antarvarian atau walking.
