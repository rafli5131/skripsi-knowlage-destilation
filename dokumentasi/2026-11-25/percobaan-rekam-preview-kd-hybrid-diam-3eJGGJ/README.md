# Rekaman preview KD Hybrid — kondisi diam

Direkam 25 November 2026 sekitar pukul 20.36 WIB. Operator menyatakan objek siap dan kondisi diam; status torque servo tidak diverifikasi. Tidak ada perintah motor yang dikirim. Model KD Hybrid full seed 1337, topic kamera `/thesis/image_raw`.

- `rekaman_preview_saja_1280x960.mp4`: rekaman 60 detik berisi area kamera dengan kotak deteksi saja; hasil crop dari rekaman layar asli dan pembesaran 2×. Sumber kamera tetap 640×480.
- `klip_preview_saja_10_detik.mp4`: potongan 10 detik dari versi di atas.
- `screenshot_preview_saja.png`: cuplikan dari sekitar detik 30.
- `rekaman_preview_kamera_optimasi.mp4`: rekaman layar jendela asli, 1100×720, 60 detik, 159 frame (rata-rata 2,65 fps).
- `rekaman_preview.mp4`: percobaan awal, dashboard terpilih dan banyak frame berulang; bukan versi yang diminta.
- `rekaman_preview_kamera_ulang.mp4`: percobaan kedua, kamera saja tetapi hanya enam frame dalam 58,5 detik; bukan rekaman realtime yang layak.
- `screenshot_preview_awal.png`, `screenshot_preview_optimasi.png`, `klip_preview_10_detik.mp4`: turunan percobaan dan rekaman jendela utuh.
- `manifest.json`: hash, pengaturan dan informasi video dari ffprobe.

Rekaman akhir tetap tersendat pada sekitar 2,65 fps karena keterbatasan perekaman jendela melalui SSH-X; angka ini bukan FPS inferensi model. Bola, gawang parsial, dan robot tampak terdeteksi pada frame awal, tengah, dan akhir yang diperiksa; seluruh frame tidak diaudit. Confidence bukan akurasi, dan rekaman ini bukan benchmark performa atau mAP. Berkas disertakan dalam repositori atas permintaan pengguna.
