# T41: konfirmasi KD hibrida v2 S2 pada VAL tiga seed

Perbandingan berpasangan memakai seed 42, 1337, 2025 dan split VAL identik. Pemilihan ini belum merupakan uji pada data independen; TEST lama sudah diketahui saat v2 dirancang.

| Metode | mAP50-95 rerata ± SD | F1@0,25 rerata ± SD |
| --- | ---: | ---: |
| supervised | 0.7208 ± 0.0041 | 0.9213 ± 0.0025 |
| hybrid_full | 0.7505 ± 0.0018 | 0.9205 ± 0.0021 |
| hybrid_v2_s2 | 0.7475 ± 0.0013 | 0.9251 ± 0.0024 |

Selisih S2 − Hybrid full per seed untuk mAP50-95: +0.0002, -0.0052, -0.0042.
Selisih S2 − Hybrid full per seed untuk F1@0,25: +0.0054, +0.0045, +0.0040.

## Aturan seleksi terkunci

1. mAP rerata S2 tidak turun lebih dari 0,002: **gagal**.
2. F1 naik minimal 0,005 atau mAP naik minimal 0,004: **gagal**.
3. Metrik yang memenuhi syarat 2 membaik pada minimal dua seed: **gagal**.
4. mAP S2 melebihi Supervised pada ketiga seed: **lulus**.

**Keputusan menurut aturan VAL: Hybrid full tetap model KD utama; S2 dilaporkan sebagai ablasi**.
Keputusan operasional dan model OP3 hanya berubah setelah dicatat di dokumen keputusan. Rincian per seed dan kelas ada di [CSV](T41_konfirmasi_hybrid_v2_val.csv).
