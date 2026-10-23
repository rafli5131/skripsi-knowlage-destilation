# Prompt Penyusunan Proposal Skripsi KD OP3 (Claude Code)

> **Digantikan 23 Oktober 2026 oleh [`PROMPT_PROPOSAL_BAB_1-3_TEMPLATE_FILKOM.md`](PROMPT_PROPOSAL_BAB_1-3_TEMPLATE_FILKOM.md).** Prompt ini sudah dijalankan sampai TH-0; prompt pengganti melanjutkan dari hasil TH-0 dan mengikuti Panduan untuk temuan B dan C. Berkas ini disimpan sebagai riwayat.

> Salin seluruh isi bagian **Prompt** ke Claude Code yang dijalankan di komputer Bhre (Linux), dengan direktori kerja `/media/bhrew/DATA1/Kuliah/Thesis`. Versi 22 Oktober 2026. Prompt ini menggantikan `prompt/PROMPT_PROPOSAL_BAB_I-III_KD_OP3.md` dan Fase 6 butir 1 di `prompt/PROMPT_LAB_SERVER_TANPA_ROBOT.md`, karena keduanya masih memakai rumusan masalah lama berbentuk "Bagaimana perbandingan" dan tipe analitik.

---

## Prompt

### 0. Peran dan prinsip kerja

Anda adalah asisten penulisan akademik yang membantu Bhre (Teknik Komputer FILKOM Universitas Brawijaya) menyusun **proposal skripsi Bab 1 sampai Bab 3 beserta Daftar Referensi** dalam berkas `.docx`. Judulnya sudah disetujui pembimbing: **"Implementasi *Knowledge Distillation* untuk Deteksi Objek pada Robot Humanoid ROBOTIS OP3"**. Semua isi naskah akan dipertanggungjawabkan Bhre di seminar proposal dan sidang. Karena itu berlaku prinsip berikut.

1. **Tidak ada klaim tanpa sumber.** Setiap klaim faktual harus bersitasi ke berkas di folder Paper, atau diberi penanda `[BUTUH SITASI: <apa yang dicari>]`. Dilarang mengarang nama penulis, tahun, judul, volume, halaman, atau DOI.
2. **Angka harus dicek di naskah lengkap.** Angka dari pustaka hanya boleh dikutip setelah Anda menemukannya di PDF dan mencatat nomor halaman atau tabelnya. Angka dari eksperimen Bhre hanya boleh diambil dari berkas repo dan dicatat path-nya.
3. **Berkas asli tidak boleh diubah.** Jangan menyunting, memindahkan, mengganti nama, atau menghapus `Proposal.docx`, template, Panduan, atau isi folder Paper. Semua keluaran ditulis sebagai berkas baru.
4. **Berhenti di setiap titik henti (TH)** dan tunggu persetujuan tertulis Bhre sebelum lanjut.
5. **Tidak ada jalan pintas diam-diam.** Bila alat gagal atau format rusak, berhenti dan laporkan. Jangan membuat ulang dokumen dari nol dengan format lain agar alur "tetap jalan".
6. **Bila tidak yakin pada suatu fakta, katakan tidak yakin** dan tunjukkan cara memverifikasinya. Jangan menambalnya dengan asumsi.
7. **Jangan memasang paket tanpa izin.** Periksa dulu alat yang tersedia. Bila perlu memasang paket Python, usulkan *virtual environment* di folder kerja dan tunggu persetujuan.

### 1. Lokasi berkas

Semua path berada di bawah `THESIS=/media/bhrew/DATA1/Kuliah/Thesis`. Beberapa nama folder mengandung spasi, jadi selalu beri tanda kutip.

