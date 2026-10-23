"""Capture missing three-seed Hybrid VAL predictions without changing older tables."""

from __future__ import annotations

from pathlib import Path

try:
    from . import analyze_val_detections as analyzer
except ImportError:
    import analyze_val_detections as analyzer


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runs/val_diagnostics/hybrid_objective_20261023"
HYBRID_RUNS = {
    "hybrid_full_seed1337": "yolo11_tiny_hybrid_full_seed1337",
    "hybrid_full_seed2025": "yolo11_tiny_hybrid_full_seed2025",
}


def main() -> None:
    images, expected, fingerprint = analyzer.source_paths()
    analyzer.verify_val_bytes(fingerprint)
    analyzer.HYBRID_RUNS.update(HYBRID_RUNS)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for label in HYBRID_RUNS:
        if (OUTPUT / f"{label}_predictions.json").exists():
            raise FileExistsError(f"Refusing to overwrite VAL capture: {label}")
        analyzer.capture_one(label, OUTPUT, images, expected, fingerprint, threads=8)


if __name__ == "__main__":
    main()
