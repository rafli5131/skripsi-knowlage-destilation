"""Build thesis tables from the locked TEST evaluation and inference benchmark."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEEDS = (42, 1337, 2025)
EXPECTED_RUNTIME_VERSIONS = {
    "python": "3.11.2",
    "numpy": "1.26.4",
    "torch": "2.4.1+cu121",
    "ultralytics": "8.4.130",
}


class AnalysisInputError(RuntimeError):
    """Raised when locked evaluation inputs do not form the planned comparison."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-manifest", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument(
        "--fingerprint",
        type=Path,
        default=ROOT / "artifacts/advance_vision_dataset_fingerprint.json",
    )
    parser.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/thesis_analysis")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def method_seed(label: str) -> tuple[str, int | None]:
    if label == "teacher_fp32":
        return "Teacher", None
    if label.startswith("kd_seed"):
        return "Pure KD", int(label.removeprefix("kd_seed"))
    if label.startswith("supervised_seed"):
        return "Supervised student", int(label.removeprefix("supervised_seed"))
    raise AnalysisInputError(f"Unexpected model label in locked evaluation: {label!r}")


def number(value: Any) -> float | None:
    return None if value is None else float(value)


def require_bootstrap_interval(interval: Any, context: str) -> None:
    if not isinstance(interval, dict):
        raise AnalysisInputError(f"Bootstrap interval is missing for {context}.")
    lower = number(interval.get("lower"))
    upper = number(interval.get("upper"))
    valid_replicates = interval.get("valid_replicates")
    if (
        lower is None
        or upper is None
        or not math.isfinite(lower)
        or not math.isfinite(upper)
        or lower < 0
        or upper > 1
        or lower > upper
        or not isinstance(valid_replicates, int)
        or not 1 <= valid_replicates <= 1000
    ):
        raise AnalysisInputError(f"Bootstrap interval is invalid for {context}.")


