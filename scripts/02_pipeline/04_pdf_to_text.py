#!/usr/bin/env python3
"""04_pdf_to_text.py — Convert source PDFs to plain-text.

Sprint 0 use: convert UNESCO student/teacher Framework PDFs and OECD/EC AILit
Review Draft PDF into UTF-8 text files for verbatim anchor extraction.

Sprint 1 use: same script, run against the harvested national policy corpus.

Pattern transferred from Paper C (inee-minimum-standards-2024-policy-alignment)
scripts/02_pipeline/04_pdf_to_text.py with minimal modifications:
- multilingual default (no lang flag)
- progress logging to stdout
- atomic write (tmp + rename) so partial runs don't corrupt outputs.

Usage
-----
# All PDFs in data/source_pdfs/
python scripts/02_pipeline/04_pdf_to_text.py

# Specific files
python scripts/02_pipeline/04_pdf_to_text.py path/to/foo.pdf path/to/bar.pdf

# Custom input directory
python scripts/02_pipeline/04_pdf_to_text.py --in data/corpus_pilot/raw \\
    --out data/corpus_pilot/processed
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from pdfminer.high_level import extract_text
except ImportError:
    sys.stderr.write(
        "[error] pdfminer.six not installed. Run:\n"
        "    pip install -r requirements.txt\n"
    )
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IN = REPO_ROOT / "data" / "source_pdfs"
DEFAULT_OUT = REPO_ROOT / "data" / "source_pdfs"


def convert(pdf_path: Path, out_path: Path) -> int:
    """Extract text from one PDF; return character count written."""
    text = extract_text(str(pdf_path))
    # Normalise — strip nbsp, collapse triple-blank-lines.
    text = text.replace("\xa0", " ")
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(out_path)
    return len(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pdfs", nargs="*", type=Path,
                        help="explicit PDF paths (default: all PDFs in --in)")
    parser.add_argument("--in", dest="in_dir", type=Path, default=DEFAULT_IN,
                        help=f"input directory (default: {DEFAULT_IN})")
    parser.add_argument("--out", dest="out_dir", type=Path, default=DEFAULT_OUT,
                        help=f"output directory (default: {DEFAULT_OUT})")
    args = parser.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.pdfs:
        pdfs = args.pdfs
    else:
        pdfs = sorted(args.in_dir.glob("*.pdf"))

    if not pdfs:
        sys.stderr.write(f"[error] no PDFs found in {args.in_dir}\n")
        return 1

    total = 0
    for pdf in pdfs:
        out = args.out_dir / (pdf.stem + ".txt")
        try:
            n = convert(pdf, out)
            total += n
            print(f"[ok]  {pdf.name:>45s}  →  {out.name}  ({n:>8,d} chars)")
        except Exception as e:  # noqa: BLE001
            print(f"[err] {pdf.name}: {e}")
    print(f"[done] {len(pdfs)} files, {total:,} chars total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
