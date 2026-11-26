# Video KD Murni kondisi diam, servo disiapkan

Pada 26 November 2026 pukul 18.31 WIB operator meminta merekam setelah mengonfirmasi pose siap, stabil, dan arah kamera sesuai. Tidak ada perintah start gait pada sesi ini. Manager mengirim torque-on saat inisialisasi; status torque per servo tidak dibaca ulang ketika manager menguasai bus. Persiapan dan batas pembacaan kepala dicatat di [dokumentasi persiapan](../persiapan-kd-murni-siap-jalan-gb6cu55v/README.md).

- `preview_deteksi_langsung.mp4`: keluaran preview beranotasi KD Murni seed 42, 10 detik, 640×480, 100 frame pada 10 fps. Recorder melaporkan 8 frame mengulang hasil inferensi sebelumnya.
- `screenshot_awal.png`, `screenshot_tengah.png`, `screenshot_akhir.png`: cuplikan pada detik 2, 5, dan 8. Bola, gawang parsial, dan robot terlihat terdeteksi pada ketiganya; semua frame belum diaudit. Teks confidence bola kurang jelas karena melampaui latar label.
- `recording_stats.json`, `ffmpeg.log`, dan `manifest.json`: status perekaman serta metadata/hash.

Ini rekaman keluaran deteksi langsung, bukan screen record desktop atau benchmark. Confidence bukan akurasi, dan sesi tidak menghitung mAP. Video dan dokumentasi tersimpan lokal.
