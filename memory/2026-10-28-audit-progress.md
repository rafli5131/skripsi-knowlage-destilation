# Audit progres dan persiapan publikasi 28 Oktober 2026

Training utama tiga metode × tiga seed selesai. T40/T41 selesai; Hybrid full seed 1337 tetap model utama menurut D16, sementara S2 menjadi ablasi.

T42 telah melampaui memory 24 Oktober: manifest privat teacher YOLO11n retry1 berstatus complete dan results.csv mencapai epoch 100. Durasi manifest 8145,535 detik. Hasil `runs/val_ablation/teacher_yolo11s_t42_20261024/teacher_yolo11n_seed42_val.json` mencatat VAL mAP50–95 0,7760286 dan F1@0,25 0,9355309 pada 1213 gambar. Event terakhir `runs/kd_teacher_ablation/t42_status.jsonl` adalah evaluasi berhasil pada 24 Oktober pukul 06:10:07 UTC (13:10 WIB). Belum ada hasil teacher YOLO11s, enam student, atau tabel final T42. Proses host belum diverifikasi; driver dapat menunggu GPU tanpa event berkala. Jangan menyimpulkan driver mati dari log saja. Resume umum setelah tahap sukses belum didukung skrip sekarang.

Uji historis Hybrid OP3 sudah ada pada percobaan 27 dan T34, sehingga pernyataan lama agent.md bahwa Hybrid belum diuji robot sudah tertinggal. Uji setara baru T36/T37 dan evaluasi frame baru belum tersedia. D14 menempatkan uji live setara sebagai rencana bukti runtime akhir. Kondisi robot terkini belum diperiksa.

Draf Bab I–III masih memakai judul Pure KD dan Bab IV–V masih mengacu hasil 10 Oktober; perlu diselaraskan. Indeks T39/T40 juga masih memuat status historis meskipun T41 selesai.

Pengguna meminta push folder bre ke GitHub. Publikasi dikurasi untuk kode, protokol, metadata/hasil VAL, sumber training, dan best.pt student konfirmasi seed 1337/2025. Last.pt, log training mentah, teacher privat, serta data/log mentah robot tetap lokal. Catatan ini dibuat sebelum commit/push; keberhasilan publikasi harus diperiksa dari Git.
