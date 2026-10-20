# Catatan keputusan protokol

| Tanggal | Keputusan | Catatan |
| --- | --- | --- |
| 2026-10-19 | D2: pure teacher-only KD (`pure_v4`) | Bhre memilih KD murni. Objektif hybrid tidak menjadi kandidat. Pilihan ini berlaku untuk eksperimen utama; kandidat objektif pure KD lain memerlukan persetujuan sebelum pelatihan. |
| 2026-10-20 | D1: teacher YOLO11n dan student YOLO11 skala `t` yang sudah ada | Bhre menyetujui arsitektur sekarang. Student berjumlah 810.649 parameter dan bukan YOLO11n standar; judul dan rumusan masalah akhir harus menyebut model secara akurat. |
| 2026-10-20 | Pilot `pure_weighted` disetujui | Bhre meminta kandidat teacher-only KD berbobot lokasi teacher untuk melengkapi ablasi lab/server. `pure_v4` tetap baseline. Pilot memakai seed 42 dan anggaran 100 epoch yang sama; pemilihan kandidat hanya pada VAL. D3 untuk training utama tiga seed tetap belum dikunci. |

D3 sampai D10 masih berstatus `BELUM DIKUNCI` di [`configs/analysis.yaml`](../configs/analysis.yaml). Eksperimen pelatihan utama baru tidak dimulai sebelum keputusan relevan dicatat.
