# Audit Pustaka Terarah: Knowledge Distillation untuk Deteksi Objek

**Batas waktu audit:** 10 Oktober 2026  
**Status:** peta pustaka terarah, bukan systematic review atau telaah PRISMA.

## Tujuan dan definisi kerja

Audit ini membantu menetapkan batas istilah *pure teacher-only KD* dan mencegah klaim kebaruan yang lebih luas daripada bukti. Fokusnya adalah objective yang memperbarui student pada deteksi objek. Metode digolongkan berdasarkan sumber seluruh loss student, bukan hanya nama atau mekanisme komponen distilasinya.

Untuk studi ini, KD disebut **pure teacher-only** jika setiap loss yang memperbarui student dibentuk dari fitur atau keluaran teacher yang dibekukan. Label TRAIN tidak dipakai di loss, tidak dipakai untuk memilih lokasi distilasi, tidak ada loss deteksi berbasis ground truth, dan tidak ada pseudo-label loss. Loss supervised pada student kontrol merupakan kelompok eksperimen terpisah. Definisi ini sengaja lebih ketat daripada istilah “tanpa anotasi ground-truth”: pseudo-label dari teacher tetap dikecualikan jika diperlakukan sebagai target loss deteksi.

## Cara pencarian dan batasnya

Pencarian terarah dilakukan pada halaman primer CVF Open Access, PMLR, AAAI OJS, dan arXiv; laman resmi dipakai untuk memeriksa judul, venue, abstrak, persamaan objective, dan tanggal naskah. Kata kunci mencakup `object detection knowledge distillation`, `teacher-only`, `data-free`, `pseudo-label`, `task loss`, serta judul dan istilah `overall loss` atau `objective`. Untuk dua metode 2026, objective diperiksa pada naskah arXiv CanKD (versi yang juga terbit di WACV 2026) dan HTML arXiv FD-CanKD. Audit tidak menetapkan basis data menyeluruh, prosedur deduplikasi, hitungan screening, maupun penilaian risiko bias; karena itu audit ini tidak dapat diperlakukan sebagai systematic review dan tidak membuktikan ketiadaan metode lain.

## Matriks bukti objective

