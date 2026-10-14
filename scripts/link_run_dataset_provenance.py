"""Link a completed run to an earlier dataset snapshot after rechecking its bytes.

Use this only for runs that began after a fingerprint was created but whose
original training manifest did not record that fingerprint. Legacy runs may
also lack a run-time hash of their dataset YAML; saved args, class/split paths,
and current YAML are then verified and that limitation remains explicit. The
manifest clearly records that linkage happened after training.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class ProvenanceLinkError(RuntimeError):
    """Raised when the run cannot be linked to the requested data snapshot."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_split(data_yaml: Path, payload: dict[str, Any], name: str) -> Path:
    value = payload.get(name)
    if not isinstance(value, str) or not value:
        raise ProvenanceLinkError(f"Training YAML has no valid {name!r} split.")
    path = Path(value).expanduser()
    if not path.is_absolute():
        root = Path(payload.get("path") or data_yaml.parent).expanduser()
        if not root.is_absolute():
            root = (data_yaml.parent / root).resolve()
        path = root / path
    path = path.resolve()
    if not path.is_dir() or path.name != "images" or not (path.parent / "labels").is_dir():
        raise ProvenanceLinkError(f"Invalid {name} image/label directory: {path}")
    return path


def verify_split(name: str, snapshot: dict[str, Any]) -> Path:
    images_dir = Path(snapshot["images_dir"]).expanduser().resolve()
    labels_dir = images_dir.parent / "labels"
    if not images_dir.is_dir() or not labels_dir.is_dir():
        raise ProvenanceLinkError(f"Snapshot directories are missing for {name}: {images_dir}")

    images = sorted(
        path for path in images_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    labels = sorted(path for path in labels_dir.rglob("*.txt") if path.is_file())
    records = snapshot.get("files")
    if not isinstance(records, list):
        raise ProvenanceLinkError(f"Snapshot file inventory is missing for {name}.")

    expected_images = [record["image"] for record in records]
    actual_images = [path.relative_to(images_dir).as_posix() for path in images]
    if actual_images != expected_images:
        raise ProvenanceLinkError(f"Image inventory changed in {name} since fingerprint creation.")

    expected_labels = [record["label"] for record in records if record.get("label_sha256") is not None]
    actual_labels = [path.relative_to(labels_dir).as_posix() for path in labels]
    if actual_labels != expected_labels:
        raise ProvenanceLinkError(f"Label inventory changed in {name} since fingerprint creation.")

    aggregate = hashlib.sha256()
    for image, record in zip(images, records, strict=True):
        image_relative = record["image"]
        label_relative = record["label"]
        image_hash = sha256_file(image)
        label_path = labels_dir / label_relative
        label_hash = sha256_file(label_path) if label_path.is_file() else None
        if image_hash != record.get("image_sha256") or label_hash != record.get("label_sha256"):
            raise ProvenanceLinkError(f"Image or label bytes changed in {name}: {image_relative}")
        aggregate.update(f"{image_relative}\0{image_hash}\0".encode())
        aggregate.update(f"{label_relative}\0{label_hash or 'MISSING'}\n".encode())

    if aggregate.hexdigest() != snapshot.get("split_fingerprint_sha256"):
        raise ProvenanceLinkError(f"Aggregate {name} fingerprint does not match the snapshot.")
    return images_dir


def mount_read_only(path: Path) -> dict[str, Any] | None:
    """Report the current mount flags for a path; this is not a historical claim."""
    try:
        lines = Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    target = path.resolve()
    candidates = []
    for line in lines:
        before, separator, after = line.partition(" - ")
        if not separator:
            continue
        fields = before.split()
        filesystem = after.split()
        if len(fields) < 6 or len(filesystem) < 3:
            continue
        mountpoint = Path(fields[4].replace("\\040", " ")).resolve()
        try:
            target.relative_to(mountpoint)
        except ValueError:
            continue
        options = set(fields[5].split(",")) | set(filesystem[2].split(","))
        candidates.append((len(str(mountpoint)), mountpoint, options, filesystem[0], filesystem[1]))
    if not candidates:
        return None
    _, mountpoint, options, filesystem, source = max(candidates, key=lambda item: item[0])
    return {
        "mountpoint": str(mountpoint),
        "filesystem": filesystem,
        "source": source,
        "read_only_at_link_time": "ro" in options,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="Completed run manifest to update.")
    parser.add_argument(
        "--fingerprint",
        type=Path,
        default=ROOT / "artifacts/advance_vision_dataset_fingerprint.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.expanduser().resolve()
    fingerprint_path = args.fingerprint.expanduser().resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))

    if manifest.get("status") != "complete":
        raise ProvenanceLinkError("Only a completed training run can be linked.")
    if manifest.get("test_split_used") is not False:
        raise ProvenanceLinkError("Run is not eligible: TEST must be declared unused during training.")
    started_at = datetime.fromisoformat(manifest["started_at_utc"])
    snapshot_at = datetime.fromisoformat(fingerprint["created_at_utc"])
    if snapshot_at > started_at:
        raise ProvenanceLinkError("Dataset fingerprint was created after this run started.")

    data_yaml = Path(manifest["dataset_yaml"]).expanduser().resolve()
    if not data_yaml.is_file():
        raise ProvenanceLinkError(f"Training YAML is missing: {data_yaml}")
    data_yaml_hash_at_link = sha256_file(data_yaml)
    run_args_path = manifest_path.parent / "args.yaml"
    if not run_args_path.is_file():
        raise ProvenanceLinkError(f"Ultralytics training args are missing: {run_args_path}")
    run_args = yaml.safe_load(run_args_path.read_text(encoding="utf-8")) or {}
    if Path(run_args.get("data", "")).expanduser().resolve() != data_yaml:
        raise ProvenanceLinkError("Ultralytics args do not point to the training YAML in the run manifest.")

    data_yaml_hash_recorded_at_start = manifest.get("dataset_yaml_sha256")
    if data_yaml_hash_recorded_at_start:
        if data_yaml_hash_recorded_at_start != data_yaml_hash_at_link:
            raise ProvenanceLinkError("Training YAML differs from the hash recorded in the original run manifest.")
    else:
        expected_legacy_run = (
            manifest.get("seed") == 42
            and "supervised" in str(manifest.get("objective", "")).lower()
            and Path(manifest.get("output_dir", "")).expanduser().resolve()
            == (ROOT / "runs/supervised/yolo11_tiny_supervised_seed42_retry1").resolve()
        )
        if not expected_legacy_run:
            raise ProvenanceLinkError("Training YAML hash is missing for a run outside the documented legacy baseline.")
        if run_args.get("val") is not True or run_args.get("split") != "val":
            raise ProvenanceLinkError("Legacy baseline args do not show validation-based checkpoint selection.")

    training_data = yaml.safe_load(data_yaml.read_text(encoding="utf-8")) or {}
    if "test" in training_data:
        raise ProvenanceLinkError("Training YAML exposes a TEST split; this run cannot be linked as TEST-unseen.")

    source_yaml_record = fingerprint.get("source_yaml", {})
    source_yaml = Path(source_yaml_record.get("path", "")).expanduser()
    if not source_yaml.is_file() or sha256_file(source_yaml) != source_yaml_record.get("sha256"):
        raise ProvenanceLinkError("Canonical dataset YAML differs from the recorded fingerprint.")
    for metadata_record in fingerprint.get("metadata_files", []):
        metadata_path = Path(metadata_record["path"]).expanduser()
        if not metadata_path.is_file() or sha256_file(metadata_path) != metadata_record.get("sha256"):
            raise ProvenanceLinkError(f"Dataset provenance metadata changed: {metadata_path}")

    training_names = training_data.get("names")
    if isinstance(training_names, list):
        training_classes = {str(index): str(name) for index, name in enumerate(training_names)}
    elif isinstance(training_names, dict):
        training_classes = {str(index): str(name) for index, name in training_names.items()}
    else:
        raise ProvenanceLinkError("Training YAML has no valid class mapping.")
    if training_classes != fingerprint.get("classes"):
        raise ProvenanceLinkError("Training YAML class mapping differs from the dataset fingerprint.")

    split_dirs = {}
    for split in ("train", "val", "test"):
        if split not in fingerprint.get("splits", {}):
            raise ProvenanceLinkError(f"Fingerprint has no {split!r} split.")
        split_dirs[split] = verify_split(split, fingerprint["splits"][split])
    for split in ("train", "val"):
        configured = resolve_split(data_yaml, training_data, split)
        if configured != split_dirs[split]:
            raise ProvenanceLinkError(f"Training YAML {split} path differs from the fingerprinted split.")

    if manifest.get("dataset_fingerprint_sha256"):
        if manifest["dataset_fingerprint_sha256"] != sha256_file(fingerprint_path):
            raise ProvenanceLinkError("Run already points to a different dataset fingerprint.")

    linked_at = datetime.now(timezone.utc).isoformat()
    manifest.update(
        {
            "dataset_fingerprint": str(fingerprint_path),
            "dataset_fingerprint_sha256": sha256_file(fingerprint_path),
            "dataset_split_fingerprints": {
                split: fingerprint["splits"][split]["split_fingerprint_sha256"]
                for split in ("train", "val", "test")
            },
            "dataset_snapshot_provenance": {
                "linked_after_training": True,
                "linked_at_utc": linked_at,
                "fingerprint_created_at_utc": fingerprint["created_at_utc"],
                "run_started_at_utc": manifest["started_at_utc"],
                "fingerprint_predates_run": True,
                "all_image_and_label_hashes_revalidated_at_link_time": True,
                "training_yaml_hash_recorded_at_run_start": bool(data_yaml_hash_recorded_at_start),
                "training_yaml_sha256_at_link_time": data_yaml_hash_at_link,
                "training_args_path": str(run_args_path),
                "training_args_sha256_at_link_time": sha256_file(run_args_path),
                "current_source_mount": mount_read_only(split_dirs["train"]),
                "note": (
                    "Fingerprint linkage was added after training because the original run manifest "
                    "did not record it. The fingerprint predates the run; every image and label in "
                    "train, val, and test was rehashed and matched at link time. If the original "
                    "manifest lacks the training YAML hash, the saved Ultralytics args, current YAML "
                    "class map, and train/val paths were checked; its byte identity at run start "
                    "cannot be claimed retrospectively."
                ),
            },
        }
    )

    temporary = manifest_path.with_name(f".{manifest_path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    print(f"Linked pre-run dataset fingerprint to completed run: {manifest_path}")
    print(f"Fingerprint SHA-256: {manifest['dataset_fingerprint_sha256']}")
    for split, split_hash in manifest["dataset_split_fingerprints"].items():
        print(f"{split}: {split_hash}")
    print(f"Linkage time UTC: {linked_at}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
