# Percobaan 37 — T38, evaluasi offline empat model pada frame OP3

Pada 5 November 2026, empat checkpoint dievaluasi pada gambar dan label OP3 yang sama menggunakan package `op3_multi_session_eval`. Evaluasi membaca file lokal: **kamera, ROS, servo, dan gait tidak dijalankan**. T38 melengkapi perbandingan eksploratif domain kamera OP3; hasil runtime OP3 T36/T37 serta hasil TEST resmi tetap memiliki peran dan sumber terpisah.

## Komposisi dan pengaturan

- Tabel utama memakai **260 gambar**: 200 berobjek dan 60 tanpa target, dengan 400 kotak acuan ditinjau Bhre: 160 ball, 80 gawang, 160 robot. Frame negatif termasuk dalam 260, bukan tambahan.
- **50 frame gawang parsial** dievaluasi terpisah dan dikecualikan dari tabel utama karena definisi kotak tidak konsisten. Hasilnya tersedia dalam `results.json` lokal.
- Ukuran 640, CPU FP32, NMS IoU 0,7. AP memakai confidence floor 0,001; precision/recall/F1 memakai confidence **>0,25** dan pencocokan satu-ke-satu IoU **≥0,5**. F1 makro adalah rata-rata F1 tiap kelas; F1 mikro memakai jumlah TP/FP/FN gabungan.
- Label awal dibantu prediksi KD murni sebelum ditinjau manusia. Seluruh gambar berasal dari satu rangkaian pengambilan. Karena itu hasil retrospektif ini dapat mengandung bias anotasi dan tidak membuktikan generalisasi lintas adegan, jarak, pencahayaan, atau sesi. T38 tidak menggantikan TEST resmi maupun set eksternal baru yang independen.

## Hasil utama

| Model | mAP50 | mAP50–95 | Precision makro | Recall makro | F1 makro | Frame negatif dengan FP |
|---|---:|---:|---:|---:|---:|---:|
| Teacher YOLO11n | 0,7058 | 0,5004 | 0,8690 | 0,6833 | 0,6829 | 2/60 |
| KD Hybrid full seed 1337 | 0,7526 | 0,4885 | 0,6836 | 0,5583 | 0,5121 | 21/60 |
| Supervised seed 1337 | 0,7045 | 0,4414 | 0,7855 | 0,5729 | 0,6054 | 0/60 |
| KD murni seed 42 | 0,6301 | 0,4218 | 0,7386 | 0,4729 | 0,5008 | 0/60 |

Pada set ini teacher memperoleh mAP50–95 dan F1 makro tertinggi; Hybrid memperoleh mAP50 tertinggi. Pada ambang operasi Hybrid hanya mencocokkan 2/80 kotak gawang, sedangkan supervised 21/80. Hasil per kelas dan TP/FP/FN ada di T38. Perbedaan ini menggambarkan set eksploratif dan tidak menjadi dasar memilih ulang model atau threshold.

## Bukti dan grafik

- [Tabel T38 dan rincian per kelas](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) · [CSV](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.csv).
- Grafik perbandingan empat model: [Bahasa Indonesia](grafik_t38_empat_model_id_hd.png) · [English](grafik_t38_empat_model_en_hd.png), 2880×1800 piksel.
- Grafik F1 per kelas dan frame negatif: [Bahasa Indonesia](grafik_t38_kelas_negatif_id_hd.png) · [English](grafik_t38_kelas_negatif_en_hd.png), 2880×1260 piksel.
- [Audit sumber dan hash](audit_t38.json) · [draf pembahasan](DRAF_PEMBAHASAN_T38.md). Hasil lengkap per kelas/sesi, prediksi, dataset evaluasi dan manifest tersimpan lokal pada `runs/op3_multi_session_eval/20261105_empat_model_primary260_v1/`.

Pemeriksaan menunjukkan seluruh 310 entri frame dan sesi identik dengan manifest T34, dan hasil lengkap Hybrid serta supervised identik dengan hasil T34. Keempat hash checkpoint sesuai registry; teacher diambil dari `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/best.pt`, dengan hash yang sesuai dengan teacher protokol. Package pelaporan baru `ros2_packages/op3_t38_report` tidak mengubah package evaluasi lama.
