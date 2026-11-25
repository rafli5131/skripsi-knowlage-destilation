# Guard video berjalan OP3

Package baru ini memakai guard `op3_equal_live_walk` dan recorder `op3_fullscreen_preview` sebagai komponen bersama. Preview khusus menunggu sinyal SIGUSR1 untuk mulai merekam; guard hanya mengirim sinyal itu setelah operator mengonfirmasi gait dan ada ack `Start walking`. Akhiri gait setelah rekaman, atau segera saat head melebihi dua encoder count, telemetry putus, preview berhenti, atau terjadi error. Tidak ada perintah pose kepala. Kegagalan ack stop dicatat dan perintah stop dikirim ulang.

Konversi kepala mengikuti XM430-W350 dengan 2048 sebagai nol, 4095 maksimum, dan 0 minimum. Dua count adalah batas, bukan jaminan bahwa kepala sama sekali tidak bergerak. Status fisik tetap harus diperiksa operator sebelum gait; sistem tidak bisa menjamin stop segera pada semua kegagalan mekanis. Recording 10 detik adalah output deteksi beranotasi, bukan screen record X11 dan bukan benchmark.

Sebelum menjalankan di robot, verifikasi terlebih dahulu telemetry kepala, offset nol, modul kepala `none`, modul kaki `walking_module`, pose, area, dan kesiapan operator. Jangan jalankan gait tanpa konfirmasi mulai yang baru. Pastikan ID proses dan direktori recorder yang disiapkan sesuai; jangan gunakan manager secara bersamaan dengan pembacaan langsung port servo.
