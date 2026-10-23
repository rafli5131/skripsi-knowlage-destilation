# Prompt penyusunan proposal skripsi Bab 1 sampai 3 sesuai template dan Panduan FILKOM

> Versi 23 Oktober 2026. Menggantikan `PROMPT_PROPOSAL_KD_OP3_CLAUDE_CODE.md` (22 Oktober, sudah dijalankan sampai TH-0), `PROMPT_PROPOSAL_BAB_I-III_KD_OP3_V2.md`, dan versi awalnya. Perubahan utama: (1) melanjutkan hasil TH-0 tanpa mengulanginya; (2) temuan TH-0 tentang Panduan diselesaikan dengan **mengikuti Panduan**; (3) struktur skripsi mengikuti contoh tipe implementatif-pengembangan Panduan (tujuh bab); (4) konteks penelitian diperbarui: KD Hybrid sebagai model hasil KD dan uji live OP3 dengan kondisi setara, termasuk *teacher*, sebagai pengujian akhir. Revisi 23 Oktober 2026 sore: inventaris pustaka diperbarui untuk 19 berkas baru di folder Paper, K9 ditetapkan, rujukan pada kerangka disesuaikan dengan isi folder Paper, keputusan K14 ditambahkan, serta aturan pemeriksaan ejaan dan kata baku terhadap folder `EYD & KBBI/` ditambahkan, dengan edisi acuan berkas di folder itu (K15).

Jalankan prompt ini di Claude Code pada komputer Bhre. Salin seluruh bagian **Prompt**.

---

## Prompt

### 0. Peran dan prinsip kerja

Anda adalah asisten penulisan akademik untuk Bhre, mahasiswa Teknik Komputer FILKOM Universitas Brawijaya. Tugas Anda menyusun **proposal skripsi Bab 1, Bab 2, Bab 3, Daftar Referensi, dan bagian awalnya** dalam berkas `.docx` yang mengikuti `Template-ProposalSkripsi-v3.0.docx` dan `PanduanSkripsiFilkom-v3.0.pdf`. Judul yang sudah disetujui pembimbing: **"Implementasi *Knowledge Distillation* untuk Deteksi Objek pada Robot Humanoid ROBOTIS OP3"**. Naskah ini akan dipertanggungjawabkan Bhre di seminar proposal.

1. **Tidak ada klaim tanpa sumber.** Setiap klaim faktual bersitasi ke berkas di folder Paper atau skripsi kating, atau diberi penanda `[BUTUH SITASI: <apa yang dicari>]`. Dilarang mengarang penulis, tahun, judul, volume, halaman, atau DOI.
2. **Angka dicek di sumber aslinya.** Angka pustaka hanya dikutip setelah ditemukan di PDF, dengan nomor halaman atau tabel dicatat. Fakta eksperimen hanya diambil dari repo, dengan path dicatat.
3. **Berkas asli tidak boleh diubah.** `Proposal.docx`, kedua template, Panduan, isi folder Paper, dan skripsi kating hanya dibaca. Semua keluaran berupa berkas baru.
4. **Berhenti di setiap titik henti (TH)** dan tunggu persetujuan tertulis Bhre.
5. **Tidak ada jalan pintas diam-diam.** Bila alat gagal atau format rusak, berhenti dan laporkan. Jangan membangun ulang dokumen dari nol dengan format lain.
6. **Bila tidak yakin pada suatu fakta, katakan tidak yakin** dan jelaskan cara memverifikasinya.
7. **Jangan memasang paket atau mengakses web tanpa izin Bhre.**

### 1. Lokasi berkas

`THESIS` adalah `E:\Kuliah\Thesis` di Windows atau `/media/bhrew/DATA1/Kuliah/Thesis` di Linux. Gunakan yang sesuai dengan sistem tempat Anda berjalan dan selalu beri tanda kutip pada path yang mengandung spasi.

| Peran | Path di bawah `THESIS` | Catatan |
|---|---|---|
| Panduan | `PanduanSkripsiFilkom-v3.0.pdf` | Acuan utama struktur, isi, format, bahasa, dan sitasi |
| Template proposal | `Template/Template-ProposalSkripsi-v3.0.docx` | Acuan *style*, sampul, dan susunan halaman proposal |
| Template skripsi | `Template/Template-Skripsi-v3.0.docx` | Acuan agar Bab 1 sampai 3 dapat dibawa ke skripsi akhir tanpa ubah format |
| **Berkas pengerjaan** | `Laporan/Proposal/Proposal_KD_OP3_v1.docx` | Satu-satunya naskah yang disunting (lihat aturan di bawah tabel) |
| Hasil TH-0 | `Laporan/Proposal/kerja_proposal_kd/` | `LAPORAN_TH0.md`, `RINGKASAN_PANDUAN.md`, `INVENTARIS_PAPER.csv`, `VERIFIKASI_FAKTA.md`, `audit/`, `pdf_text/`, `skrip/` |
| Pustaka | `Paper/` dan `Skripsi kating/Skripsi - Ivan Rafli A.docx` | Satu-satunya sumber sitasi. Skripsi kating dicatat sebagai Adipratama (2026) di inventaris |
| Ejaan | `EYD & KBBI/` | Rujukan ejaan dan kata baku |
| Repo eksperimen | `Kode program/skripsi-knowlage-destilation/` | Sumber fakta rancangan dan eksperimen |
| Praproposal | `Laporan/Praproposal/` | **Tidak dipakai** sebagai sumber, sesuai instruksi Bhre |

**Berkas pengerjaan proposal:**

```text
Windows : E:\Kuliah\Thesis\Laporan\Proposal\Proposal_KD_OP3_v1.docx
Linux   : /media/bhrew/DATA1/Kuliah/Thesis/Laporan/Proposal/Proposal_KD_OP3_v1.docx
```

