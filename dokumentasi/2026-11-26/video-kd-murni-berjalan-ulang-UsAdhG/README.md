# Video deteksi KD Murni saat gait — ulangan

Pada 26 November 2026 sekitar 18.39 WIB operator mengonfirmasi robot siap dan mendampingi. Preview menggunakan KD Murni seed 42. Parameter gait yang dibaca menetapkan amplitudo maju, samping, dan putar nol (melangkah di tempat); perpindahan fisik aktual tidak diukur.

- `video/preview_deteksi_langsung.mp4`: keluaran preview beranotasi 10 detik, 640×480, 100 frame pada 10 fps; enam frame mengulang hasil inferensi sebelumnya. Ini bukan screen record desktop atau benchmark.
- `screenshot_awal.png`, `screenshot_tengah.png`, dan `screenshot_akhir.png`: cuplikan pada 2, 5, dan 8 detik. Bola, gawang parsial, dan robot terlihat terdeteksi pada ketiganya; semua frame belum diaudit. Label confidence bola kurang jelas karena melampaui latar label.
- `guard/gait_guard.json`, `guard/head_samples.csv`, `guard/pasca_stop.json`: respons gait dan telemetry.
- `video/recording_stats.json`, `video/ffmpeg.log`, dan `manifest.json`: statistik serta metadata/hash.

Pengendali memberi ack start dan stop. 11 sampel telemetry menunjukkan rentang sudut lutut kiri 0.6124 rad dan kanan 0.5875 rad; ini mendukung adanya gerakan kaki, bukan pengukuran jarak. Modul kepala `none` sebelum gait, guard tidak memberi perintah posisi kepala, dan perubahan pembacaan maksimum dua count; ini tidak menjamin kepala sama sekali tidak bergerak. Pemeriksaan lima detik pascastop mencatat rentang sendi kaki sekitar 0,00153 rad.

Percobaan sebelumnya [terhenti oleh pengaman](../video-kd-murni-berjalan-JLNffv/README.md) setelah sekitar satu detik dan tetap disimpan terpisah. Sesi ini merupakan dokumentasi, bukan perhitungan akurasi atau benchmark. Video tersimpan lokal.
