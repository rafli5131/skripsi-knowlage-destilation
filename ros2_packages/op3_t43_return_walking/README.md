# Pemetaan kembali ke modul jalan T43

Package baru ini memakai monitor bersama `op3_t43_walk_ready`, memetakan 12 sendi kaki dan dua shoulder pitch dari action ke walking module, dan menjaga kepala pada `none`. Pemetaan dapat mengubah pose badan saat walking module menyesuaikan stance; operator harus siap mendampingi. Telemetry kepala dan preview dipantau, namun perintah stop tidak selalu menghentikan transisi `WalkingInitPose`. Tidak mengirim start gait. Catatan lokal di `runs/op3_t43_return_walking/`.
