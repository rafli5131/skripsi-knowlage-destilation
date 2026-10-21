# Percobaan 02 — kandidat 60 frame tanpa objek target

**Tanggal:** 21 Oktober 2026, sekitar 14:09–14:14 WIB. **Commit runtime:** `0c14591`. Operator menyatakan bidang pandang telah dikosongkan, lalu setelah temuan objek tepi menyatakan benda itu telah disingkirkan sebelum rekaman pengganti. Kondisi servo untuk sesi ini **tidak diverifikasi** dan dicatat `unknown`; agen tidak mengirim perintah servo, gait, atau motor.

Satu publisher `usb_cam` membuka Logitech C920 `/dev/video0` pada 640×480 dan menerbitkan `/thesis/image_raw`. Detektor KD FP32 CPU (`models/weights/kd_student_best.pt`, SHA-256 `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3`) menerbitkan `/vision/debug_image`; jendela SSH-X `OP3 live detection` terverifikasi terbuka dan berlangganan topic itu. Detektor tidak mengendalikan robot. Perekam membaca `/thesis/image_raw` yang sama, bukan gambar dengan kotak. `run_id=20261021_empty_01_live`, kondisi log `unknown`.

| Rekaman | Jumlah | Status | Catatan |
| --- | ---: | --- | --- |
| [Sesi awal](../../../data/op3_camera_eval/sessions/20261021_empty_01/capture_manifest.json) | 60/60 JPEG | `max_frames_reached` | Durasi antar-frame pertama–terakhir 139,01 detik; jeda terpanjang 8,26 detik. |
| [Sesi pengganti](../../../data/op3_camera_eval/sessions/20261021_empty_replacement_01/capture_manifest.json) | 12/12 JPEG | `max_frames_reached` | Durasi 29,24 detik; jeda terpanjang 8,41 detik. |
| [Kandidat negatif terkurasi](../../../data/op3_camera_eval/sessions/20261021_negative_candidate_01/curation_manifest.json) | **60 JPEG** | **60/60 ditinjau `bhre`** | 52 gambar sesi awal + 8 gambar pengganti; gambar sumber tidak dihapus. |

Kontak visual seluruh kandidat: [frame 1–30](../../../data/op3_camera_eval/sessions/20261021_negative_candidate_01/contact_sheet_1.jpg) dan [frame 31–60](../../../data/op3_camera_eval/sessions/20261021_negative_candidate_01/contact_sheet_2.jpg). Semua JPEG berukuran 640×480 dan hash masing-masing cocok dengan manifest kurasi. Selama kedua jendela waktu capture, CSV live mencatat **0 baris deteksi**; ini pemeriksaan output model, **bukan** bukti bahwa setiap frame bebas target. Publisher kamera sempat mengalami jeda; detektor melaporkan tidak menerima gambar selama lebih dari 5 detik. Angka FPS/latensi dari sesi bersamaan ini bukan benchmark performa.

Dalam pemeriksaan lembar kontak dan frame resolusi penuh, **frame 20–21 pada sesi awal menampilkan gawang di tepi**. Frame **34–39** menampilkan benda putih di tepi yang statusnya tidak pasti, sehingga juga dikeluarkan secara konservatif. Delapan JPEG itu tetap berada di sesi awal untuk audit dan **tidak** masuk set kandidat negatif. Delapan frame pengganti dipilih dari sesi pengganti yang memperlihatkan latar tanpa target pada pemeriksaan lembar kontak. [Manifest kurasi](../../../data/op3_camera_eval/sessions/20261021_negative_candidate_01/curation_manifest.json) mencatat pemetaan nama dan hash sumber ke setiap kandidat.

Seluruh **60 JPEG telah ditinjau** oleh `bhre` pada resolusi penuh dan disimpan sebagai label kosong. Audit serta perbandingan deteksi palsu KD dan supervised dicatat pada [percobaan 12](../percobaan-12-peninjauan-60-frame-negatif/README.md). Gambar, log, dan lembar kontak tetap lokal dan tidak untuk di-push ke GitHub.
