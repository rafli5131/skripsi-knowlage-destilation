#!/usr/bin/env python3
"""Verify file and dataset fingerprints recorded in experiment manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FINGERPRINT = ROOT / "artifacts/advance_vision_dataset_fingerprint.json"
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
ALIASES = {
    "student_best": ("student_best_checkpoint",),
    "teacher": ("teacher_checkpoint",),
    "checkpoint": ("checkpoint",),
    "training_manifest": ("training_manifest",),
    "test_manifest": ("test_manifest",),
    "dataset_fingerprint": ("dataset_fingerprint",),
    "dataset_yaml": ("dataset_yaml", "data_yaml"),
    "run_config": ("run_config_path",),
    "training_script": ("training_script_path",),
    "analysis_script": ("analysis_script",),
    "benchmark": ("benchmark",),
    "evaluator_script": ("evaluator_script",),
    "source_yaml": ("source_yaml",),
    "source_summary": ("source_summary",),
    "evidence": ("evidence_path", "evidence"),
    "fingerprint": ("fingerprint", "dataset_fingerprint"),
    "corrected_analysis_manifest": ("corrected_analysis_manifest", "corrected_analysis_output"),
    "final_test_manifest": ("final_test_manifest", "test_manifest", "test_output"),
}


def sha256_file(path: Path) -> str:
    """Return a file's SHA-256 digest."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_files(paths: list[Path]) -> list[Path]:
    """Expand directories to known manifest JSON files."""
    result: set[Path] = set()
    for value in paths:
        path = value.expanduser().resolve()
        if path.is_dir():
            result.update(path.rglob("*manifest.json"))
            result.update(path.rglob("final_evaluation_pipeline.json"))
        elif path.is_file():
            result.add(path)
        else:
            raise FileNotFoundError(f"Manifest path does not exist: {path}")
    return sorted(path for path in result if path.suffix.lower() == ".json")


