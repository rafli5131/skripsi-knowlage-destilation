# Pure KD walking — repetition 3

> This run is retained as history; its [replacement](../walk-u3-ulang1/README_EN.md) is the active slot after passing automated checks.

Run `20261103_eq_kd42_walk_u3` began after operator confirmation with SSH-X preview active. Walking start and stop were acknowledged at 10:26:20 and 10:27:23 UTC. Head joints 19/20 received no position command; maximum guard deviation was one encoder count.

The 60-second window contained 727 frames and zero errors: mean/P95 latency 74.07/161.28 ms, effective FPS 12.12, process CPU 1297.81% of one logical CPU, and RSS 356.21 MiB. Automated status is **`perlu_audit`** because the two selected mid-window samples differed by at most 0.01687 rad from baseline, below the 0.03 rad threshold.

Across all 60 guard samples in the gait window, left and right knee ranges were **0.6630 and 0.6688 rad**. These provide evidence of joint motion during the window, while the two automatically selected samples were close to baseline. The possible effect of gait phase is an inference; the automated status remains unchanged pending protocol review.

Evidence: [before overlay](preview_sebelum_run.png), [after overlay](frame_deteksi_sesudah_jendela.png), [metrics](summary_metrics.json), [gait guard](gait_guard.json), [joint samples](head_guard_samples.csv), [performance table](performance_table.csv), and [class outputs](detection_table.csv). Output coverage is not labeled accuracy.
