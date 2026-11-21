# BAB 6 PENGUJIAN DAN PEMBAHASAN

> Draf berbasis bukti yang tersedia. Pengujian fungsional dan nonfungsional berikut dinilai secara retrospektif dari log pengukuran, bukan dari skenario uji baru.

## 6.1 Uji fungsional dan nonfungsional

Pengujian memakai pendekatan kotak hitam: setiap kebutuhan dinilai dari masukan dan keluaran sistem tanpa memeriksa struktur internal kode (Khan dan Khan, 2012; Nidhra dan Dondeti, 2012). Kasus uji disusun dari indikator pada Bab 4 dan dinilai terhadap log 24 run live (4 model × diam/berjalan × 3 ulangan) serta satu sesi pelacakan bola bergerak. Kriteria lulus dirumuskan sesudah data tersedia, sehingga penilaian ini bersifat retrospektif.

| ID uji | Kebutuhan | Hasil yang diharapkan | Hasil aktual | Status |
|---|---|---|---|---|
| UJ-KF-01 | KF-01 Menerima citra kamera OP3 | Setiap run memproses frame dan error frame bernilai nol | 24/24 run; 17.090 frame terproses tanpa error | Lulus |
| UJ-KF-02 | KF-02 Mendeteksi bola, gawang, dan robot | Ketiga kelas muncul sebagai kotak berlabel pada setiap run | 24/24 run memuat ketiga kelas; cakupan frame terendah: bola 100%, gawang 92,5%, robot 100% | Lulus |
| UJ-KF-03 | KF-03 ID pelacakan pada mode tambahan | Bola utama memperoleh ID dan ID tersebut tetap muncul selama bola bergerak | ID bola utama muncul pada 382/382 frame, sementara pusatnya bergeser 257,2 px (X) dan 130,8 px (Y); kotak bola kedua dengan ID lain muncul pada 13 frame | Lulus dengan catatan |
| UJ-KF-04 | KF-04 Mencatat runtime per frame | Setiap baris memuat timestamp, durasi tahap, CPU, RSS, dan status error | 9/9 log jendela di repositori lengkap; 24/24 log mentah cocok dengan T36 | Lulus |
| UJ-KF-05 | KF-05 Menampilkan preview deteksi | Kotak, kelas, confidence, dan ID tampak pada preview | Enam tangkapan dari empat model memenuhi | Lulus untuk contoh yang tersedia |
| UJ-KNF-01 | KNF-01 Laju pemrosesan | FPS efektif rata-rata tiap run minimal 8 FPS | 24/24 run; terendah 9,69 FPS (teacher, diam, ulangan 3) | Lulus |

KF-02 hanya menilai keberadaan kelas dan kotak pada keluaran; ketepatannya terhadap label acuan dibahas pada subbab 6.2 dan 6.3. KF-03 diuji pada satu sesi sekitar 30 detik dengan KD Hybrid seed 1337. Kotak bola kedua yang muncul sesaat tidak menggantikan ID utama, tetapi menunjukkan adanya kotak ganda atau deteksi palsu. Tangkapan preview pada KF-05 tidak membuktikan preview bebas macet sepanjang setiap run. KNF-01 dinilai dari rerata per run; FPS pada bin 2 detik dapat turun di bawah 8 tanpa membatalkan kriteria.

Prosedur, data per run, gambar, dan manifest hash setiap kasus uji tersedia di [`bukti_kebutuhan/`](../../bukti_kebutuhan/README.md).

## 6.2 Akurasi pada TEST

Nilai student adalah rerata tiga seed; teacher memakai satu checkpoint. F1 adalah harmonic mean precision dan recall makro. TEST terdiri dari 592 gambar dan sudah digunakan pada tahap sebelumnya.

| Model | mAP50 | mAP50–95 | Precision | Recall | F1 utama |
|---|---:|---:|---:|---:|---:|
| Teacher YOLO11n | 0,9642 | 0,7800 | 0,8915 | 0,9697 | 0,9290 |
| Hybrid full | 0,9583 | 0,7469 | 0,8519 | 0,9698 | 0,9071 |
| Supervised | 0,9601 | 0,7225 | 0,8609 | 0,9699 | 0,9121 |
| KD murni | 0,9446 | 0,6630 | 0,7547 | 0,9631 | 0,8462 |

Hybrid memperoleh rerata mAP50–95 lebih tinggi 0,0244 daripada supervised, tetapi F1-nya sekitar 0,005 lebih rendah. Tiga seed mendukung analisis eksploratif, bukan kesimpulan signifikansi yang kuat. Rincian simpangan baku dan sumber: [T05](../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md).