- Seluruh isi sampul, bagian awal, Bab 1, Bab 2, Bab 3, dan Daftar Referensi ditulis langsung ke berkas ini. Berkas ini adalah salinan `Proposal.docx` yang dibuat di TH-0, dengan *style* yang praktis identik dengan template proposal.
- Jangan membuat naskah baru dengan nama lain (misalnya `_v2`) kecuali Bhre memintanya. Cuplikan per TH di `kerja_proposal_kd/cuplikan/` hanya cadangan dan tidak disunting.
- Sebelum setiap sesi penyuntingan, pastikan berkas tidak sedang dibuka di Word. Bila ada berkas kunci `~$oposal_KD_OP3_v1.docx` di folder yang sama, berhenti dan minta Bhre menutup Word.
- Bila Bhre sudah menyunting berkas ini sendiri sejak TH terakhir, baca perubahan tersebut dan pertahankan; jangan menimpanya dengan cuplikan lama.

Urutan prioritas bila terjadi pertentangan: instruksi Bhre di sesi ini, prompt ini, Panduan v3.0, template proposal, berkas repo, naskah lama. Bila Panduan dan template berbeda, ikuti Panduan dan laporkan.

### 2. Sinkronisasi dengan hasil TH-0

TH-0 selesai pada 22 Oktober 2026 dengan repo di commit `a5b59d5`. Jangan mengulang pekerjaan TH-0. Gunakan berkas di folder kerja dan lakukan hanya hal berikut:

1. Cek `sha256sum -c audit/SHA256_BERKAS_ASLI_TH0.txt` untuk memastikan berkas asli tidak berubah.
2. Bandingkan berkas pengerjaan dengan cuplikan `cuplikan/Proposal_KD_OP3_TH0.docx`. Bila berkas pengerjaan sudah berubah sejak TH-0, laporkan perbedaannya dan tunggu keputusan Bhre sebelum menyunting.
3. Catat HEAD repo saat ini (minimal `dc89666`), lalu periksa perubahan sejak `a5b59d5` yang memengaruhi fakta bagian 3: `docs/DECISIONS.md`, `configs/analysis.yaml`, `configs/model_registry.yaml`, `analisis_performa/tabel/`, `dokumentasi/`, `memory/`, dan `prompt/`. Tambahkan bagian "Pembaruan 23 Oktober" di `VERIFIKASI_FAKTA.md`. Jangan menjalankan `git pull` tanpa izin.
4. Perbarui `INVENTARIS_PAPER.csv` tanpa mengulang TH-0. Inventaris TH-0 memuat 46 baris (45 PDF dan skripsi kating), sedangkan folder Paper per 23 Oktober 2026 berisi 64 berkas. Tambahkan baris untuk 19 berkas baru yang tercantum di bagian 7, isi kolom `jenis` untuk cetakan halaman web dengan `dokumentasi`, lalu buat *cache* `pdftotext -layout` di `pdf_text/` hanya untuk berkas baru. Bandingkan isi folder dengan inventaris dan laporkan selisihnya di kedua arah.

### 3. Keputusan yang sudah ditetapkan

Bhre meminta naskah disesuaikan dengan template dan Panduan. Karena itu temuan TH-0 berikut diselesaikan sebagai berikut:

| Kode TH-0 | Keputusan | Dasar |
|---|---|---|
| B | Sitasi dalam teks: dua atau tiga penulis ditulis semua; empat penulis atau lebih memakai "Nama, et al. (tahun)" dengan koma. Daftar Referensi menulis semua penulis | Panduan hlm 55 sampai 56 |
| C | Bab 3 hanya menjelaskan **cara** meneliti dan hasil yang diharapkan dari setiap tahap. Daftar kebutuhan yang sudah diidentifikasi dan hasil perancangan (arsitektur rinci, *node* ROS 2, *flowchart* sistem) tidak dimuat di Bab 3; tempatnya di Bab 4 dan Bab 5 skripsi | Panduan hlm 41 dan 44 sampai 45; Bab 3 skripsi kating Adipratama (2026) |
| D | Bidang RPC, tipe implementatif-pengembangan, Lampiran A.5.1.1 | Konfirmasi Bhre 22 Oktober; Panduan hlm 121 sampai 122 |
| E | Arik dan Ağgül (2026) dipakai dalam versi terbit di folder Paper (PDF terbit mencetak "Arik", bukan "Arık" seperti versi pracetak); angka Raspberry Pi 3B+ dan Jetson Nano disebut sebagai milik model *pseudo-labeling*, bukan model KD | `VERIFIKASI_FAKTA.md` butir 35 |
| Struktur skripsi | Sistematika Pembahasan memakai tujuh bab: Bab 1 Pendahuluan, Bab 2 Landasan Kepustakaan, Bab 3 Metodologi Penelitian, Bab 4 Rekayasa Kebutuhan, Bab 5 Perancangan dan Implementasi, Bab 6 Pengujian dan Evaluasi, Bab 7 Penutup. Tandai sebagai menunggu konfirmasi pembimbing (K12) | Panduan hlm 44 sampai 45, subbab 3.4.4.4 |
| K9 | Dokumentasi daring boleh disitasi. Bukti aksesnya berupa cetakan PDF halaman web di folder Paper yang dicetak 23 Oktober 2026 (tanggal cetak tercantum di kepala halaman). Format mengikuti Panduan butir 18 untuk situs web dan butir 17 untuk program komputer; halaman tanpa tanggal memakai "n.d." (butir 23); beberapa karya organisasi yang sama dengan tahun sama dibedakan dengan huruf kecil (butir 5) | Keputusan Bhre 23 Oktober 2026; Panduan hlm 57 dan 64 sampai 67 |
| K15 | Ejaan dan kata baku mengacu pada berkas di folder `EYD & KBBI/`: `EYD_permen_46_2009.pdf` dan `KamusIndonesia-KBBI-edisi4-2008.pdf`. Edisi lain tidak dipakai | Keputusan Bhre 23 Oktober 2026 |

Keputusan TH-0 yang masih terbuka diajukan lagi di TH-1: A (*pandoc* untuk persamaan OMML), F (nama model komputer OP3), G dan H (akses web untuk verifikasi metadata, kini terutama untuk butir `[PERLU DICEK]` di bagian 7).

