# T01. spesifikasi model

Status: Lengkap dari artefak historis.

| model | method | seed | parameters_before_fusion [count] | parameters_after_fusion [count] | GFLOPs @640 [GFLOPs] | checkpoint_size [MiB] | checkpoint_SHA256 | registry_manifest |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kd_seed1337 | Pure KD | 1337 | 810649 | 806613 | 2,4291 | 1,8190 | bb51513031b8b522303a6c51e7914f72adf523f4af1dad984415c69fe3833fe5 | runs/kd/yolo11_tiny_pure_kd_v4_seed1337/manifest.json |
| kd_seed2025 | Pure KD | 2025 | 810649 | 806613 | 2,4291 | 1,8190 | 79997050873a1b9cf2759148d8315546b81845b7c0e02e6bfca656534b280389 | runs/kd/yolo11_tiny_pure_kd_v4_seed2025/manifest.json |
| kd_seed42 | Pure KD | 42 | 810649 | 806613 | 2,4291 | 1,8191 | 2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3 | runs/kd/yolo11_tiny_pure_kd_v4_locked_seed42/manifest.json |
| supervised_seed1337 | Supervised student | 1337 | 810649 | 806613 | 2,4291 | 1,8211 | d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041 | runs/supervised/yolo11_tiny_supervised_seed1337/manifest.json |
| supervised_seed2025 | Supervised student | 2025 | 810649 | 806613 | 2,4291 | 1,8210 | 0157546d16279d48b8ca5e0ec147b771202353daeb6195eaab93cb8872098301 | runs/supervised/yolo11_tiny_supervised_seed2025/manifest.json |
| supervised_seed42 | Supervised student | 42 | 810649 | 806613 | 2,4291 | 1,8210 | c2d940ec3800dde0e311df310438eaba28b4013d7819ad958a79489c5b36568e | runs/supervised/yolo11_tiny_supervised_seed42_retry1/manifest.json |
| teacher_fp32 | Teacher | teacher | 2590425 | 2582737 | 6,5017 | 5,2279 | e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c | /mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/manifest.json |

Sumber: [per_model.csv](../../artifacts/thesis_analysis_final_corrected/per_model.csv) dan [model_registry.yaml](../../configs/model_registry.yaml).

Manifest teacher yang dirujuk registry berada di luar repository; spesifikasi teacher juga tercatat pada artefak evaluasi terkunci.
