#!/usr/bin/env python3
"""Audit baca-saja hash SHA-256 pada manifest JSON terhadap berkas di repositori.

Untuk setiap pasangan path dan SHA-256 yang menunjuk ke berkas yang dilacak Git,
skrip mengelompokkan hasil menjadi: cocok, hanya beda akhir baris (CRLF/LF),
cocok dengan versi lama di riwayat Git, atau tidak ditemukan. Manifest dan berkas
sumber tidak diubah.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEX = re.compile(r"[0-9a-f]{64}")
PATH_KEYS = ("path", "file", "relative_path", "repo_path", "output", "source")
HASH_KEYS = ("sha256", "sha", "hash", "sha256_hex")


def git(*args: str, binary: bool = False):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False)
    return result.stdout if binary else result.stdout.decode("utf-8", "replace")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pairs(obj, found):
    if isinstance(obj, dict):
        pkey = next((k for k in PATH_KEYS if isinstance(obj.get(k), str)), None)
        hkey = next((k for k in HASH_KEYS if isinstance(obj.get(k), str) and HEX.fullmatch(obj[k])), None)
        if pkey and hkey:
            found.append((obj[pkey], obj[hkey]))
        for key, value in obj.items():
            if isinstance(value, str) and HEX.fullmatch(value) and ("/" in key or "." in key):
                found.append((key, value))
            pairs(value, found)
    elif isinstance(obj, list):
        for value in obj:
            pairs(value, found)


def resolve(manifest: str, path: str, tracked: set[str]) -> str | None:
    for base in ((ROOT / manifest).parent, ROOT):
        try:
            candidate = (base / path).resolve()
            relative = candidate.relative_to(ROOT).as_posix()
        except (ValueError, OSError):
            continue
        if relative in tracked and candidate.is_file():
            return relative
    return None


def classify(relative: str, expected: str, cache: dict) -> tuple[str, str]:
    data = (ROOT / relative).read_bytes()
    if digest(data) == expected:
        return "cocok", ""
    lf = data.replace(b"\r\n", b"\n")
    if expected in (digest(lf), digest(lf.replace(b"\n", b"\r\n"))):
        return "beda_akhir_baris", ""
    if relative not in cache:
        cache[relative] = git("log", "--format=%h", "--", relative).split()
    for commit in cache[relative]:
        blob = git("show", f"{commit}:{relative}", binary=True)
        blob_lf = blob.replace(b"\r\n", b"\n")
        if expected in (digest(blob), digest(blob_lf), digest(blob_lf.replace(b"\n", b"\r\n"))):
            return "versi_lama_di_git", commit
    return "tidak_ditemukan", ""


def main() -> int:
    stamp = dt.date.today().strftime("%Y%m%d")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output-prefix", type=Path,
                        default=ROOT / f"analisis_performa/AUDIT_HASH_MANIFEST_{stamp}")
    args = parser.parse_args()
    tracked = set(filter(None, git("ls-files").split("\n")))
    rows, cache = [], {}
    for manifest in sorted(tracked):
        if not manifest.endswith(".json") or manifest.startswith("runs/"):
            continue
        path = ROOT / manifest
        if path.stat().st_size > 5_000_000:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        found: list = []
        pairs(data, found)
        seen = set()
        for target, expected in found:
            relative = resolve(manifest, target, tracked)
            if relative is None or (relative, expected) in seen:
                continue
            seen.add((relative, expected))
            status, commit = classify(relative, expected, cache)
            rows.append([manifest, relative, expected, status, commit,
                         "arsip" if re.search(r"arsip|archive|sebelum", manifest, re.I) else "aktif"])
    header = ["manifest", "berkas", "sha256_tercatat", "status", "commit_versi_lama", "jenis_manifest"]
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows([header, *rows])
    csv_path = args.output_prefix.with_suffix(".csv")
    csv_path.write_bytes(buffer.getvalue().encode("utf-8"))

    totals = Counter(r[3] for r in rows)
    per_manifest = defaultdict(Counter)
    for r in rows:
        per_manifest[r[0]][r[3]] += 1
    problem = [(m, c) for m, c in sorted(per_manifest.items()) if c["tidak_ditemukan"] or c["versi_lama_di_git"]]
    lines = [f"| `{m}` | {c['cocok']} | {c['beda_akhir_baris']} | {c['versi_lama_di_git']} | {c['tidak_ditemukan']} |"
             for m, c in problem]
    unknown = [r for r in rows if r[3] == "tidak_ditemukan" and not r[1].endswith(".md")]
    unknown_lines = "\n".join(f"- `{r[1]}` (manifest `{r[0]}`)" for r in unknown) or "- tidak ada"
    md = f"""# Audit hash manifest repositori

Dibangkitkan oleh `scripts/audit_manifest_hashes.py` pada {dt.date.today().isoformat()}. Audit ini
baca-saja: manifest dan berkas sumber tidak diubah. Hanya pasangan path dan SHA-256 yang menunjuk ke
berkas yang dilacak Git yang diperiksa; berkas lokal robot atau server di luar Git tidak dihitung.

| Status | Jumlah | Arti |
|---|---:|---|
| `cocok` | {totals['cocok']} | Hash berkas saat ini sama dengan manifest |
| `beda_akhir_baris` | {totals['beda_akhir_baris']} | Isi sama; hanya akhir baris CRLF/LF yang berbeda |
| `versi_lama_di_git` | {totals['versi_lama_di_git']} | Manifest mencatat versi lama yang ada di riwayat Git; berkas diperbarui sesudah manifest ditulis |
| `tidak_ditemukan` | {totals['tidak_ditemukan']} | Versi yang di-hash tidak ditemukan di riwayat Git |

## Manifest dengan entri yang perlu dibaca hati-hati

| Manifest | Cocok | Beda akhir baris | Versi lama di Git | Tidak ditemukan |
|---|---:|---:|---:|---:|
{chr(10).join(lines)}

Sebagian besar entri `versi_lama_di_git` berasal dari `analisis_performa/manifest.json`. Bagian `tables`
manifest itu ditulis pada 19 Oktober 2026, ketika banyak tabel T02 sampai T26 masih berupa kerangka atau
penanda `[BELUM DIUKUR]`, dan tidak diperbarui ketika tabel diisi atau diberi kolom interval. Pada T05,
perubahan sejak versi tersebut berada di kolom interval bootstrap dan keterangan, bukan pada nilai rerata.
Berkas Markdown dengan status selain `cocok` umumnya README yang kemudian ditambah tautan.

## Berkas non-Markdown yang versinya tidak ditemukan

{unknown_lines}

Delapan belas PNG akurasi di `dokumentasi/model/` sudah dicatat pada
[audit grafik 12 November](../dokumentasi/2026-11-12/AUDIT_GRAFIK_AKURASI.md); versi reproduksi yang
terverifikasi ada di `dokumentasi/2026-11-12/grafik-akurasi-terverifikasi/`.

Rincian per entri: [`{csv_path.name}`]({csv_path.name}).
"""
    args.output_prefix.with_suffix(".md").write_bytes(md.encode("utf-8"))
    print(dict(totals))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
