# Audit asal 60 frame negatif OP3, 21 Oktober 2026

## Jejak yang tersedia

1. [Percobaan 02](../../dokumentasi/2026-10-21/percobaan-02-frame-negatif/README.md) menjelaskan 60 JPEG sesi awal, delapan frame yang dikeluarkan setelah pemeriksaan visual (frame 20–21 menampilkan tepi gawang; 34–39 mengandung benda putih yang belum pasti), dan delapan frame pengganti dari sesi kedua. Kandidat akhir berisi 52 + 8 gambar. Berkas `curation_manifest.json` mentah yang memetakan setiap frame tidak tersedia pada checkout server.
2. Pada saat pengambilan, detektor KD berjalan di topic debug dan CSV live dilaporkan memiliki nol baris deteksi. Perekam mengambil topic gambar mentah. Tidak ada catatan bahwa algoritme memilih frame berdasarkan confidence model. Nol deteksi tidak membuktikan ketiadaan objek.
3. [Percobaan 12](../../dokumentasi/2026-10-21/percobaan-12-peninjauan-60-frame-negatif/README.md) mencatat draf label otomatis dari KD yang semuanya kosong, diikuti tinjauan manusia resolusi penuh pada 60/60 gambar. Setelah itu, [manifest audit](../../runs/op3_camera_eval/20261021_negative_candidate_01_fp_audit/input_manifest.json) merekam hash gambar dan label; [ringkasan audit](../../runs/op3_camera_eval/20261021_negative_candidate_01_fp_audit/summary.json) melaporkan deteksi palsu offline kedua model.

## Penilaian

Dokumentasi menyatakan kurasi akhir memakai pemeriksaan visual manusia, tetapi detektor KD juga aktif selama perekaman dan draf label otomatis dibuat sebelum peninjauan. Tanpa manifest kurasi mentah dan log keputusan per frame pada server, **apakah pemilihan frame bergantung pada keluaran model tidak dapat dipastikan dari artefak**. Set negatif ini berasal dari satu rangkaian adegan terkurasi; hasil deteksi palsu hanya berlaku deskriptif pada sampel tersebut. Audit ini tidak mengubah data atau label.
