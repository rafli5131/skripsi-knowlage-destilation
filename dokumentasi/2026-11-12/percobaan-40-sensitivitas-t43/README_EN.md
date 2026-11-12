# T43 sensitivity analysis — 12 November 2026

**Parts A and B are complete.** The offline confidence sweep uses the same 260 reviewed frames; AP and per-frame counts at confidence >0.25 reproduce the T43 baseline for all four models. Thresholds 0.05–0.90 are descriptive only; the operating threshold remains 0.25. See the [detailed CSV](../../../analisis_performa/tabel/T43_sensitivitas_confidence.csv) and English plots in `grafik/`.

Important qualification: T43 AP uses `model.val` while operating metrics and this sweep use `model.predict`. For the teacher, measured padded input shapes were 512×672 and 480×640, respectively; validation also uses multi-label NMS. A single-frame check shows confidence changes with different padding. Their individual effects have not been isolated, so the AP–F1 discrepancy cannot be attributed solely to calibration.

All frames derive from one setup and are correlated. The same models helped produce prelabels. The second reviewer has annotated all 52 frames: all 40 boxes per class match at IoU ≥0.5, but mAP50–95 ordering differs between reviewers. The convention was clarified after the first review, confounding reviewer and rule effects; these findings do not establish generalization. Raw images, labels and per-frame predictions remain local.

The [three-label comparison](grafik/perbandingan_tiga_label_en.png) evaluates the same 52 frames. Bhre used the initial convention; Dipo annotated the clarified convention and then the alternative convention. Reviewer, rule clarification and annotation order effects cannot be isolated. See the [detailed CSV](../../../analisis_performa/tabel/T43_sensitivitas_label_52.csv).
