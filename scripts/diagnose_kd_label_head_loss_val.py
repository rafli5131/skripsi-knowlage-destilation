"""Measure available Hybrid seed-42 label/head loss terms on a fixed VAL batch.

The trained projector was not serialized with best.pt, so feature KD is excluded.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import cv2
import torch
import torch.nn.functional as F
import yaml
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]
FINGERPRINT = ROOT / "artifacts/advance_vision_dataset_fingerprint.json"
TEACHER = Path("/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt")
STUDENT = ROOT / "runs/kd_hybrid/yolo11_tiny_hybrid_full_seed42/weights/best.pt"
OUTPUT = ROOT / "runs/kd_diagnosis/20261023_label_head_loss_val_batch16.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw(prediction: object) -> dict:
    data = prediction[1] if isinstance(prediction, tuple) else prediction
    if isinstance(data, dict) and "one2many" in data:
        return data["one2many"]
    if isinstance(data, dict) and {"boxes", "scores"}.issubset(data):
        return data
    raise RuntimeError(f"Unexpected Detect prediction: {type(data).__name__}")


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUTPUT}")
    torch.set_num_threads(8)
    split = json.loads(FINGERPRINT.read_text(encoding="utf-8"))["splits"]["val"]
    chosen = sorted(split["files"], key=lambda item: item["image"])[:16]
    images = []
    classes, boxes, indices = [], [], []
    for index, record in enumerate(chosen):
        image_path = Path(split["images_dir"]) / record["image"]
        label_path = image_path.parent.parent / "labels" / record["label"]
        if digest(image_path) != record["image_sha256"] or digest(label_path) != record["label_sha256"]:
            raise RuntimeError(f"VAL image/label hash mismatch: {record['image']}")
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError(f"Could not decode {image_path}")
        image = cv2.resize(image, (640, 640), interpolation=cv2.INTER_LINEAR)
        images.append(torch.from_numpy(image[:, :, ::-1].copy()).permute(2, 0, 1))
        for line in label_path.read_text(encoding="utf-8").splitlines():
            fields = line.split()
            if len(fields) != 5:
                raise RuntimeError(f"Invalid label in {label_path}")
            classes.append(float(fields[0]))
            boxes.append([float(value) for value in fields[1:]])
            indices.append(index)
    batch = {
        "img": torch.stack(images).float() / 255.0,
        "cls": torch.tensor(classes, dtype=torch.float32).view(-1, 1),
        "bboxes": torch.tensor(boxes, dtype=torch.float32).view(-1, 4),
        "batch_idx": torch.tensor(indices, dtype=torch.long),
    }
    teacher = YOLO(str(TEACHER), task="detect").model.float().cpu().eval()
    student = YOLO(str(STUDENT), task="detect").model.float().cpu().train()
    # The exported inference checkpoint retains only a small args dict. Recover
    # the actual detection-loss gains from the frozen training args.yaml.
    training_args = yaml.safe_load((ROOT / "runs/kd_hybrid/yolo11_tiny_hybrid_full_seed42/args.yaml").read_text())
    student.args = SimpleNamespace(**training_args)
    with torch.no_grad():
        t = raw(teacher(batch["img"]))
        s_prediction = student(batch["img"])
        s = raw(s_prediction)
        _, label_items = student.loss(batch, s_prediction)
        tau = 2.0
        box_kd = F.smooth_l1_loss(s["boxes"].float(), t["boxes"].float())
        soft_target = torch.sigmoid(t["scores"].float() / tau)
        class_kd = F.binary_cross_entropy_with_logits(s["scores"].float() / tau, soft_target) * tau**2
    result = {
        "scope": "diagnostic 16-image VAL batch with known labels; no optimization or TEST access",
        "preprocessing": "OpenCV direct resize 640x640, RGB float32/255; diagnostic, not exact rect VAL pipeline",
        "VAL_fingerprint_sha256": split["split_fingerprint_sha256"],
        "images": [record["image"] for record in chosen],
        "teacher_checkpoint_sha256": digest(TEACHER),
        "student_checkpoint_sha256": digest(STUDENT),
        "labeled_objects": len(classes),
        "label_loss_terms_per_batch": {name: float(value) for name, value in label_items.items()},
        "raw_box_kd_smooth_l1_mean": float(box_kd),
        "class_kd_soft_BCE_tau2_mean": float(class_kd),
        "feature_kd": None,
        "feature_kd_reason": "The trained feature projector is absent from student best.pt and last.pt; reconstructing a random projector would not reproduce the trained Hybrid objective.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
