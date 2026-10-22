# Audit kelengkapan dokumentasi skripsi — 22 Oktober 2026

## Kesimpulan

Bukti pengujian sudah terdokumentasi cukup luas untuk bahan analisis: ada laporan per sesi OP3, grafik, contoh visual, tabel evaluasi model, log mentah, dan draf bab skripsi. Namun dokumentasi **belum siap disebut paket skripsi final**. Indeks dan T19 kini disinkronkan dengan eksperimen terbaru; Bab IV–V masih memakai hasil yang dinyatakan selesai 10 Oktober dan perlu diperbarui agar memasukkan hasil Oktober 21–22 serta menjelaskan batas bukti runtime.

## Materi yang tersedia

- **Eksperimen kamera/robot OP3:** [indeks per tanggal](INDEKS.md), dengan 26 folder eksperimen pada tiga tanggal (penomoran per tanggal) dan 32 berkas README, termasuk versi bilingual. Laporan memiliki ringkasan metode dan hasil; grafik, gambar contoh/audit, CSV, dan JSON tersedia sesuai jenis sesi. Tidak semua sesi menyimpan video atau semua frame mentah.
- **Evaluasi dataset dan model:** [indeks T01–T33](../analisis_performa/INDEKS.md), tabel CSV/Markdown, hasil VAL/TEST, analisis per kelas, benchmark server, serta catatan audit label.
- **Benchmark KD runtime terbaru:** [KD murni idle/walking](2026-10-22/percobaan-18-benchmark-kd-murni-setara-preview/README_ID.md), [KD Hybrid idle/walking](2026-10-22/percobaan-19-benchmark-kd-hybrid-setara-preview/README_ID.md), dan [KD Hybrid idle terverifikasi setelah OpenCR pulih](2026-10-22/percobaan-21-kd-hybrid-servo-idle-opencr-pulih/README_ID.md). Ketiganya menyediakan grafik dan tautan log CSV/JSON.
- **Draf naskah:** [Proposal Bab I–III](../DRAF_PROPOSAL_BAB_I-III.md), [Bab IV–V](../DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md), dan [abstrak](../DRAF_ABSTRAK_SKRIPSI.md).
- **Tabel robot T15–T27 diaudit/dilengkapi dari bukti yang ada:** lingkungan NUC, benchmark idle/walking, startup, frame-gap, deadline, deteksi per kelas, dan trade-off kini menunjuk langsung ke CSV/JSON sumber. Indeks tabel menjelaskan batas pengukuran yang belum ada; angka yang tidak pernah direkam tidak diisi dengan perkiraan.

## Hal yang perlu dibereskan sebelum naskah final

1. **Integrasikan hasil terbaru ke Bab IV–V.** Draf sekarang menyatakan hasilnya berhenti pada 10 Oktober. Masukkan tabel/grafik eksperimen 18, 19, dan 21, jelaskan protokol, checkpoint, preview, jumlah run, serta bedakan metrik runtime dari akurasi.
2. **Tentukan perlakuan atas pengukuran yang belum tersedia.** Status per tabel ada di [indeks analisis](../analisis_performa/INDEKS.md). Yang belum ada dari bukti saat ini antara lain fixed-frame CPU OP3 (T16), sapuan thread terkendali (T17), rekaman suhu berkelanjutan (T21), laju kamera-only berpasangan (T22), efek preview terisolasi (T24), serta set kamera independen yang dikunci untuk klaim generalisasi (T27). Jika bukan kebutuhan rumusan masalah, cantumkan sebagai batasan; jangan mengisi dengan estimasi.
3. **Jaga validitas klaim kamera.** Frekuensi keluaran kotak, confidence, FPS, latensi, CPU, dan RAM sudah tercatat. Itu tidak menggantikan ground truth. Untuk klaim precision/recall/mAP kamera, gunakan frame beranotasi independen dan protokol evaluasi yang ditetapkan sebelum pengujian; hasil eksploratif T27 dan risiko bias anotasinya perlu disebutkan.
4. **Perjelas bukti kondisi berjalan.** Label walking pada benchmark 18–19 berasal dari operator/perintah gait, bukan pengukuran gerak independen. Laporkan sebagaimana adanya; jangan menyebutnya pengenalan gait oleh detector. Percobaan 21 mendukung idle dengan telemetry kecepatan joint nol sebelum/sesudah.
5. **Rapikan paket gambar dan rujukan.** Pilih gambar representatif yang terbaca (hasil deteksi, contoh kesalahan, grafik utama), pastikan nomor gambar/tabel dan caption konsisten, serta tautkan ke protokol dan sumber angka. Log per-frame tetap menjadi lampiran/artefak, bukan ditempel seluruhnya ke badan bab.
6. **Finalisasi akademik.** Periksa sitasi dan daftar pustaka, format kampus, penomoran, konsistensi istilah “KD murni/KD Hybrid”, pembahasan ancaman validitas, kesimpulan yang menjawab rumusan masalah, dan persetujuan pembimbing.

## Prioritas praktis berikutnya

Tabel robot sudah dilengkapi dari log yang tersedia. Berikutnya, perbarui Bab IV–V dari tabel/laporan ini, audit angka terhadap CSV/JSON sumber, lalu nyatakan pengukuran yang belum ada sebagai keterbatasan kecuali memang diperlukan untuk menjawab rumusan masalah.
