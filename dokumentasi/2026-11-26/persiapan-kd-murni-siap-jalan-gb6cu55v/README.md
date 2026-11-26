# Persiapan pose jalan untuk KD Murni

Pada 26 November 2026 operator meminta menyalakan servo dan mempersiapkan pose jalan tanpa memulai rekaman. Operator menyatakan badan dan kepala ditopang serta area kosong. Preview KD Murni aktif. Daya bus OpenCR diaktifkan setelah pembacaan 12,7 V; seluruh 20 servo terdeteksi, torque awal mati, mode posisi dan hardware error 0.

Manager dijalankan tanpa pose awal otomatis dan tanpa reconnect otomatis; inisialisasinya mengirim torque-on. Status torque per servo setelah startup tidak dibaca langsung karena manager memegang port. Sebelum startup posisi kepala 19/20 terbaca 2191/1792 count; setelah inisialisasi pembacaan sampel awal sama dan modul kepala `none`.

Saat pemetaan kaki, guard lama mengirim stop karena ambang radian terlampaui; perhitungan ulang sampelnya menunjukkan perubahan maksimum dua count pan dan satu count tilt dari acuan. Pemetaan kaki ke `walking_module` sudah terjadi dan pemeriksaan berikutnya menunjukkan kaki relatif stabil. Operator mengonfirmasi robot stabil dan arah kamera sesuai. Selanjutnya kedua shoulder pitch dipetakan ke walking module menggunakan package baru guard count, tanpa perintah kepala dan tanpa gait. Guard baru diuji sintetis: dua count diizinkan, tiga count dan telemetry kepala tidak valid memicu pelanggaran.

Setelah penyesuaian bahu, telemetry lima detik memperlihatkan pembacaan kepala terakhir 2191/1792 count dan penyimpangan maksimum terhadap acuan 2/1 count; rentang maksimum sendi kaki sekitar 0,001535 rad. Kaki dan bahu terpetakan ke walking module, kepala tetap `none`. Ini tidak membuktikan kepala tidak bergerak sama sekali. Operator kemudian mengonfirmasi pose siap dan arah kamera sesuai.

Tidak ada perintah start gait dan tidak ada rekaman video. `daya_bus.json`, `pengaman_kaki.json`, `pengaman_bahu.json`, dan `manifest.json` mendokumentasikan langkah; hasil guard kaki awal tetap dipertahankan sebagai gagal, tidak dinyatakan lulus. Tidak ada berkas media baru dalam sesi ini.
