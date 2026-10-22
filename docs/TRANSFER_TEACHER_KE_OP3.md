# Prosedur transfer teacher FP32 ke OP3

Teacher YOLO11n tidak disimpan di repo publik. Berkas lokal yang diverifikasi di lab/server:

```text
/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt
SHA-256: e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c
Ukuran: 5.481.875 byte
```

Hash cocok dengan entri `teacher_fp32` di `configs/model_registry.yaml`. Prosedur ini belum menjalankan transfer; gunakan hanya setelah Bhre menyetujui jalur transfer dan host/kredensial OP3 diketahui.

## Opsi transfer melalui SSH

Jalankan dari server lab setelah mengganti placeholder dengan alamat yang disetujui operator:

```bash
ssh <op3-user>@<op3-host> 'mkdir -p <repo-op3>/models_local'
scp /mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt \
  <op3-user>@<op3-host>:<repo-op3>/models_local/teacher_fp32_best.pt
```

Jika server tidak dapat menjangkau OP3, salin berkas lewat laptop operator atau media yang disetujui, lalu hitung hash sumber dan salinan untuk memastikan transfer utuh. Jangan mengirim bobot melalui repo publik.

## Verifikasi dan konfigurasi pada OP3

Di root repo OP3:

```bash
sha256sum models_local/teacher_fp32_best.pt
```

Hasil wajib sama dengan hash di atas. Buat `configs/model_registry_local.yaml` lokal dengan isi:

```yaml
teacher_fp32: models_local/teacher_fp32_best.pt
```

Berkas konfigurasi lokal dan direktori `models_local/` masuk `.gitignore`. Runtime membandingkan SHA-256 berkas lokal dengan hash teacher pada registry publik dan menolak ketidakcocokan. Metadata run mencatat apakah override digunakan, path lokal, dan hash registry. Jangan commit atau push berkas teacher maupun konfigurasi lokalnya.

## Hasil verifikasi lab/server

- Sumber teacher ada dan dapat dibaca pada server lab.
- SHA-256 aktual: `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`.
- Manifest sumber mencatat kelas `ball`, `gawang`, `robot`, PyTorch `2.4.1+cu121`, Ultralytics `8.4.130`, serta training selesai.
- Transfer ke OP3, verifikasi hash di OP3, dan inferensi teacher di robot belum dilakukan.
