# Percobaan 29: diagnosis KD jalur tengah di server lab

Tanggal: 23 Oktober 2026. Perangkat: CPU server AMD EPYC dalam sandbox; lingkungan Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130. Tujuan: menyelesaikan audit serta diagnosis yang tersedia tanpa robot dan tanpa training baru sebelum pemilihan objektif `hybrid_v2`.

## Prosedur dan artefak

1. Verifikasi hash teacher YOLO11n dan lingkungan. `nvidia-smi` serta CUDA tidak tersedia dalam sandbox ini; tidak ada perubahan driver atau paket.
2. Evaluasi ulang Hybrid full seed 42 dan Supervised seed 42 pada VAL resmi dengan `scripts/evaluate_val_ablation.py`, `--device cpu --threads 8`, keluaran baru `runs/val_ablation/hybrid_20261023_phase0_reproduction/`. Hasil mAP50–95 dan F1@0,25 identik dengan hasil 22 Oktober.
3. Tangkap prediksi VAL Hybrid seed 1337/2025 dengan `scripts/capture_t39_val_predictions.py` di `runs/val_diagnostics/hybrid_objective_20261023/`. Hitung sapuan ambang dan histogram TP/FP enam model dengan `scripts/build_t39_kd_diagnosis.py`; hasil kurasi di [T39](../../../analisis_performa/tabel/T39_diagnosis_objektif_kd.md).
4. Audit satu batch 16 gambar VAL dengan `scripts/diagnose_kd_heads_val.py` dan `scripts/diagnose_kd_label_head_loss_val.py`. JSON mentah ada di `runs/kd_diagnosis/`. Gambar dan label diverifikasi terhadap fingerprint sebelum dibaca; TEST tidak disentuh.

## Hasil

- F1 rerata tiga seed pada ambang 0,25: Hybrid full 0,9205 dan Supervised 0,9213. Ambang terbaik pada **VAL yang sama** memberi 0,9369 dan 0,9356. Ini diagnosis ambang, bukan angka uji final.
- Teacher dan student memiliki `reg_max=16`; kotak mentah berukuran 64 kanal dan 8.400 anchor/gambar. Hanya cabang `one2many` ditemukan. Proporsi anchor teacher dengan skor >0,05 adalah 0,154% pada satu batch.
- Komponen loss label, KD kotak, dan KD kelas dapat dihitung sebagai potret satu batch. Proyektor fitur terlatih tidak ada dalam `best.pt`/`last.pt`, sehingga komponen fitur historis tidak dapat dipulihkan secara sah.

## Batas dan langkah berikutnya

Seluruh pengukuran batch memakai *direct resize* 640 dan tidak mereproduksi persis pemrosesan `rect` pada evaluasi VAL. Tidak ada checkpoint baru. Tahap berikutnya adalah membekukan grid/aturan seleksi dan menambahkan pencatatan loss fitur untuk run baru; training membutuhkan akses GPU dan tidak dijalankan dalam konteks ini. Uji OP3 tetap menunggu robot dan pembekuan model.

Laporan gabungan: [hasil diagnosis lab](../../../analisis_performa/lab_server/HASIL_DIAGNOSIS_KD_JALUR_TENGAH_2026-10-23.md). Prompt lab dan robot direvisi pada sesi yang sama.
