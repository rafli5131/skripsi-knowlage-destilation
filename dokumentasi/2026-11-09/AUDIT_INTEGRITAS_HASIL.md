# Audit integritas hasil — 9 November 2026

Audit baca-saja terhadap sumber yang tersedia di robot; tidak menjalankan kamera, aktuator, training, atau evaluasi model ulang.

## Pemeriksaan yang lulus

- **Runtime:** 24 baris T36 mencakup empat model × dua kondisi × tiga ulangan. Rerata latensi, FPS, CPU, dan RSS pada delapan baris T37 cocok dengan tiga run masing-masing; CPU dinormalisasi dalam grafik terhadap 16 CPU logis.
- **T38:** 16 baris per model/kelas cocok dengan `results.json` lokal untuk precision, recall, F1, mAP50 dan mAP50–95. Komposisi sumber adalah 200 frame berobjek, 60 negatif, 50 parsial terpisah.
- **T42:** enam baris CSV cocok dengan delapan JSON evaluasi per teacher/student untuk mAP dan hash checkpoint yang tercatat. File [audit server](../../audit_teacher_t42_LTOW7Xw5.json) menyatakan sembilan cek tiap teacher dan empat cek lintas-teacher lulus. Saat preflight training, kode memeriksa SHA-256 setiap gambar dan label TRAIN/VAL dan manifest mencatat verifikasi lulus; audit teacher terbaru tidak menghitung ulang seluruh byte dataset.
- **Visualisasi:** 30 gambar final beresolusi minimum 2.400 × 1.500 piksel; hash terhadap 31 sumber dan keluaran cocok. Empat screenshot terkurasi dan video 10 detik cocok dengan manifest medianya. Tautan Markdown pada dokumen terbit yang diperiksa tersedia pada commit Git.
- **Skrip:** 22 tes audit teacher, portabilitas, dan kelanjutan T42 lulus.

## Hal yang masih memerlukan perhatian

- Uji robot sudah terdokumentasi untuk analisis deskriptif, tetapi bukti yang tidak direkam tidak dapat direkonstruksi. CPU/RSS adalah ukuran proses detektor. Frame T38 memakai satu rangkaian yang ditinjau setelah pra-label; interpretasi dibatasi sumbernya.
- TEST sudah pernah digunakan sebelumnya. Konfigurasi dataset training teacher utama lama belum dapat diverifikasi sampai ke setiap byte. Teacher T42 adalah teacher baru, bukan checkpoint teacher utama lama.
- Akurasi tracking berlabel belum dihitung karena tidak ada ground truth posisi/ID per frame. Cuplikan video terkurasi berasal dari supervised kondisi fisik `unknown`, bukan bukti gait; screenshot run berjalan adalah frame sesudah jendela analisis.
- Data mentah dan sebagian log tetap lokal; cadangan terpisah belum diverifikasi. Tabel T38, grafik terkurasi, screenshot, video dan audit T42 sudah masuk GitHub. Pada saat audit dilakukan, draf terpadu, matriks bukti dan memory masih lokal; periksa status Git terkini sebelum memakai checkout lain.
- Finalisasi naskah, verifikasi sitasi/sumber asli, penomoran, kesesuaian format kampus, dan tanggapan pembimbing belum tercatat selesai.

Audit ini memverifikasi konsistensi pada cakupan di atas; ia tidak menjamin tidak ada kesalahan lain atau membuktikan validitas seluruh kondisi fisik eksperimen.
