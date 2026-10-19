"""Resolusi path data eksperimen dengan pemeriksaan fingerprint terkunci."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePath
from typing import Any

import yaml


EXPECTED_NAMES = {0: "ball", 1: "gawang", 2: "robot"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def sha256_file(path: Path) -> str:
    """Hitung SHA-256 berkas secara bertahap agar hemat memori."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    """Hitung SHA-256 teks UTF-8."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _split_suffix(value: str | Path, split: str) -> Path:
    """Ambil akhiran path mulai nama folder split dari YAML sumber."""
    parts = PurePath(str(value)).parts
    tokens = {"train"} if split == "train" else {"val", "valid"}
    for index, part in enumerate(parts):
        if part.lower() in tokens:
            return Path(*parts[index:])
    raise ValueError(f"Tidak dapat menentukan path relatif split {split!r} dari {value!r}.")


def _verify_split(root: Path, split: str, expected_split: dict[str, Any]) -> str:
    """Cocokkan semua gambar dan label split dengan fingerprint yang terkunci."""
    suffix = "valid" if split == "val" else split
    image_dir = root / suffix / "images"
    label_dir = root / suffix / "labels"
    if not image_dir.is_dir() or not label_dir.is_dir():
        raise FileNotFoundError(f"Direktori gambar/label {split} tidak lengkap di {root}.")

    expected_files = expected_split.get("files", [])
    expected_images = {str(item["image"]) for item in expected_files}
    expected_labels = {str(item["label"]) for item in expected_files}
    actual_images = {path.name for path in image_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES}
    actual_labels = {path.name for path in label_dir.iterdir() if path.is_file() and path.suffix.lower() == ".txt"}
    if actual_images != expected_images:
        missing = sorted(expected_images - actual_images)[:3]
        extra = sorted(actual_images - expected_images)[:3]
        raise ValueError(f"Inventaris gambar {split} berbeda; hilang={missing}, tambahan={extra}.")
    if actual_labels != expected_labels:
        missing = sorted(expected_labels - actual_labels)[:3]
        extra = sorted(actual_labels - expected_labels)[:3]
        raise ValueError(f"Inventaris label {split} berbeda; hilang={missing}, tambahan={extra}.")

    for item in expected_files:
        image_path = image_dir / str(item["image"])
        label_path = label_dir / str(item["label"])
        if sha256_file(image_path) != item["image_sha256"]:
            raise ValueError(f"Hash gambar {split} tidak cocok: {image_path}")
        if sha256_file(label_path) != item["label_sha256"]:
            raise ValueError(f"Hash label {split} tidak cocok: {label_path}")
    fingerprint = expected_split.get("split_fingerprint_sha256")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError(f"Fingerprint split {split} tidak tersedia atau tidak valid.")
    return fingerprint


def resolve_training_data(
    source_yaml: Path,
    run_dir: Path,
    fingerprint_path: Path,
    root_override: str | Path | None = None,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    """Resolve data YAML, opsional merebase root sambil memverifikasi byte data."""
    source_yaml = source_yaml.expanduser().resolve()
    raw = yaml.safe_load(source_yaml.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Konfigurasi data harus berupa mapping YAML: {source_yaml}")
    if "test" in raw:
        raise ValueError("YAML training tidak boleh memuat split TEST.")
    names = {int(key): str(value) for key, value in (raw.get("names") or {}).items()}
    if names != EXPECTED_NAMES:
        raise ValueError(f"Mapping kelas dataset tidak cocok: {names!r}")

    root_value = str(root_override).strip() if root_override is not None else ""
    if not root_value:
        for split in ("train", "val"):
            split_path = Path(str(raw.get(split, ""))).expanduser()
            if not split_path.is_absolute():
                split_path = (source_yaml.parent / split_path).resolve()
            if not split_path.is_dir():
                raise FileNotFoundError(f"Direktori gambar {split} tidak ditemukan: {split_path}")
            raw[split] = str(split_path)
        return source_yaml, raw, {
            "dataset_root_override": None,
            "dataset_root_sha256": None,
            "dataset_split_fingerprints_verified": False,
        }

    root = Path(root_value).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"KD_DATA_ROOT bukan direktori: {root}")
    fingerprint_path = fingerprint_path.expanduser().resolve()
    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
    splits = fingerprint.get("splits", {})
    split_fingerprints: dict[str, str] = {}
    for split in ("train", "val"):
        suffix = _split_suffix(raw.get(split, ""), split)
        split_path = (root / suffix).resolve()
        raw[split] = str(split_path)
        split_info = splits.get(split)
        if not isinstance(split_info, dict):
            raise ValueError(f"Fingerprint split {split} tidak ditemukan: {fingerprint_path}")
        split_fingerprints[split] = _verify_split(root, split, split_info)

    combined = sha256_text(json.dumps(split_fingerprints, sort_keys=True, separators=(",", ":")))
    raw.pop("path", None)
    resolved_yaml = run_dir / "resolved_data.yaml"
    return resolved_yaml, raw, {
        "dataset_root_override": str(root),
        "dataset_root_sha256": combined,
        "dataset_split_fingerprints_verified": True,
        "dataset_split_fingerprints": split_fingerprints,
    }


def write_resolved_data_yaml(path: Path, data: dict[str, Any]) -> None:
    """Simpan YAML hasil resolusi tanpa mengubah YAML sumber."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
