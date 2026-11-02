# Interpretasi akurasi dan precision pada uji live berjalan teacher

Uji ini memiliki log prediksi model dan video/overlay, tetapi **tidak memiliki kotak ground truth manusia untuk setiap frame yang diukur**. Karena itu accuracy, precision, recall, F1, AP, dan mAP **tidak dihitung** untuk run berjalan ini. Menyebut persentase frame yang mengeluarkan kelas sebagai akurasi akan menyesatkan: deteksi yang muncul dapat salah objek, dan frame tanpa keluaran bisa saja memang tidak memiliki target.

Pernyataan itu **khusus untuk run live berjalan**. Skripsi sudah memiliki mAP, precision, recall, dan F1 dari TEST resmi untuk KD Hybrid, supervised, dan teacher pada [T30](../../../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md) serta [T05](../../../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md). [Peta rumusan masalah](../PETA_RUMUSAN_MASALAH.md) memisahkan bukti TEST, evaluasi kamera OP3 berlabel, dan benchmark runtime.

Grafik per run `grafik_keluaran_kelas_id.png` dan grafik gabungan `../01-teacher/grafik_cakupan_confidence_teacher_walk_hd.png` menampilkan dua besaran yang memang tersedia:

1. **Cakupan keluaran:** proporsi frame ukur dengan setidaknya satu prediksi untuk kelas tersebut.
2. **Median confidence model:** skor keyakinan prediksi pada frame ukur; skor ini bukan probabilitas akurasi dan tidak sama dengan precision.

Untuk menghitung precision deteksi (`TP / (TP + FP)`) serta recall (`TP / (TP + FN)`), frame uji perlu dilabeli manual oleh peninjau manusia, termasuk kotak objek dan frame tanpa target. Prediksi dan label kemudian dipasangkan dengan aturan IoU serta kelas yang ditetapkan sebelumnya. Angka mAP dari set evaluasi berlabel lain, bila tersedia, harus dilaporkan terpisah dengan nama dataset dan protokolnya; angka itu tidak boleh dipindahkan menjadi nilai akurasi run berjalan ini.

Run berjalan baru tetap menggunakan sumber raw yang tercatat pada `active_run_sources.json`; ulangan 1 adalah run lama ulangan 3. Perbedaan cakupan kelas antarulangan dapat dipengaruhi posisi relatif objek dan gerak kamera, sehingga tidak membuktikan perubahan mutu model.

**Pemilihan set:** ulangan 1 diganti dengan run lama ulangan 3 dan dua run berikutnya diambil setelah hasil gawang set lama diketahui. Set aktif karena itu bukan sampel ulangan yang dipilih tanpa melihat hasil. Angka cakupan 94,3% dapat lebih optimistis daripada estimasi dari semua run yang pernah diambil. Laporkan aturan pemilihan ini dan arsip set lama bila digunakan dalam skripsi; jangan menyebut peningkatannya sebagai efek model atau gait.