### 4. Ketentuan Panduan dan template yang wajib dipenuhi

Gunakan `RINGKASAN_PANDUAN.md` sebagai acuan cepat dan cek ulang ke PDF bila ragu. Pokoknya:

- **Kerangka proposal** (hlm 70 sampai 71): sampul, daftar isi, daftar tabel, daftar gambar, daftar lampiran, daftar istilah bila perlu; Bab 1 sampai Bab 3; Daftar Referensi; lampiran.
- **Sampul proposal** (hlm 29 dan 71): jenis laporan "PROPOSAL SKRIPSI", tanpa kalimat "Diajukan untuk memenuhi…", tahun pengajuan proposal, nama institusi berurutan sesuai Panduan. Isi data yang belum pasti dengan `[ISI]`.
- **Subbab Bab 1** sesuai template: Latar Belakang, Rumusan Masalah, Tujuan, Manfaat, Batasan Masalah, Sistematika Pembahasan. Rumusan hipotesis bersifat opsional (hlm 37).
- **Bab 3 proposal wajib diakhiri subbab Jadwal Penelitian** dalam tabel atau diagram (hlm 71), dengan rentang maksimal satu semester (hlm 9 sampai 11).
- **Kelayakan proposal** (hlm 9 sampai 11): penelitian terdahulu menunjukkan perbedaan atau kontribusi; metodologi memuat tahapan, metode setiap langkah, dan hasil setiap langkah.
- **Kecukupan RPC implementatif-pengembangan** (hlm 121 sampai 122): keunikan berupa arsitektur sistem, metode, atau data yang berbeda; implementasi metode ke *embedded system* dengan lebih dari satu variabel yang memengaruhi objek; minimal empat kebutuhan fungsional dan satu kebutuhan nonfungsional yang dianalisis lalu diuji sistematis; pemodelan perangkat keras dan perangkat lunak; skenario pengujian fungsional. Bab 3 proposal harus menjelaskan bagaimana setiap ketentuan ini akan dipenuhi, tanpa memuat daftar kebutuhan atau hasil rancangannya.
- **Format** (hlm 47 sampai 51): A4, margin kiri 4 cm dan lainnya 3 cm, Calibri sesuai *style* template, kepala bab "BAB 1 PENDAHULUAN", maksimal empat level subbab, nomor tabel di atas tabel, nomor gambar di bawah gambar, gambar dari sumber lain diberi "Sumber: …", persamaan bernomor per bab dengan format contoh template "(2.1)".
- **Bahasa** (hlm 48 dan 69 sampai 70): istilah asing miring kecuali nama produk; "Gambar 2.1" dan "Tabel 2.1" berhuruf kapital; tidak merujuk "di atas" atau "di bawah".
- **Sitasi Harvard FILKOM** (hlm 46 dan 55 sampai 69): urutan kronologis untuk beberapa karya sekaligus; nomor halaman untuk kutipan langsung; format jurnal, prosiding, skripsi, dan sumber daring sesuai contoh Panduan. Pracetak tidak diatur Panduan; usulkan satu format di TH-1 dan pakai konsisten.

### 5. Konteks penelitian (fakta per 23 Oktober 2026)

Verifikasi setiap butir terhadap repo. Bila berbeda, tandai `[PERLU VERIFIKASI REPO]` dan laporkan.

**5.1 Rumusan masalah** (ditulis apa adanya; `docs/KONFIRMASI_RUMUSAN_MASALAH_2026-10-22.md` mencatat Bhre melaporkan pembimbing menyetujuinya, tanpa tanggal):

1. Bagaimana implementasi sistem deteksi objek berbasis ROS 2 yang menjalankan model YOLO11 skala t hasil *knowledge distillation* (KD) pada robot humanoid ROBOTIS OP3?
2. Bagaimana tingkat akurasi, berdasarkan nilai *mean average precision* (mAP), model YOLO11 skala t hasil KD dibandingkan dengan model berarsitektur sama yang dilatih secara *supervised* dan dengan *teacher* YOLO11n?
3. Bagaimana kinerja ketiga model tersebut jika ditinjau dari nilai *precision*, *recall*, dan *F1-score*?
4. Berapa rata-rata latensi dan *frames per second* (FPS) yang dicapai model hasil KD dan *teacher* YOLO11n saat beroperasi secara *real-time* pada kondisi robot diam dan berjalan?
5. Bagaimana tingkat efisiensi penggunaan CPU dan RAM model hasil KD dan *teacher* YOLO11n saat dijalankan secara penuh pada komputer *onboard* robot?

Nomor 1 dijawab oleh tahap analisis kebutuhan, perancangan, implementasi, dan pengujian fungsional (Bab 4 sampai Bab 6 skripsi). Nomor 2 sampai 5 dijawab di Bab 6.

**5.2 Model dan metode KD**

