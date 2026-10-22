# T16. latensi frame tetap

**Status: belum diukur dengan protokol frame tetap di OP3.** Log kamera live yang ada mengukur callback pada stream yang berubah, sehingga tidak dapat dilabeli sebagai benchmark identik per-frame. Benchmark server/L40 juga bukan hasil CPU OP3.

| Bukti tersedia | Nilai | Rujukan | Batas penggunaan |
|---|---|---|---|
| Runtime camera stream, KD murni dan Hybrid | Callback median/P95 per kondisi tersedia | [T19](T19_servo_idle_vs_walking.md) dan laporan eksperimen 18–21 | Bukan fixed-frame latency; stream dan adegan berbeda |
| Status pengukuran fixed frame di OP3 | Tidak ada run tersimpan | [CSV status](T16_latensi_frame_tetap.csv) | Tidak boleh diisi dengan angka server atau latency dari kamera live |

Untuk angka fixed-frame yang sesungguhnya diperlukan set citra tetap, pengulangan inferensi per frame, warm-up yang didefinisikan, dan log terpisah di NUC. Pengukuran ini belum dibuat agar tidak mengganggu live detector yang sedang berjalan.
