"""Evaluate one completed hybrid_v2 training run with the locked T28 VAL settings."""

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
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=base.ROOT / "runs/val_ablation/hybrid_v2_20261023")
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--device", choices=("cpu", "cuda:0"), default="cpu")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    if run_dir.parent != (base.ROOT / "runs/kd_hybrid_v2").resolve():
        raise ValueError("Only runs/kd_hybrid_v2 child runs are accepted")
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["status"] != "complete" or manifest["distillation"]["mode"] != "hybrid_v2":
        raise ValueError("A completed hybrid_v2 manifest is required")
    checkpoint = Path(manifest["student_best_checkpoint"]).resolve()
    if checkpoint != (run_dir / "weights/best.pt").resolve():
        raise ValueError("Unexpected checkpoint location in manifest")
    if base.sha256(checkpoint) != manifest["student_best_sha256"]:
        raise ValueError("Student checkpoint hash differs from training manifest")
    label = run_dir.name
    output_dir = args.output_dir.resolve()
    result_path = output_dir / f"{label}_val.json"
    if result_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing VAL result: {result_path}")
    if args.threads < 1:
        raise ValueError("threads must be positive")
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")
    images, expected, fingerprint = base.source_paths()
    base.verify_val_bytes(fingerprint)
    old_resolver = base.checkpoint_and_manifest
    try:
        base.checkpoint_and_manifest = lambda requested: (
            (checkpoint, manifest_path, manifest) if requested == label else old_resolver(requested)
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        print(base.evaluate(label, images, expected, fingerprint, args.threads, device, output_dir))
    finally:
        base.checkpoint_and_manifest = old_resolver


if __name__ == "__main__":
    main()
