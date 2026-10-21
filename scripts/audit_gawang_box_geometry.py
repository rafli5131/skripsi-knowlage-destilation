"""Audit geometri label TRAIN/VAL tanpa membaca split TEST."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import random
from pathlib import Path
from statistics import mean

import yaml
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
LOGGER = logging.getLogger(__name__)
QUANTILES = (5, 25, 50, 75, 95)


def percentile(values: list[float], percent: int) -> float | None:
    """Hitung persentil dengan interpolasi linear pada posisi (n-1)q."""
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def label_dir(image_dir: Path) -> Path:
    """Temukan direktori label yang sejajar dengan direktori gambar."""
    if image_dir.name != "images":
        raise ValueError(f"Path gambar harus berakhir dengan images: {image_dir}")
    return image_dir.parent / "labels"


def read_label(label_path: Path, image_path: Path, names: dict[int, str]) -> tuple[list[dict[str, object]], dict[int, int]]:
    """Baca satu label YOLO dan hitung geometri kotaknya."""
    per_class = {class_id: 0 for class_id in names}
    boxes: list[dict[str, object]] = []
    if not label_path.exists():
        return boxes, per_class
    for line_number, raw in enumerate(label_path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        parts = raw.split()
        if len(parts) != 5:
            raise ValueError(f"Format YOLO salah: {label_path}:{line_number}")
        class_id = int(parts[0])
        if class_id not in names:
            raise ValueError(f"Kelas tidak dikenal: {label_path}:{line_number}")
        x, y, width, height = map(float, parts[1:])
        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1):
            raise ValueError(f"Koordinat tidak valid: {label_path}:{line_number}")
        per_class[class_id] += 1
        boxes.append({"class": names[class_id], "image": image_path,
                      "xywh": (x, y, width, height), "width_px640": width * 640,
                      "height_px640": height * 640, "height_width_ratio": height / width,
                      "area_px640": width * height * 640 * 640})
    return boxes, per_class


def collect_split(image_dir: Path, names: dict[int, str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Baca label YOLO dan kumpulkan geometri serta jumlah kotak per gambar."""
    labels = label_dir(image_dir)
    if not image_dir.is_dir() or not labels.is_dir():
        raise FileNotFoundError(f"Gambar/label tidak ditemukan: {image_dir}, {labels}")
    image_paths = sorted(path for path in image_dir.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"})
    boxes: list[dict[str, object]] = []
    counts: list[dict[str, object]] = []
    for image_path in image_paths:
        label_path = labels / f"{image_path.stem}.txt"
        image_boxes, per_class = read_label(label_path, image_path, names)
        boxes.extend(image_boxes)
        for class_id, count in per_class.items():
            counts.append({"class": names[class_id], "count": count})
    LOGGER.info("%s: %d gambar, %d kotak", image_dir, len(image_paths), len(boxes))
    return boxes, counts


def collect_op3(root: Path, manifest_path: Path, names: dict[int, str]) -> dict[str, tuple[list[dict[str, object]], list[dict[str, object]]]]:
    """Audit set OP3 hanya setelah hash gambar, label, dan log cocok."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    groups: dict[str, tuple[list[dict[str, object]], list[dict[str, object]]]] = {
        "OP3_UTAMA": ([], []), "OP3_PARSIAL": ([], [])
    }
    for session, info in manifest["sessions"].items():
        review_hash = info.get("review_log_sha256")
        if review_hash:
            log_path = root / session / "review_log.jsonl"
            if not log_path.is_file() or hashlib.sha256(log_path.read_bytes()).hexdigest() != review_hash:
                raise ValueError(f"Hash log peninjau berbeda: {log_path}")
    for frame in manifest["frames"].values():
        if frame["role"] == "negative":
            continue
        session = root / frame["session"]
        image_path = session / "images" / Path(frame["image"]).name
        label_path = session / "labels_reviewed" / Path(frame["label"]).name
        for path, key in ((image_path, "image_sha256"), (label_path, "label_sha256")):
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != frame[key]:
                raise ValueError(f"Hash input OP3 berbeda: {path}")
        group = "OP3_UTAMA" if frame["role"] == "primary" else "OP3_PARSIAL"
        image_boxes, per_class = read_label(label_path, image_path, names)
        groups[group][0].extend(image_boxes)
        groups[group][1].extend({"class": names[class_id], "count": count} for class_id, count in per_class.items())
    return groups


def summary_rows(split: str, names: dict[int, str], boxes: list[dict[str, object]],
                 counts: list[dict[str, object]]) -> list[dict[str, object]]:
    """Ringkas jumlah dan distribusi kotak tiap kelas."""
    rows: list[dict[str, object]] = []
    for name in names.values():
        selected = [box for box in boxes if box["class"] == name]
        per_image = [int(row["count"]) for row in counts if row["class"] == name]
        for metric in ("count_per_image", "width_px640", "height_px640", "height_width_ratio", "area_px640"):
            values = [float(value) for value in per_image] if metric == "count_per_image" else [float(box[metric]) for box in selected]
            row: dict[str, object] = {"split": split, "class": name, "metric": metric,
                                      "n_images": len(per_image), "n_boxes": len(selected),
                                      "mean": mean(values) if values else "[BELUM DIUKUR]"}
            row.update({f"p{q:02d}": percentile(values, q) if values else "[BELUM DIUKUR]" for q in QUANTILES})
            rows.append(row)
    return rows


def make_contact_sheet(boxes: list[dict[str, object]], output: Path, seed: int) -> int:
    """Buat lembar 30 potongan kotak gawang TRAIN yang dipilih acak."""
    choices = [box for box in boxes if box["class"] == "gawang"]
    selected = random.Random(seed).sample(choices, k=min(30, len(choices)))
    sheet = Image.new("RGB", (6 * 192, 5 * 160), "white")
    draw = ImageDraw.Draw(sheet)
    for index, box in enumerate(selected):
        with Image.open(Path(box["image"])) as image:
            image = image.convert("RGB")
            x, y, w, h = box["xywh"]
            left = max(0, round((x - w / 2) * image.width))
            top = max(0, round((y - h / 2) * image.height))
            right = min(image.width, round((x + w / 2) * image.width))
            bottom = min(image.height, round((y + h / 2) * image.height))
            if right <= left or bottom <= top:
                raise ValueError(f"Kotak kosong: {box['image']}")
            crop = image.crop((left, top, right, bottom))
            crop.thumbnail((184, 132))
            col, row = index % 6, index // 6
            sheet.paste(crop, (col * 192 + (192 - crop.width) // 2, row * 160))
            draw.text((col * 192 + 4, row * 160 + 135), f"{index + 1:02d} {Path(box['image']).stem[:20]}", fill="black")
    sheet.save(output, quality=90)
    return len(selected)


def main() -> None:
    """Jalankan audit TRAIN/VAL dan tulis CSV, gambar, serta ringkasan."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/data_train_val.yaml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "analisis_performa/lab_server")
    parser.add_argument("--date", default="2026-10-21")
    parser.add_argument("--seed", type=int, default=20261021)
    parser.add_argument("--op3-root", type=Path, default=ROOT / "data/op3_camera_eval/sessions")
    parser.add_argument("--op3-manifest", type=Path, default=ROOT / "runs/op3_multi_session_eval/20261021_primary260_partial50_v1/input_manifest.json")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    names = {int(key): str(value) for key, value in config["names"].items()}
    if names.get(1) != "gawang":
        raise ValueError("Kelas 1 pada konfigurasi harus gawang")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, object]] = []
    train_boxes: list[dict[str, object]] = []
    for split, key in (("TRAIN", "train"), ("VAL", "val")):
        boxes, counts = collect_split(Path(config[key]), names)
        all_rows.extend(summary_rows(split, names, boxes, counts))
        if split == "TRAIN":
            train_boxes = boxes
    if args.op3_root.is_dir():
        for split, (boxes, counts) in collect_op3(args.op3_root, args.op3_manifest, names).items():
            all_rows.extend(summary_rows(split, names, boxes, counts))
        op3_note = "Hash gambar, label, dan log peninjau cocok dengan manifest. Statistik OP3 utama dan parsial dipisah pada CSV."
    else:
        op3_note = (
            "[BELUM DIUKUR]. Gambar dan `labels_reviewed/` OP3 tidak ada di server. "
            "`per_frame_*.jsonl` menyimpan jumlah GT dan kotak prediksi, sedangkan `results.json` "
            "menyimpan ringkasan; keduanya tidak menyimpan koordinat GT. Setelah data disalin ke "
            "`data/op3_camera_eval/sessions/`, jalankan kembali "
            "`env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python "
            "scripts/audit_gawang_box_geometry.py`; skrip akan memverifikasi hash manifest terlebih dahulu."
        )
    csv_path = args.output_dir / f"AUDIT_DEFINISI_GAWANG_{args.date}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(all_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_rows)
    sheet_path = args.output_dir / f"AUDIT_DEFINISI_GAWANG_{args.date}_30_crop.jpg"
    count = make_contact_sheet(train_boxes, sheet_path, args.seed)
    md_path = args.output_dir / f"AUDIT_DEFINISI_GAWANG_{args.date}.md"
    md_path.write_text(
        f"# Audit definisi kotak gawang, {args.date}\n\n"
        f"Sumber: `{args.config}`; hanya split TRAIN dan VAL. Kelas: `{names}`. "
        "Ukuran piksel adalah koordinat label yang dinormalkan ke kanvas 640 × 640, "
        "bukan ukuran piksel asli gambar. Jumlah kotak per gambar mencakup gambar tanpa kelas tersebut. "
        "Persentil memakai interpolasi linear pada posisi (n-1)q.\n\n"
        f"[Statistik lengkap](AUDIT_DEFINISI_GAWANG_{args.date}.csv) memuat jumlah kotak, "
        "rerata, dan persentil 5, 25, 50, 75, 95 tiap kelas dan split.\n\n"
        f"![{count} potongan kotak gawang TRAIN](AUDIT_DEFINISI_GAWANG_{args.date}_30_crop.jpg)\n\n"
        f"## Data OP3\n\n{op3_note}\n\n"
        "## Batas interpretasi\n\nLembar potongan memperlihatkan isi kotak, tetapi keputusan "
        "apakah anotasi memakai satu tiang atau seluruh rangka perlu inspeksi gambar utuh dan pedoman label. "
        "Audit ini tidak membuktikan penyebab kegagalan deteksi.\n",
        encoding="utf-8",
    )
    LOGGER.info("Keluaran: %s, %s, %s", csv_path, sheet_path, md_path)


if __name__ == "__main__":
    main()
