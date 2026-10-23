# Inventaris prompt dan tabel skripsi

Pembaruan: 23 Oktober 2026. Eksperimen mencakup **KD murni teacher-only** dan **KD Hybrid full**; student supervised menjadi kontrol. T35 merangkum waktu training dan sesi TEST sebagai informasi pendukung. Sejak 23 Oktober 2026, atas arahan Bhre, uji live OP3 dengan kondisi setara (empat model termasuk teacher, idle dan berjalan, tiga ulangan) menjadi pengujian akhir untuk rumusan masalah nomor 4 dan 5; arahan sebelumnya yang menempatkan live OP3 di luar hasil utama tidak berlaku lagi. Prompt adalah instruksi kerja; angka dan klaim penelitian harus tetap ditelusuri ke artefak dan tabel hasil.

Inventaris terdahulu mengacu pada proyek YOLO11 QAT/OpenVINO yang berbeda; rujukan aktif adalah tabel T01–T35 di repository ini.

## Temukan hasil tabel

| Kelompok | Isi | Indeks hasil | Status saat ini |
| --- | --- | --- | --- |
| Lab/server T01–T14 | Spesifikasi model, training, VAL, TEST terkunci, dan benchmark server | [Indeks lab/server](../analisis_performa/lab_server/README.md) | T01–T14 lengkap dalam scope sumbernya; T04 memuat pilot `pure_weighted` satu seed dan tiga baseline. T12/T13 memakai tiga model perwakilan. |
| KD Hybrid T28–T33 | VAL dan TEST tiga seed berpasangan, benchmark L40, serta pelatihan Hybrid | [Laporan TEST Hybrid](../analisis_performa/lab_server/HASIL_KD_HYBRID_TEST_2026-10-22.md) | Selesai untuk scope lab/server; tidak mengukur kamera OP3 |
| Waktu training dan pengujian T35 | Durasi per run training dan durasi dua sesi TEST multi-model | [T35](../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md) | Durasi TEST per checkpoint belum tercatat; latensi inferensi per gambar ada di T32 |
| ROBOTIS OP3 T15–T27 dan T34 | Runtime kamera, latensi, FPS, CPU/RAM, tracking, dan akurasi frame berlabel | [Indeks umum](../analisis_performa/INDEKS.md) | T19/T26 mencakup run terbaru; T34 membandingkan Hybrid dan Supervised seed 1337 pada frame identik. Fixed-frame OP3 T16, sapuan thread T17, termal T21, kamera-only T22, dan preview terisolasi T24 masih memiliki celah yang tercatat. |

Tabel bernomor tetap tersimpan berpasangan sebagai CSV dan Markdown di [`analisis_performa/tabel/`](../analisis_performa/tabel/). Rincian interval bootstrap tiap checkpoint melengkapi T05 di [folder lab/server](../analisis_performa/lab_server/interval_bootstrap_per_model.md).

## Pilih prompt sesuai pekerjaan

