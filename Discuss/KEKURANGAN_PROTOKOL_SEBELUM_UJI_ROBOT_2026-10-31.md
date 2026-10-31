# Kekurangan protokol sebelum uji robot OP3

Tanggal: 31 Oktober 2026. Status: **bahan diskusi, belum diputuskan.** Disusun dari protokol percobaan di repo (HEAD `d628c0c`) dan proposal `Laporan/Proposal/Proposal_KD_OP3_v1.docx`. Dokumen ini tidak mengubah kode, konfigurasi, maupun proposal.

## Ringkasan

Protokol inti sudah kuat: pemilihan model dan *seed* di VAL, tiga *seed* per metode, uji *live* setara empat model × dua kondisi × tiga ulangan, dan set *frame* OP3 baru yang terpisah dari pengukuran *runtime*. Ada empat kekurangan yang perlu diselesaikan **sebelum** uji robot karena menentukan sah atau tidaknya hasil. Keempatnya ringan dan tidak menambah eksperimen.

| No | Kekurangan | Dampak bila dibiarkan | Perlu dari Bhre |
| --- | --- | --- | --- |
| 1 | Skenario uji fungsional rumusan masalah 1 belum ada | RQ1 tidak punya data | Setujui atau ubah daftar kebutuhan dan skenario |
| 2 | D3, D4, D6, D7, D8, D11 masih "BELUM DIKUNCI"; definisi F1 dua evaluator berbeda | Ambang dan metrik bisa dipersoalkan; F1 TEST dan OP3 tidak sebanding | Setujui nilai yang dikunci |
| 3 | Ukuran set *frame* OP3 baru belum ditetapkan | Set evaluasi eksternal bisa terlalu kecil, terutama kelas bola dan robot | Tetapkan jumlah per kondisi dan per kelas |
| 4 | Persetujuan pembimbing atas protokol *live* belum tercatat | Hasil uji robot bisa dipersoalkan saat P2 atau seminar hasil | Minta persetujuan singkat |

## 1. Skenario uji fungsional rumusan masalah 1

**Masalah.** Proposal (Subbab 3.1 dan 3.3.5) menjanjikan minimal empat kebutuhan fungsional dan satu kebutuhan nonfungsional yang diuji dengan metode kotak hitam. Di repo belum ada daftar kebutuhan maupun skenario ujinya. `prompt/PROMPT_BAB_IV_V_HASIL_KD_OP3_V2.md` baris 64 juga mensyaratkan tabel kebutuhan fungsional dan hasil ujinya untuk RQ1.

**Usulan awal** (diturunkan dari kemampuan `scripts/op3_pytorch_detector.py` yang sudah ada; dijalankan pada sesi robot yang sama dengan pemeriksaan fungsi di prompt 30 Oktober):

| Kode | Kebutuhan | Skenario uji (masukan dan langkah) | Hasil yang diharapkan |
| --- | --- | --- | --- |
| KF-01 | Sistem menerima citra kamera OP3 | Jalankan *node* dengan `input_topic:=/thesis/image_raw` | *Frame* diterima dan diproses tanpa *error frame* |
| KF-02 | Sistem mendeteksi bola, gawang, dan robot | Tampilkan ketiga objek satu per satu di depan kamera | Kelas yang benar muncul pada `/vision/detections` dan *preview* |
| KF-03 | Sistem melacak objek dengan BoT-SORT | Gerakkan bola perlahan di depan kamera | Objek mendapat ID dan ID bertahan selama objek terlihat |
| KF-04 | Sistem mencatat log *runtime* per *frame* | Jalankan satu *run* pendek, lalu buka CSV | Kolom cap waktu, waktu tiap tahap, CPU, RSS, dan jumlah deteksi per kelas terisi |
| KF-05 | Sistem menampilkan *preview* deteksi ke laptop | Aktifkan `publish_debug_image:=true` dan penampil SSH-X | Kotak, kelas, ID, dan *confidence* tampil di laptop |
| KNF-01 | Laju pemrosesan | Uji *runtime* sesuai protokol setara | FPS efektif rata-rata minimal 8 pada kondisi diam dan berjalan (acuan Lau dan Pottier, 2026) |

Catatan: KF-05 bersifat pilihan; empat kebutuhan pertama sudah memenuhi syarat minimal. Skenario dinyatakan berhasil bila keluaran aktual sama dengan yang diharapkan. Pemeriksaan ini terpisah dari 24 *run* benchmark.

## 2. Keputusan protokol yang belum dikunci

**Masalah.** `configs/analysis.yaml` masih menandai beberapa keputusan "BELUM DIKUNCI", padahal nilainya sudah dipakai di proposal dan di `prompt/PROMPT_TES_ROBOT_OP3_2026-10-30.md`. Mengunci sebelum uji mencegah kesan bahwa nilai dipilih sesudah melihat hasil.

