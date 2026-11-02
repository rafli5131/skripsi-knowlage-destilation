# Teacher idle repetition 3

Run ID `20261102_eq_teacher_idle_u3`, 2 November 2026. The FP32 teacher ran on the 640×480 OP3 camera with BoT-SORT and SSH-X preview; automatic manager init pose was disabled. Input size 640, confidence 0.25, NMS IoU 0.45, PyTorch 4/2 threads. The 60-second analysis window followed 30 warm-up frames.

The window contained 581 frames and zero processing errors. Ball, goal, and robot were detected in every measured frame. Mean callback latency was 97.67 ms, P95 181.73 ms, effective camera FPS 9.69, mean process CPU 1337.67% of one logical CPU (83.60% of 16 logical CPUs), and mean RSS 372.06 MiB. Maximum sampled head/body displacement was 0.001534/0.001535 rad.

Evidence: [source summary](summary_metrics.json), [2160×1800 runtime plot](grafik_runtime_hd.png), [in-run detection image](frame_deteksi_saat_run.png), [image after the analysis window](frame_deteksi_sesudah_jendela.png), and four `telemetry_*.txt` files. Raw logs: `runs/op3_pytorch/20261102_eq_teacher_idle_u3.*`. Detection coverage is not labeled accuracy. Automatic CSV/joint checks passed; final temperature and preview-continuity review remains pending.