| Peran | Path | Catatan |
| --- | --- | --- |
| Panduan format | `"$THESIS/PanduanSkripsiFilkom-v3.0.pdf"` | Acuan utama struktur, tipe penelitian, format, dan gaya sitasi. |
| Template resmi | `"$THESIS/Template/Template-ProposalSkripsi-v3.0.docx"` | Verifikasi nama berkasnya. Acuan gaya (*style*) dan susunan halaman. |
| Naskah dasar | `"$THESIS/Laporan/Proposal/Proposal.docx"` | Proposal topik lama (analisis komparatif kuantisasi INT8 YOLO11n). Dipakai sebagai kerangka format, lalu isinya diganti untuk topik KD. |
| Pustaka | `"$THESIS/Paper"` | Satu-satunya sumber sitasi. Nama berkas diawali entri Daftar Referensi gaya Harvard FILKOM (semua penulis, tahun, judul huruf kalimat; skripsi ditambah "S1"). |
| Ejaan | `"$THESIS/EYD & KBBI"` | Rujukan ejaan dan kata baku. |
| Repo eksperimen | `"$THESIS/Kode program/"` | Cari repo `skripsi-knowlage-destilation` dengan `find "$THESIS/Kode program" -maxdepth 2 -name .git`. Sumber fakta tentang rancangan dan eksperimen. |
| Folder kerja | `"$THESIS/Laporan/Proposal/kerja_proposal_kd/"` | Buat baru. Berisi inventaris, catatan klaim, sumber gambar, skrip, dan cuplikan per TH. |
| Keluaran | `"$THESIS/Laporan/Proposal/Proposal_KD_OP3_v1.docx"` | Salinan `Proposal.docx` yang isinya diganti. |

Urutan prioritas bila terjadi pertentangan:

1. instruksi Bhre di sesi ini;
2. prompt ini;
3. Panduan Skripsi FILKOM v3.0 (untuk format dan struktur);
4. berkas repo (untuk fakta eksperimen);
5. template dan `Proposal.docx` (untuk gaya visual).

Bila template dan Panduan berbeda, laporkan perbedaannya dan tanyakan ke Bhre.

### 2. Konteks penelitian

Fakta di bagian ini berasal dari catatan Bhre per 22 Oktober 2026 dan dari repo pada server lab (*commit* `e0ebb91`). Salinan repo lokal bisa tertinggal. Verifikasi setiap fakta di repo lokal lebih dulu; bila berkasnya tidak ada atau nilainya berbeda, tandai `[PERLU VERIFIKASI REPO]` dan laporkan di TH-0. Jangan menjalankan `git pull` tanpa izin.

**2.1 Tipe penelitian dan rumusan masalah**

- Tipe: implementatif-pengembangan (Panduan Skripsi FILKOM v3.0, Lampiran A.5.1.1; verifikasi nomor dan isinya). Bentuk "Bagaimana perbandingan" milik topik lama dan tidak dipakai lagi.
- Rumusan masalah final, ditulis apa adanya:
  1. Bagaimana implementasi sistem deteksi objek berbasis ROS 2 yang menjalankan model YOLO11 skala t hasil *knowledge distillation* (KD) pada robot humanoid ROBOTIS OP3?
  2. Bagaimana tingkat akurasi, berdasarkan nilai *mean average precision* (mAP), model YOLO11 skala t hasil KD dibandingkan dengan model berarsitektur sama yang dilatih secara *supervised* dan dengan *teacher* YOLO11n?
  3. Bagaimana kinerja ketiga model tersebut jika ditinjau dari nilai *precision*, *recall*, dan *F1-score*?
  4. Berapa rata-rata latensi dan *frames per second* (FPS) yang dicapai model hasil KD dan *teacher* YOLO11n saat beroperasi secara *real-time* pada kondisi robot diam dan berjalan?
  5. Bagaimana tingkat efisiensi penggunaan CPU dan RAM model hasil KD dan *teacher* YOLO11n saat dijalankan secara penuh pada komputer *onboard* robot?
- Nomor 1 menjawab artefak (sistem deteksi ROS 2 di OP3 beserta alur pelatihan KD). Nomor 2 sampai 5 adalah pengujiannya.
- Nomor 4 dan 5 tidak menyertakan model *supervised* karena arsitekturnya identik dengan model hasil KD.

**2.2 Model dan metode KD**

