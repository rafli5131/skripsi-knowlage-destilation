# Prompt penulisan Bab IV–V skripsi KD dan ROBOTIS OP3

Gunakan prompt ini **setelah** tabel dan dokumen hasil ditinjau. Instruksi ini hanya menyiapkan naskah; jangan menjalankan robot, kamera, training, atau pengujian ulang.

## Instruksi siap pakai

Bertindak sebagai penulis ilmiah bidang deteksi objek dan Knowledge Distillation (KD). Susun **draf baru Bab IV (Hasil dan Pembahasan) serta Bab V (Kesimpulan dan Saran)** dalam Bahasa Indonesia, dengan fokus pada **waktu training, waktu pengujian, akurasi VAL/TEST, dan biaya inferensi per gambar**. Hasil evaluasi live/online kamera dan gerak OP3 disimpan sebagai dokumentasi teknis dan **tidak dimasukkan sebagai hasil utama Bab IV–V**. Tulis klaim berdasarkan artefak yang dapat ditelusuri. Jangan mengarang angka, kutipan, persetujuan pembimbing, atau kepastian statistik. Istilahnya adalah *Knowledge Distillation*, bukan *Knowledge Development*. Penelitian ini mengevaluasi metode yang ada, bukan mengklaim algoritma KD baru.

### Audit sumber sebelum menulis

1. Baca `docs/DECISIONS.md`, `PROTOKOL_EKSPERIMEN_SKRIPSI.md`, `KERANGKA_BAB_SKRIPSI.md`, `DRAF_PROPOSAL_BAB_I-III.md`, `DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`, `analisis_performa/INDEKS.md`, dan `dokumentasi/INDEKS.md`. Cocokkan tujuan/rumusan masalah dengan Bab I–III terkini; jika redaksinya belum pasti, tandai untuk konfirmasi, jangan menebak.
2. Audit tabel T01–T14 (training, VAL, TEST dan benchmark server), T28–T33 (KD Hybrid tiga seed dan TEST), serta **[T35 waktu training dan pengujian](../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md)**. Cocokkan angka penting dengan CSV, `results.csv`, dan manifest TEST primer.
3. Untuk waktu training, utamakan [T02](../analisis_performa/tabel/T02_resep_pelatihan.md), [T33](../analisis_performa/tabel/T33_pelatihan_kd_hybrid_full.md), dan T35. Untuk waktu TEST, baca `started_at_utc` dan `finished_at_utc` pada dua manifest `runs/final_test/`. Untuk biaya inferensi per gambar, baca [T32](../analisis_performa/tabel/T32_kd_hybrid_benchmark_server.md) beserta protokol benchmark. T19/T26/T27/T34 dan dokumentasi percobaan 25–28 tetap arsip pendukung; jangan memasukkannya ke hasil utama tanpa perubahan arahan pengguna/pembimbing.
4. Bila sumber bertentangan, pakai urutan: keputusan/protokol bertanggal → manifest dan log primer → tabel hasil terkini → laporan percobaan → draf lama. Catat konflik dan statusnya.

### Pisahkan jenis waktu dan hasil

