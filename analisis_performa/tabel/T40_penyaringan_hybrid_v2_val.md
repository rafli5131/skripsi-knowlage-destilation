# T40: penyaringan awal KD hibrida v2 pada VAL

Hanya seed 42. Pemilihan bersifat eksploratif; TEST dan T34 OP3 tidak dipakai.
Aturan terkunci: [protokol](../../docs/PROTOKOL_HYBRID_V2_2026-10-23.md). Konfigurasi terbaik setelah S3: **s2**.

| Tahap | mAP50-95 | F1@0,25 | F1 rerata kelas | Terpilih saat tahap itu? |
| --- | ---: | ---: | ---: | --- |
| baseline | 0.7488 | 0.9220 | 0.9206 | yes |
| s1 | 0.7465 | 0.9204 | 0.9188 | no |
| s2 | 0.7489 | 0.9274 | 0.9258 | yes |
| s3 | 0.7462 | 0.9276 | 0.9262 | no |

Nilai per kelas, precision, recall, SHA-256 checkpoint, dan path JSON sumber ada pada [CSV](T40_penyaringan_hybrid_v2_val.csv).
