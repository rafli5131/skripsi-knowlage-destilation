# Teacher idle repetition 2 (replacement)

The first repetition-2 run was replaced at Bhre's request after frequent missed goal detections. The replacement uses the same run ID and settings: CPU FP32 teacher, 640×480 camera, 0.25 confidence, 0.45 NMS IoU, BoT-SORT, SSH-X preview, 4/2 PyTorch threads, and a 60-second measurement window after 30 warm-up frames.

The window contains 614 frames, zero processing errors, and detections for ball, goal, and robot in every frame. Mean total callback latency was 92.15 ms, P95 181.84 ms, effective camera-timestamp FPS 10.24, mean process CPU 1349.11% of one logical CPU (84.32% of 16 logical CPUs), and mean process RSS 369.66 MiB. Sampled head position did not change; sampled body displacement was at most 0.001535 rad.

See the [source summary](summary_metrics.json), [2160×1800 pixel runtime plot](grafik_runtime_hd.png), [pre-run preview](../../00-persiapan/preview_sebelum_u2_ulang.png), and [post-run preview](preview_setelah_run.png). Neither preview image was captured inside the measurement window. JointState sampling logged a few ROS message-loss warnings before obtaining one middle sample. The automatic CSV/joint checks passed; final review of preview continuity and temperature remains pending. Detection coverage is not labeled accuracy.
