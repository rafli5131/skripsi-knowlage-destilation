# T19. Runtime OP3 pada kondisi idle dan berjalan

**Status: terukur secara eksploratif.** Bagian ini menampilkan uji terbaru dengan preview SSH-X aktif. Tiap kondisi satu run; angka menggambarkan sesi tersebut, bukan perubahan kinerja yang terisolasi akibat gerak robot. Riwayat 22 Oktober dipertahankan di [CSV](T19_servo_idle_vs_walking.csv).

| Model dan percobaan | Kondisi | Frame ukur | FPS efektif | Callback P50 / P95 (ms) | CPU median (% kapasitas 16 CPU logis) | RSS median (MiB) | Frame dengan keluaran gawang | Error frame |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Supervised seed 1337 · 25 | Idle | 724 | 12,06 | 52,13 / 163,95 | 78,34% | 362,99 | 724/724 (100%) | 0 |
| Supervised seed 1337 · 25 | Berjalan | 742 | 12,31 | 55,60 / 165,14 | 79,86% | 357,61 | 585/742 (78,84%) | 0 |
| KD murni seed 42 · 26 | Idle | 839 | 13,94 | 46,87 / 159,14 | 79,01% | 357,38 | 839/839 (100%) | 0 |
| KD murni seed 42 · 26 | Berjalan | 675 | 11,84 | 59,05 / 167,24 | 79,93% | 358,47 | 675/675 (100%) | 0 |
| KD Hybrid full seed 1337 · 27 | Idle | 726 | 12,09 | 54,54 / 164,70 | 80,24% | 363,12 | 726/726 (100%) | 0 |
| KD Hybrid full seed 1337 · 27 | Berjalan | 671 | 11,76 | 60,03 / 168,26 | 80,53% | 363,72 | 671/671 (100%) | 0 |

Sumber JSON, log, grafik, gambar, dan telemetry: [Supervised · percobaan 25](../../dokumentasi/2026-10-22/percobaan-25-supervised-retest-head-locked/README_ID.md), [KD murni · percobaan 26](../../dokumentasi/2026-10-23/percobaan-26-uji-ulang-kd-murni/README_ID.md), dan [KD Hybrid · percobaan 27](../../dokumentasi/2026-10-23/percobaan-27-uji-ulang-kd-hybrid/README_ID.md). Angka FPS memakai frame sesudah warmup. CPU adalah penggunaan proses yang dinormalisasi terhadap 16 CPU logis; RSS adalah memori resident proses detector.

## Protokol dan batas interpretasi

- Pada Supervised dan KD Hybrid, manager aktif saat idle dan berjalan; gerak kaki saat gait diverifikasi dari telemetry. Posisi kepala 19/20 dipertahankan tanpa perintah posisi baru. Pada KD murni, manager **tidak aktif saat idle** tetapi aktif saat berjalan. Karena itu, selisih FPS idle–berjalan KD murni juga dapat dipengaruhi status manager.
- Jendela walking KD murni dan Hybrid hanya 57 detik yang beririsan dengan gait terverifikasi; run Supervised memakai sekitar 60 detik. Adegan, pencahayaan, objek, dan waktu pengambilan berbeda antarmodel. Tidak ada pengulangan independen untuk estimasi variasi run.
- Keluaran gawang adalah jumlah frame yang diberi kotak oleh model, **bukan precision, recall, F1, atau akurasi**. Nilai 585/742 pada walking Supervised tidak dapat dinilai sebagai kegagalan tanpa label kebenaran pada frame yang sama.
- Lima run lama tetap ada dalam CSV sebagai riwayat. Dua run walking lama hanya berlabel perintah gait/operator tanpa verifikasi gerak independen; run Hybrid idle sebelum pemulihan OpenCR menghasilkan gawang 0/744. Untuk angka terbaru gunakan enam baris di atas.
