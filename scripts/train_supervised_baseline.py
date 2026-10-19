"""Train a label-supervised control student separately from the pure-KD run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import ultralytics
import yaml
from ultralytics import YOLO

try:
    from .experiment_paths import resolve_training_data, write_resolved_data_yaml
    from .training_runtime import verify_training_runtime
except ImportError:
    from experiment_paths import resolve_training_data, write_resolved_data_yaml
    from training_runtime import verify_training_runtime


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NAMES = {0: "ball", 1: "gawang", 2: "robot"}


class BaselineRunError(RuntimeError):
    """Raised when the supervised control run cannot be started safely."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/supervised_baseline.yaml",
        help="Path to the supervised-baseline YAML.",
    )
    parser.add_argument("--seed", type=int, help="Override the configured seed; each seed gets a separate run.")
    parser.add_argument("--run-name", help="Optional unique run directory name, useful when preserving failed attempts.")
    parser.add_argument("--data-root", type=Path, help="Verified dataset root; overrides KD_DATA_ROOT.")
    return parser.parse_args()


def resolve_path(value: str | Path, *, relative_to: Path) -> Path:
    path = Path(value).expanduser()
    return (relative_to / path).resolve() if not path.is_absolute() else path.resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def runtime_device_metadata(device: Any) -> dict[str, Any]:
    requested = str(device)
    cuda_available = torch.cuda.is_available()
    metadata: dict[str, Any] = {
        "requested_device": requested,
        "cuda_available": cuda_available,
        "cuda_runtime_version": torch.version.cuda,
        "cudnn_version": torch.backends.cudnn.version(),
        "platform": platform.platform(),
        "visible_cuda_device_count": torch.cuda.device_count() if cuda_available else 0,
    }
    if not cuda_available or requested.lower() == "cpu":
        metadata["device_type"] = "cpu"
        return metadata

    try:
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
    except Exception as error:
        # Device metadata should not prevent a training run from starting.
        metadata["device_type"] = "cuda"
        metadata["device_metadata_error"] = f"{type(error).__name__}: {error}"
    return metadata


