# Hasil lab/server: diagnosis KD jalur tengah, 23 Oktober 2026

Fase 0 selesai dan Fase 1 menghasilkan [T39](../tabel/T39_diagnosis_objektif_kd.md). Dua model seed 42 dievaluasi ulang di 1.213 gambar VAL dengan hasil identik terhadap T28. Dua prediksi Hybrid seed 1337/2025 ditangkap dari checkpoint lama untuk melengkapi diagnosis enam model. Tidak ada training, evaluasi TEST, akses robot, atau perubahan checkpoint.

Pada VAL, F1 Hybrid full dan Supervised berbeda kurang dari 0,001 pada ambang 0,25 bila dirata-ratakan tiga seed. Ambang terbaik pada VAL cenderung 0,35–0,45, tetapi hasil tersebut dipilih dan diukur pada data yang sama, sehingga hanya usulan pengujian lanjut. Audit keluaran head membuktikan `boxes` memuat 64 kanal distribusi DFL (`reg_max=16`) dan 8.400 anchor per gambar; hanya `one2many` yang ada pada pasangan checkpoint ini. Di satu batch, kurang dari 0,2% anchor memiliki skor maksimum teacher di atas 0,05.

Komponen *loss* fitur historis tidak dapat dipulihkan dari `best.pt`/`last.pt` karena proyektor fitur terlatih tidak tersimpan. Angka kotak, kelas, dan label pada T39 adalah diagnostik satu batch, bukan bukti dominasi total objektif. Pengukuran seluruh komponen harus diinstrumentasi pada eksperimen baru.

Tahap berikutnya di lab adalah membekukan grid S1–S8 dan aturan seleksi sebelum pelatihan `hybrid_v2`. Perkiraan berdasarkan T33 adalah sekitar 1–1,4 jam GPU per run 100 epoch: maksimal delapan run penyaringan sekitar 8–11,2 jam GPU, lalu maksimal dua kandidat dengan dua seed tambahan sekitar 4–5,6 jam GPU. Biaya teacher baru belum diukur dan harus dipisahkan dari estimasi ini. Konteks sandbox melihat CUDA `False` dan `nvidia-smi` gagal, tetapi pemeriksaan host baca-saja melihat tiga NVIDIA L40 dengan utilisasi GPU 0/1/2 sekitar 48%/100%/99% saat diaudit. Tidak ada alasan dari bukti itu untuk mengubah driver host. Ablasi teacher YOLO11s memerlukan bobot awal resmi dan, untuk klaim efek ukuran teacher, kontrol YOLO11n yang dilatih dengan resep identik beserta student tiga seed untuk tiap teacher. Uji live OP3 tetap setelah model dibekukan.

## Rekomendasi keputusan TH1

| Butir | Rekomendasi berdasarkan diagnosis |
| --- | --- |
| Penyaringan | Tetapkan S1–S3 sebagai perbandingan pertama yang sudah punya alasan mekanistik: KD kotak berbobot skor teacher, KL-DFL, dan gabungan. S4–S8 tetap sesuai grid yang dicatat di prompt, dengan maksimum delapan run dan ambang seleksi yang dikunci sebelum run pertama. |
| Seleksi kandidat | Pertahankan aturan empat syarat di bagian 5 prompt sebagai aturan eksploratif VAL tiga seed; jangan menyebut batas 0,004/0,005 sebagai signifikansi statistik. |
| Ambang deteksi | Pertahankan 0,25 sebagai protokol live utama yang sebanding dengan run OP3 sebelumnya. Ambang F1 terbaik dari VAL dilaporkan sebagai analisis sensitivitas sampai ada keputusan dan set eksternal baru untuk menguji ambang yang dibekukan. |
| Ablasi ukuran teacher | Bila tujuannya mengisolasi ukuran YOLO11n vs YOLO11s, wajib latih kedua teacher dengan data/resep sama dan masing-masing student dengan seed sama. Tanpa kontrol itu, laporkan eksplorasi pipeline saja. |
| Run baru | Simpan nilai semua komponen loss dan proyektor fitur terlatih dalam artefak privat, agar diagnosis historis tidak terulang. Jangan mengubah atau menimpa run lama. |

Rekomendasi ini belum mengganti model hasil KD utama. Checkpoint Hybrid full seed 1337 tetap kandidat OP3 sampai ada seleksi baru yang didokumentasikan.