Angka TEST dihitung dengan validator Ultralytics (`model.val`), yang memakai tensor 672 × 672 dan NMS *multi-label*, sedangkan robot memakai `model.predict` dengan tensor 640 × 640. Pemeriksaan ulang pada ambang yang sama menghasilkan selisih rerata kelompok *student* paling besar 0,0035 untuk mAP50–95 dan 0,0024 untuk F1, dengan urutan mAP50–95 yang tetap. Pada teacher, mAP50–95 berubah dari 0,7800 menjadi 0,7791 dan F1 dari 0,9290 menjadi 0,9120, terutama karena precision turun. Rincian: [verifikasi *student*](../../analisis_performa/lab_server/verifikasi_jalur_test_20261113/RINGKASAN.md) dan [verifikasi teacher](../../analisis_performa/lab_server/verifikasi_jalur_test_20261116_teacher/RINGKASAN.md).

## 6.3 Evaluasi frame kamera OP3 T38

T38 menggunakan 260 frame yang sama untuk empat checkpoint, meliputi 200 frame berobjek dan 60 negatif. Sebanyak 50 frame gawang parsial dilaporkan terpisah. F1 utama dihitung ulang sebagai `2 × precision makro × recall makro / (precision makro + recall makro)` dari nilai presisi penuh CSV T38; F1 pelengkap adalah rerata F1 per kelas yang sudah dilaporkan T38. [CSV turunan dan hash](../../dokumentasi/2026-11-12/T38_F1_D11_turunan.csv) menyimpan angka sebelum pembulatan tampilan; [manifest](../../dokumentasi/2026-11-12/T38_F1_D11_manifest.json) mencatat sumbernya.

| Model | mAP50–95 | Precision makro | Recall makro | F1 utama D11 | F1 per kelas T38 | Frame negatif dengan FP |
|---|---:|---:|---:|---:|---:|---:|
| Teacher | 0,5004 | 0,8690 | 0,6833 | 0,7651 | 0,6829 | 2/60 |
| Hybrid seed 1337 | 0,4885 | 0,6836 | 0,5583 | 0,6146 | 0,5121 | 21/60 |
| Supervised seed 1337 | 0,4414 | 0,7855 | 0,5729 | 0,6626 | 0,6054 | 0/60 |
| KD murni seed 42 | 0,4218 | 0,7386 | 0,4729 | 0,5766 | 0,5008 | 0/60 |

Pada confidence >0,25 dan pencocokan IoU ≥0,5, Hybrid mencocokkan 2 dari 80 kotak gawang, sedangkan supervised 21 dari 80. AP dan recall pada satu ambang menjawab hal berbeda. Set ini retrospektif, label awal dibantu KD murni, berasal dari satu rangkaian dan termasuk sesi objek bergerak; hasil tidak membuktikan generalisasi lintas adegan atau bahwa seluruh set merepresentasikan objek statis. [T38](../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) dan [confusion matrix](../../dokumentasi/model/README.md) memuat detail.

### 6.3.1 Pemeriksaan jalur inferensi dan set T43

Pada T38, AP dihitung lewat `model.val` (tensor 512 × 672), sedangkan precision, recall, dan F1 dihitung lewat `model.predict` (tensor 480 × 640). Perhitungan ulang seluruh metrik lewat `model.predict` menghasilkan nilai berikut ([T44](../../analisis_performa/tabel/T44_jalur_tunggal_op3_t38_t43.md)).

| Model | mAP50–95 T38 (`model.val`) | mAP50–95 T38 (`model.predict`) | F1 T38 runtime | mAP50–95 T43 (`model.predict`) | F1 T43 runtime |
|---|---:|---:|---:|---:|---:|
| Teacher | 0,5004 | 0,5041 | 0,7728 | 0,5473 | 0,6616 |
| Hybrid seed 1337 | 0,4885 | 0,4307 | 0,6186 | 0,8900 | 0,9958 |
| Supervised seed 1337 | 0,4414 | 0,4216 | 0,6626 | 0,7828 | 0,9081 |
| KD murni seed 42 | 0,4218 | 0,4729 | 0,5835 | 0,7239 | 0,6667 |

Urutan mAP50–95 T38 berubah ketika jalur diganti, dan selisih Hybrid terhadap supervised menyusut dari 0,0471 menjadi 0,0091. Pada teacher di T43, perubahan bentuk masukan dari 512 × 672 ke 480 × 640 menurunkan AP50 gawang dari 0,9946 menjadi 0,1112, sedangkan penggantian NMS *multi-label* tidak mengubah nilai tersebut. T43 adalah evaluasi eksploratif pada 260 frame dari satu susunan adegan. Keunggulan Hybrid pada T43 bergantung pada konvensi kotak gawang bagian bawah, dan urutan mAP50–95 berubah antarpeninjau ([sensitivitas T43](../../analisis_performa/tabel/T43_sensitivitas_label_52.md)).

