#!/usr/bin/env python3
"""Susun ``ringkasan_capture.csv`` dari ``status_metadata.json`` (dijalankan di laptop).

Timestamp capture diambil hanya dari jurnal ``capture_frames.jsonl``
(``captured_at_utc``). Untuk sesi kurasi, frame ditelusuri lewat
``curation_manifest.json`` (``source_session``/``source_image``) ke jurnal sesi
sumber. Bila tidak ada jurnal, kolom diisi ``tidak tercatat``; timestamp tidak
diturunkan dari nama berkas atau waktu modifikasi.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

KOLOM = ["set", "session_id", "peran", "kondisi", "jumlah_frame_dipakai", "jumlah_frame_capture",
         "capture_pertama_utc", "capture_terakhir_utc", "sumber_timestamp", "frame_tanpa_timestamp",
         "berkas_sumber", "sha256", "hash_manifest_cocok_dengan_t43"]


def rentang(times: list[str]) -> tuple[str, str]:
    return (min(times), max(times)) if times else ("tidak tercatat", "tidak tercatat")


def baris(setname: str, sid: str, s: dict, semua: dict, folder: Path) -> dict:
    cm = s.get("capture_manifest", {})
    journal = s.get("capture_frames")
    used = s.get("frame_dipakai", [])
    sumber_ts, missing = "tidak tercatat", ""
    times: list[str] = []
    if journal:
        targets = used or list(journal)
        times = [journal[f] for f in targets if journal.get(f)]
        missing = len(targets) - len(times)
        sumber_ts = "capture_frames.jsonl" + ("" if used else " (semua frame sesi)")
    elif (folder / sid / "curation_manifest.json").is_file():
        cur = json.loads((folder / sid / "curation_manifest.json").read_text(encoding="utf-8"))
        mapping = {f["image"]: (f["source_session"], f["source_image"]) for f in cur.get("frames", [])}
        targets = used or list(mapping)
        for frame in targets:
            src = mapping.get(frame)
            src_journal = semua.get(src[0], {}).get("capture_frames") if src else None
            if src_journal and src_journal.get(src[1]):
                times.append(src_journal[src[1]])
        missing = len(targets) - len(times)
        if times:
            sumber_ts = "curation_manifest.json -> capture_frames.jsonl sesi sumber"
    first, last = rentang(times)
    peran = s.get("peran_t38") or s.get("peran_t43") or ""
    jumlah = s.get("jumlah_frame_t38") if setname == "T38" else s.get("jumlah_frame_t43")
    cocok = ""
    if setname == "T43" and s.get("capture_manifest_sha256_menurut_t43"):
        cocok = str(s.get("capture_manifest_sha256") == s["capture_manifest_sha256_menurut_t43"]).lower()
    return {"set": setname, "session_id": sid, "peran": peran, "kondisi": cm.get("condition", "tidak tercatat"),
            "jumlah_frame_dipakai": jumlah, "jumlah_frame_capture": cm.get("frame_count", "tidak tercatat"),
            "capture_pertama_utc": first, "capture_terakhir_utc": last, "sumber_timestamp": sumber_ts,
            "frame_tanpa_timestamp": missing,
            "berkas_sumber": f"OP3: data/op3_camera_eval/sessions/{sid}/capture_manifest.json"
            if s.get("capture_manifest_sha256") else "tidak ditemukan",
            "sha256": s.get("capture_manifest_sha256", ""), "hash_manifest_cocok_dengan_t43": cocok}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=Path("log_op3_pelengkap"))
    args = parser.parse_args()
    status = json.loads((args.folder / "status_metadata.json").read_text(encoding="utf-8"))
    rows = []
    for setname, key, sub in (("T38", "t38", "t38_capture"), ("T43", "t43", "t43_capture/sesi")):
        sesi = status[key]["sesi"]
        for sid, s in sesi.items():
            rows.append(baris(setname, sid, s, sesi, args.folder / sub))
    out = args.folder / "ringkasan_capture.csv"
    with out.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=KOLOM, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} baris -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
