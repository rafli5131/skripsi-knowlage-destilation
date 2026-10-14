"""Create a read-only SHA-256 inventory for a YOLO image/label dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("/mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/dataset/data.yaml"),
        help="Canonical YOLO YAML with train, val, and test paths.",
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        nargs="*",
        default=[
            Path("/mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/raw/advance_vision_human/README.dataset.txt"),
            Path("/mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/raw/advance_vision_human/README.roboflow.txt"),
            Path("/mnt/nas-hpg9/rafli5131/rafli/advance_vision/configs/base.yaml"),
        ],
        help="Optional local provenance files to fingerprint.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts/advance_vision_dataset_fingerprint.json",
        help="Output JSON manifest path.",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_path(data_yaml: Path, payload: dict[str, Any], name: str) -> Path:
    value = payload.get(name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Dataset YAML has no valid {name!r} entry: {data_yaml}")
    path = Path(value).expanduser()
    if not path.is_absolute():
        dataset_root = Path(payload.get("path") or data_yaml.parent).expanduser()
        if not dataset_root.is_absolute():
            dataset_root = (data_yaml.parent / dataset_root).resolve()
        path = dataset_root / path
    path = path.resolve()
    if not path.is_dir() or path.name != "images" or not (path.parent / "labels").is_dir():
        raise ValueError(f"Expected a YOLO images directory with sibling labels for {name}: {path}")
    return path


def valid_annotation(line: str, num_classes: int) -> int | None:
    fields = line.split()
    if len(fields) != 5:
        return None
    try:
        class_id = int(fields[0])
        x, y, width, height = (float(value) for value in fields[1:])
    except ValueError:
        return None
    if class_id < 0 or class_id >= num_classes:
        return None
    if not all(math.isfinite(value) for value in (x, y, width, height)):
        return None
    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1):
        return None
    return class_id


def fingerprint_split(name: str, images_dir: Path, num_classes: int) -> dict[str, Any]:
    labels_dir = images_dir.parent / "labels"
    images = sorted(
        path for path in images_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    labels = sorted(path for path in labels_dir.rglob("*.txt") if path.is_file())
    image_relatives = {path.relative_to(images_dir).with_suffix("") for path in images}
    class_counts: Counter[int] = Counter()
    records = []
    empty_labels = 0
    invalid_annotations = []
    missing_pairs = []
    fingerprint = hashlib.sha256()

    for image in images:
        relative_image = image.relative_to(images_dir).as_posix()
        relative_label = image.relative_to(images_dir).with_suffix(".txt")
        label = labels_dir / relative_label
        if not label.is_file():
            missing_pairs.append(relative_image)
            label_hash = None
        else:
            label_hash = sha256_file(label)
            lines = [line.strip() for line in label.read_text(encoding="utf-8").splitlines() if line.strip()]
            if not lines:
                empty_labels += 1
            for line_number, line in enumerate(lines, 1):
                class_id = valid_annotation(line, num_classes)
                if class_id is None:
                    invalid_annotations.append(f"{relative_label.as_posix()}:{line_number}")
                else:
                    class_counts[class_id] += 1

        image_hash = sha256_file(image)
        fingerprint.update(f"{relative_image}\0{image_hash}\0".encode())
        fingerprint.update(f"{relative_label.as_posix()}\0{label_hash or 'MISSING'}\n".encode())
        records.append(
            {
                "image": relative_image,
                "image_sha256": image_hash,
                "label": relative_label.as_posix(),
                "label_sha256": label_hash,
            }
        )

    orphan_labels = sorted(
        label.relative_to(labels_dir).with_suffix("").as_posix()
        for label in labels
        if label.relative_to(labels_dir).with_suffix("") not in image_relatives
    )
    return {
        "images_dir": str(images_dir),
        "image_count": len(images),
        "label_count": len(labels),
        "annotation_count_by_class": {str(index): class_counts[index] for index in range(num_classes)},
        "annotation_count": sum(class_counts.values()),
        "empty_label_count": empty_labels,
        "missing_image_label_pairs": missing_pairs,
        "orphan_labels": orphan_labels,
        "invalid_annotations": invalid_annotations,
        "split_fingerprint_sha256": fingerprint.hexdigest(),
        "files": records,
    }


def main() -> int:
    args = parse_args()
    data_yaml = args.data.expanduser().resolve()
    payload = yaml.safe_load(data_yaml.read_text(encoding="utf-8")) or {}
    names = payload.get("names")
    if isinstance(names, list):
        class_names = {index: str(name) for index, name in enumerate(names)}
    elif isinstance(names, dict):
        class_names = {int(index): str(name) for index, name in names.items()}
    else:
        raise ValueError(f"Dataset YAML has invalid class names: {names!r}")
    if sorted(class_names) != list(range(len(class_names))):
        raise ValueError(f"Dataset class IDs must be contiguous from zero: {class_names!r}")

    splits = {}
    for name in ("train", "val", "test"):
        splits[name] = fingerprint_split(name, split_path(data_yaml, payload, name), len(class_names))

    metadata = []
    for path in args.metadata or []:
        resolved = path.expanduser().resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"Metadata file does not exist: {resolved}")
        metadata.append({"path": str(resolved), "sha256": sha256_file(resolved)})

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_yaml": {"path": str(data_yaml), "sha256": sha256_file(data_yaml)},
        "classes": {str(index): class_names[index] for index in sorted(class_names)},
        "metadata_files": metadata,
        "splits": splits,
    }
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Dataset fingerprint written: {output}")
    for split, values in splits.items():
        print(
            f"{split}: {values['image_count']} images, {values['annotation_count']} annotations, "
            f"fingerprint={values['split_fingerprint_sha256']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
