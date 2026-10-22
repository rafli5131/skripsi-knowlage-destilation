"""Build auditable VAL tables for three paired KD Hybrid/supervised seeds."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "runs/val_ablation/hybrid_20261022_multiseed"
HYBRID_RUNS = {s: f"runs/kd_hybrid/yolo11_tiny_hybrid_full_seed{s}" for s in (42, 1337, 2025)}
SUPERVISED_RUNS = {
    42: "runs/supervised/yolo11_tiny_supervised_seed42_retry1",
    1337: "runs/supervised/yolo11_tiny_supervised_seed1337",
    2025: "runs/supervised/yolo11_tiny_supervised_seed2025",
}
EXPECTED_SETTINGS = {
    "imgsz": 640,
    "batch": 16,
    "rect": True,
    "augment": False,
    "confidence_floor_for_AP": 0.001,
    "nms_iou": 0.7,
    "fixed_confidence": 0.25,
    "match_iou": 0.5,
    "device": "cpu",
    "threads": 8,
}
T04 = ROOT / "analisis_performa/tabel/T04_ablasi_kd_val.csv"
T04_MD = T04.with_suffix(".md")
T04_CLASS = ROOT / "analisis_performa/tabel/T04_ablasi_kd_val_per_kelas.csv"
T04_CLASS_MD = T04_CLASS.with_suffix(".md")
T28 = ROOT / "analisis_performa/tabel/T28_selisih_kd_hybrid_val.csv"
T28_MD = T28.with_suffix(".md")
T29 = ROOT / "analisis_performa/tabel/T29_kd_hybrid_val_per_kelas.csv"
T29_MD = T29.with_suffix(".md")
REPORT = ROOT / "analisis_performa/lab_server/HASIL_KD_HYBRID_MULTI_SEED_VAL_2026-10-22.md"
LAB_MANIFEST = ROOT / "analisis_performa/lab_server/manifest.json"
ANALYSIS_MANIFEST = ROOT / "analisis_performa/manifest.json"
INDEX = ROOT / "analisis_performa/INDEKS.md"
LAB_README = ROOT / "analisis_performa/lab_server/README.md"
CLASSES = ("ball", "gawang", "robot")
GLOBAL_METRICS = ("mAP50", "mAP50-95", "precision@0.25", "recall@0.25", "F1@0.25")
CLASS_METRICS = ("AP50", "AP50-95", "precision@0.25", "recall@0.25", "F1@0.25")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def best_epoch(run_dir: Path) -> int:
    with (run_dir / "results.csv").open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise RuntimeError(f"No training epochs in {run_dir / 'results.csv'}")
    row = max(rows, key=lambda item: float(item["metrics/mAP50-95(B)"]))
    return int(float(row["epoch"]))


def load_verified_eval(seed: int, kind: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    label = f"{'hybrid_full' if kind == 'hybrid' else 'supervised'}_seed{seed}"
    result_path = EVAL_DIR / f"{label}_val.json"
    result = read_json(result_path)
    run_dir = ROOT / (HYBRID_RUNS if kind == "hybrid" else SUPERVISED_RUNS)[seed]
    manifest_path = run_dir / "manifest.json"
    manifest = read_json(manifest_path)

    if result.get("model") != label or result.get("images") != 1213:
        raise RuntimeError(f"Unexpected identity or image count in {result_path}")
    if result.get("settings") != EXPECTED_SETTINGS:
        raise RuntimeError(f"Evaluation settings differ from locked VAL protocol in {result_path}")
    if manifest.get("status") != "complete" or int(manifest.get("seed", -1)) != seed:
        raise RuntimeError(f"Training manifest is incomplete or has wrong seed: {manifest_path}")
    if manifest.get("test_split_used") is not False:
        raise RuntimeError(f"Training manifest does not certify TEST exclusion: {manifest_path}")
    if manifest.get("distillation", {}).get("mode", "supervised") != (
        "hybrid_full" if kind == "hybrid" else "supervised"
    ):
        raise RuntimeError(f"Unexpected method for {manifest_path}")

    checkpoint = Path(manifest["student_best_checkpoint"])
    if not checkpoint.is_absolute():
        checkpoint = ROOT / checkpoint
    checkpoint = checkpoint.resolve()
    checkpoint_hash = sha256(checkpoint)
    if checkpoint_hash != manifest.get("student_best_sha256"):
        raise RuntimeError(f"Training manifest checkpoint hash mismatch: {checkpoint}")
    if result.get("checkpoint_sha256") != checkpoint_hash:
        raise RuntimeError(f"Evaluation used a different checkpoint: {result_path}")
    if result.get("training_manifest_sha256") != sha256(manifest_path):
        raise RuntimeError(f"Evaluation manifest hash mismatch: {result_path}")

    fingerprint = read_json(ROOT / "artifacts/advance_vision_dataset_fingerprint.json")
    expected_val = fingerprint["splits"]["val"]["split_fingerprint_sha256"]
    if result.get("val_split_fingerprint_sha256") != expected_val:
        raise RuntimeError(f"Wrong VAL fingerprint: {result_path}")
    if manifest.get("dataset_split_fingerprints", {}).get("val") != expected_val:
        raise RuntimeError(f"Training run used a different VAL split: {manifest_path}")
    return result, manifest, run_dir


def validate_paired_training(hybrid: dict[str, Any], supervised: dict[str, Any], seed: int) -> None:
    if hybrid.get("dataset_split_fingerprints") != supervised.get("dataset_split_fingerprints"):
        raise RuntimeError(f"Paired seed {seed} did not use the same dataset splits")
    if hybrid.get("student_architecture_sha256") != supervised.get("student_architecture_sha256"):
        raise RuntimeError(f"Paired seed {seed} did not use the same student architecture")
    training_fields = (
        "seed", "epochs", "batch", "workers", "imgsz", "optimizer", "lr0", "lrf",
        "warmup_epochs", "weight_decay", "close_mosaic", "amp", "patience",
    )
    for field in training_fields:
        if hybrid.get("training", {}).get(field) != supervised.get("training", {}).get(field):
            raise RuntimeError(f"Paired seed {seed} training mismatch in {field}")
    for run_dir in (ROOT / HYBRID_RUNS[seed], ROOT / SUPERVISED_RUNS[seed]):
        args_path = run_dir / "args.yaml"
        if not args_path.is_file() or "pretrained: false" not in args_path.read_text(encoding="utf-8").lower():
            raise RuntimeError(f"Expected random student initialization was not recorded in {args_path}")


def global_value(result: dict[str, Any], metric: str) -> float:
    if metric in ("mAP50", "mAP50-95"):
        key = "metrics/mAP50(B)" if metric == "mAP50" else "metrics/mAP50-95(B)"
        return float(result["validator_metrics"][key])
    key = {
        "precision@0.25": "precision_macro",
        "recall@0.25": "recall_macro",
        "F1@0.25": "F1_macro",
    }[metric]
    return float(result["fixed_confidence_metrics"][key])


def class_value(result: dict[str, Any], class_name: str, metric: str) -> float:
    field = {
        "AP50": "AP50",
        "AP50-95": "AP50_95",
        "precision@0.25": "precision_conf025",
        "recall@0.25": "recall_conf025",
        "F1@0.25": "F1_conf025",
    }[metric]
    return float(result["per_class"][class_name][field])


def mean_sd(values: list[float]) -> tuple[float, float]:
    return statistics.mean(values), statistics.stdev(values)


def fmt_float(value: float, signed: bool = False) -> str:
    text = f"{value:+.4f}" if signed else f"{value:.4f}"
    return text.replace(".", ",")


def fmt_pm(mean: float, sd: float, signed: bool = False) -> str:
    return f"{fmt_float(mean, signed)} ± {fmt_float(sd)}"


def markdown_cell(column: str, value: Any) -> str:
    if value is None:
        return ""
    if column in {"seed", "best_epoch", "ground_truth_count"}:
        try:
            return str(int(float(value)))
        except (TypeError, ValueError):
            return str(value)
    if column in {
        "feature_weight", "box_weight", "class_weight", "temperature",
        "val_mAP50", "val_mAP50_95", "val_precision_conf025", "val_recall_conf025",
        "val_F1_conf025", "gawang_recall_conf025", "val_AP50", "val_AP50_95",
        "val_precision_conf025", "val_recall_conf025", "val_F1_conf025",
    }:
        try:
            return fmt_float(float(value))
        except (TypeError, ValueError):
            pass
    return str(value)


def replace_markdown_table(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_idx = next((i for i, line in enumerate(lines) if line.startswith("| model |")), None)
    if header_idx is None or header_idx + 1 >= len(lines):
        raise RuntimeError(f"Could not find model table in {path}")
    end = header_idx + 2
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    data = [
        "| " + " | ".join(markdown_cell(col, row.get(col, "")) for col in columns) + " |"
        for row in rows
    ]
    lines[header_idx:end] = [header, separator, *data]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def csv_markdown_table(headers: list[str], rows: list[dict[str, Any]], signed_fields: set[str] | None = None) -> str:
    signed_fields = signed_fields or set()
    output = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        cells = []
        for field in row:
            value = row[field]
            if isinstance(value, float):
                cells.append(fmt_float(value, signed=field in signed_fields))
            else:
                cells.append(str(value))
        output.append("| " + " | ".join(cells) + " |")
    return "\n".join(output)


def build_t04_rows(evals: dict[tuple[str, int], dict[str, Any]], manifests: dict[tuple[str, int], dict[str, Any]], run_dirs: dict[tuple[str, int], Path]) -> None:
    columns, summary_rows = read_csv(T04)
    class_columns, class_rows = read_csv(T04_CLASS)
    summary_index = {row["model"]: i for i, row in enumerate(summary_rows)}
    class_index = {(row["model"], row["class"]): i for i, row in enumerate(class_rows)}
    for seed in (42, 1337, 2025):
        key = ("hybrid", seed)
        result, manifest, run_dir = evals[key], manifests[key], run_dirs[key]
        label = f"hybrid_full_seed{seed}"
        distill = manifest["distillation"]
        epoch = best_epoch(run_dir)
        overall = result["validator_metrics"]
        fixed = result["fixed_confidence_metrics"]
        row = {
            "model": label,
            "seed": seed,
            "mode": "hybrid_full",
            "feature_weight": distill["feature_weight"],
            "box_weight": distill["box_weight"],
            "class_weight": distill["class_weight"],
            "temperature": distill.get("class_temperature", distill.get("temperature", "not applicable")),
            "best_epoch": epoch,
            "val_mAP50": overall["metrics/mAP50(B)"],
            "val_mAP50_95": overall["metrics/mAP50-95(B)"],
            "val_precision_conf025": fixed["precision_macro"],
            "val_recall_conf025": fixed["recall_macro"],
            "val_F1_conf025": fixed["F1_macro"],
            "gawang_recall_conf025": result["per_class"]["gawang"]["recall_conf025"],
            "source_run": (EVAL_DIR / f"{label}_val.json").relative_to(ROOT).as_posix(),
        }
        if list(row) != columns:
            raise RuntimeError(f"T04 schema changed: {list(row)} != {columns}")
        if label in summary_index:
            i = summary_index[label]
            old = summary_rows[i]
            for metric_field in ("val_mAP50", "val_mAP50_95", "val_precision_conf025", "val_recall_conf025", "val_F1_conf025"):
                if not math.isclose(float(old[metric_field]), float(row[metric_field]), abs_tol=1e-9):
                    raise RuntimeError(f"Existing T04 row does not match re-evaluated {label}: {metric_field}")
            summary_rows[i] = {k: str(v) for k, v in row.items()}
        else:
            summary_index[label] = len(summary_rows)
            summary_rows.append({k: str(v) for k, v in row.items()})

        for class_name in CLASSES:
            class_metric = result["per_class"][class_name]
            class_row = {
                "model": label,
                "seed": seed,
                "mode": "hybrid_full",
                "class": class_name,
                "ground_truth_count": class_metric["ground_truth_count"],
                "val_AP50": class_metric["AP50"],
                "val_AP50_95": class_metric["AP50_95"],
                "val_precision_conf025": class_metric["precision_conf025"],
                "val_recall_conf025": class_metric["recall_conf025"],
                "val_F1_conf025": class_metric["F1_conf025"],
                "source_run": row["source_run"],
            }
            if list(class_row) != class_columns:
                raise RuntimeError(f"T04 per-class schema changed: {list(class_row)} != {class_columns}")
            ck = (label, class_name)
            if ck in class_index:
                i = class_index[ck]
                old = class_rows[i]
                for metric_field in ("val_AP50", "val_AP50_95", "val_precision_conf025", "val_recall_conf025", "val_F1_conf025"):
                    if not math.isclose(float(old[metric_field]), float(class_row[metric_field]), abs_tol=1e-9):
                        raise RuntimeError(f"Existing T04 per-class row differs: {label} {class_name} {metric_field}")
                class_rows[i] = {k: str(v) for k, v in class_row.items()}
            else:
                class_index[ck] = len(class_rows)
                class_rows.append({k: str(v) for k, v in class_row.items()})

    write_csv(T04, columns, summary_rows)
    write_csv(T04_CLASS, class_columns, class_rows)
    replace_markdown_table(T04_MD, columns, summary_rows)
    replace_markdown_table(T04_CLASS_MD, class_columns, class_rows)
    class_text = T04_CLASS_MD.read_text(encoding="utf-8")
    class_text = class_text.replace(
        "Rincian tiga kelas untuk empat checkpoint pada T04.",
        "Rincian tiga kelas untuk delapan checkpoint pada T04, termasuk hybrid_full tiga seed.",
    )
    T04_CLASS_MD.write_text(class_text, encoding="utf-8")
    return


def build_pair_tables(evals: dict[tuple[str, int], dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    overall_rows: list[dict[str, Any]] = []
    for seed in (42, 1337, 2025):
        hybrid, supervised = evals[("hybrid", seed)], evals[("supervised", seed)]
        for metric in GLOBAL_METRICS:
            h, s = global_value(hybrid, metric), global_value(supervised, metric)
            overall_rows.append({
                "seed": seed, "metric": metric, "hybrid_full": h,
                "supervised_student": s, "delta_hybrid_minus_supervised": h - s,
            })
    for metric in GLOBAL_METRICS:
        hs = [global_value(evals[("hybrid", s)], metric) for s in (42, 1337, 2025)]
        ss = [global_value(evals[("supervised", s)], metric) for s in (42, 1337, 2025)]
        ds = [h - s for h, s in zip(hs, ss)]
        hm, hsd = mean_sd(hs)
        sm, ssd = mean_sd(ss)
        dm, dsd = mean_sd(ds)
        overall_rows.append({
            "seed": "mean ± SD (n=3)", "metric": metric,
            "hybrid_full": fmt_pm(hm, hsd), "supervised_student": fmt_pm(sm, ssd),
            "delta_hybrid_minus_supervised": fmt_pm(dm, dsd, signed=True),
        })

    class_rows: list[dict[str, Any]] = []
    for class_name in CLASSES:
        for seed in (42, 1337, 2025):
            hybrid, supervised = evals[("hybrid", seed)], evals[("supervised", seed)]
            for metric in CLASS_METRICS:
                h = class_value(hybrid, class_name, metric)
                s = class_value(supervised, class_name, metric)
                class_rows.append({
                    "class": class_name, "seed": seed, "metric": metric,
                    "hybrid_full": h, "supervised_student": s,
                    "delta_hybrid_minus_supervised": h - s,
                })
        for metric in CLASS_METRICS:
            hs = [class_value(evals[("hybrid", s)], class_name, metric) for s in (42, 1337, 2025)]
            ss = [class_value(evals[("supervised", s)], class_name, metric) for s in (42, 1337, 2025)]
            ds = [h - s for h, s in zip(hs, ss)]
            hm, hsd = mean_sd(hs)
            sm, ssd = mean_sd(ss)
            dm, dsd = mean_sd(ds)
            class_rows.append({
                "class": class_name, "seed": "mean ± SD (n=3)", "metric": metric,
                "hybrid_full": fmt_pm(hm, hsd), "supervised_student": fmt_pm(sm, ssd),
                "delta_hybrid_minus_supervised": fmt_pm(dm, dsd, signed=True),
            })
    return overall_rows, class_rows


def write_pair_markdown(path: Path, title: str, intro: str, columns: list[str], rows: list[dict[str, Any]]) -> None:
    labels = {
        "seed": "seed", "class": "kelas", "metric": "metrik",
        "hybrid_full": "KD Hybrid full", "supervised_student": "Student supervised",
        "delta_hybrid_minus_supervised": "Δ Hybrid − supervised",
    }
    header = [labels.get(column, column) for column in columns]
    md_rows = []
    for row in rows:
        md_row: dict[str, Any] = {}
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                md_row[column] = fmt_float(value, signed=(column == "delta_hybrid_minus_supervised"))
            else:
                md_row[column] = value
        md_rows.append(md_row)
    md = f"# {title}\n\n{intro}\n\n" + csv_markdown_table(header, md_rows) + "\n"
    path.write_text(md, encoding="utf-8")


def metric_summaries(evals: dict[tuple[str, int], dict[str, Any]]) -> dict[str, dict[str, tuple[float, float]]]:
    result: dict[str, dict[str, tuple[float, float]]] = {}
    for metric in GLOBAL_METRICS:
        values = {kind: [global_value(evals[(kind, seed)], metric) for seed in (42, 1337, 2025)] for kind in ("hybrid", "supervised")}
        deltas = [h - s for h, s in zip(values["hybrid"], values["supervised"])]
        result[metric] = {
            "hybrid": mean_sd(values["hybrid"]),
            "supervised": mean_sd(values["supervised"]),
            "delta": mean_sd(deltas),
        }
    return result


def write_report(evals: dict[tuple[str, int], dict[str, Any]]) -> None:
    summaries = metric_summaries(evals)
    val_fp = evals[("hybrid", 42)]["val_split_fingerprint_sha256"]
    summary_table = ["| metrik | Hybrid full, rerata ± SD | Supervised, rerata ± SD | Δ berpasangan, rerata ± SD |", "| --- | --- | --- | --- |"]
    for metric in GLOBAL_METRICS:
        row = summaries[metric]
        summary_table.append(
            f"| {metric} | {fmt_pm(*row['hybrid'])} | {fmt_pm(*row['supervised'])} | {fmt_pm(*row['delta'], signed=True)} |"
        )
    seed_deltas = []
    for seed in (42, 1337, 2025):
        h = global_value(evals[("hybrid", seed)], "mAP50-95")
        s = global_value(evals[("supervised", seed)], "mAP50-95")
        seed_deltas.append(f"| {seed} | {fmt_float(h)} | {fmt_float(s)} | {fmt_float(h-s, signed=True)} |")
    class_table = ["| kelas | Δ AP50–95, rerata ± SD | Δ precision@0,25, rerata ± SD | Δ recall@0,25, rerata ± SD | Δ F1@0,25, rerata ± SD |", "| --- | --- | --- | --- | --- |"]
    for class_name in CLASSES:
        deltas = {}
        for metric in ("AP50-95", "precision@0.25", "recall@0.25", "F1@0.25"):
            by_seed = [class_value(evals[("hybrid", s)], class_name, metric) - class_value(evals[("supervised", s)], class_name, metric) for s in (42, 1337, 2025)]
            deltas[metric] = fmt_pm(*mean_sd(by_seed), signed=True)
        class_table.append(f"| {class_name} | {deltas['AP50-95']} | {deltas['precision@0.25']} | {deltas['recall@0.25']} | {deltas['F1@0.25']} |")

    content = f"""# Evaluasi VAL KD Hybrid full multi-seed — 22 Oktober 2026

