"""Pulihkan label poligon hasil ekspor ulang Roboflow menjadi kotak pembatas.

Default hanya memeriksa (dry-run). Berkas hanya diubah dengan --apply, dan hanya bila
hasil konversi memiliki SHA-256 yang sama persis dengan hash yang dikunci di sidik jari.
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def polygon_to_box(raw):
    """Ganti tiap baris poligon dengan kotak pembatas (x pusat, y pusat, lebar, tinggi; 12 desimal)."""
    out, changed = [], 0
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) > 5 and (len(parts) - 1) % 2 == 0:
            xs = [float(v) for v in parts[1::2]]
            ys = [float(v) for v in parts[2::2]]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            values = ((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0)
            line = parts[0] + " " + " ".join(f"{v:.12f}" for v in values)
            changed += 1
        out.append(line)
    return ("\n".join(out) + "\n").encode("utf-8"), changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="folder dataset (isi $DATA)")
    parser.add_argument("--fingerprint", default="artifacts/advance_vision_dataset_fingerprint.json")
    parser.add_argument("--backup", default=None, help="folder cadangan label asli (default: <root>_backup_label_polygon)")
    parser.add_argument("--apply", action="store_true", help="tulis label hasil pemulihan")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    backup_root = Path(args.backup).resolve() if args.backup else root.parent / (root.name + "_backup_label_polygon")
    fingerprint = json.loads(Path(args.fingerprint).read_text(encoding="utf-8"))

    restorable, hopeless, bad_images, checked = [], [], [], 0
    for split, folder in (("train", "train"), ("val", "valid")):
        for item in fingerprint["splits"][split]["files"]:
            checked += 1
            image = root / folder / "images" / item["image"]
            label = root / folder / "labels" / item["label"]
            if sha_file(image) != item["image_sha256"]:
                bad_images.append(f"{folder}/images/{item['image']}")
            if sha_file(label) == item["label_sha256"]:
                continue
            new, changed = polygon_to_box(label.read_bytes())
            if changed and sha_bytes(new) == item["label_sha256"]:
                restorable.append((folder, label, new, item["label_sha256"], changed))
            else:
                hopeless.append(f"{folder}/labels/{item['label']}")

    print(f"Diperiksa {checked} pasang (TRAIN+VAL).")
    print(f"Gambar dengan hash beda: {len(bad_images)}")
    for name in bad_images[:5]:
        print("  ", name)
    print(f"Label beda yang bisa dipulihkan (hasil konversi cocok persis dengan hash terkunci): {len(restorable)}")
    for folder, label, _, locked, changed in restorable:
        print(f"   {folder}/labels/{label.name} ({changed} baris poligon) -> {locked}")
    print(f"Label beda yang TIDAK bisa dipulihkan dengan cara ini: {len(hopeless)}")
    for name in hopeless[:10]:
        print("  ", name)

    if not args.apply:
        print("Dry-run: tidak ada berkas yang diubah. Tambahkan --apply untuk menulis.")
        return 1 if (bad_images or hopeless) else 0
    if bad_images or hopeless:
        print("Ada selisih lain yang tidak bisa dipulihkan. Tidak ada berkas diubah. Berhenti dan laporkan.")
        return 2
    for folder, label, new, locked, _ in restorable:
        backup = backup_root / folder / label.name
        if backup.exists():
            print(f"Cadangan sudah ada, dilewati agar tidak menimpa: {backup}")
            return 3
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(label, backup)
        label.write_bytes(new)
        if sha_file(label) != locked:
            shutil.copy2(backup, label)
            print(f"Verifikasi gagal, label dikembalikan dari cadangan: {label}")
            return 4
        print(f"Dipulihkan dan terverifikasi: {label.name}; cadangan asli di {backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
