"""Uji override path lokal dengan checkpoint sementara dan hash registry."""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.model_registry import DEFAULT_REGISTRY, checkpoint_for_variant, validate_checkpoint


class LocalCheckpointOverrideTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.canonical = self.root / "canonical.pt"
        self.local = self.root / "models_local" / "teacher.pt"
        self.local.parent.mkdir()
        self.payload = b"registered teacher test checkpoint"
        self.canonical.write_bytes(self.payload)
        self.local.write_bytes(self.payload)
        digest = hashlib.sha256(self.payload).hexdigest()
        self.registry = self.root / "registry.yaml"
        self.registry.write_text(yaml.safe_dump({
            "models": {"teacher_fp32": {"checkpoint": str(self.canonical), "sha256": digest}},
            "aliases": {},
        }), encoding="utf-8")
        self.local_registry = self.root / "local.yaml"
        self.local_registry.write_text(yaml.safe_dump({"teacher_fp32": str(self.local)}), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_default_checkpoint_path_is_unchanged_without_local_registry(self) -> None:
        name, path = checkpoint_for_variant("teacher", self.registry, local_registry_path=self.root / "missing.yaml")
        self.assertEqual(name, "teacher_fp32")
        self.assertEqual(path, self.canonical)
        model_name, entry = validate_checkpoint(
            path, label=name, registry_path=self.registry, local_registry_path=self.root / "missing.yaml"
        )
        self.assertEqual(model_name, name)
        self.assertFalse(entry["local_override_used"])

    def test_local_override_is_accepted_when_hash_matches(self) -> None:
        name, path = checkpoint_for_variant(
            "teacher", self.registry, local_registry_path=self.local_registry
        )
        model_name, entry = validate_checkpoint(
            path, label=name, registry_path=self.registry, local_registry_path=self.local_registry
        )
        self.assertEqual(model_name, "teacher_fp32")
        self.assertTrue(entry["local_override_used"])
        self.assertEqual(entry["local_override_path"], str(self.local.resolve()))

    def test_local_override_with_wrong_hash_is_rejected(self) -> None:
        self.local.write_bytes(b"different payload")
        with self.assertRaisesRegex(ValueError, "Hash checkpoint"):
            validate_checkpoint(
                self.local, label="teacher_fp32", registry_path=self.registry,
                local_registry_path=self.local_registry,
            )

    def test_supervised_seed1337_registered_checkpoint_is_accepted(self) -> None:
        checkpoint = Path("runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt")
        model_name, entry = validate_checkpoint(checkpoint, registry_path=DEFAULT_REGISTRY)
        self.assertEqual(model_name, "supervised_seed1337")
        self.assertEqual(entry["sha256"], "d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041")


if __name__ == "__main__":
    unittest.main()