| Prompt | Kegunaan | Hasil atau langkah terkait |
| --- | --- | --- |
| [Proposal Bab 1 sampai 3 sesuai template dan Panduan FILKOM](PROMPT_PROPOSAL_BAB_1-3_TEMPLATE_FILKOM.md) | Menyusun proposal `.docx` Bab 1 sampai 3, Daftar Referensi, dan bagian awal mengikuti Template-ProposalSkripsi-v3.0 dan Panduan v3.0 (RPC implementatif-pengembangan, struktur skripsi tujuh bab), melanjutkan hasil TH-0 | Prompt aktif untuk proposal; mulai dari TH-1 |
| [Proposal Bab I–III KD OP3 V2 (arsip)](PROMPT_PROPOSAL_BAB_I-III_KD_OP3_V2.md) | Versi 22 Oktober | Digantikan prompt template FILKOM; jangan gunakan untuk draf baru. |
| [Perbaikan objektif KD jalur tengah](PROMPT_PERBAIKAN_KD_JALUR_TENGAH.md) | Server lab: diagnosis objektif KD hibrida, mode baru `hybrid_v2` (KL-DFL, bobot foreground kotak, penyetelan di VAL), konfirmasi tiga seed, ablasi teacher YOLO11s ke student t di VAL saja, aturan seleksi terkunci sebelum training, serah terima model final ke uji live | Belum dijalankan; dijalankan sebelum uji live setara; menghasilkan T39 sampai T43 |
| [Uji ulang live OP3 setara dengan teacher](PROMPT_UJI_ULANG_LIVE_SETARA_OP3_DENGAN_TEACHER.md) | Pengujian akhir: teacher, KD Hybrid seed 1337, Supervised seed 1337, dan KD murni seed 42 pada kondisi idle (semua servo menyala) dan berjalan (ID 19/20 torque on tanpa gerak), preview SSH -X aktif, tiga ulangan dengan urutan digilir, dokumentasi per run, serta evaluasi offline empat model pada 260 frame | Belum dijalankan; menghasilkan T36, T37, dan T38 |
| [Bab IV–V hasil KD V2: uji live OP3 sebagai pengujian akhir](PROMPT_BAB_IV_V_HASIL_KD_OP3_V2.md) | Menulis draf baru Bab IV dan V yang menjawab lima rumusan masalah; RQ4 dan RQ5 dari uji live setara | Prompt aktif untuk naskah |
| [Bab IV–V hasil KD versi 23 Oktober (arsip)](PROMPT_BAB_IV_V_HASIL_KD_OP3_2026-10-23.md) | Versi lama yang berfokus pada waktu training/TEST | Digantikan V2; jangan gunakan untuk draf baru. |
| [Prompt proposal versi awal (arsip)](PROMPT_PROPOSAL_BAB_I-III_KD_OP3.md) | Riwayat prompt fokus pure KD sebelum hasil Hybrid OP3 | Digantikan V2; jangan gunakan untuk proposal terkini. |
| [Tabel lab/server KD](PROMPT_TABEL_LAB_SERVER_KD.md) | Menyusun T01–T14 dari artefak training, VAL, TEST terkunci, dan benchmark server | Sudah dipakai untuk kurasi [T01–T14](../analisis_performa/lab_server/README.md) pada 20 Oktober 2026 |
| [Tabel ROBOTIS OP3 KD](PROMPT_TABEL_ROBOT_OP3_KD.md) | Menyusun T15–T27 dari log robot yang sudah ada | Dipakai saat pembaruan tabel runtime robot, tanpa menjalankan perangkat |
| [Percobaan KD Hybrid di OP3](PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3.md) | Panduan kandidat Hybrid seed 1337: prasyarat runtime, live tracking, capture, sesi performa, dan evaluasi frame berlabel | Hasil runtime Hybrid tersedia pada dokumentasi percobaan 18–21; gunakan laporan hasil untuk status terkini |
| [Evaluasi eksternal OP3 — Jalur Pertama](PROMPT_EVALUASI_EKSTERNAL_OP3_JALUR_1.md) | Protokol evaluasi baru yang membandingkan Hybrid seed 1337 dan supervised seed 1337 pada frame dengan label berbantuan auto-label yang ditinjau Bhre, serta benchmark runtime idle/berjalan | Untuk sesi OP3 baru; tidak menggantikan atau membersihkan hasil TEST Advance Vision dan T27 eksploratif |
| [Uji live kamera dan tracking OP3](PROMPT_UJI_LIVE_KAMERA_TRACKING_OP3.md) | Panduan pemeriksaan kamera, kelas, dan ID tracking pada perangkat | Hasil uji harus dicatat sebagai observasi runtime, bukan mAP kamera |
| [Monitor dan rekam OP3 bersamaan](PROMPT_MONITOR_DAN_REKAM_KAMERA_OP3_BERSAMAAN.md) | Deteksi/ID live di jendela sambil merekam frame mentah dari topic kamera yang sama | Pra-label setelah capture; log sesi gabungan bukan benchmark |
| [Kumpul frame dan label kamera OP3](PROMPT_KUMPUL_FRAME_DAN_LABEL_OP3.md) | Pengambilan frame mentah dan pra-label otomatis untuk ditinjau manusia | Gambar dan label draf di `data/op3_camera_eval/sessions/<session_id>/`; mAP menunggu label final |
| [Perbaikan kode dan analisis performa](PROMPT_PERBAIKAN_KODE_DAN_ANALISIS_PERFORMA.md) | Peta fase riset, aturan protokol, dan titik henti | Baca keputusan terkunci di [`docs/DECISIONS.md`](../docs/DECISIONS.md) |
| [Implementasi robot OP3](PROMPT_IMPLEMENTASI_ROBOT_OP3.md) | Rancangan awal node inferensi PyTorch pada OP3 | Runtime terkini ada di [`OP3_PYTORCH_RUNTIME.md`](../OP3_PYTORCH_RUNTIME.md) |
| [Penyusunan laporan skripsi](PROMPT_PENYUSUNAN_LAPORAN_SKRIPSI.md) | Menyusun naskah dari protokol, tabel, dan bukti | Draf hasil ada di [`DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`](../DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md) |

## Aturan penggunaan hasil

- TRAIN dipakai untuk melatih, VAL untuk memilih konfigurasi dan checkpoint, sedangkan TEST dipakai untuk evaluasi akhir. Split TEST Advance Vision sudah pernah dipakai pada eksperimen teacher dan KD murni; evaluasi Hybrid adalah lanjutan pada split yang sama. Parameter Hybrid tidak dipilih ulang berdasarkan TEST.
- Benchmark NVIDIA L40 adalah hasil server. Pengukuran kamera dan perangkat ROBOTIS OP3 dilaporkan pada kelompok tabel robot.
- Metrik deteksi kamera OP3 memerlukan frame berlabel untuk menjadi precision, recall, F1, atau mAP. Jumlah kotak dan confidence dari log live hanya observasi.
- Berkas dari proyek YOLO11 QAT/OpenVINO lain tidak digabungkan ke hasil KD ini.
