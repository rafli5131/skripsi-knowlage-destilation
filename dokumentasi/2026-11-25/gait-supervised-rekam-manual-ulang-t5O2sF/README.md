# Gait Supervised untuk perekaman manual di laptop

Operator meminta gait dengan preview Supervised seed 1337 aktif agar dapat merekam secara manual di laptop. Pengendali memberi ack mulai dan berhenti; waktu dari ack mulai hingga perintah stop 30.00 detik. Gait dihentikan otomatis sesuai target 30 detik. Kepala tidak diberi perintah posisi oleh guard; modul kepala `none` sebelum gait dan perubahan pembacaan maksimum dua count dari acuan. Ini bukan jaminan tidak terjadi gerakan sama sekali.

Sebanyak 30 sampel telemetry, termasuk preflight, menunjukkan rentang sudut lutut kiri 0.6477 rad dan kanan 0.6642 rad. Pemeriksaan baca-saja pasca-stop memiliki status `read_only_completed`; rincian ada pada `guard/pasca_stop.json`. Sampel mendukung adanya gerakan kaki, tetapi perpindahan fisik robot tidak diukur.

- `guard/gait_guard.json`: status, waktu dan batas pengaman.
- `guard/head_samples.csv`: telemetry sampel kepala dan kaki.
- `guard/pasca_stop.json`: pemeriksaan setelah stop.
- `manifest.json`: metadata dan ringkasan hasil.

Video dilakukan secara manual oleh operator di laptop; file belum tersedia atau diverifikasi pada robot. Sesi ini merupakan dokumentasi, bukan benchmark.
