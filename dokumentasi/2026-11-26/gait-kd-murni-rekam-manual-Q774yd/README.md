# Gait KD Murni untuk perekaman manual di laptop

Pada 26 November 2026 sekitar 18.43 WIB, operator meminta robot berjalan agar dapat melakukan screen record manual dengan preview KD Murni aktif. Pengendali memberi ack mulai dan berhenti; durasi dari ack mulai sampai perintah stop 30.00 detik. Gait dihentikan otomatis sesuai target 30 detik. Kepala tidak diberi perintah posisi oleh guard; modul kepala `none` sebelum gait dan perubahan pembacaan maksimum dua count dari acuan. Ini tidak menjamin kepala sama sekali tidak bergerak.

Sebanyak 30 sampel telemetry, termasuk preflight, menunjukkan rentang sudut lutut kiri 0.6599 rad dan kanan 0.6673 rad. Pemeriksaan baca-saja pasca-stop berstatus `read_only_completed`. Sampel mendukung adanya gerakan kaki, tetapi perpindahan fisik robot tidak diukur.

- `guard/gait_guard.json`: status, waktu dan batas pengaman.
- `guard/head_samples.csv`: sampel telemetry kepala dan kaki.
- `guard/pasca_stop.json`: pemeriksaan setelah stop.
- `manifest.json`: metadata dan ringkasan hasil.

Video direkam secara manual oleh operator di laptop; file belum tersedia atau diverifikasi pada robot. Sesi ini dokumentasi, bukan benchmark. Berkas belum dipush.
