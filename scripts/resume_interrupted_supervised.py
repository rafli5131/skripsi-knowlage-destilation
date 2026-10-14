"""Resume one interrupted supervised student run from its latest Ultralytics checkpoint.

This recovery entry point preserves the original training manifest and recipe.
It is deliberately limited to an existing run with a matching pending manifest,
dataset fingerprint, source hashes, and resumable last.pt checkpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import ultralytics
import yaml
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/supervised_baseline.yaml"
QUEUE_STATE = ROOT / "artifacts/student_training_queue.json"
PIPELINE_STATE = ROOT / "artifacts/final_evaluation_pipeline.json"
FINGERPRINT = ROOT / "artifacts/advance_vision_dataset_fingerprint.json"
EXPECTED_NAMES = {0: "ball", 1: "gawang", 2: "robot"}


class ResumeError(RuntimeError):
    """Raised when an interrupted run cannot be resumed without ambiguity."""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def metric_values(results: Any) -> dict[str, float]:
    values = getattr(results, "results_dict", results)
    return {str(key): float(value) for key, value in values.items()} if isinstance(values, dict) else {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--run-name", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path: Path | None = None
    manifest: dict[str, Any] = {}
    try:
        config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
        training = {**config["training"], "seed": args.seed}
        project = (ROOT / config["run"]["project"]).resolve()
        run_dir = project / args.run_name
        manifest_path = project / f".{args.run_name}.manifest.json"
        final_manifest = run_dir / "manifest.json"
        checkpoint = run_dir / "weights/last.pt"
        results_csv = run_dir / "results.csv"

        if not run_dir.is_dir() or not checkpoint.is_file() or not results_csv.is_file():
            raise ResumeError(f"Partial run is missing its directory, last.pt, or results.csv: {run_dir}")
        if final_manifest.exists():
            raise ResumeError(f"Run already has a final manifest: {final_manifest}")
        if not manifest_path.is_file():
            raise ResumeError(f"Pending run manifest is missing: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") not in {"started", "interrupted", "failed"}:
            raise ResumeError(f"Pending manifest has unexpected status: {manifest.get('status')}")
        if manifest.get("seed") != args.seed or manifest.get("output_dir") != str(run_dir):
            raise ResumeError("Pending manifest does not match the requested seed and run directory.")
        if manifest.get("training") != training:
            raise ResumeError("Pending manifest training recipe differs from the current frozen config.")
        if manifest.get("test_split_used") is not False or manifest.get("train_labels_used_for_loss") is not True:
            raise ResumeError("Pending manifest does not describe the expected supervised, TRAIN/VAL-only run.")
        if "supervised" not in str(manifest.get("objective", "")):
            raise ResumeError("Pending manifest is not a supervised control run.")

        student = (ROOT / config["student_model"]).resolve()
        data_yaml = (ROOT / config["data_yaml"]).resolve()
        data = yaml.safe_load(data_yaml.read_text(encoding="utf-8")) or {}
        if "test" in data or data.get("names") != EXPECTED_NAMES:
            raise ResumeError("Training data YAML exposes TEST or has an unexpected class mapping.")
        for split in ("train", "val"):
            if split not in data or not Path(data[split]).is_dir():
                raise ResumeError(f"Missing {split} image directory in training YAML: {data.get(split)!r}")

        expected_hashes = {
            "run_config_sha256": sha256_file(CONFIG),
            "training_script_sha256": sha256_file(ROOT / "scripts/train_supervised_baseline.py"),
            "student_architecture_sha256": sha256_file(student),
            "dataset_yaml_sha256": sha256_file(data_yaml),
            "dataset_fingerprint_sha256": sha256_file(FINGERPRINT),
        }
        mismatched = {
            key: (manifest.get(key), value)
            for key, value in expected_hashes.items()
            if manifest.get(key) != value
        }
        if mismatched:
            raise ResumeError(f"Run provenance no longer matches its original manifest: {mismatched}")
        if manifest.get("dataset_split_fingerprints") != {
            split: entry["split_fingerprint_sha256"]
            for split, entry in json.loads(FINGERPRINT.read_text(encoding="utf-8"))["splits"].items()
        }:
            raise ResumeError("Dataset split fingerprints differ from the interrupted run manifest.")

        checkpoint_data = torch.load(checkpoint, map_location="cpu", weights_only=False)
        if checkpoint_data.get("epoch", -1) < 0 or checkpoint_data.get("optimizer") is None:
            raise ResumeError("last.pt does not contain a resumable epoch and optimizer state.")
        saved_args = checkpoint_data.get("train_args", {})
        expected_args = {
            "epochs": training["epochs"],
            "batch": training["batch"],
            "workers": training["workers"],
            "imgsz": training["imgsz"],
            "device": training["device"],
            "seed": training["seed"],
            "optimizer": training["optimizer"],
            "lr0": training["lr0"],
            "lrf": training["lrf"],
            "warmup_epochs": training["warmup_epochs"],
            "weight_decay": training["weight_decay"],
            "close_mosaic": training["close_mosaic"],
            "amp": training["amp"],
            "patience": training["patience"],
            "pretrained": False,
            "val": True,
        }
        if any(saved_args.get(key) != value for key, value in expected_args.items()):
            raise ResumeError("Checkpoint training arguments differ from the frozen supervised recipe.")
        if Path(saved_args.get("data", "")).resolve() != data_yaml:
            raise ResumeError("Checkpoint data YAML path does not match the locked TRAIN/VAL YAML.")
        if Path(saved_args.get("save_dir", "")).resolve() != run_dir:
            raise ResumeError("Checkpoint output directory does not match the existing run directory.")

        rows = results_csv.read_text(encoding="utf-8").splitlines()
        if len(rows) < 2:
            raise ResumeError("results.csv has no completed validation rows.")
        last_result_epoch = int(rows[-1].split(",", maxsplit=1)[0])
        checkpoint_epoch = int(checkpoint_data["epoch"])
        if last_result_epoch != checkpoint_epoch + 1:
            raise ResumeError(
                "Checkpoint and validation CSV are not synchronized: "
                f"CSV epoch={last_result_epoch}, checkpoint epoch={checkpoint_epoch}."
            )

        queue = json.loads(QUEUE_STATE.read_text(encoding="utf-8"))
        item = next(
            (entry for entry in queue.get("items", []) if entry.get("label") == f"supervised_seed{args.seed}"),
            None,
        )
        if queue.get("status") not in {"running", "interrupted", "failed"} or item is None:
            raise ResumeError("Training queue does not contain this run in an active or recoverable state.")
        if item.get("status") not in {"running", "interrupted", "failed"}:
            raise ResumeError(f"Queue item is not recoverable: {item.get('status')}")
        if item.get("run_dir") != str(run_dir.relative_to(ROOT)):
            raise ResumeError("Queue item run directory does not match the requested recovery target.")

        previous_status = manifest["status"]
        resume_record = {
            "started_at_utc": now_utc(),
            "previous_manifest_status": previous_status,
            "checkpoint": str(checkpoint),
            "checkpoint_sha256": sha256_file(checkpoint),
            "checkpoint_epoch_zero_based": checkpoint_epoch,
            "next_epoch_one_based": checkpoint_epoch + 2,
            "results_csv_last_epoch_one_based": last_result_epoch,
            "resume_script": str(Path(__file__).resolve()),
            "resume_script_sha256": sha256_file(Path(__file__).resolve()),
            "resume_mode": "Ultralytics optimizer/EMA checkpoint continuation; original train args retained",
        }
        manifest.setdefault("resume_history", []).append(resume_record)
        manifest["status"] = "started"
        manifest["resumed_at_utc"] = now_utc()
        write_json(manifest_path, manifest)

        print(
            f"Resuming {args.run_name} from completed epoch {last_result_epoch}; "
            f"next training epoch is {checkpoint_epoch + 2}/100.",
            flush=True,
        )
        model = YOLO(str(checkpoint), task="detect")
        results = model.train(resume=True)

        best_checkpoint = run_dir / "weights/best.pt"
        if not best_checkpoint.is_file():
            raise ResumeError(f"Training resumed without a best checkpoint: {best_checkpoint}")
        manifest.update(
            {
                "status": "complete",
                "finished_at_utc": now_utc(),
                "student_best_checkpoint": str(best_checkpoint),
                "student_best_sha256": sha256_file(best_checkpoint),
                "metrics": metric_values(results),
                "resume_history": [*manifest["resume_history"][:-1], {**resume_record, "finished_at_utc": now_utc()}],
            }
        )
        write_json(manifest_path, manifest)
        manifest_path.replace(final_manifest)

        queue = json.loads(QUEUE_STATE.read_text(encoding="utf-8"))
        item = next(entry for entry in queue["items"] if entry.get("label") == f"supervised_seed{args.seed}")
        item.update(
            {
                "status": "succeeded",
                "finished_at_utc": now_utc(),
                "manifest": str(final_manifest),
                "recovered_from_checkpoint": str(checkpoint),
            }
        )
        item.pop("error", None)
        queue["status"] = "interrupted"
        queue["updated_at_utc"] = now_utc()
        queue.pop("error", None)
        write_json(QUEUE_STATE, queue)

        pipeline = json.loads(PIPELINE_STATE.read_text(encoding="utf-8"))
        if pipeline.get("status") == "waiting_for_training_queue":
            pipeline["status"] = "interrupted"
            pipeline["error"] = "Training queue observer stopped while the queue was running; resume after queue recovery."
            pipeline["updated_at_utc"] = now_utc()
            write_json(PIPELINE_STATE, pipeline)

        print(f"Resumed run completed; manifest: {final_manifest}", flush=True)
        return 0
    except KeyboardInterrupt:
        error = "Recovery interrupted before training completed."
        if manifest_path is not None and manifest:
            manifest.update({"status": "interrupted", "finished_at_utc": now_utc(), "error": error})
            write_json(manifest_path, manifest)
        print(error, file=sys.stderr, flush=True)
        return 130
    except Exception as error:
        if manifest_path is not None and manifest:
            manifest.update(
                {
                    "status": "failed",
                    "finished_at_utc": now_utc(),
                    "error": f"{type(error).__name__}: {error}",
                }
            )
            write_json(manifest_path, manifest)
        print(f"{type(error).__name__}: {error}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