- *Teacher*: YOLO11n FP32 beku, 2.590.425 parameter, SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`, berasal dari proyek Advance Vision (catatan asal di `VERIFIKASI_FAKTA.md` butir 4; cara menyebutnya diputuskan di K3).
- *Student*: `models/yolo11_tiny_kd.yaml`, YOLO11 skala t (kedalaman 0,50; lebar 0,125), 810.649 parameter, inisialisasi acak. Bukan YOLO11n standar.
- Varian pelatihan *student* dengan resep identik (100 *epoch*, *batch* 16, AdamW `lr0` 0,001, `lrf` 0,01, *warmup* 3, *weight decay* 0,0005, `close_mosaic` 10, AMP mati, `patience` 30, `imgsz` 640, *seed* 42, 1337, 2025): *supervised*; KD murni `pure_v4` (tanpa *loss* label; distilasi fitur P3/P4/P5, Smooth L1 pada `boxes`, BCE bertemperatur pada `scores`, bobot 1 : 1 : 1, T = 2); KD hibrida `hybrid_full` (*loss* label ditambah *loss* `pure_v4`); KD hibrida `hybrid_feature` (*loss* label ditambah `dis` × distilasi fitur bawaan Ultralytics).
- "Model hasil KD" adalah `hybrid_full`, dipilih pada VAL sebelum TEST dibuka; kandidat perangkat seed 1337. Status konfirmasi pembimbing atas varian ini dicek di `configs/analysis.yaml` (D2) dan `docs/DECISIONS.md`. Perbaikan objektif KD sedang direncanakan (`prompt/PROMPT_PERBAIKAN_KD_JALUR_TENGAH.md`): bila varian baru lolos aturan seleksi di VAL, model hasil KD mengikuti keputusan terbaru di `docs/DECISIONS.md`. Karena itu Bab 3 sebaiknya menulis aturan pemilihan varian di VAL, bukan mengunci nama varian, dan menyebut ablasi *teacher* YOLO11s sebagai rencana pengujian tambahan di VAL.
- Semua model dijalankan sebagai `.pt` PyTorch FP32. Tanpa OpenVINO, ONNX untuk penerapan, INT8, PTQ, atau QAT.

**5.3 Data dan lingkungan**

- Himpunan data Roboflow `humanoid-atom/advance_vision_human` versi v1, tiga kelas `ball`, `gawang`, `robot`. TRAIN 4.600 citra (6.143 objek), VAL 1.213 (1.525), TEST 592 (734). Ada nama sumber bersama antar-*split*, sehingga TEST tidak boleh diklaim mengukur adegan baru (`AUDIT_DATASET_SKRIPSI.md`).
- Pelatihan di server lab NVIDIA L40, Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130.
- Robot ROBOTIS OP3: CPU Intel Core i5-1240P, 16 CPU logis, Ubuntu 24.04.5, Python 3.12.3, PyTorch 2.4.1+cpu, Ultralytics 8.4.130, ROS 2 Jazzy, kamera Logitech C920 640×480 pada *topic* `/thesis/image_raw`. Nama model NUC belum terverifikasi (keputusan F). e-Manual ROBOTIS (n.d.) mencantumkan Intel NUC i3 *dual core* dan kamera Logitech C920 untuk kedua versi OP3, sehingga unit penelitian ini harus disebut terpisah dari spesifikasi pabrikan. Bhre pernah menyebut unitnya NUC12WSHi5; tetap tunggu keluaran `product_name` sebelum menuliskannya. Skripsi Adipratama (2026) mencatat OP3 memakai NUC7i3BNK; jelaskan perbedaan unit ini hanya setelah Bhre memberikan keluaran `cat /sys/class/dmi/id/product_name` dari OP3. Tulis "komputer *onboard*", bukan "perangkat bawaan".

**5.4 Rencana pengujian** (ditulis di Bab 3 sebagai metode)

- **Fungsional**: kotak hitam untuk setiap kebutuhan fungsional yang dihasilkan tahap analisis kebutuhan.
- **Akurasi pada himpunan data**: TEST, tiga *seed*, mAP50, mAP50-95, *precision*, *recall*, F1 (IoU 0,5; *confidence* 0,25). Definisi F1 mengikuti D11 di `configs/analysis.yaml`; tulis statusnya.
- **Akurasi pada citra kamera OP3**: evaluasi *offline* pada *frame* kamera OP3 berlabel hasil tinjauan Bhre, sebagai pemeriksaan domain robot. Status sebagai pengujian utama atau pendukung diputuskan di K8.
- **Runtime live** sesuai `prompt/PROMPT_UJI_ULANG_LIVE_SETARA_OP3_DENGAN_TEACHER.md`: model hasil KD dan *teacher* sebagai pembanding utama; *supervised* seed 1337 dan KD murni seed 42 sebagai pembanding pelengkap (K13). Dua kondisi: diam dengan seluruh servo menyala, dan berjalan dengan *gait* standar; servo kepala ID 19/20 menyala tetapi tidak menerima perintah gerak selama pengujian agar arah kamera tetap. *Preview* melalui SSH -X menyala, `op3_manager` aktif, CPU FP32, masukan 640, *confidence* 0,25, NMS IoU 0,45, BoT-SORT, empat *thread* intra-op dan dua inter-op, *warm-up* 30 *frame*, jendela ukur 60 detik, tiga ulangan dengan urutan model digilir, jeda minimal dua menit. Metrik: rata-rata, median, dan P95 latensi; FPS efektif dari cap waktu kamera; CPU proses; RSS.
- Bab 3 menyebut status keputusan protokol yang belum dikunci di `configs/analysis.yaml` (misalnya D4, D6, D7) sebagai rencana, bukan sebagai keputusan final.

**5.5 Status pekerjaan** (untuk jadwal): studi literatur, perancangan, pelatihan tiga varian dan tiga *seed*, evaluasi VAL dan TEST, serta uji pendahuluan di OP3 sudah selesai. Uji live akhir dengan kondisi setara dan *teacher*, evaluasi *offline* empat model, serta penulisan skripsi belum selesai. Proposal tetap ditulis sebagai rencana penelitian sesuai fungsinya; cara menyikapi pekerjaan yang sudah berjalan diputuskan di K1.

**5.6 Pembeda dengan skripsi rekan satu tim**

Rekan mengerjakan QAT dan OpenVINO, yang mengubah representasi bobot (INT8) dan *runtime*. Penelitian ini tidak mengubah keduanya; perbaikan dicari dari cara melatih *student* yang lebih kecil daripada *teacher*. Skripsi rekan yang belum terbit tidak disitasi kecuali Bhre memberikan berkasnya.

**5.7 Koreksi pustaka yang sudah terverifikasi di TH-0** (`VERIFIKASI_FAKTA.md` bagian C)

- Lau dan Pottier (2026), *Biomimetics*, dipakai sebagai sitasi utama menggantikan pracetak Pottier dan Lau (2025). Keduanya memakai OP3, YOLOv9, dan ROS Kinetic dengan tabel FPS *idle* yang identik, tetapi artikel 2026 tidak menyebut pracetaknya; catat hubungan ini di `VERIFIKASI_FAKTA.md`. Koreksi TH-0 berikut berasal dari pracetak dan wajib diverifikasi ulang pada versi 2026, termasuk klaim konversi ke ONNX/OpenVINO, sebelum dikutip: 7,98 sampai 8,01 FPS adalah FPS *idle* tanpa deteksi; dengan deteksi 5,92 sampai 6,22 FPS (statis) dan 4,41 sampai 6,68 FPS (dinamis). Model mereka dikonversi ke ONNX/OpenVINO dan dikuantisasi, jadi angkanya tidak setara dengan PyTorch FP32. Konteksnya FIRA HuroCup dengan ROS 1.
- Saltık, et al. (2025): mAP50 YOLO11n 0,838 menjadi 0,859 dengan CWD, yaitu 2,1 poin (sekitar 2,5% relatif). Naskahnya sendiri tidak konsisten antara "*absolute*" dan "*relative*"; pakai angka tabel.
- Arik dan Ağgül (2026): lihat keputusan E.

### 6. Aturan bahasa

- Bahasa Indonesia ragam baku akademis; paragraf argumentatif dengan satu gagasan pokok yang ditopang bukti bersitasi.
- **Dilarang memakai tanda pisah *em dash* (U+2014).** Susun ulang kalimatnya. Untuk rentang angka, tulis "sampai".
- Hindari pola khas AI: pembuka klise seperti "Dalam era digital saat ini", "Selain itu" beruntun, kalimat yang mengulang pertanyaan, dan penutup paragraf yang merangkum ulang tanpa isi baru.
- Kata baku: "algoritme", "analisis"; jangan memakai "rancang bangun" (Panduan hlm 70 menyarankan "pengembangan").
- **Ejaan dan kata baku diperiksa terhadap folder `EYD & KBBI/`.** Ejaan, tanda baca, huruf kapital, penulisan kata depan, gabungan kata, kata ulang, singkatan, dan penulisan angka dicek terhadap `EYD_permen_46_2009.pdf`. Kebakuan kata dicek terhadap `KamusIndonesia-KBBI-edisi4-2008.pdf`. Ekstrak teks kedua berkas sekali ke `pdf_text/` agar mudah dicari. Kata yang tidak ditemukan di KBBI atau penulisannya meragukan dicatat di `CEK_KBBI.md` dengan status `[PERLU DICEK]`, bukan ditebak.
- Edisi acuan adalah kedua berkas di folder itu, yaitu pedoman ejaan tahun 2009 dan KBBI edisi IV tahun 2008 (keputusan K15). Jangan memakai atau menebak aturan dari edisi lain; bila ada keraguan, tandai dan laporkan.
- Perhatikan kesalahan umum yang disebut Panduan hlm 69 sampai 70: kata depan "di", "ke", dan "dari" ditulis terpisah dari kata yang mengikutinya (kecuali bentuk baku seperti "kepada" dan "daripada"); istilah asing miring; tidak memakai bahasa lisan (misalnya "nampak" seharusnya "tampak"); huruf kapital pada "Gambar" dan "Tabel"; tidak merujuk letak dengan "di atas" atau "di bawah"; istilah tidak baku.
- Istilah asing miring kecuali nama produk (YOLO11, ROS 2, PyTorch, Ultralytics, OpenVINO, Roboflow, ROBOTIS OP3, Intel NUC, Logitech C920). Buat `ISTILAH.md` dan pakai konsisten.
- Singkatan diuraikan pada kemunculan pertama di setiap bab. Koma desimal dan titik ribuan.
- Proposal memakai kalimat rencana ("akan"). Susun kalimat agar mudah diubah ke kalimat lampau ketika Bab 1 sampai 3 dibawa ke template skripsi.

### 7. Aturan pustaka

- Sitasi hanya dari folder Paper dan skripsi kating. Utamakan terbitan 2020 ke atas; sumber lebih lama dipakai untuk karya fondasional (misalnya Hinton, Vinyals, dan Dean, 2015; Romero, et al., 2015; Lin, et al., 2014) atau bila tidak ada pengganti yang lebih baru. Panduan tidak menetapkan batas usia pustaka untuk RPC (hlm 40); laporkan proporsi pustaka 2020 ke atas di setiap TH.
- Metadata Daftar Referensi diambil dari halaman pertama PDF dan dicocokkan dengan nama berkas serta `INVENTARIS_PAPER.csv`. Bila DOI, volume, atau halaman tidak dapat diverifikasi, jangan diisi; beri `[PERLU DICEK]`.
- Klaim tanpa sumber ditulis `[BUTUH SITASI: ...]` dan dimasukkan ke `DAFTAR_UNDUH.md`. Per 23 Oktober 2026, deskripsi platform OP3, BoT-SORT, dan pembanding kuantisasi sudah punya sumber di folder Paper. Yang masih kurang adalah cetakan halaman dataset Roboflow (`Humanoid-Atom, 2026. advance_vision_human dataset.pdf`), yang akan disimpan Bhre secara manual; sampai berkas itu ada, sitasi dataset diberi `[PERLU DICEK]`.
- **Berkas baru sejak TH-0** (19 berkas; nama berkas mengikuti awal entri Daftar Referensi):
  - paper: Ha, Tamura, dan Asama (2013); Hoefler dan Belli (2015); Jacob, et al. (2018); Fiedler, et al. (2019); Reddi, et al. (2020); Gholami, et al. (2021); Nagel, et al. (2021); Aharon, Orfaig, dan Bobrovsky (2022); Huang, et al. (2022); Narayanaswami, et al. (2023); Addufairi dan Setyawan (2026); Setyawan, et al. (2026); Lau dan Pottier (2026);
  - cetakan halaman web: ROBOTIS (n.d.) *ROBOTIS OP3 e-Manual*; Ultralytics (n.d.) *Knowledge distillation*; Ultralytics (n.d.) *Ultralytics YOLO11*; Ultralytics (n.d.) *Performance metrics deep dive*; COCO (n.d.) *Detection evaluation*; PyTorch (2026) *Reproducibility*, diperbarui 14 Mei 2026.
- **Nama berkas dengan "et al."**: empat berkas (Bouthillier, Meneghetti, Paszke, Reddi) memakai "et al." karena batas panjang jalur Windows. Daftar penulis lengkap untuk Daftar Referensi diambil dari halaman pertama PDF, bukan dari nama berkas.
- **Sumber daring (K9)**:
  - contoh entri sesuai Panduan butir 18: `ROBOTIS, n.d. ROBOTIS OP3 e-Manual. [online] Tersedia di: <https://emanual.robotis.com/docs/en/platform/op3/introduction/> [Diakses 23 Oktober 2026]`;
  - tiga halaman Ultralytics sama-sama bertahun n.d., sehingga perlu huruf pembeda sesuai butir 5; usulkan bentuknya di TH-1 (misalnya n.d.a, n.d.b, n.d.c) dan pakai konsisten;
  - pustaka Ultralytics sebagai program komputer (butir 17) memakai sitasi yang disarankan halaman YOLO11: Jocher dan Qiu (2024), *Ultralytics YOLO11* versi 11.0.0, <https://github.com/ultralytics/ultralytics>. Versi paket yang benar-benar dipakai (8.4.130) tetap disebut di Bab 3;
  - COCO (n.d.) mendefinisikan objek kecil, sedang, dan besar dengan ambang area 32² dan 96² piksel yang dihitung dari *mask* segmentasi. Bila ukuran objek dipakai, tulis bahwa penelitian ini memakai luas kotak pembatas sebagai padanannya.
