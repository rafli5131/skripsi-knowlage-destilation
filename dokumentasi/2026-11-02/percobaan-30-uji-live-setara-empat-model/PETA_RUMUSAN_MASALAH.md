# Peta bukti untuk lima rumusan masalah skripsi

Pembaruan 2 November 2026. **Metrik akurasi untuk skripsi sudah tersedia pada TEST resmi; metrik itu tidak berasal dari run live berjalan.** Angka dari dataset dan definisi F1 berbeda tidak boleh digabung menjadi satu tabel tanpa label protokol.

| Rumusan masalah | Bukti saat ini | Status dan pekerjaan tersisa |
|---|---|---|
| 1. Sistem ROS 2 deteksi YOLO11 skala t hasil KD pada ROBOTIS OP3 | Package ROS 2, log kamera/deteksi/tracking, dokumentasi robot, dan uji idle/berjalan. | Implementasi serta uji fungsi ada; rangkum arsitektur dan bukti deployment dalam bab hasil. |
| 2. mAP KD vs supervised arsitektur sama vs teacher YOLO11n | [T30 TEST berpasangan](../../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md) untuk KD Hybrid full dan supervised seed 1337; [T05 TEST keseluruhan](../../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) untuk teacher. | **Terukur pada TEST resmi 592 gambar.** Bila ingin menyatakan mAP khusus domain kamera OP3, [T34](../../../analisis_performa/tabel/T34_akurasi_op3_hybrid_supervised_seed1337.md) baru memuat Hybrid dan supervised; teacher harus diuji pada 260 frame/label yang sama (T38 sesuai prompt), atau pada set OP3 baru yang dibekukan sebelum melihat hasil. |
| 3. Precision, recall, F1 ketiga model | T30 dan T05 dengan protokol TEST yang sama. T34 memberi analisis OP3 eksploratif untuk dua model. | **Terukur pada TEST resmi.** Untuk klaim ketiga model pada kamera OP3, teacher masih perlu evaluasi berlabel pada frame identik. F1 makro T34 adalah rerata F1 tiap kelas, berbeda dari F1 keseluruhan pada tabel TEST; jangan bandingkan nilainya lintas tabel tanpa menjelaskan definisi. |
| 4. Rata-rata latensi dan FPS saat diam/berjalan | [Tabel runtime aktif](05-ringkasan/tabel_24_run.csv) dan [agregat](05-ringkasan/tabel_agregat_saat_ini.csv). | Teacher 6 run dan KD Hybrid idle 3 run selesai; **15 run lain belum diukur**. Setelah lengkap, bangun T36/T37 dan perbandingan setara. |
| 5. CPU dan RAM onboard saat model penuh berjalan | CSV runtime per frame dan tabel yang sama. | Teacher serta KD Hybrid idle tersedia; 15 run lain dan ringkasan antarmodel belum lengkap. |

## Angka TEST resmi untuk tiga model utama

| Model | mAP50–95 | Precision | Recall | F1 | Sumber |
|---|---:|---:|---:|---:|---|
| KD Hybrid full seed 1337 | 0,7468 | 0,8513 | 0,9694 | 0,9065 | T30, TEST 592 gambar |
| Supervised student seed 1337 | 0,7265 | 0,8632 | 0,9673 | 0,9123 | T30, TEST 592 gambar |
| Teacher YOLO11n | 0,7800 | 0,8915 | 0,9697 | 0,9290 | T05, satu checkpoint, TEST resmi |

Angka dibulatkan empat desimal dari tabel sumber. T30 juga memuat seed 42 dan 2025 serta rerata antarseed; gunakan itu saat membahas kestabilan KD. KD murni seed 42 adalah ablasi tambahan, bukan pengganti KD Hybrid full sebagai model utama. Nilai TEST ini menjawab mutu prediksi pada TEST resmi, **bukan akurasi setiap frame dari sesi live OP3**.

## Bukti tambahan kamera OP3 yang sudah tersedia

[T34](../../../analisis_performa/tabel/T34_akurasi_op3_hybrid_supervised_seed1337.md) mengevaluasi 260 frame yang sama (200 berobjek, 60 negatif) dengan 400 kotak acuan yang ditinjau manusia. KD Hybrid full seed 1337: mAP50–95 **0,4885**, precision makro **0,6836**, recall makro **0,5583**, F1 makro **0,5121**. Supervised seed 1337: **0,4414**, **0,7855**, **0,5729**, **0,6054**. Set ini eksploratif karena satu rangkaian pengambilan dan draf label awal dibantu model; teacher belum ada pada T34. Nilai F1 makro di sini memakai definisi berbeda dari tabel TEST.

## Urutan penyelesaian

1. Selesaikan 15 run live yang belum diukur tanpa mengubah threshold/checkpoint; dokumentasikan penyimpangan urutan dan adegan teacher yang sudah terjadi.
2. Hitung T36/T37 dari seluruh run untuk rumusan masalah 4–5.
3. Jalankan evaluasi teacher dan KD murni pada **frame serta label 260 OP3 yang sama** menurut Fase 8a prompt; cocokkan ulang angka Hybrid/Supervised dengan T34. T38 bersifat evaluasi domain OP3 eksploratif.
4. Jika bab hasil akan mengklaim generalisasi akurasi **pada kamera OP3** di luar satu adegan/sesi, ambil set OP3 baru dengan aturan sampling dan label final dibekukan sebelum melihat prediksi, lalu evaluasi ketiga model utama pada gambar identik. Lakukan setelah runtime agar perekaman tidak menambah beban CPU saat benchmark.

Run live berjalan pada percobaan ini hanya menyediakan keluaran, confidence, tracking, latensi, FPS, CPU, dan RAM. Tanpa kotak acuan per frame, cakupan keluaran live tidak dapat disebut precision, recall, F1, atau mAP; lihat [catatan interpretasi](05-ringkasan/CATATAN_AKURASI_PRECISION_ID.md).
