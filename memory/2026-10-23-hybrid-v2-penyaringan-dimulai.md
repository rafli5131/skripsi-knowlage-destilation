# Memori kerja: penyaringan KD hibrida v2 dimulai, 23 Oktober 2026

## Keputusan dan batas

Bhre meminta melanjutkan eksperimen `hybrid_v2` dengan syarat checkpoint lama tidak ditimpa atau dihapus. Protokol VAL dikunci sebelum training pada `docs/PROTOKOL_HYBRID_V2_2026-10-23.md`. S1–S3 adalah perbandingan awal; maksimal delapan run penyaringan direncanakan. Ambang 0,25 tetap titik operasi utama. TEST dan T34 OP3 tidak dipakai untuk seleksi.

## Yang dibuat

- Mode baru `hybrid_v2` pada `scripts/train_kd.py` dan loss head pada `scripts/kd_losses_v2.py`. Mode lama tetap memakai fungsi loss yang sama seperti sebelumnya.
- Konfigurasi baru `configs/kd_hybrid_v2_s1.yaml`, `s2.yaml`, `s3.yaml` di `runs/kd_hybrid_v2/`.
- Evaluator VAL baru `scripts/evaluate_hybrid_v2_val.py`, pengawas run berurutan `scripts/run_hybrid_v2_screen.py`, dan pembuat tabel `scripts/build_t40_hybrid_v2_val.py` serta `scripts/finalize_hybrid_v2_screen.py`.
- Perekaman sampel komponen loss label, fitur, kotak, dan kelas tiap 100 batch pada run baru. Nilai loss label dicatat sebagaimana dikembalikan Ultralytics dan memiliki skala batch; jangan langsung membandingkannya dengan komponen KD tanpa normalisasi.

## Status saat berkas ini dibuat

S1 seed 42 sedang berjalan di GPU 0 dengan Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130. Environment training membersihkan `PYTHONPATH`, `PYTHONHOME`, dan `LD_LIBRARY_PATH` yang berasal dari ROS sehingga paket tidak tercampur. Proses pertama gagal sebelum membuat run; proses kedua dimulai dengan benar. Pengawas akan menunggu S1 selesai, lalu mengevaluasi S1 dan menjalankan serta mengevaluasi S2, S3 secara berurutan. Finalizer akan menyusun T40 setelah seluruhnya selesai. Status ada pada `runs/kd_hybrid_v2/screen_s1_s3_status.jsonl`.

Hash checkpoint Hybrid full lama yang dipastikan masih ada: seed 42 `6cc425a2142fccb1ddc6be3d5fe070f27362c9fd3a71cc4e8dff346839e24c8a`, seed 1337 `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`, seed 2025 `68c4f20db711867e7bb508126638f09cbd482245887d835275d188ebd6e8afca`.

## Berikutnya

Periksa status dan tabel T40 setelah S1–S3 selesai. Bila pengawas gagal, baca `screen_s1_s3_status.jsonl` dan log tahap terkait; jangan memakai nama run yang sudah ada. Jika berhasil, tentukan S4–S8 dari hasil VAL sesuai protokol, kemudian konfirmasi kandidat pada seed 1337 dan 2025. Model Hybrid full lama tetap model utama sampai aturan seleksi tiga seed terpenuhi. Uji robot setelah model final dibekukan.
