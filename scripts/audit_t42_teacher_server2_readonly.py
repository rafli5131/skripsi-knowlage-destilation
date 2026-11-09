#!/usr/bin/env python3
"""Audit dua teacher T42 server2 secara read-only; keluaran JSON hanya ke stdout."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRETRAINED = {
    "n": "0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1",
    "s": "85a76fe86dd8afe384648546b56a7a78580c7cb7b404fc595f97969322d502d5",
}
EXPECTED_TRAINING = {
    "epochs": 100, "batch": 16, "workers": 2, "imgsz": 640,
    "optimizer": "AdamW", "lr0": 0.001, "lrf": 0.01,
    "warmup_epochs": 3.0, "weight_decay": 0.0005, "close_mosaic": 10,
    "amp": False, "patience": 30, "pretrained": True,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(root: Path) -> dict:
    result = {"attempt": "server2", "mode": "read_only", "teachers": {}, "checks": {}, "issues": []}
    manifests = {}
    for variant in ("n", "s"):
        label = f"teacher_yolo11{variant}_seed42"
        manifest_path = root / "models_local/teacher_ablation_t42/server2/training" / label / "manifest.json"
        eval_path = root / "runs/val_ablation/teacher_yolo11s_t42_server2" / f"{label}_val.json"
        record = {"checks": {}, "values": {}}
        result["teachers"][label] = record
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            evaluation = json.loads(eval_path.read_text(encoding="utf-8"))
            manifests[variant] = manifest
            checks = record["checks"]
            checks["manifest_hash_matches_evaluation"] = sha256(manifest_path) == evaluation["training_manifest_sha256"]
            checks["identity_status"] = (manifest["status"] == "complete" and manifest["kind"] == "matched_teacher_training_t42"
                                         and manifest["t42_attempt"] == "server2" and manifest["variant"] == f"yolo11{variant}"
                                         and manifest["seed"] == 42)
            checks["train_recipe_matches_protocol"] = manifest["training"] == EXPECTED_TRAINING
            checks["val_only_and_train_val_verified"] = (manifest["validation_split"] == "VAL only"
                                                          and manifest["test_split_used"] is False
                                                          and manifest["dataset_split_fingerprints_verified"] is True)
            checks["checkpoint_hash_agrees"] = (sha256(Path(manifest["teacher_best_checkpoint"]))
                                                  == manifest["teacher_best_sha256"] == evaluation["checkpoint_sha256"])
            checks["official_pretrained_hash_agrees"] = (sha256(Path(manifest["pretrained_checkpoint"]))
                                                           == manifest["pretrained_sha256"] == PRETRAINED[variant])
            checks["dataset_fingerprint_file_hash"] = (sha256(root / "artifacts/advance_vision_dataset_fingerprint.json")
                                                         == manifest["dataset_fingerprint_sha256"])
            checks["data_yaml_hash"] = sha256(Path(manifest["data_yaml"])) == manifest["data_yaml_sha256"]
            checks["val_identity"] = evaluation["model"] == label and evaluation["images"] == 1213
            record["values"] = {"teacher_sha256": manifest["teacher_best_sha256"],
                                "pretrained_sha256": manifest["pretrained_sha256"],
                                "dataset_fingerprint_sha256": manifest["dataset_fingerprint_sha256"],
                                "val_split_fingerprint_sha256": evaluation["val_split_fingerprint_sha256"],
                                "parameters": manifest["teacher_parameters"],
                                "duration_seconds": manifest["duration_seconds"],
                                "versions": manifest["versions"]}
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            result["issues"].append({"teacher": label, "error": f"{type(exc).__name__}: {exc}"})
    if len(manifests) == 2:
        n, s = manifests["n"], manifests["s"]
        result["checks"]["teacher_recipes_match"] = n.get("training") == s.get("training") == EXPECTED_TRAINING
        result["checks"]["dataset_fingerprint_matches"] = n.get("dataset_fingerprint_sha256") == s.get("dataset_fingerprint_sha256")
        result["checks"]["versions_match"] = n.get("versions") == s.get("versions")
        values = [item["values"] for item in result["teachers"].values()]
        result["checks"]["val_fingerprints_match"] = bool(all(values)) and values[0].get("val_split_fingerprint_sha256") == values[1].get("val_split_fingerprint_sha256")
    result["complete"] = (len(manifests) == 2 and not result["issues"] and bool(result["checks"])
                          and all(result["checks"].values())
                          and all(item["checks"] and all(item["checks"].values()) for item in result["teachers"].values()))
    return result


if __name__ == "__main__":
    report = audit(ROOT)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["complete"] else 1)
