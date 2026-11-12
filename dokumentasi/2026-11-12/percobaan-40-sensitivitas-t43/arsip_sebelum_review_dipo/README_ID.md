# Uji sensitivitas T43 — 12 November 2026

**Bagian A selesai; bagian B menunggu peninjau kedua dan sesi label alternatif.**

[Tabel dan metode](../../../analisis_performa/tabel/T43_sensitivitas_confidence.md) · [CSV rinci](../../../analisis_performa/tabel/T43_sensitivitas_confidence.csv) · [Bagian B: status](../../../analisis_performa/tabel/T43_sensitivitas_label_52.md)

Grafik ID dan EN di `grafik/`: recall dan F1 masing-masing kelas untuk empat model, dalam kondisi diam, berjalan di tempat dan gabungan. Ambang operasi tetap >0,25. AP dan hasil operasi baseline per frame terverifikasi sebelum sapuan.

## Temuan perbedaan jalur AP dan prediksi

AP T43 dihitung dengan `model.val`, sedangkan sapuan dan precision/recall/F1 menggunakan `model.predict`. Pada pemeriksaan lokal model teacher, validator menerima tensor **512 × 672** setelah padding, sedangkan prediktor menerima **480 × 640**. Kode Ultralytics validator juga menggunakan NMS `multi_label=True`; tidak dapat diasumsikan kedua jalur memiliki postprocessing yang identik. Pada satu frame yang sama, prediksi gawang teacher tidak muncul di atas 0,001 pada jalur operasi default, tetapi confidence berubah ketika ukuran/padding prediksi diubah. Diagnosis ini menunjukkan bahwa perbedaan preprocessing dan postprocessing **dapat memengaruhi** hasil; pengaruh masing-masing belum diisolasi.

Sebagai pemeriksaan tambahan, keluaran validator teacher yang disimpan dalam JSON (nilai dan kotak dibulatkan) menghasilkan 200/200 pasangan gawang pada floor 0,001 dan 37/200 pada confidence >0,25; pada jalur prediksi operasi hasilnya 68/200 dan 0/200. Hasil ini tidak menggantikan tabel utama karena jalurnya berbeda. Jangan menyimpulkan bahwa selisih AP dan F1 hanya akibat confidence atau kalibrasi, dan jangan mengganti ambang operasi berdasarkan set ini.

## Peninjauan manusia

Peninjau kedua adalah Dipo. Aturan tertulis dibekukan setelah klarifikasi Bhre dan sebelum jendela peninjau dibuka; titik tengah bagian tiang yang terlihat adalah batas atas kotak gawang, dan kotak robot mencakup badan, tangan dan kaki namun mengecualikan bagian hitam di atas badan sesuai keputusan sebelumnya. Aturan ini dipertegas setelah label awal T43, sehingga perbedaan dengan label awal mungkin mencerminkan aturan dan peninjau sekaligus. Belum ada data Dipo; konvensi alternatif juga belum dilabeli. Frame, label, dan prediksi per frame tetap lokal.

## Integritas tabel terdahulu

Tabel utama T43 hanya ditambahi tautan sensitivitas tanpa mengubah angkanya. Karena penambahan tersebut mengubah hash, [arsip tabel sebelum penambahan](arsip_tabel_T43_sebelum_sensitivitas.md) dipertahankan dengan hash yang cocok pada manifest historis percobaan 39. Manifest historis mengacu ke versi sebelum penambahan; manifest percobaan 40 mencatat kedua versi.
