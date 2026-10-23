# Prompt penulisan Bab IV dan V skripsi KD dan ROBOTIS OP3 (V2)

> Versi 2, 23 Oktober 2026. Menggantikan `PROMPT_BAB_IV_V_HASIL_KD_OP3_2026-10-23.md`. Perubahan utama: atas arahan Bhre, **uji live OP3 dengan kondisi setara adalah pengujian akhir** dan menjadi sumber utama jawaban rumusan masalah nomor 4 dan 5. Pernyataan pada memory 23 Oktober, `analisis_performa/INDEKS.md`, dan `prompt/inventaris_tabel_dan_prompt.md` bahwa evaluasi live OP3 berada di luar hasil utama **tidak berlaku lagi**. Persetujuan pembimbing atas perubahan fokus ini belum tercatat di `docs/DECISIONS.md`; tandai sebagai hal yang perlu dikonfirmasi.

Gunakan prompt ini untuk menyiapkan naskah. Jangan menjalankan robot, kamera, *training*, atau pengujian ulang.

## Prasyarat

Bab IV ditulis lengkap hanya setelah uji live setara (`prompt/PROMPT_UJI_ULANG_LIVE_SETARA_OP3_DENGAN_TEACHER.md`, perkiraan percobaan 29) dan evaluasi *offline* empat model (perkiraan percobaan 30) selesai, serta tabel T36, T37, dan T38 tersedia. Bila belum tersedia, tetap susun kerangka dan bagian yang buktinya sudah ada, lalu tulis `[BELUM DIUKUR: <apa yang ditunggu>]` pada bagian RQ4, RQ5, dan akurasi *teacher* di kamera OP3. Jangan mengisi kekosongan itu dengan angka percobaan 16 sampai 27.

## Instruksi siap pakai

Bertindak sebagai penulis ilmiah bidang deteksi objek dan *Knowledge Distillation* (KD). Susun **draf baru Bab IV (Hasil dan Pembahasan) dan Bab V (Kesimpulan dan Saran)** untuk skripsi Bhre, Teknik Komputer FILKOM UB. Tipe penelitian implementatif-pengembangan; penelitian ini mengimplementasikan dan menguji metode KD yang sudah ada, bukan mengusulkan algoritme KD baru.

### Aturan bahasa dan klaim

- Bahasa Indonesia ragam baku akademis. Jangan memakai tanda pisah *em dash*; susun ulang kalimatnya, bukan sekadar mengganti tandanya.
- Hindari pola khas AI: tanpa "Dalam era digital saat ini", tanpa "Selain itu" beruntun, tanpa kalimat pembuka yang mengulang pertanyaan, tanpa penutup yang merangkum ulang tanpa isi baru.
- Istilah baku: "algoritme", "analisis"; dilarang memakai "rancang bangun". Istilah asing dicetak miring kecuali nama produk (ROBOTIS OP3, YOLO11, Ultralytics, PyTorch, ROS 2).
- Istilahnya *Knowledge Distillation*, bukan *Knowledge Development*.
- Setiap klaim faktual dari literatur wajib bersitasi. Bila sumber belum ada, tulis `[BUTUH SITASI: <apa yang dicari>]`. Jangan mengarang penulis, tahun, judul, atau DOI.
- Setiap angka hasil harus dapat ditelusuri ke CSV, JSON, atau manifest. Bila ragu pada suatu fakta teknis, tulis bahwa hal itu belum pasti dan tandai untuk konfirmasi.

### Rumusan masalah yang dijawab

Gunakan lima rumusan masalah berikut. `docs/DECISIONS.md` mencatat Bhre melaporkan pembimbing sudah menyetujuinya, tanpa tanggal. Bila redaksi di Bab I berbeda, tandai perbedaannya; jangan memilih sendiri.

1. Bagaimana implementasi sistem deteksi objek berbasis ROS 2 yang menjalankan model YOLO11 skala t hasil *knowledge distillation* (KD) pada robot humanoid ROBOTIS OP3?
2. Bagaimana tingkat akurasi, berdasarkan nilai *mean average precision* (mAP), model YOLO11 skala t hasil KD dibandingkan dengan model berarsitektur sama yang dilatih secara *supervised* dan dengan *teacher* YOLO11n?
3. Bagaimana kinerja ketiga model tersebut jika ditinjau dari nilai *precision*, *recall*, dan *F1-score*?
4. Berapa rata-rata latensi dan *frames per second* (FPS) yang dicapai model hasil KD dan *teacher* YOLO11n saat beroperasi secara *real-time* pada kondisi robot diam dan berjalan?
5. Bagaimana tingkat efisiensi penggunaan CPU dan RAM model hasil KD dan *teacher* YOLO11n saat dijalankan secara penuh pada komputer *onboard* robot?

