# Audit sementara 52 frame tinjauan tanpa kotak prediksi

> **Pembaruan:** seluruh 52 frame sudah tersimpan. Operator memilih acuan gawang sebagai bagian bawah seperti label sekarang; catatan awal yang menyarankan seluruh rangka terlihat merupakan temuan sebelum keputusan tersebut. Lihat addendum 04 dan snapshot label awal yang dicatat di bawah.

Pemeriksaan membaca file dan log tanpa mengubah label. Pada saat pemeriksaan, frame 1–43 memiliki label dan entri log `bhre`; frame 44–52 belum memiliki label atau entri. Terdapat 46 entri log untuk 43 gambar, karena frame 15, 32 dan 37 disimpan dua kali. Penyimpanan ulang tidak otomatis merupakan kesalahan. Delapan label kosong pada 43 frame tersebut secara visual sesuai adegan tanpa target pada lembar kontak yang diperiksa.

Dari 43 frame, 35 memiliki masing-masing tiga kotak. Pada pemeriksaan visual, kotak gawang pada frame-frame berobjek mulai pada kira-kira baris y=104–195 dari tinggi 480 piksel, sementara rangka putih terlihat berlanjut sampai batas atas gambar. Ini perlu diperiksa ulang terhadap konvensi: satu kotak mencakup **seluruh rangka gawang yang tampak**, termasuk bagian yang mencapai batas gambar. Pada beberapa frame, sebagian kepala atau bagian samping robot juga tampak di luar kotak robot; periksa seluruh bagian robot yang terlihat. Temuan bersifat bantuan pemeriksaan visual, bukan koreksi otomatis atau verifikasi ground truth final.

Peninjau sebelumnya sudah berhenti; peninjau dibuka kembali pada frame 44 menggunakan identitas `bhre`. Operator dapat menyelesaikan sisa frame lalu memeriksa ulang kotak yang ditandai. Tinjauan ulang ini didorong oleh audit visual asisten; catat sebagai intervensi selama proses anotasi, bukan sebagai rangkaian pelabelan yang tidak menerima masukan sama sekali. Operator sebelumnya telah melihat preview Hybrid saat pengambilan; kotak prediksi tidak dimuat pada peninjau 52 frame.

## Status setelah 52 frame

Seluruh 52 gambar dan hash-nya cocok dengan manifest; semua memiliki label valid dan entri review `bhre` (55 entri karena tiga gambar disimpan ulang). Terdapat 40 frame masing-masing dengan tiga kotak dan 12 frame berlabel kosong. Pemeriksaan visual awal pada 12 frame kosong tidak menemukan target yang jelas.

Operator memilih mempertahankan gawang sebagai bagian bawah seperti label sekarang. [Addendum 04 lokal](../../../data/op3_camera_eval/experiments/t43_20261112/addendum_04_goal_lower_region.json) mencatat bahwa keputusan memperbarui konvensi awal setelah label sampel dibuat. Salinan 52 label sebelum QA tersimpan dalam [snapshot lokal](../../../data/op3_camera_eval/experiments/t43_20261112/blind_review_52/labels_blind_snapshot_before_qa/snapshot_manifest.json); label kerja asli tidak diubah.

Batas atas kotak gawang pada 40 frame berobjek berada pada y≈73–195 dari tinggi 480 piksel; variasi ini perlu dipertimbangkan bila menginginkan definisi yang dapat diulang. Posisi dalam gambar bervariasi antarframe, sehingga rentang ini sendiri bukan ukuran kesalahan. Beberapa kotak robot secara visual tampak belum meliputi bagian kepala; perlu penilaian operator sebelum label dibekukan. Perbandingan dengan T38 harus menyebut perbedaan konvensi label gawang; jangan menyatakan hasil sebanding tanpa kualifikasi. Sampel belum digunakan untuk pra-label union atau evaluasi.

## Konfirmasi konvensi dan penyelesaian

Operator mengonfirmasi bahwa label robot menggunakan kotak badan seperti yang ada dan bagian hitam di atas tidak perlu ditambahkan. [Addendum 05 lokal](../../../data/op3_camera_eval/experiments/t43_20261112/addendum_05_robot_body_box.json) mencatat pilihan ini; anjuran sebelumnya untuk memperluas kotak robot merupakan temuan sebelum konfirmasi dan tidak diterapkan. Operator juga memilih mempertahankan bagian bawah gawang. Seluruh 52 label tersimpan, dan [manifest penyelesaian tinjauan lokal](../../../data/op3_camera_eval/experiments/t43_20261112/blind_review_completion.json) mengikat gambar, label snapshot, log, dan addendum berdasarkan hash.

Status `complete` dalam manifest berarti tinjauan manual 52 sampel telah disimpan; ini bukan bukti label sempurna atau tanpa pengaruh. Batas atas kotak bagian bawah gawang belum didefinisikan dengan patokan fisik tetap dan perlu diterapkan sekonsisten mungkin pada sisa 260 frame. Preview Hybrid telah dilihat sebelumnya, asisten memberikan masukan saat tinjauan, dan kedua aturan diklarifikasi setelah sampel selesai. Perbedaan konvensi gawang dari T38 membatasi perbandingan langsung. Tidak ada pra-label model untuk 260 frame atau hasil evaluasi yang dibuat dalam pemeriksaan ini.