| Studi primer | Loss/sinyal yang memperbarui student menurut sumber | Penggunaan label | Hubungan dengan definisi studi |
| --- | --- | --- | --- |
| [Fine-Grained Feature Imitation, CVPR 2019](https://openaccess.thecvf.com/content_CVPR_2019/html/Wang_Distilling_Object_Detectors_With_Fine-Grained_Feature_Imitation_CVPR_2019_paper.html) | Loss deteksi dan feature imitation. | Ground-truth box membantu memilih anchor/area imitation. | Bukan teacher-only. |
| [DIODE, WACV 2021](https://openaccess.thecvf.com/content/WACV2021/html/Chawla_Data-Free_Knowledge_Distillation_for_Object_Detection_WACV_2021_paper.html) | Student meniru prediksi teacher dengan loss L2 pada data sintetis yang dihasilkan dari detector. | Tidak memakai label ground-truth pada update student di tahap distilasi yang dilaporkan. | Preseden langsung untuk distilasi output teacher tanpa loss GT. Fokusnya transfer data-free dengan YOLOv3, bukan studi kompresi YOLO11 Advance Vision. Karena itu penelitian ini tidak mengklaim KD teacher-only sebagai ide baru. |
| [Banitalebi-Dehkordi, ICCV Workshops 2021](https://openaccess.thecvf.com/content/ICCV2021W/LPCV/html/Banitalebi-Dehkordi_Knowledge_Distillation_for_Low-Power_Object_Detection_A_Simple_Technique_and_ICCVW_2021_paper.html) | Tahap awal memakai pseudo-label teacher dalam loss deteksi student; fine-tuning berlabel tersedia sebagai tahap lanjutan. | Tidak memakai anotasi asli pada tahap pseudo-label, tetapi pseudo-label dipakai sebagai target loss deteksi. | Menunjukkan training student tanpa label asli dapat dilakukan, tetapi tidak sama dengan definisi ketat direct teacher-feature/output loss penelitian ini. |
| [Focal and Global Distillation, CVPR 2022](https://openaccess.thecvf.com/content/CVPR2022/html/Yang_Focal_and_Global_Knowledge_Distillation_for_Detectors_CVPR_2022_paper.html) | Distilasi fitur fokal dan relasi global. | Ground-truth box dipakai membentuk mask foreground untuk mekanisme distilasi. | Tidak memenuhi kriteria label-free pada penelitian ini. |
| [General Instance Distillation, CVPR 2021](https://openaccess.thecvf.com/content/CVPR2021/html/Dai_General_Instance_Distillation_for_Object_Detection_CVPR_2021_paper.html) | Memindahkan fitur, relasi, dan respons pada instance terpilih. | Pernyataan paper bahwa seleksi instance tidak memisahkan positif/negatif berdasarkan GT hanya menjelaskan seleksi; itu belum membuktikan seluruh objective bebas GT. | Tidak dipakai sebagai bukti preseden pure teacher-only tanpa verifikasi objective total. |
| [Rank Mimicking dan Prediction-Guided Feature Imitation, AAAI 2022](https://ojs.aaai.org/index.php/AAAI/article/view/20018) | Rank mimicking dan prediction-guided feature imitation. | Objective total menambahkan `Loss_task` pada RM dan PFI (Pers. 10). | Bukan teacher-only walau PFI tidak memakai GT untuk membentuk foreground/background. |
| [ScaleKD, CVPR 2023](https://openaccess.thecvf.com/content/CVPR2023/html/Zhu_ScaleKD_Distilling_Scale-Aware_Knowledge_in_Small_Object_Detector_CVPR_2023_paper.html) | Distilasi fitur, kelas, dan box lintas skala. | Objective total memuat detection loss `L_det` (Pers. 7). | Bukan teacher-only. |
| [CrossKD, CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Wang_CrossKD_Cross-Head_Knowledge_Distillation_for_Object_Detection_CVPR_2024_paper.html) | Cross-head prediction imitation terhadap prediksi teacher. | Objective total mencakup loss deteksi student terhadap ground truth (Pers. 3). | Bukan teacher-only; “prediction mimicking” menerangkan komponen KD, bukan objective total. |
| [MKD, PMLR/ACML 2025](https://proceedings.mlr.press/v304/xu26b.html) | Distilasi multi-knowledge untuk deteksi real-time. | Abstrak PMLR menyatakan total loss menggabungkan distilasi dengan traditional detection loss. | Bukan teacher-only. |
| [CanKD, WACV 2026](https://openaccess.thecvf.com/content/WACV2026/html/Sun_CanKD_Cross-Attention-based_Non-local_Operation_for_Feature-based_Knowledge_Distillation_WACV_2026_paper.html) | Feature distillation memakai cross-attention non-local antara fitur student dan teacher. | Objective total adalah `L_student = L_task + μ L_feat` (arXiv naskah, Pers. 8); loss tugas deteksi tetap ada. | Metode fitur yang relevan untuk konteks mutakhir, tetapi bukan teacher-only. |
| [FD-CanKD, arXiv:2608.18590 v1 (19 Agustus 2026)](https://arxiv.org/html/2608.18590) | Distilasi keluaran head, transfer fitur cross-attention, dan alignment fitur berbasis frekuensi. | Objective bagian 3.6 menggabungkan `L_det` dengan `L_head` dan `L_fd`; Algoritme 1 menghitung `YOLOLoss(O_S,Y)`. | Bukan teacher-only. Diperlakukan sebagai manuskrip arXiv v1; status publikasi perlu dikonfirmasi lagi sebelum naskah akhir. |
| Penelitian ini | Score-weighted feature L2 P3/P4/P5, Smooth L1 box-logit, dan soft class-logit dari teacher. | Label TRAIN tidak masuk ke loss KD maupun pemilihan lokasi KD; label dipakai hanya pada kontrol supervised dan evaluasi VAL/TEST sesuai protokol. | Memenuhi definisi operasional pure teacher-only yang ditetapkan di atas. |

## Implikasi untuk posisi skripsi

1. Bukti yang diperiksa menunjukkan objective distilasi deteksi beragam. Ada preseden langsung transfer output teacher tanpa loss GT seperti DIODE; ada pula training awal berbasis pseudo-label teacher yang bukan bentuk loss direct teacher-target yang digunakan di sini.
2. Banyak metode deteksi mutakhir menggabungkan KD dengan detection/task loss. Mekanisme KD teacher-based saja tidak cukup untuk menyimpulkan bahwa objective total bebas label.
3. Studi ini sebaiknya diposisikan sebagai evaluasi kompresi terapan yang transparan pada student YOLO lebih kecil, dibanding teacher dan kontrol supervised berarsitektur sama. Jangan mengklaim “metode KD murni pertama” atau “belum ada KD murni untuk deteksi” berdasarkan audit terbatas ini.
4. Hasil eksperimen menunjukkan hipotesis bahwa KD mengungguli kontrol supervised tidak didukung oleh mAP50–95 TEST. Bab pembahasan perlu mempertahankan hasil tersebut dan membahasnya sebagai temuan, bukan mengubah framing agar tampak berhasil.

## Rujukan primer tambahan

Informasi bibliografi CanKD dan FD-CanKD ditambahkan ke [`REFERENSI_SKRIPSI.bib`](REFERENSI_SKRIPSI.bib). Untuk CanKD, versi WACV 2026 menjadi sitasi venue; halaman HTML arXiv dipakai untuk memeriksa Persamaan 8. FD-CanKD disitasi sebagai arXiv v1, bukan sebagai publikasi peer-reviewed yang statusnya telah dipastikan.
