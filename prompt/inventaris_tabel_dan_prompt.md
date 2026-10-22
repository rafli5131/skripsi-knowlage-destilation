# Inventaris prompt dan tabel skripsi

Pembaruan: 23 Oktober 2026. Eksperimen mencakup **KD murni teacher-only** dan **KD Hybrid full**; student supervised menjadi kontrol. T35 merangkum waktu training dan sesi TEST untuk naskah; evaluasi live OP3 tidak menjadi hasil utama skripsi sesuai arahan terbaru. Prompt adalah instruksi kerja; angka dan klaim penelitian harus tetap ditelusuri ke artefak dan tabel hasil.

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
| [Proposal Bab I–III KD OP3 — V2 terkini](PROMPT_PROPOSAL_BAB_I-III_KD_OP3_V2.md) | Menulis proposal baru dari keputusan dan bukti KD Hybrid, pure KD, supervised, serta uji OP3 terbaru | Prompt 22 Oktober; buat draf baru dan tandai keputusan pembimbing yang belum final. |
| [Bab IV–V hasil KD — fokus waktu training/TEST](PROMPT_BAB_IV_V_HASIL_KD_OP3_2026-10-23.md) | Menulis draf baru hasil dan kesimpulan dari training, VAL/TEST, durasi sesi TEST, dan benchmark per gambar | Prompt siap pakai; evaluasi live OP3 di luar hasil utama. |
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
