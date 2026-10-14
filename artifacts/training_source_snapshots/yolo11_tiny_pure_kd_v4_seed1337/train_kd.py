"""Train a smaller FP32 YOLO student using teacher-only distillation targets."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
import ultralytics
import yaml
from ultralytics import YOLO
from ultralytics.nn.distill_model import DistillationModel


ROOT = Path(__file__).resolve().parents[1]


class KDRunError(RuntimeError):
    """Raised when the configured pure-KD run cannot be started safely."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/kd.yaml",
        help="Path to the experiment YAML.",
    )
    parser.add_argument("--seed", type=int, help="Override the configured seed; creates a separate run directory.")
    parser.add_argument("--run-name", help="Optional unique run directory name for a final rerun of a pilot seed.")
    return parser.parse_args()


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
        raise KDRunError(f"Locked dataset fingerprint is missing: {fingerprint_path}")
    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
    splits = fingerprint.get("splits", {})
    if not all(name in splits for name in ("train", "val", "test")):
        raise KDRunError(f"Dataset fingerprint is incomplete: {fingerprint_path}")
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


def resolve_path(value: str | Path, *, relative_to: Path) -> Path:
    path = Path(value).expanduser()
    return (relative_to / path).resolve() if not path.is_absolute() else path.resolve()


def install_teacher_only_kd_loss(distillation: dict[str, Any]) -> None:
    """Replace Ultralytics' supervised+KD objective with teacher-only targets.

    Ultralytics' DistillationModel is used for teacher/student feature hooks,
    channel projectors, and score-weighted feature loss. Raw box and class
    outputs are distilled too, so the student detection head receives targets.
    The stock labeled detection loss is omitted. Validation labels are used
    only for detection metrics.
    """

    feature_weight = float(distillation["feature_weight"])
    box_weight = float(distillation["box_weight"])
    class_weight = float(distillation["class_weight"])
    temperature = float(distillation["temperature"])

    def head_branches(head: Any) -> list[dict[str, torch.Tensor]]:
        if isinstance(head, dict) and "one2many" in head:
            branches = [head["one2many"]]
            if isinstance(head.get("one2one"), dict):
                branches.append(head["one2one"])
            return branches
        return [head] if isinstance(head, dict) and {"boxes", "scores"}.issubset(head) else []

    def teacher_only_loss(self, batch, preds=None):
        # Ultralytics updates the detection criterion's internal epoch state
        # after validation. Initialize it for trainer compatibility, but never
        # evaluate it or include its labels-based loss in the KD objective.
        if getattr(self.student_model, "criterion", None) is None:
            self.student_model.criterion = self.student_model.init_criterion()

        if not self.training:
            # The validator computes detection metrics from predictions and
            # labels separately. Return zero auxiliary loss here so val labels
            # never enter either the train or validation loss calculation.
            zero = torch.zeros((), device=batch["img"].device)
            return zero, {"feature_kd": zero, "box_kd": zero, "class_kd": zero}

        self._teacher_feats.clear()
        self._student_feats.clear()
        with torch.no_grad():
            self.teacher_model(batch["img"])
        self.student_model(batch["img"])

        teacher_head = self._teacher_feats[self.feats_idx[-1]]
        student_head = self._student_feats[self.feats_idx[-1]]
        teacher_scores = (
            self.decouple_outputs(teacher_head, branch="one2many")["scores"]
            + self.decouple_outputs(teacher_head, branch="one2one")["scores"]
        ) / 2
        neck_features = [self._teacher_feats[index] for index in self.feats_idx[:-1]]
        score_parts = torch.split(
            teacher_scores,
            [feature.shape[-2] * feature.shape[-1] for feature in neck_features],
            dim=-1,
        )
        teacher_scores = tuple(part.sigmoid().max(dim=1, keepdim=True).values for part in score_parts)

        feature_loss = torch.zeros((), device=batch["img"].device)
        for level, feature_index in enumerate(self.feats_idx[:-1]):
            teacher_feature = self.decouple_outputs(self._teacher_feats[feature_index])
            student_feature = self.projector[level](
                self.decouple_outputs(self._student_feats[feature_index])
            )
            feature_loss = feature_loss + self.loss_sl2(
                    student_feature,
                    teacher_feature,
                    feat_idx=level,
                    teacher_scores=teacher_scores,
                )

        teacher_branches = head_branches(self.decouple_outputs(teacher_head))
        student_branches = head_branches(self.decouple_outputs(student_head))
        if not teacher_branches or len(teacher_branches) != len(student_branches):
            raise KDRunError("Teacher and student Detect head output branches do not match.")

        box_losses = []
        class_losses = []
        for teacher_branch, student_branch in zip(teacher_branches, student_branches):
            teacher_boxes = teacher_branch["boxes"].detach().float()
            student_boxes = student_branch["boxes"].float()
            teacher_logits = teacher_branch["scores"].detach().float()
            student_logits = student_branch["scores"].float()
            if teacher_boxes.shape != student_boxes.shape or teacher_logits.shape != student_logits.shape:
                raise KDRunError(
                    "Teacher/student Detect output shapes differ: "
                    f"boxes={tuple(teacher_boxes.shape)}/{tuple(student_boxes.shape)}, "
                    f"scores={tuple(teacher_logits.shape)}/{tuple(student_logits.shape)}"
                )
            box_losses.append(F.smooth_l1_loss(student_boxes, teacher_boxes))
            soft_targets = torch.sigmoid(teacher_logits / temperature)
            class_losses.append(
                F.binary_cross_entropy_with_logits(student_logits / temperature, soft_targets)
                * (temperature**2)
            )

        box_loss = torch.stack(box_losses).mean()
        class_loss = torch.stack(class_losses).mean()
        distillation_loss = feature_weight * feature_loss + box_weight * box_loss + class_weight * class_loss

        # Ultralytics' trainer sums the returned tensor and expects the loss to
        # be scaled by batch size, matching its own distillation implementation.
        scaled_loss = distillation_loss * batch["img"].shape[0]
        return scaled_loss, {
            "feature_kd": feature_loss.detach(),
            "box_kd": box_loss.detach(),
            "class_kd": class_loss.detach(),
        }

    DistillationModel.loss = teacher_only_loss


