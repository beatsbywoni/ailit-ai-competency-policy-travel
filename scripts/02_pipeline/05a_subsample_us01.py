#!/usr/bin/env python3
"""05a_subsample_us01.py — restrict US-01 to Division E (NAI Act of 2020).

PLAW-116publ283 is the National Defense Authorization Act for FY 2021. Its
Division E IS the National Artificial Intelligence Initiative Act of 2020.
The other divisions are unrelated military / Coast Guard / anti-money-
laundering provisions and should not load into our AI-in-education adherence
analysis.

Strategy
--------
1. Locate "DIVISION E—NATIONAL ARTIFICIAL\nINTELLIGENCE INITIATIVE ACT OF 2020"
   in data/corpus_pilot/processed/US-01.txt (occurrence after the table of
   contents — i.e., the second match).
2. Locate the immediately following "DIVISION F—" line.
3. Slice between those bounds.
4. Save as US-01_eduonly.txt (replaces the alignment input for US-01).
   Keep original as US-01_full.txt for transparency.
5. Re-run sentence split + alignment on the new text.

Usage
-----
python scripts/02_pipeline/05a_subsample_us01.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROCESSED = REPO / "data" / "corpus_pilot" / "processed"
SRC = PROCESSED / "US-01.txt"
FULL_BACKUP = PROCESSED / "US-01_full.txt"
SLICED = PROCESSED / "US-01.txt"  # we overwrite the canonical name


def main() -> int:
    if not SRC.exists():
        sys.stderr.write(f"[error] {SRC} not found. Run 05_extract_corpus.py first.\n")
        return 1

    # Backup the full text once
    if not FULL_BACKUP.exists():
        FULL_BACKUP.write_bytes(SRC.read_bytes())
        print(f"[backup] {FULL_BACKUP}")

    text = FULL_BACKUP.read_text(encoding="utf-8")

    # Find every line index that starts with DIVISION
    lines = text.split("\n")
    div_lines = [(i, ln) for i, ln in enumerate(lines)
                 if re.match(r"^DIVISION [A-Z]", ln)]
    print(f"[scan] {len(div_lines)} DIVISION marker lines")

    # Locate Division E content section: the *second* "DIVISION E" occurrence
    # (first is in the TOC at the top of the document).
    e_idxs = [i for i, ln in div_lines if re.match(r"^DIVISION E", ln)]
    if len(e_idxs) < 2:
        sys.stderr.write("[error] Division E content section not found (need ≥ 2 matches).\n")
        return 1
    e_start = e_idxs[1]

    # End: first DIVISION marker strictly after e_start
    e_end = None
    for i, ln in div_lines:
        if i > e_start:
            e_end = i
            break
    if e_end is None:
        e_end = len(lines)

    slice_text = "\n".join(lines[e_start:e_end]).strip() + "\n"
    SLICED.write_text(slice_text, encoding="utf-8")

    full_chars = len(text)
    new_chars = len(slice_text)
    print(f"[ok] Division E sliced: lines {e_start:,}–{e_end:,} "
          f"({new_chars:,} chars; {new_chars/full_chars*100:.1f}% of original)")
    print(f"[out] {SLICED}  (US-01 now contains NAI Act of 2020 only)")
    print(f"[bk ] {FULL_BACKUP}  (original full NDAA preserved)")
    # Show first 5 lines so user can sanity-check
    head = slice_text.splitlines()[:5]
    print()
    print("[head sample]")
    for h in head:
        print(f"  {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
