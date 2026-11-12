# T43 — sensitivitas label 52 frame

**Sementara:** label Bhre dan Dipo selesai; sesi label alternatif sedang berlangsung dan urutan tiga set belum dapat disimpulkan. Keduanya menggunakan 52 frame identik. Aturan kotak diperjelas setelah label awal Bhre; pengaruh peninjau dan aturan tidak dapat dipisahkan.

| Kelas | Pasangan IoU ≥0,5 | Rata-rata IoU | Median IoU |
|---|---:|---:|---:|
| ball | 40/40 | 0.6811 | 0.6748 |
| gawang | 40/40 | 0.6389 | 0.6307 |
| robot | 40/40 | 0.8882 | 0.8969 |

| Model | mAP50–95 Bhre | mAP50–95 Dipo | F1 Bhre | F1 Dipo |
|---|---:|---:|---:|---:|
| Teacher | 0.7409 | 0.4625 | 0.6582 | 0.6582 |
| KD Hybrid | 0.8134 | 0.4328 | 0.9876 | 0.9876 |
| Supervised | 0.7888 | 0.5230 | 0.9041 | 0.9041 |
| KD Murni | 0.7056 | 0.3995 | 0.6667 | 0.6667 |

Pada hasil sementara, urutan mAP50–95 berubah antara label Bhre dan Dipo. Ini belum memisahkan efek peninjau dari perubahan atau klarifikasi aturan. AP dan metrik operasi memakai jalur preprocessing berbeda sebagaimana dijelaskan dalam [sensitivitas confidence](T43_sensitivitas_confidence.md). Jangan memilih ulang model dari hasil ini.