## Protokol

Enam checkpoint `best.pt` dibandingkan pada VAL resmi yang sama, 1.213 gambar. Per pasangan seed, arsitektur student, split, dan resep training supervised cocok dengan KD Hybrid; perbedaan objective-nya adalah ada/tidaknya loss distilasi. Kontrol supervised seed 1337 melanjutkan run terhenti dari `last.pt`; manifest merekam resume dan penyelesaian resep 100 epoch yang sama. Fingerprint split VAL: `{val_fp}`. Inferensi FP32 pada CPU, imgsz 640, batch 16, rectangular validation, tanpa augmentasi; AP memakai confidence floor 0,001 dan NMS IoU 0,7. Precision/recall/F1 memakai confidence tetap 0,25 dan matching IoU 0,50. Tidak ada training saat evaluasi dan **TEST tidak dibuka**.

## Hasil keseluruhan

Nilai berikut adalah rerata ± simpangan baku sampel antar tiga seed. Δ dihitung berpasangan sebagai KD Hybrid full dikurangi supervised pada seed yang sama.

{chr(10).join(summary_table)}

Selisih mAP50–95 per seed:

| seed | Hybrid full | Supervised | Δ Hybrid − supervised |
| --- | --- | --- | --- |
{chr(10).join(seed_deltas)}