> Catatan draf: jalur yang dipakai sebagai angka utama T38/T43 pada naskah akhir belum diputuskan.

## 6.4 Runtime pada OP3

Nilai berikut adalah rerata ± simpangan baku sampel dari tiga rerata run, bersumber dari [T37](../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md).

| Model | Kondisi | Latensi (ms) | FPS | CPU (% satu CPU logis) | RSS (MiB) |
|---|---|---:|---:|---:|---:|
| Teacher | Diam | 96,24 ± 3,60 | 9,88 ± 0,31 | 1338,90 ± 9,65 | 370,58 ± 1,29 |
| Hybrid | Diam | 64,70 ± 1,92 | 13,60 ± 0,35 | 1305,97 ± 4,91 | 358,87 ± 1,24 |
| Supervised | Diam | 73,12 ± 3,27 | 12,14 ± 0,29 | 1299,18 ± 3,32 | 355,93 ± 3,32 |
| KD murni | Diam | 74,09 ± 1,04 | 12,07 ± 0,05 | 1300,21 ± 2,44 | 356,97 ± 5,92 |
| Teacher | Berjalan | 95,85 ± 1,27 | 9,87 ± 0,17 | 1333,54 ± 4,08 | 372,42 ± 5,11 |
| Hybrid | Berjalan | 71,47 ± 2,98 | 12,54 ± 0,38 | 1303,77 ± 3,88 | 356,31 ± 2,09 |
| Supervised | Berjalan | 70,80 ± 2,71 | 12,64 ± 0,52 | 1301,13 ± 6,03 | 359,16 ± 4,76 |
| KD murni | Berjalan | 72,65 ± 2,55 | 12,21 ± 0,15 | 1295,65 ± 1,35 | 360,18 ± 4,69 |

Pada sampel ini, Hybrid memiliki latensi lebih rendah dan FPS lebih tinggi daripada teacher pada kedua kondisi. CPU semua model sekitar 1.300% satu CPU logis, sehingga bukan pembeda efisiensi yang jelas pada pengukuran ini. RSS hanya mencerminkan proses detektor. Run dikelompokkan lintas hari dan tidak dilakukan serentak; hasil ini tidak membuktikan penyebab perbedaan atau kesetaraan fisik sepenuhnya. [Grafik per waktu dan per ulangan](../../dokumentasi/model/gabungan/README.md) menggunakan bin 2 detik.

Rincian per tahap dari log mentah yang sama ([T45](../../analisis_performa/tabel/T45_rincian_latensi_dan_cpu_op3.md)) menunjukkan bahwa inferensi mendominasi latensi: sekitar 77 ms untuk teacher dan 45 sampai 53 ms untuk ketiga *student*. Sisa waktu di luar tiga tahap Ultralytics, sekitar 12 sampai 15 ms, hampir sama pada semua model karena memuat pelacakan, penggambaran preview, dan penerbitan pesan ROS. Latensi pada tabel di atas adalah latensi node secara keseluruhan, bukan latensi model saja.

CPU sekitar 1.300% satu CPU logis setara dengan 81 sampai 84% dari 16 CPU logis. Uji ulang offline tanpa ROS dan kamera menunjukkan bahwa tanpa pelacakan, CPU proses sekitar 400% (sesuai empat thread PyTorch), sedangkan dengan pelacakan aktif thread OpenBLAS ikut berjalan dan CPU naik mendekati 1.000%. Pada uji ulang tanpa pelacakan tersebut, waktu CPU per frame teacher 147,3 ms dan Hybrid 71,3 ms. Karena hanya satu ulangan dan tidak melibatkan kamera, angka ini menjadi analisis pendukung, bukan pengganti T37.

## 6.5 Waktu dan ablasi tambahan

[T35](../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md) memisahkan waktu training student, satu sesi TEST multi-model, dan benchmark L40. Durasi sesi multi-model bukan durasi per checkpoint; waktu teacher utama dengan provenance setara tidak tersedia. Benchmark server bukan runtime OP3.

Pada VAL T42, teacher YOLO11n/s mencapai mAP50–95 0,7760/0,7843 dan student masing-masing 0,7482 ± 0,0003/0,7473 ± 0,0003. Teacher s yang lebih tinggi tidak menghasilkan rerata mAP student yang lebih tinggi dalam eksperimen ini. T42 memakai teacher yang dilatih ulang, hanya satu teacher per ukuran, dan tiga seed student; ia bukan TEST atau pengganti checkpoint utama. Lihat [T42](../../analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md).
