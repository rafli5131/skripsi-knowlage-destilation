# Uji rekaman langsung preview deteksi KD Hybrid

Pada 25 November 2026 pukul 20.44 WIB, operator mengonfirmasi mulai merekam dalam kondisi diam. Status torque tidak diverifikasi; tidak ada perintah servo atau gerak.

`preview_deteksi_langsung.mp4` adalah rekaman **keluaran preview beranotasi** dari model KD Hybrid full seed 1337, bukan screen record desktop. Menggunakan topic `/thesis/image_raw`, satu proses inferensi yang sama dengan preview, tanpa merekam panel grafik. Cuplikan `screenshot_preview.png` menampilkan deteksi bola, gawang parsial, dan robot; tidak semua frame diaudit.

Video terverifikasi 640×480, 10 detik, 100 frame pada 10 fps. Pencatat melaporkan 11 frame mengulang hasil inferensi sebelumnya; durasi hingga finalisasi 10,016 detik. FPS berkas tidak sama dengan FPS inferensi. Sebagai pembanding terbatas, perekaman jendela melalui SSH-X sebelumnya dalam kondisi lain mencapai rata-rata 2,65 fps; ini bukan benchmark setara.

`recording_stats.json` memuat hitungan dan status, `manifest.json` menyimpan metadata dan hash, dan `ffmpeg.log` adalah log encoder. Video dan gambar tetap lokal. Confidence bukan akurasi; sesi ini tidak menghasilkan mAP atau metrik pengujian skripsi.