def read_inputs(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    test_path = args.test_manifest.expanduser().resolve()
    benchmark_path = args.benchmark.expanduser().resolve()
    fingerprint_path = args.fingerprint.expanduser().resolve()
    for path in (test_path, benchmark_path, fingerprint_path):
        if not path.is_file():
            raise FileNotFoundError(f"Required analysis input is missing: {path}")
    test_manifest = json.loads(test_path.read_text(encoding="utf-8"))
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
    for artifact, path_key, hash_key in (
        (test_manifest, "evaluator_script", "evaluator_script_sha256"),
        (benchmark, "benchmark_script", "benchmark_script_sha256"),
    ):
        script_path_value = artifact.get(path_key)
        script_hash = artifact.get(hash_key)
        if not script_path_value or not script_hash:
            raise AnalysisInputError(f"Evaluation provenance is missing {path_key}/{hash_key}.")
        script_path = Path(script_path_value).expanduser().resolve()
        if not script_path.is_file() or sha256_file(script_path) != script_hash:
            raise AnalysisInputError(f"Evaluation script differs from its recorded hash: {script_path}")
    if test_manifest.get("status") != "complete" or test_manifest.get("settings", {}).get("split") != "test":
        raise AnalysisInputError("TEST evaluation manifest is not a completed locked TEST evaluation.")
    kd_labels = {label for label in test_manifest.get("models", {}) if label.startswith("kd_seed")}
    if kd_labels != {"kd_seed42", "kd_seed1337", "kd_seed2025"}:
        raise AnalysisInputError("TEST evaluation must contain all three locked KD seeds.")
    kd_implementation_hashes = set()
    for label in sorted(kd_labels):
        evidence = test_manifest["models"][label].get("training_artifact_provenance", {})
        implementation = evidence.get("distillation_implementation")
        expected_snapshot_timing = label != "kd_seed42"
        if (
            not isinstance(implementation, dict)
            or implementation.get("module") != "ultralytics.nn.distill_model"
            or not implementation.get("sha256")
            or implementation.get("snapshot_recorded_at_run_time") is not expected_snapshot_timing
            or evidence.get("training_script_snapshot_recorded_at_run_time") is not expected_snapshot_timing
        ):
            raise AnalysisInputError(f"KD implementation provenance is missing or inconsistent for {label}.")
        kd_implementation_hashes.add(implementation["sha256"])
    if len(kd_implementation_hashes) != 1:
        raise AnalysisInputError("Final KD seeds use different DistillationModel implementations.")
    test_settings = test_manifest.get("settings", {})
    expected_test_settings = {
        "split": "test",
        "imgsz": 640,
        "batch": 16,
        "workers": 2,
        "device": "0",
        "cache": False,
        "augmentation": False,
        "precision": "FP32",
        "amp": False,
        "conf": 0.001,
        "confidence_threshold_policy": "candidate floor fixed at 0.001 for AP; point P/R/F1 fixed at 0.25 before TEST",
        "metric_operating_confidence_threshold": 0.25,
        "metric_operating_iou_threshold": 0.5,
        "iou": 0.7,
        "rect": True,
        "plots": False,
    }
    if any(test_settings.get(key) != value for key, value in expected_test_settings.items()):
        raise AnalysisInputError("TEST evaluation settings differ from the locked protocol.")
    if test_manifest.get("dataset_fingerprint_sha256") != sha256_file(fingerprint_path):
        raise AnalysisInputError("TEST results do not reference the current dataset fingerprint file.")
    expected_test_hash = fingerprint.get("splits", {}).get("test", {}).get("split_fingerprint_sha256")
    if test_manifest.get("test_split_fingerprint_sha256") != expected_test_hash:
        raise AnalysisInputError("TEST results use a different TEST split fingerprint.")
    if test_manifest.get("test_image_count") != 592 or test_manifest.get("test_annotation_count") != 734:
        raise AnalysisInputError("TEST image/annotation counts differ from the audited split.")
    bootstrap_settings = test_manifest.get("settings", {}).get("bootstrap", {})
    expected_operating_point = {
        "confidence_threshold": 0.25,
        "true_positive_iou_threshold": 0.5,
        "candidate_confidence_floor_for_ap": 0.001,
        "precision_recall_averaging": "macro over the three classes",
    }
    expected_bootstrap = {
        "method": "nonparametric percentile bootstrap over TEST images, sampled with replacement",
        "confidence_level": 0.95,
        "replicates": 1000,
        "random_seed": 20261009,
        "sampling_unit": "image",
        "overall_metric_requires_all_classes": True,
        "operating_point": expected_operating_point,
    }
    if any(bootstrap_settings.get(key) != value for key, value in expected_bootstrap.items()):
        raise AnalysisInputError("TEST evaluator did not follow the recorded image-bootstrap protocol.")
    if test_manifest.get("metric_operating_point") != {
        **expected_operating_point,
        "selection": "fixed a priori from the Ultralytics default prediction confidence; not estimated on TEST",
    }:
        raise AnalysisInputError("TEST precision/recall/F1 operating point is missing or was not fixed a priori.")
    if not test_manifest.get("versions", {}).get("numpy"):
        raise AnalysisInputError("TEST manifest does not record the NumPy version used for bootstrap metrics.")
    benchmark_versions = benchmark.get("versions", {})
    if not benchmark_versions.get("numpy") or not benchmark_versions.get("opencv"):
        raise AnalysisInputError("Benchmark manifest does not record NumPy and OpenCV versions.")
    test_versions = test_manifest.get("versions", {})
    for version_key, expected_version in EXPECTED_RUNTIME_VERSIONS.items():
        if test_versions.get(version_key) != expected_version or benchmark_versions.get(version_key) != expected_version:
            raise AnalysisInputError(
                f"TEST and benchmark must use the frozen {version_key} version {expected_version}."
            )
    if benchmark.get("settings", {}).get("device") != "0":
        raise AnalysisInputError("Inference benchmark must use the locked logical CUDA device 0.")
    test_device = test_manifest.get("runtime", {}).get("device_name")
    benchmark_device = benchmark.get("settings", {}).get("device_name")
    if test_device != benchmark_device or test_device != "NVIDIA L40":
        raise AnalysisInputError("TEST evaluation and inference benchmark must use the same locked NVIDIA L40 device.")
    benchmark_data_yaml = Path(benchmark.get("data_yaml", "")).expanduser().resolve()
    if (
        not benchmark_data_yaml.is_file()
        or sha256_file(benchmark_data_yaml) != benchmark.get("data_yaml_sha256")
    ):
        raise AnalysisInputError("Inference benchmark data YAML is missing or differs from its recorded hash.")
    locked_val_hashes = {
        record.get("image_sha256") for record in fingerprint.get("splits", {}).get("val", {}).get("files", [])
    }
    if not benchmark.get("validation_image_sha256") or benchmark["validation_image_sha256"] not in locked_val_hashes:
        raise AnalysisInputError("Inference benchmark frame is not one of the fingerprinted VAL images.")
    settings = benchmark.get("settings", {})
    if settings.get("batch") != 1 or settings.get("precision") != "FP32":
        raise AnalysisInputError("Inference benchmark must use FP32 and batch size 1.")
    if settings.get("imgsz") != 640:
        raise AnalysisInputError("Inference benchmark image size differs from the locked 640-pixel protocol.")
    if settings.get("warmup_iterations") != 30 or settings.get("timed_iterations") != 200:
        raise AnalysisInputError("Inference benchmark warm-up/timed iteration counts differ from the locked protocol.")
    if settings.get("confidence") != 0.001 or settings.get("iou") != 0.7:
        raise AnalysisInputError("Inference benchmark confidence/IoU differs from the locked protocol.")
    if "diagnostic" not in str(benchmark.get("purpose", "")).lower():
        raise AnalysisInputError("Inference benchmark must be labeled as a diagnostic, not deployment evidence.")
    return test_manifest, benchmark


def build_records(
    test_manifest: dict[str, Any], benchmark: dict[str, Any], seeds: set[int]
) -> list[dict[str, Any]]:
    test_models = test_manifest.get("models", {})
    speed_models = benchmark.get("models", {})
    expected_labels = {"teacher_fp32"}
    expected_labels.update(f"kd_seed{seed}" for seed in seeds)
    expected_labels.update(f"supervised_seed{seed}" for seed in seeds)
    if set(test_models) != expected_labels:
        raise AnalysisInputError(
            f"TEST comparison must include exactly the teacher and paired seed runs {sorted(expected_labels)}; "
            f"got {sorted(test_models)}"
        )
    if set(speed_models) != expected_labels:
        raise AnalysisInputError("Speed benchmark labels must match all locked TEST models.")

    records = []
    for label in sorted(expected_labels):
        evaluated = test_models[label]
        speed = speed_models[label]
        latency_samples = speed.get("latency_ms", {}).get("samples", [])
        if len(latency_samples) != 200 or any(
            not math.isfinite(float(sample)) or float(sample) <= 0 for sample in latency_samples
        ):
            raise AnalysisInputError(f"Raw 200-sample latency series is missing or invalid for {label}.")
        test_checkpoint_hash = evaluated.get("checkpoint_sha256")
        benchmark_checkpoint_hash = speed.get("checkpoint_sha256")
        if not test_checkpoint_hash or benchmark_checkpoint_hash != test_checkpoint_hash:
            raise AnalysisInputError(
                f"TEST and benchmark results do not use the same checkpoint for {label}."
            )
        checkpoint_parameters = int(speed.get("parameters", 0))
        validator_parameters = int(evaluated.get("parameters", 0))
        if checkpoint_parameters <= 0 or validator_parameters <= 0:
            raise AnalysisInputError(f"Parameter counts are missing for {label}.")
        if label != "teacher_fp32":
            training_manifest_path = Path(evaluated.get("training_manifest", "")).expanduser().resolve()
            if not training_manifest_path.is_file():
                raise AnalysisInputError(f"Training manifest is missing for {label}: {training_manifest_path}")
            training_manifest = json.loads(training_manifest_path.read_text(encoding="utf-8"))
            if training_manifest.get("student_parameters") != checkpoint_parameters:
                raise AnalysisInputError(
                    f"Benchmark parameter count differs from the training architecture for {label}."
                )
        method, seed = method_seed(label)
        overall = evaluated.get("test_metrics", {}).get("overall", {})
        per_class = evaluated.get("test_metrics", {}).get("per_class", {})
        bootstrap = evaluated.get("bootstrap_ci_95", {})
        if evaluated.get("metric_operating_point") != test_manifest.get("metric_operating_point"):
            raise AnalysisInputError(f"Per-model metric operating point differs from TEST manifest for {label}.")
        if "mAP50-95" not in overall or "mAP50" not in overall:
            raise AnalysisInputError(f"Missing TEST metrics for {label}.")
        if (
            bootstrap.get("method")
            != "nonparametric percentile bootstrap over TEST images, sampled with replacement"
            or bootstrap.get("replicates") != 1000
            or bootstrap.get("sampling_unit") != "image"
            or bootstrap.get("confidence_level") != 0.95
            or bootstrap.get("random_seed") != 20261009
            or bootstrap.get("sample_size_per_replicate") != test_manifest.get("test_image_count")
        ):
            raise AnalysisInputError(f"Image-level bootstrap intervals are missing for {label}.")
        for metric in ("precision", "recall", "F1", "mAP50", "mAP50-95"):
            require_bootstrap_interval(bootstrap.get("overall", {}).get(metric), f"{label} overall {metric}")
            for class_name in ("ball", "gawang", "robot"):
                require_bootstrap_interval(
                    bootstrap.get("per_class", {}).get(class_name, {}).get(metric),
                    f"{label} {class_name} {metric}",
                )
        record: dict[str, Any] = {
            "model": label,
            "method": method,
            "seed": seed if seed is not None else "",
            "P_R_F1_confidence_threshold": test_manifest["metric_operating_point"]["confidence_threshold"],
            "P_R_F1_IoU_threshold": test_manifest["metric_operating_point"]["true_positive_iou_threshold"],
            "val_mAP50": number(evaluated.get("validation_metrics", {}).get("metrics/mAP50(B)")),
            "val_mAP50_95": number(evaluated.get("validation_metrics", {}).get("metrics/mAP50-95(B)")),
            "test_precision": number(overall.get("precision")),
            "test_recall": number(overall.get("recall")),
            "test_F1": number(overall.get("F1")),
            "test_mAP50": number(overall.get("mAP50")),
            "test_mAP50_95": number(overall.get("mAP50-95")),
            # Count the checkpoint architecture before the first predictor call
            # fuses Conv-BN layers. Preserve the validator's post-fusion count
            # separately as a diagnostic; do not use it for compression ratios.
            "parameters": checkpoint_parameters,
            "parameters_after_validator_fusion": validator_parameters,
            "checkpoint_size_bytes": int(evaluated["checkpoint_size_bytes"]),
            "checkpoint_size_MiB": int(evaluated["checkpoint_size_bytes"]) / (1024**2),
            "GFLOPs": number(speed.get("flops_gflops")),
            "latency_mean_ms": number(speed.get("latency_ms", {}).get("mean")),
            "latency_median_ms": number(speed.get("latency_ms", {}).get("median")),
            "latency_p95_ms": number(speed.get("latency_ms", {}).get("p95")),
            "throughput_images_s": number(speed.get("latency_ms", {}).get("images_per_second")),
            "checkpoint_sha256": evaluated.get("checkpoint_sha256"),
        }
        for metric in ("precision", "recall", "F1", "mAP50", "mAP50-95"):
            interval = bootstrap.get("overall", {}).get(metric) or {}
            metric_slug = metric.replace("-", "_")
            record[f"test_{metric_slug}_ci95_lower"] = number(interval.get("lower"))
            record[f"test_{metric_slug}_ci95_upper"] = number(interval.get("upper"))
            record[f"test_{metric_slug}_ci95_valid_replicates"] = interval.get("valid_replicates")
        for class_name in ("ball", "gawang", "robot"):
            class_metrics = per_class.get(class_name, {})
            class_intervals = bootstrap.get("per_class", {}).get(class_name, {})
            for class_metric in ("precision", "mAP50", "mAP50_95", "recall", "F1"):
                source_metric = "mAP50-95" if class_metric == "mAP50_95" else class_metric
                record[f"test_{class_name}_{class_metric}"] = number(class_metrics.get(source_metric))
                interval = class_intervals.get(source_metric) or {}
                record[f"test_{class_name}_{class_metric}_ci95_lower"] = number(interval.get("lower"))
                record[f"test_{class_name}_{class_metric}_ci95_upper"] = number(interval.get("upper"))
                record[f"test_{class_name}_{class_metric}_ci95_valid_replicates"] = interval.get("valid_replicates")
        records.append(record)
    teacher = next(record for record in records if record["method"] == "Teacher")
    teacher_map = teacher["test_mAP50_95"]
    for record in records:
        if record["method"] == "Teacher":
            record["test_mAP50_95_delta_vs_teacher"] = 0.0
            record["mAP50_95_retention_vs_teacher_percent"] = 100.0
            record["parameter_reduction_vs_teacher_percent"] = 0.0
            record["checkpoint_size_reduction_vs_teacher_percent"] = 0.0
            record["latency_speedup_vs_teacher"] = 1.0
            record["GFLOPs_reduction_vs_teacher_percent"] = 0.0
            continue
        record["test_mAP50_95_delta_vs_teacher"] = record["test_mAP50_95"] - teacher_map
        record["mAP50_95_retention_vs_teacher_percent"] = (
            100.0 * record["test_mAP50_95"] / teacher_map if teacher_map else None
        )
        record["parameter_reduction_vs_teacher_percent"] = (
            100.0 * (teacher["parameters"] - record["parameters"]) / teacher["parameters"]
        )
        record["checkpoint_size_reduction_vs_teacher_percent"] = (
            100.0 * (teacher["checkpoint_size_bytes"] - record["checkpoint_size_bytes"])
            / teacher["checkpoint_size_bytes"]
        )
        record["latency_speedup_vs_teacher"] = (
            teacher["latency_median_ms"] / record["latency_median_ms"]
            if teacher["latency_median_ms"] and record["latency_median_ms"]
            else None
        )
        record["GFLOPs_reduction_vs_teacher_percent"] = (
            100.0 * (teacher["GFLOPs"] - record["GFLOPs"]) / teacher["GFLOPs"]
            if teacher["GFLOPs"] and record["GFLOPs"] is not None
            else None
        )
    for record in records:
        for class_name in ("ball", "gawang", "robot"):
            for metric in ("precision", "mAP50", "mAP50_95", "recall", "F1"):
                metric_key = f"test_{class_name}_{metric}"
                delta_key = f"{metric_key}_delta_vs_teacher"
                if record["method"] == "Teacher":
                    record[delta_key] = 0.0
                else:
                    student_value = record.get(metric_key)
                    teacher_value = teacher.get(metric_key)
                    record[delta_key] = (
                        float(student_value) - float(teacher_value)
                        if student_value is not None and teacher_value is not None
                        else None
                    )
    return records


def summary_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics = (
        "val_mAP50",
        "val_mAP50_95",
        "test_mAP50",
        "test_mAP50_95",
        "test_precision",
        "test_recall",
        "test_F1",
        "parameters",
        "checkpoint_size_MiB",
        "GFLOPs",
        "latency_median_ms",
        "latency_p95_ms",
        "throughput_images_s",
        "test_mAP50_95_delta_vs_teacher",
        "mAP50_95_retention_vs_teacher_percent",
        "parameter_reduction_vs_teacher_percent",
        "checkpoint_size_reduction_vs_teacher_percent",
        "latency_speedup_vs_teacher",
        "GFLOPs_reduction_vs_teacher_percent",
    )
    metrics = (*metrics, *(
        f"test_{class_name}_{class_metric}"
        for class_name in ("ball", "gawang", "robot")
        for class_metric in ("precision", "mAP50", "mAP50_95", "recall", "F1")
    ))
    metrics = (*metrics, *(
        f"test_{class_name}_{class_metric}_delta_vs_teacher"
        for class_name in ("ball", "gawang", "robot")
        for class_metric in ("precision", "mAP50", "mAP50_95", "recall", "F1")
    ))
    result = []
    for method in ("Teacher", "Supervised student", "Pure KD"):
        method_records = [record for record in records if record["method"] == method]
        for metric in metrics:
            values = [float(record[metric]) for record in method_records if record[metric] is not None]
            result.append(
                {
                    "method": method,
                    "metric": metric,
                    "n": len(values),
                    "mean": statistics.mean(values) if values else None,
                    "sample_sd": statistics.stdev(values) if len(values) > 1 else None,
                }
            )
    return result


def paired_seed_deltas(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kd = {int(record["seed"]): record for record in records if record["method"] == "Pure KD"}
    supervised = {
        int(record["seed"]): record for record in records if record["method"] == "Supervised student"
    }
    metrics = ("test_mAP50", "test_mAP50_95", "test_precision", "test_recall", "test_F1") + tuple(
        f"test_{class_name}_{class_metric}"
        for class_name in ("ball", "gawang", "robot")
        for class_metric in ("precision", "mAP50", "mAP50_95", "recall", "F1")
    )
    per_seed = []
    for seed in sorted(kd):
        row: dict[str, Any] = {"seed": seed}
        for metric in metrics:
            kd_value = float(kd[seed][metric])
            supervised_value = float(supervised[seed][metric])
            row[f"kd_{metric}"] = kd_value
            row[f"supervised_{metric}"] = supervised_value
            row[f"kd_minus_supervised_{metric}"] = kd_value - supervised_value
        per_seed.append(row)
    aggregate = []
    for metric in metrics:
        delta_values = [row[f"kd_minus_supervised_{metric}"] for row in per_seed]
        aggregate.append(
            {
                "comparison": "Pure KD minus supervised student",
                "metric": metric,
                "n_pairs": len(delta_values),
                "mean_paired_delta": statistics.mean(delta_values) if delta_values else None,
                "sample_sd": statistics.stdev(delta_values) if len(delta_values) > 1 else None,
            }
        )
    return per_seed, aggregate


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def format_value(value: Any, digits: int = 4) -> str:
    return "—" if value is None else f"{float(value):.{digits}f}"


def markdown_report(
    records: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
    paired_summaries: list[dict[str, Any]],
    inference_device: str,
) -> str:
    lines = [
        "# Ringkasan Analisis Skripsi",
        "",
        f"Sumber kebenaran metrik TEST adalah manifest evaluasi locked-test; ukuran/latensi/FLOPs berasal dari benchmark FP32 batch 1 pada {inference_device}. Precision/recall/F1 memakai confidence tetap >0,25 dan IoU pencocokan 0,50 yang dikunci sebelum TEST; confidence floor 0,001 dipakai untuk menghitung kurva AP, dengan NMS IoU 0,7. Student KD dan supervised menggunakan arsitektur student yang sama, sehingga kontras utama di antara keduanya adalah objective training; kompresi student KD dinilai terpisah terhadap teacher. Hasil hanya mengukur split level-gambar Advance Vision dan bukan klaim deployment robot.",
        "Jumlah parameter pada tabel dihitung dari checkpoint sebelum predictor melakukan fusi Conv-BN, dan jumlah student dicocokkan dengan manifest training. Jumlah pascafusi yang dicatat validator tersedia terpisah di `per_model.csv` sebagai diagnostik; rasio kompresi memakai jumlah parameter checkpoint.",
        "",
        "## Hasil per model dan seed",
        "",
        "| Model | Metode | Seed | VAL mAP50–95 | TEST P | TEST R | TEST F1 | TEST mAP50 | TEST mAP50–95 | Δ mAP50–95 vs teacher | Parameter | Size MiB | GFLOPs | Median ms | P95 ms | Speedup | Img/s |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in records:
        lines.append(
            "| {model} | {method} | {seed} | {val_mAP50_95} | {test_precision} | {test_recall} | {test_F1} | {test_mAP50} | {test_mAP50_95} | {mAP_delta} | {parameters:,} | {checkpoint_size_MiB} | {GFLOPs} | {latency_median_ms} | {latency_p95_ms} | {speedup}× | {throughput_images_s} |".format(
                model=row["model"],
                method=row["method"],
                seed=row["seed"] or "—",
                val_mAP50_95=format_value(row["val_mAP50_95"]),
                test_precision=format_value(row["test_precision"]),
                test_recall=format_value(row["test_recall"]),
                test_F1=format_value(row["test_F1"]),
                test_mAP50=format_value(row["test_mAP50"]),
                test_mAP50_95=format_value(row["test_mAP50_95"]),
                mAP_delta=format_value(row["test_mAP50_95_delta_vs_teacher"]),
                parameters=row["parameters"],
                checkpoint_size_MiB=format_value(row["checkpoint_size_MiB"], 2),
                GFLOPs=format_value(row["GFLOPs"], 3),
                latency_median_ms=format_value(row["latency_median_ms"], 3),
                latency_p95_ms=format_value(row["latency_p95_ms"], 3),
                speedup=format_value(row["latency_speedup_vs_teacher"], 2),
                throughput_images_s=format_value(row["throughput_images_s"], 2),
            )
        )
    lines.extend(
        [
            "",
            "## Mean dan simpangan baku antar-run",
            "",
            "| Metode | Metrik | n | Mean | SD sampel |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in summaries:
        if row["metric"] in {"test_mAP50", "test_mAP50_95", "test_precision", "test_recall", "test_F1", "parameters", "checkpoint_size_MiB", "GFLOPs", "latency_median_ms", "latency_p95_ms", "throughput_images_s", "test_mAP50_95_delta_vs_teacher", "mAP50_95_retention_vs_teacher_percent", "parameter_reduction_vs_teacher_percent", "checkpoint_size_reduction_vs_teacher_percent", "latency_speedup_vs_teacher", "GFLOPs_reduction_vs_teacher_percent"} or row["metric"].startswith("test_ball_") or row["metric"].startswith("test_gawang_") or row["metric"].startswith("test_robot_"):
            lines.append(
                f"| {row['method']} | {row['metric']} | {row['n']} | {format_value(row['mean'])} | {format_value(row['sample_sd'])} |"
            )
    lines.extend(
        [
            "",
            "## Dampak metrik per kelas relatif terhadap teacher",
            "",
            "Nilai negatif menunjukkan student berada di bawah teacher untuk metrik tersebut; nilai positif menunjukkan student berada di atas teacher pada split TEST level-gambar.",
            "",
            "| Metode student | Kelas | Metrik | n | Mean delta | SD sampel |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    class_delta_suffix = "_delta_vs_teacher"
    for row in summaries:
        if row["method"] not in {"Supervised student", "Pure KD"}:
            continue
        for class_name in ("ball", "gawang", "robot"):
            prefix = f"test_{class_name}_"
            metric_key = row["metric"]
            if metric_key.startswith(prefix) and metric_key.endswith(class_delta_suffix):
                metric_name = metric_key[len(prefix) : -len(class_delta_suffix)]
                lines.append(
                    f"| {row['method']} | {class_name} | {metric_name} | {row['n']} | "
                    f"{format_value(row['mean'])} | {format_value(row['sample_sd'])} |"
                )
    lines.extend(
        [
            "",
            "## Selisih berpasangan: pure KD minus supervised",
            "",
            "Kontras ini membandingkan objective pada arsitektur student yang sama. Mean dan SD selisih tiga pasangan seed bersifat deskriptif dan bukan uji signifikansi formal; seluruh pasangan seed ditampilkan.",
            "",
            "| Metrik TEST | Pasangan seed | Mean selisih | SD sampel |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in paired_summaries:
        lines.append(
            f"| {row['metric']} | {row['n_pairs']} | {format_value(row['mean_paired_delta'])} | {format_value(row['sample_sd'])} |"
        )
    lines.extend(
        [
            "",
            "## Interval kepercayaan bootstrap 95% pada TEST",
            "",
            "Interval dihitung dengan bootstrap nonparametrik pada tingkat gambar (592 gambar, sampling dengan pengembalian), 1.000 replikasi, seed 20261009, dan persentil 2,5–97,5. Interval bersyarat pada checkpoint yang diuji: interval menggambarkan variasi sampling gambar dan tidak mencakup variasi akibat mengulang training atau mengganti seed. Precision/recall/F1 memakai confidence tetap >0,25 dan IoU pencocokan 0,50 pada setiap replikasi; confidence threshold tidak dioptimalkan pada TEST. Untuk interval keseluruhan, hanya replikasi yang memuat ketiga kelas digunakan agar penyebut macro tetap tiga. Replikasi tanpa objek pada suatu kelas tidak berkontribusi pada interval kelas tersebut. Jumlah replikasi valid dicantumkan untuk setiap interval.",
            "",
            "| Model | Cakupan | Metrik | Batas bawah | Batas atas | Replikasi valid |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    ci_metrics = ("precision", "recall", "F1", "mAP50", "mAP50_95")
    for row in records:
        for metric in ci_metrics:
            lower_key = f"test_{metric}_ci95_lower"
            upper_key = f"test_{metric}_ci95_upper"
            valid_key = f"test_{metric}_ci95_valid_replicates"
            lines.append(
                f"| {row['model']} | keseluruhan | {metric.replace('_', '–')} | "
                f"{format_value(row.get(lower_key))} | {format_value(row.get(upper_key))} | "
                f"{row.get(valid_key) or 0} |"
            )
        for class_name in ("ball", "gawang", "robot"):
            for metric in ci_metrics:
                field = f"test_{class_name}_{metric}"
                lower_key = f"{field}_ci95_lower"
                upper_key = f"{field}_ci95_upper"
                valid_key = f"{field}_ci95_valid_replicates"
                lines.append(
                    f"| {row['model']} | {class_name} | {metric.replace('_', '–')} | "
                    f"{format_value(row.get(lower_key))} | {format_value(row.get(upper_key))} | "
                    f"{row.get(valid_key) or 0} |"
                )
    lines.extend(
        [
            "",
            "Semua model student terpilih melalui VAL sebelum evaluasi TEST. TEST hanya dipakai untuk pelaporan akhir; jangan gunakan tabel ini untuk mengubah konfigurasi atau memilih seed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output = args.output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite an existing analysis directory: {output}")
    test_manifest, benchmark = read_inputs(args)
    records = build_records(test_manifest, benchmark, set(args.seeds))
    summaries = summary_rows(records)
    per_seed_deltas, paired_summaries = paired_seed_deltas(records)
    output.mkdir(parents=True, exist_ok=False)
    write_csv(output / "per_model.csv", records)
    write_csv(output / "summary_mean_sd.csv", summaries)
    write_csv(output / "paired_seed_deltas.csv", per_seed_deltas)
    write_csv(output / "paired_summary.csv", paired_summaries)
    inference_device = str(benchmark.get("settings", {}).get("device_name", "device tidak tercatat"))
    (output / "ANALISIS.md").write_text(
        markdown_report(records, summaries, paired_summaries, inference_device), encoding="utf-8"
    )
    input_manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_script": str(Path(__file__).resolve()),
        "analysis_script_sha256": sha256_file(Path(__file__).resolve()),
        "dataset_fingerprint": str(args.fingerprint.expanduser().resolve()),
        "dataset_fingerprint_sha256": sha256_file(args.fingerprint.expanduser().resolve()),
        "test_split_fingerprint_sha256": test_manifest.get("test_split_fingerprint_sha256"),
        "test_manifest": str(args.test_manifest.expanduser().resolve()),
        "test_manifest_sha256": sha256_file(args.test_manifest.expanduser().resolve()),
        "benchmark": str(args.benchmark.expanduser().resolve()),
        "benchmark_sha256": sha256_file(args.benchmark.expanduser().resolve()),
        "benchmark_settings": benchmark.get("settings", {}),
        "benchmark_versions": benchmark.get("versions", {}),
        "test_bootstrap_settings": test_manifest.get("settings", {}).get("bootstrap", {}),
        "parameter_count_semantics": {
            "parameters": (
                "Checkpoint model count recorded by the fixed-image benchmark before its first predict call; "
                "student counts are cross-checked against training manifests."
            ),
            "parameters_after_validator_fusion": (
                "Count after TEST validator AutoBackend setup, which fuses Conv-BN layers; diagnostic only, "
                "not used for compression ratios."
            ),
        },
        "test_evaluator_versions": test_manifest.get("versions", {}),
        "status": "complete",
        "models": len(records),
        "seeds": sorted(set(args.seeds)),
        "outputs": {
            name: {
                "path": str(output / name),
                "sha256": sha256_file(output / name),
            }
            for name in (
                "per_model.csv",
                "summary_mean_sd.csv",
                "paired_seed_deltas.csv",
                "paired_summary.csv",
                "ANALISIS.md",
            )
        },
    }
    (output / "analysis_manifest.json").write_text(
        json.dumps(input_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Thesis analysis tables written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