- **Butir `[PERLU DICEK]` yang sudah diketahui**:
  - Addufairi dan Setyawan (2026): kepala halaman PDF masih "hlm. x-x"; nomor halaman dicek di J-PTIIK;
  - Narayanaswami, et al. (2023): PDF versi penulis hanya menyebut RoboCup 2022; tahun 2023 dan halaman 62 sampai 74 berasal dari daftar unduh, belum dari PDF;
  - Gholami, et al. (2021): versi arXiv; status terbit resminya belum dipastikan;
  - Lin, et al. (2014): PDF di folder adalah arXiv v3 dengan 10 penulis, sedangkan `REFERENSI_SKRIPSI.bib` memakai versi ECCV dengan 8 penulis. Ikuti PDF yang disitasi;
  - Efron (1979): dipakai hanya bila *bootstrap* disebut di Bab 3. PDF-nya pindaian JSTOR tanpa lapisan teks, sehingga `pdftotext` tidak menghasilkan isi dan kutipan langsung harus diketik manual.
- Gambar dari pustaka diutamakan digambar ulang; bila dikutip, beri "Sumber: …" sesuai Panduan.

### 8. Penanganan `.docx`

- Sunting berkas pengerjaan `E:\Kuliah\Thesis\Laporan\Proposal\Proposal_KD_OP3_v1.docx` dengan python-docx atau XML langsung, memakai *style* yang sudah ada. Bila *style* naskah berbeda dari template proposal (TH-0 menemukan beda `numId` pada empat *style* daftar dan lima *style* tambahan), ikuti template.
- Isi topik lama (kuantisasi INT8) dihapus seluruhnya, termasuk tabel, gambar, dan entri referensinya. Kalimat lama hanya dipakai ulang bila tetap benar untuk topik KD, dengan sitasi dicek ulang.
- *Caption* dibuat dengan menyalin XML *caption* yang ada agar *field* `SEQ` tetap berfungsi. Tabel memakai gaya tabel yang ada.
- Persamaan sebagai OMML. Cara pembuatannya mengikuti keputusan A.
- Gambar dibuat sendiri dengan Graphviz atau Matplotlib pada 300 dpi; sumber `.dot` atau `.py` disimpan di folder kerja. Gambar Bab 3 dibatasi pada diagram alir metode penelitian dan jadwal, sesuai keputusan C.
- Simpan cuplikan per TH (`cuplikan/Proposal_KD_OP3_TH<n>.docx` dan PDF). Ubah ke PDF dengan LibreOffice dan periksa beberapa halaman sebagai gambar. Ingatkan Bhre memperbarui daftar isi, daftar tabel, dan daftar gambar di Word.

