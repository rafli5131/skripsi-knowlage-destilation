# Protokol T42: ablasi kapasitas teacher pada VAL

Tanggal penetapan: 24 Oktober 2026, sebelum training T42. Bhre meminta T42 dijalankan. Eksperimen ini terpisah dari pemilihan Hybrid full seed 1337 untuk OP3; hasil T42 tidak mengganti model OP3, ambang operasi, atau keputusan D16.

## Pasangan terkendali

- Data: TRAIN/VAL resmi Advance Vision dengan fingerprint proyek yang sudah dikunci; TEST dan frame OP3 tidak dipakai.
- Pralatih resmi Ultralytics dari rilis [v8.3.0](https://github.com/ultralytics/assets/releases/tag/v8.3.0): `yolo11n.pt` SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1` dan `yolo11s.pt` SHA-256 `85a76fe86dd8afe384648546b56a7a78580c7cb7b404fc595f97969322d502d5`. Berkas disimpan di `models_local/teacher_ablation_t42/pretrained/`, yang diabaikan Git.
- Kedua teacher dilatih ulang pada tiga kelas dengan seed 42, 100 epoch, batch 16, 640 piksel, AdamW, `lr0=0.001`, `lrf=0.01`, warm-up 3 epoch, weight decay 0.0005, close mosaic 10, AMP mati, dan patience 30. Inisialisasi keduanya dari bobot COCO resmi yang sesuai arsitekturnya.
- Student menggunakan arsitektur YOLO11 skala t dan objective KD Hybrid full yang sama untuk kedua teacher. Tiap pasangan teacher memakai seed student 42, 1337, 2025, 100 epoch, serta resep training dasar yang sama. Student dimulai dari bobot acak sesuai eksperimen utama.
- Evaluator semua teacher dan student memakai pengaturan VAL T28 yang sama: mAP50–95, mAP50, serta precision/recall/F1 makro pada confidence 0,25. Kontrol supervised tiga seed dari T41 digunakan tanpa dilatih ulang. Bandingkan student antar-teacher secara berpasangan per seed; laporkan rasio pemulihan hanya bila penyebut memadai.

Ada delapan training baru: dua teacher dan enam student. Bobot teacher berada di `models_local/` dan tidak dipublikasikan. Run student ada di `runs/kd_teacher_ablation/` dengan nama unik; evaluasi di `runs/val_ablation/teacher_yolo11s_t42_20261024/`. T42 berupa CSV dan Markdown di `analisis_performa/tabel/`. Driver menunggu GPU L40 yang memori terpakai maksimal 8 GiB dan utilisasi maksimal 25% pada dua pemeriksaan berjarak 60 detik sebelum memulai satu training, untuk mengurangi benturan dengan job server yang sudah berjalan. Training gagal dihentikan dan tidak ditimpa otomatis.

Karena teacher utama YOLO11n lama mempunyai resep yang tidak tercatat lengkap, klaim pengaruh ukuran teacher hanya bersandar pada pasangan YOLO11n dan YOLO11s yang **dilatih ulang secara setara** di T42. Hasil ini deskriptif pada split VAL gambar dan tidak menghilangkan batas TEST atau provenance teacher lama.
