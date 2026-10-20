# T22. aliran kamera

Status: Sebagian; laju subscriber probe ada, perbandingan kamera-saja versus detektor dengan protokol berpasangan belum ada.

| run_id | condition | protocol | camera_topic_rate_estimate [Hz] | subscriber_samples [frame] | processed_frame_rate [frame/s] | processed_frames [frame] | capture_gap_p50 [ms] | capture_gap_p95 [ms] | capture_gap_max [s] | gaps_over_1s [count] | with_detector | camera_only_comparison | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20261019T080757Z | unknown | legacy | [BELUM DIUKUR] | [BELUM DIUKUR] | 3,408 | 724 | 32,05 | 2004,15 | 7,317 | 62 | yes; KD seed 42 | [BELUM DIUKUR] | runs/op3_pytorch/20261019T080757Z.csv |
| 20261019T083428Z | unknown | legacy | [BELUM DIUKUR] | [BELUM DIUKUR] | 14,11 | 512 | 32,02 | 266,03 | 2,004 | 3 | yes; KD seed 42 | [BELUM DIUKUR] | runs/op3_pytorch/20261019T083428Z.csv |
| 20261019T084434Z | unknown | legacy | [BELUM DIUKUR] | [BELUM DIUKUR] | 15,898 | 887 | 32,04 | 232,08 | 1,404 | 3 | yes; KD seed 42 | [BELUM DIUKUR] | runs/op3_pytorch/20261019T084434Z.csv |
| 20261019T123737Z_023704 | servo_idle | idle_trial | [BELUM DIUKUR] | [BELUM DIUKUR] | 24,901 | 1501 | 32,04 | 68,01 | 0,668 | 0 | yes; KD seed 42 | [BELUM DIUKUR] | runs/op3_idle_trial/20261019T123737Z_023704/frames.csv |
| 20261019T130201Z_7ba2ef | unknown | hardware_head_only | [BELUM DIUKUR] | [BELUM DIUKUR] | 3,248 | 49 | 250,05 | 580,44 | 1,168 | 1 | yes; KD seed 42 | [BELUM DIUKUR] | runs/op3_head_ball_tracking/20261019T130201Z_7ba2ef/tracking.csv |
| 20261019T130400Z_74c464 | unknown | hardware_head_only | [BELUM DIUKUR] | [BELUM DIUKUR] | 13,265 | 79 | 67,92 | 168,01 | 0,536 | 0 | yes; KD seed 42 | [BELUM DIUKUR] | runs/op3_head_ball_tracking/20261019T130400Z_74c464/tracking.csv |
| probe_20261019T1748 | unknown | reliable_subscriber_probe | 30 | 360 | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | no detector in subscriber probe | [BELUM DIUKUR] | analisis_performa/UJI_LIVE_TRACKING_OP3_2026-10-19.md |

Sumber: runs/op3_pytorch/*.csv; runs/op3_idle_trial/20261019T123737Z_023704/frames.csv; runs/op3_head_ball_tracking/*/tracking.csv; analisis_performa/UJI_LIVE_TRACKING_OP3_2026-10-19.md

Processed_frame_rate berasal dari timestamp capture frame yang diproses, bukan laju topic. Probe 360 frame/12 s adalah hitung subscriber terpisah tanpa timestamp mentah; 30 Hz adalah perkiraan, bukan perbandingan kausal dengan sesi detektor.
