# Bukti uji KF/KNF dan audit repositori, 21 November 2026

Bukti per kebutuhan ada di [`bukti_kebutuhan/`](../bukti_kebutuhan/README.md), dibangkitkan dengan `python3 scripts/build_bukti_kebutuhan.py --replace` (tes: `tests/test_build_bukti_kebutuhan.py`). Status: KF-01, KF-02, KF-04, KNF-01 lulus pada 24 run T36; KF-03 lulus dengan catatan dari percobaan 27 (ID bola 2 pada 382/382 frame, kotak bola kedua pada 13 frame); KF-05 lulus untuk enam tangkapan preview. Minimum KNF-01 adalah 9,69 FPS per run (T36), bukan 9,87 (rerata model T37). Status KF-03 menunggu konfirmasi Bhre.

Persetujuan D18 adalah lisan pada 12 November 2026; baris D18 di `docs/DECISIONS.md` bertanggal 11 November.

Audit hash manifest: [`analisis_performa/AUDIT_HASH_MANIFEST_20261121.md`](../analisis_performa/AUDIT_HASH_MANIFEST_20261121.md). Bagian `tables` di `analisis_performa/manifest.json` mencatat versi 19 Oktober; jangan memakainya sebagai hash tabel saat ini.

Masih terbuka: jalur angka utama T38/T43 dan penyajian CPU RM5 (keputusan Bhre dan pembimbing). Tidak ada pekerjaan tersisa di robot atau server.
