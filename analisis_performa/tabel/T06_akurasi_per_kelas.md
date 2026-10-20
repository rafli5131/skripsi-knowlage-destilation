# T06. akurasi per kelas

Status: Lengkap dari evaluasi TEST terkunci.

| method | class | ground_truth_objects [object] | AP50 mean | AP50 SD | AP50-95 mean | AP50-95 SD | precision mean | precision SD | recall mean | recall SD | F1 mean | F1 SD | n_models [model] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pure KD | ball | 83 | 0,9560 | 0,0084 | 0,7302 | 0,0190 | 0,7447 | 0,0431 | 0,9639 | 0,0000 | 0,8397 | 0,0272 | 3 |
| Pure KD | gawang | 532 | 0,9139 | 0,0034 | 0,5382 | 0,0041 | 0,7371 | 0,0054 | 0,9311 | 0,0029 | 0,8228 | 0,0023 | 3 |
| Pure KD | robot | 119 | 0,9640 | 0,0060 | 0,7207 | 0,0151 | 0,7824 | 0,0241 | 0,9944 | 0,0049 | 0,8756 | 0,0167 | 3 |
| Supervised student | ball | 83 | 0,9760 | 0,0046 | 0,8241 | 0,0040 | 0,9415 | 0,0107 | 0,9679 | 0,0070 | 0,9545 | 0,0031 | 3 |
| Supervised student | gawang | 532 | 0,9266 | 0,0086 | 0,5486 | 0,0004 | 0,7531 | 0,0083 | 0,9417 | 0,0038 | 0,8369 | 0,0059 | 3 |
| Supervised student | robot | 119 | 0,9776 | 0,0047 | 0,7949 | 0,0062 | 0,8882 | 0,0114 | 1,0000 | 0,0000 | 0,9407 | 0,0064 | 3 |
| Teacher | ball | 83 | 0,9848 | [TIDAK BERLAKU: n=1] | 0,9131 | [TIDAK BERLAKU: n=1] | 0,9647 | [TIDAK BERLAKU: n=1] | 0,9880 | [TIDAK BERLAKU: n=1] | 0,9762 | [TIDAK BERLAKU: n=1] | 1 |
| Teacher | gawang | 532 | 0,9234 | [TIDAK BERLAKU: n=1] | 0,5684 | [TIDAK BERLAKU: n=1] | 0,7349 | [TIDAK BERLAKU: n=1] | 0,9380 | [TIDAK BERLAKU: n=1] | 0,8241 | [TIDAK BERLAKU: n=1] | 1 |
| Teacher | robot | 119 | 0,9846 | [TIDAK BERLAKU: n=1] | 0,8585 | [TIDAK BERLAKU: n=1] | 0,9750 | [TIDAK BERLAKU: n=1] | 0,9832 | [TIDAK BERLAKU: n=1] | 0,9791 | [TIDAK BERLAKU: n=1] | 1 |

Sumber: [per_model.csv](../../artifacts/thesis_analysis_final_corrected/per_model.csv) dan [hasil evaluasi terkunci](../../runs/final_test/pure_kd_official_split_locked_retry1/manifest.json).

Jumlah ground truth TEST sama pada tujuh berkas metrik model: ball 83, gawang 532, robot 119. SD sampel tidak berlaku untuk teacher (n=1).