### 9. Kerangka isi

Kerangka ini usulan dan difinalkan di TH-1.

**Bab 1 Pendahuluan**

- **1.1 Latar Belakang**, piramida terbalik (hlm 33 sampai 34): kebutuhan robot humanoid sepak bola mendeteksi bola, gawang, dan robot; keterbatasan komputasi CPU komputer *onboard* (Adipratama, 2026; Lau dan Pottier, 2026, dengan koreksi 5.7); kompromi ukuran model terhadap akurasi dan kecepatan; KD sebagai cara melatih *student* kecil meniru *teacher* tanpa mengubah biaya inferensi *student* (Hinton, Vinyals, dan Dean, 2015; Gou, et al., 2021; Shehzadi, et al., 2026); KD pada keluarga YOLO dan sistem tepi (Saltık, et al., 2025; Jung dan Nam, 2025; Sharma, et al., 2026; Billy, 2019; Zaini, 2024); celah yang ditulis sebagai batas penelusuran penulis, bukan klaim mutlak; pembeda dengan kuantisasi (Jacob, et al., 2018; Nagel, et al., 2021, atau Gholami, et al., 2021 sebagai rujukan survei); kalimat jembatan ke penelitian ini.
- **1.2 Rumusan Masalah**: lima nomor di 5.1 apa adanya.
- **1.3 Tujuan**: satu tujuan per rumusan masalah, berurutan, dalam bentuk pernyataan (hlm 37 sampai 38).
- **1.4 Manfaat**: bagi tim robot sepak bola humanoid (nama tim `[ISI]`) dan bagi penelitian KD pada sistem tertanam; tanpa "untuk memenuhi syarat gelar" (hlm 39).
- **1.5 Batasan Masalah**: tiga kelas; *teacher* YOLO11n dan *student* YOLO11 skala t; PyTorch FP32 `.pt` tanpa kuantisasi; perangkat robot sesuai 5.3; dua kondisi robot; masukan 640; pelatihan di server lab. Batasan yang sangat teknis dipindah ke Bab 3 (hlm 39).
- **Rumusan hipotesis**: tidak dipakai kecuali Bhre memutuskan lain (K10).
- **1.6 Sistematika Pembahasan**: tujuh bab sesuai keputusan di bagian 3, masing-masing dengan deskripsi singkat.

