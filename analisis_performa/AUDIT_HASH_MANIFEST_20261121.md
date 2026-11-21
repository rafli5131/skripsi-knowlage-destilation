# Audit hash manifest repositori

Dibangkitkan oleh `scripts/audit_manifest_hashes.py` pada 2026-11-21. Audit ini
baca-saja: manifest dan berkas sumber tidak diubah. Hanya pasangan path dan SHA-256 yang menunjuk ke
berkas yang dilacak Git yang diperiksa; berkas lokal robot atau server di luar Git tidak dihitung.

| Status | Jumlah | Arti |
|---|---:|---|
| `cocok` | 777 | Hash berkas saat ini sama dengan manifest |
| `beda_akhir_baris` | 28 | Isi sama; hanya akhir baris CRLF/LF yang berbeda |
| `versi_lama_di_git` | 80 | Manifest mencatat versi lama yang ada di riwayat Git; berkas diperbarui sesudah manifest ditulis |
| `tidak_ditemukan` | 29 | Versi yang di-hash tidak ditemukan di riwayat Git |

## Manifest dengan entri yang perlu dibaca hati-hati

| Manifest | Cocok | Beda akhir baris | Versi lama di Git | Tidak ditemukan |
|---|---:|---:|---:|---:|
| `analisis_performa/lab_server/manifest.json` | 172 | 0 | 5 | 0 |
| `analisis_performa/manifest.json` | 128 | 8 | 58 | 0 |
| `dokumentasi/2026-11-12/percobaan-39-evaluasi-t43/manifest_hasil_sha256.json` | 31 | 0 | 1 | 0 |
| `dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43/arsip_sebelum_hasil_akhir/manifest_hasil_sha256.json` | 32 | 0 | 0 | 4 |
| `dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43/arsip_sebelum_review_dipo/manifest_hasil_sha256.json` | 19 | 0 | 0 | 4 |
| `dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43/arsip_sebelum_status_akhir/manifest_hasil_sha256.json` | 47 | 0 | 0 | 1 |
| `dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43/manifest_hasil_sha256.json` | 50 | 0 | 3 | 0 |
| `dokumentasi/2026-11-16/percobaan-41-jalur-tunggal-dan-runtime-op3/arsip_sebelum_audit_akhir/manifest_hasil_sha256.json` | 44 | 0 | 1 | 2 |
| `dokumentasi/2026-11-16/percobaan-41-jalur-tunggal-dan-runtime-op3/arsip_sebelum_penggabungan_github/manifest_hasil_sha256.json` | 53 | 0 | 4 | 0 |
| `dokumentasi/2026-11-16/percobaan-41-jalur-tunggal-dan-runtime-op3/manifest_hasil_sha256.json` | 60 | 0 | 4 | 0 |
| `dokumentasi/model/manifest_confusion_matrix.json` | 39 | 1 | 4 | 0 |
| `dokumentasi/model/manifest_grafik_garis_akurasi.json` | 13 | 0 | 0 | 18 |

Sebagian besar entri `versi_lama_di_git` berasal dari `analisis_performa/manifest.json`. Bagian `tables`
manifest itu ditulis pada 19 Oktober 2026, ketika banyak tabel T02 sampai T26 masih berupa kerangka atau
penanda `[BELUM DIUKUR]`, dan tidak diperbarui ketika tabel diisi atau diberi kolom interval. Pada T05,
perubahan sejak versi tersebut berada di kolom interval bootstrap dan keterangan, bukan pada nilai rerata.
Berkas Markdown dengan status selain `cocok` umumnya README yang kemudian ditambah tautan.

## Berkas non-Markdown yang versinya tidak ditemukan

- `dokumentasi/model/supervised/garis_akurasi_val_per_epoch_supervised_id.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/kd_murni/garis_akurasi_val_per_epoch_kd_murni_id.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/kd_hybrid/garis_akurasi_val_per_epoch_kd_hybrid_id.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/teacher_yolo11n/garis_sapuan_confidence_val_teacher_yolo11n_id.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/kd_hybrid/garis_sapuan_confidence_val_kd_hybrid_id.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/supervised/garis_sapuan_confidence_val_supervised_id.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/kd_murni/garis_sapuan_confidence_val_kd_murni_id.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/gabungan/garis_akurasi_val_per_epoch_tiga_metode_id.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/gabungan/garis_sapuan_confidence_val_empat_model_id.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/supervised/garis_akurasi_val_per_epoch_supervised_en.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/kd_murni/garis_akurasi_val_per_epoch_kd_murni_en.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/kd_hybrid/garis_akurasi_val_per_epoch_kd_hybrid_en.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/teacher_yolo11n/garis_sapuan_confidence_val_teacher_yolo11n_en.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/kd_hybrid/garis_sapuan_confidence_val_kd_hybrid_en.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/supervised/garis_sapuan_confidence_val_supervised_en.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/kd_murni/garis_sapuan_confidence_val_kd_murni_en.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/gabungan/garis_akurasi_val_per_epoch_tiga_metode_en.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)
- `dokumentasi/model/gabungan/garis_sapuan_confidence_val_empat_model_en.png` (manifest `dokumentasi/model/manifest_grafik_garis_akurasi.json`)

Delapan belas PNG akurasi di `dokumentasi/model/` sudah dicatat pada
[audit grafik 12 November](../dokumentasi/2026-11-12/AUDIT_GRAFIK_AKURASI.md); versi reproduksi yang
terverifikasi ada di `dokumentasi/2026-11-12/grafik-akurasi-terverifikasi/`.

Rincian per entri: [`AUDIT_HASH_MANIFEST_20261121.csv`](AUDIT_HASH_MANIFEST_20261121.csv).
