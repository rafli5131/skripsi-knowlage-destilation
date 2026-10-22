# Inventaris prompt dan tabel skripsi

Pembaruan: 22 Oktober 2026. Eksperimen mencakup **KD murni teacher-only** dan **KD Hybrid full**; student supervised menjadi kontrol. Kandidat uji OP3 saat ini adalah Hybrid full seed 1337, sementara alias runtime `op3_default` masih menunjuk KD murni. Prompt adalah instruksi kerja; angka dan klaim penelitian harus tetap ditelusuri ke artefak dan tabel hasil.

Inventaris terdahulu mengacu pada proyek YOLO11 QAT/OpenVINO yang berbeda; rujukan aktif adalah tabel T01–T33 di repository ini.

## Temukan hasil tabel

| Kelompok | Isi | Indeks hasil | Status saat ini |
| --- | --- | --- | --- |
| Lab/server T01–T14 | Spesifikasi model, training, VAL, TEST terkunci, dan benchmark server | [Indeks lab/server](../analisis_performa/lab_server/README.md) | T01–T14 lengkap dalam scope sumbernya; T04 memuat pilot `pure_weighted` satu seed dan tiga baseline. T12/T13 memakai tiga model perwakilan. |
| KD Hybrid T28–T33 | VAL dan TEST tiga seed berpasangan, benchmark L40, serta pelatihan Hybrid | [Laporan TEST Hybrid](../analisis_performa/lab_server/HASIL_KD_HYBRID_TEST_2026-10-22.md) | Selesai untuk scope lab/server; tidak mengukur kamera OP3 |
| ROBOTIS OP3 T15–T27 | Runtime kamera, latensi, FPS, CPU/RAM, tracking, dan akurasi frame berlabel | [Indeks umum](../analisis_performa/INDEKS.md) | T15, T18, T20, T22, T23, T25, T26 sebagian dari log lama; T27 sebagian dari evaluasi eksploratif 21 Oktober; T16, T17, T19, T21, T24 belum diukur |

Tabel bernomor tetap tersimpan berpasangan sebagai CSV dan Markdown di [`analisis_performa/tabel/`](../analisis_performa/tabel/). Rincian interval bootstrap tiap checkpoint melengkapi T05 di [folder lab/server](../analisis_performa/lab_server/interval_bootstrap_per_model.md).

## Pilih prompt sesuai pekerjaan

| Prompt | Kegunaan | Hasil atau langkah terkait |
| --- | --- | --- |
| [Tabel lab/server KD](PROMPT_TABEL_LAB_SERVER_KD.md) | Menyusun T01–T14 dari artefak training, VAL, TEST terkunci, dan benchmark server | Sudah dipakai untuk kurasi [T01–T14](../analisis_performa/lab_server/README.md) pada 20 Oktober 2026 |
| [Tabel ROBOTIS OP3 KD](PROMPT_TABEL_ROBOT_OP3_KD.md) | Menyusun T15–T27 dari log robot yang sudah ada | Dipakai saat pembaruan tabel runtime robot, tanpa menjalankan perangkat |
| [Percobaan KD Hybrid di OP3](PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3.md) | Panduan kandidat Hybrid seed 1337: prasyarat runtime, live tracking, capture, sesi performa, dan evaluasi frame berlabel | Prompt utama untuk percobaan robot berikutnya; hasil OP3 Hybrid belum diukur |
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
