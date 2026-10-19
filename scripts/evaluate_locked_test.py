"""Evaluate VAL-selected students and the provenance-checked teacher on frozen TEST."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
import ultralytics
import yaml
from torch.utils.data import Dataset
from ultralytics import YOLO
from ultralytics.cfg import DEFAULT_CFG, get_cfg
from ultralytics.data.build import build_dataloader
from ultralytics.data.dataset import YOLODataset
from ultralytics.models.yolo.detect.val import DetectionValidator
from ultralytics.utils.metrics import ap_per_class

try:
    from .model_registry import validate_checkpoint
    from .project_config import load_run_config
except ImportError:
    from model_registry import validate_checkpoint
    from project_config import load_run_config


ROOT = Path(__file__).resolve().parents[1]
RUN_CONFIG = load_run_config()
MODEL_REGISTRY = ROOT / "configs/model_registry.yaml"
EXPECTED_NAMES = {0: "ball", 1: "gawang", 2: "robot"}
EXPECTED_SEEDS = tuple(sorted(int(seed) for seed in RUN_CONFIG["queue"]["seeds"]))
EXPECTED_RUNTIME_VERSIONS = {
    "python": "3.11.2",
    "numpy": "1.26.4",
    "torch": "2.4.1+cu121",
    "ultralytics": "8.4.130",
}
EXPECTED_TEST_SETTINGS = {"imgsz": 640, "batch": 16, "workers": 2, "device": "0"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
BOOTSTRAP_REPLICATES = 1000
BOOTSTRAP_SEED = 20261009
BOOTSTRAP_CONFIDENCE_LEVEL = 0.95
METRIC_OPERATING_CONFIDENCE = 0.25
METRIC_MATCH_IOU_INDEX = 0
METRIC_MATCH_IOU_THRESHOLD = 0.5


class TestEvaluationError(RuntimeError):
    """Raised when the frozen TEST protocol cannot be followed safely."""


def runtime_device_metadata(device: str) -> dict[str, Any]:
    requested = str(device)
    metadata: dict[str, Any] = {
        "requested_device": requested,
        "platform": platform.platform(),
        "cuda_available": torch.cuda.is_available(),
        "cuda_runtime_version": torch.version.cuda,
        "cudnn_version": torch.backends.cudnn.version(),
        "visible_cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    }
    if requested.lower() == "cpu":
        metadata.update(
            {
                "device_type": "cpu",
                "device_name": platform.processor() or platform.machine(),
            }
        )
        return metadata
    if not torch.cuda.is_available():
        raise TestEvaluationError("CUDA was requested but is unavailable in this process.")

    token = requested.split(",", maxsplit=1)[0].strip().lower()
    if token in {"", "cuda"}:
        index = torch.cuda.current_device()
    elif token.startswith("cuda:"):
        index = int(token.split(":", maxsplit=1)[1])
    else:
        index = int(token)
    properties = torch.cuda.get_device_properties(index)
    metadata.update(
        {
            "device_type": "cuda",
            "logical_device_index": index,
            "device_name": torch.cuda.get_device_name(index),
            "total_memory_bytes": int(properties.total_memory),
            "compute_capability": f"{properties.major}.{properties.minor}",
        }
    )
    return metadata


class ReadOnlyTestDataset(YOLODataset):
    """Keep Ultralytics' label cache outside the frozen dataset tree."""

    def __init__(self, *args: Any, external_cache_path: Path, **kwargs: Any) -> None:
        self.external_cache_path = external_cache_path
        super().__init__(*args, **kwargs)

    def _load_or_scan_cache(self, cache_path: Path, cache_hash: str):
        del cache_path
        self.external_cache_path.parent.mkdir(parents=True, exist_ok=True)
        return super()._load_or_scan_cache(self.external_cache_path, cache_hash)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models",
        nargs="+",
        required=True,
        metavar="LABEL=CHECKPOINT",
        help="Completed student best checkpoints chosen using VAL only.",
    )
    parser.add_argument(
        "--teacher",
        metavar="LABEL=CHECKPOINT",
        default=f"teacher_fp32={RUN_CONFIG['teacher_checkpoint']}",
        help="Frozen FP32 teacher checkpoint; its training and prior TEST-only evaluation evidence are verified.",
    )
    parser.add_argument(
        "--teacher-training-manifest",
        type=Path,
        default=Path(RUN_CONFIG["teacher_training_manifest"]),
    )
    parser.add_argument(
        "--teacher-training-args",
        type=Path,
        default=Path(RUN_CONFIG["teacher_training_args"]),
    )
    parser.add_argument(
        "--teacher-test-evidence",
        type=Path,
        default=Path(RUN_CONFIG["teacher_test_evidence"]),
        help="Historical manifest proving the teacher was tested only after model selection.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path(RUN_CONFIG["evaluation_data_yaml"]),
    )
    parser.add_argument(
        "--fingerprint",
        type=Path,
        default=ROOT / "artifacts/advance_vision_dataset_fingerprint.json",
    )
    parser.add_argument("--device", default="0")
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(EXPECTED_SEEDS))
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / RUN_CONFIG["pipeline"]["evaluator_default_output"],
    )
    parser.add_argument("--model-registry", type=Path, default=MODEL_REGISTRY)
    parser.add_argument(
        "--retry-of-manifest",
        type=Path,
        help="Record a prior failed harness attempt that produced no model metrics.",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checkpoint_architecture_matches(
    checkpoint_paths: tuple[Path, ...], architecture_path: Path, expected_parameters: int
) -> bool:
    """Compare resumed checkpoint models with a fresh model parsed from the recorded YAML."""
    from ultralytics.nn.tasks import DetectionModel

    expected_model = DetectionModel(str(architecture_path), ch=3, nc=len(EXPECTED_NAMES), verbose=False)
    expected_yaml = dict(expected_model.yaml)
    expected_yaml.pop("yaml_file", None)
    expected_shapes = tuple(
        (name, tuple(value.shape)) for name, value in expected_model.state_dict().items()
    )
    expected_modules = tuple(
        (name, type(module).__module__, type(module).__qualname__)
        for name, module in expected_model.named_modules()
    )
    if sum(parameter.numel() for parameter in expected_model.parameters()) != expected_parameters:
        return False

    for checkpoint_path in checkpoint_paths:
        payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        model = payload.get("ema") or payload.get("model") if isinstance(payload, dict) else None
        if not isinstance(model, torch.nn.Module):
            return False
        actual_yaml = dict(getattr(model, "yaml", {}))
        actual_yaml.pop("yaml_file", None)
        actual_shapes = tuple((name, tuple(value.shape)) for name, value in model.state_dict().items())
        actual_modules = tuple(
            (name, type(module).__module__, type(module).__qualname__)
            for name, module in model.named_modules()
        )
        actual_parameters = sum(parameter.numel() for parameter in model.parameters())
        if (
            actual_yaml != expected_yaml
            or actual_shapes != expected_shapes
            or actual_modules != expected_modules
            or actual_parameters != expected_parameters
        ):
            return False
    return True


def documented_resume_model_reference(
    run_args: dict[str, Any], run_manifest: dict[str, Any], run_manifest_path: Path
) -> Path | None:
    """Return the resume checkpoint path only when args and manifest document the same run."""
    model_value = run_args.get("model")
    resume_value = run_args.get("resume")
    if not isinstance(model_value, str) or not isinstance(resume_value, str):
        return None
    model_path = Path(model_value).expanduser().resolve()
    resume_path = Path(resume_value).expanduser().resolve()
    expected_last = (run_manifest_path.parent / "weights" / "last.pt").resolve()
    if model_path != expected_last or resume_path != expected_last or not expected_last.is_file():
        return None
    for record in run_manifest.get("resume_history", []):
        recorded_checkpoint = record.get("checkpoint")
        if (
            recorded_checkpoint
            and Path(recorded_checkpoint).expanduser().resolve() == expected_last
            and record.get("resume_mode")
        ):
            return expected_last
    return None


def parse_models(
    specifications: list[str],
    fingerprint_path: Path,
) -> list[tuple[str, Path, dict[str, Any], Path, Path | None]]:
    parsed = []
    labels = set()
    kd_implementation_sha256: str | None = None
    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
    expected_fingerprint_sha256 = sha256_file(fingerprint_path)
    expected_split_fingerprints = {
        name: fingerprint["splits"][name]["split_fingerprint_sha256"] for name in ("train", "val", "test")
    }
    for specification in specifications:
        label, separator, path_value = specification.partition("=")
        if not separator or not label or not path_value:
            raise TestEvaluationError(f"Model must be LABEL=CHECKPOINT: {specification!r}")
        if Path(label).name != label or label in {".", ".."}:
            raise TestEvaluationError(f"Model label must be a simple directory name: {label!r}")
        if label in labels:
            raise TestEvaluationError(f"Model labels must be unique: {label!r}")
        labels.add(label)
        checkpoint = Path(path_value).expanduser().resolve()
        if not checkpoint.is_file():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")
        run_manifest_path = checkpoint.parent.parent / "manifest.json"
        if not run_manifest_path.is_file():
            raise TestEvaluationError(f"Training manifest is required beside checkpoint: {run_manifest_path}")
        run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
        if run_manifest.get("status") != "complete" or run_manifest.get("test_split_used") is not False:
            raise TestEvaluationError(f"Checkpoint is not a completed TEST-unseen training run: {checkpoint}")
        if label.startswith("kd_seed"):
            implementation = run_manifest.get("distillation_implementation")
            if not isinstance(implementation, dict):
                raise TestEvaluationError(f"KD implementation provenance is missing for {label}.")
            implementation_path = Path(str(implementation.get("path", ""))).expanduser().resolve()
            implementation_hash = implementation.get("sha256")
            expected_snapshot_timing = label != "kd_seed42"
            if (
                implementation.get("module") != "ultralytics.nn.distill_model"
                or not implementation_path.is_file()
                or not implementation_hash
                or sha256_file(implementation_path) != implementation_hash
                or implementation.get("snapshot_recorded_at_run_time") is not expected_snapshot_timing
                or run_manifest.get("training_script_snapshot_recorded_at_run_time") is not expected_snapshot_timing
            ):
                raise TestEvaluationError(
                    f"KD implementation snapshot is missing, changed, or has unexpected capture timing for {label}."
                )
            if kd_implementation_sha256 is None:
                kd_implementation_sha256 = str(implementation_hash)
            elif kd_implementation_sha256 != implementation_hash:
                raise TestEvaluationError("Final KD seeds use different DistillationModel implementations.")
        legacy_seed42_baseline = (
            label == "supervised_seed42"
            and Path(run_manifest.get("output_dir", "")).expanduser().resolve()
            == (ROOT / "runs/supervised" / RUN_CONFIG["queue"]["seeds"][42]["supervised"]).resolve()
            and run_manifest.get("dataset_snapshot_provenance", {}).get("linked_after_training") is True
        )
        snapshot_provenance = run_manifest.get("dataset_snapshot_provenance", {})
        if legacy_seed42_baseline and (
            snapshot_provenance.get("fingerprint_predates_run") is not True
            or snapshot_provenance.get("all_image_and_label_hashes_revalidated_at_link_time") is not True
        ):
            raise TestEvaluationError("Legacy seed-42 provenance lacks verified pre-run snapshot evidence.")
        for path_key, hash_key in (
            ("run_config_path", "run_config_sha256"),
            ("training_script_path", "training_script_sha256"),
        ):
            artifact_value = run_manifest.get(path_key)
            artifact_hash = run_manifest.get(hash_key)
            if not artifact_value or not artifact_hash:
                if legacy_seed42_baseline:
                    continue
                raise TestEvaluationError(f"Run config/code provenance is missing for {label}: {path_key}")
            artifact_path = Path(artifact_value).expanduser().resolve()
            if not artifact_path.is_file() or sha256_file(artifact_path) != artifact_hash:
                raise TestEvaluationError(f"Run config/code hash differs from its manifest for {label}: {artifact_path}")
        checkpoint_hash = sha256_file(checkpoint)
        if run_manifest.get("student_best_sha256") != checkpoint_hash:
            raise TestEvaluationError(f"Checkpoint hash differs from its training manifest: {checkpoint}")
        if run_manifest.get("dataset_fingerprint_sha256") != expected_fingerprint_sha256:
            raise TestEvaluationError(f"Training manifest does not reference the current locked dataset fingerprint: {checkpoint}")
        if run_manifest.get("dataset_split_fingerprints") != expected_split_fingerprints:
            raise TestEvaluationError(f"Training manifest split fingerprints differ from the locked dataset: {checkpoint}")
        data_yaml_path = Path(run_manifest.get("dataset_yaml", "")).expanduser()
        if not data_yaml_path.is_file():
            raise TestEvaluationError(f"Training YAML is missing: {data_yaml_path}")
        data_yaml_hash_now = sha256_file(data_yaml_path)
        data_yaml_hash_recorded = run_manifest.get("dataset_yaml_sha256")
        if data_yaml_hash_recorded:
            if data_yaml_hash_now != data_yaml_hash_recorded:
                raise TestEvaluationError(f"Training YAML differs from its recorded hash: {data_yaml_path}")
        elif not legacy_seed42_baseline:
            raise TestEvaluationError(f"Training YAML hash is missing from the run manifest: {data_yaml_path}")
        run_args_path = run_manifest_path.parent / "args.yaml"
        if not run_args_path.is_file():
            raise TestEvaluationError(f"Ultralytics training args are missing: {run_args_path}")
        if legacy_seed42_baseline:
            linked_yaml_hash = snapshot_provenance.get("training_yaml_sha256_at_link_time")
            linked_args_hash = snapshot_provenance.get("training_args_sha256_at_link_time")
            if linked_yaml_hash != data_yaml_hash_now or linked_args_hash != sha256_file(run_args_path):
                raise TestEvaluationError("Legacy seed-42 YAML/args differ from the verified post-run linkage.")
        run_args = yaml.safe_load(run_args_path.read_text(encoding="utf-8")) or {}
        for key, expected_value in run_manifest.get("training", {}).items():
            actual_value = run_args.get(key)
            if isinstance(expected_value, float) and isinstance(actual_value, (float, int)):
                matches = abs(float(actual_value) - expected_value) < 1e-12
            else:
                matches = actual_value == expected_value
            if not matches:
                raise TestEvaluationError(
                    f"Training args {key!r} differ from the provenance manifest for {checkpoint}: "
                    f"{actual_value!r} != {expected_value!r}"
                )
        if not run_args.get("val") or run_args.get("split") != "val" or run_args.get("pretrained") is not False:
            raise TestEvaluationError(f"Training args do not show VAL selection and random student initialization: {checkpoint}")
        if Path(run_args.get("data", "")).expanduser().resolve() != data_yaml_path.resolve():
            raise TestEvaluationError(f"Ultralytics args use a different training data YAML: {checkpoint}")
        architecture_path = Path(run_manifest.get("student_architecture", "")).expanduser().resolve()
        if (
            not architecture_path.is_file()
            or sha256_file(architecture_path) != run_manifest.get("student_architecture_sha256")
        ):
            raise TestEvaluationError(f"Student architecture differs from its training manifest: {architecture_path}")
        args_model_path = Path(run_args.get("model", "")).expanduser().resolve()
        if args_model_path != architecture_path:
            resumed_checkpoint = documented_resume_model_reference(run_args, run_manifest, run_manifest_path)
            if resumed_checkpoint != args_model_path:
                raise TestEvaluationError(f"Ultralytics args use a different student architecture: {checkpoint}")
            if not checkpoint_architecture_matches(
                (checkpoint, resumed_checkpoint), architecture_path, int(run_manifest.get("student_parameters", -1))
            ):
                raise TestEvaluationError(
                    f"Resumed training checkpoint architecture does not match its recorded YAML: {checkpoint}"
                )
        if Path(run_manifest.get("student_best_checkpoint", "")).resolve() != checkpoint:
            raise TestEvaluationError(f"Checkpoint does not match the best checkpoint in its manifest: {checkpoint}")
        parsed.append((label, checkpoint, run_manifest, run_manifest_path, None))
    return parsed


def validate_paired_students(
    students: list[tuple[str, Path, dict[str, Any], Path, Path | None]], seeds: tuple[int, ...]
) -> None:
    expected_labels = {f"kd_seed{seed}" for seed in seeds} | {
        f"supervised_seed{seed}" for seed in seeds
    }
    actual_labels = {label for label, _, _, _, _ in students}
    if actual_labels != expected_labels:
        raise TestEvaluationError(
            f"Locked TEST requires paired KD and supervised checkpoints for seeds {seeds}; "
            f"expected {sorted(expected_labels)}, got {sorted(actual_labels)}."
        )
    expected_architecture_hash = None
    expected_parameters = None
    expected_training = None
    expected_teacher_hash = None
    expected_distillation = None
    expected_versions = None
    for label, checkpoint, run_manifest, _, _ in students:
        if label.startswith("kd_seed"):
            seed = int(label.removeprefix("kd_seed"))
            is_kd = True
        else:
            seed = int(label.removeprefix("supervised_seed"))
            is_kd = False
        if run_manifest.get("seed") != seed or run_manifest.get("qat_used") is not False:
            raise TestEvaluationError(f"Run seed or QAT status does not match its label: {label}")
        expected_label_use = not is_kd
        if run_manifest.get("train_labels_used_for_loss") != expected_label_use:
            raise TestEvaluationError(f"Training objective/label-use declaration does not match {label}.")
        if is_kd and "teacher-only" not in str(run_manifest.get("objective", "")):
            raise TestEvaluationError(f"KD run is not declared teacher-only: {label}")
        if not is_kd and "supervised" not in str(run_manifest.get("objective", "")):
            raise TestEvaluationError(f"Control run is not declared supervised: {label}")
        if is_kd:
            teacher_hash = run_manifest.get("teacher_sha256")
            distillation = run_manifest.get("distillation")
            if not teacher_hash or not isinstance(distillation, dict):
                raise TestEvaluationError(f"Teacher checkpoint or KD loss provenance is missing for {label}.")
            if expected_teacher_hash is None:
                expected_teacher_hash = teacher_hash
                expected_distillation = distillation
            elif teacher_hash != expected_teacher_hash or distillation != expected_distillation:
                raise TestEvaluationError("KD seeds do not use the same frozen teacher and loss configuration.")
        architecture_hash = run_manifest.get("student_architecture_sha256")
        parameters = run_manifest.get("student_parameters")
        if not architecture_hash or not parameters:
            raise TestEvaluationError(f"Architecture provenance is missing for {label}.")
        if expected_architecture_hash is None:
            expected_architecture_hash = architecture_hash
            expected_parameters = parameters
        elif architecture_hash != expected_architecture_hash or parameters != expected_parameters:
            raise TestEvaluationError("KD and supervised checkpoints do not use the same student architecture.")
        training = dict(run_manifest.get("training", {}))
        training.pop("seed", None)
        if expected_training is None:
            expected_training = training
        elif training != expected_training:
            raise TestEvaluationError("KD and supervised runs differ in a shared training hyperparameter.")
        versions = run_manifest.get("versions", {})
        training_versions = {key: versions.get(key) for key in ("python", "torch", "ultralytics")}
        expected_training_versions = {key: EXPECTED_RUNTIME_VERSIONS[key] for key in training_versions}
        if training_versions != expected_training_versions:
            raise TestEvaluationError(f"Training runtime differs from the frozen environment for {label}.")
        if expected_versions is None:
            expected_versions = training_versions
        elif training_versions != expected_versions:
            raise TestEvaluationError("Paired student runs were trained with different software versions.")
        if Path(run_manifest.get("student_best_checkpoint", "")).resolve() != checkpoint:
            raise TestEvaluationError(f"Checkpoint differs from its declared validation-best artifact: {label}")


def parse_teacher(
    specification: str,
    training_manifest_path: Path,
    training_args_path: Path,
    test_evidence_path: Path,
) -> tuple[str, Path, dict[str, Any], Path, Path]:
    label, separator, checkpoint_value = specification.partition("=")
    if not separator or not label or not checkpoint_value or Path(label).name != label:
        raise TestEvaluationError(f"Teacher must be LABEL=CHECKPOINT: {specification!r}")
    checkpoint = Path(checkpoint_value).expanduser().resolve()
    training_manifest_path = training_manifest_path.expanduser().resolve()
    training_args_path = training_args_path.expanduser().resolve()
    test_evidence_path = test_evidence_path.expanduser().resolve()
    for path in (checkpoint, training_manifest_path, training_args_path, test_evidence_path):
        if not path.is_file():
            raise FileNotFoundError(f"Teacher provenance file does not exist: {path}")

    training_manifest = json.loads(training_manifest_path.read_text(encoding="utf-8"))
    if training_manifest.get("status") != "completed":
        raise TestEvaluationError("Teacher training manifest is not complete.")
    if training_manifest.get("class_mapping") != {str(k): v for k, v in EXPECTED_NAMES.items()}:
        raise TestEvaluationError("Teacher training manifest has an unexpected class mapping.")

    training_args = yaml.safe_load(training_args_path.read_text(encoding="utf-8")) or {}
    if not training_args.get("val") or training_args.get("split") != "val":
        raise TestEvaluationError("Teacher args do not show validation-based checkpoint selection.")
    expected_checkpoint = training_manifest_path.parent / "best.pt"
    if checkpoint != expected_checkpoint.resolve():
        raise TestEvaluationError(
            f"Teacher checkpoint does not match the completed training artifact: {expected_checkpoint}"
        )

    training_run_checkpoint = training_args_path.parent / "weights/best.pt"
    if not training_run_checkpoint.is_file() or sha256_file(training_run_checkpoint) != sha256_file(checkpoint):
        raise TestEvaluationError("Teacher checkpoint hash does not match the source run's validation-best artifact.")

    results_csv = training_args_path.parent / "results.csv"
    if not results_csv.is_file():
        raise TestEvaluationError(f"Teacher validation history is missing: {results_csv}")
    with results_csv.open("r", encoding="utf-8", newline="") as stream:
        validation_rows = list(csv.DictReader(stream))
    required_metrics = (
        "metrics/precision(B)",
        "metrics/recall(B)",
        "metrics/mAP50(B)",
        "metrics/mAP50-95(B)",
    )
    if not validation_rows or any(key not in validation_rows[0] for key in required_metrics):
        raise TestEvaluationError("Teacher results.csv has no required validation metrics.")
    best_validation_row = max(validation_rows, key=lambda row: float(row["metrics/mAP50-95(B)"]))
    teacher_validation_metrics = {
        key: float(best_validation_row[key]) for key in required_metrics
    }
    teacher_validation_metrics["fitness"] = teacher_validation_metrics["metrics/mAP50-95(B)"]

    checkpoint_sha256 = sha256_file(checkpoint)
    evidence = json.loads(test_evidence_path.read_text(encoding="utf-8"))
    if evidence.get("status") != "passed":
        raise TestEvaluationError("Historical teacher TEST evidence is not marked passed.")
    if Path(evidence.get("FP32 checkpoint path", "")).resolve() != checkpoint:
        raise TestEvaluationError("Historical TEST evidence names a different teacher checkpoint.")
    if evidence.get("FP32 SHA256") != checkpoint_sha256:
        raise TestEvaluationError("Teacher checkpoint hash differs from its historical TEST evidence.")
    statement = str(evidence.get("statement", "")).lower()
    required_claims = ("not used for training", "checkpoint selection", "hyperparameter tuning")
    if any(claim not in statement for claim in required_claims):
        raise TestEvaluationError("Historical TEST evidence does not establish TEST-only final evaluation.")

    run_manifest = {
        "objective": "frozen FP32 YOLO11n teacher trained with labeled data",
        "train_labels_used_for_loss": True,
        "metrics": teacher_validation_metrics,
        "training_provenance": {
            "dataset_project": training_manifest.get("dataset_project"),
            "dataset_workspace": training_manifest.get("dataset_workspace"),
            "dataset_version": training_manifest.get("dataset_version"),
            "source_checkpoint": training_manifest.get("checkpoint_source"),
            "training_args": str(training_args_path),
            "training_args_sha256": sha256_file(training_args_path),
        },
        "validation_selection_evidence": {
            "selection_metric": "mAP50-95(B)",
            "best_epoch": int(float(best_validation_row["epoch"])),
            "results_csv": str(results_csv),
            "results_csv_sha256": sha256_file(results_csv),
        },
    }
    return label, checkpoint, run_manifest, training_manifest_path, test_evidence_path


def resolve_splits(data_yaml: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    raw = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TestEvaluationError(f"Invalid dataset YAML: {data_yaml}")
    names_raw = raw.get("names")
    if isinstance(names_raw, list):
        names = dict(enumerate(str(name) for name in names_raw))
    elif isinstance(names_raw, dict):
        names = {int(index): str(name) for index, name in names_raw.items()}
    else:
        raise TestEvaluationError("Dataset YAML has no valid class names mapping.")
    if names != EXPECTED_NAMES:
        raise TestEvaluationError(f"Unexpected class names: {names!r}")
    splits = {}
    for split in ("train", "val", "test"):
        value = raw.get(split)
        if not isinstance(value, str) or not value:
            raise TestEvaluationError(f"Dataset YAML has no {split} path.")
        path = Path(value).expanduser()
        if not path.is_absolute():
            dataset_root = Path(raw.get("path") or data_yaml.parent).expanduser()
            if not dataset_root.is_absolute():
                dataset_root = (data_yaml.parent / dataset_root).resolve()
            path = dataset_root / path
        path = path.resolve()
        if not path.is_dir() or path.name != "images" or not (path.parent / "labels").is_dir():
            raise TestEvaluationError(f"Invalid {split} images/labels paths: {path}")
        splits[split] = path
    data = {
        "path": str(splits["test"].parent.parent),
        "train": str(splits["train"]),
        "val": str(splits["val"]),
        "test": str(splits["test"]),
        "names": names,
        "nc": len(names),
        "channels": 3,
    }
    return data, splits


def verify_test_fingerprint(test_dir: Path, fingerprint_path: Path) -> tuple[str, int, int]:
    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
    expected = fingerprint.get("splits", {}).get("test", {})
    image_records = expected.get("files", [])
    if not image_records:
        raise TestEvaluationError(f"Fingerprint contains no TEST file inventory: {fingerprint_path}")
    seen_images = set()
    seen_labels = set()
    annotations = 0
    for record in image_records:
        image = test_dir / record["image"]
        label = test_dir.parent / "labels" / record["label"]
        if not image.is_file() or sha256_file(image) != record["image_sha256"]:
            raise TestEvaluationError(f"TEST image differs from locked fingerprint: {image}")
        if not label.is_file() or sha256_file(label) != record["label_sha256"]:
            raise TestEvaluationError(f"TEST label differs from locked fingerprint: {label}")
        seen_images.add(record["image"])
        seen_labels.add(record["label"])
        annotations += sum(1 for line in label.read_text(encoding="utf-8").splitlines() if line.strip())

    current_images = {
        path.relative_to(test_dir).as_posix()
        for path in test_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    }
    current_labels = {
        path.relative_to(test_dir.parent / "labels").as_posix()
        for path in (test_dir.parent / "labels").rglob("*.txt")
        if path.is_file()
    }
    if current_images != seen_images or current_labels != seen_labels:
        raise TestEvaluationError("TEST file inventory differs from the locked fingerprint.")
    return expected["split_fingerprint_sha256"], len(seen_images), annotations


def evaluation_args(args: argparse.Namespace) -> Any:
    return get_cfg(
        DEFAULT_CFG,
        {
            "task": "detect",
            "mode": "val",
            "split": "test",
            "data": str(args.data.expanduser().resolve()),
            "imgsz": args.imgsz,
            "batch": args.batch,
            "workers": args.workers,
            "device": args.device,
            "cache": False,
            "fraction": 1.0,
            "rect": True,
            "augment": False,
            "amp": False,
            "plots": False,
            "save_json": False,
            "save_txt": False,
            # Explicitly pin the 0.001 confidence floor used by Ultralytics 8.4.130 validation.
            "conf": 0.001,
            "iou": 0.7,
            "verbose": True,
            "compile": False,
        },
    )


def build_test_dataset(
    model: torch.nn.Module, data: dict[str, Any], args: Any, cache_path: Path
) -> Dataset:
    stride = max(int(model.stride.max()), 32)
    return ReadOnlyTestDataset(
        img_path=data["test"],
        imgsz=args.imgsz,
        batch_size=args.batch,
        augment=False,
        hyp=copy.copy(args),
        rect=True,
        cache=False,
        single_cls=False,
        stride=stride,
        pad=0.5,
        prefix="test: ",
        task="detect",
        classes=None,
        data=data,
        fraction=1.0,
        external_cache_path=cache_path,
    )


def fixed_threshold_precision_recall(
    per_image_stats: list[dict[str, np.ndarray]],
) -> dict[str, dict[str, float | int]]:
    """Compute class P/R at the pre-locked confidence and IoU operating point."""
    tp = np.concatenate([item["tp"] for item in per_image_stats], axis=0)
    confidence = np.concatenate([item["conf"].reshape(-1) for item in per_image_stats])
    predicted_class = np.concatenate([item["pred_cls"].reshape(-1) for item in per_image_stats])
    target_class = np.concatenate([item["target_cls"].reshape(-1) for item in per_image_stats])
    if tp.ndim != 2 or tp.shape[0] != confidence.size or confidence.size != predicted_class.size:
        raise TestEvaluationError("Validator statistics have inconsistent detection dimensions.")
    if tp.shape[1] <= METRIC_MATCH_IOU_INDEX:
        raise TestEvaluationError("Validator statistics do not include the IoU=0.5 match column.")

    result: dict[str, dict[str, float | int]] = {}
    for class_id, class_name in EXPECTED_NAMES.items():
        target_count = int(np.count_nonzero(target_class == class_id))
        selected = (predicted_class == class_id) & (confidence > METRIC_OPERATING_CONFIDENCE)
        prediction_count = int(np.count_nonzero(selected))
        true_positive_count = int(np.count_nonzero(tp[selected, METRIC_MATCH_IOU_INDEX]))
        precision = true_positive_count / prediction_count if prediction_count else 0.0
        recall = true_positive_count / target_count if target_count else 0.0
        result[class_name] = {
            "precision": precision,
            "recall": recall,
            "target_count": target_count,
            "prediction_count": prediction_count,
            "true_positive_iou50_count": true_positive_count,
        }
    return result


def metric_report(
    validator: DetectionValidator, per_image_stats: list[dict[str, np.ndarray]]
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    mean = [float(value) for value in validator.metrics.mean_results()]
    _, _, map50, map5095 = mean
    operating_metrics = fixed_threshold_precision_recall(per_image_stats)
    precision = float(np.mean([operating_metrics[name]["precision"] for name in EXPECTED_NAMES.values()]))
    recall = float(np.mean([operating_metrics[name]["recall"] for name in EXPECTED_NAMES.values()]))
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    overall = {
        "precision": precision,
        "recall": recall,
        "F1": f1,
        "mAP50": map50,
        "mAP50-95": map5095,
    }
    per_class = {}
    for metric_index, class_id_raw in enumerate(validator.metrics.ap_class_index):
        class_id = int(class_id_raw)
        _, _, ap50, ap5095 = (float(value) for value in validator.metrics.class_result(metric_index))
        p = float(operating_metrics[EXPECTED_NAMES[class_id]]["precision"])
        r = float(operating_metrics[EXPECTED_NAMES[class_id]]["recall"])
        per_class[EXPECTED_NAMES[class_id]] = {
            "precision": p,
            "recall": r,
            "F1": 0.0 if p + r == 0 else 2 * p * r / (p + r),
            "mAP50": ap50,
            "mAP50-95": ap5095,
            "ground_truth_count": int(operating_metrics[EXPECTED_NAMES[class_id]]["target_count"]),
            "predictions_above_confidence": int(operating_metrics[EXPECTED_NAMES[class_id]]["prediction_count"]),
            "true_positives_at_iou50": int(operating_metrics[EXPECTED_NAMES[class_id]]["true_positive_iou50_count"]),
        }
    for name in EXPECTED_NAMES.values():
        per_class.setdefault(name, {metric: 0.0 for metric in overall})
    return overall, per_class


def bootstrap_test_metrics(per_image_stats: list[dict[str, np.ndarray]]) -> dict[str, Any]:
    """Estimate image-level percentile intervals from the validator's per-image detection stats."""
    image_count = len(per_image_stats)
    if image_count == 0:
        raise TestEvaluationError("Validator returned no per-image statistics for bootstrap intervals.")

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    overall_samples: dict[str, list[float]] = {
        metric: [] for metric in ("precision", "recall", "F1", "mAP50", "mAP50-95")
    }
    class_samples: dict[str, dict[str, list[float]]] = {
        name: {metric: [] for metric in overall_samples} for name in EXPECTED_NAMES.values()
    }

    for _ in range(BOOTSTRAP_REPLICATES):
        sampled_indices = rng.integers(0, image_count, size=image_count)
        sample_stats = [per_image_stats[int(index)] for index in sampled_indices]
        tp = np.concatenate([item["tp"] for item in sample_stats], axis=0)
        confidence = np.concatenate([item["conf"].reshape(-1) for item in sample_stats])
        predicted_class = np.concatenate([item["pred_cls"].reshape(-1) for item in sample_stats])
        target_class = np.concatenate([item["target_cls"].reshape(-1) for item in sample_stats])
        if target_class.size == 0:
            continue

        result = ap_per_class(tp, confidence, predicted_class, target_class)
        ap, class_ids = result[5], result[6]
        if len(class_ids) == 0:
            continue
        operating_metrics = fixed_threshold_precision_recall(sample_stats)
        # Keep the macro metric's class denominator fixed across bootstrap
        # replicates. If an image resample omits an entire class, overall
        # metrics for that replicate are undefined for the full class set.
        if {int(class_id) for class_id in class_ids} == set(EXPECTED_NAMES):
            overall_precision = float(
                np.mean([operating_metrics[name]["precision"] for name in EXPECTED_NAMES.values()])
            )
            overall_recall = float(
                np.mean([operating_metrics[name]["recall"] for name in EXPECTED_NAMES.values()])
            )
            overall_f1 = (
                0.0
                if overall_precision + overall_recall == 0
                else 2 * overall_precision * overall_recall / (overall_precision + overall_recall)
            )
            overall_values = {
                "precision": overall_precision,
                "recall": overall_recall,
                "F1": overall_f1,
                "mAP50": float(np.mean(ap[:, 0])),
                "mAP50-95": float(np.mean(ap)),
            }
            for metric, value in overall_values.items():
                overall_samples[metric].append(value)

        for row_index, class_id_raw in enumerate(class_ids):
            class_id = int(class_id_raw)
            class_name = EXPECTED_NAMES[class_id]
            class_precision = float(operating_metrics[class_name]["precision"])
            class_recall = float(operating_metrics[class_name]["recall"])
            class_samples[class_name]["precision"].append(class_precision)
            class_samples[class_name]["recall"].append(class_recall)
            class_samples[class_name]["F1"].append(
                0.0
                if class_precision + class_recall == 0
                else 2 * class_precision * class_recall / (class_precision + class_recall)
            )
            class_samples[class_name]["mAP50"].append(float(ap[row_index, 0]))
            class_samples[class_name]["mAP50-95"].append(float(np.mean(ap[row_index])))

    def interval(values: list[float]) -> dict[str, Any] | None:
        if not values:
            return None
        tail_percent = 50 * (1 - BOOTSTRAP_CONFIDENCE_LEVEL)
        lower, upper = np.percentile(values, [tail_percent, 100 - tail_percent])
        return {
            "lower": float(lower),
            "upper": float(upper),
            "valid_replicates": len(values),
        }

    return {
        "method": "nonparametric percentile bootstrap over TEST images, sampled with replacement",
        "confidence_level": BOOTSTRAP_CONFIDENCE_LEVEL,
        "replicates": BOOTSTRAP_REPLICATES,
        "random_seed": BOOTSTRAP_SEED,
        "sampling_unit": "image",
        "sample_size_per_replicate": image_count,
        "overall_metric_requires_all_classes": True,
        "operating_point": {
            "confidence_threshold": METRIC_OPERATING_CONFIDENCE,
            "true_positive_iou_threshold": METRIC_MATCH_IOU_THRESHOLD,
            "candidate_confidence_floor_for_ap": 0.001,
            "precision_recall_averaging": "macro over the three classes",
        },
        "overall": {metric: interval(values) for metric, values in overall_samples.items()},
        "per_class": {
            class_name: {metric: interval(values) for metric, values in metrics.items()}
            for class_name, metrics in class_samples.items()
        },
    }


def evaluate_one(
    label: str,
    checkpoint: Path,
    run_manifest: dict[str, Any],
    data: dict[str, Any],
    args: argparse.Namespace,
    output_dir: Path,
    training_manifest_path: Path,
    historical_test_evidence_path: Path | None = None,
) -> dict[str, Any]:
    model = YOLO(str(checkpoint), task="detect").model
    names = {int(index): str(name) for index, name in model.names.items()}
    if names != EXPECTED_NAMES:
        raise TestEvaluationError(f"Checkpoint {checkpoint} has unexpected classes: {names!r}")
    if args.device == "cpu":
        device = torch.device("cpu")
    else:
        first_device = args.device.split(",")[0].replace("cuda:", "")
        device = torch.device(f"cuda:{int(first_device) if first_device.isdigit() else 0}")
    model.to(device).float().eval()
    validator_args = evaluation_args(args)
    dataset = build_test_dataset(model, data, validator_args, output_dir / ".test_labels.cache")
    loader = build_dataloader(
        dataset,
        batch=args.batch,
        workers=args.workers,
        shuffle=False,
        rank=-1,
        drop_last=False,
        device=device,
    )
    validator = DetectionValidator(loader, save_dir=output_dir / label, args=copy.copy(validator_args))
    captured_stats: dict[str, list[dict[str, np.ndarray]]] = {}
    original_get_stats = validator.get_stats

    def capture_stats_before_clear() -> dict[str, float]:
        if "per_image" not in captured_stats:
            metric_stats = validator.metrics.stats
            keys = ("tp", "conf", "pred_cls", "target_cls")
            per_key_counts = {key: len(metric_stats.get(key, [])) for key in keys}
            if any(count != len(dataset) for count in per_key_counts.values()):
                raise TestEvaluationError(
                    f"Expected per-image TEST statistics for {len(dataset)} images; got {per_key_counts}."
                )
            captured_stats["per_image"] = [
                {
                    key: np.asarray(metric_stats[key][image_index]).copy()
                    for key in keys
                }
                for image_index in range(len(dataset))
            ]
        return original_get_stats()

    validator.get_stats = capture_stats_before_clear
    try:
        # Run inference-only validation. Passing a trainer context asks
        # Ultralytics to compute training loss on TEST labels and expects
        # training-only hyperparameters on checkpoint-loaded models.
        returned = validator(model=model)
    finally:
        if hasattr(loader, "close"):
            loader.close()
    overall, per_class = metric_report(validator, captured_stats["per_image"])
    bootstrap_ci = bootstrap_test_metrics(captured_stats["per_image"])
    result = {
        "model": label,
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": sha256_file(checkpoint),
        "checkpoint_size_bytes": checkpoint.stat().st_size,
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "training_manifest": str(training_manifest_path),
        "training_manifest_sha256": sha256_file(training_manifest_path),
        "training_objective": run_manifest.get("objective"),
        "training_artifact_provenance": {
            "run_config_path": run_manifest.get("run_config_path"),
            "run_config_sha256": run_manifest.get("run_config_sha256"),
            "training_script_path": run_manifest.get("training_script_path"),
            "training_script_source_path": run_manifest.get("training_script_source_path"),
            "training_script_sha256": run_manifest.get("training_script_sha256"),
            "training_script_snapshot_recorded_at_run_time": run_manifest.get(
                "training_script_snapshot_recorded_at_run_time"
            ),
            "distillation_implementation": run_manifest.get("distillation_implementation"),
            "dataset_yaml_sha256_recorded_at_run_time": run_manifest.get("dataset_yaml_sha256"),
            "dataset_yaml_sha256_verified_at_evaluation": (
                sha256_file(Path(run_manifest["dataset_yaml"]).expanduser())
                if run_manifest.get("dataset_yaml")
                and Path(run_manifest["dataset_yaml"]).expanduser().is_file()
                else None
            ),
            "legacy_seed42_baseline_missing_run_time_hashes": (
                label == "supervised_seed42"
                and not run_manifest.get("run_config_sha256")
                and run_manifest.get("dataset_snapshot_provenance", {}).get("linked_after_training") is True
            ),
        },
        "train_labels_used_for_loss": run_manifest.get("train_labels_used_for_loss"),
        "training_provenance": run_manifest.get("training_provenance"),
        "validation_metrics": run_manifest.get("metrics", {}),
        "validation_selection_evidence": run_manifest.get("validation_selection_evidence"),
        "metric_operating_point": {
            "confidence_threshold": METRIC_OPERATING_CONFIDENCE,
            "true_positive_iou_threshold": METRIC_MATCH_IOU_THRESHOLD,
            "candidate_confidence_floor_for_ap": 0.001,
            "precision_recall_averaging": "macro over the three classes",
            "selection": "fixed a priori from the Ultralytics default prediction confidence; not estimated on TEST",
        },
        "test_metrics": {"overall": overall, "per_class": per_class},
        "bootstrap_ci_95": bootstrap_ci,
        "test_image_count": len(dataset),
        "test_annotation_count": sum(int(len(item.get("cls", ()))) for item in dataset.labels),
        "ultralytics_ap_diagnostic": {
            str(key): float(value)
            for key, value in (returned or {}).items()
            if key in {"metrics/mAP50(B)", "metrics/mAP50-95(B)"}
        },
    }
    if historical_test_evidence_path is not None:
        result["historical_test_evidence"] = {
            "path": str(historical_test_evidence_path),
            "sha256": sha256_file(historical_test_evidence_path),
            "note": "Teacher TEST metrics were published before this student study; they were not used to select student checkpoints.",
        }
    return result


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    runtime_versions = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "torch": str(torch.__version__),
        "ultralytics": ultralytics.__version__,
    }
    if runtime_versions != EXPECTED_RUNTIME_VERSIONS:
        raise TestEvaluationError(f"Evaluation runtime differs from the frozen environment: {runtime_versions!r}")
    actual_test_settings = {key: getattr(args, key) for key in EXPECTED_TEST_SETTINGS}
    if actual_test_settings != EXPECTED_TEST_SETTINGS or args.imgsz != 640:
        raise TestEvaluationError(f"TEST evaluation settings differ from the locked protocol: {actual_test_settings!r}")
    output_dir = args.output.expanduser().resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to reuse a TEST evaluation directory: {output_dir}")
    data_yaml = args.data.expanduser().resolve()
    fingerprint_path = args.fingerprint.expanduser().resolve()
    if not data_yaml.is_file() or not fingerprint_path.is_file():
        raise FileNotFoundError(f"TEST dataset YAML or locked fingerprint missing: {data_yaml}, {fingerprint_path}")

    models = parse_models(args.models, fingerprint_path)
    for label, checkpoint, _, _, _ in models:
        try:
            validate_checkpoint(checkpoint, label=label, registry_path=args.model_registry.expanduser().resolve())
        except (FileNotFoundError, ValueError) as error:
            raise TestEvaluationError(f"Checkpoint registry check failed for {label}: {error}") from error
    student_seeds = tuple(sorted(set(args.seeds)))
    if student_seeds != EXPECTED_SEEDS:
        raise TestEvaluationError(f"The frozen protocol requires the seed set {EXPECTED_SEEDS}.")
    validate_paired_students(models, student_seeds)
    teacher = parse_teacher(
        args.teacher,
        args.teacher_training_manifest,
        args.teacher_training_args,
        args.teacher_test_evidence,
    )
    try:
        validate_checkpoint(teacher[1], label=teacher[0], registry_path=args.model_registry.expanduser().resolve())
    except (FileNotFoundError, ValueError) as error:
        raise TestEvaluationError(f"Teacher checkpoint registry check failed: {error}") from error
    teacher_checkpoint_hash = sha256_file(teacher[1])
    kd_teacher_hashes = {
        run_manifest.get("teacher_sha256")
        for label, _, run_manifest, _, _ in models
        if label.startswith("kd_seed")
    }
    if kd_teacher_hashes != {teacher_checkpoint_hash}:
        raise TestEvaluationError("KD runs do not use the same teacher checkpoint as the TEST comparison.")
    models.append(teacher)
    model_labels = [label for label, _, _, _, _ in models]
    if len(model_labels) != len(set(model_labels)):
        raise TestEvaluationError("Model labels must be unique, including the teacher label.")
    data, splits = resolve_splits(data_yaml)
    if args.device != "cpu" and not torch.cuda.is_available():
        raise TestEvaluationError("CUDA was requested but is unavailable in this process.")
    runtime = runtime_device_metadata(args.device)
    if runtime.get("device_name") != "NVIDIA L40":
        raise TestEvaluationError("Locked TEST evaluation must run on the recorded NVIDIA L40 device.")
    fingerprint, test_images, test_annotations = verify_test_fingerprint(splits["test"], fingerprint_path)
    retry_context = None
    if args.retry_of_manifest is not None:
        prior_manifest_path = args.retry_of_manifest.expanduser().resolve()
        if not prior_manifest_path.is_file():
            raise FileNotFoundError(f"Prior failed evaluation manifest is missing: {prior_manifest_path}")
        prior_manifest = json.loads(prior_manifest_path.read_text(encoding="utf-8"))
        if (
            prior_manifest.get("status") != "failed"
            or prior_manifest.get("models") != {}
            or prior_manifest.get("error") != "AttributeError: 'dict' object has no attribute 'box'"
            or prior_manifest.get("dataset_fingerprint_sha256") != sha256_file(fingerprint_path)
            or prior_manifest.get("test_split_fingerprint_sha256") != fingerprint
        ):
            raise TestEvaluationError(
                "Prior evaluation is not the documented no-metrics validator failure on the same frozen dataset."
            )
        retry_context = {
            "prior_attempt_manifest": str(prior_manifest_path),
            "prior_attempt_manifest_sha256": sha256_file(prior_manifest_path),
            "prior_attempt_status": prior_manifest["status"],
            "prior_attempt_error": prior_manifest["error"],
            "prior_attempt_models_with_metrics": [],
            "note": (
                "The prior harness attempt scanned the frozen TEST labels but failed on the first batch before "
                "recording any model metrics. This run uses inference-only validation and a new output directory."
            ),
        }
    output_dir.mkdir(parents=True, exist_ok=False)
    args.output = output_dir

    manifest = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "started",
        "purpose": "final evaluation only; do not use TEST to alter models, losses, thresholds, or hyperparameters",
        "retry_context": retry_context,
        "metric_operating_point": {
            "confidence_threshold": METRIC_OPERATING_CONFIDENCE,
            "true_positive_iou_threshold": METRIC_MATCH_IOU_THRESHOLD,
            "candidate_confidence_floor_for_ap": 0.001,
            "precision_recall_averaging": "macro over the three classes",
            "selection": "fixed a priori from the Ultralytics default prediction confidence; not estimated on TEST",
        },
        "evaluator_script": str(Path(__file__).resolve()),
        "evaluator_script_sha256": sha256_file(Path(__file__).resolve()),
        "data_yaml": str(data_yaml),
        "data_yaml_sha256": sha256_file(data_yaml),
        "dataset_fingerprint": str(fingerprint_path),
        "dataset_fingerprint_sha256": sha256_file(fingerprint_path),
        "test_split_fingerprint_sha256": fingerprint,
        "resolved_splits": {name: str(path) for name, path in splits.items()},
        "test_image_count": test_images,
        "test_annotation_count": test_annotations,
        "classes": EXPECTED_NAMES,
        "models_selected_by_val_or_previously_locked": [
            {
                "label": label,
                "checkpoint": str(checkpoint),
                "checkpoint_sha256": sha256_file(checkpoint),
                "training_manifest": str(training_manifest_path),
                "training_manifest_sha256": sha256_file(training_manifest_path),
                "historical_test_evidence": (
                    {
                        "path": str(evidence_path),
                        "sha256": sha256_file(evidence_path),
                    }
                    if evidence_path is not None
                    else None
                ),
            }
            for label, checkpoint, _, training_manifest_path, evidence_path in models
        ],
        "historical_teacher_test_use": {
            "description": "The frozen teacher was previously evaluated on TEST after selection; this evidence is recorded and was not used to select student checkpoints.",
            "evidence": str(args.teacher_test_evidence.expanduser().resolve()),
            "evidence_sha256": sha256_file(args.teacher_test_evidence.expanduser().resolve()),
        },
        "settings": {
            "split": "test",
            "imgsz": args.imgsz,
            "batch": args.batch,
            "workers": args.workers,
            "device": args.device,
            "cache": False,
            "augmentation": False,
            "precision": "FP32",
            "amp": False,
            "conf": 0.001,
            "confidence_threshold_policy": "candidate floor fixed at 0.001 for AP; point P/R/F1 fixed at 0.25 before TEST",
            "metric_operating_confidence_threshold": METRIC_OPERATING_CONFIDENCE,
            "metric_operating_iou_threshold": METRIC_MATCH_IOU_THRESHOLD,
            "iou": 0.7,
            "rect": True,
            "plots": False,
            "test_label_cache": "written only inside this output directory",
            "bootstrap": {
                "method": "nonparametric percentile bootstrap over TEST images, sampled with replacement",
                "confidence_level": BOOTSTRAP_CONFIDENCE_LEVEL,
                "replicates": BOOTSTRAP_REPLICATES,
                "random_seed": BOOTSTRAP_SEED,
                "sampling_unit": "image",
                "overall_metric_requires_all_classes": True,
                "operating_point": {
                    "confidence_threshold": METRIC_OPERATING_CONFIDENCE,
                    "true_positive_iou_threshold": METRIC_MATCH_IOU_THRESHOLD,
                    "candidate_confidence_floor_for_ap": 0.001,
                    "precision_recall_averaging": "macro over the three classes",
                },
            },
        },
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "ultralytics": ultralytics.__version__,
        },
        "runtime": runtime,
        "models": {},
    }
    manifest_path = output_dir / "manifest.json"
    write_json(manifest_path, manifest)
    try:
        for label, checkpoint, run_manifest, training_manifest_path, evidence_path in models:
            print(f"Evaluating locked TEST model {label}: {checkpoint}", flush=True)
            manifest["models"][label] = evaluate_one(
                label,
                checkpoint,
                run_manifest,
                data,
                args,
                output_dir,
                training_manifest_path,
                evidence_path,
            )
            write_json(output_dir / f"{label}_metrics.json", manifest["models"][label])
            write_json(manifest_path, manifest)
        manifest["status"] = "complete"
        manifest["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(manifest_path, manifest)
    except Exception as error:
        manifest["status"] = "failed"
        manifest["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["error"] = f"{type(error).__name__}: {error}"
        write_json(manifest_path, manifest)
        raise

    print(f"Locked TEST evaluation complete: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
