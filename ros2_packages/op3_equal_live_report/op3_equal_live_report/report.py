"""Buat tabel dan grafik HD dari log uji live setara yang sudah selesai."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

MODELS = ("teacher", "hybrid1337", "sup1337", "kd42")
CONDITIONS = ("idle", "walk")
METRICS = (
    ("latency_mean_ms", "Latensi rata-rata (ms)"),
    ("fps", "FPS efektif (frame/detik)"),
    ("cpu_percent", "CPU proses (% satu CPU logis)"),
    ("rss_mib", "RAM proses RSS (MiB)"),
)


def for_slot(summaries: list[dict], model: str, cond: str, rep: int) -> dict | None:
    return next((s for s in summaries if s.get("slot_key") == f"{model}_{cond}_u{rep}"), None)


def read_joint(path: Path) -> dict[str, float]:
    raw = path.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^header:\n.*?(?=^---|\Z)", raw)
    if match is None:
        raise ValueError(f"Tidak ada JointState di {path}")
    data = yaml.safe_load(match.group())
    return dict(zip(data["name"], data["position"]))


def summarize(csv_path: Path, run_dir: Path) -> tuple[dict, list[dict]]:
    rows = list(csv.DictReader(csv_path.open(newline="", encoding="utf-8")))
    if not rows:
        raise ValueError(f"CSV kosong: {csv_path}")
    warm = next((r for r in rows if r["is_warmup"].lower() == "false"), None)
    if warm is None:
        raise ValueError(f"Warm-up tidak selesai: {csv_path}")
    tw = datetime.fromisoformat(warm["receive_time_utc"])
    walking = rows[0]["condition"] == "walking"
    ack_path = run_dir / "gait_start_ack_utc.txt"
    gait_ack = datetime.fromisoformat(ack_path.read_text(encoding="utf-8").strip()) if walking and ack_path.is_file() else None
    start, stop = ((gait_ack + timedelta(seconds=2), gait_ack + timedelta(seconds=62))
                   if gait_ack else (tw + timedelta(seconds=5), tw + timedelta(seconds=65)))
    selected = [r for r in rows if start <= datetime.fromisoformat(r["receive_time_utc"]) <= stop]
    clean = [r for r in selected if not r["error"]]
    if len(clean) < 2:
        raise ValueError(f"Frame ukur kurang: {csv_path}")
    stamps = [int(r["capture_stamp_ns"]) for r in clean]
    stamp_ok = all(n > 0 for n in stamps) and all(b > a for a, b in zip(stamps, stamps[1:]))
    fps = (len(stamps) - 1) * 1e9 / (stamps[-1] - stamps[0]) if stamp_ok else None
    latency = np.array([float(r["end_to_end_ms"]) for r in clean])
    cpu = np.array([float(r["process_cpu_percent"]) for r in clean])
    rss = np.array([float(r["process_rss_bytes"]) / 1048576 for r in clean])
    span_ok = datetime.fromisoformat(rows[-1]["receive_time_utc"]) >= stop
    errors = len(selected) - len(clean)
    samples = {}
    for name in ("pre", "mid1", "mid2", "after", "after2"):
        p = run_dir / f"telemetry_{name}.txt"
        if p.is_file():
            samples[name] = read_joint(p)
    head_delta = None
    body_delta = None
    if "pre" in samples:
        base = samples["pre"]
        head_delta = max(abs(s[j] - base[j]) for s in samples.values() for j in ("head_pan", "head_tilt"))
        body_delta = max(abs(s[j] - base[j]) for s in samples.values() for j in base if j not in ("head_pan", "head_tilt"))
    guard_path = run_dir / "gait_guard.json"
    guard = json.loads(guard_path.read_text(encoding="utf-8")) if walking and guard_path.is_file() else None
    guard_samples = []
    guard_samples_path = run_dir / "head_guard_samples.csv"
    if walking and guard_samples_path.is_file():
        guard_samples = list(csv.DictReader(guard_samples_path.open(newline="", encoding="utf-8")))
    mid_guard = {}
    if gait_ack is not None and guard_samples:
        for name, seconds in (("mid1", 20), ("mid2", 40)):
            target = gait_ack + timedelta(seconds=seconds)
            sample = min(guard_samples, key=lambda row: abs((datetime.fromisoformat(row["receive_time_utc"]) - target).total_seconds()))
            if abs((datetime.fromisoformat(sample["receive_time_utc"]) - target).total_seconds()) <= 2:
                mid_guard[name] = sample
                if "pre" in samples:
                    base = samples["pre"]
                    guard_body_delta = max(abs(float(sample[j + "_rad"]) - base[j]) for j in ("l_hip_pitch", "l_knee", "r_hip_pitch", "r_knee"))
                    body_delta = max(body_delta or 0.0, guard_body_delta)
    if guard is not None and head_delta is not None:
        head_delta = max(head_delta, float(guard["max_head_delta_rad"]))
    reasons = []
    if not span_ok:
        reasons.append("jendela_60_detik_tidak_lengkap")
    if errors / max(1, len(selected)) > 0.01:
        reasons.append("error_frame_lebih_1_persen")
    if not stamp_ok:
        reasons.append("timestamp_kamera_tidak_valid")
    if head_delta is None or head_delta > 2 * 0.00153473:
        reasons.append("telemetry_kepala_belum_lengkap_atau_bergeser")
    if walking:
        if gait_ack is None or guard is None or guard.get("status") != "completed":
            reasons.append("ack_atau_guard_gait_tidak_lengkap")
        if body_delta is None or body_delta < 0.03:
            reasons.append("gerak_kaki_tidak_terkonfirmasi")
        if len(mid_guard) != 2:
            reasons.append("sampel_tengah_gait_tidak_lengkap")
        if not all(name in samples for name in ("after", "after2")):
            reasons.append("stabilitas_setelah_stop_belum_terukur")
        else:
            after = samples["after"]
            after2 = samples["after2"]
            leg_joints = [j for j in after if j.startswith(("l_hip", "l_knee", "l_ank", "r_hip", "r_knee", "r_ank"))]
            if not leg_joints or max(abs(after2[j] - after[j]) for j in leg_joints) > 0.00307:
                reasons.append("kaki_belum_stabil_setelah_stop")
    elif body_delta is None or body_delta > 0.00307:
        reasons.append("telemetry_badan_belum_lengkap_atau_bergeser")
    if walking and not all(name in samples for name in ("pre", "after", "after2")):
        reasons.append("sampel_telemetry_kurang")
    elif not walking and len(samples) < 4:
        reasons.append("sampel_telemetry_kurang")
    summary = {
        "run_id": rows[0]["run_id"], "condition": rows[0]["condition"],
        "window_start_utc": start.isoformat(), "window_end_utc": stop.isoformat(),
        "frames_window": len(selected), "error_frames": errors,
        "latency_mean_ms": float(np.mean(latency)), "latency_median_ms": float(np.median(latency)),
        "latency_p95_ms": float(np.percentile(latency, 95)),
        "fps": fps, "cpu_percent": float(np.mean(cpu)),
        "rss_mib": float(np.mean(rss)), "head_max_delta_rad": head_delta,
        "body_max_delta_rad": body_delta,
        "gait_start_ack_utc": gait_ack.isoformat() if gait_ack else None,
        "gait_guard_status": guard.get("status") if guard else None,
        "mid_gait_samples_source": str(guard_samples_path) if len(mid_guard) == 2 else None,
        "mid_gait_sample_times_utc": {name: row["receive_time_utc"] for name, row in mid_guard.items()},
        "status": "lulus_cek_otomatis" if not reasons else "perlu_audit",
        "reasons": reasons, "source_csv": str(csv_path),
    }
    return summary, clean


def save_plot(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)


def plot_run(summary: dict, rows: list[dict], out: Path) -> None:
    t0 = datetime.fromisoformat(rows[0]["receive_time_utc"])
    x = [(datetime.fromisoformat(r["receive_time_utc"]) - t0).total_seconds() for r in rows]
    series = (
        ("end_to_end_ms", "Latensi total (ms)"),
        ("process_cpu_percent", "CPU proses (% satu CPU logis)"),
        ("process_rss_bytes", "RAM proses RSS (MiB)"),
    )
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    for ax, (key, ylabel) in zip(axes, series):
        vals = [float(r[key]) / (1048576 if key == "process_rss_bytes" else 1) for r in rows]
        ax.plot(x, vals, linewidth=1, color="#1464a0")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.25)
    axes[-1].set_xlabel("Waktu sejak awal jendela ukur (detik)")
    fig.suptitle(summary["run_id"] + " — jendela 60 detik")
    save_plot(fig, out / "grafik_runtime_hd.png")


def write_run_details(csv_path: Path, summary: dict, rows: list[dict], out: Path) -> None:
    """Write stage metrics and observed class outputs for the measured window."""
    with (out / "jendela_runtime.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    stages = (
        ("preprocess_ms", "Pra-pemrosesan", "Preprocessing"),
        ("inference_ms", "Inferensi", "Inference"),
        ("postprocess_ms", "Pasca-pemrosesan", "Postprocessing"),
        ("end_to_end_ms", "Callback total", "Total callback"),
    )
    stage_stats = []
    for key, id_name, en_name in stages:
        values = np.array([float(r[key]) for r in rows])
        stage_stats.append({"metric": key, "label_id": id_name, "label_en": en_name,
                            "mean_ms": float(np.mean(values)), "median_ms": float(np.median(values)),
                            "p95_ms": float(np.percentile(values, 95))})
    for filename in ("tabel_performa.csv", "performance_table.csv"):
        with (out / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=stage_stats[0].keys())
            writer.writeheader()
            writer.writerows(stage_stats)
    selected_indices = {int(r["frame_index"]) for r in rows}
    detections_path = csv_path.with_name(csv_path.stem + "_detections.csv")
    detections = []
    if detections_path.is_file():
        detections = [r for r in csv.DictReader(detections_path.open(newline="", encoding="utf-8"))
                      if int(r["frame_index"]) in selected_indices]
    if detections:
        with (out / "jendela_deteksi.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=detections[0].keys())
            writer.writeheader()
            writer.writerows(detections)
    class_stats = []
    for name in ("ball", "gawang", "robot"):
        count = sum(int(r["n_" + name]) > 0 for r in rows)
        det = [r for r in detections if r["class_name"] == name]
        class_stats.append({"class": name, "frames_detected": count, "frames_window": len(rows),
                            "coverage_percent": 100 * count / len(rows),
                            "median_confidence": float(np.median([float(r["confidence"]) for r in det])) if det else "",
                            "unique_track_ids": len({r["track_id"] for r in det if r["track_id"]})})
    for filename in ("tabel_deteksi.csv", "detection_table.csv"):
        with (out / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=class_stats[0].keys())
            writer.writeheader()
            writer.writerows(class_stats)
    if summary["condition"] == "walking" and (out / "gait_guard.json").is_file():
        guard = json.loads((out / "gait_guard.json").read_text(encoding="utf-8"))
        for filename, command, field in (
            ("gait_start_command.txt", "start", "start_command_utc"),
            ("gait_stop_command.txt", "stop", "stop_command_utc"),
        ):
            (out / filename).write_text(f"topic=/robotis/walking/command\ndata={command}\ncommand_utc={guard.get(field, '')}\nsource=gait_guard.json\n", encoding="utf-8")
        if (out / "head_guard_samples.csv").is_file():
            (out / "status_kepala.csv").write_text((out / "head_guard_samples.csv").read_text(encoding="utf-8"), encoding="utf-8")
    for lang, latency_name, class_name in (
        ("id", "grafik_latensi_id.png", "grafik_keluaran_kelas_id.png"),
        ("en", "latency_graph_en.png", "class_outputs_graph_en.png"),
    ):
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(stages))
        ax.bar(x - 0.18, [s["mean_ms"] for s in stage_stats], width=0.36, label="Rata-rata" if lang == "id" else "Mean", color="#1464a0")
        ax.bar(x + 0.18, [s["p95_ms"] for s in stage_stats], width=0.36, label="P95", color="#e69330")
        ax.set_xticks(x, [s["label_id" if lang == "id" else "label_en"] for s in stage_stats])
        ax.set_ylabel("Latensi (ms)" if lang == "id" else "Latency (ms)")
        ax.set_title(summary["run_id"])
        ax.legend()
        ax.grid(axis="y", alpha=0.25)
        save_plot(fig, out / latency_name)
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar([s["class"] for s in class_stats], [s["coverage_percent"] for s in class_stats], color="#1464a0")
        for bar, item in zip(bars, class_stats):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f'{item["coverage_percent"]:.1f}%', ha="center")
        ax.set_ylim(0, 112)
        ax.set_ylabel("Frame dengan keluaran (%)" if lang == "id" else "Frames with output (%)")
        ax.set_title(("Cakupan keluaran deteksi, bukan akurasi" if lang == "id" else "Detection output coverage, not accuracy") + "\n" + summary["run_id"])
        ax.grid(axis="y", alpha=0.25)
        save_plot(fig, out / class_name)
        fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
        t0 = datetime.fromisoformat(rows[0]["receive_time_utc"])
        x = [(datetime.fromisoformat(r["receive_time_utc"]) - t0).total_seconds() for r in rows]
        axes[0].plot(x, [float(r["process_cpu_percent"]) for r in rows], color="#1464a0", linewidth=1)
        axes[1].plot(x, [float(r["process_rss_bytes"]) / 1048576 for r in rows], color="#e69330", linewidth=1)
        axes[0].set_ylabel("CPU proses (% satu CPU)" if lang == "id" else "Process CPU (% of one CPU)")
        axes[1].set_ylabel("RAM RSS (MiB)")
        axes[1].set_xlabel("Waktu (detik)" if lang == "id" else "Time (seconds)")
        for ax in axes:
            ax.grid(alpha=0.25)
        fig.suptitle(summary["run_id"])
        save_plot(fig, out / ("grafik_cpu_ram_id.png" if lang == "id" else "cpu_ram_graph_en.png"))


def plot_matrix(summaries: list[dict], out: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    groups = [(model, cond) for cond in CONDITIONS for model in MODELS]
    labels = [f"{model}\n{cond}" for model, cond in groups]
    for ax, (metric, ylabel) in zip(axes.flat, METRICS):
        for i, (model, cond) in enumerate(groups):
            for rep in (1, 2, 3):
                match = for_slot(summaries, model, cond, rep)
                x = i + (rep - 2) * 0.22
                if match and match[metric] is not None:
                    color = "#1464a0" if match["status"] == "lulus_cek_otomatis" else "#cb6b17"
                    ax.scatter(x, match[metric], s=52, color=color, zorder=3)
                    ax.annotate(str(rep), (x, match[metric]), xytext=(0, 5), textcoords="offset points", ha="center", fontsize=8)
                else:
                    ax.scatter(x, 0, s=30, marker="x", color="#aaaaaa")
        ax.set_xticks(range(len(groups)), labels, rotation=25, ha="right")
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Matriks 24 run OP3: nomor titik = ulangan; × = belum diukur", fontsize=16)
    save_plot(fig, out / "grafik_24_run_ulangan_1_2_3_hd.png")


def plot_repetitions(summaries: list[dict], session_dir: Path) -> None:
    for model in MODELS:
        for cond in CONDITIONS:
            runs = [for_slot(summaries, model, cond, rep) for rep in (1, 2, 3)]
            if not all(runs):
                continue
            folder = session_dir / {"teacher":"01-teacher", "hybrid1337":"02-kd-hybrid", "sup1337":"03-supervised", "kd42":"04-kd-murni"}[model]
            for lang, filename in (("id", f"grafik_{model}_{cond}_ulangan_1_2_3_hd.png"),
                                   ("en", f"graph_{model}_{cond}_repetitions_1_2_3_hd.png")):
                fig, axes = plt.subplots(2, 2, figsize=(16, 10))
                for ax, (metric, ylabel) in zip(axes.flat, METRICS):
                    values = [r[metric] for r in runs]
                    ax.plot((1, 2, 3), values, marker="o", markersize=9, linewidth=2, color="#1464a0")
                    for index, value in enumerate(values, start=1):
                        ax.annotate(f"{value:.2f}", (index, value), xytext=(0, 8), textcoords="offset points", ha="center")
                    ax.set_xticks((1, 2, 3))
                    ax.set_xlabel("Ulangan" if lang == "id" else "Repetition")
                    ax.set_ylabel(ylabel if lang == "id" else {
                        "latency_mean_ms": "Mean latency (ms)", "fps": "Effective FPS (frames/s)",
                        "cpu_percent": "Process CPU (% of one CPU)", "rss_mib": "Process RSS (MiB)",
                    }[metric])
                    ax.grid(alpha=0.25)
                fig.suptitle(f"{model} — {cond}: " + ("tiga ulangan" if lang == "id" else "three repetitions"), fontsize=16)
                save_plot(fig, folder / filename)
            class_rows = []
            for rep in (1, 2, 3):
                table = folder / f"{cond}-u{rep}" / "tabel_deteksi.csv"
                if not table.is_file():
                    break
                class_rows.append({row["class"]: row for row in csv.DictReader(table.open(newline="", encoding="utf-8"))})
            if len(class_rows) != 3:
                continue
            for lang, filename in (("id", f"grafik_cakupan_confidence_{model}_{cond}_hd.png"),
                                   ("en", f"graph_output_coverage_confidence_{model}_{cond}_hd.png")):
                fig, axes = plt.subplots(1, 2, figsize=(15, 6))
                for name, color in (("ball", "#1464a0"), ("gawang", "#e69330"), ("robot", "#288a67")):
                    coverage = [float(group[name]["coverage_percent"]) for group in class_rows]
                    confidence = [float(group[name]["median_confidence"]) if group[name]["median_confidence"] else np.nan for group in class_rows]
                    axes[0].plot((1, 2, 3), coverage, marker="o", label=name, color=color)
                    axes[1].plot((1, 2, 3), confidence, marker="o", label=name, color=color)
                axes[0].set_ylabel("Frame dengan keluaran (%)" if lang == "id" else "Frames with output (%)")
                axes[0].set_ylim(0, 105)
                axes[1].set_ylabel("Median confidence model" if lang == "id" else "Median model confidence")
                axes[1].set_ylim(0, 1)
                for ax in axes:
                    ax.set_xticks((1, 2, 3))
                    ax.set_xlabel("Ulangan" if lang == "id" else "Repetition")
                    ax.grid(alpha=0.25)
                    ax.legend()
                fig.suptitle(("Cakupan keluaran dan confidence — bukan akurasi/precision" if lang == "id" else
                              "Output coverage and confidence — not accuracy/precision") + f"\n{model} — {cond}")
                save_plot(fig, folder / filename)


def write_session_tables(summaries: list[dict], session_dir: Path) -> None:
    with (session_dir / "jadwal_run.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("model", "condition", "ulangan", "status", "run_id", "window_start_utc", "window_end_utc"))
        writer.writeheader()
        for cond in CONDITIONS:
            for model in MODELS:
                for rep in (1, 2, 3):
                    match = for_slot(summaries, model, cond, rep)
                    writer.writerow({"model": model, "condition": cond, "ulangan": rep,
                                     "status": match["status"] if match else "belum_diukur",
                                     "run_id": match["run_id"] if match else "",
                                     "window_start_utc": match["window_start_utc"] if match else "",
                                     "window_end_utc": match["window_end_utc"] if match else ""})
    aggregates = []
    for cond in CONDITIONS:
        for model in MODELS:
            group = [for_slot(summaries, model, cond, rep) for rep in (1, 2, 3)]
            if any(s is None for s in group):
                continue
            row = {"model": model, "condition": cond, "runs": len(group), "frames_total": sum(s["frames_window"] for s in group),
                   "status": "semua_lulus_cek_otomatis" if all(s["status"] == "lulus_cek_otomatis" for s in group) else "perlu_audit"}
            for metric, _ in METRICS:
                values = [s[metric] for s in group]
                row[metric + "_mean"] = float(np.mean(values)) if all(v is not None for v in values) else ""
                row[metric + "_sd_sample"] = float(np.std(values, ddof=1)) if all(v is not None for v in values) else ""
            aggregates.append(row)
    if aggregates:
        with (session_dir / "05-ringkasan" / "tabel_agregat_saat_ini.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=aggregates[0].keys())
            writer.writeheader()
            writer.writerows(aggregates)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("runs/op3_pytorch"))
    parser.add_argument("--session-dir", type=Path, required=True)
    args = parser.parse_args()
    summaries = []
    active_path = args.session_dir / "active_run_sources.json"
    active_sources = json.loads(active_path.read_text(encoding="utf-8")) if active_path.is_file() else {}
    for model in MODELS:
        for cond in CONDITIONS:
            for rep in (1, 2, 3):
                mapped = active_sources.get(f"{model}_{cond}", {}).get(str(rep), "UNMAPPED")
                if mapped is None:
                    continue
                if mapped == "UNMAPPED":
                    matches = sorted(args.runs_dir.glob(f"*_eq_{model}_{cond}_u{rep}.csv"))
                    if not matches:
                        continue
                    csv_path = matches[-1]
                else:
                    csv_path = args.runs_dir / f"{mapped}.csv"
                    if not csv_path.is_file():
                        raise FileNotFoundError(f"Run aktif belum ada: {csv_path}")
                folder = args.session_dir / {"teacher":"01-teacher", "hybrid1337":"02-kd-hybrid", "sup1337":"03-supervised", "kd42":"04-kd-murni"}[model] / f"{cond}-u{rep}"
                folder.mkdir(parents=True, exist_ok=True)
                summary, rows = summarize(csv_path, folder)
                summary["slot_key"] = f"{model}_{cond}_u{rep}"
                summary["display_repetition"] = rep
                summary["source_run_id"] = summary["run_id"]
                (folder / "summary_metrics.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
                plot_run(summary, rows, folder)
                write_run_details(csv_path, summary, rows, folder)
                summaries.append(summary)
    out = args.session_dir / "05-ringkasan"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "tabel_24_run.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["model", "condition", "ulangan", "status", "run_id", "latency_mean_ms", "latency_p95_ms", "fps", "cpu_percent", "rss_mib", "frames_window", "error_frames", "head_max_delta_rad", "body_max_delta_rad", "reasons"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for cond in CONDITIONS:
            for model in MODELS:
                for rep in (1, 2, 3):
                    match = for_slot(summaries, model, cond, rep)
                    writer.writerow({
                        **({k: v for k, v in match.items() if k in fields} if match else {"status": "belum_diukur"}),
                        "model": model, "condition": cond, "ulangan": rep,
                    })
    plot_matrix(summaries, out)
    plot_repetitions(summaries, args.session_dir)
    write_session_tables(summaries, args.session_dir)
    print(f"Run terbaca: {len(summaries)}/24; keluaran: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
