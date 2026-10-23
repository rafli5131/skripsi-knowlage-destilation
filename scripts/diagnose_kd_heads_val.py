"""Inspect teacher/student raw Detect heads on one fixed 16-image VAL batch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import torch
import torch.nn.functional as F
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]
FINGERPRINT = ROOT / "artifacts/advance_vision_dataset_fingerprint.json"
TEACHER = Path("/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt")
STUDENT = ROOT / "runs/kd_hybrid/yolo11_tiny_hybrid_full_seed42/weights/best.pt"
OUTPUT = ROOT / "runs/kd_diagnosis/20261023_heads_val_batch16.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branches(model: torch.nn.Module, images: torch.Tensor) -> dict:
    model.eval()
    with torch.no_grad():
        output = model(images)
    raw = output[1] if isinstance(output, tuple) else output
    if isinstance(raw, dict) and "one2many" in raw:
        return {key: raw[key] for key in ("one2many", "one2one")}
    if isinstance(raw, dict) and {"boxes", "scores"}.issubset(raw):
        return {"one2many": raw}
    raise RuntimeError(f"Unexpected raw head output: {type(raw).__name__}")


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUTPUT}")
    torch.set_num_threads(8)
    split = json.loads(FINGERPRINT.read_text(encoding="utf-8"))["splits"]["val"]
    chosen = sorted(split["files"], key=lambda item: item["image"])[:16]
    images = []
    for record in chosen:
        path = Path(split["images_dir"]) / record["image"]
        if digest(path) != record["image_sha256"]:
            raise RuntimeError(f"VAL image hash mismatch: {path}")
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError(f"Could not decode {path}")
        image = cv2.resize(image, (640, 640), interpolation=cv2.INTER_LINEAR)
        images.append(torch.from_numpy(image[:, :, ::-1].copy()).permute(2, 0, 1))
    batch = torch.stack(images).float() / 255.0
    teacher_model = YOLO(str(TEACHER), task="detect").model.float().cpu()
    student_model = YOLO(str(STUDENT), task="detect").model.float().cpu()
    teacher_head = branches(teacher_model, batch)
    student_head = branches(student_model, batch)
    reg_teacher = int(teacher_model.model[-1].reg_max)
    reg_student = int(student_model.model[-1].reg_max)
    tau = 2.0
    result = {
        "scope": "one fixed batch of 16 Roboflow VAL images; raw head diagnosis only",
        "preprocessing": "OpenCV BGR decode, direct resize 640x640, RGB conversion, float32 divided by 255; diagnostic, not exact Ultralytics rect VAL preprocessing",
        "VAL_fingerprint_sha256": split["split_fingerprint_sha256"],
        "images": [item["image"] for item in chosen],
        "teacher_checkpoint_sha256": digest(TEACHER),
        "student_checkpoint_sha256": digest(STUDENT),
        "teacher_reg_max": reg_teacher,
        "student_reg_max": reg_student,
        "branches": {},
    }
    if set(teacher_head) != set(student_head):
        raise RuntimeError("Teacher/student Detect branches differ")
    for name in teacher_head:
        t, s = teacher_head[name], student_head[name]
        tb, sb = t["boxes"].float(), s["boxes"].float()
        tc, sc = t["scores"].float(), s["scores"].float()
        if tb.shape != sb.shape or tc.shape != sc.shape:
            raise RuntimeError(f"Teacher/student raw Detect shapes differ: {name}")
        score = tc.sigmoid().amax(dim=1)
        targets = torch.sigmoid(tc / tau)
        result["branches"][name] = {
            "teacher_boxes_shape": list(tb.shape),
            "student_boxes_shape": list(sb.shape),
            "teacher_scores_shape": list(tc.shape),
            "student_scores_shape": list(sc.shape),
            "boxes_channels_equal_4_reg_max": tb.shape[1] == 4 * reg_teacher,
            "anchors_per_image": int(tb.shape[-1]),
            "teacher_anchor_fraction_score_gt_0_05": float((score > 0.05).float().mean()),
            "teacher_anchor_fraction_score_gt_0_25": float((score > 0.25).float().mean()),
            "teacher_anchor_fraction_score_gt_0_50": float((score > 0.50).float().mean()),
            "raw_box_smooth_l1_mean": float(F.smooth_l1_loss(sb, tb)),
            "class_soft_BCE_tau2_mean": float(F.binary_cross_entropy_with_logits(sc / tau, targets) * tau**2),
            "class_soft_BCE_equal_teacher_tau2_mean": float(F.binary_cross_entropy_with_logits(tc / tau, targets) * tau**2),
        }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
