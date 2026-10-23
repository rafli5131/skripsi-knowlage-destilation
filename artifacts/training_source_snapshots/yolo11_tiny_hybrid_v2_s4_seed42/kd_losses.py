"""Teacher-only detection-head losses for the pure-weighted KD candidate."""

from __future__ import annotations

import torch
import torch.nn.functional as F


def pure_weighted_head_losses(
    teacher_boxes: torch.Tensor,
    student_boxes: torch.Tensor,
    teacher_logits: torch.Tensor,
    student_logits: torch.Tensor,
    temperature: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Weight each dense head location by the teacher's strongest class score.

    Inputs are raw Detect outputs shaped [batch, channels, locations]. The
    teacher's logits and box outputs are detached so only the student updates.
    Each loss is normalized by the total location weight and channel count,
    preserving the scale of the original mean reduction when weights are flat.
    """
    if temperature <= 0:
        raise ValueError("KD class temperature must be positive")
    if teacher_boxes.shape != student_boxes.shape or teacher_logits.shape != student_logits.shape:
        raise ValueError("Teacher/student Detect output shapes differ")
    if teacher_boxes.ndim != 3 or teacher_logits.ndim != 3:
        raise ValueError("Detect outputs must have [batch, channels, locations] shape")
    if teacher_boxes.shape[0] != teacher_logits.shape[0] or teacher_boxes.shape[-1] != teacher_logits.shape[-1]:
        raise ValueError("Teacher Detect box and class locations differ")

    teacher_boxes = teacher_boxes.detach().float()
    teacher_logits = teacher_logits.detach().float()
    student_boxes = student_boxes.float()
    student_logits = student_logits.float()
    attention = teacher_logits.sigmoid().amax(dim=1, keepdim=True)
    weight_sum = attention.sum().clamp_min(1e-9)

    box_elements = F.smooth_l1_loss(student_boxes, teacher_boxes, reduction="none")
    box_loss = (box_elements * attention).sum() / (weight_sum * box_elements.shape[1])

    soft_targets = torch.sigmoid(teacher_logits / temperature)
    class_elements = F.binary_cross_entropy_with_logits(
        student_logits / temperature, soft_targets, reduction="none"
    ) * (temperature**2)
    class_loss = (class_elements * attention).sum() / (weight_sum * class_elements.shape[1])
    return box_loss, class_loss
