# Log progres 21 November 2026

Pekerjaan hari ini hanya di laptop dan repositori. Tidak ada eksperimen, robot, atau server yang dipakai.

## Bukti uji kebutuhan

Folder baru [`bukti_kebutuhan/`](../../bukti_kebutuhan/README.md) mengumpulkan bukti KF-01 sampai KF-05 dan KNF-01 per subfolder. Isinya dibangkitkan oleh `scripts/build_bukti_kebutuhan.py` dari berkas yang sudah ada di repositori, beserta manifest SHA-256 sumber dan keluaran. Kriteria lulus disusun retrospektif dari indikator Bab 4 (D18).

| Kebutuhan | Status | Ringkasan |
|---|---|---|
| KF-01 | Lulus | 24/24 run, 17.090 frame tanpa error |
| KF-02 | Lulus | 24/24 run memuat ketiga kelas; cakupan gawang terendah 92,5% |
| KF-03 | Lulus dengan catatan | Percobaan 27: ID bola 2 pada 382/382 frame selama bola bergerak; kotak bola kedua dengan ID lain pada 13 frame |
| KF-04 | Lulus | 9/9 log jendela di repositori lengkap; 24/24 log mentah cocok T36 (T45) |
| KF-05 | Lulus untuk contoh yang tersedia | Enam tangkapan dari empat model |
| KNF-01 | Lulus | 24/24 run; terendah 9,69 FPS (teacher, diam, ulangan 3) |

Status KF-03 sebelumnya ditulis "belum dinyatakan lulus" di Bab 6 karena sesi bola bergerak percobaan 27 belum dirujuk. Status "lulus dengan catatan" perlu dikonfirmasi Bhre. Angka minimum KNF-01 memakai nilai per run (9,69 FPS dari T36). Angka 9,87 FPS pada log 11 November adalah rerata per model T37 dan bukan dasar penilaian KNF-01.

## Perbaikan dan pembaruan

- `agent.md`: tanggal persetujuan disamakan dengan D18 dan `configs/analysis.yaml` (lisan, 12 November 2026); kalimat "tanggal dan bentuk persetujuan belum dicatat" dihapus.
- Bab 3: pernyataan empat thread intra-op dan dua inter-op diberi batas sesuai T45 (metadata dicatat sebelum inferensi pertama; jumlah aktual saat run tidak terekam).
- Bab 4: definisi kebutuhan fungsional dan nonfungsional dengan rujukan Glinz (2007), serta tautan bukti per kebutuhan.
- Bab 6: subbab 6.1 diubah menjadi tabel kasus uji kotak hitam (Khan dan Khan, 2012; Nidhra dan Dondeti, 2012); subbab 6.2 diberi catatan jalur TEST (D23, D24); subbab 6.3.1 baru memuat T44 dan ringkasan T43; subbab 6.4 diberi rincian latensi per tahap dan penjelasan CPU dari T45.
- Bab 7: kesimpulan 1 dan 5 serta saran diperbarui.
- Judul ketujuh bab draf tidak lagi memakai tanda pisah em dash.
- `REFERENSI_SKRIPSI.bib`: tiga entri baru (Glinz 2007, Khan dan Khan 2012, Nidhra dan Dondeti 2012) dari PDF lokal. Halaman dan DOI Glinz belum diverifikasi.
- Audit hash: `scripts/audit_manifest_hashes.py` dan [`AUDIT_HASH_MANIFEST_20261121.md`](../../analisis_performa/AUDIT_HASH_MANIFEST_20261121.md). Dari 914 pasangan, 777 cocok, 28 hanya beda akhir baris, 80 mencatat versi lama yang ada di riwayat Git, dan 29 tidak ditemukan (18 PNG akurasi yang sudah diketahui sejak 12 November, sisanya README). Manifest tidak diubah.
- Tes baru `tests/test_build_bukti_kebutuhan.py`; 39 tes lulus (tanpa `tests/test_kd_hybrid.py`, yang memerlukan PyTorch).

## Temuan audit yang tidak diubah

- Sekitar 400 tautan relatif di README percobaan menunjuk berkas lokal robot (telemetri, preview, `runs/`, `data/`) yang sengaja tidak masuk Git, atau berada di README arsip yang disalin ke folder lain. Dokumen aktif (README utama, indeks, draf bab, tabel, keputusan) tidak memiliki tautan rusak ke berkas yang seharusnya ada di Git.
- Pilihan jalur angka utama T38/T43 (`model.val` atau `model.predict`) dan cara penyajian CPU untuk RM5 belum diputuskan; Bab 6 menyajikan keduanya dan memberi catatan draf.
- Draf tujuh bab masih ringkas dan baru memuat rujukan pada Bab 4 dan Bab 6.
