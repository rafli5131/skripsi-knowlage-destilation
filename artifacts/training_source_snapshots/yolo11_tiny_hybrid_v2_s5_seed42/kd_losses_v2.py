"""Detection-head losses for the additive hybrid_v2 research mode."""

from __future__ import annotations

import torch
import torch.nn.functional as F


def hybrid_v2_head_losses(
    teacher_boxes: torch.Tensor,
    student_boxes: torch.Tensor,
    teacher_logits: torch.Tensor,
    student_logits: torch.Tensor,
    *,
    box_kd: str,
    box_tau: float,
    box_fg_weighting: str,
    class_kd_weighting: str,
    class_floor_alpha: float,
    temperature: float,
    reg_max: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return mean box and soft-target class KD losses; teacher has no gradient."""
    if teacher_boxes.shape != student_boxes.shape or teacher_logits.shape != student_logits.shape:
        raise ValueError("Teacher/student Detect output shapes differ")
    if teacher_boxes.ndim != 3 or teacher_logits.ndim != 3:
        raise ValueError("Detect outputs must have [batch, channels, locations] shape")
    if teacher_boxes.shape[0] != teacher_logits.shape[0] or teacher_boxes.shape[-1] != teacher_logits.shape[-1]:
        raise ValueError("Box and class outputs have different batch or anchor counts")
    if box_kd not in {"smooth_l1", "kl_dfl"}:
        raise ValueError(f"Unsupported box_kd: {box_kd}")
    if box_fg_weighting not in {"none", "teacher_score"}:
        raise ValueError(f"Unsupported box_fg_weighting: {box_fg_weighting}")
    if class_kd_weighting not in {"none", "floor"}:
        raise ValueError(f"Unsupported class_kd_weighting: {class_kd_weighting}")
    if box_tau <= 0 or temperature <= 0 or not 0 <= class_floor_alpha <= 1:
        raise ValueError("Temperatures must be positive and class_floor_alpha must be in [0, 1]")

    teacher_boxes = teacher_boxes.detach().float()
    student_boxes = student_boxes.float()
    teacher_logits = teacher_logits.detach().float()
    student_logits = student_logits.float()
    attention = teacher_logits.sigmoid().amax(dim=1)

    if box_kd == "smooth_l1":
        box_per_anchor = F.smooth_l1_loss(student_boxes, teacher_boxes, reduction="none").mean(dim=1)
    else:
        if reg_max < 2 or teacher_boxes.shape[1] != 4 * reg_max:
            raise ValueError("KL-DFL requires 4 * reg_max raw box logits")
        b, _, a = student_boxes.shape
        teacher_distribution = (teacher_boxes.reshape(b, 4, reg_max, a) / box_tau).softmax(dim=2)
        student_log_distribution = (student_boxes.reshape(b, 4, reg_max, a) / box_tau).log_softmax(dim=2)
        box_per_anchor = (
            F.kl_div(student_log_distribution, teacher_distribution, reduction="none")
            .sum(dim=2).mean(dim=1) * box_tau**2
        )
    if box_fg_weighting == "teacher_score":
        box_loss = (box_per_anchor * attention).sum() / attention.sum().clamp_min(1e-9)
    else:
        box_loss = box_per_anchor.mean()

    class_per_anchor = (
        F.binary_cross_entropy_with_logits(
            student_logits / temperature, (teacher_logits / temperature).sigmoid(), reduction="none"
        ).mean(dim=1) * temperature**2
    )
    if class_kd_weighting == "floor":
        weights = class_floor_alpha + (1 - class_floor_alpha) * attention
        class_loss = (class_per_anchor * weights).sum() / weights.sum().clamp_min(1e-9)
    else:
        class_loss = class_per_anchor.mean()
    return box_loss, class_loss