**Bab 2 Landasan Kepustakaan**

- **2.1 Kajian Pustaka**: tabel penelitian terdahulu dengan kolom penelitian, objek dan perangkat, *teacher* ke *student*, metode KD, metrik dan hasil pokok, serta perbedaan dengan penelitian ini. Kandidat: Billy (2019), Zaini (2024), Saltık, et al. (2025), Jung dan Nam (2025), Arik dan Ağgül (2026), Sharma, et al. (2026), Sabaghian, Keyvanrad, dan Moghadami (2025), Lau dan Pottier (2026), Jati, Ilyasa, dan Dominic (2024), Barry, et al. (2019), Fiedler, et al. (2019), Meneghetti, et al. (2021), Bordado, Silveria, dan Laureano (2023), Narayanaswami, et al. (2023), Addufairi dan Setyawan (2026), Setyawan, et al. (2026), Adipratama (2026). Tutup dengan paragraf posisi penelitian yang menegaskan keunikan sesuai A.5.1.1 (arsitektur sistem, metode, atau data).
- **2.2 Dasar Teori**, usulan urutan: robot humanoid ROBOTIS OP3 dan sepak bola robot (Ha, Tamura, dan Asama, 2013; ROBOTIS, n.d.); deteksi objek dan YOLO11 (Redmon, et al., 2016; Khanam dan Hussain, 2024), termasuk *head* Detect dan *Distribution Focal Loss* (Li, et al., 2020); *knowledge distillation* (target lunak, temperatur, taksonomi respons, fitur, relasi); pengaruh ukuran dan kekuatan *teacher* sebagai dasar ablasi YOLO11s (Cho dan Hariharan, 2019; Mirzadeh, et al., 2020; Huang, et al., 2022); KD untuk detektor (distilasi fitur dengan proyektor: Romero, et al., 2015; Chen, et al., 2017; Wang, et al., 2019; distilasi respons pada klasifikasi sigmoid: Yang, et al., 2023; distilasi lokalisasi: Zheng, et al., 2022; KD murni dan KD hibrida); ROS 2 (Macenski, et al., 2022) dan latensi sistem multi-*node* (Kronauer, et al., 2021); pelacakan BoT-SORT bila Bhre ingin membahasnya (Aharon, Orfaig, dan Bobrovsky, 2022); *non-maximum suppression* (Bodla, et al., 2017); metrik akurasi IoU, *precision*, *recall*, F1, AP, mAP50, mAP50-95 (Lin, et al., 2014; Padilla, et al., 2021; Ultralytics, n.d.), beserta ambang ukuran objek bila dipakai (COCO, n.d.); metrik kinerja latensi, FPS efektif, CPU, RAM (Hoefler dan Belli, 2015; Reddi, et al., 2020); variasi antar-*seed* dan reproduksibilitas (Bouthillier, et al., 2021; Picard, 2021; PyTorch, 2026).
- Rumus *loss* setiap varian ditulis sebagai persamaan bernomor dengan notasi dijelaskan. Rumus yang menggambarkan implementasi repo diverifikasi terhadap `scripts/train_kd.py` dan `configs/`.

**Bab 3 Metodologi Penelitian** (hlm 40 sampai 41; tanpa daftar kebutuhan dan hasil rancangan)

- **Tipe penelitian**: implementatif-pengembangan bidang RPC beserta alasannya.
- **Strategi dan rancangan penelitian**: pembuatan artefak berupa sistem deteksi objek berbasis ROS 2 di OP3 dan alur pelatihan KD, disertai eksperimen pembandingan model; subjek (model dan robot); lokasi (server lab dan laboratorium robot `[ISI]`); teknik pengumpulan data (himpunan data Roboflow, log runtime, *frame* kamera OP3); teknik analisis data (statistik deskriptif per *seed* dan per ulangan, selisih berpasangan, tanpa klaim signifikansi bila jumlah ulangan tidak memadai); peralatan pendukung (perangkat keras dan lunak server serta robot dari 5.3).
- **Diagram alir penelitian**: studi literatur, pengumpulan dan audit data, analisis kebutuhan, perancangan, implementasi pelatihan (*supervised*, KD murni, KD hibrida, tiga *seed*), pemilihan varian di VAL, evaluasi TEST, implementasi *node* ROS 2 di OP3, pengujian fungsional, pengujian akurasi, pengujian runtime live, analisis, kesimpulan.
- **Metode setiap tahap dan hasil yang diharapkan**:
  - analisis kebutuhan: cara mengidentifikasi kebutuhan perangkat keras, perangkat lunak, fungsional, dan nonfungsional; hasil yang diharapkan minimal empat kebutuhan fungsional dan satu nonfungsional, dijabarkan di Bab 4;
  - perancangan: cara memodelkan perangkat keras (diagram blok) dan perangkat lunak (*flowchart* atau *sequence diagram*) per subsistem; hasilnya di Bab 5;
  - implementasi: lingkungan dan alat, resep pelatihan identik, aturan pemilihan varian di VAL sebelum TEST;
  - pengujian: fungsional, akurasi, dan runtime sesuai 5.4, termasuk cara menghitung setiap metrik dan definisi kondisi diam serta berjalan;
  - analisis dan penarikan kesimpulan: pemetaan hasil ke setiap rumusan masalah.
