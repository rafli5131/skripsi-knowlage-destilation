# T05. akurasi test keseluruhan

Status: Sebagian; ringkasan antar-seed dan interval per model tersedia, interval rerata lintas-seed belum tersedia.

| method | metric | n_models [model] | mean | sample_SD | CI95 bootstrap of across-seed mean | CI95 bootstrap per model |
| --- | --- | --- | --- | --- | --- | --- |
| Pure KD | test_precision | 3 | 0,7547 | 0,0209 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Pure KD | test_recall | 3 | 0,9631 | 0,0017 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Pure KD | test_F1 | 3 | 0,8462 | 0,0136 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Pure KD | test_mAP50 | 3 | 0,9446 | 0,0040 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Pure KD | test_mAP50_95 | 3 | 0,6630 | 0,0108 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Supervised student | test_precision | 3 | 0,8609 | 0,0032 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Supervised student | test_recall | 3 | 0,9699 | 0,0035 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Supervised student | test_F1 | 3 | 0,9121 | 0,0026 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Supervised student | test_mAP50 | 3 | 0,9601 | 0,0034 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Supervised student | test_mAP50_95 | 3 | 0,7225 | 0,0035 | [BELUM DIUKUR] | tersedia; lihat interval_bootstrap_per_model.csv |
| Teacher | test_precision | 1 | 0,8915 | [TIDAK BERLAKU: n=1] | [TIDAK BERLAKU: n=1] | tersedia; lihat interval_bootstrap_per_model.csv |
| Teacher | test_recall | 1 | 0,9697 | [TIDAK BERLAKU: n=1] | [TIDAK BERLAKU: n=1] | tersedia; lihat interval_bootstrap_per_model.csv |
| Teacher | test_F1 | 1 | 0,9290 | [TIDAK BERLAKU: n=1] | [TIDAK BERLAKU: n=1] | tersedia; lihat interval_bootstrap_per_model.csv |
| Teacher | test_mAP50 | 1 | 0,9642 | [TIDAK BERLAKU: n=1] | [TIDAK BERLAKU: n=1] | tersedia; lihat interval_bootstrap_per_model.csv |
| Teacher | test_mAP50_95 | 1 | 0,7800 | [TIDAK BERLAKU: n=1] | [TIDAK BERLAKU: n=1] | tersedia; lihat interval_bootstrap_per_model.csv |

Sumber: [summary_mean_sd.csv](../../artifacts/thesis_analysis_final_corrected/summary_mean_sd.csv), [per_model.csv](../../artifacts/thesis_analysis_final_corrected/per_model.csv), dan [rincian interval per model](../lab_server/interval_bootstrap_per_model.md).

P/R/F1 memakai confidence >0,25 dan IoU pencocokan 0,50; AP memakai confidence floor 0,001 dan NMS IoU 0,7. Bootstrap per model meresampling gambar TEST, sedangkan SD sampel menggambarkan variasi tiga seed.