"Model hasil KD" adalah KD Hybrid full (`hybrid_full`), dipilih pada VAL sebelum TEST dibuka; kandidat perangkat adalah seed 1337. KD murni (`pure_v4`) dan `hybrid_feature` dilaporkan sebagai ablasi. Pada RQ4 dan RQ5, pembanding utama adalah KD Hybrid seed 1337 dan *teacher*; *supervised* seed 1337 dan KD murni seed 42 disajikan sebagai pembanding pelengkap dengan label yang jelas.

### Pemetaan rumusan masalah ke bukti

| RQ | Bukti utama | Bukti pendukung | Jangan dicampur dengan |
|---|---|---|---|
| 1 | `OP3_PYTORCH_RUNTIME.md`, `scripts/op3_pytorch_detector.py`, alur topic `/thesis/image_raw` ke `/vision/debug_image`, keberhasilan keempat model berjalan pada percobaan 29 | Percobaan 16 sampai 27 sebagai riwayat uji fungsi | Klaim akurasi |
| 2 | TEST Advance Vision tiga seed: T05 sampai T07, T30, T31 | Kamera OP3 260 *frame*: T34 dan T38 | Benchmark L40 |
| 3 | P/R/F1 TEST pada T05, T30, T31 | P/R/F1 kamera OP3 pada T34 dan T38 | F1 T27 (definisi berbeda) |
| 4 | Uji live setara: T36 dan T37 (rata-rata, median, P95 latensi; FPS efektif; *idle* dan berjalan; tiga ulangan) | Pembagian latensi per tahap; percobaan 16 sampai 27 sebagai uji pendahuluan | T32 (L40), T35 (waktu *training*/TEST) |
| 5 | CPU dan RSS dari T36 dan T37 | Spesifikasi NUC T15 | Benchmark server |

### Audit sumber sebelum menulis

1. Baca `docs/DECISIONS.md`, `PROTOKOL_EKSPERIMEN_SKRIPSI.md`, `KERANGKA_BAB_SKRIPSI.md`, draf Bab I sampai III terbaru, draf Bab IV dan V lama, `analisis_performa/INDEKS.md`, `dokumentasi/INDEKS.md`, serta dokumentasi percobaan 29 dan 30.
2. Cocokkan angka penting T05 sampai T07, T28 sampai T31, T34 sampai T38 dengan CSV, `results.csv`, `summary_metrics.json`, dan manifest primer.
3. Periksa `jadwal_run.csv` dan `log_penyimpangan.md` percobaan 29. Hanya *run* berstatus sah yang masuk ringkasan; jumlah ulangan sah per model dan kondisi wajib disebut.
4. Bila sumber bertentangan, gunakan urutan: keputusan dan protokol bertanggal, lalu manifest dan log primer, lalu tabel hasil terkini, lalu laporan percobaan, lalu draf lama. Catat konfliknya.

### Hal yang wajib dipisahkan

- **TEST Advance Vision** mengukur kualitas deteksi pada split dataset resmi. Split ini pernah dipakai pada eksperimen *teacher* dan KD murni, jadi jangan menyebutnya *holdout* yang belum pernah dilihat. Untuk kesimpulan metode, gunakan rerata tiga seed berpasangan beserta simpangannya.
- **Kamera OP3 260 *frame*** (T34, T38) adalah evaluasi eksploratif satu rangkaian pengambilan. Label awal dibantu KD murni seed 42 sebelum ditinjau Bhre, sehingga berpotensi bias. Definisi F1 makro T34 dan T38 (rerata F1 per kelas) berbeda dari F1 T27.
- **Uji live setara** (percobaan 29) mengukur runtime dengan *preview* SSH -X aktif, `op3_manager` aktif, seluruh servo menyala, ID 19/20 menahan arah kamera, empat *thread* intra-op dan dua inter-op, jendela 60 detik, tiga ulangan, urutan digilir. Keluaran per kelas pada uji live bukan akurasi.
- **Uji pendahuluan** (percobaan 16 sampai 27) memakai protokol yang berbeda dan hanya boleh dibahas sebagai riwayat atau pembanding deskriptif.
- **Waktu *training* dan TEST** (T35) serta **latensi L40** (T32) adalah informasi pendukung di lingkungan server. Durasi sesi TEST pada T35 mencakup beberapa *checkpoint* sekaligus, bukan durasi per model. Latensi L40 dari sesi berbeda tidak boleh digabung untuk mengklaim satu metode lebih cepat. Keduanya bukan FPS robot.

