# Hasil TEST lanjutan KD Hybrid full — 22 Oktober 2026

## Cakupan dan protokol

Enam checkpoint `best.pt` dievaluasi pada split TEST resmi yang sama: **592 gambar dan 734 anotasi**, kelas ball, gawang, robot. Student adalah YOLO11 skala `t` kustom (810.649 parameter), dengan teacher YOLO11n FP32 saat training Hybrid. Semua tiga seed Hybrid full dibandingkan berpasangan dengan supervised. Inferensi FP32 pada NVIDIA L40; imgsz 640, batch 16, confidence floor AP 0,001, NMS IoU 0,7, P/R/F1 makro pada confidence >0,25 dan matching IoU 0,50. Interval bootstrap per checkpoint ada di JSON sumber. Protokol dikunci dan dipush sebelum evaluasi. Fingerprint TEST: `aa9685a022c7484ef94cbfe68b6d000585d29de752071967709de66bed1762f1`.

TEST ini pernah dievaluasi untuk teacher dan KD murni. Hasil Hybrid adalah eksperimen lanjutan pada split yang sama; interpretasinya dibatasi pada gambar dalam dataset resmi. Tiga seed memberi variasi deskriptif, bukan bukti signifikansi kuat.

## Hasil akurasi

| metrik | Hybrid full, rerata ± SD | Supervised, rerata ± SD | Δ berpasangan, rerata ± SD |
| --- | --- | --- | --- |
| mAP50 | 0,9583 ± 0,0008 | 0,9601 ± 0,0034 | -0,0018 ± 0,0037 |
| mAP50-95 | 0,7469 ± 0,0022 | 0,7225 ± 0,0035 | +0,0244 ± 0,0040 |
| precision | 0,8519 ± 0,0024 | 0,8609 ± 0,0032 | -0,0090 ± 0,0025 |
| recall | 0,9698 ± 0,0007 | 0,9699 ± 0,0035 | -0,0000 ± 0,0028 |
| F1 | 0,9071 ± 0,0017 | 0,9121 ± 0,0026 | -0,0051 ± 0,0011 |

mAP50–95 TEST Hybrid full lebih tinggi pada ketiga pasangan seed:

| seed | Hybrid full | Supervised | Δ |
| --- | --- | --- | --- |
| 42 | 0,7447 | 0,7203 | +0,0244 |
| 1337 | 0,7468 | 0,7265 | +0,0203 |
| 2025 | 0,7492 | 0,7208 | +0,0284 |

Per kelas, selisih AP50–95 rerata berpasangan:

| kelas | Δ AP50–95, rerata ± SD |
| --- | --- |
| ball | +0,0513 ± 0,0095 |
| gawang | +0,0083 ± 0,0031 |
| robot | +0,0136 ± 0,0046 |

Metrik utama mAP50–95 naik `+0.0244`. Pada confidence tetap 0,25, F1 turun `-0.0051` dan precision turun `-0.0090`; selisih recall sekitar nol (`-0.000038`). Keunggulan AP tidak menunjukkan peningkatan semua metrik deteksi.

Kelas gawang perlu perhatian saat uji OP3: meskipun AP50–95 naik, precision@0,25 turun `-0.0259` dan F1@0,25 turun `-0.0193` terhadap supervised. Frame kamera berlabel diperlukan untuk melihat apakah pola ini muncul pada robot.

Ketiga hasil supervised yang diulang identik dengan metrik TEST historis pada checksum checkpoint dan manifest training yang sama. Kandidat tunggal untuk pengujian OP3 tetap Hybrid seed 1337 sesuai aturan VAL sebelum TEST; pemilihan ini tidak didasarkan pada hasil TEST.

Sebagai konteks eksperimen terdahulu pada split TEST yang sama, rerata mAP50–95 KD murni teacher-only `0.6630` dan teacher FP32 `0.7800`. Angka historis ini tidak dimasukkan ke perbandingan berpasangan Hybrid–supervised. Hybrid memakai loss deteksi berlabel tambahan, sehingga selisih dengan KD murni tidak mengisolasi satu komponen loss saja.

## Benchmark diagnostik server

Benchmark pada satu frame VAL tetap di memori memakai NVIDIA L40, FP32, batch 1, 30 pemanasan dan 200 iterasi ukur. Tabel lengkap ada di T32. Ringkasan berikut adalah median latency tiap checkpoint:

| seed | Hybrid median ms | Supervised median ms |
| --- | --- | --- |
| 42 | 8.887 | 11.681 |
| 1337 | 8.483 | 13.132 |
| 2025 | 8.632 | 12.323 |

Semua student memakai arsitektur, parameter, dan GFLOPs yang sama. Selisih waktu pada satu urutan benchmark host tidak dapat diatribusikan secara kausal ke KD. Benchmark ini tidak mengukur FPS kamera, latensi end-to-end, CPU, atau RAM OP3. Pengujian tersebut menunggu sesi robot idle dan berjalan dengan frame kamera berlabel yang diperiksa manual.

## Artefak sumber

- Manifest TEST: [`runs/final_test/hybrid_full_official_split_20261022/manifest.json`](../../runs/final_test/hybrid_full_official_split_20261022/manifest.json), SHA-256 `6713e29ac144b0bf0e0f87c1af978c91b1b02f96af4f749f28a46c537c297e42`.
- Benchmark: [`runs/benchmarks/hybrid_full_paired_20261022.json`](../../runs/benchmarks/hybrid_full_paired_20261022.json), SHA-256 `544f30aa35c647dd44b82bb3ad914ecdc144ea21ec0e6aed2fc6b998d3fa379b`.
- Tabel keseluruhan: [T30](../tabel/T30_kd_hybrid_test_berpasangan.md); per kelas: [T31](../tabel/T31_kd_hybrid_test_per_kelas.md); benchmark: [T32](../tabel/T32_kd_hybrid_benchmark_server.md); pelatihan: [T33](../tabel/T33_pelatihan_kd_hybrid_full.md).
- Protokol praevaluasi: [`PROTOKOL_TEST_KD_HYBRID_2026-10-22.md`](../../docs/PROTOKOL_TEST_KD_HYBRID_2026-10-22.md).
- `best.pt` Hybrid seed 1337 dan 2025 tersimpan pada direktori run lab/server dan hash-nya dicatat di manifest serta registry. Payload bobot dua seed itu belum dipublikasikan ke repo GitHub publik; reproduksi inferensi di checkout lain memerlukan transfer artefak berizin.
