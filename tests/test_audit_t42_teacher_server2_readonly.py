import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import audit_t42_teacher_server2_readonly as audit


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TeacherAuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        fingerprint = self.root / "artifacts/advance_vision_dataset_fingerprint.json"
        fingerprint.parent.mkdir(parents=True)
        fingerprint.write_text("fingerprint")
        self.pretrained_hashes = {}
        for variant in ("n", "s"):
            label = f"teacher_yolo11{variant}_seed42"
            base = self.root / "models_local/teacher_ablation_t42/server2/training" / label
            base.mkdir(parents=True)
            pretrained, checkpoint, yaml = (base / p for p in ("pretrained.pt", "best.pt", "data.yaml"))
            for path in (pretrained, checkpoint, yaml):
                path.write_text(f"{variant}-{path.name}")
            self.pretrained_hashes[variant] = digest(pretrained)
            manifest = {"status": "complete", "kind": "matched_teacher_training_t42", "t42_attempt": "server2",
                        "variant": f"yolo11{variant}", "seed": 42, "training": audit.EXPECTED_TRAINING,
                        "validation_split": "VAL only", "test_split_used": False,
                        "dataset_split_fingerprints_verified": True, "teacher_best_checkpoint": str(checkpoint),
                        "teacher_best_sha256": digest(checkpoint), "pretrained_checkpoint": str(pretrained),
                        "pretrained_sha256": digest(pretrained), "data_yaml": str(yaml), "data_yaml_sha256": digest(yaml),
                        "dataset_fingerprint_sha256": digest(fingerprint), "teacher_parameters": 10,
                        "duration_seconds": 10, "versions": {"python": "3.11"}}
            mpath = base / "manifest.json"
            mpath.write_text(json.dumps(manifest))
            evdir = self.root / "runs/val_ablation/teacher_yolo11s_t42_server2"
            evdir.mkdir(parents=True, exist_ok=True)
            (evdir / f"{label}_val.json").write_text(json.dumps({"model": label, "images": 1213,
                "checkpoint_sha256": digest(checkpoint), "training_manifest_sha256": digest(mpath),
                "val_split_fingerprint_sha256": "same-val"}))

    def run_audit(self):
        with patch.object(audit, "PRETRAINED", self.pretrained_hashes):
            return audit.audit(self.root)

    def test_valid_inputs_pass(self):
        self.assertTrue(self.run_audit()["complete"])

    def test_changed_checkpoint_fails(self):
        target = self.root / "models_local/teacher_ablation_t42/server2/training/teacher_yolo11n_seed42/best.pt"
        target.write_text("changed")
        report = self.run_audit()
        self.assertFalse(report["complete"])
        self.assertFalse(report["teachers"]["teacher_yolo11n_seed42"]["checks"]["checkpoint_hash_agrees"])

    def test_missing_manifest_fails_without_crashing(self):
        target = self.root / "models_local/teacher_ablation_t42/server2/training/teacher_yolo11s_seed42/manifest.json"
        target.unlink()
        self.assertFalse(self.run_audit()["complete"])
        self.assertTrue(self.run_audit()["issues"])


if __name__ == "__main__":
    unittest.main()
