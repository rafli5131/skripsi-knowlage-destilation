# Indeks dokumentasi percobaan OP3

Dokumentasi percobaan disimpan menurut tanggal, lalu nomor dan kondisi percobaan. Setiap folder berisi ringkasan, grafik performa, dan tautan ke CSV serta metadata JSON.

## 2026-10-19

- [Percobaan 01 — kondisi tidak terverifikasi](2026-10-19/percobaan-01-kondisi-tidak-terverifikasi/README.md). Log awal memakai label `servo_idle`, tetapi kondisi aktual kemudian dilaporkan berbeda.
- [Percobaan 02 — kamera, kondisi unknown](2026-10-19/percobaan-02-kamera-unknown/README.md). 512 frame, 0 deteksi objek.
- [Percobaan 03 — label servo_idle](2026-10-19/percobaan-03-servo-idle/README.md). 887 frame, 887 instance deteksi tercatat, 0 error pemrosesan. Label idle berasal dari operator; tidak ada perintah gerak yang dikirim.

Label kondisi dicatat sebagai masukan operator. Node deteksi tidak membaca telemetry gerak dan bukan pengenal aksi berjalan.
