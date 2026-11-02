# Trial 30: matched live OP3 evaluation

As of 2 November 2026, three teacher idle and three teacher walking repetitions have been recorded. The other 18 of 24 planned runs remain unmeasured. The first idle repetition-2 files were replaced at Bhre's request after frequent missed goal detections. This session measures runtime with SSH-X preview and BoT-SORT tracking; it does not measure labeled detection accuracy.

The teacher checkpoint hash matched the registry. The 640×480 camera and `op3_manager` were active, with automatic init pose disabled. The operator supported the robot and camera while torque was temporarily disabled for manager EEPROM initialization. Head telemetry then matched the initial pose.

See the [teacher results](01-teacher/README_EN.md), [24-slot table](05-ringkasan/tabel_24_run.csv), [2880×1800 pixel plot](05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png), and [deviation log](log_penyimpangan.md). Blue points passed automatic CSV and sampled-joint checks; × marks runs not yet measured. All three gait commands received stop acknowledgments, and the teacher monitoring preview remains active. Final protocol validity still requires review of preview continuity, temperature, and physical-condition notes.
