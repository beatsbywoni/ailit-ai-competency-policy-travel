#!/usr/bin/env python3
"""06_sentence_split.py — split processed corpus text into sentences.

Paper C settings, transferred:
- length filter 40–600 characters (the 'meaningful policy sentence' range
  Paper C validated against INEE)
- multilingual: simple regex on terminal punctuation `.!?` plus the
  Korean full-stop equivalents `。 .` and the Japanese `。`
- pysbd not used here — Paper C found regex performed comparably for
  policy text and avoided pysbd's CPU overhead on long Korean documents

Output: data/corpus_pilot/processed/{doc_id}.sentences.jsonl
        one JSON per line: {"doc_id", "iso2", "language", "sent_idx", "text"}

Usage
-----
python scripts/02_pipeline/06_sentence_split.py
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

CORPUS_PATHS = {
    "pilot": {
        "csv": REPO / "data" / "corpus_inventory" / "pilot_urls.csv",
        "processed": REPO / "data" / "corpus_pilot" / "processed",
    },
    "full": {
        "csv": REPO / "data" / "corpus_inventory" / "sprint1_urls.csv",
        "processed": REPO / "data" / "corpus_full" / "processed",
    },
    "negative": {
        "csv": REPO / "data" / "corpus_inventory" / "negative_urls.csv",
        "processed": REPO / "data" / "corpus_negative" / "processed",
    },
}
CSV_PATH = CORPUS_PATHS["pilot"]["csv"]
PROCESSED_DIR = CORPUS_PATHS["pilot"]["processed"]

# Match a terminator (.,!,?,。) followed by whitespace OR end-of-string.
# Lookbehind handles "etc." reasonably well for English; for Korean text the
# split happens at every sentence-ending mark which is fine.
SPLIT_RE = re.compile(r"(?<=[\.!?。])[\s ]+")

MIN_CHARS = 40
MAX_CHARS = 600


def split_sentences(text: str) -> list[str]:
    # collapse internal whitespace; the splitter wants whitespace as the seam
    text = re.sub(r"[ \t]+", " ", text)
    # don't split on lines that are just headings (no terminal punctuation)
    candidates = SPLIT_RE.split(text)
    out: list[str] = []
    for c in candidates:
        c = c.strip()
        if not c:
            continue
        # also split on paragraph breaks if the regex missed (very long lines)
        for chunk in re.split(r"\n{2,}", c):
            chunk = chunk.strip()
            if MIN_CHARS <= len(chunk) <= MAX_CHARS:
                out.append(chunk)
            elif len(chunk) > MAX_CHARS:
                # one more fallback: split on single newlines
                for piece in chunk.split("\n"):
                    piece = piece.strip()
                    if MIN_CHARS <= len(piece) <= MAX_CHARS:
                        out.append(piece)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--country", default="", help="ISO2 filter")
    parser.add_argument("--corpus", default="pilot", choices=["pilot", "full", "negative"])
    args = parser.parse_args()

    paths = CORPUS_PATHS[args.corpus]
    csv_path = paths["csv"]
    processed_dir = paths["processed"]

    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"{'doc_id':<8s}  {'lang':<4s}  {'in_chars':>10s}  {'sents':>6s}")
    grand_total = 0
    for r in rows:
        if args.country and r.get("iso2", "") != args.country:
            continue
        doc_id = r["doc_id"]
        lang = r.get("language", "en")  # negative corpus has no language column
        txt_path = processed_dir / f"{doc_id}.txt"
        if not txt_path.exists():
            print(f"{doc_id:<8s}  {lang:<4s}  {'--':>10s}  missing")
            continue
        text = txt_path.read_text(encoding="utf-8")
        sents = split_sentences(text)
        out_path = processed_dir / f"{doc_id}.sentences.jsonl"
        with out_path.open("w", encoding="utf-8") as g:
            for i, s in enumerate(sents):
                g.write(json.dumps(
                    {"doc_id": doc_id, "iso2": r.get("iso2", ""), "language": lang,
                     "sent_idx": i, "text": s},
                    ensure_ascii=False,
                ) + "\n")
        print(f"{doc_id:<8s}  {lang:<4s}  {len(text):>10,d}  {len(sents):>6d}")
        grand_total += len(sents)
    print(f"\n[summary] grand total sentences: {grand_total:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
