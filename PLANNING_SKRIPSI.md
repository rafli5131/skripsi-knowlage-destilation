# Planning Skripsi: Pure Knowledge Distillation untuk Deteksi Advance Vision

## Arah topik

**Judul kerja:** *Kompresi Model YOLO untuk Deteksi Objek Advance Vision Menggunakan Pure Teacher-Only Knowledge Distillation*

Topik ini meneliti apakah student YOLO yang lebih kecil dapat meniru teacher YOLO11n melalui target teacher saja, sambil mempertahankan kualitas deteksi dan memperbaiki biaya inferensi. Judul final, istilah “Advance Vision”, dan format proposal perlu disesuaikan dengan pedoman prodi serta arahan dosen pembimbing.

Kerangka Bab I–V dan peta bukti per pertanyaan penelitian ada di [`KERANGKA_BAB_SKRIPSI.md`](KERANGKA_BAB_SKRIPSI.md).

## Goal penelitian

Mengukur secara adil efektivitas pure teacher-only KD untuk mengompresi detektor tiga kelas (`ball`, `gawang`, `robot`) pada dataset Advance Vision, dibandingkan dengan teacher dan student berarsitektur sama yang dilatih secara supervised sebagai kontrol terpisah. KD utama tidak memakai ground-truth loss, pseudo-label loss, atau QAT.

## Pertanyaan penelitian

1. Seberapa besar perubahan mAP student hasil pure KD dibandingkan teacher YOLO11n dan student arsitektur sama yang dilatih supervised?
2. Bagaimana trade-off kualitas deteksi terhadap jumlah parameter, ukuran checkpoint, FLOPs, latensi, dan throughput?
3. Kelas mana yang paling banyak kehilangan atau memperoleh performa setelah kompresi, dilihat dari mAP50, mAP50–95, dan recall?

**Hipotesis kerja utama:** student pure KD memperoleh mAP50–95 lebih tinggi daripada baseline supervised pada arsitektur student yang sama. Perbandingan tersebut menguji dampak objective terhadap akurasi, bukan keunggulan ukuran atau FLOPs student. Klaim kompresi diuji terpisah terhadap teacher dengan parameter, ukuran checkpoint, FLOPs, latensi, dan metrik akurasi. Tidak ada ambang “material” atau toleransi mAP sebagai kriteria lulus; semua hasil dilaporkan dan inferensi antar-seed diperlakukan eksploratif karena hanya ada tiga pasangan seed.

## Landasan literatur dan posisi kontribusi

Distilasi klasik memindahkan informasi dari model/ensemble besar ke model kecil melalui keluaran teacher yang dilunakkan oleh temperatur. Pada deteksi objek, keluaran terstruktur berisi kelas dan lokasi, sehingga penelitian berikutnya juga meniru fitur internal dan perilaku prediksi. Namun, istilah KD mencakup objective yang berbeda-beda: sejumlah metode memasangkan distilasi dengan loss ground-truth atau menggunakan label untuk memilih area distilasi. Metode prediction-mimicking dapat memakai prediksi teacher sebagai target KD, tetapi hal ini tidak memastikan objective total bebas label; CrossKD, misalnya, tetap memasukkan loss deteksi berlabel dalam objective total (Wang et al., 2024). Pembedaan ini penting karena studi ini menetapkan “pure teacher-only” secara operasional: loss update student hanya berasal dari output/fitur teacher; label TRAIN tidak masuk ke loss.

