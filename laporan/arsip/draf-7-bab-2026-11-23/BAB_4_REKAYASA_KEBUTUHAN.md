# BAB 4 REKAYASA KEBUTUHAN

> Identifikasi dan hasil uji disusun retrospektif dari implementasi dan log yang tersedia. Persyaratan pelacakan KF-03 adalah kemampuan tambahan historis, di luar tujuan wajib skripsi yang berfokus pada deteksi objek statis.

## 4.1 Lingkungan dan aktor

Sistem berjalan pada komputer onboard ROBOTIS OP3. Kamera menerbitkan citra melalui ROS 2; node detektor memprosesnya dengan checkpoint yang ditetapkan. Operator menata objek dan menetapkan kondisi fisik robot. Sistem dapat menerbitkan hasil, preview, dan log; node detektor tidak mengirim perintah motor.

## 4.2 Kebutuhan fungsional

Kebutuhan fungsional menyatakan fungsi atau perilaku masukan dan keluaran yang harus dimiliki sistem, sedangkan kebutuhan kinerja, misalnya laju pemrosesan, digolongkan sebagai kebutuhan nonfungsional (Glinz, 2007). Setiap kebutuhan diberi indikator yang dapat diperiksa dari keluaran sistem.

| ID | Kebutuhan | Indikator pemeriksaan | Sumber implementasi/bukti |
|---|---|---|---|
| KF-01 | Menerima citra kamera OP3 | Frame masuk diproses dan kesalahan frame dicatat | [Runtime](../../../docs/OP3_PYTORCH_RUNTIME.md), [T36](../../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md), [bukti KF-01](../../../bukti_kebutuhan/KF-01_menerima_citra/README.md) |
| KF-02 | Mendeteksi bola, gawang, dan robot | Keluaran memuat kelas dan kotak; ketepatan terhadap acuan dinilai terpisah | [T38](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md), log deteksi, [bukti KF-02](../../../bukti_kebutuhan/KF-02_deteksi_tiga_kelas/README.md) |
| KF-03 | Menyediakan ID pelacakan pada mode tambahan | ID tersedia dan kestabilan diuji pada objek bergerak | [Runtime](../../../docs/OP3_PYTORCH_RUNTIME.md), [bukti KF-03](../../../bukti_kebutuhan/KF-03_id_pelacakan/README.md); bukan tujuan wajib penelitian |
| KF-04 | Mencatat runtime per frame | Timestamp, durasi, CPU, RSS, dan error tersedia pada CSV | [T36](../../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md), log per frame, [bukti KF-04](../../../bukti_kebutuhan/KF-04_log_runtime/README.md) |
| KF-05 | Menampilkan preview deteksi | Kotak dan kelas tampak pada contoh preview | [Contoh media](../../../dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/README.md), [bukti KF-05](../../../bukti_kebutuhan/KF-05_preview/README.md) |

## 4.3 Kebutuhan nonfungsional

| ID | Kebutuhan | Kriteria | Sumber |
|---|---|---|---|
| KNF-01 | Laju pemrosesan | FPS efektif rata-rata tiap run minimal 8 FPS pada dua kondisi | [T36](../../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md), [bukti KNF-01](../../../bukti_kebutuhan/KNF-01_laju_pemrosesan/README.md) |

Batas ini berlaku untuk FPS efektif rerata run; grafik bin 2 detik dapat turun di bawah 8 FPS tanpa otomatis membatalkan kriteria rerata tersebut. Interpretasi hasil perlu membedakan kesalahan model, kesalahan frame, dan keterbatasan bukti preview.

Bukti setiap kebutuhan, tabel kasus uji, dan manifest hash dikumpulkan di [`bukti_kebutuhan/`](../../../bukti_kebutuhan/README.md). Hasil pengujiannya dibahas pada subbab 6.1.
