# T25. observasi deteksi live

Status: Sebagian; kelas/ID tersedia pada sesi idle baru, log lama hanya total dan uji kepala hanya bola terpilih.

| run_id | condition | class | n_frames [frame] | detections [count] | detections_per_frame [count/frame] | confidence_p10 | confidence_median | confidence_p90 | count_change_fraction | track_IDs | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20261019T080757Z | unknown | all | 724 | 412 | 0,569 | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | runs/op3_pytorch/20261019T080757Z.csv |
| 20261019T083428Z | unknown | all | 512 | 0 | 0 | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | runs/op3_pytorch/20261019T083428Z.csv |
| 20261019T084434Z | unknown | all | 887 | 887 | 1 | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | [BELUM DIUKUR] | runs/op3_pytorch/20261019T084434Z.csv |
| 20261019T123737Z_023704 | servo_idle | ball | 1501 | 1501 | 1 | 0,976 | 0,979 | 0,981 | 0 | 1 | runs/op3_idle_trial/20261019T123737Z_023704/detections.csv |
| 20261019T123737Z_023704 | servo_idle | gawang | 1501 | 1452 | 0,967 | 0,266 | 0,29 | 0,315 | 0,0613 | 3 | runs/op3_idle_trial/20261019T123737Z_023704/detections.csv |
| 20261019T123737Z_023704 | servo_idle | robot | 1501 | 1501 | 1 | 0,756 | 0,772 | 0,785 | 0 | 2 | runs/op3_idle_trial/20261019T123737Z_023704/detections.csv |
| 20261019T130201Z_7ba2ef | unknown | ball_selected_only | 49 | 26 | 0,531 | 0,567 | 0,844 | 0,975 | 0,1667 | 1,5,11,17 | runs/op3_head_ball_tracking/20261019T130201Z_7ba2ef/tracking.csv |
| 20261019T130400Z_74c464 | unknown | ball_selected_only | 79 | 79 | 1 | 0,914 | 0,974 | 0,976 | 0 | 1 | runs/op3_head_ball_tracking/20261019T130400Z_74c464/tracking.csv |

Sumber: runs/op3_pytorch/*.csv; runs/op3_idle_trial/20261019T123737Z_023704/frames.csv; runs/op3_idle_trial/20261019T123737Z_023704/detections.csv; runs/op3_head_ball_tracking/*/tracking.csv

Count_change_fraction adalah fraksi pasangan frame berurutan dengan jumlah deteksi kelas yang berubah; pada uji kepala hanya ada indikator bola terpilih. ID konsisten pada objek yang relatif diam tidak membuktikan tracking objek bergerak. Confidence bukan precision/akurasi kamera OP3.
