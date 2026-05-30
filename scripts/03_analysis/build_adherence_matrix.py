#!/usr/bin/env python3
"""build_adherence_matrix.py — country × anchor adherence matrix.

Reads data/adherence_matrix/pilot_alignment_full.jsonl (output of
07_embed_and_align.py) and produces the per-country, per-anchor adherence
table that is the planning §7.4 deliverable.

Two outputs:
- pilot_5x12_counts.csv   — raw aligned-sentence counts per country × anchor
- pilot_5x12_pct.csv      — percentage normalised so each country row sums to 100

The percentage matrix is the input to §7.5 Hellinger clustering and §7.6
temporal cohort analysis.

Usage
-----
python scripts/03_analysis/build_adherence_matrix.py
python scripts/03_analysis/build_adherence_matrix.py --by-doc   # finer grain
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "data" / "adherence_matrix"

ANCHOR_CSV_MAP = {
    "student": REPO / "anchors" / "unesco_ai_student_2024.csv",
    "teacher": REPO / "anchors" / "unesco_ai_teacher_2024.csv",
    "oecd": REPO / "anchors" / "oecd_ai_literacy_2025.csv",
}
ANCHOR_ID_FIELD = {"student": "anchor_id", "teacher": "anchor_id", "oecd": "anchor_id"}

CORPUS_INVENTORY = {
    "pilot": REPO / "data" / "corpus_inventory" / "pilot_urls.csv",
    "full": REPO / "data" / "corpus_inventory" / "sprint1_urls.csv",
}
CORPUS_PREFIX = {"pilot": "pilot", "full": "sprint1"}
DEFAULT_PCT_GLOB = {"pilot": "pilot", "full": "sprint1"}


def load_anchor_order(anchor_csv: Path) -> list[str]:
    with anchor_csv.open(newline="", encoding="utf-8") as f:
        return [r["anchor_id"] for r in csv.DictReader(f)]


def load_country_order(csv_path: Path | None = None) -> list[str]:
    seen: dict[str, None] = {}
    path = csv_path or CORPUS_INVENTORY["pilot"]
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            seen[r["iso2"]] = None
    return list(seen.keys())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--by-doc", action="store_true",
                        help="output document × anchor matrix instead of country × anchor")
    parser.add_argument("--tag", default="",
                        help="suffix for inputs/outputs (e.g. 'v1', 'v2', 'teacher', 'oecd')")
    parser.add_argument("--corpus", default="pilot", choices=["pilot", "full"])
    parser.add_argument("--anchor-set", default="student",
                        choices=["student", "teacher", "oecd"],
                        help="which anchor framework's columns to use "
                             "(student = 12, teacher = 5, oecd = 4)")
    args = parser.parse_args()

    suffix = f"_{args.tag}" if args.tag else ""
    inv_prefix = DEFAULT_PCT_GLOB[args.corpus]   # pilot_alignment_full or sprint1_alignment_full
    # Determine matrix-dimensions string for output filename (e.g. 25x12, 25x5, 25x4)
    base = CORPUS_PREFIX[args.corpus]            # pilot or sprint1
    n_countries = {"pilot": 5, "full": 25}[args.corpus]
    anchor_csv_path = ANCHOR_CSV_MAP[args.anchor_set]
    anchor_order = load_anchor_order(anchor_csv_path)
    n_anchors = len(anchor_order)
    out_prefix = f"{base}_{n_countries}x{n_anchors}"
    PILOT_CSV = CORPUS_INVENTORY[args.corpus]
    ALIGN = OUT_DIR / f"{inv_prefix}_alignment_full{suffix}.jsonl"
    if not ALIGN.exists():
        sys.stderr.write(f"[error] {ALIGN} not found. Run 07_embed_and_align.py first.\n")
        return 1

    country_order = load_country_order(PILOT_CSV)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build (key, anchor) -> count.
    # key = iso2 (default) or doc_id (--by-doc)
    counts: dict[tuple[str, str], int] = defaultdict(int)
    key_totals: dict[str, int] = defaultdict(int)
    seen_keys: dict[str, None] = {}

    with ALIGN.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            key = r["doc_id"] if args.by_doc else r["iso2"]
            counts[(key, r["anchor_id"])] += 1
            key_totals[key] += 1
            seen_keys[key] = None

    if args.by_doc:
        keys = list(seen_keys.keys())
    else:
        keys = [c for c in country_order if c in seen_keys]

    # Write counts
    counts_path = OUT_DIR / (f"{inv_prefix}_by_doc_counts{suffix}.csv" if args.by_doc
                              else f"{out_prefix}_counts{suffix}.csv")
    with counts_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["key"] + anchor_order + ["total_aligned"])
        for k in keys:
            row = [k] + [counts[(k, a)] for a in anchor_order] + [key_totals[k]]
            w.writerow(row)

    # Write percentages (rows sum to 100% of aligned sentences for that key)
    pct_path = OUT_DIR / (f"{inv_prefix}_by_doc_pct{suffix}.csv" if args.by_doc
                           else f"{out_prefix}_pct{suffix}.csv")
    with pct_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["key"] + anchor_order + ["total_aligned"])
        for k in keys:
            tot = key_totals[k] or 1
            row = [k] + [round(counts[(k, a)] / tot * 100, 2) for a in anchor_order] + [key_totals[k]]
            w.writerow(row)

    print(f"[out] {counts_path}")
    print(f"[out] {pct_path}")
    print()
    # Pretty print percentages
    print(f"{'iso2' if not args.by_doc else 'doc_id':<7s}  " +
          "  ".join(f"{a[-3:]:>5s}" for a in anchor_order) + "   total")
    for k in keys:
        tot = key_totals[k] or 1
        cells = "  ".join(f"{counts[(k, a)] / tot * 100:5.1f}" for a in anchor_order)
        print(f"{k:<7s}  {cells}   {key_totals[k]:>5d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
