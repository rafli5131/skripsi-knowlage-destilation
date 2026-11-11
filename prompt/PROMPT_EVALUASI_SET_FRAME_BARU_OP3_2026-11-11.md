# Prompt evaluasi set frame kamera OP3 baru dengan pra-label terkendali

Tanggal: 11 November 2026. Dasar keputusan: D19 di [`docs/DECISIONS.md`](../docs/DECISIONS.md). Dijalankan oleh agen di **komputer OP3**. Tugasnya mengevaluasi akurasi empat *checkpoint* beku pada set frame kamera OP3 baru yang independen dari T38. Ini bukan uji runtime dan bukan pelatihan.

## Larangan

- Jangan mengirim perintah servo, gait, motor, atau torque. Operator (Bhre) mengatur dan memverifikasi kondisi fisik; bila tidak terverifikasi, catat `unknown`.
- Jangan mengubah *checkpoint*, *threshold*, atau konfigurasi setelah perekaman dimulai. Jangan memilih ulang model atau *threshold* berdasarkan hasil set ini.
- Jangan menimpa atau menghapus data, label, atau hasil lama (termasuk T34 dan T38). Pakai direktori sesi baru.
- Jangan *commit* atau push frame, label, atau log robot tanpa izin eksplisit Bhre. *Commit* dan push tabel atau dokumentasi juga hanya bila diminta.
- Bila tidak yakin pada fakta teknis, katakan tidak yakin. Jangan merekonstruksi data yang tidak terekam.

## Fase 0. Persiapan dan pembekuan (sebelum kamera merekam)

1. Jalankan `git status --short`; bila bersih, `git pull --ff-only origin main`. Baca `agent.md`, `docs/DECISIONS.md`, `configs/analysis.yaml`, `analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md`, README `ros2_packages/op3_label_reviewer`, `op3_blind_label_reviewer`, `op3_multi_session_eval`, serta `scripts/capture_op3_frames.py` dan `scripts/prelabel_op3_frames.py`.
2. *Checkpoint* yang dievaluasi (verifikasi SHA-256 terhadap `configs/model_registry.yaml` dan audit T38): *teacher* YOLO11n FP32 (`e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`), `hybrid_full_seed1337`, `supervised_seed1337`, dan `kd_seed42`.
3. Pemberi pra-label: utamakan *teacher* YOLO11s T42 (`server2`). Cocokkan hash-nya dengan kolom `teacher_checkpoint_sha256` baris `yolo11s` di `analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.csv`. Bobot ini privat: simpan di `models_local/` (diabaikan Git), jangan di-*commit*. Bila bobot itu tidak ada di robot, gunakan gabungan prediksi keempat model yang dievaluasi (union setelah NMS antarmodel) agar bias tidak berpihak ke satu model. Catat pilihan dan alasannya. Jangan memakai satu model yang dievaluasi saja sebagai pemberi pra-label. Bila skrip yang ada tidak mendukung pilihan ini, buat *package* baru sesuai `agent.md`, tanpa mengubah *package* lama.
4. Tulis `frozen_plan.json` sebelum merekam, berisi hash keempat *checkpoint* dan pemberi pra-label; parameter evaluasi sama dengan T38 (imgsz 640, CPU FP32, NMS IoU 0,7, *confidence floor* 0,001 untuk AP, *precision*/*recall*/F1 pada *confidence* > 0,25 dan IoU pencocokan ≥ 0,5); definisi F1 utama sesuai D11 (rerata harmonik *precision* makro dan *recall* makro) dan F1 per kelas sebagai pelengkap; ukuran set dan aturan label di bawah. Tunjukkan isinya kepada Bhre dan minta persetujuan sebelum lanjut.
5. Ukuran set (usulan; Bhre mengonfirmasi atau mengubah sebelum merekam): total 260 frame, yaitu kondisi diam 100 berobjek dan 30 negatif, kondisi berjalan 100 berobjek dan 30 negatif; minimal 100 kotak per kelas (`ball`, `gawang`, `robot`) di seluruh set; pengambilan 1 frame per detik; adegan berbeda dari T38 (posisi objek, jarak, latar, atau pencahayaan) dan dicatat; aturan eksplisit untuk gawang utuh dan sebagian, mengikuti konvensi T38 bila ada, dengan frame gawang sebagian disimpan terpisah. Set ini dilaporkan sebagai tabel baru (usulan T43) dan tidak digabung dengan T38.