- **TEST Advance Vision:** kualitas deteksi pada split dataset resmi; T05–T07 dan T30–T31. Hybrid full seed 1337 mAP50–95 0,7468 dan F1 0,9065; Supervised seed 1337 0,7264933293 dan 0,9122955712. Untuk kesimpulan metode, gunakan hasil tiga seed berpasangan dan simpangan/interval yang tersedia; jangan menyebut satu seed sebagai rerata. TEST pernah dipakai pada eksperimen terdahulu, jadi jangan sebut holdout yang belum pernah dilihat.
- **Waktu training per run:** T02/T33/T35. Tampilkan 3 seed untuk KD murni, Supervised, dan KD Hybrid full dalam detik atau jam, lengkap dengan sumber. Supervised seed 1337 adalah jumlah dua segmen resume tanpa jeda interupsi. Server dipakai bersama, sehingga selisih durasi tidak boleh ditafsirkan sebagai akibat metode saja. Waktu training teacher tidak tersedia dengan provenance setara.
- **Waktu TEST satu sesi:** T35 menghitung selisih cap waktu manifest berstatus `complete`: sesi KD murni + Supervised + Teacher **167,217 detik untuk 7 checkpoint**, dan sesi Hybrid + Supervised **52,784 detik untuk 6 checkpoint**, masing-masing 592 gambar per checkpoint. Angka ini mencakup pipeline multi-model dan overhead; **bukan durasi TEST tiap model**. Jangan mengklaim Hybrid lebih cepat diuji hanya dari dua angka itu. Jika pertanyaan penelitian memerlukan waktu TEST per model, tulis bahwa angka tersebut belum tersedia.
- **Latensi benchmark inferensi:** T32 mencatat waktu per gambar pada frame tetap dan NVIDIA L40, termasuk median Hybrid seed 1337 **8,483 ms/gambar** dan Supervised seed 1337 **13,132 ms/gambar** dalam **sesi yang sama**. Ini bukan durasi keseluruhan TEST, bukan waktu training, dan bukan kecepatan live OP3. Benchmark KD murni lama dan benchmark Hybrid baru memakai hash skrip berbeda; checkpoint Supervised seed 1337 yang identik berubah dari 25,262 menjadi 13,132 ms median. Jangan menggabungkan latensi antar-sesi sebagai pembuktian bahwa satu objective lebih cepat. Laporkan median/P95 dan parameter benchmark sesuai sumber.

### Struktur Bab IV

Susun bagian: (a) tujuan evaluasi dan lingkungan server; (b) waktu training tiap metode dan seed dari T35 beserta pembahasan keterbatasan server bersama; (c) hasil pelatihan, VAL, dan pemilihan checkpoint; (d) hasil TEST tiga seed, pembanding teacher/supervised/pure KD/Hybrid, per kelas dan trade-off; (e) durasi total sesi TEST dari T35 serta latensi inferensi per gambar dari T32 dengan definisi waktu yang terpisah; (f) analisis kegagalan pada data TEST dan batas validitas. Rujuk tabel dan grafik yang benar-benar ada dengan nomor sementara dan caption yang menjelaskan dataset, n, unit, perangkat, seed, protokol, serta sumber. Gunakan dua grafik T35 dengan sumbu dan cakupan waktu yang eksplisit.

Jelaskan hasil yang tidak mendukung hipotesis juga. Jangan menyimpulkan Hybrid terbaik secara umum hanya karena mAP lebih tinggi; F1 TEST dan biaya evaluasi perlu dibahas sesuai definisi metriknya. Jangan menyatukan durasi training, durasi sesi TEST, dan latensi per gambar menjadi satu angka efisiensi. Dokumentasi live OP3 dan evaluasi frame OP3 tetap tersedia di repository, tetapi di luar ruang hasil utama naskah ini.

### Struktur Bab V

Tulis kesimpulan bernomor yang menjawab tiap rumusan masalah dengan angka dan lingkupnya, terutama kualitas deteksi TEST serta waktu training/pengujian. Nyatakan secara jelas bahwa durasi TEST per checkpoint belum tercatat, sedangkan T32 menyediakan latensi inferensi pada protokol benchmark terpisah. Tulis saran yang mengikuti keterbatasan nyata, seperti pengukuran waktu TEST per checkpoint dengan protokol sama, pengulangan training pada sumber daya terisolasi, serta evaluasi pada data yang lebih independen. Saran adalah pekerjaan mendatang, bukan hasil yang sudah diperoleh.

### Keluaran dan pemeriksaan akhir

Simpan **draf baru** sebagai `DRAF_BAB_IV-V_KD_OP3_REVISI_2026-10-23.md`; pertahankan draf lama. Sertakan matriks ringkas `klaim → tabel/CSV/JSON → batas interpretasi`, daftar tabel/gambar yang dirujuk, dan daftar hal yang masih memerlukan keputusan pembimbing. Periksa semua angka terhadap sumber primer, semua tautan lokal, satuan dan koma desimal, identitas seed/checkpoint, serta konsistensi rumusan masalah. Jangan mengisi celah bukti dengan estimasi atau data fiktif. Jangan push/publikasi tanpa instruksi pengguna.
