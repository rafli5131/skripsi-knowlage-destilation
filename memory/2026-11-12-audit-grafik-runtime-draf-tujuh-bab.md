# Memory — audit grafik, runtime dan draf tujuh bab, 12 November 2026

[Audit grafik akurasi](../dokumentasi/2026-11-12/AUDIT_GRAFIK_AKURASI.md): 10 sumber dan 1.500 baris CSV agregat cocok; 18 PNG historis sama dengan commit `67ecf0c` namun hash tidak cocok manifest historis. Penyebab asal belum terbukti. Reproduksi pada Matplotlib 3.6.3 berbeda byte dan piksel; [18 grafik baru](../dokumentasi/2026-11-12/grafik-akurasi-terverifikasi/README.md) serta manifestnya disimpan terpisah. Jangan menggambarkan hash baru sebagai pembuktian provenance gambar lama.

Grafik runtime 24 run aktif dibuat dalam `dokumentasi/model/`, 10 PNG ID/EN, CSV agregat dan manifest. Seluruh 24 file hash cocok; jumlah frame dan rerata latensi cocok T36. 8 FPS adalah kriteria rerata run, bukan ambang yang harus dipenuhi setiap bin 2 detik. CPU/RSS adalah proses detektor, run lintas hari, tidak menyimpulkan sebab-akibat. Screenshot preview bukan bukti bebas freeze seluruh sesi.

[Draf tujuh bab](../laporan/draf-7-bab/README.md) disusun tanpa menghapus draf terdahulu. Bab 6 memuat tabel uji fungsional retrospektif yang membatasi KF-03 pada bukti ID yang ada; tracking bukan tujuan wajib. F1 utama T38 (harmonic mean precision/recall makro) teacher/Hybrid/supervised/KD murni: 0,7651/0,6146/0,6626/0,5766, dihitung dari CSV presisi penuh; F1 historis per kelas tetap dibedakan. Draf perlu verifikasi sitasi, penyesuaian format, dan tinjauan pembimbing. T43 tetap rencana. Detail: [log progres](../dokumentasi/2026-11-12/LOG_PROGRES_SKRIPSI.md).

Tidak ada kamera, motor, training, atau pengujian baru. Data eksperimen dan gambar historis dipertahankan. Tidak ada commit/push pada pekerjaan ini kecuali diminta secara eksplisit.
