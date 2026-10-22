# Percobaan 28 — evaluasi offline KD Hybrid vs Supervised pada kamera OP3

**Status: selesai, eksploratif.** Tidak ada perintah kamera live, motor, servo, atau gait pada percobaan ini. Dua checkpoint seed 1337 dijalankan pada berkas JPEG dan label yang sama, di komputer OP3. Ini pengukuran akurasi deteksi, bukan pengukuran FPS live. Rincian hasil per kelas tersedia di [T34](../../../analisis_performa/tabel/T34_akurasi_op3_hybrid_supervised_seed1337.md).

## Input dan protokol

- Set utama: 200 gambar berobjek + 60 gambar tanpa target; 400 kotak GT (ball 160, gawang 80, robot 160). Set 50 gambar gawang parsial dievaluasi terpisah dan **dikecualikan** dari perbandingan utama karena definisi kotak tidak konsisten.
- Gambar, label, dan log tinjauan `bhre` diverifikasi evaluator; checksum seluruh 310 pasangan gambar/label cocok dengan manifest evaluasi sebelumnya. Kedua model memakai set dan urutan gambar yang identik.
- Checkpoint Hybrid full seed 1337 SHA-256 `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`; Supervised seed 1337 SHA-256 `d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041`.
- Ultralytics 8.4.130, torch 2.4.1+cpu, CPU FP32, input 640, NMS IoU 0,7. AP memakai confidence floor 0,001. P/R/F1 dihitung pada confidence >0,25 dan IoU ≥0,5. Ini berbeda dari runtime live yang memakai NMS IoU 0,45 dan BotSORT.

## Hasil utama

| Model | mAP50–95 | Precision makro | Recall makro | F1 makro | Frame negatif dengan prediksi palsu |
|---|---:|---:|---:|---:|---:|
| KD Hybrid full seed 1337 | 0,4885 | 0,6836 | 0,5583 | 0,5121 | 21/60 |
| Supervised seed 1337 | 0,4414 | 0,7855 | 0,5729 | 0,6054 | 0/60 |

Hybrid lebih tinggi pada mAP50–95 sebesar 0,0471, tetapi lebih rendah pada F1 makro ambang operasi sebesar 0,0933. Per kelas, Hybrid lebih tinggi pada AP50–95 ball (0,8367 vs 0,8027) dan robot (0,3780 vs 0,2145); Supervised lebih tinggi pada AP50–95 gawang (0,3069 vs 0,2508). Pada confidence >0,25, hanya 2/80 GT gawang cocok untuk Hybrid, dibanding 21/80 pada Supervised. Karena itu, hasil tidak mendukung klaim satu model unggul di semua ukuran.

![Precision dan recall per kelas pada ambang operasi](../../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/grafik_precision_recall.png)

![AP50 dan AP50–95 per model](../../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/grafik_map.png)

## Batas dan jejak audit

Semua gambar berasal dari rangkaian pengambilan kamera OP3 yang sama. Label awal dibantu keluaran KD murni seed 42 sebelum tinjauan manusia; risiko bias anotasi belum dihilangkan. Tidak ada pengukuran variasi lintas sesi, pencahayaan, atau jarak. Set ini tidak boleh disebut uji eksternal final yang independen dan tidak boleh digabung dengan TEST Advance Vision. Kotak palsu pada frame negatif adalah temuan spesifik adegan, bukan tingkat false positive umum.

- [Manifest input, checkpoint, checksum, dan pengaturan](../../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/input_manifest.json)
- [Hasil JSON lengkap](../../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/results.json) · [CSV evaluator](../../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/summary.csv) · [CSV T34](../../../analisis_performa/tabel/T34_akurasi_op3_hybrid_supervised_seed1337.csv)
- Prediksi per frame Hybrid (lokal: `../../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/per_frame_hybrid_full_seed1337.jsonl`) · Prediksi per frame Supervised (lokal: `../../../runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/per_frame_supervised_seed1337.jsonl`)
- [Evaluator dan cara menjalankan ulang](../../../ros2_packages/op3_multi_session_eval/README.md)
