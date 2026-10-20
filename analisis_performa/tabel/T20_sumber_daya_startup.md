# T20. sumber daya startup

Status: Sebagian; latensi frame pertama dan sumber daya tercatat, waktu muat model tidak dicatat.

| run_id | protocol | model_load_time [s] | first_frame_latency [ms] | first_frame_timing_scope | RSS_median [MiB] | RSS_peak [MiB] | CPU_median [percent] | CPU_p95 [percent] | n_frames [frame] | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20261019T080757Z | legacy | [BELUM DIUKUR] | 534,22 | callback_end_to_end | 352,1 | 357,5 | 728,2 | 811,3 | 724 | runs/op3_pytorch/20261019T080757Z.csv |
| 20261019T083428Z | legacy | [BELUM DIUKUR] | 530,39 | callback_end_to_end | 354,9 | 360,4 | 761,7 | 818,5 | 512 | runs/op3_pytorch/20261019T083428Z.csv |
| 20261019T084434Z | legacy | [BELUM DIUKUR] | 529,79 | callback_end_to_end | 354,7 | 359,3 | 738,1 | 818,8 | 887 | runs/op3_pytorch/20261019T084434Z.csv |
| 20261019T123737Z_023704 | idle_trial | [BELUM DIUKUR] | 550,57 | worker_processing | 381,7 | 387,9 | 1022,2 | 1043,2 | 1501 | runs/op3_idle_trial/20261019T123737Z_023704/frames.csv |

Sumber: runs/op3_pytorch/*.csv; runs/op3_idle_trial/20261019T123737Z_023704/frames.csv

Latensi frame pertama bukan waktu muat model. Scope callback_end_to_end dan worker_processing berbeda; CPU% relatif terhadap satu inti logis dan tidak dinormalisasi.
