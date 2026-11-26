# Percobaan video KD Murni berjalan — terhenti pengaman

Pada 26 November 2026 sekitar 18.36 WIB operator mengonfirmasi robot siap, area kosong, dan pendampingan. Preview KD Murni aktif. Pengendali memberi ack start gait, tetapi pengaman mengirim stop sekitar **0,99 detik setelah ack** karena pembacaan kepala mencapai tiga count dari acuan; ack stop diterima. Guard tidak mengirim perintah posisi kepala. Perbedaan pembacaan ini tidak memastikan penyebab gerakan fisiknya.

Recorder tetap selesai selama 10 detik karena berjalan terpisah. Oleh karena itu `video/preview_deteksi_langsung.mp4` **bukan video 10 detik berjalan**: sebagian besar periode setelah perintah stop. Video memuat 100 frame pada 10 fps (640×480), termasuk 9 frame yang mengulang hasil inferensi. `screenshot_awal.png` dan `screenshot_setelah_stop.png` adalah cuplikan; bukan audit seluruh frame.

`guard/gait_guard.json`, `guard/head_samples.csv`, dan `guard/pasca_stop.json` memuat kejadian dan telemetry; pengukuran lima detik setelah stop menunjukkan rentang kaki kecil, tetapi bukan jaminan tidak ada gerakan. `video/recording_stats.json`, `video/ffmpeg.log`, dan `manifest.json` memuat status recorder dan metadata. Kejadian ini disimpan sebagai percobaan terhenti, tidak menggantikan hasil sebelumnya. Tidak ada gait lanjutan tanpa konfirmasi baru dari operator. Video dan data tersimpan lokal.

Setelah stop, operator menyatakan robot stabil dan arah kamera sesuai. Pemeriksaan baca-saja 10 detik mencatat 626 sampel: perubahan maksimum dari acuan masing-masing satu count untuk pan dan tilt; modul kepala tetap `none`, dan modul kaki `walking_module`. Laporan ada di `guard/audit_lanjutan_diam.json`. Kondisi ini tidak menentukan penyebab simpangan tiga count saat gait dan tidak mengubah batas pengaman.
