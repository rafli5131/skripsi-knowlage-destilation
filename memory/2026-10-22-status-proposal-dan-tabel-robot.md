# Memori proyek — 22 Oktober 2026: proposal dan tabel robot

Catatan ini melanjutkan pengujian OP3/KD Hybrid. Untuk angka gunakan laporan dan log tertaut, bukan ringkasan ini jika ada perbedaan.

## Keputusan dan ruang lingkup

- Istilah penelitian: Knowledge Distillation (KD), bukan knowledge development.
- Teacher: YOLO11n FP32 beku. Student: YOLO11 kustom skala t, 810.649 parameter; bukan YOLO11n standar. Kontrol supervised memakai arsitektur student yang sama.
- Keputusan 22 Oktober memilih KD Hybrid full sebagai fokus sementara draf berdasarkan VAL; pure KD murni dan hybrid_feature menjadi pembanding/ablasi. Konfirmasi pembimbing bahwa Hybrid full menjadi fokus utama masih perlu dipastikan; lihat docs/DECISIONS.md dan configs/analysis.yaml.
- Hybrid full memakai loss deteksi label TRAIN ditambah distilasi fitur/box/kelas teacher (bobot 1:1:1, temperatur 2). Pure KD tidak memakai loss GT untuk student. Jangan campur definisi kedua objective.
- Dataset Advance Vision Human Roboflow v1, lisensi CC BY 4.0; 4.600 TRAIN, 1.213 VAL, 592 TEST; kelas ball, gawang, robot. Ada kemiripan sumber/adegan lintas split dan provenance dataset teacher tidak lengkap.
- TEST Hybrid adalah evaluasi lanjutan pada split yang pernah digunakan untuk evaluasi model terdahulu, bukan holdout yang sepenuhnya belum pernah dilihat. Hybrid TEST mAP50–95 0,7469 ± 0,0022, supervised 0,7225 ± 0,0035, delta paired +0,0244 ± 0,0040; F1@0,25 masing-masing 0,9071 dan 0,9121. Pure KD mAP50–95 TEST 0,6630 ± 0,0108, lebih rendah dari supervised.
- Evaluasi kamera OP3 eksploratif: 260 frame utama (200 positif, 60 negatif, 400 GT box); KD mAP50–95 0,422, supervised 0,419. Ada 50 frame gawang parsial yang dipisah. Label berawal dari draf KD sehingga risiko bias anotasi tetap ada.
- Runtime OP3: KD murni idle/walking 13,011/12,365 FPS; KD Hybrid 12,390/12,196 FPS. Satu run sekitar 60 detik per kondisi. Hybrid idle setelah OpenCR pulih: 708 frame terukur, 11,795 FPS, nol error; tiga kelas masing-masing muncul pada 708/708 frame. Keluaran live bukan akurasi. Label walking adalah input operator/perintah gait, bukan verifikasi gerak independen. Idle pasca-pemulihan OpenCR memiliki telemetry kecepatan joint nol sebelum/sesudah.
- Tabel T15–T27 diperbarui dari bukti yang tersedia. Celah yang tetap ditandai: T16 fixed-frame OP3, T17 sapuan thread terkendali, T21 rekaman suhu berkelanjutan, T22 laju kamera mentah dan uji kamera-only berpasangan, T24 efek preview terisolasi, T27 evaluasi kamera lintas sesi/adegan independen.
- Pengguna masuk tahap penulisan laporan. Jangan hapus/reset artefak lokal atau push tanpa diminta.

## Rujukan

- Keputusan: docs/DECISIONS.md; configs/analysis.yaml.
- Hasil utama: analisis_performa/INDEKS.md dan dokumentasi/INDEKS.md.
- Prompt proposal terkini: prompt/PROMPT_PROPOSAL_BAB_I-III_KD_OP3_V2.md.
- Audit dokumentasi: dokumentasi/AUDIT_KELENGKAPAN_SKRIPSI_2026-10-22.md.
