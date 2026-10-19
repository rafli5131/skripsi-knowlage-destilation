# T05. akurasi test keseluruhan

Status: Sebagian; CI bootstrap tersedia per model, belum untuk rerata lintas seed.

| method | metric | n_models [model] | mean | sample_SD | CI95 bootstrap of across-seed mean | CI95 bootstrap per model |
| --- | --- | --- | --- | --- | --- | --- |
| Pure KD | test_precision | 3 | 0.754727 | 0.020876 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.7073833467873947..0.7894407628754644 |
| Pure KD | test_recall | 3 | 0.96311 | 0.001717 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.9451780563813721..0.9762492956611695 |
| Pure KD | test_F1 | 3 | 0.846184 | 0.013566 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.8147800030983896..0.8676736758936052 |
| Pure KD | test_mAP50 | 3 | 0.944635 | 0.003968 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.9317543397040264..0.9641617987132814 |
| Pure KD | test_mAP50_95 | 3 | 0.663036 | 0.010753 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.6553449054711943..0.7004866209751799 |
| Supervised student | test_precision | 3 | 0.860915 | 0.003195 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.8395044883305673..0.8795021797332183 |
| Supervised student | test_recall | 3 | 0.969867 | 0.003461 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.9533582053699868..0.9818385922330097 |
| Supervised student | test_F1 | 3 | 0.912146 | 0.002565 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.8973519038739193..0.9239839157053855 |
| Supervised student | test_mAP50 | 3 | 0.960074 | 0.003359 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.9468621945241745..0.9713732705603721 |
| Supervised student | test_mAP50_95 | 3 | 0.722516 | 0.003454 | [BELUM DIUKUR] | available in source per_model.csv; seed-42 range=0.704396923962809..0.7429281937077041 |
| Teacher | test_precision | 1 | 0.891537 | [not defined for n=1] | [BELUM DIUKUR] | available in source per_model.csv; teacher range=0.8717081307674155..0.9112106109111388 |
| Teacher | test_recall | 1 | 0.969705 | [not defined for n=1] | [BELUM DIUKUR] | available in source per_model.csv; teacher range=0.9557365753484021..0.9823233038407521 |
| Teacher | test_F1 | 1 | 0.928979 | [not defined for n=1] | [BELUM DIUKUR] | available in source per_model.csv; teacher range=0.9139857641544632..0.9428288147153682 |
| Teacher | test_mAP50 | 1 | 0.964244 | [not defined for n=1] | [BELUM DIUKUR] | available in source per_model.csv; teacher range=0.9529705974958533..0.9754543186543112 |
| Teacher | test_mAP50_95 | 1 | 0.77998 | [not defined for n=1] | [BELUM DIUKUR] | available in source per_model.csv; teacher range=0.7622586189193906..0.7974102640522606 |

Sumber: summary_mean_sd.csv, per_model.csv, dan evaluasi TEST terkunci; P/R/F1 pada confidence 0,25 dan IoU 0,5