## Fase 1. Perekaman (operator mengatur robot)

6. Rekam frame mentah dengan `scripts/capture_op3_frames.py` ke `data/op3_camera_eval/sessions/<session_id_baru>/` untuk setiap kondisi. Model tidak perlu berjalan saat merekam. Catat waktu, kondisi fisik menurut operator, deskripsi adegan, dan foto adegan bila tersedia. Simpan manifest berisi hash setiap gambar.
7. Bila kuota per kondisi atau per kelas belum terpenuhi, rekam sesi tambahan dengan aturan yang sama dan catat. Jangan membuang frame yang sudah direkam; tandai bila dikeluarkan beserta alasannya sesuai aturan yang dibekukan.

## Fase 2. Label buta untuk audit bias (sebelum melihat pra-label)

8. Pilih acak 20% frame (catat *seed* acaknya; proporsional per kondisi, misalnya 52 dari 260) dan minta Bhre melabeli dari gambar mentah dengan `op3_blind_label_reviewer`, tanpa melihat prediksi apa pun. Simpan sebagai `labels_blind`.

## Fase 3. Pra-label dan tinjauan

9. Buat pra-label untuk semua frame dengan pemberi pra-label dari langkah 3, dengan *confidence* rendah (misalnya 0,10) agar objek tidak terlewat. Simpan sebagai `labels_auto`; ini draf, bukan *ground truth*.
10. Bhre meninjau **semua** frame dengan `op3_label_reviewer`, termasuk frame negatif: tambah, hapus, geser, atau ubah kelas. Simpan sebagai `labels_reviewed` beserta log tinjauan per frame. Catat statistik koreksi: kotak diterima tanpa perubahan, digeser, diubah kelas, dihapus, dan ditambah.
11. Audit bias: bandingkan `labels_reviewed` dengan `labels_blind` pada subset 20% (kecocokan kotak IoU ≥ 0,5 dan kelas, per kelas). Laporkan angka kesepakatan. Bila kesepakatan rendah pada suatu kelas, laporkan; jangan mengubah label agar cocok.

## Fase 4. Evaluasi

12. Bekukan `labels_reviewed` (hash). Evaluasi keempat *checkpoint* dengan `op3_multi_session_eval` atau evaluator T38 yang sama, pada frame dan label identik. Laporkan per model dan per kelas: mAP50, mAP50–95, *precision*, *recall*, F1 utama dan pelengkap, TP/FP/FN, serta frame negatif dengan *false positive*; terpisah untuk kondisi diam, berjalan, dan gabungan. Frame gawang sebagian dianalisis terpisah.
13. Buat *confusion matrix* empat model (mengikuti pola `dokumentasi/model/`) dan grafik ringkas versi Indonesia dan Inggris.
14. Bandingkan dengan T38 secara deskriptif saja, karena keduanya set dan konteks yang berbeda. Jangan mengganti model utama berdasarkan hasil ini.

## Fase 5. Dokumentasi dan laporan

15. Tulis `analisis_performa/tabel/T43_*.{csv,md}` dan `dokumentasi/<tanggal>/percobaan-<nomor berikutnya>-evaluasi-set-frame-baru/README_ID.md` serta `README_EN.md`, berisi rencana beku, deskripsi sesi, pemberi pra-label, statistik koreksi, hasil audit bias, hasil evaluasi, dan keterbatasan (misalnya pra-label tetap berpotensi memengaruhi peninjau, jumlah sesi, dan ukuran per kelas).
16. Simpan manifest hash sumber dan keluaran. Laporkan kepada Bhre: ringkasan hasil, `git status --short`, dan tanyakan apa yang boleh di-*commit* dan di-push. Frame dan label secara bawaan tetap lokal.

## Urutan pada hari pengujian

Jalankan [prompt grafik runtime](PROMPT_GRAFIK_RUNTIME_OP3_GARIS_KONTINU_2026-11-11.md) lebih dulu karena hanya membaca berkas, lalu prompt ini.