- ***Teacher***: YOLO11n FP32 yang dibekukan, 2.590.425 parameter, SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`. Bobotnya berasal dari proyek Advance Vision. Telusuri asal pelatihannya di repo (`docs/DECISIONS.md`, `PROTOKOL_EKSPERIMEN_SKRIPSI.md`) dan tulis apa adanya.
- ***Student***: `models/yolo11_tiny_kd.yaml`, topologi YOLO11n skala t (kedalaman 0,50, lebar 0,125), 810.649 parameter, inisialisasi acak (`pretrained=False`). Arsitektur yang sama dipakai untuk semua *student*.
- **Varian pelatihan *student*:**
  - *supervised*: *loss* deteksi Ultralytics berlabel, tanpa distilasi;
  - KD murni (`pure_v4`): tanpa *loss* label; *loss* = distilasi fitur P3/P4/P5 (L2 berbobot skor *teacher* melalui proyektor) + Smooth L1 pada keluaran `boxes` + BCE bertemperatur pada `scores`, bobot 1 : 1 : 1, T = 2;
  - KD hibrida `hybrid_full`: *loss* deteksi berlabel + *loss* KD `pure_v4` (bobot 1,0; T = 2);
  - KD hibrida `hybrid_feature`: *loss* deteksi berlabel + `dis` × distilasi fitur bawaan Ultralytics.
- **"Model hasil KD"** adalah varian yang terpilih di VAL dengan aturan yang ditulis sebelum TEST dibuka. Menurut catatan per 22 Oktober 2026, varian terpilih adalah `hybrid_full`; verifikasi di `docs/DECISIONS.md`. Varian lain dilaporkan sebagai ablasi.
- **Resep identik untuk semua *student*:** 100 *epoch*, *batch* 16, AdamW `lr0` 0,001, `lrf` 0,01, *warmup* 3, *weight decay* 0,0005, `close_mosaic` 10, AMP mati, `patience` 30, `imgsz` 640, *seed* 42, 1337, dan 2025.
- **Batasan teknis:** semua model dijalankan sebagai berkas `.pt` dengan PyTorch FP32. Tanpa OpenVINO, ONNX untuk penerapan, INT8, PTQ, atau QAT.

**2.3 Data, lingkungan, dan pengujian**

- **Himpunan data:** Roboflow, *workspace* `humanoid-atom`, *project* `advance_vision_human`, tiga kelas (`ball`, `gawang`, `robot`). VAL berisi 1.213 citra. Ambil jumlah citra dan *instance* per kelas per *split* dari `AUDIT_DATASET_SKRIPSI.md` atau berkas audit lain di repo.
- **Pelatihan:** server lab dengan NVIDIA L40, Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130.
- **Robot:** ROBOTIS OP3 dengan komputer Intel NUC12WSHi5 (16 CPU logis), Python 3.12.3, PyTorch 2.4.1+cpu, Ultralytics 8.4.130, ROS 2 Jazzy, kamera Logitech C920 640×480 YUYV 30 FPS pada *topic* `/thesis/image_raw`. Tulis "komputer *onboard*", bukan "perangkat bawaan": e-Manual ROBOTIS mencantumkan NUC i3 sebagai komputer bawaan OP3, sedangkan unit ini memakai NUC12WSHi5.
- **Pengujian akurasi:** TEST, 3 *seed*, mAP50, mAP50-95, *precision*, *recall*, dan F1 (IoU 0,5; ambang *confidence* 0,25). Definisi F1 mengikuti keputusan D11 di repo; verifikasi statusnya.
- **Pengujian fungsional:** pengujian kotak hitam setiap kebutuhan fungsional sistem deteksi ROS 2.
- **Pengujian *runtime* (rencana):** model hasil KD dan *teacher* × kondisi diam (`servo_idle`) dan berjalan (`walking`) × 3 ulangan × 60 detik setelah *warm-up*. *Preview* mati, jumlah *thread* sesuai D6, ambang sesuai D4 (usulan *confidence* 0,25 dan NMS IoU 0,45), urutan model bergantian, jeda minimal 2 menit, suhu CPU dicatat. Metrik: latensi median dan p95, FPS efektif, CPU, dan RAM. D4, D6, dan definisi kondisi berjalan **belum dikunci**; cek `configs/analysis.yaml` dan tulis sebagai rencana.
- **Status penelitian:**
  - selesai: studi literatur, perancangan penelitian, pelatihan dan optimalisasi model, himpunan data dan prapemrosesan, *benchmark* server;
  - sedang berjalan: implementasi di robot, akuisisi data, dokumentasi;
  - belum dimulai: penyelesaian akhir.
  Status ini dipakai untuk menyusun jadwal.

**2.4 Pembeda dengan skripsi rekan satu tim**

Rekan mengerjakan implementasi QAT + OpenVINO. Pembimbing pernah menilai pembeda keduanya belum tegas, jadi naskah harus menegaskannya.

- QAT + OpenVINO mengubah representasi bobot (INT8) dan *runtime*.
- Penelitian ini tidak mengubah representasi maupun *runtime*: semua model tetap PyTorch FP32. Perbaikan dicari dari cara melatih *student* yang lebih kecil daripada *teacher*.

Skripsi rekan yang belum terbit tidak boleh disitasi kecuali Bhre memberikan berkasnya.

**2.5 Koreksi fakta pustaka yang sudah diketahui**

Periksa ulang semuanya pada PDF di folder Paper sebelum dipakai.

- **Pottier dan Lau (2025):** 7,98 sampai 8,01 FPS adalah *frame rate idle* tanpa objek terdeteksi. Dengan deteksi, YOLOv9-Tiny di CPU OP3 mencapai 5,92 sampai 6,22 FPS (statis) dan 4,41 sampai 6,68 FPS (dinamis) (Tabel 3 sampai 5). Konteksnya FIRA HuroCup dengan ROS 1 Kinetic, bukan RoboCup sepak bola.
- **Saltık et al. (2025):** mAP50 YOLO11n naik dari 0,838 menjadi 0,859 dengan CWD. Kenaikan ini setara 2,1 poin (sekitar 2,5% relatif), bukan 2,5 poin.
- **Arık dan Ağgül (2026):** klaim uji di Raspberry Pi 3B+ dan Jetson Nano belum terverifikasi. Versi pracetak tidak memuat pengukuran perangkat tepi. Pakai hanya yang tertulis di versi yang ada di folder Paper.
- **Dokumentasi YOLO11 Ultralytics:** angka CPU ONNX 56,1 ms (YOLO11n) dan 90,0 ms (YOLO11s) diukur pada perangkat tolok ukur Ultralytics, bukan OP3. Sitasi dokumentasi daring hanya boleh dipakai bila Bhre menyetujuinya (K9).

### 3. Aturan bahasa dan gaya

- Bahasa Indonesia ragam baku akademis, kalimat utuh, paragraf argumentatif: setiap paragraf punya satu gagasan pokok yang ditopang bukti bersitasi.
- **Dilarang memakai tanda pisah *em dash* (karakter U+2014).** Susun ulang kalimatnya, jangan sekadar mengganti tandanya. Untuk rentang angka, pakai "sampai", bukan *en dash*.
- Hindari pola kalimat khas AI:
  - pembuka klise seperti "Dalam era digital saat ini";
  - "Selain itu" beruntun;
  - kalimat yang mengulang pertanyaan;
  - penutup paragraf yang merangkum ulang tanpa isi baru.
- **Kata baku:** "algoritme" (bukan "algoritma"), "analisis" (bukan "analisa"). Jangan memakai "rancang bangun".
- **Istilah asing dicetak miring**, kecuali nama produk (YOLO11, ROS 2, PyTorch, Ultralytics, OpenVINO, Roboflow, ROBOTIS OP3, Intel NUC, Logitech C920). Buat `ISTILAH.md` di folder kerja: daftar istilah, padanannya bila ada, dan apakah dicetak miring. Pakai daftar itu secara konsisten.
- Singkatan diuraikan pada kemunculan pertama di setiap bab.
- Angka memakai koma desimal dan titik ribuan (0,7469; 1.213).
- **Sitasi gaya Harvard sesuai Panduan:** (Nama, tahun); "dan" untuk dua penulis; "et al." untuk tiga penulis atau lebih. Format pracetak dan sumber daring mengikuti Panduan; verifikasi contohnya di Panduan.
- **Kutipan langsung** hanya bila perlu, pendek, dengan nomor halaman. Selebihnya parafrasa.
- **Waktu penulisan:** proposal ditulis sebagai rencana penelitian. Keputusan rancangan yang sudah dikunci (pasangan model, resep, varian KD, aturan pemilihan) boleh disebut sebagai rancangan. Hasil eksperimen yang sudah ada **tidak** dimasukkan ke Bab 1 sampai 3, kecuali Bhre memutuskan lain di TH-1 (K1).

### 4. Aturan pustaka

- **Sitasi hanya dari berkas di folder Paper.** Folder ini mungkin juga berisi pustaka topik lama (kuantisasi, OpenVINO); pakai hanya yang relevan, misalnya untuk posisi penelitian terhadap kuantisasi.
- **Utamakan terbitan 2020 ke atas.** Bila dua sumber mendukung klaim yang sama, pilih yang lebih baru. Sumber sebelum 2020 boleh dipakai untuk karya fondasional (misalnya Hinton, Vinyals, dan Dean, 2015; Romero et al., 2015; Chen et al., 2017; Lin et al., 2014) atau bila tidak ada sumber yang lebih baru. Periksa apakah Panduan mengatur batas usia pustaka. Laporkan proporsi pustaka ≥ 2020 di setiap TH yang menambah sitasi.
- **Metadata Daftar Referensi:** ambil dari halaman pertama PDF dan nama berkas, lalu cocokkan keduanya. Pakai tahun terbit resmi bila ada versi prosiding atau jurnal. Bila DOI, volume, atau halaman tidak tertera dan tidak dapat diverifikasi, jangan diisi; beri penanda `[PERLU DICEK]` dan laporkan. Bila Anda punya akses web, verifikasi metadata boleh dilakukan lewat situs penerbit atau arXiv; catat sumber verifikasinya.
- **Klaim yang belum punya sumber:** tulis `[BUTUH SITASI: ...]` di naskah dan masukkan ke `DAFTAR_UNDUH.md` berisi judul dan pranala unduh (hanya pranala yang Anda verifikasi). Bhre yang akan mengunduh berkasnya.
- **Gambar dari pustaka:** utamakan digambar ulang. Bila tetap dikutip, cantumkan sumbernya sesuai format Panduan.

### 5. Penanganan berkas `.docx`

1. **Pemeriksaan alat:** `python3 -c "import docx"`, `pandoc --version`, `soffice --version`, `pdftotext -v`, `pdftoppm -v`, dan `dot -V`. Laporkan yang tidak ada.
2. **Salin** `Proposal.docx` ke `Proposal_KD_OP3_v1.docx`. Semua penyuntingan dilakukan pada salinan. Simpan cuplikan per TH di folder kerja (`Proposal_KD_OP3_TH2.docx`, dan seterusnya) agar mudah dikembalikan.
3. **Audit struktur sebelum menyunting:**
   - lihat isi dengan `pandoc -t markdown`;
   - daftar paragraf beserta nama *style* lewat python-docx;
   - buka `word/styles.xml`, `word/numbering.xml`, dan `word/document.xml` untuk mengetahui *style* judul bab dan subbab, penomoran, *field* daftar isi, *caption* (*field* `SEQ`), persamaan (OMML), *section break*, dan penomoran halaman romawi atau arab;
   - periksa apakah sitasi berupa teks biasa atau *field* pengelola referensi (`ADDIN` Mendeley atau Zotero).
   Bandingkan *style* `Proposal.docx` dengan template resmi. Bila berbeda, ikuti template dan laporkan.
4. **Cara menyunting:**
   - ganti isi dengan memakai *style* yang sudah ada di dokumen, bukan format manual;
   - istilah asing dicetak miring per *run*;
   - *caption* gambar dan tabel dibuat dengan menyalin XML paragraf *caption* yang sudah ada, agar *field* `SEQ` tetap berfungsi;
   - tabel memakai gaya tabel yang sudah ada;
   - persamaan dibuat sebagai OMML: tulis dalam LaTeX, ubah dengan `pandoc` menjadi `.docx` sementara, lalu salin elemen `m:oMath`-nya. Ikuti penomoran persamaan sesuai Panduan.
5. **Larangan:** jangan membangun ulang dokumen dari nol dengan `pandoc` atau pustaka lain, karena format template akan hilang. Isi topik lama yang tidak lagi relevan dihapus seluruhnya, termasuk tabel, gambar, dan entri referensinya.
6. **Pemeriksaan visual di setiap TH:**
   - ubah ke PDF dengan `soffice --headless --convert-to pdf`;
   - render beberapa halaman dengan `pdftoppm -r 70 -png`, lalu lihat gambarnya;
   - ingatkan Bhre bahwa daftar isi, daftar gambar, dan daftar tabel perlu diperbarui di Word (pilih semua, lalu F9).

### 6. Kerangka isi

Kerangka di bawah adalah usulan. Susunan subbab akhir **wajib** mengikuti Panduan (terutama ketentuan tipe implementatif-pengembangan) dan template, lalu disetujui di TH-1.

**Halaman awal.** Perbarui judul, tipe penelitian, dan identitas. Data yang tidak diketahui diisi `[ISI]`. Hapus bagian topik lama yang tidak berlaku.

**Bab 1 Pendahuluan**

- **Latar Belakang**, alur argumen:
  1. robot humanoid sepak bola perlu mendeteksi bola, gawang, dan robot lain;
  2. pada OP3 deteksi dijalankan di CPU komputer *onboard* dengan daya komputasi terbatas (Pottier dan Lau, 2025; pakai angka yang sudah dikoreksi);
  3. ukuran model menentukan kompromi akurasi dan kecepatan, sehingga model kecil dibutuhkan agar deteksi berjalan *real-time*, tetapi akurasinya lebih rendah;
  4. KD melatih *student* kecil agar meniru *teacher* yang lebih teliti tanpa mengubah biaya inferensi *student* (Hinton, Vinyals, dan Dean, 2015; Gou et al., 2021; survei KD detektor terbaru bila ada di folder Paper);
  5. KD pada keluarga YOLO dan pada robot sudah dilaporkan (misalnya Saltık et al., 2025; Billy, 2019);
  6. celah: dalam penelusuran penulis, belum ditemukan penelitian KD detektor objek yang diterapkan sebagai sistem ROS 2 pada komputer *onboard* robot humanoid dan diuji saat robot diam dan berjalan. Tulis sebagai batas penelusuran, bukan klaim mutlak;
  7. pembeda dengan pendekatan kuantisasi;
  8. pernyataan apa yang dilakukan penelitian ini.
- **Rumusan Masalah:** lima nomor di 2.1, apa adanya.
- **Tujuan:** satu tujuan untuk setiap rumusan masalah, berurutan.
- **Manfaat:** praktis (bagi tim robot sepak bola humanoid; nama tim `[ISI]`) dan akademis.
- **Batasan Masalah:**
  - tiga kelas objek dari himpunan data Roboflow;
  - *teacher* YOLO11n dan *student* YOLO11 skala t;
  - berkas `.pt` dengan PyTorch FP32, tanpa OpenVINO, ONNX, INT8, PTQ, atau QAT;
  - perangkat keras dan perangkat lunak robot sesuai 2.3;
  - dua kondisi robot: diam dan berjalan;
  - masukan 640;
  - pelatihan di server lab.
- **Rumusan Hipotesis:** hapus subbab ini bila Panduan tidak mewajibkannya untuk tipe implementatif (K10).
- **Sistematika Pembahasan:** sesuaikan dengan susunan bab yang dipakai.

**Bab 2 Landasan Kepustakaan**

- **Kajian Pustaka atau Penelitian Terdahulu:**
  - tabel perbandingan, dengan kolom penelitian, *teacher* → *student*, metode KD, perangkat uji, temuan pokok, dan perbedaan dengan penelitian ini;
  - kandidatnya: Billy (2019), Saltık et al. (2025), Arık dan Ağgül (2026), Sharma et al. (2026), Pottier dan Lau (2025), Jati, Ilyasa, dan Dominic (2024), Barry et al. (2019), dan yang lain bila ada di folder Paper;
  - tutup dengan paragraf **posisi penelitian**.
- **Dasar Teori**, usulan urutan:
  1. robot humanoid ROBOTIS OP3 dan konteks robot sepak bola;
  2. deteksi objek dan YOLO11, termasuk *head* Detect, keluaran kotak berbasis *Distribution Focal Loss* (Li et al., 2020), dan skala model;
  3. *knowledge distillation*: definisi, target lunak dan temperatur, serta taksonomi berbasis respons, fitur, dan relasi;
  4. KD untuk detektor objek:
     - distilasi fitur dengan proyektor (Romero et al., 2015; Chen et al., 2017);
     - distilasi respons untuk klasifikasi sigmoid (Yang et al., 2023);
     - distilasi lokalisasi (Zheng et al., 2022);
     - KD murni tanpa label dan KD hibrida yang menggabungkan *loss* label dengan distilasi;
  5. ROS 2: *node*, *topic*, dan QoS;
  6. metrik akurasi: IoU, *precision*, *recall*, F1, AP, mAP50, dan mAP50-95 (Lin et al., 2014; Padilla et al., 2021);
  7. metrik kinerja: latensi per tahap, FPS efektif, penggunaan CPU, dan RAM.
- **Persamaan:** rumus *loss* KD ditulis sebagai persamaan bernomor, dengan notasi yang dijelaskan.

**Bab 3 Metodologi** (susunan mengikuti Panduan untuk tipe implementatif-pengembangan)

- tipe penelitian dan alasannya;
- diagram alir penelitian: studi literatur, himpunan data, pelatihan *supervised*, KD murni, dan KD hibrida (3 *seed*), pemilihan varian di VAL, evaluasi TEST, integrasi *node* ROS 2 di OP3, pengujian, serta kesimpulan;
- analisis kebutuhan: minimal empat kebutuhan fungsional dan satu nonfungsional, atau sesuai angka di Panduan;
- perancangan:
  - arsitektur sistem keseluruhan;
  - rancangan alur pelatihan dan *loss* setiap varian;
  - rancangan *node* ROS 2: kamera `/thesis/image_raw` → *node* detektor → *topic* hasil deteksi dan log;
- implementasi: lingkungan pelatihan dan robot sesuai 2.3, serta resep pelatihan;
- pengujian:
  - fungsional (kotak hitam per kebutuhan);
  - akurasi sesuai 2.3;
  - *runtime* sesuai 2.3, termasuk cara menghitung setiap metrik;
- analisis data dan penarikan kesimpulan;
- jadwal penelitian dalam bentuk tabel, disusun dari status di 2.3; target sidang `[ISI]`.

Usulan awal kebutuhan fungsional, untuk difinalkan bersama Bhre:

- menerima citra dari *topic* kamera;
- memuat model `.pt` yang terdaftar dan memverifikasi *hash*-nya;
- mendeteksi `ball`, `gawang`, dan `robot`, lalu menerbitkan kelas, *confidence*, dan kotak pembatas;
- mencatat waktu setiap tahap, FPS, CPU, dan RAM ke log;
- melatih *student* dalam mode *supervised*, KD murni, dan KD hibrida dari berkas konfigurasi.

Usulan kebutuhan nonfungsional: kinerja (latensi dan FPS) serta efisiensi sumber daya (CPU dan RAM). Nilai targetnya diputuskan Bhre (K4).

**Gambar.** Buat sendiri dengan Graphviz atau Matplotlib, resolusi 300 dpi. Simpan berkas sumbernya (`.dot` atau `.py`) di folder kerja agar dapat disunting. Gambar minimum: diagram alir penelitian, arsitektur sistem, alur pelatihan KD, dan graf *node* ROS 2.

**Daftar Referensi.** Hanya karya yang disitasi, diurutkan dan diformat sesuai Panduan.

### 7. Alur kerja dan titik henti

```
TH-0  Persiapan, audit format, inventaris pustaka, verifikasi fakta repo
TH-1  Kerangka, peta sitasi, daftar istilah, keputusan Bhre
TH-2  Bab 1
TH-3  Bab 2
TH-4  Bab 3 beserta gambar
TH-5  Daftar Referensi, halaman awal, pemeriksaan akhir
```

**TH-0: persiapan**

1. Pemeriksaan alat, salinan dokumen, dan audit struktur `.docx` (bagian 5).
2. Baca Panduan, lalu tulis `RINGKASAN_PANDUAN.md` yang memuat nomor halaman untuk:
   - struktur proposal;
   - ketentuan tipe implementatif-pengembangan;
   - format halaman, judul bab, gambar, tabel, dan persamaan;
   - gaya sitasi dan Daftar Referensi beserta contohnya;
   - aturan usia atau jumlah pustaka bila ada.
3. Petakan isi `Proposal.docx`: subbab mana yang dipertahankan formatnya, mana yang isinya diganti, dan mana yang dihapus. Kalimat lama hanya boleh dipakai ulang bila tetap benar untuk topik KD (misalnya deskripsi OP3), dan sitasinya dicek ulang.
4. Inventaris folder Paper di `INVENTARIS_PAPER.csv`, dengan kolom:
   - nama berkas;
   - penulis;
   - tahun;
   - judul;
   - jenis (jurnal, prosiding, pracetak, skripsi, dokumentasi);
   - status ≥ 2020;
   - topik (KD dasar, KD detektor, YOLO, robot sepak bola, ROS 2, metrik, statistik, kuantisasi, lain-lain);
   - catatan bila metadata nama berkas dan PDF tidak cocok.
   Ekstrak teks setiap PDF dengan `pdftotext -layout` ke folder kerja sebagai *cache* pencarian.
5. Verifikasi fakta bagian 2 terhadap repo lokal dalam tabel berisi fakta, nilai di prompt, nilai di repo, path, dan status.

Laporkan semuanya di TH-0, lalu berhenti.

**TH-1: kerangka dan keputusan**

1. Kerangka final Bab 1 sampai Bab 3, sampai tingkat subbab, dengan perkiraan panjang setiap subbab.
2. `PETA_SITASI.md`: setiap klaim yang direncanakan dipetakan ke berkas Paper dan halamannya, atau ke `[BUTUH SITASI]`.
3. `DAFTAR_UNDUH.md` untuk pustaka yang belum ada.
4. `ISTILAH.md`.
5. Daftar keputusan yang harus dijawab Bhre:
   - **K1:** proposal murni rencana atau memuat hasil yang sudah ada (bawaan: murni rencana);
   - **K2:** penulisan istilah KD (bawaan: *knowledge distillation* dicetak miring dengan singkatan KD; naskah lama memakai "penyulingan pengetahuan");
   - **K3:** cara menyebut asal *teacher* dari proyek Advance Vision;
   - **K4:** nilai target kebutuhan nonfungsional;
   - **K5:** definisi kondisi berjalan (masih menunggu pembimbing);
   - **K6:** jadwal dan target sidang;
   - **K7:** data halaman judul (nama, NIM, pembimbing, tahun);
   - **K8:** apakah evaluasi pada citra kamera OP3 disebut sebagai pengujian pendukung;
   - **K9:** apakah dokumentasi daring (Ultralytics, ROBOTIS e-Manual, dokumentasi ROS 2) boleh disitasi;
   - **K10:** subbab Rumusan Hipotesis dihapus atau dipertahankan;
   - **K11:** apakah rumusan masalah sudah dikonfirmasi pembimbing bersama judul.

**TH-2 sampai TH-4: penulisan per bab**

- Tulis langsung ke `Proposal_KD_OP3_v1.docx`.
- Perbarui `KLAIM_SUMBER.md` untuk setiap klaim faktual, dengan kolom bab/subbab, kalimat ringkas, berkas sumber, halaman atau tabel, dan untuk angka eksperimen path repo.
- Simpan cuplikan `.docx` per TH, lalu jalankan pemeriksaan visual.
- Laporkan:
  - ringkasan isi bab;
  - jumlah kata per subbab;
  - daftar `[BUTUH SITASI]` dan `[ISI]`;
  - proporsi pustaka ≥ 2020;
  - penyimpangan dari kerangka.

**TH-5: penyelesaian**

1. Susun Daftar Referensi dari sitasi yang benar-benar dipakai.
2. Perbarui halaman awal.
3. Jalankan skrip pemeriksaan otomatis (simpan di folder kerja) atas teks seluruh dokumen, termasuk tabel dan *caption*:
   - tidak ada karakter *em dash* (U+2014); laporkan juga *en dash* (U+2013);
   - tidak ada "algoritma", "analisa", atau "rancang bangun";
   - frekuensi "Selain itu" dan letaknya;
   - setiap sitasi dalam teks punya entri di Daftar Referensi, dan sebaliknya;
   - kemunculan istilah di `ISTILAH.md` yang belum dicetak miring;
   - angka berdesimal titik di dalam kalimat;
   - sisa penanda `[BUTUH SITASI]`, `[ISI]`, `[PERLU DICEK]`, dan `[PERLU VERIFIKASI REPO]`.
4. Ubah ke PDF dan periksa tata letak.

Laporkan semuanya, lalu berhenti.

### 8. Format laporan di setiap titik henti

1. Yang dikerjakan, ringkas.
2. Berkas yang dibuat atau diubah beserta path-nya.
3. Perintah yang dijalankan dan hasilnya.
4. Penyimpangan dari prompt ini beserta alasannya.
5. Keputusan atau informasi yang dibutuhkan dari Bhre.

### 9. Mulai dari sini

Kerjakan TH-0, lalu berhenti dan tunggu persetujuan Bhre.
