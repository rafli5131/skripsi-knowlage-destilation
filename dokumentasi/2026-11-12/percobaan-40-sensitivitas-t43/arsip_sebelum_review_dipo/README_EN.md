# T43 sensitivity analysis — 12 November 2026

**Part A completed; Part B awaits the second reviewer and an alternative-label session.** The offline confidence sweep uses the same 260 reviewed frames; AP and per-frame counts at confidence >0.25 reproduce the T43 baseline for all four models. Thresholds 0.05–0.90 are descriptive only; the operating threshold remains 0.25. See the [detailed CSV](../../../analisis_performa/tabel/T43_sensitivitas_confidence.csv) and English plots in `grafik/`.

Important qualification: T43 AP uses `model.val` while operating metrics and this sweep use `model.predict`. For the teacher, measured padded input shapes were 512×672 and 480×640, respectively; validation also uses multi-label NMS. A single-frame check shows confidence changes with different padding. Their individual effects have not been isolated, so the AP–F1 discrepancy cannot be attributed solely to calibration.

All frames derive from one setup and are correlated. The same models helped produce prelabels. The second reviewer has not annotated yet; confidence analysis does not establish inter-rater reliability or generalization. Raw images, labels and per-frame predictions remain local.
