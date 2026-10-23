# Memori: konfirmasi KD hibrida v2 S2 selesai, 24 Oktober 2026

## Yang selesai

- Penyaringan S1–S8 seed 42 selesai pada [T40](../analisis_performa/tabel/T40_penyaringan_hybrid_v2_val_s1_s8.md); S2 dipilih sementara menurut aturan yang dikunci sebelum training.
- Konfirmasi S2 pada seed 1337 dan 2025 selesai, masing-masing 100 epoch. Seed 42 dari penyaringan dipakai ulang. Evaluasi ketiganya memakai VAL resmi yang sama dengan Hybrid full dan Supervised. [T41](../analisis_performa/tabel/T41_konfirmasi_hybrid_v2_val.md) selesai.
- Pada tiga seed, mAP50–95 S2 0,7475 ± 0,0013 versus Hybrid full 0,7505 ± 0,0018; F1@0,25 S2 0,9251 ± 0,0024 versus Hybrid full 0,9205 ± 0,0021. S2 gagal aturan penggantian karena penurunan mAP rerata sekitar 0,0030 melebihi batas 0,002 dan kenaikan F1 sekitar 0,0046 belum mencapai 0,005.
- Keputusan D16 dicatat pada `docs/DECISIONS.md`: Hybrid full tetap model KD utama, S2 sebagai ablasi. Registry, alias `op3_default`, dan checkpoint robot tidak diubah. TEST dan T34 OP3 tidak digunakan untuk seleksi.
- Laporan gabungan berada di [hasil lab/server](../analisis_performa/lab_server/HASIL_KD_HYBRID_V2_2026-10-24.md).

## Status Git dan artefak

Commit `cde5887` telah dipush pada 23 Oktober setelah pull `b324e78`; commit itu memuat kode, T39–T40, dan delapan `best.pt` screening seed 42. Artefak konfirmasi seed 1337/2025 dan T41 dibuat setelah commit tersebut dan masih lokal saat memori ini ditulis. Jangan menyatakan sudah dipush sebelum memeriksa Git lagi. `last.pt` dan log training tetap lokal. Bobot teacher tetap di luar repo.

## Berikutnya

Untuk penelitian utama, lanjutkan uji live OP3 setara dan evaluasi frame baru dengan Hybrid full seed 1337, Supervised seed 1337, Pure KD seed 42, serta teacher sesuai prompt robot terbaru ketika robot siap. Operator mengendalikan kondisi idle/berjalan; detektor tidak memerintah servo. Frame auto-label adalah draf yang harus ditinjau Bhre. T42 ablasi teacher YOLO11s terpisah dan belum dijalankan; T43 tidak diperlukan karena S2 bukan model final. Jangan mengklaim TEST sebagai holdout baru atau angka VAL sebagai akurasi kamera OP3.
