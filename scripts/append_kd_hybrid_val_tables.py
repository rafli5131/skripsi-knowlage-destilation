"""Append completed KD hybrid seed-42 VAL results to the T04 tables."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LABEL_TO_RUN = {
    "hybrid_feature_seed42": "yolo11_tiny_hybrid_feature_seed42",
    "hybrid_full_seed42": "yolo11_tiny_hybrid_full_seed42",
}
EVALUATION_DIR = ROOT / "runs/val_ablation/hybrid_20261022"
T04 = ROOT / "analisis_performa/tabel/T04_ablasi_kd_val.csv"
T04_CLASS = ROOT / "analisis_performa/tabel/T04_ablasi_kd_val_per_kelas.csv"
LAB_MANIFEST = ROOT / "analisis_performa/lab_server/manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def make_rows(label: str, run_name: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    run_dir = ROOT / "runs/kd_hybrid" / run_name
    training_manifest_path = run_dir / "manifest.json"
    training_manifest = json.loads(training_manifest_path.read_text(encoding="utf-8"))
    if training_manifest.get("status") != "complete":
        raise RuntimeError(f"Training run is incomplete: {run_name}")
    training = training_manifest["training"]
    if int(training["seed"]) != 42:
        raise RuntimeError(f"Unexpected seed in {run_name}: {training['seed']}")

    result_path = EVALUATION_DIR / f"{label}_val.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("model") != label or result.get("images") != 1213:
        raise RuntimeError(f"Unexpected VAL result identity or image count: {result_path}")
    expected_split = json.loads((ROOT / "artifacts/advance_vision_dataset_fingerprint.json").read_text(encoding="utf-8"))["splits"]["val"]["split_fingerprint_sha256"]
    if result.get("val_split_fingerprint_sha256") != expected_split:
        raise RuntimeError(f"VAL fingerprint mismatch: {result_path}")

    with (run_dir / "results.csv").open(newline="", encoding="utf-8-sig") as stream:
        epoch_rows = list(csv.DictReader(stream))
    if not epoch_rows or "metrics/mAP50-95(B)" not in epoch_rows[0]:
        raise RuntimeError(f"Training metrics are missing: {run_dir / 'results.csv'}")
    best_row = max(epoch_rows, key=lambda row: float(row["metrics/mAP50-95(B)"]))
    best_epoch = int(float(best_row["epoch"]))

    distillation = training_manifest["distillation"]
    fixed = result["fixed_confidence_metrics"]
    summary = {
        "model": label,
        "seed": 42,
        "mode": distillation["mode"],
        "feature_weight": distillation["feature_weight"],
        "box_weight": distillation["box_weight"],
        "class_weight": distillation["class_weight"],
        "temperature": distillation.get("class_temperature", distillation.get("temperature", "not applicable")),
        "best_epoch": best_epoch,
        "val_mAP50": result["validator_metrics"]["metrics/mAP50(B)"],
        "val_mAP50_95": result["validator_metrics"]["metrics/mAP50-95(B)"],
        "val_precision_conf025": fixed["precision_macro"],
        "val_recall_conf025": fixed["recall_macro"],
        "val_F1_conf025": fixed["F1_macro"],
        "gawang_recall_conf025": result["per_class"]["gawang"]["recall_conf025"],
        "source_run": result_path.relative_to(ROOT).as_posix(),
    }
    class_rows = []
    for class_name, metrics in result["per_class"].items():
        class_rows.append({
            "model": label,
            "seed": 42,
            "mode": distillation["mode"],
            "class": class_name,
            "ground_truth_count": metrics["ground_truth_count"],
            "val_AP50": metrics["AP50"],
            "val_AP50_95": metrics["AP50_95"],
            "val_precision_conf025": metrics["precision_conf025"],
            "val_recall_conf025": metrics["recall_conf025"],
            "val_F1_conf025": metrics["F1_conf025"],
            "source_run": result_path.relative_to(ROOT).as_posix(),
        })
    return summary, class_rows


def append_csv(path: Path, rows: list[dict[str, Any]]) -> list[str]:
    columns, old_rows = read_rows(path)
    old_models = {row["model"] for row in old_rows}
    duplicates = old_models.intersection(row["model"] for row in rows)
    if duplicates:
        raise RuntimeError(f"Refusing to duplicate rows in {path}: {sorted(duplicates)}")
    for row in rows:
        if list(row) != columns:
            raise RuntimeError(f"Column mismatch in {path}: {list(row)} != {columns}")
    with path.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writerows(rows)
    return columns


def markdown_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}".replace(".", ",")
    return str(value)


def append_markdown(path: Path, columns: list[str], rows: list[dict[str, Any]], status: str | None = None) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if status is not None:
        for index, line in enumerate(lines):
            if line.startswith("Status:"):
                lines[index] = f"Status: {status}"
                break
    separator = next(index for index, line in enumerate(lines) if line.startswith("| ---"))
    insertion = separator + 1
    while insertion < len(lines) and lines[insertion].startswith("|"):
        insertion += 1
    markdown_rows = ["| " + " | ".join(markdown_value(row[col]) for col in columns) + " |" for row in rows]
    lines[insertion:insertion] = markdown_rows
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary_rows = []
    class_rows = []
    for label, run_name in LABEL_TO_RUN.items():
        summary, per_class = make_rows(label, run_name)
        summary_rows.append(summary)
        class_rows.extend(per_class)

    summary_columns = append_csv(T04, summary_rows)
    class_columns = append_csv(T04_CLASS, class_rows)
    append_markdown(
        T04.with_suffix(".md"), summary_columns, summary_rows,
        "Hasil VAL mencakup KD pure, pure_weighted, dan dua pilot KD Hybrid seed 42.",
    )
    append_markdown(T04_CLASS.with_suffix(".md"), class_columns, class_rows)

    manifest = json.loads(LAB_MANIFEST.read_text(encoding="utf-8"))
    manifest.setdefault("outputs_sha256", {})
    for path in (T04, T04.with_suffix(".md"), T04_CLASS, T04_CLASS.with_suffix(".md")):
        manifest["outputs_sha256"][path.relative_to(ROOT).as_posix()] = sha256(path)
    manifest["hybrid_pilots_added_on"] = "2026-10-22"
    LAB_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Appended {len(summary_rows)} hybrid runs and {len(class_rows)} class rows to T04.")


if __name__ == "__main__":
    main()
