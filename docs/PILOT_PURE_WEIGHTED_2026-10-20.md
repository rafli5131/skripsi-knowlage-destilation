# Pilot `pure_weighted` — 20 Oktober 2026

## Tujuan dan batas

Pilot membandingkan `pure_weighted` terhadap baseline `pure_v4` pada **seed 42**, dengan teacher YOLO11n, student YOLO11 kustom skala `t`, split Roboflow resmi, dan anggaran maksimum 100 epoch yang sama. Pilihan objective ini disetujui pengguna untuk melengkapi ablasi lab/server. Teacher tetap beku; label TRAIN tidak masuk loss student. TEST tidak digunakan untuk memilih model atau hyperparameter.

## Perubahan objective

Loss fitur P3/P4/P5 tetap sama dengan baseline. Pada setiap lokasi keluaran Detect, bobotnya adalah `w_i = max_c sigmoid(z_teacher[c,i])`. Loss Smooth L1 pada logit kotak dan BCE pada logit kelas teacher dihitung per elemen, dikalikan `w_i`, lalu dibagi dengan jumlah bobot dan jumlah kanal. Temperatur kelas tetap 2,0; bobot fitur/kotak/kelas masing-masing tetap 1,0. Dengan demikian perbedaan pilot terhadap baseline hanya pembobotan lokasi pada dua komponen head loss. Implementasi ada di [`scripts/kd_losses.py`](../scripts/kd_losses.py), konfigurasi di [`configs/kd_pure_weighted.yaml`](../configs/kd_pure_weighted.yaml), dan pemanggilnya di [`scripts/train_kd.py`](../scripts/train_kd.py).

## Protokol keputusan yang ditetapkan sebelum hasil dilihat

Checkpoint dipilih dari VAL selama training. Setelah training selesai, baseline tiga seed dan pilot dievaluasi ulang dengan pengaturan VAL yang sama melalui [`scripts/evaluate_val_ablation.py`](../scripts/evaluate_val_ablation.py). Metrik utama keputusan adalah mAP50–95 VAL pilot terhadap baseline **seed 42**. Precision, recall, F1 pada confidence 0,25, AP per kelas, dan recall `gawang` dilaporkan sebagai trade-off. Jika mAP50–95 pilot meningkat, kandidat layak dibawa ke pengulangan tiga seed; kenaikan satu seed saja belum cukup untuk klaim peningkatan umum. Bila tidak meningkat, `pure_v4` tetap model utama dan T04 tetap mencatat hasil ablasi negatif.

## Artefak

- Log training: `runs/kd/pure_weighted_pilot_seed42.log`.
- Run dan calon checkpoint: `runs/kd/yolo11_tiny_pure_weighted_pilot_seed42/weights/best.pt`.
- Manifest training memuat hash checkpoint, konfigurasi, skrip, modul loss, dan fingerprint dataset.
- Hasil evaluasi VAL: `runs/val_ablation/pure_weighted_20261020/`.
- Tabel ablasi: [`T04_ablasi_kd_val.md`](../analisis_performa/tabel/T04_ablasi_kd_val.md).

Angka VAL Advance Vision dalam pilot ini bukan akurasi kamera ROBOTIS OP3. Checkpoint pilot tidak otomatis mengganti file model deploy OP3.
