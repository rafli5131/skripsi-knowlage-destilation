# Hasil eksperimen KD hibrida v2 pada VAL, 24 Oktober 2026

## Ringkasan

Eksperimen perbaikan objektif KD hibrida selesai untuk delapan konfigurasi penyaringan seed 42 dan konfirmasi kandidat S2 pada seed 1337 serta 2025. Seluruh pemilihan memakai VAL resmi 1.213 gambar; TEST lama dan 260 frame OP3 T34 tidak dipakai memilih konfigurasi. Rancangan dan ambang seleksi dibekukan sebelum training pada [protokol](../../docs/PROTOKOL_HYBRID_V2_2026-10-23.md). Semua run baru tersimpan di `runs/kd_hybrid_v2/`; checkpoint lama tidak diubah.

[T40](../tabel/T40_penyaringan_hybrid_v2_val_s1_s8.md) memilih S2 pada seed 42. S2 menggunakan KL pada distribusi DFL 16 bin untuk KD kotak, tanpa pembobotan anchor, dengan loss label, fitur, dan kelas seperti Hybrid full. T40 hanya penyaringan eksploratif satu seed. [T41](../tabel/T41_konfirmasi_hybrid_v2_val.md) memberi hasil berikut pada tiga seed:

| Metode | mAP50–95 rerata ± SD | F1@0,25 rerata ± SD |
| --- | ---: | ---: |
| Supervised | 0,7208 ± 0,0041 | 0,9213 ± 0,0025 |
| Hybrid full | 0,7505 ± 0,0018 | 0,9205 ± 0,0021 |
| Hybrid v2 S2 | 0,7475 ± 0,0013 | 0,9251 ± 0,0024 |

Selisih S2 terhadap Hybrid full per seed untuk mAP50–95 adalah +0,0002, −0,0052, dan −0,0042. Selisih F1@0,25 adalah +0,0054, +0,0045, dan +0,0040. S2 meningkatkan F1 pada ketiga seed, tetapi rerata peningkatannya sekitar +0,0046, di bawah syarat +0,005; rerata mAP turun sekitar −0,0030, melewati batas penurunan 0,002. Karena itu S2 **tidak lolos** aturan penggantian. Hybrid full tetap model KD utama; S2 adalah ablasi metode. Hasil ini tidak membuktikan S2 secara umum lebih buruk pada semua metrik atau domain OP3.

## Artefak dan batas

- [Diagnosis T39](../tabel/T39_diagnosis_objektif_kd.md), [penyaringan T40](../tabel/T40_penyaringan_hybrid_v2_val_s1_s8.md), dan [konfirmasi T41](../tabel/T41_konfirmasi_hybrid_v2_val.md) adalah sumber angka utama. CSV masing-masing memuat metrik per kelas, path JSON VAL, dan hash checkpoint.
- Manifest per run dan `best.pt` baru ada di `runs/kd_hybrid_v2/yolo11_tiny_hybrid_v2_s<id>_seed<seed>/`. Berkas `loss_component_samples.jsonl` mencatat contoh komponen label dan KD selama training; loss label mengikuti skala batch Ultralytics, sehingga nilainya tidak langsung sebanding dengan komponen KD tanpa normalisasi.
- Evaluasi ini pada split gambar Roboflow. Riwayat TEST yang sudah pernah dibuka dan provenance teacher yang belum lengkap tetap menjadi batas metodologi. Tidak ada klaim akurasi kamera OP3 dari T41.
- `configs/model_registry.yaml`, alias `op3_default`, checkpoint Hybrid full, dan prompt uji robot tidak diubah oleh hasil S2. Eksperimen teacher YOLO11s T42 belum dijalankan. Karena model KD final tetap Hybrid full, TEST tambahan T43 untuk v2 tidak diperlukan.

## Langkah berikutnya

Gunakan Hybrid full seed 1337 yang telah dipilih dari VAL sebagai kandidat OP3 sesuai keputusan sebelumnya. Uji live setara dan evaluasi eksternal pada frame OP3 baru masih memerlukan robot siap serta peninjauan label manusia. Ablasi teacher YOLO11s boleh dilaporkan sebagai eksperimen terpisah bila ingin meneliti efek kapasitas teacher; untuk mengisolasi ukuran teacher, kontrol YOLO11n harus dilatih dengan resep dan data yang sama.