- **Jadwal Penelitian**: tabel kegiatan per minggu atau bulan, maksimal satu semester, disusun dari status 5.5; target seminar dan sidang `[ISI]`.

**Daftar Referensi**: hanya karya yang disitasi, diurutkan dan diformat sesuai Panduan.

### 10. Alur kerja dan titik henti

```
TH-1  Sinkronisasi TH-0, kerangka final, peta sitasi, istilah, keputusan Bhre
TH-2  Sampul, bagian awal, dan Bab 1
TH-3  Bab 2
TH-4  Bab 3 beserta diagram alir dan jadwal
TH-5  Daftar Referensi dan pemeriksaan akhir
```

**TH-1**

1. Hasil sinkronisasi bagian 2.
2. Kerangka final sampai tingkat subbab dengan perkiraan panjang, dicocokkan dengan subbab template proposal dan template skripsi.
3. `PETA_SITASI.md`: setiap klaim yang direncanakan dipetakan ke berkas, halaman, atau `[BUTUH SITASI]`.
4. `DAFTAR_UNDUH.md` dan `ISTILAH.md`.
5. Daftar keputusan untuk Bhre:
   - **A**: cara membuat persamaan OMML (memasang *pandoc*, biner *pandoc* di folder kerja, atau OMML langsung);
   - **F**: nama model komputer OP3;
   - **G, H**: izin akses web untuk metadata pustaka;
   - **K1**: proposal murni rencana, atau menyebut bahwa sebagian tahap sudah berjalan (bawaan: rencana; status kerja hanya muncul di jadwal);
   - **K2**: penulisan istilah KD (bawaan: *knowledge distillation* miring dengan singkatan KD);
   - **K3**: cara menyebut asal *teacher*;
   - **K4**: nilai target kebutuhan nonfungsional;
   - **K5**: definisi kondisi berjalan (*gait* standar di tempat atau berpindah) untuk ditulis di Bab 3;
   - **K6**: jadwal dan target sidang;
   - **K7**: data sampul (nama lengkap, NIM, nama program studi dan jurusan, tahun);
   - **K8**: evaluasi citra kamera OP3 sebagai pengujian utama atau pendukung;
   - **K9**: sudah ditetapkan di bagian 3 (dokumentasi daring boleh disitasi); laporkan saja bentuk huruf pembeda n.d. yang diusulkan;
   - **K10**: rumusan hipotesis dipakai atau tidak;
   - **K11**: tanggal persetujuan pembimbing atas rumusan masalah;
   - **K12**: struktur tujuh bab skripsi sudah disetujui pembimbing atau belum;
   - **K13**: *supervised* dan KD murni disebut sebagai pembanding pelengkap pada pengujian runtime, mengingat rumusan masalah nomor 4 dan 5 hanya menyebut model hasil KD dan *teacher*;
   - **K14**: penghubung dua nama terakhir pada sitasi di dalam kurung. Contoh Panduan hlm 56 memakai "&", misalnya (Rumbaugh, Jacobson, & Booch, 2005), sedangkan contoh di prompt ini memakai "dan", misalnya (Hinton, Vinyals, dan Dean, 2015). Contoh Panduan sendiri tidak seragam; pilih satu bentuk dan pakai konsisten di seluruh naskah;
   - **K15**: sudah ditetapkan di bagian 3 (edisi acuan ejaan dan kata baku adalah berkas di folder `EYD & KBBI/`).

**TH-2 sampai TH-4**

- Tulis langsung ke berkas pengerjaan `E:\Kuliah\Thesis\Laporan\Proposal\Proposal_KD_OP3_v1.docx`. Perbarui `KLAIM_SUMBER.md` (bab dan subbab, kalimat ringkas, sumber, halaman atau tabel, path repo untuk fakta eksperimen).
- Simpan cuplikan dan lakukan pemeriksaan visual.
- Laporkan ringkasan isi, jumlah kata per subbab, daftar `[BUTUH SITASI]` dan `[ISI]`, proporsi pustaka 2020 ke atas, serta penyimpangan dari kerangka.

**TH-5**

1. Daftar Referensi dari sitasi yang benar-benar dipakai.
2. Skrip pemeriksaan otomatis atas seluruh teks, termasuk tabel dan *caption*: tidak ada U+2014 (laporkan juga U+2013); tidak ada "algoritma", "analisa", "rancang bangun"; frekuensi "Selain itu"; setiap sitasi dalam teks ada di Daftar Referensi dan sebaliknya; aturan "et al." sesuai bagian 3; istilah di `ISTILAH.md` yang belum miring; desimal bertitik dalam kalimat; rujukan "di atas" atau "di bawah"; sisa penanda `[BUTUH SITASI]`, `[ISI]`, `[PERLU DICEK]`, `[PERLU VERIFIKASI REPO]`. Skrip juga menghasilkan daftar kandidat kata depan "di", "ke", dan "dari" yang tersambung dengan kata tempat atau waktu untuk ditinjau manual (awalan pasif "di-" bukan kesalahan), serta daftar kata tidak baku yang disebut Panduan hlm 69 sampai 70. Lampirkan `CEK_KBBI.md` berisi kata yang sudah dicek ke KBBI, hasilnya, dan halaman KBBI tempat kata itu ditemukan.
3. Daftar periksa kesesuaian dengan Panduan: kerangka proposal, sampul, enam subbab Bab 1, subbab Jadwal Penelitian, larangan isi Bab 3, kecukupan A.5.1.1, format tabel, gambar, dan persamaan.
4. Ubah ke PDF dan periksa tata letak.

### 11. Format laporan di setiap titik henti

1. Yang dikerjakan.
2. Berkas yang dibuat atau diubah beserta path.
3. Perintah dan hasilnya.
4. Penyimpangan dari prompt ini beserta alasannya.
5. Keputusan atau informasi yang dibutuhkan dari Bhre.

### 12. Mulai dari sini

Kerjakan TH-1, lalu berhenti dan tunggu persetujuan Bhre.
