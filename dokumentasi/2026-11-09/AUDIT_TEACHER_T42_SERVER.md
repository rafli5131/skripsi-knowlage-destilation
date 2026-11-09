# Audit teacher T42 di server lab

**Status:** hasil audit server [tersedia dalam JSON](../../audit_teacher_t42_LTOW7Xw5.json), dibawa oleh commit `04d697c`. Keluaran skrip menunjukkan `complete: true`, `issues: []`, sembilan pemeriksaan untuk masing-masing teacher dan empat pemeriksaan lintas-teacher semuanya lulus. Skrip dijalankan pengguna di server; manifest dan bobot privatnya tetap berada di server dan tidak diverifikasi ulang secara langsung dari robot.

Teacher YOLO11n memiliki 2.590.425 parameter, hash checkpoint `8e5416a393fd4f310d0f398a7308a43149cb856f2f88d6f563a8296b9cf02968` dan durasi training tercatat 3.538,12 detik. Teacher YOLO11s memiliki 9.428.953 parameter, hash `fc9ec7a8bcb11f16ddf01233211aa037e41c8e5df58ea7b2adf696d04fe7f4f4` dan durasi 4.976,11 detik. Audit memeriksa hash manifest, checkpoint, bobot pralatih, fingerprint dan YAML yang tercatat, juga kesesuaian konfigurasi, versi dan identitas VAL. Audit tidak menghitung ulang seluruh byte dataset maupun memverifikasi ulang secara independen bahwa proses training mengikuti seluruh catatan manifest.

## Cara menjalankan

Skrip [`scripts/audit_t42_teacher_server2_readonly.py`](../../scripts/audit_t42_teacher_server2_readonly.py) tersedia di repo pada commit `483f4d9`. Bila diperlukan pemeriksaan ulang, jalankan pada server:

```bash
cd "$HOME/skripsi/skripsi-knowlage-destilation"
python3 scripts/audit_t42_teacher_server2_readonly.py
```

Kirim keluaran JSON ringkasnya untuk ditinjau. Skrip hanya membaca manifest, checkpoint, bobot COCO, data YAML, fingerprint dan JSON evaluasi, lalu mencetak hasil ke terminal; tidak memulai training dan tidak menulis berkas hasil. Kode keluar `0` berarti semua cek otomatis lulus; `1` berarti ada cek gagal atau berkas tidak bisa dibaca. Baris `issues` menampilkan penyebabnya. Jika file dipindah dari lokasi pada manifest, skrip dapat melaporkan berkas tidak ditemukan meski salinannya ada di tempat lain.

Skrip memeriksa hash manifest dan checkpoint terhadap evaluasi, bobot pralatih resmi terhadap protokol, identitas/status/seed, konfigurasi training yang tercatat, hash file fingerprint dan YAML data, kesamaan versi, serta status pemakaian split yang **dicatat manifest**. Ini belum membuktikan seluruh byte dataset dan tidak membuktikan kebenaran laporan manifest tentang jalannya training. Untuk pemeriksaan fingerprint byte dataset diperlukan prosedur audit dataset di server secara terpisah.

Pengujian simulasi lokal mencakup kasus lulus, checkpoint diubah, dan manifest hilang. Akses ke bobot dan manifest privat tetap di server; tidak perlu mengunggahnya ke GitHub.