| Keputusan | Isi | Nilai yang sudah dipakai | Usulan |
| --- | --- | --- | --- |
| D3 | Jumlah *epoch* | 100 (semua *run* final) | Kunci 100 sesuai yang sudah dijalankan |
| D4 | *Confidence* dan NMS IoU *live* | 0,25 dan 0,45 | Kunci |
| D6 | Jumlah *thread* | `analysis.yaml` mengusulkan sapuan 2/4/6/8, tetapi prompt uji setara memakai **4/2 tetap** (sama dengan percobaan 20 sampai 27) | Kunci 4/2 dan catat bahwa sapuan tidak dijalankan |
| D7 | Ulangan | 3 sesi × 60 detik per model per kondisi | Kunci |
| D8 | Jumlah *frame* OP3 berlabel | `null` | Lihat bagian 3 |
| D11 | Definisi F1 keseluruhan | Proposal: rata-rata harmonik *precision* makro dan *recall* makro | Kunci; samakan evaluator OP3 (di bawah) |

**Selisih definisi F1.** Evaluator TEST (`scripts/evaluate_locked_test.py` baris 718) dan `op3_camera_eval` menghitung F1 dari *precision* makro dan *recall* makro (rata-rata harmonik). `op3_multi_session_eval` (`evaluate.py` baris 136 sampai 137) menyebut rata-rata F1 per kelas sebagai "macro". Bila set OP3 dievaluasi dengan `op3_multi_session_eval`, laporkan F1 harmonik sebagai angka utama dan rata-rata F1 per kelas sebagai pelengkap, agar sebanding dengan TEST.

D5 (sapuan *grid*), D9 (penyimpanan), dan D10 (ukuran objek) tidak dipakai untuk menjawab rumusan masalah; boleh ditandai "tidak dipakai".

## 3. Ukuran set *frame* OP3 baru

**Masalah.** Set ini satu-satunya evaluasi yang bersih karena TEST sudah pernah dibuka (DECISIONS D13, R-24) dan T34 sudah dipakai untuk merancang `hybrid_v2`. Prompt 30 Oktober meminta jumlah *frame* dibekukan sebelum perekaman, tetapi angkanya belum ada (D8 `null`).

**Acuan.** T34 memakai 260 *frame* (200 berobjek dan 60 tanpa objek; 400 kotak) untuk satu rangkaian. Di TEST, anotasi bola hanya 83 dan robot 119, dibanding gawang 532, sehingga metrik per kelas bola dan robot rawan tidak stabil.

**Yang perlu ditetapkan** (isi oleh Bhre sebelum merekam):

| Butir | Kondisi diam | Kondisi berjalan |
| --- | --- | --- |
| Jumlah *frame* berobjek | … | … |
| Jumlah *frame* tanpa objek | … | … |
| Minimal objek bola | … | … |
| Minimal objek gawang | … | … |
| Minimal objek robot | … | … |
| Variasi jarak dan posisi | … | … |
| Selang pengambilan | 1 *frame* per detik (bawaan `capture_op3_frames.py`) | sama |
| Aturan gawang utuh atau sebagian | … | … |
| Cara pelabelan | dari gambar mentah (`op3_blind_label_reviewer`) atau dengan pra-label (`op3_label_reviewer`) | sama |

Usulan sederhana: sekitar 260 *frame* per kondisi seperti T34, dengan sesi khusus bola dan robot agar kedua kelas itu tidak terlalu sedikit. Perekaman dilakukan sesudah seluruh *run runtime*, pada sesi terpisah.

## 4. Persetujuan pembimbing

`docs/DECISIONS.md` D14 mencatat bahwa persetujuan pembimbing atas rincian protokol *live* terbaru belum terdokumentasi. Cukup minta persetujuan singkat (pesan atau catatan bimbingan) atas: empat model, dua kondisi, tiga ulangan, pengaturan *runtime* di D4/D6/D7, dan rancangan set *frame* OP3. Catat tanggal dan bentuk persetujuannya di `DECISIONS.md`.

## Yang tidak perlu ditambah

*Seed* tambahan, uji hipotesis statistik, model atau arsitektur lain, kuantisasi atau ONNX, pengukuran *preview* mati, dan variasi *thread*. Batasan-batasan ini sudah dinyatakan di proposal; menambahnya memperpanjang pekerjaan tanpa mengubah jawaban rumusan masalah.

## Waktu

Menurut Tabel 3.5 proposal, uji robot dan pengambilan data dijadwalkan pada Oktober, P2 pada 11 Desember 2026. Keempat butir di atas dapat diselesaikan dalam satu sampai dua hari, sehingga uji robot, pelabelan, dan evaluasi masih dapat selesai sebelum P2.

## Terkait

- Usulan pembaruan proposal yang ditunda sampai uji robot (ablasi *teacher* T42 di 3.3.4 dan cara pelabelan di 3.3.5): `Laporan/Proposal/kerja_proposal_kd/LAPORAN_TH5.md`, bagian "Tertunda".
- Prosedur uji robot: `prompt/PROMPT_TES_ROBOT_OP3_2026-10-30.md`, `prompt/PROMPT_UJI_ULANG_LIVE_SETARA_OP3_DENGAN_TEACHER.md` (Fase 8c), `docs/PERSIAPAN_OP3_DARI_LAB_2026-10-30.md`.
- Protokol ablasi *teacher*: `docs/PROTOKOL_T42_ABLASI_TEACHER_2026-10-24.md`.
