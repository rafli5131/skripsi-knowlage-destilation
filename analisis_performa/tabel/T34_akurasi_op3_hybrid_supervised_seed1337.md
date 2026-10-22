# T34. Akurasi kamera OP3 eksploratif: KD Hybrid full vs Supervised seed 1337

Kedua checkpoint dievaluasi pada **260 gambar identik** (200 gambar berobjek dan 60 tanpa target), dengan 400 kotak ground truth yang telah ditinjau `bhre`: 160 ball, 80 gawang, dan 160 robot. Pengaturan: `imgsz=640`, CPU FP32, NMS IoU 0,7; AP memakai confidence floor 0,001, sedangkan P/R/F1 memakai confidence **>0,25** dan pencocokan satu-ke-satu IoU **≥0,5**. Ini evaluasi *offline*, terpisah dari throughput live OP3.

| Model | mAP50 | mAP50–95 | P makro | R makro | F1 makro | F1 mikro | TP / FP / FN | Frame negatif dengan FP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KD Hybrid full seed 1337 | 0,7526 | 0,4885 | 0,6836 | 0,5583 | 0,5121 | 0,6464 | 266 / 157 / 134 | 21/60 |
| Supervised seed 1337 | 0,7045 | 0,4414 | 0,7855 | 0,5729 | 0,6054 | 0,6471 | 254 / 131 / 146 | 0/60 |

| Kelas (GT) | Model | P | R | F1 | AP50 | AP50–95 | TP / FP / FN |
|---|---|---:|---:|---:|---:|---:|---:|
| Ball (160) | Hybrid | 0,9755 | 0,9938 | 0,9845 | 0,9950 | 0,8367 | 159 / 4 / 1 |
| Ball (160) | Supervised | 0,9938 | 0,9938 | 0,9938 | 0,9949 | 0,8027 | 159 / 1 / 1 |
| Gawang (80) | Hybrid | 0,6667 | 0,0250 | 0,0482 | 0,4874 | 0,2508 | 2 / 1 / 78 |
| Gawang (80) | Supervised | 1,0000 | 0,2625 | 0,4158 | 0,5822 | 0,3069 | 21 / 0 / 59 |
| Robot (160) | Hybrid | 0,4086 | 0,6563 | 0,5036 | 0,7755 | 0,3780 | 105 / 152 / 55 |
| Robot (160) | Supervised | 0,3627 | 0,4625 | 0,4066 | 0,5365 | 0,2145 | 74 / 130 / 86 |

Hybrid unggul **+0,0471 mAP50–95**, tetapi tertinggal **0,0933 F1 makro** pada ambang operasi. AP mengintegrasikan peringkat prediksi pada banyak ambang confidence; F1 di sini hanya memakai satu ambang. F1 makro adalah rerata aritmetika F1 tiga kelas, bukan F1 dari P/R makro. Pada gawang, recall Hybrid di ambang 0,25 hanya 2/80 walau AP50-nya 0,4874. Hybrid juga memberi 21 kotak robot pada 21/60 frame negatif; Supervised tidak memberi kotak pada frame negatif.

**Batas:** seluruh gambar berasal dari satu rangkaian pengambilan OP3, dan draf anotasi awal dibantu KD murni seed 42 sebelum ditinjau manusia. Karena itu, hasil dapat memuat bias anotasi dan tidak mewakili generalisasi lintas adegan, jarak, atau pencahayaan. Set **50 frame gawang parsial** dihitung terpisah oleh evaluator, tetapi *tidak dimasukkan* ke tabel utama karena definisi kotaknya tidak konsisten. Angka ini tidak menggantikan TEST Advance Vision ataupun T27 yang membandingkan checkpoint seed 42 lain.

Sumber: [CSV T34](T34_akurasi_op3_hybrid_supervised_seed1337.csv), [manifest input dan hash](../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/input_manifest.json), [hasil lengkap](../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/results.json), [grafik P/R per kelas](../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/grafik_precision_recall.png), [grafik AP](../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/grafik_map.png), serta [dokumentasi percobaan](../../dokumentasi/2026-10-23/percobaan-28-evaluasi-offline-hybrid-supervised-260/README_ID.md).
