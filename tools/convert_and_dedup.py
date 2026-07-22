#!/usr/bin/env python3
"""
convert_and_dedup.py — Pipeline di deduplica + conversione del corpus grezzo.

Scopo (industrializzazione dell'ingest, vedi CLAUDE.md / BLUEPRINT.md):
  1. Deduplica i file di raw/ per contenuto (sha256): utile perché le due
     cartelle originali si sovrappongono molto.
  2. Converte in testo i file unici:
       - .doc / .docx           -> textutil (nativo macOS)
       - .pdf                   -> pypdf (testo incorporato)
       - scansioni (pdf con poco/niente testo) -> flag needs_ocr (OCR in step successivo)
       - .pptx / altro          -> unsupported (per ora)
  3. Scrive il testo estratto in raw_text/<stesso percorso>.txt (proiezione
     machine-readable del Cerchio 1; NON è la wiki curata).
  4. Emette tools/manifest.csv + un riepilogo a video.

Uso:
  .venv/bin/python tools/convert_and_dedup.py            # tutto
  .venv/bin/python tools/convert_and_dedup.py --limit 50 # prova rapida
  .venv/bin/python tools/convert_and_dedup.py --dry-run  # solo analisi/dedup, nessuna scrittura
"""
from __future__ import annotations
import argparse, csv, hashlib, re, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw"
OUT_DIR = ROOT / "raw_text"
MANIFEST = ROOT / "tools" / "manifest.csv"

TEXTUTIL_EXTS = {".doc", ".docx"}
PDF_EXTS = {".pdf"}
PPTX_EXTS = {".pptx"}
UNSUPPORTED_EXTS = {".ppt"}
SKIP_NAMES = {".DS_Store"}
OCR_MIN_CHARS = 200          # sotto questa soglia un PDF è probabilmente una scansione
TEXTUTIL_TIMEOUT = 60


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_docx(path: Path) -> str:
    r = subprocess.run(
        ["textutil", "-convert", "txt", "-stdout", str(path)],
        capture_output=True, timeout=TEXTUTIL_TIMEOUT,
    )
    return r.stdout.decode("utf-8", "ignore")


def extract_pdf(path: Path) -> str:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def extract_pptx(path: Path) -> str:
    parts = []
    with zipfile.ZipFile(path) as z:
        slides = sorted(n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n))
        for n in slides:
            xml = z.read(n).decode("utf-8", "ignore")
            runs = re.findall(r"<a:t>(.*?)</a:t>", xml, flags=re.S)
            if runs:
                parts.append(" ".join(runs))
    return "\n\n".join(parts)


def classify_ext(ext: str) -> str:
    e = ext.lower()
    if e in TEXTUTIL_EXTS:
        return "textutil"
    if e in PDF_EXTS:
        return "pdf"
    if e in PPTX_EXTS:
        return "pptx"
    if e in UNSUPPORTED_EXTS:
        return "unsupported"
    return "unsupported"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="processa solo i primi N file")
    ap.add_argument("--dry-run", action="store_true", help="solo dedup/analisi, non scrive testo")
    args = ap.parse_args()

    if not RAW_DIR.is_dir():
        print(f"ERRORE: {RAW_DIR} non trovata", file=sys.stderr)
        return 1

    files = [p for p in sorted(RAW_DIR.rglob("*"))
             if p.is_file() and p.name not in SKIP_NAMES and not p.name.startswith("~$")]
    if args.limit:
        files = files[: args.limit]

    seen: dict[str, Path] = {}          # hash -> primo path (canonico)
    rows: list[dict] = []
    stats = {"converted": 0, "duplicate": 0, "needs_ocr": 0, "unsupported": 0, "error": 0}
    ext_counts: dict[str, int] = {}

    for i, path in enumerate(files, 1):
        rel = path.relative_to(RAW_DIR)
        ext = path.suffix.lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        size = path.stat().st_size
        try:
            digest = sha256_of(path)
        except Exception as e:
            rows.append(dict(path=str(rel), ext=ext, size=size, sha="", status="error",
                             chars=0, note=f"hash: {e}", duplicate_of=""))
            stats["error"] += 1
            continue

        if digest in seen:
            rows.append(dict(path=str(rel), ext=ext, size=size, sha=digest[:12],
                             status="duplicate", chars=0, note="",
                             duplicate_of=str(seen[digest].relative_to(RAW_DIR))))
            stats["duplicate"] += 1
            continue
        seen[digest] = path

        kind = classify_ext(ext)
        if kind == "unsupported":
            rows.append(dict(path=str(rel), ext=ext, size=size, sha=digest[:12],
                             status="unsupported", chars=0, note="conversione non supportata", duplicate_of=""))
            stats["unsupported"] += 1
            continue

        try:
            if kind == "textutil":
                text = extract_docx(path)
            elif kind == "pdf":
                text = extract_pdf(path)
            else:  # pptx
                text = extract_pptx(path)
        except Exception as e:
            rows.append(dict(path=str(rel), ext=ext, size=size, sha=digest[:12],
                             status="error", chars=0, note=str(e)[:200], duplicate_of=""))
            stats["error"] += 1
            continue

        chars = len(text.strip())
        if kind == "pdf" and chars < OCR_MIN_CHARS:
            rows.append(dict(path=str(rel), ext=ext, size=size, sha=digest[:12],
                             status="needs_ocr", chars=chars, note="pdf con poco testo (scansione?)", duplicate_of=""))
            stats["needs_ocr"] += 1
            continue

        if not args.dry_run:
            out = OUT_DIR / rel
            out = out.with_suffix(out.suffix + ".txt")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
        rows.append(dict(path=str(rel), ext=ext, size=size, sha=digest[:12],
                         status="converted", chars=chars, note="", duplicate_of=""))
        stats["converted"] += 1

    # manifest
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "ext", "size", "sha", "status", "chars", "duplicate_of", "note"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # riepilogo
    total = len(files)
    unique = len(seen)
    print("=" * 60)
    print(f"File totali (esclusi .DS_Store/lock): {total}")
    print(f"File unici (per contenuto sha256):   {unique}")
    print(f"Duplicati esatti:                    {stats['duplicate']}")
    print("-" * 60)
    print(f"  convertiti (testo estratto):       {stats['converted']}")
    print(f"  da OCR (pdf scansionati):          {stats['needs_ocr']}")
    print(f"  non supportati (pptx/altro):       {stats['unsupported']}")
    print(f"  errori:                            {stats['error']}")
    print("-" * 60)
    print("Estensioni:", ", ".join(f"{k or '(none)'}={v}" for k, v in sorted(ext_counts.items(), key=lambda x: -x[1])))
    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")
    if not args.dry_run:
        print(f"Testo estratto in: {OUT_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
