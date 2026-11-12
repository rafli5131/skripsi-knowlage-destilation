# Log progres — 12 November 2026

## Audit grafik akurasi

Sepuluh sumber cocok dengan manifest dan 1.500 baris data agregat cocok saat dihitung ulang. Sebanyak 18 PNG historis cocok dengan commit asal tetapi berbeda dari hash pada manifest lama; penyebab historis belum diketahui. [Audit lengkap dan hash aktual](AUDIT_GRAFIK_AKURASI.md) mempertahankan catatan awal. Sebanyak [18 grafik hasil reproduksi terpisah](grafik-akurasi-terverifikasi/README.md) dibuat dari sumber yang sama dengan manifest baru; reproduksi kedua pada environment sama cocok 18/18 hash; keduanya tidak menggantikan file historis. Dua kurva mAP tambahan pada manifest lama cocok hash-nya.

## Grafik runtime OP3

Ke-24 sumber jendela runtime tersedia dan cocok dengan manifest; generator juga memeriksa jumlah frame dan rerata latensi terhadap T36. Dibuat 10 PNG (empat model dan gabungan, ID/EN), satu CSV dan [manifest](../model/manifest_grafik_garis_runtime.json). Grafik berukuran 2.800 × 3.000 piksel, nilai per bin 2 detik. Pemeriksaan visual lembar pratinjau lima panel untuk setiap bahasa menemukan judul, sumbu, legenda dan garis 8 FPS terlihat; teks catatan kaki relatif kecil pada tampilan diperkecil dan perlu diperiksa pada skala akhir cetak. Garis 8 FPS bukan bukti setiap bin memenuhi kriteria rata-rata per run.

Grafik: [teacher](../model/teacher_yolo11n/README.md), [Hybrid](../model/kd_hybrid/README.md), [supervised](../model/supervised/README.md), [KD murni](../model/kd_murni/README.md), dan [gabungan](../model/gabungan/README.md). CPU dan RSS adalah proses detektor; perbandingan bersifat deskriptif. Data mentah tidak diubah atau dipublikasikan.

## Naskah dan tindak lanjut

[Draf tujuh bab](../../laporan/draf-7-bab/README.md) memetakan hasil ke D17 dan menyertakan tabel fungsional retrospektif. [F1 utama T38](T38_F1_D11_turunan.csv) dihitung dari precision dan recall makro sumber; nilai historis rerata F1 kelas tetap ditampilkan terpisah. KF-03 hanya didukung keberadaan ID, belum merupakan bukti lulus kestabilan ID pada objek bergerak; tracking bukan tujuan wajib. Kriteria KNF-01 dipakai pada FPS rerata per run: minimum T36 9,6869 FPS.

Draf masih memerlukan pengembangan pembahasan pustaka, verifikasi sitasi, penyesuaian format kampus dan tinjauan pembimbing. T43 masih rencana dan tidak dijalankan. Tidak ada kamera, servo, robot, training, atau evaluasi baru yang dijalankan untuk pekerjaan ini.