def validate_config(
    config_path: Path,
    seed_override: int | None = None,
    run_name_override: str | None = None,
) -> tuple[dict[str, Any], Path, Path, Path, Path]:
    config_path = config_path.resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise KDRunError(f"Config must contain a YAML mapping: {config_path}")

    teacher = resolve_path(config["teacher_checkpoint"], relative_to=ROOT)
    student = resolve_path(config["student_model"], relative_to=ROOT)
    data_yaml = resolve_path(config["data_yaml"], relative_to=ROOT)
    data = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    if "test" in data:
        raise KDRunError("KD training data config must not expose a TEST split.")
    for split in ("train", "val"):
        if split not in data or not Path(data[split]).is_dir():
            raise KDRunError(f"Missing {split} image directory in {data_yaml}: {data.get(split)!r}")
    if not teacher.is_file():
        raise KDRunError(f"Teacher checkpoint not found: {teacher}")
    if not student.is_file():
        raise KDRunError(f"Student architecture YAML not found: {student}")
    names = data.get("names")
    if names != {0: "ball", 1: "gawang", 2: "robot"}:
        raise KDRunError(f"Unexpected class map in data config: {names!r}")

    run = config["run"]
    output_root = resolve_path(run["project"], relative_to=ROOT)
    configured_seed = int(config["training"]["seed"])
    seed = configured_seed if seed_override is None else int(seed_override)
    config["training"]["seed"] = seed
    run_name = run_name_override or str(run["name"])
    if run_name_override is None and seed != configured_seed:
        run_name = f"{run_name}_seed{seed}"
    if Path(run_name).name != run_name or run_name in {".", ".."}:
        raise KDRunError(f"Run name must be a single directory name: {run_name!r}")
    run_dir = output_root / run_name
    if run_dir.exists():
        raise KDRunError(f"Refusing to overwrite an existing run directory: {run_dir}")
    return config, teacher, student, data_yaml, run_dir


