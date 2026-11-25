# Persiapan video berjalan KD Hybrid — terhenti saat walk-ready

Tanggal 25 November 2026 WIB. Preview KD Hybrid aktif. Operator meminta ID 19/20 tetap pada arah kamera dan mengonfirmasi badan serta kepala ditopang; rekaman dan gait menunggu konfirmasi tersendiri.

OpenCR merespons, tegangan 12,6 V, daya bus diaktifkan, dan seluruh ID 1–20 terdeteksi tanpa hardware error pada pembacaan awal. Torque awal seluruh servo mati; manager dijalankan dengan pose awal otomatis dan reconnect otomatis dimatikan, dan inisialisasi manager mengaktifkan torque. Torque ID 19/20 tidak dibaca terpisah sesudah manager menguasai bus. Sebelum startup, posisi kepala ID 19/20 terbaca sekitar 2193/1792 count.

Saat pemetaan kaki ke walking module, pengaman mencatat simpangan maksimum pan sekitar 2,001 count dan tilt 1 count dari baseline, lalu menandai gagal dan mengirim perintah stop. Pengaman menyatakan stop mungkin tidak langsung menghentikan transisi pose. Pembacaan setelah itu menunjukkan kepala kembali ke baseline dalam sampel terakhir, modul kepala `none`, dan 12 modul kaki `walking_module`; ini tidak membuktikan pose robot stabil atau walk-ready. Catatan lengkap terdapat pada `laporan_pengaman_kaki.json`.

Tidak ada perintah gait start dan tidak ada perekaman video berjalan pada persiapan ini. Tidak ada perubahan toleransi pengaman. Tunggu pemeriksaan operator dan keputusan sebelum melanjutkan.

Pemeriksaan baca-saja 10 detik berikutnya tersimpan dalam `pemeriksaan_stabilitas.json`: rentang pan sekitar dua count, tilt satu count, dan rentang 12 sendi kaki sekitar 0–2 count. Operator mengonfirmasi robot stabil dan arah kamera sesuai; status ini tidak membuktikan tidak ada gerakan sama sekali. Manager dan preview tetap aktif.

Audit pembacaan: konversi `XM430-W350.device` menggunakan titik nol 2048 dan maksimum 4095, sehingga konversi radian pada sisi positif memakai pembagi 2047. Pengaman lama memakai batas dua count dengan pembagi 2048; karena itu perubahan dua count di sisi positif dapat melampaui batas numerik yang lama sekitar 0,049%. Catatan ini tidak membuktikan penyebab fisik perubahan pembacaan dan tidak mengubah atau mengesampingkan pengaman lama.
