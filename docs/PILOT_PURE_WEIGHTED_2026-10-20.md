# Pilot `pure_weighted` — 20 Oktober 2026

## Tujuan dan batas

Pilot membandingkan `pure_weighted` terhadap baseline `pure_v4` pada **seed 42**, dengan teacher YOLO11n, student YOLO11 kustom skala `t`, split Roboflow resmi, dan anggaran maksimum 100 epoch yang sama. Pilihan objective ini disetujui pengguna untuk melengkapi ablasi lab/server. Teacher tetap beku; label TRAIN tidak masuk loss student. TEST tidak digunakan untuk memilih model atau hyperparameter.

## Perubahan objective

Loss fitur P3/P4/P5 tetap sama dengan baseline. Pada setiap lokasi keluaran Detect, bobotnya adalah `w_i = max_c sigmoid(z_teacher[c,i])`. Loss Smooth L1 pada logit kotak dan BCE pada logit kelas teacher dihitung per elemen, dikalikan `w_i`, lalu dibagi dengan jumlah bobot dan jumlah kanal. Temperatur kelas tetap 2,0; bobot fitur/kotak/kelas masing-masing tetap 1,0. Dengan demikian perbedaan pilot terhadap baseline hanya pembobotan lokasi pada dua komponen head loss. Implementasi ada di [`scripts/kd_losses.py`](../scripts/kd_losses.py), konfigurasi di [`configs/kd_pure_weighted.yaml`](../configs/kd_pure_weighted.yaml), dan pemanggilnya di [`scripts/train_kd.py`](../scripts/train_kd.py).

## Protokol keputusan yang ditetapkan sebelum hasil dilihat

Checkpoint dipilih dari VAL selama training. Setelah training selesai, baseline tiga seed dan pilot dievaluasi ulang dengan pengaturan VAL yang sama melalui [`scripts/evaluate_val_ablation.py`](../scripts/evaluate_val_ablation.py). Metrik utama keputusan adalah mAP50–95 VAL pilot terhadap baseline **seed 42**. Precision, recall, F1 pada confidence 0,25, AP per kelas, dan recall `gawang` dilaporkan sebagai trade-off. Jika mAP50–95 pilot meningkat, kandidat layak dibawa ke pengulangan tiga seed; kenaikan satu seed saja belum cukup untuk klaim peningkatan umum. Bila tidak meningkat, `pure_v4` tetap model utama dan T04 tetap mencatat hasil ablasi negatif.

## Artefak

- Run selesai 100 epoch; checkpoint terbaik berasal dari epoch 89: [`best.pt`](../runs/kd/yolo11_tiny_pure_weighted_pilot_seed42/weights/best.pt).
- Manifest training: [`manifest.json`](../runs/kd/yolo11_tiny_pure_weighted_pilot_seed42/manifest.json).
- Manifest training memuat hash checkpoint, konfigurasi, skrip, modul loss, dan fingerprint dataset.
- Hasil evaluasi VAL: [`pure_weighted_seed42_val.json`](../runs/val_ablation/pure_weighted_20261020/pure_weighted_seed42_val.json) dan tiga JSON baseline di folder yang sama.
- Tabel ablasi: [`T04_ablasi_kd_val.md`](../analisis_performa/tabel/T04_ablasi_kd_val.md).
- Rincian kelas: [`T04_ablasi_kd_val_per_kelas.md`](../analisis_performa/tabel/T04_ablasi_kd_val_per_kelas.md).

## Hasil dan keputusan

Empat checkpoint dievaluasi ulang pada 1.213 gambar VAL resmi dengan FP32 pada CPU server, imgsz 640, NMS IoU 0,7, dan confidence floor 0,001 untuk AP. Dibanding baseline `pure_v4` seed 42, `pure_weighted` seed 42 memperoleh mAP50–95 **0,5907 vs 0,6826** (selisih **−0,0919**). Pada confidence tetap >0,25 dan IoU pencocokan 0,50, precision makro **0,0473 vs 0,7899**, recall makro **0,9906 vs 0,9623**, dan F1 **0,0903 vs 0,8676**. Recall `gawang` naik **0,9752 vs 0,9494**, tetapi precision `gawang` turun **0,1203 vs 0,7509**. AP50–95 ketiga kelas juga turun: `ball` 0,7044 vs 0,7334, `gawang` 0,4914 vs 0,5798, dan `robot` 0,5762 vs 0,7346.

Menurut kriteria utama yang ditetapkan sebelum hasil dilihat, `pure_weighted` **tidak dipilih** untuk pengulangan tiga seed atau deploy OP3; `pure_v4` tetap model utama. T04 mencatat pilot ini sebagai ablasi negatif. Interpretasi dibatasi pada satu seed kandidat dan split VAL Advance Vision; hasil TEST historis tidak dipakai untuk memilih objective.

Angka VAL Advance Vision dalam pilot ini bukan akurasi kamera ROBOTIS OP3. Checkpoint pilot tidak otomatis mengganti file model deploy OP3.
