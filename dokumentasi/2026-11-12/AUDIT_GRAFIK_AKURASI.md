# Audit grafik akurasi VAL — 12 November 2026

Audit ini tidak mengubah gambar atau manifest lama. Hasil per file tersimpan pada [audit JSON](audit_hash_grafik_akurasi.json); referensi awal adalah [manifest 11 November](../model/manifest_grafik_garis_akurasi.json).

- Sepuluh sumber `results.csv` dan T11 cocok dengan SHA-256 manifest. Semua **1.500 baris** CSV grafik gabungan cocok dengan rerata, minimum dan maksimum yang dihitung ulang dari sembilan CSV sumber, dengan toleransi pembulatan 0,000000501.
- Hash aktual **18 PNG tidak cocok** dengan hash yang tertulis dalam manifest 11 November. Seluruh 18 PNG identik byte dengan isi commit Git awal `67ecf0c`. Maka selisih sudah ada pada commit itu; ini tidak membuktikan penyebab atau asal gambar sebelum commit.
- CSV gabungan dan dua PNG kurva mAP tambahan cocok dengan hash masing-masing pada manifest lama.
- Dengan generator dan sumber yang sama, reproduksi di direktori sementara menggunakan Matplotlib 3.6.3 menghasilkan 18 gambar yang berbeda byte dan piksel RGB dari gambar di Git. Metadata file Git menyebut `Matplotlib version3.11.2`; perbedaan environment adalah kemungkinan, bukan bukti penyebab ketidakcocokan manifest awal. Hasil sementara tidak menggantikan file historis.
- Reproduksi kedua pada environment yang sama menghasilkan **18/18 hash identik** dengan [manifest grafik versi baru](grafik-akurasi-terverifikasi/manifest.json). Ini memverifikasi keterulangan versi baru pada environment tersebut, bukan asal gambar historis.
- Rekonsiliasi JSON mencatat hash historis yang diklaim, hash aktual pada Git, dan hash reproduksi. Hash aktual dapat dipakai mendeteksi perubahan **sejak audit ini**, tetapi tidak membuktikan provenance atau kebenaran piksel sebelum commit. Jangan menyajikan manifest lama sebagai verifikasi hash 18 PNG tersebut.

**Kesimpulan:** audit dan pencatatan hash aktual selesai; penyebab historis selisih dan reproduksi byte-identik masih belum terverifikasi. Untuk penggunaan akhir, prioritaskan kurva tambahan yang hash-nya cocok atau periksa grafik terkait bersama sumbernya. Perbedaan hash gambar tidak mengubah angka T05/T30/T38/T42.
