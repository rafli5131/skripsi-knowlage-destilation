# Percobaan 24 — uji ulang model supervised pada OP3

Model yang digunakan adalah `supervised_seed1337`. Dokumentasi disusun per sesi agar status idle, berjalan, dan tracking tidak tercampur.

| Sesi | Status | Dokumentasi |
|---|---|---|
| Servo idle | Selesai | [Hasil idle](01-servo-idle/README_ID.md) |
| Robot berjalan/terbeban | Ditunda | Startup `op3_manager` standar mengaktifkan torque semua servo terdaftar, termasuk ID 19/20. Belum ada jalur gait yang mempertahankan keduanya. |
| Tracking live (adegan statis) | Selesai, gerak target belum tervalidasi | [Hasil tracking](03-tracking/README_ID.md) |

Untuk sesi idle dan tracking, preview SSH-X aktif. Preflight baca-saja sebelum/sesudah tracking mencatat ID 19/20 tetap torque-off dan goal position tidak berubah; posisi aktual ID20 berbeda 1 count pada pembacaan akhir. Detektor tidak mengirim perintah servo, posisi, atau gait. Uji berjalan ditunda agar syarat kamera tetap tidak dilanggar.

Hasil runtime dan frekuensi keluaran model bukan metrik akurasi kamera. Klaim precision/recall/mAP OP3 memerlukan ground truth yang ditinjau manusia pada gambar uji yang sama.
