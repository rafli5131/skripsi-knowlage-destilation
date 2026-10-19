#!/usr/bin/env python3
"""Build a performance report and charts from an OP3 ROS inference session."""

from __future__ import annotations

import argparse
import csv
import os
import json
import statistics
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs/op3_pytorch"
OUTPUT = ROOT / "dokumentasi"


def percentile(values: list[float], value: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), value))


def read_run(run_id: str) -> tuple[dict, list[dict[str, str]]]:
    metadata_path = RUNS / f"{run_id}.json"
    csv_path = RUNS / f"{run_id}.csv"
    if not metadata_path.is_file() or not csv_path.is_file():
        raise FileNotFoundError(f"Run metadata/CSV not found for {run_id!r} under {RUNS}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    with csv_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"Run {run_id!r} has no frame records")
    return metadata, rows


def values(rows: list[dict[str, str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows if row.get(key, "") not in {"", None}]


def chart_latency(rows: list[dict[str, str]], path: Path) -> None:
    stages = [
        ("Preprocess", "preprocess_ms"),
        ("Inference", "inference_ms"),
        ("Postprocess", "postprocess_ms"),
        ("End-to-end", "end_to_end_ms"),
    ]
    medians = [statistics.median(values(rows, key)) for _, key in stages]
    p95s = [percentile(values(rows, key), 95) for _, key in stages]
    x = np.arange(len(stages))
    width = 0.36
    fig, ax = plt.subplots(figsize=(10, 5.7), constrained_layout=True)
    first = ax.bar(x - width / 2, medians, width, label="Median", color="#2878B5")
    second = ax.bar(x + width / 2, p95s, width, label="P95", color="#F28E2B")
    ax.bar_label(first, fmt="%.1f", padding=3, fontsize=9)
    ax.bar_label(second, fmt="%.1f", padding=3, fontsize=9)
    ax.set_xticks(x, [label for label, _ in stages])
    ax.set_ylabel("Latensi (ms)")
    ax.set_title("Latensi inferensi kamera per tahap")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(path, dpi=170)
    plt.close(fig)


def chart_latency_timeline(rows: list[dict[str, str]], path: Path) -> None:
    times = [datetime.fromisoformat(row["receive_time_utc"]) for row in rows]
    elapsed = np.asarray([(time - times[0]).total_seconds() for time in times])
    latency = np.asarray(values(rows, "end_to_end_ms"))
    p95 = float(np.percentile(latency, 95))
    fig, ax = plt.subplots(figsize=(11, 5.3), constrained_layout=True)
    ax.plot(elapsed, latency, color="#2878B5", linewidth=0.8, alpha=0.75, label="Per frame")
    ax.axhline(np.median(latency), color="#2E8B57", linestyle="--", label=f"Median {np.median(latency):.1f} ms")
    ax.axhline(p95, color="#F28E2B", linestyle="--", label=f"P95 {p95:.1f} ms")
    ax.set_yscale("log")
    ax.set_xlabel("Waktu sejak frame pertama (detik)")
    ax.set_ylabel("End-to-end (ms, skala log)")
    ax.set_title("End-to-end per frame sepanjang sesi")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25, which="both")
    fig.savefig(path, dpi=170)
    plt.close(fig)


def chart_resources(rows: list[dict[str, str]], path: Path) -> None:
    times = [datetime.fromisoformat(row["receive_time_utc"]) for row in rows]
    elapsed = np.asarray([(time - times[0]).total_seconds() for time in times])
    cpu = np.asarray(values(rows, "process_cpu_percent"))
    rss = np.asarray(values(rows, "process_rss_bytes"), dtype=np.float64) / (1024**2)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, constrained_layout=True)
    axes[0].plot(elapsed, cpu, color="#7B61A8", linewidth=0.8)
    axes[0].axhline(np.median(cpu), color="#333333", linestyle="--", label=f"Median {np.median(cpu):.0f}%")
    axes[0].axhline(np.percentile(cpu, 95), color="#F28E2B", linestyle="--", label=f"P95 {np.percentile(cpu, 95):.0f}%")
    axes[0].set_ylabel("CPU proses (%)")
    axes[0].set_title("CPU proses (100% setara satu logical CPU; dapat melebihi 100%)")
    axes[0].legend(frameon=False)
    axes[0].grid(alpha=0.25)
    axes[1].plot(elapsed, rss, color="#2A9D8F", linewidth=0.8)
    axes[1].axhline(np.median(rss), color="#333333", linestyle="--", label=f"Median {np.median(rss):.0f} MiB")
    axes[1].axhline(np.percentile(rss, 95), color="#F28E2B", linestyle="--", label=f"P95 {np.percentile(rss, 95):.0f} MiB")
    axes[1].set_xlabel("Waktu sejak frame pertama (detik)")
    axes[1].set_ylabel("RSS proses (MiB)")
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=0.25)
    fig.savefig(path, dpi=170)
    plt.close(fig)


