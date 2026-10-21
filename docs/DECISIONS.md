# Catatan keputusan protokol

| Tanggal | Keputusan | Catatan |
| --- | --- | --- |
| 2026-10-19 | D2: pure teacher-only KD (`pure_v4`) | Bhre memilih KD murni. Objektif hybrid tidak menjadi kandidat. Pilihan ini berlaku untuk eksperimen utama; kandidat objektif pure KD lain memerlukan persetujuan sebelum pelatihan. |
| 2026-10-20 | D1: teacher YOLO11n dan student YOLO11 skala `t` yang sudah ada | Bhre menyetujui arsitektur sekarang. Student berjumlah 810.649 parameter dan bukan YOLO11n standar; judul dan rumusan masalah akhir harus menyebut model secara akurat. |
| 2026-10-20 | Pilot `pure_weighted` disetujui | Bhre meminta kandidat teacher-only KD berbobot lokasi teacher untuk melengkapi ablasi lab/server. `pure_v4` tetap baseline. Pilot memakai seed 42 dan anggaran 100 epoch yang sama; pemilihan kandidat hanya pada VAL. D3 untuk training utama tiga seed tetap belum dikunci. |
| 2026-10-20 | Hasil pilot `pure_weighted`: tidak dipilih | T04 VAL menunjukkan mAP50–95 0,5907, di bawah `pure_v4` seed 42 sebesar 0,6826; F1 pada confidence 0,25 juga turun 0,0903 vs 0,8676. Sesuai kriteria pilot yang dicatat sebelum training, `pure_v4` tetap model utama. Tidak ada pengulangan tiga seed atau perubahan model deploy dari hasil pilot ini. |
| 2026-10-21 | Catatan mekanisme pilot `pure_weighted` | Spesifikasi pilot membobot loss kotak **dan** kelas dengan `max_c sigmoid(z_teacher)`. Kode di `scripts/kd_losses.py` menerapkan spesifikasi itu. Pada lokasi latar dengan bobot mendekati nol, kontribusi BCE kelas untuk menekan logit student juga mengecil. Penurunan precision VAL konsisten dengan mekanisme ini; audit tidak menemukan penyimpangan implementasi dari spesifikasi pilot. Hasil pilot tidak menguji apakah pembobotan kotak saja berguna. |

D3 sampai D10 masih berstatus `BELUM DIKUNCI` di [`configs/analysis.yaml`](../configs/analysis.yaml). Eksperimen pelatihan utama baru tidak dimulai sebelum keputusan relevan dicatat.
