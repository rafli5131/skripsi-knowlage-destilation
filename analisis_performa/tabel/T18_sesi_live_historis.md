# T18. sesi live historis

Status: Sebagian; enam sesi dengan protokol berbeda; kondisi berjalan dan end-to-end sesi baru belum tersedia.

| run_id | condition | condition_note | protocol | processed_frames [frame] | duration_capture [s] | effective_FPS_all_frames [frame/s] | warmup_removed | capture_gap_p50 [ms] | capture_gap_p95 [ms] | capture_gap_max [s] | gaps_over_1s [count] | end_to_end_median [ms] | end_to_end_p95 [ms] | worker_processing_median [ms] | worker_processing_p95 [ms] | CPU_median [percent] | RSS_median [MiB] | detection_instances [count] | tracked_IDs | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20261019T080757Z | unknown | label JSON tidak diverifikasi sebagai kondisi fisik; legacy best_effort | legacy | 724 | 212,129 | 3,408 | no; marker absent | 32,05 | 2004,15 | 7,317 | 62 | 25,41 | 29,97 | [BELUM DIUKUR] | [BELUM DIUKUR] | 728,2 | 352,1 | 412 | [BELUM DIUKUR] | runs/op3_pytorch/20261019T080757Z.csv |
| 20261019T083428Z | unknown | label JSON tidak diverifikasi sebagai kondisi fisik; legacy best_effort | legacy | 512 | 36,215 | 14,11 | no; marker absent | 32,02 | 266,03 | 2,004 | 3 | 27,89 | 30,27 | [BELUM DIUKUR] | [BELUM DIUKUR] | 761,7 | 354,9 | 0 | [BELUM DIUKUR] | runs/op3_pytorch/20261019T083428Z.csv |
| 20261019T084434Z | unknown | label JSON tidak diverifikasi sebagai kondisi fisik; legacy best_effort | legacy | 887 | 55,729 | 15,898 | no; marker absent | 32,04 | 232,08 | 1,404 | 3 | 26,34 | 30,46 | [BELUM DIUKUR] | [BELUM DIUKUR] | 738,1 | 354,7 | 887 | [BELUM DIUKUR] | runs/op3_pytorch/20261019T084434Z.csv |
| 20261019T123737Z_023704 | servo_idle | operator_verified; preview X11; reliable QoS | idle_trial | 1501 | 60,238 | 24,901 | no; marker absent | 32,04 | 68,01 | 0,668 | 0 | [BELUM DIUKUR] | [BELUM DIUKUR] | 39,38 | 45,95 | 1022,2 | 381,7 | 4454 | ball:1;gawang:3;robot:2 | runs/op3_idle_trial/20261019T123737Z_023704/frames.csv |
| 20261019T130201Z_7ba2ef | unknown | head motion active; body/gait condition unverified | hardware_head_only | 49 | 14,777 | 3,248 | no; marker absent | 250,05 | 580,44 | 1,168 | 1 | [BELUM DIUKUR] | [BELUM DIUKUR] | 43,56 | 100,27 | 250,4 | 376,1 | [BELUM DIUKUR] | selected ball:1,5,11,17 | runs/op3_head_ball_tracking/20261019T130201Z_7ba2ef/tracking.csv |
| 20261019T130400Z_74c464 | unknown | head motion active; body/gait condition unverified | hardware_head_only | 79 | 5,88 | 13,265 | no; marker absent | 67,92 | 168,01 | 0,536 | 0 | [BELUM DIUKUR] | [BELUM DIUKUR] | 51,79 | 189,73 | 1258,8 | 348,4 | [BELUM DIUKUR] | selected ball:1 | runs/op3_head_ball_tracking/20261019T130400Z_74c464/tracking.csv |

Sumber: runs/op3_pytorch/*.csv dan *.json; runs/op3_idle_trial/20261019T123737Z_023704/frames.csv; runs/op3_idle_trial/20261019T123737Z_023704/summary.json; runs/op3_head_ball_tracking/*/tracking.csv dan summary.json

FPS dihitung dari timestamp capture frame yang diproses; sesi idle baru berbeda dari FPS berbasis waktu pemrosesan di laporan percobaan 04. Nilai end-to-end legacy adalah waktu callback-ke-keluaran; worker_processing pada paket baru mulai dari worker dan tidak setara.
Tiga baris terakhir menggunakan protokol baru: satu sesi servo_idle terverifikasi dan dua sesi gerak kepala dengan kondisi badan unknown. Jangan gabungkan baris untuk menghitung efek kondisi robot.