### Struktur Bab IV

1. **Lingkungan dan protokol pengujian.** Server pelatihan dan evaluasi; komputer *onboard* OP3 (T15); definisi kondisi diam dan berjalan; pengaturan setara percobaan 29 dalam satu tabel; urutan *run*; kriteria *run* sah.
2. **Hasil implementasi sistem (RQ1).** Arsitektur node ROS 2, topic, alur data, konfigurasi model, dan hasil uji fungsional keempat model di OP3. Sajikan dalam bentuk tabel kebutuhan fungsional dan hasil pengujiannya bila Bab III memuat daftar kebutuhan tersebut.
3. **Hasil pelatihan dan pemilihan model.** Kurva dan metrik VAL, pemilihan `hybrid_full` seed 1337 pada VAL, ringkasan waktu *training* dari T35 sebagai informasi pendukung.
4. **Akurasi mAP (RQ2).** TEST tiga seed untuk *teacher*, *supervised*, KD murni, dan KD Hybrid; per kelas. Lalu evaluasi kamera OP3 empat model (T38) sebagai pemeriksaan domain robot, terpisah dari TEST.
5. ***Precision*, *recall*, dan *F1-score* (RQ3).** Pada ambang operasi 0,25. Bahas temuan yang tidak mendukung hipotesis, misalnya F1 Hybrid lebih rendah dari *supervised* walau mAP lebih tinggi, *recall* gawang yang rendah, dan prediksi palsu pada *frame* negatif.
6. **Latensi dan FPS live (RQ4).** Rata-rata, median, dan P95 latensi serta FPS efektif per model pada kondisi diam dan berjalan, tiga ulangan. Rasio *teacher* terhadap KD Hybrid. Perubahan dari diam ke berjalan. Pembagian latensi per tahap untuk menjelaskan apakah FPS dibatasi inferensi atau bagian lain.
7. **Penggunaan CPU dan RAM (RQ5).** CPU proses (persen satu CPU logis dan persen kapasitas 16 CPU logis) dan RSS per model dan kondisi. Bahas efisiensi relatif terhadap jumlah parameter dan GFLOPs (T01 atau T26).
8. **Pembahasan *trade-off*.** Akurasi TEST dan kamera OP3 terhadap biaya runtime di OP3; kapan selisih akurasi sebanding dengan selisih biaya; perbandingan deskriptif dengan uji pendahuluan.
9. **Batas validitas.** n = 3 ulangan dan satu adegan; *preview* aktif memengaruhi biaya runtime secara seragam; TEST yang pernah dipakai; bias label kamera OP3; server bersama untuk *training*; tidak ada *ground truth* per *frame* pada uji live.

Rujuk tabel dan grafik yang benar-benar ada. *Caption* memuat dataset atau adegan, n, satuan, perangkat, seed, protokol, dan sumber. Dengan n = 3, tampilkan nilai tiap ulangan atau rentangnya; jangan menulis klaim signifikansi statistik.

### Struktur Bab V

Kesimpulan bernomor 1 sampai 5, satu untuk setiap rumusan masalah, masing-masing dengan angka dan lingkupnya. Kesimpulan RQ4 dan RQ5 bersumber dari percobaan 29. Bila suatu bukti belum tersedia, tulis bahwa rumusan tersebut belum terjawab beserta alasannya. Saran mengikuti keterbatasan nyata, misalnya data uji kamera yang lebih independen dan beragam, ulangan lebih banyak pada beberapa adegan, uji tanpa *preview*, atau optimasi *runtime*. Saran adalah pekerjaan mendatang, bukan hasil.

### Keluaran dan pemeriksaan akhir

Simpan sebagai **draf baru** `DRAF_BAB_IV-V_KD_OP3_V2_<YYYY-MM-DD>.md`; pertahankan semua draf lama. Sertakan:

- matriks `klaim → tabel/CSV/JSON → batas interpretasi`;
- daftar tabel dan gambar yang dirujuk;
- daftar penanda `[BUTUH SITASI]` dan `[BELUM DIUKUR]`;
- daftar hal yang memerlukan keputusan pembimbing, minimal persetujuan uji live OP3 sebagai pengujian akhir dan protokol percobaan 29.

Periksa semua angka terhadap sumber primer, tautan lokal, satuan dan koma desimal, identitas seed dan *checkpoint*, konsistensi rumusan masalah, serta tidak adanya tanda pisah *em dash*. Jangan commit atau push tanpa instruksi Bhre.