def chart_frame_gaps(rows: list[dict[str, str]], path: Path) -> list[float]:
    stamps = [int(row["capture_stamp_ns"]) for row in rows if int(row.get("capture_stamp_ns") or 0) > 0]
    gaps = np.diff(np.asarray(stamps, dtype=np.float64)) / 1e9
    fig, ax = plt.subplots(figsize=(11, 5.2), constrained_layout=True)
    ax.plot(np.arange(1, len(gaps) + 1), gaps, color="#2878B5", linewidth=0.8)
    ax.axhline(1 / 30, color="#2E8B57", linestyle="--", label="Periode nominal kamera 30 FPS (33 ms)")
    ax.axhline(1.0, color="#F28E2B", linestyle="--", label="Jeda 1 detik")
    ax.set_yscale("log")
    ax.set_xlabel("Indeks pasangan frame berurutan")
    ax.set_ylabel("Selang timestamp capture (detik, skala log)")
    ax.set_title("Selang antar-frame dari timestamp kamera")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25, which="both")
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return gaps.tolist()


def build_report(
    metadata: dict, rows: list[dict[str, str]], gaps: list[float], run_id: str, output: Path
) -> str:
    end_to_end = values(rows, "end_to_end_ms")
    preprocess = values(rows, "preprocess_ms")
    inference = values(rows, "inference_ms")
    postprocess = values(rows, "postprocess_ms")
    cpu = values(rows, "process_cpu_percent")
    rss_mib = [value / (1024**2) for value in values(rows, "process_rss_bytes")]
    detection_total = sum(int(row.get("detection_count") or 0) for row in rows)
    frame_errors = sum(bool(row.get("error")) for row in rows)
    duration = (
        datetime.fromisoformat(metadata["stopped_at_utc"])
        - datetime.fromisoformat(metadata["started_at_utc"])
    ).total_seconds()
    fps = len(rows) / duration if duration > 0 else 0.0
    class_names = ", ".join(f"{index}: {name}" for index, name in metadata["class_names"].items())
    csv_link = os.path.relpath(RUNS / f"{run_id}.csv", output)
    metadata_link = os.path.relpath(RUNS / f"{run_id}.json", output)
    script_link = os.path.relpath(Path(__file__).resolve(), output)
    sample_image_link = os.path.relpath(OUTPUT / "figures/contoh_deteksi_kamera.png", output)
    sample_json_link = os.path.relpath(OUTPUT / "contoh_deteksi_kamera.json", output)

    def metric_line(name: str, samples: list[float], unit: str = "ms") -> str:
        return f"| {name} | {statistics.median(samples):.2f} | {percentile(samples, 95):.2f} | {statistics.fmean(samples):.2f} | {unit} |"

    gap_over_1 = sum(value > 1.0 for value in gaps)
    gap_over_5 = sum(value > 5.0 for value in gaps)
    return f"""# Hasil inferensi kamera OP3

Dokumentasi ini merangkum satu sesi inferensi kamera yang benar-benar dijalankan. Grafik menunjukkan performa dan aliran frame. Satu frame beranotasi disertakan sebagai contoh visual; video dan frame mentah tidak disimpan.

## Ringkasan sesi

| Item | Nilai |
| --- | --- |
| Run ID | `{run_id}` |
| Kondisi tercatat | `{metadata['condition']}` (label operator; tidak diukur otomatis) |
| Sumber label kondisi | Input operator; bukan telemetry gerak |
| Waktu mulai (UTC) | `{metadata['started_at_utc']}` |
| Waktu berhenti (UTC) | `{metadata['stopped_at_utc']}` |
| Durasi | {duration:.1f} detik |
| Kamera/sumber | Logitech HD Pro Webcam C920, `/dev/video0`, ROS topic `{metadata['input_topic']}` |
| Mode capture | 640×480, YUYV dikonversi `yuyv2rgb`, 30 FPS diminta |
| Frame diproses | {len(rows)} |
| FPS rata-rata sesi | {fps:.2f} |
| Error pemrosesan frame | {frame_errors} |
| Checkpoint | `{Path(metadata['checkpoint']).name}` (SHA-256 `{metadata['checkpoint_sha256']}`) |
| Runtime | Python 3.12.3, PyTorch {metadata['torch']}, Ultralytics {metadata['ultralytics']}, CPU FP32 |
| Input model | {metadata['imgsz']}×{metadata['imgsz']}, batch 1 |
| Threshold runtime | confidence {metadata['confidence_threshold']}, IoU NMS {metadata['iou_threshold']} |
| Preview | Mati; tidak menyimpan gambar/video |
| Topic output | `{metadata['output_topic']}` (`vision_msgs/Detection2DArray`) |
| Mapping kelas | {class_names} |

Log frame menunjukkan total **{detection_total} instance deteksi** yang dikeluarkan selama {len(rows)} frame. CSV hanya merekam jumlah deteksi per frame. Gambar beranotasi di bawah adalah contoh kamera terpisah dari sesi sebelumnya; timestamp, kelas, confidence, dan koordinatnya tercatat di JSON pendamping. Contoh tunggal ini dan jumlah deteksi bukan ukuran akurasi, precision, atau recall karena tidak ada frame berlabel dan ground truth.

![Contoh hasil deteksi pada satu frame kamera]({sample_image_link})

Detail bbox dan confidence untuk contoh frame: [`contoh_deteksi_kamera.json`]({sample_json_link}).

## Performa

Latensi dihitung per frame dari CSV. P95 memakai persentil linear NumPy. End-to-end mencakup callback deteksi dan publish ROS; preview mati.

| Tahap | Median (ms) | P95 (ms) | Rata-rata (ms) | Unit |
| --- | ---: | ---: | ---: | --- |
{metric_line('Preprocess', preprocess)}
{metric_line('Inference', inference)}
{metric_line('Postprocess/NMS', postprocess)}
{metric_line('End-to-end', end_to_end)}

![Median dan p95 latensi per tahap](figures/latensi_tahap.png)

![Latensi end-to-end sepanjang sesi](figures/latensi_per_frame.png)

CPU proses: median {statistics.median(cpu):.1f}% dan p95 {percentile(cpu, 95):.1f}%. psutil menghitung 100% sebagai satu logical CPU, sehingga nilai dapat melampaui 100% ketika beberapa thread bekerja bersamaan. RSS proses: median {statistics.median(rss_mib):.1f} MiB dan p95 {percentile(rss_mib, 95):.1f} MiB.

![Penggunaan CPU dan RAM proses](figures/cpu_ram_proses.png)

## Aliran frame dan batas hasil

Di antara timestamp capture berurutan, terdapat {gap_over_1} jeda lebih dari 1 detik dan {gap_over_5} jeda lebih dari 5 detik; jeda maksimum {max(gaps):.2f} detik. Pengamatan ini sejalan dengan peringatan kamera terputus sementara pada log node. FPS sesi karenanya menggambarkan stream yang benar-benar diterima selama sesi ini, bukan kemampuan maksimum model atau kamera dalam kondisi lain.

![Selang timestamp capture antar-frame](figures/jeda_frame.png)

Node ini mendeteksi objek (`ball`, `gawang`, `robot`), bukan aksi/gerakan; ia tidak menentukan apakah robot sedang berjalan. Kondisi `{metadata['condition']}` pada run ini adalah label operator, bukan hasil telemetry otomatis. Label `servo_idle` pada run pertama tidak cocok dengan kondisi yang kemudian dilaporkan, sehingga kondisi fisik run pertama tidak dapat dipastikan. Run ini tidak mengirim perintah servo/gait. Sesi walking terkontrol belum dilakukan.

Contoh PNG di atas dibuat untuk dokumentasi atas permintaan. Grafik performa dibuat dari CSV sesi benchmark yang preview-nya mati. CSV benchmark tidak menyimpan bounding box per kelas atau frame; detail bbox di JSON hanya berlaku untuk contoh tunggal. Evaluasi akurasi memerlukan frame berlabel dan ground truth.

## Artefak sumber

- Data mentah per frame: [`{run_id}.csv`]({csv_link})
- Metadata konfigurasi dan status: [`{run_id}.json`]({metadata_link})
- Script pembuat laporan dan grafik: [`build_op3_session_documentation.py`]({script_link})
""".replace("{run_id}", run_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Session run ID; defaults to latest metadata file")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    run_id = args.run_id
    if not run_id:
        candidates = sorted(RUNS.glob("*.json"), key=lambda path: path.stat().st_mtime)
        if not candidates:
            raise SystemExit(f"No session metadata found in {RUNS}")
        run_id = candidates[-1].stem
    metadata, rows = read_run(run_id)
    if metadata.get("status") != "stopped":
        raise SystemExit(f"Run must be stopped before documentation is built: {run_id}")
    if metadata.get("condition") not in {"unknown", "servo_idle", "walking"}:
        raise SystemExit(f"Unsupported experiment condition in metadata: {metadata.get('condition')!r}")

    figures = args.output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    chart_latency(rows, figures / "latensi_tahap.png")
    chart_latency_timeline(rows, figures / "latensi_per_frame.png")
    chart_resources(rows, figures / "cpu_ram_proses.png")
    gaps = chart_frame_gaps(rows, figures / "jeda_frame.png")
    report = build_report(metadata, rows, gaps, run_id, args.output.resolve())
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "README.md").write_text(report, encoding="utf-8")
    print(f"Dokumentasi dibuat: {args.output / 'README.md'}")
    print(f"Grafik dibuat: {figures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