def dataset_fingerprint_metadata() -> dict[str, Any]:
    fingerprint_path = ROOT / "artifacts/advance_vision_dataset_fingerprint.json"
    if not fingerprint_path.is_file():
        raise BaselineRunError(f"Locked dataset fingerprint is missing: {fingerprint_path}")
    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
    splits = fingerprint.get("splits", {})
    if not all(name in splits for name in ("train", "val", "test")):
        raise BaselineRunError(f"Dataset fingerprint is incomplete: {fingerprint_path}")
    return {
        "dataset_fingerprint": str(fingerprint_path),
        "dataset_fingerprint_sha256": sha256_file(fingerprint_path),
        "dataset_split_fingerprints": {
            name: splits[name]["split_fingerprint_sha256"] for name in ("train", "val", "test")
        },
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def metric_values(results: Any) -> dict[str, float]:
    values = getattr(results, "results_dict", results)
    if not isinstance(values, dict):
        return {}
    return {str(key): float(value) for key, value in values.items()}


def model_parameter_count(model_path: Path) -> int:
    model = YOLO(str(model_path), task="detect").model
    return sum(parameter.numel() for parameter in model.parameters())


def load_run_config(
    config_path: Path, seed_override: int | None, run_name_override: str | None,
    data_root_override: Path | None = None,
) -> tuple[dict[str, Any], Path, Path, Path, dict[str, Any], dict[str, Any], Path, int]:
    config_path = config_path.resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise BaselineRunError(f"Config must contain a YAML mapping: {config_path}")

    student = resolve_path(config["student_model"], relative_to=ROOT)
    source_data_yaml = resolve_path(config["data_yaml"], relative_to=ROOT)
    if not student.is_file() or not source_data_yaml.is_file():
        raise BaselineRunError(f"Student model or data YAML is missing: {student}, {source_data_yaml}")

    training = config["training"]
    seed = int(training["seed"] if seed_override is None else seed_override)
    run_name = run_name_override or str(config["run"]["name"]).format(seed=seed)
    if Path(run_name).name != run_name or run_name in {".", ".."}:
        raise BaselineRunError(f"Run name must be a single directory name: {run_name!r}")
    project = resolve_path(config["run"]["project"], relative_to=ROOT)
    run_dir = project / run_name
    if run_dir.exists():
        raise BaselineRunError(f"Refusing to overwrite an existing run directory: {run_dir}")
    data_root = data_root_override or os.environ.get("KD_DATA_ROOT")
    data_yaml, data, data_metadata = resolve_training_data(
        source_data_yaml,
        run_dir,
        ROOT / "artifacts/advance_vision_dataset_fingerprint.json",
        root_override=data_root,
    )
    return config, student, source_data_yaml, data_yaml, data, data_metadata, run_dir, seed


def main() -> int:
    args = parse_args()
    manifest_path: Path | None = None
    manifest: dict[str, Any] = {}
    try:
        runtime_compatibility = verify_training_runtime()
        (
            config, student, source_data_yaml, data_yaml, data_config,
            data_metadata, run_dir, seed,
        ) = load_run_config(args.config, args.seed, args.run_name, args.data_root)
        training = config["training"]
        manifest_path = run_dir.parent / f".{run_dir.name}.manifest.json"
        if manifest_path.exists():
            raise BaselineRunError(f"A pending manifest already exists; inspect it before rerunning: {manifest_path}")
        if data_yaml != source_data_yaml:
            run_dir.mkdir(parents=False, exist_ok=False)
            write_resolved_data_yaml(data_yaml, data_config)

        parameters = model_parameter_count(student)
        manifest = {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "started",
            "objective": "student-only supervised detection baseline; separate from pure KD",
            "run_config_path": str(args.config.expanduser().resolve()),
            "run_config_sha256": sha256_file(args.config.expanduser().resolve()),
            "training_script_path": str(Path(__file__).resolve()),
            "training_script_sha256": sha256_file(Path(__file__).resolve()),
            "student_architecture": str(student),
            "student_architecture_sha256": sha256_file(student),
            "student_initialization": "random initialization; pretrained=False",
            "student_parameters": parameters,
            "dataset_yaml": str(data_yaml),
            "dataset_yaml_sha256": sha256_file(data_yaml),
            "resolved_inputs": {
                "source_dataset_yaml": str(source_data_yaml),
                "source_dataset_yaml_sha256": sha256_file(source_data_yaml),
                "resolved_dataset_yaml": str(data_yaml),
                **data_metadata,
            },
            "training_runtime_compatibility": runtime_compatibility,
            **dataset_fingerprint_metadata(),
            "train_labels_used_for_loss": True,
            "validation_split": "VAL only; labels used only for metrics and checkpoint selection",
            "test_split_used": False,
            "qat_used": False,
            "seed": seed,
            "training": {**training, "seed": seed},
            "versions": {
                "python": platform.python_version(),
                "torch": torch.__version__,
                "ultralytics": ultralytics.__version__,
            },
            "runtime": runtime_device_metadata(training["device"]),
            "output_dir": str(run_dir),
        }
        write_json(manifest_path, manifest)

        model = YOLO(str(student), task="detect")
        results = model.train(
            model=str(student),
            data=str(data_yaml),
            epochs=int(training["epochs"]),
            batch=int(training["batch"]),
            workers=int(training["workers"]),
            imgsz=int(training["imgsz"]),
            device=training["device"],
            seed=seed,
            optimizer=str(training["optimizer"]),
            lr0=float(training["lr0"]),
            lrf=float(training["lrf"]),
            warmup_epochs=float(training["warmup_epochs"]),
            weight_decay=float(training["weight_decay"]),
            close_mosaic=int(training["close_mosaic"]),
            amp=bool(training["amp"]),
            patience=int(training["patience"]),
            pretrained=False,
            val=True,
            plots=False,
            save=True,
            project=str(run_dir.parent),
            name=run_dir.name,
            exist_ok=(data_yaml != source_data_yaml),
            compile=False,
        )

        best_checkpoint = run_dir / "weights/best.pt"
        if not best_checkpoint.is_file():
            raise BaselineRunError(f"Training finished without a best student checkpoint: {best_checkpoint}")
        manifest.update(
            {
                "status": "complete",
                "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                "student_best_checkpoint": str(best_checkpoint),
                "student_best_sha256": sha256_file(best_checkpoint),
                "metrics": metric_values(results),
            }
        )
        write_json(manifest_path, manifest)
        final_manifest = run_dir / "manifest.json"
        manifest_path.replace(final_manifest)
        print(f"Best supervised student: {best_checkpoint}")
        print(f"Manifest: {final_manifest}")
        return 0
    except KeyboardInterrupt:
        error = BaselineRunError("Training interrupted before completion.")
        if manifest_path is not None:
            manifest.update(
                {
                    "status": "interrupted",
                    "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                    "error": str(error),
                }
            )
            write_json(manifest_path, manifest)
        print(f"Supervised baseline interrupted: {error}", file=sys.stderr)
        return 130
    except Exception as error:
        traceback.print_exc()
        if manifest_path is not None:
            manifest.update(
                {
                    "status": "failed",
                    "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                    "error": f"{type(error).__name__}: {error}",
                }
            )
            write_json(manifest_path, manifest)
        print(f"Supervised baseline failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
