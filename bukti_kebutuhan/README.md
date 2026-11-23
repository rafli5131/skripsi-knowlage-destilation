# Bukti uji kebutuhan fungsional dan nonfungsional

Folder ini mengumpulkan bukti untuk kebutuhan KF-01 sampai KF-05 dan KNF-01 pada
[Bab 4](../laporan/draf-7-bab/BAB_4_REKAYASA_KEBUTUHAN.md) serta hasil uji pada
[Bab 6](../laporan/draf-7-bab/BAB_6_PENGUJIAN_DAN_PEMBAHASAN.md). Pengujian memakai
pendekatan kotak hitam: sistem dinilai dari masukan dan keluarannya, bukan dari struktur
kode di dalamnya (Khan dan Khan, 2012; Nidhra dan Dondeti, 2012). KNF-01 dirumuskan
sebagai kebutuhan kinerja, yaitu salah satu jenis kebutuhan nonfungsional (Glinz, 2007).

Semua bukti berasal dari pengukuran yang sudah dilakukan. Tidak ada uji baru untuk folder
ini. Daftar kebutuhan dan pengujian retrospektif dari log disetujui pembimbing secara lisan
pada 12 November 2026 (D18 di [`docs/DECISIONS.md`](../docs/DECISIONS.md)). Kriteria lulus
pada tabel di bawah dirumuskan dari indikator Bab 4 sesudah data tersedia, sehingga
penilaiannya bersifat retrospektif.

## Ringkasan kasus uji

| ID uji | Kebutuhan | Hasil yang diharapkan | Hasil aktual | Status | Bukti |
|---|---|---|---|---|---|
| UJ-KF-01 | KF-01 Menerima citra kamera OP3 | Setiap run memproses frame (>0) dan error frame = 0; jumlah frame dan error pada T36 sama dengan ringkasan run. | 24/24 run memenuhi; 17.090 frame terproses tanpa error. | Lulus | [KF-01_menerima_citra/](KF-01_menerima_citra/README.md) |
| UJ-KF-02 | KF-02 Mendeteksi bola, gawang, dan robot | Ketiga kelas muncul sebagai kotak berlabel kelas pada setiap run. | 24/24 run memuat ketiga kelas; cakupan frame terendah bola 100,0%, gawang 92,5%, robot 100,0%. | Lulus | [KF-02_deteksi_tiga_kelas/](KF-02_deteksi_tiga_kelas/README.md) |
| UJ-KF-03 | KF-03 Menyediakan ID pelacakan pada mode tambahan | Bola utama memiliki ID dan ID yang sama tetap muncul pada setiap frame jendela selama bola bergerak. | ID 2 muncul pada 382/382 frame; pusat bergeser 257,2 px (X) dan 130,8 px (Y). Kotak bola tambahan dengan ID lain muncul pada 13 frame. | Lulus dengan catatan | [KF-03_id_pelacakan/](KF-03_id_pelacakan/README.md) |
| UJ-KF-04 | KF-04 Mencatat runtime per frame | Setiap baris memuat timestamp, durasi tahap, CPU, RSS, dan kolom error; log mentah cocok dengan T36. | 24/24 log jendela di repositori lengkap; 24/24 log mentah di OP3 cocok dengan T36 (pemeriksaan T45). | Lulus | [KF-04_log_runtime/](KF-04_log_runtime/README.md) |
| UJ-KF-05 | KF-05 Menampilkan preview deteksi | Kotak, nama kelas, confidence, dan ID tampak pada preview. | Enam tangkapan dari empat model menampilkan kotak, kelas, confidence, dan ID. | Lulus untuk contoh yang tersedia | [KF-05_preview/](KF-05_preview/README.md) |
| UJ-KNF-01 | KNF-01 Laju pemrosesan | FPS efektif rata-rata tiap run >= 8 FPS pada kondisi diam dan berjalan. | 24/24 run memenuhi; terendah 9,69 FPS (Teacher YOLO11n, diam, ulangan 3). | Lulus | [KNF-01_laju_pemrosesan/](KNF-01_laju_pemrosesan/README.md) |

Tabel lengkap dengan kolom prosedur dan masukan: [`kasus_uji_kf_knf.csv`](kasus_uji_kf_knf.csv).

## Isi folder

| Folder | Isi |
|---|---|
| `KF-01_menerima_citra/` | Jumlah frame dan error frame 24 run dari T36, dicocokkan dengan ringkasan tiap run |
| `KF-02_deteksi_tiga_kelas/` | Cakupan frame dan confidence median tiap kelas untuk 24 run, contoh keluaran |
| `KF-03_id_pelacakan/` | ID bola per frame pada sesi bola bergerak, grafik lintasan dan ID |
| `KF-04_log_runtime/` | Pemeriksaan kolom log jendela di repositori dan kecocokan 24 log mentah dengan T36 |
| `KF-05_preview/` | Tangkapan preview beranotasi dari empat model |
| `KNF-01_laju_pemrosesan/` | FPS efektif 24 run terhadap batas 8 FPS, grafik runtime |

Setiap folder memuat README dengan prosedur, hasil, sumber, dan batas tafsir.
[`manifest_bukti_sha256.json`](manifest_bukti_sha256.json) mencatat SHA-256 setiap berkas
di folder ini dan setiap berkas sumber yang dibaca. Gambar adalah salinan identik dari
dokumentasi percobaan; sumber aslinya tidak diubah.

## Batas bukti

- Lulus berarti kebutuhan terpenuhi pada run dan contoh yang diperiksa, bukan jaminan pada
  semua kondisi.
- KF-02 hanya menilai bahwa keluaran berisi kelas dan kotak. Ketepatan deteksi terhadap label
  acuan dinilai pada RM2 dan RM3 (TEST, T38, T43, T44).
- KF-03 diuji pada satu sesi bola bergerak berdurasi sekitar 30 detik. Pelacakan bukan tujuan
  wajib penelitian.
- Log mentah 24 run, frame, dan label tetap tersimpan lokal di OP3. Folder ini hanya memuat
  ringkasan dan hash.

## Membangkitkan ulang

```bash
python3 scripts/build_bukti_kebutuhan.py --replace
```

Dibangkitkan dari commit `a4bc9b23306a`.
