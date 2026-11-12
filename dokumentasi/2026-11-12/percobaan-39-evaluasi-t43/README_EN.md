# T43 — offline OP3 camera evaluation

[Detailed CSV](../../../analisis_performa/tabel/T43_akurasi_op3_empat_model_260.csv) · [mAP chart](grafik/perbandingan_map_en.png) · [Combined confusion matrices](confusion_matrix/empat_model_en.png)

This exploratory evaluation uses the same 260 frames for four models: 130 idle and 130 walking in place, including 30 negative frames per condition. All goal frames are partial; the reviewer chose a lower-goal-region box and a robot-body box. These conventions differ from T38, so results are not directly comparable. Images come from one setup and adjacent frames are correlated.

AP uses confidence floor 0.001, while operating precision/recall/F1 use confidence > 0.25 and matching IoU ≥ 0.5; NMS IoU is 0.7. Primary macro F1 is the harmonic mean of macro precision and macro recall. Matrix rows are predictions and columns are manual labels, matched class-agnostically by descending IoU; background denotes unmatched boxes.

Prelabels are a union of all four evaluated models. The operator saw a Hybrid preview and received feedback while annotating. The 52-frame audit compares two passes by the same reviewer, not independent raters; the partial-goal upper boundary has no fixed landmark. These limitations and the dataset scope must accompany any results. Runtime speed is not measured here. Individual and combined plots and matrices are in the respective folders.
