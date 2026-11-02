# Log penyimpangan sesi 2 November 2026

| Run | Temuan | Tindakan dan batas interpretasi |
|---|---|---|
| Set lama, teacher berjalan u1 | Screenshot overlay setelah jendela tetapi sebelum detektor berhenti tidak tersimpan. | Preview pemantauan dihidupkan lagi; bukti dan catatan aslinya tersimpan di `01-teacher/arsip-set-sebelumnya-20261102-1200/slot-lama-u1/`. Run ini tidak masuk set aktif. |
| Set lama, teacher berjalan u1 | Sampel JointState penuh kedua pada tengah gait tidak tersimpan. | Log pengawas pan/tilt dan empat sendi kaki sekitar tiap satu detik dipakai langsung. Run ini tidak masuk set aktif. |
| Set lama, teacher berjalan u1 | Gawang muncul pada 112/611 frame jendela (18,3%). | Angka asli tetap di arsip dan log mentah; tidak masuk agregat aktif. |
| Set lama, sesudah teacher berjalan u1 | Jendela SSH-X sempat menampilkan frame lama saat detektor run berhenti. | Preview teacher pemantauan dinyalakan lagi setelah gait berhenti. |
| Set lama, teacher berjalan u2 | Generator laporan sempat menandai kaki belum stabil karena menghitung perubahan bahu kanan 0,004604 rad. | Kriteria diperbaiki agar hanya menilai sendi kaki sesuai prompt; data mentah tidak berubah. Run ini tidak masuk set aktif. |
| Set lama, teacher berjalan u1–u3 | Cakupan gawang 18,3%, 63,1%, lalu 95,2%. | Arsip mempertahankan hasil lama dan menunjukkan adegan tidak terbukti identik. |
| Set aktif, penomoran berjalan | Ulangan 1 memakai run mentah u3 dari set lama; ulangan 2 dan 3 memakai run baru. | `active_run_sources.json` menjadi sumber pemetaan slot; ID dan cap waktu mentah dipertahankan. |
| Set aktif, pemilihan hasil | Set ulang dipilih setelah melihat cakupan gawang set lama. | Rata-rata cakupan set aktif bersifat kondisional pada pemilihan run dan penataan adegan; arsip set lama wajib disertakan bila hasil dipakai di skripsi. |
| Set aktif, ulangan 2 | Suhu CPU tepat setelah run tidak tersimpan; pembacaan baru diambil sekitar enam menit kemudian. | Pembacaan diberi nama `suhu_diagnostik_terlambat_utc.txt`, tidak digunakan sebagai suhu akhir run. |
| Set aktif, ulangan 3 | Operator mengatur posisi gawang lagi sebelum run karena preview sempat menampilkan gawang hanya pada 14/50 frame. | Setelah penataan, gawang muncul pada 50/50 frame cek dan tidak ada orang pada frame; operator mengonfirmasi robot walk-ready dan area kaki kosong sebelum gait. Perubahan adegan dicatat sebagai batas perbandingan antar-run. |
| KD Hybrid idle u1–u3 | Ketiga ulangan idle KD Hybrid dijalankan sebagai satu blok atas permintaan Bhre, sedangkan prompt mengatur model bergilir per putaran. | Seluruh log, waktu, suhu, dan urutan aktual disimpan. Pengaruh waktu/suhu antarblok model tidak dapat dieliminasi; perbandingan runtime antarmodel dilaporkan deskriptif. |