| Studi primer | Mekanisme utama | Hubungan dengan objective studi ini |
| --- | --- | --- |
| [Hinton, Vinyals, dan Dean (2015), *Distilling the Knowledge in a Neural Network*](https://arxiv.org/abs/1503.02531) | Distilasi distribusi keluaran lunak dengan temperatur. | Landasan umum teacher–student; bukan metode deteksi objek. |
| [Wang et al. (CVPR 2019), *Distilling Object Detectors with Fine-Grained Feature Imitation*](https://openaccess.thecvf.com/content_CVPR_2019/html/Wang_Distilling_Object_Detectors_With_Fine-Grained_Feature_Imitation_CVPR_2019_paper.html) | Fitur teacher ditiru pada anchor dekat objek yang dipilih memakai ground-truth box. | Makalah merumuskan loss total sebagai loss deteksi ground-truth ditambah loss imitation; jadi bukan objective teacher-only seperti definisi eksperimen ini. |
| [Banitalebi-Dehkordi (ICCV Workshops 2021), *Knowledge Distillation for Low-Power Object Detection*](https://openaccess.thecvf.com/content/ICCV2021W/LPCV/html/Banitalebi-Dehkordi_Knowledge_Distillation_for_Low-Power_Object_Detection_A_Simple_Technique_and_ICCVW_2021_paper.html) | Tahap pertama memakai pseudo-label teacher dalam loss deteksi student; fine-tuning berlabel dapat menyusul. | Menunjukkan training awal tanpa anotasi asli, tetapi bukan direct teacher-feature/output loss menurut definisi ketat penelitian ini. |
| [Chawla et al. (WACV 2021), *Data-Free Knowledge Distillation for Object Detection*](https://openaccess.thecvf.com/content/WACV2021/html/Chawla_Data-Free_Knowledge_Distillation_for_Object_Detection_WACV_2021_paper.html) | DIODE mensintesis gambar dari detector teacher; student dicocokkan dengan prediksi teacher memakai loss L2. | Preseden distilasi berbasis output teacher tanpa loss ground-truth pada tahap student. Paper memakai teacher dan student YOLOv3 berarsitektur sama untuk transfer data-free, bukan kompresi; studi ini tidak mengklaim objective teacher-only sebagai metode baru. |
| [Dai et al. (CVPR 2021), *General Instance Distillation for Object Detection*](https://openaccess.thecvf.com/content/CVPR2021/html/Dai_General_Instance_Distillation_for_Object_Detection_CVPR_2021_paper.html) | Memilih general instances dari keluaran teacher/student lalu meniru fitur, relasi, dan respons; pemilihan instance tidak membedakan positif/negatif berdasarkan GT. | Menunjukkan ragam sinyal KD deteksi. Pernyataan tentang pemilihan instance tidak dengan sendirinya membuktikan seluruh objective training teacher-only; paper ini tidak dipakai untuk klaim tersebut. |
| [Yang et al. (CVPR 2022), *Focal and Global Knowledge Distillation for Detectors*](https://openaccess.thecvf.com/content/CVPR2022/html/Yang_Focal_and_Global_Knowledge_Distillation_for_Detectors_CVPR_2022_paper.html) | Distilasi fitur lokal dan relasi global; foreground mask dibentuk dari ground-truth box. | Menginformasikan desain feature KD, tetapi pemetaan area berdasarkan GT berbeda dari loss KD di sini yang hanya menggunakan output teacher. |
| [Li et al. (AAAI 2022), *Knowledge Distillation for Object Detection via Rank Mimicking and Prediction-Guided Feature Imitation*](https://ojs.aaai.org/index.php/AAAI/article/view/20018) | Meniru peringkat kandidat prediksi (rank mimicking) dan memandu feature imitation berdasarkan selisih prediksi teacher–student. | PFI tidak memakai GT untuk mempartisi foreground/background, tetapi objective total tetap memuat `Loss_task` bersama loss RM dan PFI (Pers. 10); mekanisme pemilihan fitur yang bebas mask GT tidak menjadikannya teacher-only. |
| [Zhu et al. (CVPR 2023), *ScaleKD: Distilling Scale-Aware Knowledge in Small Object Detector*](https://openaccess.thecvf.com/content/CVPR2023/html/Zhu_ScaleKD_Distilling_Scale-Aware_Knowledge_in_Small_Object_Detector_CVPR_2023_paper.html) | Memisahkan representasi fitur berdasarkan skala dan memakai cross-scale assistant untuk membantu prediksi box student; dievaluasi pada COCO dan VisDrone. | Objective total menambahkan detection loss standar `L_det` pada loss feature, class, dan box distillation (Pers. 7); metode ini relevan untuk small-object detection, tetapi objective totalnya bukan teacher-only. |
| [Wang et al. (CVPR 2024), *CrossKD: Cross-Head Knowledge Distillation for Object Detection*](https://openaccess.thecvf.com/content/CVPR2024/html/Wang_CrossKD_Cross-Head_Knowledge_Distillation_for_Object_Detection_CVPR_2024_paper.html) | Fitur head student dialirkan ke head teacher, lalu prediksi silang dicocokkan dengan prediksi teacher. | Persamaan objective total (Eq. 3) mencakup loss deteksi student terhadap ground truth selain loss CrossKD. Frasa abstrak “only prediction mimicking losses” menjelaskan jenis loss KD yang digunakan, bukan penghapusan objective deteksi supervised; jadi CrossKD bukan contoh objective total teacher-only. |
| [Xu et al. (ACML 2025), *MKD: Multi-Knowledge Distillation for Real-Time Object Detection on Edge Devices*](https://proceedings.mlr.press/v304/xu26b.html) | Menggabungkan distilasi multi-skala, frequency-mask, dan feature-alignment. | Abstrak PMLR menyatakan loss total juga mencakup traditional detection loss; metode ini relevan untuk kompresi edge, tetapi bukan objective teacher-only total. |
| [Sun & Ohyama (WACV 2026), *CanKD: Cross-Attention-based Non-local Operation for Feature-based Knowledge Distillation*](https://openaccess.thecvf.com/content/WACV2026/html/Sun_CanKD_Cross-Attention-based_Non-local_Operation_for_Feature-based_Knowledge_Distillation_WACV_2026_paper.html) | Distilasi fitur melalui operasi cross-attention non-local pada fitur student dan teacher. | Objective totalnya memuat `L_task + μ L_feat` (Pers. 8); loss tugas deteksi tetap digunakan, sehingga bukan teacher-only. |
| [Cheong & An (arXiv v1, 2026), *FD-CanKD*](https://arxiv.org/html/2608.18590) | Distilasi head, transfer fitur cross-attention, dan alignment frekuensi. | Objective total menggabungkan `L_det`, `L_head`, dan `L_fd`; manuskrip ini diperlakukan sebagai arXiv v1 dan status publikasinya perlu dikonfirmasi. |
| [Dokumentasi resmi Ultralytics YOLO11](https://docs.ultralytics.com/models/yolo11/) | Menjelaskan keluarga model dan implementasi YOLO11. | Sumber perangkat lunak, bukan makalah peer-reviewed atau klaim kebaruan metode. |

Posisi penelitian bukan mereplikasi FGFI, FGD, GID, ScaleKD, CrossKD, CanKD, atau FD-CanKD. Objective yang dikunci adalah gabungan feature imitation P3/P4/P5 dan target keluaran teacher untuk box/kelas tanpa loss GT, pseudo-label loss, atau QAT. Audit pustaka terarah untuk membedakan mekanisme KD dari objective total ada di [`TINJAUAN_PUSTAKA_KD_DETEKSI.md`](TINJAUAN_PUSTAKA_KD_DETEKSI.md); audit ini bukan telaah sistematis dan tidak mendukung klaim bahwa “belum ada KD murni untuk deteksi”. Kontribusi yang diajukan adalah evaluasi terapan yang transparan pada model YOLO dan dataset Advance Vision, dibandingkan teacher serta kontrol supervised berarsitektur sama; klaim research gap yang lebih spesifik perlu didukung telaah sistematis dan arahan pembimbing.

Rujukan ini menunjukkan bahwa KD untuk deteksi sudah luas diteliti; karena itu skripsi **tidak** mengklaim algoritma distilasi baru. Kontribusi yang layak diajukan adalah evaluasi empiris yang transparan pada dataset Advance Vision: satu teacher YOLO11n, student YOLO11 yang diperkecil, loss student dari target teacher saja, kontrol supervised dengan arsitektur student sama, seed berpasangan, serta pelaporan akurasi, ukuran, dan latensi. Klaim research gap yang lebih spesifik harus dikonfirmasi melalui telaah pustaka sistematis dan arahan pembimbing sebelum proposal final.

Bibliografi awal untuk gaya sitasi prodi tersimpan di [`REFERENSI_SKRIPSI.bib`](REFERENSI_SKRIPSI.bib). Audit pustaka terarah dan penambahan sumber 2026 dirangkum di [`TINJAUAN_PUSTAKA_KD_DETEKSI.md`](TINJAUAN_PUSTAKA_KD_DETEKSI.md). Format akhir sitasi tetap perlu dicocokkan dengan pedoman kampus.

## Metode yang dijaga tetap murni

- Teacher: checkpoint FP32 YOLO11n yang sudah tersedia, dibekukan selama KD.
- Student: arsitektur YOLO11 lebih kecil, inisialisasi acak; checkpoint terbaik dari run awal dipertahankan sebagai hasil eksplorasi, bukan dianggap sebagai hasil final multi-seed.
- Objective KD: distilasi fitur P3/P4/P5, output box teacher, dan soft output kelas teacher. Konfigurasi awal memakai bobot 1:1:1 dan temperatur kelas 2.
- **Tidak ada** loss deteksi ground-truth dalam update student KD; tidak ada QAT. Label validasi hanya untuk metrik/diagnostik.
- Baseline supervised memakai arsitektur student yang sama, tetapi dilatih dalam run terpisah dengan label train. Ini kontrol eksperimen, bukan bagian dari objective KD.
- Teacher menjadi acuan kualitas atas. Semua model memakai split, resolusi, dan prosedur evaluasi yang sama.

## Eksperimen dan evaluasi

Protokol run final, hash konfigurasi/data, aturan pemilihan checkpoint, dan gerbang TEST dibekukan pada [`PROTOKOL_EKSPERIMEN_SKRIPSI.md`](PROTOKOL_EKSPERIMEN_SKRIPSI.md).

| Kelompok | Tujuan | Catatan |
| --- | --- | --- |
| Teacher FP32 YOLO11n | Acuan kualitas dan biaya | Checkpoint dan hash dicatat |
| Student supervised | Kontrol untuk efek ukuran arsitektur saja | Arsitektur student sama dengan KD; loss label hanya di baseline ini |
| Student pure KD | Metode utama skripsi | Hanya target teacher untuk loss training |

Rencana final dijalankan pada student supervised dan KD dengan **3 seed berpasangan: 42, 1337, 2025**. Semua run dilaporkan. Optimizer, jumlah epoch maksimum, augmentasi, ukuran gambar, dan aturan pemilihan checkpoint disamakan; pengecualian provenance dicatat. Tidak ada pemilihan hyperparameter berdasarkan TEST.

Enam run student telah selesai dan lolos preflight provenance. Pure KD menghasilkan mean TEST mAP50–95 `0,6630 ± 0,0108`, dibandingkan `0,7225 ± 0,0035` untuk supervised student. Selisih berpasangan KD–supervised adalah `−0,0595 ± 0,0138`, sehingga hipotesis kerja bahwa KD mengungguli kontrol supervised tidak didukung. Student KD memiliki parameter `68,71%` lebih sedikit, checkpoint `65,20%` lebih kecil, dan FLOPs `62,64%` lebih rendah daripada teacher. Pengurangan biaya model tersebut berasal dari arsitektur student yang lebih kecil: parameter dan GFLOPs student KD identik dengan baseline supervised. Mean latensi median pada NVIDIA L40 adalah `25,01 ms` untuk KD, `25,00 ms` untuk supervised, dan `25,72 ms` untuk teacher. Draf hasil dan keterbatasan ada di [`DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`](DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md), sedangkan tabel final yang memakai hitungan parameter checkpoint ada di [`artifacts/thesis_analysis_final_corrected/`](artifacts/thesis_analysis_final_corrected/).

Laporkan precision, recall, mAP50, mAP50–95, metrik per kelas, selisih per kelas terhadap teacher, selisih KD–baseline berpasangan per seed, jumlah parameter, ukuran checkpoint, FLOPs, latensi dan throughput pada perangkat yang dinyatakan jelas. Laporkan mean ± simpangan baku antar-seed serta interval bootstrap persentil 95% pada tingkat gambar (1.000 replikasi, seed 20261009); interval keseluruhan hanya memakai replikasi yang memuat seluruh kelas agar penyebut macro tetap, sementara interval per kelas menyertakan jumlah replikasi valid. Manifest mencatat aturan ini dan generator analisis memverifikasinya. Bootstrap bersyarat pada checkpoint: ia mengukur variasi sampling gambar dan tidak menggantikan variasi antar-seed atau generalisasi ke adegan baru. Script [`scripts/benchmark_inference.py`](scripts/benchmark_inference.py) mengukur inference YOLO end-to-end pada satu frame VAL tetap, dengan warm-up, batch 1, FP32, dan perangkat yang sama; manifest menyimpan semua 200 sampel latensi mentah per model. Hasil L40/CPU adalah diagnostik host; klaim deployment perlu diuji langsung di perangkat robot.

## Keputusan protokol dan tata kelola data

1. Audit datasheet dan split selesai: lisensi, kelas, jumlah objek, label kosong/rusak, fingerprint file, dan risiko kemiripan lintas-split dirangkum di [`AUDIT_DATASET_SKRIPSI.md`](AUDIT_DATASET_SKRIPSI.md).
2. **Split yang dipakai:** Roboflow v1 resmi, dikonfirmasi peneliti pada 9 Oktober 2026 karena lebih hemat dan paling sebanding secara praktis dengan teacher yang tersedia. Split mencakup 4.600/1.213/592 gambar TRAIN/VAL/TEST. TEST juga pernah dipakai untuk evaluasi historis FP32 dan QAT pada 24 September 2026; student baru dipilih dari VAL dan evaluasi finalnya dilakukan setelah checkpoint terkunci.
3. Setelah suffix Roboflow `.rf.<hash>` dihapus, ada 326 nama sumber bersama TRAIN–VAL, 176 TRAIN–TEST, dan 155 VAL–TEST. Pemeriksaan piksel tidak menemukan pasangan identik pada pasangan bernama dasar sama, tetapi inspeksi visual menemukan beberapa frame/adegan serupa. Ini adalah risiko kemiripan, bukan bukti semua pasangan duplikat. Klaim dibatasi pada generalisasi level-gambar, bukan sesi atau adegan baru.
4. Versi dataset yang dilihat teacher lama tidak tercatat (`dataset_version=null`) dan YAML training-nya tidak tersedia. Kesamaan byte TRAIN/VAL teacher dengan export v1 tidak dapat diverifikasi; keterbatasan ini dicatat dalam proposal, hasil, dan draf abstrak.
5. Hash data, checkpoint, manifest, dan hasil per-run diarsipkan. TEST final tidak digunakan untuk tuning atau pemilihan checkpoint; setelah melihat hasil TEST, model tidak diubah.

## Status akhir eksperimen (diperbarui 2026-10-10)

- Queue training berstatus `complete`; seluruh enam run pure KD/supervised selesai dengan seed 42, 1337, dan 2025. Semua `best.pt` dipilih melalui VAL dan manifest keenam student mencatat `test_split_used=false`; manifest KD mencatat `train_labels_used_for_loss=false`.
- Evaluasi locked TEST selesai pada 592 gambar dan 734 anotasi untuk keenam student serta teacher. Evaluasi awal yang berjalan di GPU berhenti pada batch pertama karena validator mencoba menghitung loss; label TEST sempat dipindai, tetapi tidak ada metrik model tersimpan. Retry inference-only memakai direktori baru dan menghubungkan manifest percobaan awal melalui hash.
- Benchmark selesai pada NVIDIA L40, FP32, batch 1, resolusi 640, warm-up 30 iterasi dan 200 iterasi terukur. Pipeline mencatat ketiga tahap (`locked_test_evaluation`, `inference_benchmark`, `thesis_analysis`) sebagai `complete`.
- Audit lanjutan menemukan jumlah parameter validator setelah fusi Conv-BN berbeda dari jumlah parameter checkpoint. Tabel final memakai hitungan checkpoint dari benchmark yang cocok dengan manifest training; hitungan pascafusi dipertahankan terpisah sebagai diagnostik. Folder analisis pertama tetap tersimpan sebagai jejak audit; gunakan folder `thesis_analysis_final_corrected` untuk hasil final.

## Arsip riwayat training

Pembaruan progres saat training berlangsung dipertahankan sebagai arsip historis di [`artifacts/training_status_history_2026-10-09.md`](artifacts/training_status_history_2026-10-09.md). Gunakan bagian **Status akhir eksperimen** di atas untuk status terkini.

## Tahapan dan status kerja

| Tahap | Status | Hasil / pekerjaan tersisa |
| --- | --- | --- |
| 1. Topik dan pertanyaan | Draf siap | Judul kerja, rumusan masalah, objective KD, baseline, dan batas klaim tertulis; persetujuan judul formal masih menunggu pembimbing. |
| 2. Dataset dan literatur | Audit terarah selesai | Datasheet dan audit dataset selesai. Peta objective KD ditulis di [`TINJAUAN_PUSTAKA_KD_DETEKSI.md`](TINJAUAN_PUSTAKA_KD_DETEKSI.md), tetapi bukan systematic review; tidak ada klaim “metode pertama”. |
| 3. Protokol | Selesai dan dibekukan | Teacher/student, objective, seed, metrik, perangkat, pilihan split, aturan VAL/TEST, serta keterbatasan provenance didokumentasikan di [`PROTOKOL_EKSPERIMEN_SKRIPSI.md`](PROTOKOL_EKSPERIMEN_SKRIPSI.md). |
| 4. Eksperimen final | Selesai | Enam student pada tiga pasangan seed, evaluasi TEST terkunci, benchmark NVIDIA L40, dan generator analisis telah selesai. |
| 5. Analisis | Selesai | Tabel terkoreksi ada di [`artifacts/thesis_analysis_final_corrected/`](artifacts/thesis_analysis_final_corrected/); draf hasil dan pembahasan menyatakan hipotesis tidak didukung. |
| 6. Penulisan skripsi | Berjalan | Draf abstrak, Bab I–III, dan Bab IV–V tersedia; audit pustaka menjadi bahan Bab II. Selanjutnya perlu diselaraskan dengan pedoman kampus dan revisi pembimbing. |
| 7. Persiapan sidang | Belum dimulai | Buat slide dan demonstrasi hanya bila format/ketentuan prodi meminta; jawaban harus mengikuti hasil terkunci. |

## Jadwal sisa pekerjaan

Eksperimen dan analisis sudah selesai, sehingga jadwal run GPU yang lama tidak lagi berlaku. Tenggat akademik belum tersedia; sisa pekerjaan disusun berdasarkan dependensi, bukan perkiraan minggu.

| Urutan | Fokus | Keluaran |
| --- | --- | --- |
| 1 | Cocokkan format, sistematika, gaya sitasi, dan batas panjang dengan pedoman prodi. | Naskah dalam format kampus. |
| 2 | Minta masukan pembimbing untuk framing studi evaluasi, objective ketat teacher-only, serta keterbatasan split dan provenance teacher. | Revisi isi dan judul final. |
| 3 | Lengkapi lampiran yang diwajibkan: konfigurasi, hash, manifest, skrip, dan prosedur reproduksi. | Paket lampiran yang dapat ditelusuri. |
| 4 | Periksa konsistensi seluruh angka, tabel, sitasi, dan abstrak terhadap manifest/CSV final. | Naskah final yang konsisten dengan data eksperimen. |
| 5 | Siapkan materi sidang sesuai instruksi prodi. | Slide dan demonstrasi jika diminta. |

### Catatan durasi komputasi

Semua run telah selesai. Durasi final per-run tersedia pada manifest dan log training masing-masing; estimasi “4,4 jam tersisa” dari catatan historis sebelum queue selesai tidak lagi berlaku.

## Hal yang perlu disepakati saat revisi akademik

- Cocokkan judul kerja, struktur bab, gaya sitasi, dan panjang abstrak dengan pedoman kampus.
- Tinjau keputusan split resmi Roboflow v1, keterbatasan kemiripan sumber/adegan, serta provenance teacher yang tidak lengkap. Jika dosen meminta generalisasi sesi baru atau provenance byte-level yang lengkap, perlukan eksperimen terpisah dengan group-held-out split dan teacher yang dilatih ulang; hasil saat ini tetap dilaporkan apa adanya.
- Pertahankan posisi kontribusi sebagai evaluasi terapan, bukan metode KD baru. Audit pustaka yang ada bersifat terarah dan tidak mendukung klaim novelty yang menyeluruh.
- Klaim real-time atau deployment hanya dapat dibuat setelah benchmark pada perangkat sasaran; eksperimen sekarang mengukur NVIDIA L40 sebagai host.

## Batasan yang perlu dinyatakan

Kesimpulan utama berlaku untuk split resmi level-gambar, tiga kelas, teacher, student, dan konfigurasi yang diuji. Kemiripan nama sumber/adegan, provenance data teacher yang tidak lengkap, tiga pasangan seed, dan benchmark satu host membatasi inferensi. Hasil tidak membuktikan generalisasi pada sesi baru atau kesiapan real-time pada perangkat robot.
