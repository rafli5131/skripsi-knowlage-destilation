#!/usr/bin/env python3
"""Render a reproducible thesis figure from the hash-locked final analysis."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS = ROOT / "artifacts" / "thesis_analysis_final_corrected"
METHODS = ("Pure KD", "Supervised student", "Teacher")
COLORS = {
    "Pure KD": "#0072B2",
    "Supervised student": "#D55E00",
    "Teacher": "#555555",
}
MARKERS = {"Pure KD": "o", "Supervised student": "s", "Teacher": "^"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_summary(path: Path) -> dict[tuple[str, str], tuple[float, float | None]]:
    values: dict[tuple[str, str], tuple[float, float | None]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            sd = row.get("sample_sd", "")
            values[(row["method"], row["metric"])] = (
                float(row["mean"]),
                float(sd) if sd else None,
            )
    return values


def render(analysis_dir: Path) -> tuple[Path, Path, Path]:
    summary_path = analysis_dir / "summary_mean_sd.csv"
    if not summary_path.is_file():
        raise FileNotFoundError(f"Final summary table not found: {summary_path}")
    values = load_summary(summary_path)
    required_metrics = (
        "test_mAP50_95",
        "checkpoint_size_MiB",
        "latency_median_ms",
    )
    missing = [
        (method, metric)
        for method in METHODS
        for metric in required_metrics
        if (method, metric) not in values
    ]
    if missing:
        raise ValueError(f"Missing final analysis values: {missing}")

    figure_dir = analysis_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    png_path = figure_dir / "figure_4_1_model_tradeoff.png"
    pdf_path = figure_dir / "figure_4_1_model_tradeoff.pdf"

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.8), constrained_layout=True)
    panels = (
        (axes[0], "checkpoint_size_MiB", "Ukuran checkpoint (MiB)"),
        (axes[1], "latency_median_ms", "Latensi median (ms)"),
    )
    for axis, x_metric, x_label in panels:
        for method in METHODS:
            y, y_sd = values[(method, "test_mAP50_95")]
            x, x_sd = values[(method, x_metric)]
            axis.errorbar(
                x,
                y,
                xerr=x_sd,
                yerr=y_sd,
                fmt=MARKERS[method],
                color=COLORS[method],
                markersize=8,
                capsize=4,
                elinewidth=1.2,
                markeredgecolor="white",
                markeredgewidth=0.8,
                label=method,
                zorder=3,
            )
        axis.set_xlabel(x_label)
        axis.set_ylabel("TEST mAP50–95")
        axis.set_ylim(0.60, 0.82)
        axis.set_yticks((0.60, 0.65, 0.70, 0.75, 0.80))
        axis.grid(True, color="#D9DEE5", linewidth=0.8, alpha=0.8)
        axis.set_axisbelow(True)
        axis.spines[["top", "right"]].set_visible(False)

    axes[0].set_title("A. Akurasi terhadap ukuran", loc="left", weight="bold")
    axes[1].set_title("B. Akurasi terhadap latensi", loc="left", weight="bold")
    axes[0].set_xlim(1.4, 5.7)
    axes[1].set_xlim(20.0, 30.5)

    # Offsets affect labels only; points and error bars retain their measured values.
    label_offsets = {
        "Pure KD": (34, -28),
        "Supervised student": (32, 16),
        "Teacher": (-20, 15),
    }
    for axis, x_metric, _ in panels:
        for method in METHODS:
            y = values[(method, "test_mAP50_95")][0]
            x = values[(method, x_metric)][0]
            axis.annotate(
                method,
                (x, y),
                xytext=label_offsets[method],
                textcoords="offset points",
                fontsize=8.5,
                color=COLORS[method],
                ha="center",
            )
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.06))
    fig.suptitle(
        "Kualitas deteksi terhadap ukuran model dan latensi",
        fontsize=14,
        weight="bold",
        y=1.12,
    )
    fig.text(
        0.5,
        -0.02,
        "Titik student: mean ± SD sampel dari tiga seed; teacher: satu checkpoint. "
        "Rentang sumbu-y ditampilkan 0,60–0,82 untuk memperjelas perbedaan.",
        ha="center",
        fontsize=9,
        color="#404854",
    )
    fig.savefig(png_path, dpi=240, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    script_path = Path(__file__).resolve()
    manifest_path = figure_dir / "figure_manifest.json"
    manifest = {
        "status": "complete",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": str(script_path),
        "script_sha256": sha256(script_path),
        "source_summary": str(summary_path.resolve()),
        "source_summary_sha256": sha256(summary_path),
        "python_version": platform.python_version(),
        "matplotlib_version": matplotlib.__version__,
        "figure_specification": {
            "metrics": ["test_mAP50_95", "checkpoint_size_MiB", "latency_median_ms"],
            "student_uncertainty": "sample SD across three paired seeds",
            "teacher_uncertainty": "not estimated; one checkpoint",
            "test_metric": "locked TEST mAP50-95",
            "mAP50_95_axis_range": [0.60, 0.82],
        },
        "outputs": {
            path.name: {"path": str(path.resolve()), "sha256": sha256(path)}
            for path in (png_path, pdf_path)
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return png_path, pdf_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS)
    args = parser.parse_args()
    png_path, pdf_path, manifest_path = render(args.analysis_dir.resolve())
    print(f"PNG: {png_path}")
    print(f"PDF: {pdf_path}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
