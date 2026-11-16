# Sesi OP3 offline — jalur tunggal dan runtime

[T44 perbandingan jalur](../../../analisis_performa/tabel/T44_jalur_tunggal_op3_t38_t43.md) · [T45 rincian latensi dan CPU](../../../analisis_performa/tabel/T45_rincian_latensi_dan_cpu_op3.md) · [Grafik dengan konteks](grafik/jalur_dan_cpu_konteks_id.png)

Uji identitas 48/48 lulus. Empat model diuji dengan jalur prediktor dan faktor padding/NMS; rincian kondisi dan validasi endpoint ada pada T44. Rincian seluruh 24 run dan delapan replay utama dan dua kontrol OpenBLAS 4/2 ada pada T45. Bobot, frame, label, log mentah dan prediksi per frame tetap lokal.

Teacher FP32 yang diverifikasi: `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/best.pt`, 5.481.875 byte, SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`. Alias `models_local/teacher_fp32_best.pt` tidak ada; bobot tidak disalin di OP3.

## Batas interpretasi

T38 dan T43 adalah set eksploratif berbeda, bukan data independen lintas adegan. Prediktor dan validator memakai pengaturan preprocessing/NMS yang berbeda; pada tiga student T38 endpoint faktor val tidak cocok, sehingga pengaruh faktor pada bagian tersebut tidak ditafsirkan. Replay CPU dilakukan offline sekali per varian dengan data yang diulang, tanpa ROS; pengukuran per-thread bersifat tersampel. Metadata historis Torch 4/2 dicatat sebelum backend mulai dan bukan bukti pengukuran thread sepanjang run. Definisi waktu pada sumber Ivan belum diperiksa. Model maupun ambang tetap.

## Perintah salin dari laptop

Alamat Wi-Fi OP3 terdeteksi `192.168.1.147`; pastikan alamat masih sesuai. Jalankan dari laptop:

```bash
scp humanoid@192.168.1.147:/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/best.pt ./teacher_fp32_best.pt
sha256sum teacher_fp32_best.pt
ssh dindarosyidah@labkc-l40-debian 'mkdir -p "$HOME/skripsi/skripsi-knowlage-destilation/models_local/teacher_utama"'
scp teacher_fp32_best.pt dindarosyidah@labkc-l40-debian:skripsi/skripsi-knowlage-destilation/models_local/teacher_utama/best.pt
ssh dindarosyidah@labkc-l40-debian 'sha256sum "$HOME/skripsi/skripsi-knowlage-destilation/models_local/teacher_utama/best.pt"'
```

## Verifikasi akhir dan status Git

Dua puluh dari dua puluh endpoint predictor cocok juga untuk precision, recall, F1, TP dan frame negatif. Endpoint AP validator cocok pada 14 dari 20 pasangan model–set; enam ketidakcocokan adalah tiga student pada dua set T38 dan faktor tersebut tidak ditafsirkan. Hasil lengkap ada pada `runs/op3_single_path_eval/20261116_analysis_01/endpoint_operating_audit.json`.

Prompt dan skrip acuan dibaca dari objek Git `origin/main` revisi `ade031a89d0e9d5cb088c5615e31746fd9c43a4c`; branch kerja dimulai dari `d35c31b` dan tidak di-pull karena banyak file lokal belum dilacak. Kode acuan dipakai dari objek Git dengan hash tercatat, tanpa menimpa file lokal. Penambahan tautan ke T38/T43 mengubah hash Markdown, bukan angkanya; versi sebelum penambahan disimpan sebagai arsip dan manifest historis tetap dipertahankan.
