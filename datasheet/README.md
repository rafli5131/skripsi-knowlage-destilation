# Salinan Datasheet Dataset

Dua berkas teks di direktori ini adalah salinan verbatim metadata dataset yang diekspor dari Roboflow. Salinan dibuat 9 Oktober 2026 dari:

`/mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/raw/advance_vision_human/`

| Berkas | SHA-256 | Isi utama |
| --- | --- | --- |
| [`README.dataset.txt`](README.dataset.txt) | `14b3de840ea3259fe6dcf511c2989ec6426324f12fca96097fa046d2e994cb8e` | Nama project, atribusi pengguna Roboflow, dan lisensi CC BY 4.0. |
| [`README.roboflow.txt`](README.roboflow.txt) | `42272ecc63630d753374fb4b8a3a1f7065bf1cb6d3aad01322e2829c2557816c` | Metadata export V1-Base: tanggal, jumlah gambar, format anotasi, resize, dan preprocessing. |

Metadata sumber menyebut project [Advance Vision Human di Roboflow Universe](https://universe.roboflow.com/humanoid-atom/advance_vision_human). Salinan ini hanya mencakup berkas teks datasheet, tidak mencakup gambar atau label dataset. Untuk isi split yang dipakai eksperimen, gunakan fingerprint file pada `artifacts/advance_vision_dataset_fingerprint.json` dan catatan di [`AUDIT_DATASET_SKRIPSI.md`](../AUDIT_DATASET_SKRIPSI.md).

README export mengidentifikasi versi sebagai `v1` (`V1-Base`). Skrip unduh proyek sumber menerima nomor versi melalui `ROBOFLOW_VERSION`, sehingga unduh ulang harus meminta versi `1`; setelah normalisasi, verifikasi isi file dengan fingerprint SHA-256 eksperimen. Dokumen ringkasan dataset lama di repository sumber masih menandai versi `UNRESOLVED`, sedangkan nilai `dataset_version: null` pada manifest teacher adalah keterbatasan provenance teacher, bukan versi export yang dipakai eksperimen ini.
