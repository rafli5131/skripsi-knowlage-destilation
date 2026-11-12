# BAB 4 — REKAYASA KEBUTUHAN

> Identifikasi dan hasil uji disusun retrospektif dari implementasi dan log yang tersedia. Persyaratan pelacakan KF-03 adalah kemampuan tambahan historis, di luar tujuan wajib skripsi yang berfokus pada deteksi objek statis.

## 4.1 Lingkungan dan aktor

Sistem berjalan pada komputer onboard ROBOTIS OP3. Kamera menerbitkan citra melalui ROS 2; node detektor memprosesnya dengan checkpoint yang ditetapkan. Operator menata objek dan menetapkan kondisi fisik robot. Sistem dapat menerbitkan hasil, preview, dan log; node detektor tidak mengirim perintah motor.

## 4.2 Kebutuhan fungsional

| ID | Kebutuhan | Indikator pemeriksaan | Sumber implementasi/bukti |
|---|---|---|---|
| KF-01 | Menerima citra kamera OP3 | Frame masuk diproses dan kesalahan frame dicatat | [Runtime](../../OP3_PYTORCH_RUNTIME.md), [T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md) |
| KF-02 | Mendeteksi bola, gawang, dan robot | Keluaran memuat kelas dan kotak; ketepatan terhadap acuan dinilai terpisah | [T38](../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md), log deteksi |
| KF-03 | Menyediakan ID pelacakan pada mode tambahan | ID tersedia dan kestabilan diuji pada objek bergerak | [Runtime](../../OP3_PYTORCH_RUNTIME.md); bukan tujuan wajib penelitian |
| KF-04 | Mencatat runtime per frame | Timestamp, durasi, CPU, RSS, dan error tersedia pada CSV | [T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md) dan log per frame |
| KF-05 | Menampilkan preview deteksi | Kotak dan kelas tampak pada contoh preview | [Contoh media](../../dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/README.md) |

## 4.3 Kebutuhan nonfungsional

| ID | Kebutuhan | Kriteria | Sumber |
|---|---|---|---|
| KNF-01 | Laju pemrosesan | FPS efektif rata-rata tiap run minimal 8 FPS pada dua kondisi | [T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md) |

Batas ini berlaku untuk FPS efektif rerata run; grafik bin 2 detik dapat turun di bawah 8 FPS tanpa otomatis membatalkan kriteria rerata tersebut. Interpretasi hasil perlu membedakan kesalahan model, kesalahan frame, dan keterbatasan bukti preview.
