# Gait untuk perekaman manual di laptop — terhenti oleh pengaman

Operator meminta gait dengan preview KD Hybrid aktif agar dapat merekam layar secara manual di laptop. Robot memulai gait dan perintah stop dikonfirmasi pengendali setelah 19.72 detik, lebih singkat dari target 30 detik, karena pembacaan kepala mencapai tiga count dari baseline dan melewati batas dua count. Tidak ada perintah posisi kepala dari pengaman; perbedaan pembacaan tidak membuktikan penyebab gerakan.

Dua puluh dua sampel telemetry, termasuk preflight, menunjukkan variasi sudut lutut kiri 0.6553 rad dan kanan 0.6657 rad. Sesudah stop, pembacaan lima detik menunjukkan rentang tiap sendi kaki sekitar 0,00153 rad, dan pembacaan kepala terakhir pan 2191/tilt 1792 count. Ini bukan bukti bahwa robot mustahil bergerak.

Video direkam secara manual oleh operator di laptop dan tidak tersedia pada robot; keberadaan, isi dan durasinya belum diverifikasi. `guard/gait_guard.json` dan `guard/head_samples.csv` menyimpan peristiwa dan telemetry; `guard/pasca_stop.json` adalah pemeriksaan sesudah stop. `manifest.json` merangkum hasil. Sesi ini bukan benchmark.
