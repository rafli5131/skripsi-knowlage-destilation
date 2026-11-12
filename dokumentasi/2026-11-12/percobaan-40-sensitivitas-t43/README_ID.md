# Uji sensitivitas T43 — 12 November 2026

**Bagian A dan B selesai.**

[Tabel dan metode](../../../analisis_performa/tabel/T43_sensitivitas_confidence.md) · [CSV rinci](../../../analisis_performa/tabel/T43_sensitivitas_confidence.csv) · [Bagian B: status](../../../analisis_performa/tabel/T43_sensitivitas_label_52.md)

Grafik ID dan EN di `grafik/`: recall dan F1 masing-masing kelas untuk empat model, dalam kondisi diam, berjalan di tempat dan gabungan. Ambang operasi tetap >0,25. AP dan hasil operasi baseline per frame terverifikasi sebelum sapuan.

## Temuan perbedaan jalur AP dan prediksi

AP T43 dihitung dengan `model.val`, sedangkan sapuan dan precision/recall/F1 menggunakan `model.predict`. Pada pemeriksaan lokal model teacher, validator menerima tensor **512 × 672** setelah padding, sedangkan prediktor menerima **480 × 640**. Kode Ultralytics validator juga menggunakan NMS `multi_label=True`; tidak dapat diasumsikan kedua jalur memiliki postprocessing yang identik. Pada satu frame yang sama, prediksi gawang teacher tidak muncul di atas 0,001 pada jalur operasi default, tetapi confidence berubah ketika ukuran/padding prediksi diubah. Diagnosis ini menunjukkan bahwa perbedaan preprocessing dan postprocessing **dapat memengaruhi** hasil; pengaruh masing-masing belum diisolasi.

Sebagai pemeriksaan tambahan, keluaran validator teacher yang disimpan dalam JSON (nilai dan kotak dibulatkan) menghasilkan 200/200 pasangan gawang pada floor 0,001 dan 37/200 pada confidence >0,25; pada jalur prediksi operasi hasilnya 68/200 dan 0/200. Hasil ini tidak menggantikan tabel utama karena jalurnya berbeda. Jangan menyimpulkan bahwa selisih AP dan F1 hanya akibat confidence atau kalibrasi, dan jangan mengganti ambang operasi berdasarkan set ini.

## Peninjauan manusia

Peninjau kedua adalah Dipo. Aturan tertulis dibekukan setelah klarifikasi Bhre dan sebelum jendela peninjau dibuka; titik tengah bagian tiang yang terlihat adalah batas atas kotak gawang, dan kotak robot mencakup badan, tangan dan kaki namun mengecualikan bagian hitam di atas badan sesuai keputusan sebelumnya. Aturan ini dipertegas setelah label awal T43, sehingga perbedaan dengan label awal mungkin mencerminkan aturan dan peninjau sekaligus. Label Dipo lengkap dan cocok dengan 52 frame sumber; hasil awal dan keterbatasan ada pada tabel bagian B. Konvensi alternatif telah dilabeli Dipo dan dievaluasi. Frame, label, dan prediksi per frame tetap lokal.

## Integritas tabel terdahulu

Tabel utama T43 hanya ditambahi tautan sensitivitas tanpa mengubah angkanya. Karena penambahan tersebut mengubah hash, [arsip tabel sebelum penambahan](arsip_tabel_T43_sebelum_sensitivitas.md) dipertahankan dengan hash yang cocok pada manifest historis percobaan 39. Manifest historis mengacu ke versi sebelum penambahan; manifest percobaan 40 mencatat kedua versi.

## Progres bagian B

Pada IoU ≥0,5, 40/40 kotak berpasangan untuk setiap kelas. Rata-rata IoU bola 0,6811; gawang 0,6389; robot 0,8882. Urutan mAP50–95 berubah antara label Bhre dan Dipo; klarifikasi aturan setelah tinjauan Bhre membuat efek aturan dan peninjau tercampur. Evaluasi menggunakan foto yang sama, dan hasil alternatif belum tersedia.

## Hasil lengkap tiga set label

[Tabel, kesepakatan, urutan dan batas interpretasi](../../../analisis_performa/tabel/T43_sensitivitas_label_52.md) · [CSV per kelas](../../../analisis_performa/tabel/T43_sensitivitas_label_52.csv) · [Grafik perbandingan](grafik/perbandingan_tiga_label_id.png). Hasil tiga set menggunakan 52 frame identik; koreksi label bila ada dicatat pada manifest penyelesaian label alternatif. Data mentah, label, log dan prediksi per frame tetap lokal.