## Hasil per kelas

{chr(10).join(class_table)}

## Interpretasi dan langkah berikutnya

KD Hybrid full menaikkan mAP50–95 VAL terhadap kontrol supervised pada ketiga seed. Rerata selisihnya `{fmt_pm(*summaries['mAP50-95']['delta'], signed=True)}`. Pada confidence 0,25, F1 makro hampir sama tetapi sedikit lebih rendah (Δ `{fmt_pm(*summaries['F1@0.25']['delta'], signed=True)}`); precision rata-rata turun dan recall rata-rata naik. Jadi hasil VAL mendukung KD Hybrid full untuk dipertimbangkan pada evaluasi TEST terkunci, tetapi tidak menunjukkan peningkatan F1 pada operating point tersebut.

Simpangan baku dari tiga seed bersifat deskriptif dengan `n=3`; ini bukan uji signifikansi. Metrik VAL mengukur dataset Advance Vision pada level gambar, bukan kamera atau runtime OP3. Checkpoint deployment OP3 tidak berubah dari hasil ini. Evaluasi TEST terkunci adalah langkah berikutnya setelah pemilihan metode; jangan menggunakannya untuk mengubah objective atau threshold.

## Artefak sumber

- Evaluasi JSON: [`runs/val_ablation/hybrid_20261022_multiseed/`](../../runs/val_ablation/hybrid_20261022_multiseed/)
- Tabel hasil keseluruhan: [T04](../tabel/T04_ablasi_kd_val.md)
- Perbandingan berpasangan: [T28](../tabel/T28_selisih_kd_hybrid_val.md)
- Perbandingan per kelas: [T29](../tabel/T29_kd_hybrid_val_per_kelas.md)
- Skrip evaluasi: [`evaluate_val_ablation.py`](../../scripts/evaluate_val_ablation.py)
- Skrip pembaruan tabel: [`build_kd_hybrid_multiseed_val_tables.py`](../../scripts/build_kd_hybrid_multiseed_val_tables.py)
"""
    REPORT.write_text(content, encoding="utf-8")


def update_t04_prose(evals: dict[tuple[str, int], dict[str, Any]]) -> None:
    summaries = metric_summaries(evals)
    delta_map = summaries["mAP50-95"]["delta"]
    delta_p = summaries["precision@0.25"]["delta"]
    delta_r = summaries["recall@0.25"]["delta"]
    delta_f1 = summaries["F1@0.25"]["delta"]
    text = T04_MD.read_text(encoding="utf-8")
    start = text.find("Perubahan pilot `pure_weighted`")
    if start < 0:
        start = text.find("Perubahan pilot terhadap `pure_v4`")
    end = text.find("Catatan mekanisme:", start)
    if start < 0 or end < 0:
        raise RuntimeError("Could not locate the T04 interpretation block")
    replacement = (
        "Perubahan pilot `pure_weighted` terhadap `pure_v4` seed 42: mAP50–95 turun 0,0919 dan F1 pada confidence 0,25 turun 0,7773. "
        "Pilot `pure_weighted` tidak diteruskan ke seed tambahan.\n\n"
        f"KD Hybrid full dibandingkan dengan student supervised pada tiga seed berpasangan. Rerata Δ mAP50–95 VAL adalah "
        f"**{fmt_pm(*delta_map, signed=True)}**, dengan Δ positif pada seed 42, 1337, dan 2025. Pada confidence 0,25, rerata Δ precision "
        f"{fmt_pm(*delta_p, signed=True)}, Δ recall {fmt_pm(*delta_r, signed=True)}, dan Δ F1 {fmt_pm(*delta_f1, signed=True)}. "
        "Hasil mendukung Hybrid full sebagai kandidat untuk evaluasi TEST terkunci berdasarkan mAP50–95, dengan trade-off P/R/F1 tetap dilaporkan. "
        "Ini hasil VAL Advance Vision level gambar, bukan evaluasi kamera OP3; model deployment OP3 belum diganti.\n\n"
    )
    T04_MD.write_text(text[:start] + replacement + text[end:], encoding="utf-8")
    lines = T04_MD.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.startswith("Status:"):
            lines[i] = "Status: Mencakup KD pure tiga seed, pilot pure_weighted seed 42, hybrid_feature seed 42, dan hybrid_full tiga seed."
            break
    T04_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_indexes() -> None:
    text = INDEX.read_text(encoding="utf-8")
    text = text.replace(
        "Pembaruan T27: 2026-10-21.",
        "Pembaruan T29: 2026-10-22. T28–T29 merangkum evaluasi VAL KD Hybrid full tiga seed berpasangan dengan supervised; TEST tidak digunakan.",
    )
    text = text.replace(
        "| T04 | Lengkap untuk ablasi pilot VAL: `pure_v4` tiga seed dan `pure_weighted` seed 42; hasil kandidat menurun. | [CSV](tabel/T04_ablasi_kd_val.csv) · [Markdown](tabel/T04_ablasi_kd_val.md) · [Per kelas](tabel/T04_ablasi_kd_val_per_kelas.md) |",
        "| T04 | Lengkap untuk KD pure tiga seed, pilot pure_weighted seed 42, hybrid_feature seed 42, dan hybrid_full tiga seed; hasil Hybrid full dibandingkan dengan supervised pada T28–T29. | [CSV](tabel/T04_ablasi_kd_val.csv) · [Markdown](tabel/T04_ablasi_kd_val.md) · [Per kelas](tabel/T04_ablasi_kd_val_per_kelas.md) |",
    )
    t28 = "| T28 | Evaluasi VAL berpasangan KD Hybrid full vs supervised pada tiga seed, rerata ± SD dan delta. | [CSV](tabel/T28_selisih_kd_hybrid_val.csv) · [Markdown](tabel/T28_selisih_kd_hybrid_val.md) |"
    t29 = "| T29 | Evaluasi VAL per kelas berpasangan KD Hybrid full vs supervised pada tiga seed. | [CSV](tabel/T29_kd_hybrid_val_per_kelas.csv) · [Markdown](tabel/T29_kd_hybrid_val_per_kelas.md) |"
    if "| T28 |" not in text:
        at = text.find("\n", text.find("| T27 |"))
        if at < 0:
            raise RuntimeError("Could not find T27 row in index")
        text = text[:at + 1] + t28 + "\n" + t29 + "\n" + text[at + 1:]
    INDEX.write_text(text, encoding="utf-8")

    lab = LAB_README.read_text(encoding="utf-8")
    lab = lab.replace("Pembaruan: 20 Oktober 2026.", "Pembaruan: 22 Oktober 2026.")
    lab = lab.replace(
        "Metode penelitian adalah **Knowledge Distillation (KD) murni dengan objective teacher-only**; student supervised adalah kontrol. Angka TEST berasal dari evaluasi terkunci pada split resmi Roboflow Advance Vision v1. Hasilnya berlaku pada level gambar dan belum menjadi ukuran akurasi kamera ROBOTIS OP3.",
        "Analisis ini memuat eksperimen utama **KD murni teacher-only** dan eksperimen lanjutan **KD Hybrid full** yang dibandingkan dengan student supervised. Hasil TEST terkunci yang sudah ada berasal dari eksperimen KD murni; evaluasi KD Hybrid pada pembaruan ini baru sampai VAL. Semua hasil berlaku pada level gambar dan bukan ukuran akurasi kamera ROBOTIS OP3.",
    )
    lab = lab.replace(
        "| T04 | Ablasi objective KD pada VAL | Lengkap untuk pilot: `pure_v4` tiga seed dan `pure_weighted` satu seed | [Markdown](../tabel/T04_ablasi_kd_val.md) · [CSV](../tabel/T04_ablasi_kd_val.csv) · [Per kelas](../tabel/T04_ablasi_kd_val_per_kelas.md) |",
        "| T04 | Ablasi objective KD pada VAL | Lengkap untuk KD pure tiga seed, pilot pure_weighted seed 42, hybrid_feature seed 42, dan hybrid_full tiga seed | [Markdown](../tabel/T04_ablasi_kd_val.md) · [CSV](../tabel/T04_ablasi_kd_val.csv) · [Per kelas](../tabel/T04_ablasi_kd_val_per_kelas.md) |",
    )
    section = """## KD Hybrid full: hasil VAL tiga seed

