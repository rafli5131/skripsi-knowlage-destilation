"""Evaluate one T42 teacher or student checkpoint on the locked VAL protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

try:
    from . import evaluate_val_ablation as base
except ImportError:
    import evaluate_val_ablation as base


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    checkpoint = args.checkpoint.resolve()
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete":
        raise RuntimeError("T42 training manifest is not complete")
    expected_hash = manifest.get("student_best_sha256", manifest.get("teacher_best_sha256"))
    if base.sha256(checkpoint) != expected_hash:
        raise RuntimeError("T42 checkpoint hash differs from manifest")
    output_dir = args.output_dir.resolve()
    result = output_dir / f"{args.label}_val.json"
    if result.exists():
        raise FileExistsError(f"Refusing to overwrite T42 result: {result}")
    images, expected_images, fingerprint = base.source_paths()
    base.verify_val_bytes(fingerprint)
    old_resolver = base.checkpoint_and_manifest
    try:
        base.checkpoint_and_manifest = lambda requested: (
            (checkpoint, manifest_path, manifest) if requested == args.label else old_resolver(requested)
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        print(base.evaluate(args.label, images, expected_images, fingerprint, 8, torch.device("cpu"), output_dir))
    finally:
        base.checkpoint_and_manifest = old_resolver


if __name__ == "__main__":
    main()
