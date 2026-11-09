# Draf pembahasan T38

Evaluasi offline empat checkpoint menggunakan 260 frame kamera OP3 yang sama, terdiri atas 200 frame berobjek dan 60 frame negatif. Terdapat 400 kotak acuan yang telah ditinjau manusia. Lima puluh frame dengan gawang parsial dianalisis terpisah karena definisi kotaknya berbeda dan tidak dimasukkan ke hasil utama.

Pada set utama, teacher YOLO11n memperoleh mAP50–95 sebesar 0,5004 dan F1 makro 0,6829. Hybrid full seed 1337 memperoleh 0,4885 dan 0,5121; supervised seed 1337 memperoleh 0,4414 dan 0,6054; KD murni seed 42 memperoleh 0,4218 dan 0,5008. Hybrid memiliki mAP50 sebesar 0,7526, tertinggi pada perbandingan ini. Perbedaan urutan mAP dan F1 dapat terjadi karena AP menilai prediksi pada berbagai ambang, sedangkan F1 dihitung pada confidence >0,25 dan IoU pencocokan ≥0,5.

Pada 60 frame negatif, teacher menghasilkan false positive pada dua frame dan Hybrid pada 21 frame; supervised serta KD murni tidak menghasilkan false positive pada frame negatif tersebut. Pada kelas gawang, Hybrid mencocokkan 2 dari 80 kotak acuan pada ambang operasi, sementara supervised mencocokkan 21 dari 80. Temuan ini hanya berlaku pada frame dan aturan evaluasi yang digunakan; hasil per kelas lengkap disajikan pada T38.

Frame berasal dari satu rangkaian pengambilan dan draf label awal dibantu KD murni sebelum peninjauan manusia. Oleh karena itu, potensi bias anotasi dan keterbatasan variasi adegan harus dipertahankan dalam interpretasi. T38 merupakan analisis retrospektif, bukan pengujian eksternal independen; hasilnya tidak digunakan untuk memilih ulang checkpoint atau threshold. Hasil akurasi ini tidak dicampur dengan pengukuran runtime live OP3 atau evaluasi TEST resmi.
