#!/usr/bin/env python3
"""05_extract_corpus.py — extract plain text from PDF and HTML corpus documents.

Sprint 0 use: process data/corpus_pilot/raw/{doc_id}.{pdf,html} into
data/corpus_pilot/processed/{doc_id}.txt for downstream sentence splitting.

PDF: pdfminer.six (same engine as 04_pdf_to_text.py).
HTML: trafilatura (mainstream, boilerplate stripping).

Usage
-----
python scripts/02_pipeline/05_extract_corpus.py            # all files in raw/
python scripts/02_pipeline/05_extract_corpus.py --country KR
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

try:
    from pdfminer.high_level import extract_text as pdf_extract
except ImportError:
    sys.stderr.write("[error] pdfminer.six not installed. pip install -r requirements.txt\n")
    sys.exit(1)

try:
    import trafilatura
except ImportError:
    sys.stderr.write("[error] trafilatura not installed. pip install -r requirements.txt\n")
    sys.exit(1)

try:
    import docx  # python-docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

REPO = Path(__file__).resolve().parents[2]

CORPUS_PATHS = {
    "pilot": {
        "csv": REPO / "data" / "corpus_inventory" / "pilot_urls.csv",
        "raw": REPO / "data" / "corpus_pilot" / "raw",
        "out": REPO / "data" / "corpus_pilot" / "processed",
    },
    "full": {
        "csv": REPO / "data" / "corpus_inventory" / "sprint1_urls.csv",
        "raw": REPO / "data" / "corpus_full" / "raw",
        "out": REPO / "data" / "corpus_full" / "processed",
    },
    "negative": {
        "csv": REPO / "data" / "corpus_inventory" / "negative_urls.csv",
        "raw": REPO / "data" / "corpus_negative" / "raw",
        "out": REPO / "data" / "corpus_negative" / "processed",
    },
}

# Defaults (back-compat with pilot scripts)
CSV_PATH = CORPUS_PATHS["pilot"]["csv"]
RAW_DIR = CORPUS_PATHS["pilot"]["raw"]
OUT_DIR = CORPUS_PATHS["pilot"]["out"]


def normalise(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    # collapse trailing/leading whitespace per line
    lines = [ln.strip() for ln in text.split("\n")]
    return "\n".join(lines).strip() + "\n"


def extract_pdf(path: Path) -> str:
    return normalise(pdf_extract(str(path)))


def extract_html(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    text = trafilatura.extract(
        raw,
        include_comments=False,
        include_tables=True,
        include_images=False,
        include_links=False,
        favor_recall=True,
    )
    if not text:
        # trafilatura sometimes returns None; fall back to bare strip
        text = trafilatura.html2txt(raw)
    return normalise(text or "")


def extract_docx(path: Path) -> str:
    """Extract text from a .docx file using python-docx.

    Used for files manually downloaded by the user from publishers that
    serve their flagship document as a Word file (e.g. Australian DfE).
    """
    if not DOCX_AVAILABLE:
        raise RuntimeError("python-docx not installed; pip install python-docx")
    d = docx.Document(str(path))
    paragraphs = [p.text for p in d.paragraphs if p.text.strip()]
    return normalise("\n\n".join(paragraphs))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--country", default="", help="ISO2 filter (e.g. KR)")
    parser.add_argument("--corpus", default="pilot", choices=["pilot", "full", "negative"],
                        help="which corpus to process (pilot=5-country, full=25-country, negative=discriminant-validity)")
    args = parser.parse_args()

    paths = CORPUS_PATHS[args.corpus]
    csv_path = paths["csv"]
    raw_dir = paths["raw"]
    out_dir = paths["out"]

    if not csv_path.exists():
        sys.stderr.write(f"[error] {csv_path} not found\n")
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    n_ok = n_skip = n_fail = 0
    print(f"{'doc_id':<8s}  {'fmt':<5s}  {'in_kb':>7s}  {'out_chars':>10s}  status")
    for r in rows:
        # iso2 filter is policy-corpus only; negative corpus has no iso2 column.
        if args.country and r.get("iso2", "") != args.country:
            continue
        doc_id = r["doc_id"]
        fmt = r["format"]
        raw_path = raw_dir / f"{doc_id}.{fmt}"
        out_path = out_dir / f"{doc_id}.txt"

        # Skip rows flagged DROP: in the URL (e.g. CN-03 scanned PDF requires
        # zh tessdata not available in this sandbox; documented limitation).
        if r.get("url", "").startswith("DROP:"):
            print(f"{doc_id:<8s}  {fmt:<5s}  {'--':>7s}  {'--':>10s}  dropped")
            n_skip += 1
            continue

        if not raw_path.exists():
            print(f"{doc_id:<8s}  {fmt:<5s}  {'--':>7s}  {'--':>10s}  missing")
            n_skip += 1
            continue

        # If a sub-sampled variant has been produced (e.g. US-01_full.txt
        # backup created by 05a_subsample_us01.py), keep the current sliced
        # processed/{doc_id}.txt rather than overwriting it from the raw PDF.
        if (out_dir / f"{doc_id}_full.txt").exists():
            existing = out_dir / f"{doc_id}.txt"
            sz = existing.stat().st_size if existing.exists() else 0
            print(f"{doc_id:<8s}  {fmt:<5s}  {'--':>7s}  {sz:>10,d}  preserved_subsample")
            n_skip += 1
            continue

        # If a sentinel OCR'd variant exists (e.g. MX-01_pdfminer_broken.txt
        # marks that 05b_ocr_mx01.sh replaced the broken pdfminer output
        # with tesseract-OCR'd text), preserve the existing .txt.
        if (out_dir / f"{doc_id}_pdfminer_broken.txt").exists():
            existing = out_dir / f"{doc_id}.txt"
            sz = existing.stat().st_size if existing.exists() else 0
            print(f"{doc_id:<8s}  {fmt:<5s}  {'--':>7s}  {sz:>10,d}  preserved_ocr")
            n_skip += 1
            continue

        in_kb = raw_path.stat().st_size // 1024
        try:
            if fmt == "pdf":
                text = extract_pdf(raw_path)
            elif fmt == "html":
                text = extract_html(raw_path)
            elif fmt == "docx":
                text = extract_docx(raw_path)
            else:
                print(f"{doc_id:<8s}  {fmt:<5s}  {in_kb:>7d}  {'--':>10s}  unsupported_fmt")
                n_fail += 1
                continue
        except Exception as exc:  # noqa: BLE001
            print(f"{doc_id:<8s}  {fmt:<5s}  {in_kb:>7d}  {'--':>10s}  err: {exc}")
            n_fail += 1
            continue

        tmp = out_path.with_suffix(".txt.tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(out_path)
        print(f"{doc_id:<8s}  {fmt:<5s}  {in_kb:>7d}  {len(text):>10,d}  ok")
        n_ok += 1

    print(f"\n[summary] ok={n_ok}  skip={n_skip}  fail={n_fail}")
    # Always return 0 so downstream pipeline steps proceed.
    # Failed extractions are logged above and re-flagged in sentence-split
    # (missing .txt → skipped). Hard-stopping on partial fails is too
    # brittle for 60+ document Sprint 1 runs.
    return 0


if __name__ == "__main__":
    sys.exit(main())