def _resolve_path(value: str, manifest_path: Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    repo_relative = (ROOT / path).resolve()
    if repo_relative.exists():
        return repo_relative
    return (manifest_path.parent / path).resolve()


def _candidate_keys(hash_key: str) -> tuple[str, ...]:
    if hash_key == "sha256":
        return ("path", "checkpoint", "manifest", "source_path", "file", "artifact", "evidence_path")
    stem = hash_key[:-7] if hash_key.endswith("_sha256") else hash_key
    aliases = ALIASES.get(stem, ())
    return tuple(dict.fromkeys((*aliases, stem, f"{stem}_path", f"{stem}_file", f"{stem}_checkpoint", f"{stem}_manifest")))


def _find_file_reference(ancestors: list[dict[str, Any]], hash_key: str) -> str | None:
    for mapping in reversed(ancestors):
        for key in _candidate_keys(hash_key):
            value = mapping.get(key)
            if isinstance(value, str) and value and not HASH_RE.fullmatch(value):
                path = _resolve_path(value, Path.cwd() / "manifest.json")
                if path.is_dir() and hash_key.startswith(("corrected_analysis_manifest", "final_test_manifest")):
                    return str(path / ("analysis_manifest.json" if hash_key.startswith("corrected") else "manifest.json"))
                return value
            if isinstance(value, dict):
                for nested_key in ("path", "checkpoint", "manifest", "file"):
                    nested_value = value.get(nested_key)
                    if isinstance(nested_value, str) and nested_value:
                        return nested_value
    return None


def _find_fingerprint_path(ancestors: list[dict[str, Any]], manifest_path: Path) -> Path:
    for mapping in reversed(ancestors):
        for key in ("dataset_fingerprint", "fingerprint"):
            value = mapping.get(key)
            if isinstance(value, str) and value and not HASH_RE.fullmatch(value):
                return _resolve_path(value, manifest_path)
    return DEFAULT_FINGERPRINT


def verify_manifest(manifest_path: Path) -> list[dict[str, str]]:
    """Verify every resolvable SHA-256 field in one JSON manifest."""
    manifest_path = manifest_path.expanduser().resolve()
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    results: list[dict[str, str]] = []

    def check(value: Any, location: str, ancestors: list[dict[str, Any]]) -> None:
        if isinstance(value, dict):
            chain = [*ancestors, value]
            split_fingerprints = value.get("dataset_split_fingerprints")
            if isinstance(split_fingerprints, dict):
                fingerprint_path = _find_fingerprint_path(chain, manifest_path)
                if fingerprint_path.is_file():
                    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
                    for split, expected in split_fingerprints.items():
                        actual = fingerprint.get("splits", {}).get(str(split), {}).get("split_fingerprint_sha256")
                        status = "PASS" if actual == expected else "MISMATCH"
                        results.append({
                            "manifest": str(manifest_path), "field": f"{location}.dataset_split_fingerprints.{split}",
                            "expected": str(expected), "actual": str(actual), "status": status,
                        })
                else:
                    results.append({
                        "manifest": str(manifest_path), "field": f"{location}.dataset_split_fingerprints",
                        "expected": str(fingerprint_path), "actual": "missing", "status": "MISSING",
                    })
            for key, child in value.items():
                if isinstance(child, str) and (key == "sha256" or key.endswith("_sha256")) and HASH_RE.fullmatch(child):
                    field = f"{location}.{key}"
                    if key in {"test_split_fingerprint_sha256", "split_fingerprint_sha256"}:
                        split_name = "test" if key == "test_split_fingerprint_sha256" else location.split(".")[-1]
                        fingerprint_path = _find_fingerprint_path(chain, manifest_path)
                        try:
                            fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
                            actual = fingerprint.get("splits", {}).get(split_name, {}).get("split_fingerprint_sha256")
                            status = "PASS" if actual == child else "MISMATCH"
                        except (OSError, json.JSONDecodeError):
                            actual, status = "missing", "MISSING"
                    else:
                        reference = _find_file_reference(chain, key)
                        if reference is None and key == "fingerprint_sha256":
                            reference = str(DEFAULT_FINGERPRINT)
                        if reference is None:
                            results.append({"manifest": str(manifest_path), "field": field, "expected": child, "actual": "unresolved", "status": "UNRESOLVED"})
                            continue
                        target = _resolve_path(reference, manifest_path)
                        if not target.is_file():
                            actual, status = "missing", "MISSING"
                        else:
                            actual = sha256_file(target)
                            status = "PASS" if actual.lower() == child.lower() else "MISMATCH"
                    results.append({"manifest": str(manifest_path), "field": field, "expected": child, "actual": str(actual), "status": status})
                else:
                    check(child, f"{location}.{key}", chain)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check(child, f"{location}[{index}]", ancestors)

    check(document, "$", [])
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths", nargs="*", type=Path,
        default=[ROOT / "runs", ROOT / "artifacts"],
        help="Manifest files or directories; defaults to runs/ and artifacts/.",
    )
    parser.add_argument("--json-output", type=Path, help="Optional JSON report path; refuses to overwrite.")
    args = parser.parse_args()
    records: list[dict[str, str]] = []
    for path in manifest_files(args.paths):
        try:
            records.extend(verify_manifest(path))
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
            records.append({"manifest": str(path), "field": "$", "expected": "valid JSON", "actual": str(error), "status": "ERROR"})
    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
        print(f"{record['status']:10} {record['manifest']} {record['field']} expected={record['expected']} actual={record['actual']}")
    print("Summary:", json.dumps(counts, sort_keys=True))
    if args.json_output is not None:
        output = args.json_output.expanduser().resolve()
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite hash report: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({"records": records, "counts": counts}, indent=2) + "\n", encoding="utf-8")
    return 0 if not any(key in counts for key in ("MISMATCH", "MISSING", "UNRESOLVED", "ERROR")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
