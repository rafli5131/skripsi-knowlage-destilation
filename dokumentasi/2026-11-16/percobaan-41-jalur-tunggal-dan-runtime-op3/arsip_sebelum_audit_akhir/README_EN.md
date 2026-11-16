# Offline OP3 single-path and runtime analysis

[T44 paths](../../../analisis_performa/tabel/T44_jalur_tunggal_op3_t38_t43.md) · [T45 stages and CPU](../../../analisis_performa/tabel/T45_rincian_latensi_dan_cpu_op3.md) · [Chart](grafik/jalur_dan_cpu_en.png)

All 48 baseline identity checks passed. Four models were assessed offline on frozen T38/T43 frames. Factor endpoint reproduction failed for the three student models on T38; those factor differences are reported without causal interpretation. 24 historical runs were rechecked and ten replay variants used 300 array inputs with torch 4/2 threads confirmed throughout. The 260-frame source was cycled; replay is not a replacement for live ROS performance.

Initial replay exposed an Ultralytics CPU backend reset to 8 intra-op threads after metadata was recorded; the primary replay resets and verifies 4. Historical post-initialization thread counts were not measured, so an additional one-thread OpenBLAS control reduces replay CPU substantially. Actual OpenBLAS and post-initialization thread counts were not observed during historical runs, so their CPU cause cannot be established conclusively. Teacher weights, images, labels, raw logs and frame-level predictions remain local.
