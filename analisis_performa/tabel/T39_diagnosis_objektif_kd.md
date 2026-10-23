# T39. Diagnosis awal objektif KD pada VAL

Status 23 Oktober 2026: audit dan diagnosis yang dapat dihitung tanpa GPU/robot selesai. **Belum ada model baru atau training `hybrid_v2`.** Sumber angka per seed adalah [CSV T39](T39_diagnosis_objektif_kd.csv), dengan histogram TP/FP per kelas di [CSV pendamping](T39_histogram_confidence_tp_fp.csv). Keenam prediksi memakai 1.213 gambar VAL resmi dan sidik jari split yang sama.

| Model | Seed | F1@0,25 | F1 terbaik pada grid VAL | Ambang VAL | FP@0,25 |
| --- | ---: | ---: | ---: | ---: | ---: |
| KD Hybrid full | 42 | 0,9220 | 0,9392 | 0,40 | 353 |
| KD Hybrid full | 1337 | 0,9181 | 0,9371 | 0,35 | 345 |
| KD Hybrid full | 2025 | 0,9214 | 0,9343 | 0,40 | 302 |
| Supervised | 42 | 0,9235 | 0,9400 | 0,40 | 310 |
| Supervised | 1337 | 0,9186 | 0,9262 | 0,45 | 318 |
| Supervised | 2025 | 0,9218 | 0,9407 | 0,40 | 320 |

F1 di sini adalah rerata *precision* per kelas dan rerata *recall* per kelas, lalu rerata harmonik keduanya, sesuai evaluator T28. Nilai terbaik dicari pada ambang 0,05–0,90 dengan langkah 0,05 **pada VAL yang sama**, sehingga optimistis sebagai estimasi performa dan belum menjadi keputusan ambang OP3. Rerata F1@0,25 adalah 0,9205 Hybrid dan 0,9213 Supervised. Bila setiap seed memilih ambang terbaik di VAL, reratanya 0,9369 dan 0,9356; selisih kecil ini bukan bukti kenaikan yang akan bertahan pada data baru. ECE sepuluh bin pada CSV hanya diagnostik kalibrasi kepercayaan deteksi pada prediksi dengan *confidence* >0,25, bukan kalibrasi seluruh peluang kelas.

## Audit dan reproduksi

- Reproduksi seed 42 pada VAL disimpan terpisah di `runs/val_ablation/hybrid_20261023_phase0_reproduction/`. Hybrid: mAP50–95 **0,7487697525007468** dan F1@0,25 **0,9220323253426412**; Supervised: **0,7189302996225481** dan **0,9234655863184226**. Keempat nilai identik dengan `runs/val_ablation/hybrid_20261022_multiseed/` sampai angka yang disimpan. Evaluasi memakai CPU FP32, 640 piksel, 1.213 gambar VAL; TEST tidak dijalankan.
- Checkpoint teacher YOLO11n SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c` cocok dengan registri. Lingkungan terkunci: Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130, NumPy 1.26.4. Konteks sandbox ini tidak melihat CUDA dan `nvidia-smi` gagal; pemeriksaan baca-saja pada host melihat tiga NVIDIA L40. Ini bukan bukti driver host rusak.
- Dua berkas prediksi Hybrid seed 1337 dan 2025 baru ada di `runs/val_diagnostics/hybrid_objective_20261023/`; empat prediksi lainnya di `runs/val_diagnostics/official_split_20261020/`. Semua checkpoint lama tetap utuh.

## Keluaran head dan komponen loss

Pada 16 gambar VAL tetap, teacher dan student seed 42 sama-sama memiliki `reg_max=16`, `boxes=[16,64,8400]`, `scores=[16,3,8400]`, dan **hanya cabang `one2many`**. Bukti numerik ada di `runs/kd_diagnosis/20261023_heads_val_batch16.json`. Kode Ultralytics 8.4.130 `nn/modules/head.py` pada `Detect.forward_head` membentuk `boxes` dari 4 × `reg_max` keluaran konvolusi sebelum *decode*. `utils/loss.py` pada `v8DetectionLoss.bbox_decode` menerapkan *softmax* ke 16 bin. Ini mendukung percobaan KL-DFL pada distribusi mentah, dengan susunan `[batch, 4, 16, anchor]`; bentuk serta gradien tetap perlu diperiksa pada implementasi baru. SHA-256 sumber `head.py`: `38a31163093ae01fe691a68d1eecdab74456151c98140b28bf1da1bc9a0bdc23`; `loss.py`: `c3bcc774547b8fcc5066ad4877fb96074f3d43844a4df5772de8706fd3549761`.

Pada batch tersebut, proporsi lokasi teacher dengan skor maksimum di atas 0,05/0,25/0,50 berturut-turut **0,154% / 0,137% / 0,115%**. Jadi sebagian besar anchor adalah latar. Temuan ini mendukung diagnosis bahwa pembobotan kelas murni berdasarkan skor teacher dapat terlalu melemahkan pembelajaran latar, tetapi **belum membuktikan** penyebab kegagalan pilot `pure_weighted`.

Pada batch VAL tetap yang sama dengan label, komponen deteksi student adalah box **1,5055**, kelas **0,8807**, DFL **1,4612**; KD kotak Smooth L1 mentah **1,0071**, KD kelas BCE temperatur 2 **0,01037**. Angka lengkap di `runs/kd_diagnosis/20261023_label_head_loss_val_batch16.json`. Ini hanya potret satu batch dengan *direct resize* 640, bukan rerata training atau reproduksi persis *rect validation*. `best.pt` dan `last.pt` menyimpan `DetectionModel` student tanpa proyektor fitur terlatih, sehingga *feature loss* historis **tidak dapat dihitung secara sah**. Karena satu komponen tidak tersedia dan normalisasi suku berbeda, jangan menyatakan komponen mana yang mendominasi total objektif historis.

## Keputusan operasional berikutnya

Fase 0 lulus; Fase 1 cukup untuk merancang penyaringan tetapi belum mengukur seluruh *loss* historis. Kandidat paling langsung untuk tahap eksploratif adalah pembobotan **hanya** KD kotak berdasarkan skor teacher (S1), KL-DFL pada kotak (S2), dan kombinasinya (S3). Pembobotan kelas dengan dasar nonnol (S4) serta temperatur/bobot S5–S8 tetap kandidat sekunder. Seluruh seleksi dilakukan di VAL. Sebelum training baru, tetapkan grid final dan aturan seleksi, tambahkan pencatatan semua komponen *loss* termasuk proyektor fitur pada run baru, serta pastikan akses GPU tersedia. Jangan memakai TEST lama atau 260 frame OP3 untuk memilih kandidat.