def main() -> int:
    args = parse_args()
    manifest_path: Path | None = None
    manifest: dict[str, Any] = {}
    try:
        config, teacher, student, data_yaml, run_dir = validate_config(args.config, args.seed, args.run_name)
        training = config["training"]
        distillation = config["distillation"]
        manifest_path = run_dir.parent / f".{run_dir.name}.manifest.json"
        if manifest_path.exists():
            raise KDRunError(f"A pending manifest already exists; inspect it before rerunning: {manifest_path}")
        source_snapshot_dir = ROOT / "artifacts/training_source_snapshots" / run_dir.name
        implementation_source_value = inspect.getsourcefile(DistillationModel)
        if not implementation_source_value:
            raise KDRunError("Could not resolve the imported DistillationModel source file.")
        implementation_source = Path(implementation_source_value).resolve()
        if not implementation_source.is_file():
            raise KDRunError(f"DistillationModel source file is missing: {implementation_source}")
        script_source = Path(__file__).resolve()
        training_script_snapshot = source_snapshot_dir / "train_kd.py"
        implementation_snapshot = source_snapshot_dir / "distill_model.py"
        if source_snapshot_dir.exists():
            if (
                not training_script_snapshot.is_file()
                or not implementation_snapshot.is_file()
                or sha256_file(training_script_snapshot) != sha256_file(script_source)
                or sha256_file(implementation_snapshot) != sha256_file(implementation_source)
            ):
                raise KDRunError(
                    f"Existing training source snapshot differs from this attempt; use a new run name: {source_snapshot_dir}"
                )
        else:
            source_snapshot_dir.mkdir(parents=True, exist_ok=False)
            training_script_snapshot.write_bytes(script_source.read_bytes())
            implementation_snapshot.write_bytes(implementation_source.read_bytes())
        if sha256_file(training_script_snapshot) != sha256_file(script_source):
            raise KDRunError("Training script source snapshot does not match the running script.")
        if sha256_file(implementation_snapshot) != sha256_file(implementation_source):
            raise KDRunError("DistillationModel source snapshot does not match the imported implementation file.")
        teacher_parameters = model_parameter_count(teacher)
        student_parameters = model_parameter_count(student)
        if student_parameters >= teacher_parameters:
            raise KDRunError(
                "The configured student is not smaller than the teacher: "
                f"student={student_parameters:,}, teacher={teacher_parameters:,} parameters."
            )
        manifest = {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "started",
            "objective": "pure FP32 teacher-only distillation; no supervised training loss and no QAT",
            "run_config_path": str(args.config.expanduser().resolve()),
            "run_config_sha256": sha256_file(args.config.expanduser().resolve()),
            "training_script_path": str(training_script_snapshot),
            "training_script_source_path": str(script_source),
            "training_script_sha256": sha256_file(training_script_snapshot),
            "training_script_snapshot_recorded_at_run_time": True,
            "distillation_implementation": {
                "module": DistillationModel.__module__,
                "path": str(implementation_snapshot),
                "source_path": str(implementation_source),
                "sha256": sha256_file(implementation_snapshot),
                "snapshot_recorded_at_run_time": True,
            },
            "teacher_checkpoint": str(teacher),
            "teacher_sha256": sha256_file(teacher),
            "student_architecture": str(student),
            "student_architecture_sha256": sha256_file(student),
            "student_initialization": "random initialization from custom narrow YOLO11 YAML",
            "teacher_parameters": teacher_parameters,
            "student_parameters": student_parameters,
            "parameter_reduction_percent": round(
                100.0 * (teacher_parameters - student_parameters) / teacher_parameters, 3
            ),
            "dataset_yaml": str(data_yaml),
            "dataset_yaml_sha256": sha256_file(data_yaml),
            **dataset_fingerprint_metadata(),
            "seed": int(training["seed"]),
            "train_labels_used_for_loss": False,
            "validation_split": "VAL only; labels used only for metrics and diagnostics",
            "test_split_used": False,
            "qat_used": False,
            "distillation": {
                "type": "feature, box-output, and class-output distillation; no ground-truth loss",
                "layers": "YOLO Detect neck inputs (P3/P4/P5) and raw Detect outputs",
                "feature_weight": float(distillation["feature_weight"]),
                "box_weight": float(distillation["box_weight"]),
                "class_weight": float(distillation["class_weight"]),
                "class_temperature": float(distillation["temperature"]),
            },
            "training": training,
            "versions": {
                "python": platform.python_version(),
                "torch": torch.__version__,
                "ultralytics": ultralytics.__version__,
            },
            "runtime": runtime_device_metadata(training["device"]),
            "output_dir": str(run_dir),
        }
        write_json(manifest_path, manifest)

        install_teacher_only_kd_loss(distillation)
        model = YOLO(str(student), task="detect")
        results = model.train(
            model=str(student),
            data=str(data_yaml),
            distill_model=str(teacher),
            dis=float(distillation["feature_weight"]),
            epochs=int(training["epochs"]),
            batch=int(training["batch"]),
            workers=int(training["workers"]),
            imgsz=int(training["imgsz"]),
            device=training["device"],
            seed=int(training["seed"]),
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
            exist_ok=False,
            compile=False,
        )

        best_checkpoint = run_dir / "weights/best.pt"
        if not best_checkpoint.is_file():
            raise KDRunError(f"Training finished without a best student checkpoint: {best_checkpoint}")
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
        print(f"Best distilled student: {best_checkpoint}")
        print(f"Manifest: {final_manifest}")
        return 0
    except KeyboardInterrupt:
        error = KDRunError("Training interrupted before completion.")
        if manifest_path is not None:
            manifest.update(
                {
                    "status": "interrupted",
                    "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                    "error": str(error),
                }
            )
            write_json(manifest_path, manifest)
        print(f"Pure KD run interrupted: {error}", file=sys.stderr)
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
        print(f"Pure KD run failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
