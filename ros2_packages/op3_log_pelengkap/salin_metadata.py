#!/usr/bin/env python3
"""Kumpulkan metadata capture T38/T43 dan berkas teks training teacher di OP3.

Dijalankan di komputer OP3 dari root repositori robot, hanya dengan pustaka
standar. Skrip membaca berkas dan menyalin berkas metadata yang lolos
pemeriksaan isi ke direktori keluaran baru (direktori kerja sementara). Tidak
ada berkas di repositori robot atau folder teacher yang ditulis, dipindahkan,
atau dihapus.

Yang tidak pernah disalin: gambar, contact sheet, folder ``images/`` dan
``labels_*``, label YOLO, prediksi per frame, berkas ``.pt``, dan kode. Berkas
JSON/JSONL/CSV/TXT kandidat diperiksa dulu; bila memuat koordinat kotak, prediksi
per frame, atau data gambar tersandi, berkas itu dicatat sebagai "tidak disalin
karena memuat label atau prediksi".
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import platform
import re
import shutil
import socket
import sys
from pathlib import Path

T38_RUN = Path("runs/op3_multi_session_eval/20261105_empat_model_primary260_v1")
T43_DIR = Path("data/op3_camera_eval/experiments/t43_20261112")
SESSIONS = Path("data/op3_camera_eval/sessions")
EKSTENSI = {".json", ".jsonl", ".csv", ".txt"}
FOLDER_DILEWATI = ("images", "labels_auto", "labels_reviewed", "labels_blind_snapshot_before_qa")
KUNCI_KOORDINAT = {"bbox", "box", "boxes", "xyxy", "xywh", "xyxyn", "xywhn", "x1", "y1", "x2", "y2",
                   "x_center", "y_center", "cx", "cy", "polygon", "points", "segments", "xmin", "ymin",
                   "xmax", "ymax"}
KUNCI_PREDIKSI = {"predictions", "prediction", "detections", "detection", "pred", "preds"}
BARIS_YOLO = re.compile(r"^\s*\d+(\s+-?\d*\.?\d+(e-?\d+)?){4,}\s*$", re.MULTILINE)
BASE64 = re.compile(r"^[A-Za-z0-9+/=\s]{2000,}$")
TEACHER_TEKS = ("manifest.json", "args.yaml", "results.csv", "SHA256SUMS.txt")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def temuan_isi(obj, temuan: set[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            k = str(key).lower()
            if k in KUNCI_KOORDINAT and value not in (None, [], {}, ""):
                temuan.add(f"kunci koordinat '{key}'")
            if k in KUNCI_PREDIKSI and isinstance(value, (list, dict)) and value:
                temuan.add(f"kunci prediksi '{key}'")
            temuan_isi(value, temuan)
    elif isinstance(obj, list):
        for value in obj:
            temuan_isi(value, temuan)
    elif isinstance(obj, str):
        if "data:image" in obj:
            temuan.add("data gambar tersandi (data:image)")
        elif BASE64.match(obj):
            temuan.add("string panjang mirip base64")
        elif BARIS_YOLO.search(obj):
            temuan.add("baris label YOLO di dalam string")


def periksa_isi(path: Path) -> list[str]:
    """Kembalikan daftar alasan berkas tidak boleh disalin; kosong berarti boleh."""
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return ["bukan teks UTF-8"]
    temuan: set[str] = set()
    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            temuan_isi(json.loads(text), temuan)
        elif suffix == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    temuan_isi(json.loads(line), temuan)
        elif suffix == ".csv":
            header = next(csv.reader(io.StringIO(text)), [])
            cols = {c.strip().lower() for c in header}
            if cols & KUNCI_KOORDINAT:
                temuan.add(f"kolom koordinat {sorted(cols & KUNCI_KOORDINAT)}")
            if cols & {"confidence", "score", "conf"} and cols & {"class", "class_name", "cls"}:
                temuan.add("kolom prediksi (kelas dan confidence)")
        else:
            if BARIS_YOLO.search(text):
                temuan.add("baris label YOLO")
    except (json.JSONDecodeError, csv.Error) as exc:
        return [f"gagal diurai: {type(exc).__name__}"]
    return sorted(temuan)


def kumpulkan_sesi(repo: Path, session_id: str, tujuan: Path, laporan: dict) -> dict:
    folder = repo / SESSIONS / session_id
    hasil = {"session_id": session_id, "path": str(folder), "ada": folder.is_dir(), "disalin": [],
             "tidak_disalin": []}
    if not folder.is_dir():
        return hasil
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        rel = path.relative_to(folder)
        di_folder_dilewati = rel.parts[0] in FOLDER_DILEWATI if len(rel.parts) > 1 else False
        if path.suffix.lower() not in EKSTENSI:
            if not di_folder_dilewati:
                hasil["tidak_disalin"].append({"berkas": str(rel), "alasan": "bukan metadata teks (gambar atau lainnya)"})
            continue
        if di_folder_dilewati and path.suffix.lower() == ".txt" and rel.parts[0].startswith("labels"):
            continue  # label YOLO per frame; dihitung saja
        alasan = periksa_isi(path)
        if di_folder_dilewati:
            alasan = alasan or ["berada di folder label; tidak disalin"]
        if alasan:
            hasil["tidak_disalin"].append({"berkas": str(rel), "sha256": sha256(path), "alasan": alasan})
            continue
        target = tujuan / session_id / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        hasil["disalin"].append({"berkas": str(rel), "sumber": str(path), "sha256": sha256(path),
                                 "bytes": path.stat().st_size, "salinan_sha256": sha256(target)})
    label_txt = sum(1 for p in folder.glob("labels_*/*.txt"))
    hasil["jumlah_label_txt_tidak_disalin"] = label_txt
    hasil["jumlah_gambar_tidak_disalin"] = sum(1 for p in folder.rglob("*") if p.suffix.lower() in (".jpg", ".png"))
    cm = folder / "capture_manifest.json"
    if cm.is_file():
        hasil["capture_manifest"] = json.loads(cm.read_text(encoding="utf-8"))
        hasil["capture_manifest_sha256"] = sha256(cm)
    cf = folder / "capture_frames.jsonl"
    if cf.is_file():
        hasil["capture_frames_sha256"] = sha256(cf)
        hasil["capture_frames"] = {json.loads(l)["image"]: json.loads(l).get("captured_at_utc")
                                   for l in cf.read_text(encoding="utf-8").splitlines() if l.strip()}
    return hasil


def bagian_t38(repo: Path, out: Path) -> dict:
    manifest_path = repo / T38_RUN / "input_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    used: dict[str, list[str]] = {}
    for frame in manifest["frames"].values():
        used.setdefault(frame["session"], []).append(Path(frame["image"]).name)
    sesi = {}
    for session_id, info in manifest["sessions"].items():
        hasil = kumpulkan_sesi(repo, session_id, out / "t38_capture", {})
        hasil["peran_t38"] = info.get("role")
        hasil["jumlah_frame_t38"] = info.get("image_count")
        hasil["frame_dipakai"] = sorted(used.get(session_id, []))
        sesi[session_id] = hasil
    # Sesi kurasi (bukan capture asli) merujuk sesi sumber; metadata sesi sumber ikut
    # dikumpulkan agar waktu capture frame kurasi dapat ditelusuri dari jurnalnya.
    for session_id in list(sesi):
        sumber = sesi[session_id].get("capture_manifest", {}).get("source_sessions", [])
        for source_id in sumber:
            if source_id in sesi:
                continue
            hasil = kumpulkan_sesi(repo, source_id, out / "t38_capture", {})
            hasil["peran_t38"] = f"sumber_kurasi:{session_id}"
            hasil["jumlah_frame_t38"] = 0
            hasil["frame_dipakai"] = []
            sesi[source_id] = hasil
    return {"input_manifest": {"path": str(manifest_path), "sha256": sha256(manifest_path),
                               "created_at_utc": manifest.get("created_at_utc"), "status": manifest.get("status")},
            "sesi": sesi}


def bagian_t43(repo: Path, out: Path) -> dict:
    exp = repo / T43_DIR
    tujuan = out / "t43_capture"
    tujuan.mkdir(parents=True, exist_ok=True)
    berkas = {"disalin": [], "tidak_disalin": []}
    for path in sorted(p for p in exp.rglob("*") if p.is_file()):
        rel = path.relative_to(exp)
        if any(part in FOLDER_DILEWATI for part in rel.parts[:-1]):
            continue  # gambar dan label tinjauan buta
        if rel.name == "frozen_plan.json":
            berkas["tidak_disalin"].append({"berkas": str(rel), "sha256": sha256(path), "alasan": ["sudah ada di Git"]})
            continue
        if path.suffix.lower() not in EKSTENSI:
            berkas["tidak_disalin"].append({"berkas": str(rel), "sha256": sha256(path),
                                            "alasan": ["bukan metadata (kode atau berkas lain)"]})
            continue
        alasan = periksa_isi(path)
        if alasan:
            berkas["tidak_disalin"].append({"berkas": str(rel), "sha256": sha256(path), "alasan": alasan})
            continue
        target = tujuan / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        berkas["disalin"].append({"berkas": str(rel), "sumber": str(path), "sha256": sha256(path),
                                  "bytes": path.stat().st_size, "salinan_sha256": sha256(target)})
    capture = json.loads((exp / "capture_260_manifest.json").read_text(encoding="utf-8"))
    sesi = {}
    for item in capture["sessions"]:
        hasil = kumpulkan_sesi(repo, item["session"], tujuan / "sesi", {})
        hasil["peran_t43"] = item.get("role")
        hasil["jumlah_frame_t43"] = item.get("count")
        hasil["frame_dipakai"] = sorted(item.get("images", {}))
        hasil["capture_manifest_sha256_menurut_t43"] = item.get("capture_manifest_sha256")
        hasil["capture_log_sha256_menurut_t43"] = item.get("capture_log_sha256")
        sesi[item["session"]] = hasil
    for session_id in capture.get("excluded_archived_sessions", []):
        hasil = kumpulkan_sesi(repo, session_id, tujuan / "sesi", {})
        hasil["peran_t43"] = "dikecualikan_diarsipkan"
        hasil["jumlah_frame_t43"] = 0
        hasil["frame_dipakai"] = []
        sesi[session_id] = hasil
    return {"berkas_eksperimen": berkas, "capture_260_created_utc": capture.get("created_utc"), "sesi": sesi}


def bagian_teacher(dirs: list[Path], out: Path) -> dict:
    hasil = {"folder": {}}
    tujuan = out / "teacher_training"
    for folder in dirs:
        entri = {"ada": folder.is_dir(), "berkas": []}
        if folder.is_dir():
            for path in sorted(p for p in folder.iterdir() if p.is_file()):
                entri["berkas"].append({"nama": path.name, "bytes": path.stat().st_size, "sha256": sha256(path),
                                        "mtime_utc": dt.datetime.fromtimestamp(path.stat().st_mtime,
                                                                               dt.timezone.utc).isoformat()})
        hasil["folder"][str(folder)] = entri
    utama = dirs[0]
    hasil["disalin"] = []
    for name in TEACHER_TEKS:
        path = utama / name
        if path.is_file():
            tujuan.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, tujuan / name)
            hasil["disalin"].append({"berkas": name, "sumber": str(path), "sha256": sha256(path),
                                     "bytes": path.stat().st_size, "salinan_sha256": sha256(tujuan / name)})
    return hasil


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True, help="Direktori keluaran baru di luar repositori")
    parser.add_argument("--teacher-dir", type=Path, action="append", required=True,
                        help="Folder teacher; yang pertama menjadi sumber salinan berkas teks")
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    if out.exists():
        raise SystemExit(f"Direktori keluaran sudah ada dan tidak akan ditimpa: {out}")
    if out == repo or repo in out.parents or any(d.resolve() in (out, *out.parents) for d in args.teacher_dir):
        raise SystemExit("Direktori keluaran tidak boleh berada di dalam repositori atau folder teacher")
    out.mkdir(parents=True)
    status = {
        "dibuat_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "hostname": socket.gethostname(), "python": platform.python_version(), "repo": str(repo),
        "skrip": str(Path(__file__).resolve()), "skrip_sha256": sha256(Path(__file__).resolve()),
        "t38": bagian_t38(repo, out), "t43": bagian_t43(repo, out),
        "teacher": bagian_teacher([d.resolve() for d in args.teacher_dir], out),
    }
    (out / "status_metadata.json").write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n",
                                              encoding="utf-8")
    ringkas = {
        "t38_sesi": len(status["t38"]["sesi"]),
        "t38_berkas_disalin": sum(len(s["disalin"]) for s in status["t38"]["sesi"].values()),
        "t43_sesi": len(status["t43"]["sesi"]),
        "t43_berkas_eksperimen_disalin": len(status["t43"]["berkas_eksperimen"]["disalin"]),
        "teacher_disalin": [b["berkas"] for b in status["teacher"]["disalin"]],
    }
    print(json.dumps(ringkas, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
