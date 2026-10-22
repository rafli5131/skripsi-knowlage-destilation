# Indeks tabel analisis performa

Pembaruan T33: 2026-10-22. T28–T29 merangkum VAL KD Hybrid full, T30–T31 memuat evaluasi TEST lanjutannya, T32 memuat benchmark server, dan T33 memuat pelatihan tiga seed. [Indeks lab/server](lab_server/README.md) menjelaskan sumber dan protokol. T15–T26 masih merujuk pembaruan log OP3 sampai 20 Oktober; T27 memuat evaluasi kamera OP3 eksploratif dari artefak 21 Oktober. F1 utama T27 dihitung dari precision dan recall makro; rerata F1 per kelas disimpan sebagai kolom sekunder (usulan D11 belum dikunci). Hasil TEST Advance Vision adalah evaluasi level gambar, bukan akurasi kamera OP3.

| Tabel | Status | Berkas |
| --- | --- | --- |
| T01 | Lengkap dari artefak historis; bukan validasi kamera OP3. | [CSV](tabel/T01_spesifikasi_model.csv) · [Markdown](tabel/T01_spesifikasi_model.md) |
| T02 | Lengkap; durasi enam run ditelusuri ke results.csv atau manifest resume. | [CSV](tabel/T02_resep_pelatihan.csv) · [Markdown](tabel/T02_resep_pelatihan.md) |
| T03 | Lengkap dari results.csv run yang sudah ada. | [CSV](tabel/T03_konvergensi.csv) · [Markdown](tabel/T03_konvergensi.md) |
| T04 | Lengkap untuk KD pure tiga seed, pilot pure_weighted seed 42, hybrid_feature seed 42, dan hybrid_full tiga seed; hasil Hybrid full dibandingkan dengan supervised pada T28–T29. | [CSV](tabel/T04_ablasi_kd_val.csv) · [Markdown](tabel/T04_ablasi_kd_val.md) · [Per kelas](tabel/T04_ablasi_kd_val_per_kelas.md) |
| T05 | Lengkap untuk ringkasan tiga seed, bootstrap antar-seed, dan [interval per checkpoint](lab_server/interval_bootstrap_per_model.md); bootstrap antar-seed eksploratif karena n=3. | [CSV](tabel/T05_akurasi_test_keseluruhan.csv) · [Markdown](tabel/T05_akurasi_test_keseluruhan.md) |
| T06 | Lengkap dari hasil TEST terkunci yang sudah ada. | [CSV](tabel/T06_akurasi_per_kelas.csv) · [Markdown](tabel/T06_akurasi_per_kelas.md) |
| T07 | Lengkap untuk lima metrik keseluruhan pada tiga pasangan seed dan retensi mAP50–95 terhadap teacher. | [CSV](tabel/T07_selisih_berpasangan.csv) · [Markdown](tabel/T07_selisih_berpasangan.md) |
| T08 | Lengkap untuk tiga kelas × tiga ukuran × tujuh checkpoint pada VAL. | [CSV](tabel/T08_akurasi_ukuran_objek.csv) · [Markdown](tabel/T08_akurasi_ukuran_objek.md) |
| T09 | Lengkap dari diagnosis tujuh checkpoint pada VAL; kategori FP saling eksklusif. | [CSV](tabel/T09_analisis_kesalahan.csv) · [Markdown](tabel/T09_analisis_kesalahan.md) |
| T10 | Lengkap dari prediksi VAL dan pencocokan satu-ke-satu. | [CSV](tabel/T10_matriks_kebingungan.csv) · [Markdown](tabel/T10_matriks_kebingungan.md) |
| T11 | Lengkap dari sapuan confidence pada VAL; hasil TEST historis tidak dipilih ulang. | [CSV](tabel/T11_sapuan_confidence.csv) · [Markdown](tabel/T11_sapuan_confidence.md) |
| T12 | Lengkap untuk lima ambang NMS pada tiga model perwakilan di VAL. | [CSV](tabel/T12_sapuan_iou_nms.csv) · [Markdown](tabel/T12_sapuan_iou_nms.md) |
| T13 | Lengkap untuk empat ukuran input pada tiga model perwakilan CPU server, ditambah tujuh titik dasar 640 NVIDIA L40. | [CSV](tabel/T13_sapuan_imgsz.csv) · [Markdown](tabel/T13_sapuan_imgsz.md) |
| T14 | Lengkap dari prediksi VAL yang lolos confidence 0,25 dan bin ECE. | [CSV](tabel/T14_kalibrasi_confidence.csv) · [Markdown](tabel/T14_kalibrasi_confidence.md) |
| T15 | Sebagian; inti/logical CPU, kapasitas RAM, governor, dan mode daya belum direkam. | [CSV](tabel/T15_lingkungan_uji_op3.csv) · [Markdown](tabel/T15_lingkungan_uji_op3.md) |
| T16 | Belum diukur pada CPU OP3 dengan frame tetap. | [CSV](tabel/T16_latensi_frame_tetap.csv) · [Markdown](tabel/T16_latensi_frame_tetap.md) |
| T17 | Belum diukur. | [CSV](tabel/T17_sapuan_thread.csv) · [Markdown](tabel/T17_sapuan_thread.md) |
| T18 | Sebagian; enam sesi dengan protokol berbeda; kondisi berjalan dan end-to-end sesi baru belum tersedia. | [CSV](tabel/T18_sesi_live_historis.csv) · [Markdown](tabel/T18_sesi_live_historis.md) |
| T19 | Belum diukur; sesi walking belum tersedia. | [CSV](tabel/T19_servo_idle_vs_walking.csv) · [Markdown](tabel/T19_servo_idle_vs_walking.md) |
| T20 | Sebagian; latensi frame pertama dan sumber daya tercatat, waktu muat model tidak dicatat. | [CSV](tabel/T20_sumber_daya_startup.csv) · [Markdown](tabel/T20_sumber_daya_startup.md) |
| T21 | Belum diukur. | [CSV](tabel/T21_stabilitas_termal.csv) · [Markdown](tabel/T21_stabilitas_termal.md) |
| T22 | Sebagian; laju subscriber probe ada, perbandingan kamera-saja versus detektor dengan protokol berpasangan belum ada. | [CSV](tabel/T22_aliran_kamera.csv) · [Markdown](tabel/T22_aliran_kamera.md) |
| T23 | Sebagian; proporsi sampel live tersedia, benchmark frame tetap dan end-to-end sesi baru belum tersedia. | [CSV](tabel/T23_kepatuhan_tenggat.csv) · [Markdown](tabel/T23_kepatuhan_tenggat.md) |
| T24 | Belum diukur. | [CSV](tabel/T24_pengaruh_preview.csv) · [Markdown](tabel/T24_pengaruh_preview.md) |
| T25 | Sebagian; kelas/ID tersedia pada sesi idle baru, log lama hanya total dan uji kepala hanya bola terpilih. | [CSV](tabel/T25_observasi_deteksi_live.csv) · [Markdown](tabel/T25_observasi_deteksi_live.md) |
| T26 | Sebagian; akurasi TEST offline ada, runtime OP3 hanya KD seed 42 idle; walking dan benchmark frame tetap belum ada. | [CSV](tabel/T26_tradeoff_utama.csv) · [Markdown](tabel/T26_tradeoff_utama.md) |
| T27 | Sebagian: evaluasi eksploratif 260 frame utama (200 berobjek + 60 negatif). Set 50 frame gawang parsial hanya catatan dan tidak digunakan membandingkan model karena definisi kotak berbeda serta draf label berasal dari KD. Set final D8 belum dikunci; risiko bias anotasi juga berlaku pada set utama. | [CSV](tabel/T27_akurasi_frame_kamera_op3.csv) · [Markdown](tabel/T27_akurasi_frame_kamera_op3.md) · [Audit label](lab_server/AUDIT_DEFINISI_GAWANG_2026-10-21.md) · [Asal frame negatif](lab_server/AUDIT_ASAL_FRAME_NEGATIF_2026-10-21.md) |
| T28 | Evaluasi VAL berpasangan KD Hybrid full vs supervised pada tiga seed, rerata ± SD dan delta. | [CSV](tabel/T28_selisih_kd_hybrid_val.csv) · [Markdown](tabel/T28_selisih_kd_hybrid_val.md) |
| T29 | Evaluasi VAL per kelas berpasangan KD Hybrid full vs supervised pada tiga seed. | [CSV](tabel/T29_kd_hybrid_val_per_kelas.csv) · [Markdown](tabel/T29_kd_hybrid_val_per_kelas.md) |
| T30 | Evaluasi TEST lanjutan berpasangan KD Hybrid full vs supervised pada tiga seed; split pernah dipakai eksperimen lama. | [CSV](tabel/T30_kd_hybrid_test_berpasangan.csv) · [Markdown](tabel/T30_kd_hybrid_test_berpasangan.md) |
| T31 | Evaluasi TEST lanjutan per kelas berpasangan. | [CSV](tabel/T31_kd_hybrid_test_per_kelas.csv) · [Markdown](tabel/T31_kd_hybrid_test_per_kelas.md) |
| T32 | Benchmark enam checkpoint pada frame VAL tetap dan NVIDIA L40; bukan FPS OP3. | [CSV](tabel/T32_kd_hybrid_benchmark_server.csv) · [Markdown](tabel/T32_kd_hybrid_benchmark_server.md) |
| T33 | Resep, durasi, dan konvergensi training KD Hybrid full tiga seed. | [CSV](tabel/T33_pelatihan_kd_hybrid_full.csv) · [Markdown](tabel/T33_pelatihan_kd_hybrid_full.md) |
