# T23. kepatuhan tenggat

Status: Sebagian; proporsi sampel live tersedia, benchmark frame tetap dan end-to-end sesi baru belum tersedia.

| run_id | condition | latency_metric | n_frames [frame] | frames_le_33_3_ms [percent] | frames_le_66_7_ms [percent] | source |
| --- | --- | --- | --- | --- | --- | --- |
| 20261019T080757Z | unknown | stage_total | 724 | 99,45 | 100 | runs/op3_pytorch/20261019T080757Z.csv |
| 20261019T080757Z | unknown | callback_end_to_end | 724 | 99,31 | 99,86 | runs/op3_pytorch/20261019T080757Z.csv |
| 20261019T083428Z | unknown | stage_total | 512 | 98,05 | 100 | runs/op3_pytorch/20261019T083428Z.csv |
| 20261019T083428Z | unknown | callback_end_to_end | 512 | 97,85 | 99,8 | runs/op3_pytorch/20261019T083428Z.csv |
| 20261019T084434Z | unknown | stage_total | 887 | 98,31 | 100 | runs/op3_pytorch/20261019T084434Z.csv |
| 20261019T084434Z | unknown | callback_end_to_end | 887 | 98,08 | 99,89 | runs/op3_pytorch/20261019T084434Z.csv |
| 20261019T123737Z_023704 | servo_idle | stage_total | 1501 | 65,62 | 100 | runs/op3_idle_trial/20261019T123737Z_023704/frames.csv |
| 20261019T123737Z_023704 | servo_idle | worker_processing | 1501 | 9,99 | 99,93 | runs/op3_idle_trial/20261019T123737Z_023704/frames.csv |

Sumber: runs/op3_pytorch/*.csv; runs/op3_idle_trial/20261019T123737Z_023704/frames.csv

Stage_total adalah jumlah preprocess, inference, dan postprocess per frame. Worker_processing mulai saat worker mengambil frame, sehingga tidak setara callback_end_to_end dan tidak mencakup antrean/pengiriman tampilan. Proporsi ini deskriptif untuk sesi live, bukan benchmark frame tetap.
