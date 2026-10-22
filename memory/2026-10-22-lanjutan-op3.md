# Memori proyek — 22 Oktober 2026: transisi dari lab/server ke uji OP3

Catatan ini melanjutkan [memori eksperimen KD Hybrid](2026-10-22-kd-hybrid.md). Sumber angka utama adalah manifest dan [laporan TEST Hybrid](../analisis_performa/lab_server/HASIL_KD_HYBRID_TEST_2026-10-22.md), bukan catatan ini.

## Yang sudah selesai

- KD Hybrid full dan kontrol supervised masing-masing selesai dilatih pada seed 42, 1337, dan 2025 dengan split Advance Vision yang sama. Teacher dibekukan; student adalah YOLO11 skala `t` kustom, **bukan YOLO11n standar**.
- Evaluasi VAL, TEST lanjutan, benchmark L40, tabel T28–T33, dan laporan lab/server sudah selesai. Pada TEST resmi 592 gambar, rerata mAP50–95 Hybrid **0,7469 ± 0,0022** dan supervised **0,7225 ± 0,0035**; selisih berpasangan **+0,0244 ± 0,0040**. F1 makro pada confidence 0,25 adalah **0,9071 ± 0,0017** vs **0,9121 ± 0,0026**. Kelas `gawang` perlu diperhatikan saat uji robot.
- Hybrid seed **1337** dipilih sebagai kandidat tunggal OP3 berdasarkan VAL sebelum melihat TEST Hybrid. Hasil TEST tidak dipakai untuk mengganti pilihan model atau ambang.
- `best.pt` Hybrid seed 1337 dan 2025 dipublikasikan ke repo GitHub publik setelah izin pengguna, commit `95bf789`. Dokumentasi dan manifest diselaraskan pada commit `35ba3eb`; kedua commit itu sudah ter-push. Bobot kandidat: [`runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt`](../runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt), SHA-256 `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`.
- `op3_default` pada [`configs/model_registry.yaml`](../configs/model_registry.yaml) masih menunjuk KD murni seed 42. Checkpoint aktif robot **belum diganti**, dan Hybrid seed 1337 **belum diuji pada OP3**. Benchmark L40 tidak boleh disebut FPS robot.

## Temuan persiapan uji robot

- Audit setelah prompt pertama dibuat menemukan bahwa [`scripts/model_registry.py`](../scripts/model_registry.py) dan [`scripts/op3_pytorch_detector.py`](../scripts/op3_pytorch_detector.py) belum menerima varian `hybrid`. Pemetaan `hybrid` → `hybrid_full_seed1337` dan pemeriksaan prefiks `hybrid_full_` kemudian ditambahkan. Alias `op3_default` tetap KD murni. Checkout robot harus memuat pembaruan ini sebelum uji Hybrid.
- Prompt kamera lama memakai `models/weights/kd_student_best.pt` dan cocok untuk KD murni, sehingga uji Hybrid menggunakan [prompt baru khusus OP3](../prompt/PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3.md). Prompt baru mengharuskan hash checkpoint, kelas `ball/gawang/robot`, versi runtime, topic kamera, dan kondisi robot diverifikasi.
- `scripts/capture_op3_frames.py` menyimpan gambar mentah di `data/op3_camera_eval/sessions/<session_id>/images/`. `scripts/prelabel_op3_frames.py` membuat draf di `labels_auto/`; hasilnya **bukan** ground truth. Semua frame, termasuk frame kosong, harus ditinjau manusia menjadi `labels_reviewed/` sebelum menghitung mAP/P/R/F1 kamera OP3.

## Langkah berikutnya

1. Tarik checkout terbaru pada komputer OP3; periksa bahwa runtime menerima `model_variant:=hybrid`, dependensi ROS 2 Jazzy tersedia, dan hash checkpoint Hybrid seed 1337 cocok dengan registry. Model bawaan `op3_default` tidak perlu diganti.
2. Jalankan sesi fungsi kamera dan tracking saat `servo_idle` sambil memantau serta merekam frame mentah. Agen tidak memberi perintah servo/gait; kondisi fisik ditentukan operator. Jalankan sesi `walking` terpisah ketika operator siap. Log sesi monitor + capture adalah observasi, bukan benchmark performa.
3. Buat sesi runtime bersih dengan preview/capture mati dan pengaturan sama per model/kondisi; simpan latensi, FPS frame terproses, CPU, RAM, serta data deteksi/track. Untuk perbandingan kausal distilasi, bandingkan Hybrid seed 1337 dengan supervised seed 1337 pada protokol yang sama.
4. Pra-label setelah capture selesai, tinjau manual seluruh frame, lalu evaluasi model pada gambar OP3 yang **sama** dan label final yang sama. Isi T15–T27 hanya dari bukti robot yang memenuhi syarat; status lain tetap `[BELUM DIUKUR]`.
5. Pisahkan angka TEST Advance Vision dari angka kamera OP3 di skripsi. Split TEST Advance Vision sudah pernah dipakai untuk teacher dan KD murni; klaim hasilnya dibatasi pada gambar dataset resmi.

Data kamera, gambar, label, dan log robot tidak dipush otomatis ke GitHub. Publikasi atau transfer artefak robot dilakukan hanya melalui prosedur yang disetujui operator.
