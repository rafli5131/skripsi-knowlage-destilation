# T18. sesi live historis

Status: Sebagian; tiga sesi historis, belum ada run tracking dan belum semua kondisi terverifikasi.

| run_id | condition | condition_note | processed_frames [frame] | duration_capture [s] | effective_FPS_all_frames [frame/s] | warmup_removed | capture_gap_p50 [ms] | capture_gap_p95 [ms] | capture_gap_max [s] | gaps_over_1s [count] | end_to_end_median [ms] | end_to_end_p95 [ms] | CPU_median [percent] | RSS_median [MiB] | detection_instances [count] | tracked_IDs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20261019T080757Z | servo_idle | label tidak terverifikasi | 724 | 212.129275 | 3.408299 | no; not identifiable in legacy logs | 32.051 | 2004.1543 | 7.316513 | 62 | 25.405128 | 29.966671 | 728.2 | 352.082031 | 412 | not logged in this run |
| 20261019T083428Z | unknown | label operator; bukan telemetry | 512 | 36.215149 | 14.110117 | no; not identifiable in legacy logs | 32.024 | 266.035 | 2.004056 | 3 | 27.89265 | 30.270559 | 761.7 | 354.933594 | 0 | not logged in this run |
| 20261019T084434Z | servo_idle | label operator; bukan telemetry | 887 | 55.728925 | 15.898387 | no; not identifiable in legacy logs | 32.0375 | 232.07675 | 1.404169 | 3 | 26.342263 | 30.457165 | 738.1 | 354.660156 | 887 | not logged in this run |

Sumber: runs/op3_pytorch/*.csv dan *.json; tidak termasuk bukti akurasi atau tracking
