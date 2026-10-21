"""Make a static comparison figure from an exploratory OP3 metrics.json."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = json.loads(args.metrics.read_text())
    names = list(report["models"])
    colors = ["#1d7a8c", "#d97732"]
    classes = ("ball", "gawang", "robot")
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.3), constrained_layout=True)

    x = np.arange(4)
    keys = ("mAP50-95", "mAP50", "precision", "recall")
    for i, name in enumerate(names):
        vals = [report["models"][name]["overall"][key] for key in keys]
        axes[0].bar(x + (i - 0.5) * 0.34, vals, width=0.34, label=name, color=colors[i])
    axes[0].set_xticks(x, ("mAP50–95", "mAP50", "Precision", "Recall"), rotation=25)
    axes[0].set_title("Keseluruhan · macro P/R")

    x = np.arange(3)
    for ax, key, title in zip(axes[1:], ("mAP50-95", "recall"),
                              ("mAP50–95 per kelas", "Recall per kelas · conf > 0,25")):
        for i, name in enumerate(names):
            vals = [report["models"][name]["per_class"][class_name][key]
                    for class_name in classes]
            ax.bar(x + (i - 0.5) * 0.34, vals, width=0.34, color=colors[i])
        ax.set_xticks(x, classes)
        ax.set_title(title)
    for ax in axes:
        ax.set_ylim(0, 1.05)
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
    axes[0].legend(loc="lower left")
    fig.suptitle("Kamera OP3 · 120 frame ditinjau · satu sesi servo idle · eksploratif", fontsize=13)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