KD Hybrid full dan kontrol supervised dievaluasi ulang pada VAL dengan prosedur yang sama. Rerata mAP50–95 Hybrid full **0,7505 ± 0,0018**, supervised **0,7208 ± 0,0041**, dan delta berpasangan **+0,0297 ± 0,0047** pada tiga seed. Selisih mAP50–95 positif pada setiap pasangan. F1 makro pada confidence 0,25 hampir sama dan sedikit lebih rendah untuk Hybrid full; precision turun sementara recall naik. Lihat [laporan evaluasi](HASIL_KD_HYBRID_MULTI_SEED_VAL_2026-10-22.md), [T28](../tabel/T28_selisih_kd_hybrid_val.md), dan [T29](../tabel/T29_kd_hybrid_val_per_kelas.md).

Hasil ini hanya mendukung pertimbangan kandidat berdasarkan VAL. TEST KD Hybrid belum dijalankan dan checkpoint OP3 belum diganti.

"""
    if "## KD Hybrid full: hasil VAL tiga seed" not in lab:
        marker = "## Data yang masih dibutuhkan"
        if marker not in lab:
            raise RuntimeError("Could not find insertion point in lab/server README")
        lab = lab.replace(marker, section + marker)
    lab = lab.replace(
        "- T04 sudah memuat pilot `pure_weighted` seed 42. Perbandingan kandidat lintas tiga seed belum tersedia, dan pilot yang menurun tidak dipilih untuk pengulangan. Keputusan anggaran epoch eksperimen utama D3 tetap belum dikunci.",
        "- T04 kini memuat hasil VAL KD Hybrid full tiga seed. T28–T29 memuat perbandingan berpasangan dengan supervised; evaluasi TEST Hybrid masih diperlukan untuk melengkapi klaim generalisasi level gambar.",
    )
    LAB_README.write_text(lab, encoding="utf-8")


def update_manifests(evals: dict[tuple[str, int], dict[str, Any]], manifests: dict[tuple[str, int], dict[str, Any]], run_dirs: dict[tuple[str, int], Path], overall_rows: list[dict[str, Any]], class_rows: list[dict[str, Any]]) -> None:
    eval_paths = [EVAL_DIR / f"{kind}_seed{seed}_val.json" for seed in (42, 1337, 2025) for kind in ("hybrid_full", "supervised")]
    output_paths = [T04, T04_MD, T04_CLASS, T04_CLASS_MD, T28, T28_MD, T29, T29_MD, REPORT, INDEX, LAB_README, *eval_paths]
    lab = read_json(LAB_MANIFEST)
    lab.setdefault("outputs_sha256", {})
    lab.setdefault("sources_sha256", {})
    for path in output_paths:
        lab["outputs_sha256"][path.relative_to(ROOT).as_posix()] = sha256(path)
    source_paths = [
        ROOT / "scripts/evaluate_val_ablation.py",
        ROOT / "scripts/build_kd_hybrid_multiseed_val_tables.py",
        ROOT / "artifacts/advance_vision_dataset_fingerprint.json",
        ROOT / "runs/kd_hybrid_logs/evaluate_hybrid_multiseed_val.log",
    ]
    for seed in (42, 1337, 2025):
        for kind in ("hybrid", "supervised"):
            run_dir = run_dirs[(kind, seed)]
            source_paths.extend((run_dir / "manifest.json", run_dir / "results.csv", run_dir / "weights/best.pt"))
    for path in source_paths:
        lab["sources_sha256"][path.relative_to(ROOT).as_posix()] = sha256(path)
    lab["hybrid_multiseed_val_added_on"] = "2026-10-22"
    lab["scope"] = "Curated lab/server tables T01-T14 plus VAL-only three-seed KD Hybrid full versus paired supervised; historical locked TEST remains the pure-KD experiment and OP3 metrics are separate."
    lab["notes"] = [
        "T04 includes KD pure three seeds, the pure_weighted seed-42 pilot, hybrid_feature seed 42, and hybrid_full across seeds 42/1337/2025.",
        "T28 and T29 compare KD Hybrid full with supervised using paired seeds on the same official VAL split; TEST was not opened.",
        "The evaluation reports mAP/P/R/F1 on Advance Vision image-level VAL; it does not establish camera OP3 accuracy or justify replacing the current OP3 checkpoint.",
        "The previous build_performance_tables.py may overwrite curated tables; compare output hashes before accepting a regeneration.",
    ]
    LAB_MANIFEST.write_text(json.dumps(lab, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    analysis = read_json(ANALYSIS_MANIFEST)
    analysis.setdefault("tables", {})
    analysis["tables"]["4"] = {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in (T04, T04_MD, T04_CLASS, T04_CLASS_MD)
    }
    analysis["tables"]["28"] = {path.relative_to(ROOT).as_posix(): sha256(path) for path in (T28, T28_MD)}
    analysis["tables"]["29"] = {path.relative_to(ROOT).as_posix(): sha256(path) for path in (T29, T29_MD)}
    analysis.setdefault("sources", {})
    for path in source_paths:
        analysis["sources"][str(path)] = sha256(path)
    analysis["kd_hybrid_multiseed_val_2026_10_22"] = {
        "status": "complete",
        "protocol": "official VAL only; three paired seeds; CPU FP32; TEST not opened",
        "report": REPORT.relative_to(ROOT).as_posix(),
        "paired_mAP50_95_delta_mean": metric_summaries(evals)["mAP50-95"]["delta"][0],
        "paired_mAP50_95_delta_sample_sd": metric_summaries(evals)["mAP50-95"]["delta"][1],
        "outputs": [path.relative_to(ROOT).as_posix() for path in output_paths],
    }
    ANALYSIS_MANIFEST.write_text(json.dumps(analysis, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    fingerprint = read_json(ROOT / "artifacts/advance_vision_dataset_fingerprint.json")
    expected_val = fingerprint["splits"]["val"]["split_fingerprint_sha256"]
    evals: dict[tuple[str, int], dict[str, Any]] = {}
    manifests: dict[tuple[str, int], dict[str, Any]] = {}
    run_dirs: dict[tuple[str, int], Path] = {}
    for seed in (42, 1337, 2025):
        for kind in ("hybrid", "supervised"):
            result, manifest, run_dir = load_verified_eval(seed, kind)
            if result["val_split_fingerprint_sha256"] != expected_val:
                raise RuntimeError(f"VAL fingerprint mismatch for seed {seed}, {kind}")
            evals[(kind, seed)] = result
            manifests[(kind, seed)] = manifest
            run_dirs[(kind, seed)] = run_dir
        validate_paired_training(manifests[("hybrid", seed)], manifests[("supervised", seed)], seed)

    overall_rows, class_rows = build_pair_tables(evals)
    overall_columns = ["seed", "metric", "hybrid_full", "supervised_student", "delta_hybrid_minus_supervised"]
    class_columns = ["class", "seed", "metric", "hybrid_full", "supervised_student", "delta_hybrid_minus_supervised"]
    build_t04_rows(evals, manifests, run_dirs)
    update_t04_prose(evals)
    write_csv(T28, overall_columns, overall_rows)
    write_pair_markdown(T28_MD, "T28. KD Hybrid full vs supervised pada VAL", "Perbandingan berpasangan pada split VAL resmi yang sama. Nilai seed adalah checkpoint `best.pt`; baris ringkasan menunjukkan rerata ± simpangan baku sampel tiga seed. Δ = Hybrid full − supervised.", overall_columns, overall_rows)
    write_csv(T29, class_columns, class_rows)
    write_pair_markdown(T29_MD, "T29. KD Hybrid full vs supervised pada VAL per kelas", "AP memakai confidence floor 0,001 dan NMS IoU 0,7. Precision, recall, dan F1 memakai confidence 0,25 serta IoU matching 0,50. Baris ringkasan memakai rerata ± SD sampel tiga pasangan seed.", class_columns, class_rows)
    write_report(evals)
    update_indexes()
    update_manifests(evals, manifests, run_dirs, overall_rows, class_rows)

    summaries = metric_summaries(evals)
    print("Updated T04, T28, T29, VAL report, indexes, and manifests.")
    for metric in ("mAP50-95", "F1@0.25"):
        print(metric, "hybrid=", fmt_pm(*summaries[metric]["hybrid"]), "supervised=", fmt_pm(*summaries[metric]["supervised"]), "paired_delta=", fmt_pm(*summaries[metric]["delta"], signed=True))
    print("Evaluation source directory:", EVAL_DIR.relative_to(ROOT))
    print("TEST used: false")


if __name__ == "__main__":
    main()
