# Video deteksi Supervised — kondisi diam

Direkam 25 November 2026 pukul 21.26 WIB setelah operator menyatakan objek terdeteksi dan meminta mulai. Kondisi dicatat sebagai diam berdasarkan rangkaian sesi; status gait dan torque tidak diverifikasi ulang saat rekaman. Tidak ada perintah servo atau gait yang dikirim untuk sesi ini.

- `preview_deteksi_langsung.mp4`: keluaran deteksi Supervised seed 1337, 10 detik, 640×480, 100 frame dan 10 fps dalam berkas. Recorder melaporkan sembilan frame mengulang hasil inferensi sebelumnya.
- `screenshot_awal.png`, `screenshot_tengah.png`, `screenshot_akhir.png`: cuplikan pada detik 2, 5, dan 8. Pada ketiganya bola, gawang parsial, dan robot terdeteksi. Gawang dan robot terlihat sebagian di tepi gambar; teks confidence bola kurang jelas karena melampaui latar label.
- `recording_stats.json`, `ffmpeg.log`, dan `manifest.json`: status perekaman, log dan metadata/hash.

Ini rekaman langsung keluaran preview beranotasi, bukan screen record desktop atau benchmark. Confidence bukan akurasi; semua frame belum diaudit. Video dan gambar tersedia dalam repositori.
