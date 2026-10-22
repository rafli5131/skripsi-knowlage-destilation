"""Evaluate the frozen three-seed Hybrid full extension on the official TEST split.

This is a follow-up experiment: the split was previously used for teacher and
pure-KD evaluations. Run --preflight before the one-time TEST evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
import ultralytics

try:
    from . import evaluate_locked_test as previous
except ImportError:
    import evaluate_locked_test as previous


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/PROTOKOL_TEST_KD_HYBRID_2026-10-22.md"
REGISTRY = ROOT / "configs/model_registry.yaml"
FINGERPRINT = ROOT / "artifacts/advance_vision_dataset_fingerprint.json"
HISTORICAL_TEST = ROOT / "runs/final_test/pure_kd_official_split_locked_retry1/manifest.json"
OUTPUT = ROOT / "runs/final_test/hybrid_full_official_split_20261022"
SEEDS = (42, 1337, 2025)
SPECS = [
    (
        f"hybrid_full_seed{seed}",
        ROOT / f"runs/kd_hybrid/yolo11_tiny_hybrid_full_seed{seed}/weights/best.pt",
    )
    for seed in SEEDS
] + [
    (
        f"supervised_seed{seed}",
        ROOT
        / (
            "runs/supervised/yolo11_tiny_supervised_seed42_retry1/weights/best.pt"
            if seed == 42
            else f"runs/supervised/yolo11_tiny_supervised_seed{seed}/weights/best.pt"
        ),
    )
    for seed in SEEDS
]
SUPERVISED_SOURCE_COMMIT = "965e8d860576450145400c058d69c8a8eaf89ea6"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true", help="Check frozen inputs without reading TEST images or labels.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    return parser.parse_args()


def checked_snapshot(manifest: dict[str, Any], key: str, label: str) -> str:
    record = manifest.get(key)
    if not isinstance(record, dict) or record.get("snapshot_recorded_at_run_time") is not True:
        raise previous.TestEvaluationError(f"Run-time {key} snapshot is missing for {label}.")
    path = Path(str(record.get("path", ""))).expanduser().resolve()
    expected_hash = record.get("sha256")
    if not path.is_file() or not expected_hash or previous.sha256_file(path) != expected_hash:
        raise previous.TestEvaluationError(f"Run-time {key} snapshot hash differs for {label}: {path}")
    return str(expected_hash)


def historical_supervised_models(
    historical: dict[str, Any], fingerprint: dict[str, Any]
) -> list[tuple[str, Path, dict[str, Any], Path, Path | None]]:
    """Use the earlier completed TEST audit as provenance for unchanged controls.

    The current supervised training script changed after these runs. Its exact
    training-time bytes are recoverable from the first repository commit.
    """
    original_source = subprocess.check_output(
        [
            "git", "-c", f"safe.directory={ROOT}", "show",
            f"{SUPERVISED_SOURCE_COMMIT}:scripts/train_supervised_baseline.py",
        ],
        cwd=ROOT,
    )
    source_hash = hashlib.sha256(original_source).hexdigest()
    expected_splits = {
        split: fingerprint["splits"][split]["split_fingerprint_sha256"]
        for split in ("train", "val", "test")
    }
    models = []
    for label, checkpoint in SPECS:
        if not label.startswith("supervised_seed"):
            continue
        checkpoint = checkpoint.resolve()
        manifest_path = checkpoint.parent.parent / "manifest.json"
        if not checkpoint.is_file() or not manifest_path.is_file():
            raise FileNotFoundError(f"Historical control artifact is missing for {label}.")
        run_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        prior = historical.get("models", {}).get(label)
        if not isinstance(prior, dict):
            raise previous.TestEvaluationError(f"Historical TEST audit did not include {label}.")
        if (
            run_manifest.get("status") != "complete"
            or run_manifest.get("test_split_used") is not False
            or run_manifest.get("dataset_fingerprint_sha256") != previous.sha256_file(FINGERPRINT)
            or run_manifest.get("dataset_split_fingerprints") != expected_splits
            or run_manifest.get("student_best_sha256") != previous.sha256_file(checkpoint)
            or prior.get("checkpoint_sha256") != previous.sha256_file(checkpoint)
            or prior.get("training_manifest_sha256") != previous.sha256_file(manifest_path)
        ):
            raise previous.TestEvaluationError(f"Historical TEST provenance or hash differs for {label}.")
        script_hash = run_manifest.get("training_script_sha256")
        if label != "supervised_seed42" and script_hash != source_hash:
            raise previous.TestEvaluationError(f"Training-time Git source hash differs for {label}.")
        if label == "supervised_seed42" and run_manifest.get("dataset_snapshot_provenance", {}).get("linked_after_training") is not True:
            raise previous.TestEvaluationError("Legacy seed-42 provenance is not explicitly recorded.")
        models.append((label, checkpoint, run_manifest, manifest_path, None))
    return models


def validate_students(students: list[tuple[str, Path, dict[str, Any], Path, Path | None]]) -> None:
    required = {f"hybrid_full_seed{seed}" for seed in SEEDS} | {
        f"supervised_seed{seed}" for seed in SEEDS
    }
    if {entry[0] for entry in students} != required:
        raise previous.TestEvaluationError("The three paired Hybrid full and supervised seeds are required.")

    teacher_path = Path(previous.RUN_CONFIG["teacher_checkpoint"]).expanduser().resolve()
    if not teacher_path.is_file():
        raise FileNotFoundError(f"Frozen teacher is missing: {teacher_path}")
    teacher_hash = previous.sha256_file(teacher_path)
    architecture = None
    parameters = None
    training = None
    hybrid_distillation = None
    hybrid_implementation = None
    hybrid_head_loss = None
    hybrid_training_script = None

    for label, checkpoint, manifest, _, _ in students:
        hybrid = label.startswith("hybrid_full_seed")
        seed = int(label.removeprefix("hybrid_full_seed" if hybrid else "supervised_seed"))
        if manifest.get("seed") != seed or manifest.get("qat_used") is not False:
            raise previous.TestEvaluationError(f"Seed or QAT declaration differs for {label}.")
        if manifest.get("train_labels_used_for_loss") is not True:
            raise previous.TestEvaluationError(f"Labeled detection loss declaration is missing for {label}.")
        objective = str(manifest.get("objective", "")).lower()
        if hybrid and "hibrida" not in objective:
            raise previous.TestEvaluationError(f"Hybrid objective is not declared for {label}.")
        if not hybrid and "supervised" not in objective:
            raise previous.TestEvaluationError(f"Supervised objective is not declared for {label}.")
        actual_architecture = manifest.get("student_architecture_sha256")
        actual_parameters = manifest.get("student_parameters")
        if not actual_architecture or not actual_parameters:
            raise previous.TestEvaluationError(f"Student architecture provenance is missing for {label}.")
        if architecture is None:
            architecture, parameters = actual_architecture, actual_parameters
        elif (actual_architecture, actual_parameters) != (architecture, parameters):
            raise previous.TestEvaluationError("Paired students do not share the same architecture.")

        shared_training = dict(manifest.get("training", {}))
        shared_training.pop("seed", None)
        # Older supervised manifests omit this explicit option, but their
        # checked args.yaml records pretrained=false.
        shared_training.setdefault("pretrained", False)
        if training is None:
            training = shared_training
        elif shared_training != training:
            raise previous.TestEvaluationError(f"Shared training hyperparameters differ for {label}.")

        versions = manifest.get("versions", {})
        for key in ("python", "torch", "ultralytics"):
            if versions.get(key) != previous.EXPECTED_RUNTIME_VERSIONS[key]:
                raise previous.TestEvaluationError(f"Training runtime {key} differs for {label}.")

        if hybrid:
            if manifest.get("teacher_sha256") != teacher_hash:
                raise previous.TestEvaluationError(f"Teacher checkpoint differs for {label}.")
            distillation = manifest.get("distillation")
            if not isinstance(distillation, dict) or distillation.get("mode") != "hybrid_full":
                raise previous.TestEvaluationError(f"Hybrid full loss declaration is missing for {label}.")
            implementation_hash = checked_snapshot(manifest, "distillation_implementation", label)
            head_loss_hash = checked_snapshot(manifest, "head_loss_implementation", label)
            script_hash = manifest.get("training_script_sha256")
            if manifest.get("training_script_snapshot_recorded_at_run_time") is not True or not script_hash:
                raise previous.TestEvaluationError(f"Training script snapshot was not captured at run time for {label}.")
            actual = (distillation, implementation_hash, head_loss_hash, script_hash)
            if hybrid_distillation is None:
                hybrid_distillation, hybrid_implementation, hybrid_head_loss, hybrid_training_script = actual
            elif actual != (hybrid_distillation, hybrid_implementation, hybrid_head_loss, hybrid_training_script):
                raise previous.TestEvaluationError("Hybrid seeds do not share the same frozen KD implementation.")

        if manifest.get("student_best_checkpoint") != str(checkpoint):
            # parse_models independently resolves and verifies the path/hash.
            if Path(str(manifest.get("student_best_checkpoint", ""))).resolve() != checkpoint:
                raise previous.TestEvaluationError(f"Validation-best checkpoint differs for {label}.")


def preflight() -> tuple[list[tuple[str, Path, dict[str, Any], Path, Path | None]], dict[str, Any], dict[str, Path], dict[str, Any]]:
    versions = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "torch": str(torch.__version__),
        "ultralytics": ultralytics.__version__,
    }
    if versions != previous.EXPECTED_RUNTIME_VERSIONS:
        raise previous.TestEvaluationError(f"Runtime differs from the frozen TEST protocol: {versions!r}")
    if not PROTOCOL.is_file() or not REGISTRY.is_file() or not FINGERPRINT.is_file():
        raise FileNotFoundError("Protocol, model registry, or dataset fingerprint is missing.")
    if not HISTORICAL_TEST.is_file():
        raise FileNotFoundError(f"Historical TEST manifest is missing: {HISTORICAL_TEST}")
    historical = json.loads(HISTORICAL_TEST.read_text(encoding="utf-8"))
    fingerprint = json.loads(FINGERPRINT.read_text(encoding="utf-8"))
    if historical.get("status") != "complete" or historical.get("test_split_fingerprint_sha256") != fingerprint["splits"]["test"]["split_fingerprint_sha256"]:
        raise previous.TestEvaluationError("Historical TEST evidence differs from the official split fingerprint.")
    hybrid_specifications = [
        f"{label}={checkpoint}" for label, checkpoint in SPECS
        if label.startswith("hybrid_full_seed")
    ]
    students = previous.parse_models(hybrid_specifications, FINGERPRINT)
    students.extend(historical_supervised_models(historical, fingerprint))
    for label, checkpoint, _, _, _ in students:
        previous.validate_checkpoint(checkpoint, label=label, registry_path=REGISTRY)
    validate_students(students)
    data_yaml = Path(previous.RUN_CONFIG["evaluation_data_yaml"]).expanduser().resolve()
    data, splits = previous.resolve_splits(data_yaml)
    runtime = previous.runtime_device_metadata("0")
    if runtime.get("device_name") != "NVIDIA L40":
        raise previous.TestEvaluationError("Locked TEST extension must use NVIDIA L40 logical device 0.")
    return students, data, splits, {"versions": versions, "runtime": runtime, "historical": historical, "data_yaml": data_yaml}


def main() -> int:
    args = parse_args()
    students, data, splits, context = preflight()
    if args.preflight:
        print(json.dumps({
            "status": "ready_without_test_read",
            "models": {label: previous.sha256_file(checkpoint) for label, checkpoint, _, _, _ in students},
            "runtime": context["runtime"],
            "protocol_sha256": previous.sha256_file(PROTOCOL),
            "historical_test_manifest_sha256": previous.sha256_file(HISTORICAL_TEST),
        }, indent=2, sort_keys=True))
        return 0

    output = args.output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to reuse a TEST evaluation directory: {output}")
    test_fingerprint, test_images, test_annotations = previous.verify_test_fingerprint(splits["test"], FINGERPRINT)
    output.mkdir(parents=True, exist_ok=False)
    evaluation_args = argparse.Namespace(
        data=context["data_yaml"], device="0", imgsz=640, batch=16, workers=2
    )
    manifest: dict[str, Any] = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "started",
        "experiment": "KD Hybrid full three-seed TEST extension",
        "historical_test_exposure": "Official TEST was previously evaluated for teacher and pure KD; this is a follow-up comparison on the same split.",
        "historical_test_manifest": str(HISTORICAL_TEST),
        "historical_test_manifest_sha256": previous.sha256_file(HISTORICAL_TEST),
        "protocol": str(PROTOCOL),
        "protocol_sha256": previous.sha256_file(PROTOCOL),
        "evaluator_script": str(Path(__file__).resolve()),
        "evaluator_script_sha256": previous.sha256_file(Path(__file__).resolve()),
        "shared_metric_implementation": str(Path(previous.__file__).resolve()),
        "shared_metric_implementation_sha256": previous.sha256_file(Path(previous.__file__).resolve()),
        "model_registry_sha256": previous.sha256_file(REGISTRY),
        "data_yaml": str(context["data_yaml"]),
        "data_yaml_sha256": previous.sha256_file(context["data_yaml"]),
        "dataset_fingerprint": str(FINGERPRINT),
        "dataset_fingerprint_sha256": previous.sha256_file(FINGERPRINT),
        "test_split_fingerprint_sha256": test_fingerprint,
        "test_image_count": test_images,
        "test_annotation_count": test_annotations,
        "classes": previous.EXPECTED_NAMES,
        "settings": {
            "split": "test", "precision": "FP32", "imgsz": 640, "batch": 16,
            "workers": 2, "device": "0", "augmentation": False, "rect": True,
            "conf_for_ap": 0.001, "nms_iou": 0.7,
            "operating_confidence": 0.25, "matching_iou": 0.5,
            "bootstrap_replicates": previous.BOOTSTRAP_REPLICATES,
            "bootstrap_seed": previous.BOOTSTRAP_SEED,
        },
        "versions": context["versions"],
        "runtime": context["runtime"],
        "locked_models": [
            {
                "label": label,
                "checkpoint": str(checkpoint),
                "checkpoint_sha256": previous.sha256_file(checkpoint),
                "training_manifest": str(training_manifest_path),
                "training_manifest_sha256": previous.sha256_file(training_manifest_path),
            }
            for label, checkpoint, _, training_manifest_path, _ in students
        ],
        "models": {},
    }
    manifest_path = output / "manifest.json"
    previous.write_json(manifest_path, manifest)
    try:
        for label, checkpoint, run_manifest, training_manifest_path, _ in students:
            print(f"Evaluating frozen TEST: {label}", flush=True)
            result = previous.evaluate_one(
                label, checkpoint, run_manifest, data, evaluation_args,
                output, training_manifest_path,
            )
            manifest["models"][label] = result
            previous.write_json(output / f"{label}_metrics.json", result)
            previous.write_json(manifest_path, manifest)
        manifest["status"] = "complete"
        manifest["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        previous.write_json(manifest_path, manifest)
    except Exception as error:
        manifest["status"] = "failed"
        manifest["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["error"] = f"{type(error).__name__}: {error}"
        previous.write_json(manifest_path, manifest)
        raise
    print(f"Hybrid TEST evaluation complete: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
