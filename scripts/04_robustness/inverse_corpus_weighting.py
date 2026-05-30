#!/usr/bin/env python3
"""inverse_corpus_weighting.py — Sprint 1 robustness IV.2 (planning §7.9).

Problem
-------
Pilot result is dominated by a single huge document per country (KR-02 89%,
FI-01 98%, SG-01 94%). A country-level adherence matrix that sums raw
aligned-sentence counts then inherits the size bias of its largest document.

Method
------
For each (country, anchor) cell, replace the raw count with a document-
weighted equivalent:

    weighted(c, a) = Σ_d (count(d, a) / total_aligned_in_d) × W_d

where W_d = 1 / N_d (the number of documents in country c).
This is equivalent to "average across documents", which gives each document
equal weight regardless of size. (Planning §7.9 step 2 prescription.)

Outputs
-------
data/robustness/inverse_weighted_5x12_pct.csv     country × anchor (%)
data/robustness/inverse_weighted_5x12_pct_v1.csv  v1 anchor version (if --tag v1)
data/robustness/inverse_weighted_summary.csv      one row per country, T÷E + dominant aspect, vs raw matrix
data/robustness/inverse_weighting_report.md       interpretation

Usage
-----
python scripts/04_robustness/inverse_corpus_weighting.py             # active
python scripts/04_robustness/inverse_corpus_weighting.py --tag v1    # archived
python scripts/04_robustness/inverse_corpus_weighting.py --tag v2    # explicit
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALIGN_DIR = REPO / "data" / "adherence_matrix"
ROBUST_DIR = REPO / "data" / "robustness"
ANCHOR_CSV = REPO / "anchors" / "unesco_ai_student_2024.csv"

ASPECT_2 = ["AILIT-S04", "AILIT-S05", "AILIT-S06"]
ASPECT_3 = ["AILIT-S07", "AILIT-S08", "AILIT-S09"]
ASPECT_OF = {
    **{f"AILIT-S0{i}": "A1 HCM" for i in [1, 2, 3]},
    **{f"AILIT-S0{i}": "A2 Ethics" for i in [4, 5, 6]},
    **{f"AILIT-S0{i}": "A3 Tech" for i in [7, 8, 9]},
    **{f"AILIT-S{i:02d}": "A4 SysDes" for i in [10, 11, 12]},
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", default="", help="suffix selecting the alignment file (e.g. v1, v2)")
    parser.add_argument("--corpus", default="pilot", choices=["pilot", "full"],
                        help="which corpus alignment to use (pilot = 5-country, full = 25-country)")
    args = parser.parse_args()

    suffix = f"_{args.tag}" if args.tag else ""
    prefix = "pilot" if args.corpus == "pilot" else "sprint1"
    raw_matrix_prefix = "pilot_5x12" if args.corpus == "pilot" else "sprint1_25x12"
    out_size_label = "5x12" if args.corpus == "pilot" else "25x12"
    align_path = ALIGN_DIR / f"{prefix}_alignment_full{suffix}.jsonl"
    if not align_path.exists():
        sys.stderr.write(f"[error] {align_path} not found. Run 07_embed_and_align.py first.\n")
        return 1

    with ANCHOR_CSV.open(encoding="utf-8") as f:
        anchor_ids = [r["anchor_id"] for r in csv.DictReader(f)]

    # Read alignment: per-(doc, anchor) counts and per-doc total
    doc_counts: dict[tuple[str, str], int] = defaultdict(int)
    doc_totals: dict[str, int] = defaultdict(int)
    doc_country: dict[str, str] = {}
    with align_path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            doc_counts[(r["doc_id"], r["anchor_id"])] += 1
            doc_totals[r["doc_id"]] += 1
            doc_country[r["doc_id"]] = r["iso2"]

    # Group docs by country
    docs_by_country: dict[str, list[str]] = defaultdict(list)
    for d, iso in doc_country.items():
        docs_by_country[iso].append(d)

    # Inverse-weighted per-country anchor shares: mean of per-doc shares
    weighted_pct: dict[tuple[str, str], float] = {}
    for iso, docs in docs_by_country.items():
        for a in anchor_ids:
            shares = []
            for d in docs:
                if doc_totals[d] == 0:
                    continue
                shares.append(doc_counts[(d, a)] / doc_totals[d] * 100.0)
            weighted_pct[(iso, a)] = sum(shares) / len(shares) if shares else 0.0

    # Write per-country × anchor weighted matrix
    ROBUST_DIR.mkdir(parents=True, exist_ok=True)
    wpath = ROBUST_DIR / f"inverse_weighted_{out_size_label}_pct{suffix}.csv"
    with wpath.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["iso"] + anchor_ids + ["n_docs"])
        for iso in sorted(docs_by_country):
            row = [iso] + [round(weighted_pct[(iso, a)], 2) for a in anchor_ids] + [len(docs_by_country[iso])]
            w.writerow(row)

    # Summary: weighted vs raw T/E, dominant aspect
    raw_pct_path = ALIGN_DIR / f"{raw_matrix_prefix}_pct{suffix}.csv"
    raw = {}
    if raw_pct_path.exists():
        with raw_pct_path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                raw[r["key"]] = r

    summary_rows = []
    for iso in sorted(docs_by_country):
        wt = sum(weighted_pct[(iso, a)] for a in ASPECT_3)
        we = sum(weighted_pct[(iso, a)] for a in ASPECT_2)
        w_aspects = {"A1 HCM": sum(weighted_pct[(iso, a)] for a in anchor_ids if ASPECT_OF[a] == "A1 HCM"),
                     "A2 Ethics": we,
                     "A3 Tech": wt,
                     "A4 SysDes": sum(weighted_pct[(iso, a)] for a in anchor_ids if ASPECT_OF[a] == "A4 SysDes")}
        wt_dominant = max(w_aspects, key=w_aspects.get)

        if iso in raw:
            rt = sum(float(raw[iso][a]) for a in ASPECT_3)
            re = sum(float(raw[iso][a]) for a in ASPECT_2)
            raw_aspects = {"A1 HCM": sum(float(raw[iso][a]) for a in anchor_ids if ASPECT_OF[a] == "A1 HCM"),
                           "A2 Ethics": re,
                           "A3 Tech": rt,
                           "A4 SysDes": sum(float(raw[iso][a]) for a in anchor_ids if ASPECT_OF[a] == "A4 SysDes")}
            raw_dominant = max(raw_aspects, key=raw_aspects.get)
            r_te = rt / re if re > 0 else float("inf")
        else:
            r_te = float("nan")
            raw_dominant = "?"

        w_te = wt / we if we > 0 else float("inf")
        summary_rows.append({
            "iso": iso,
            "n_docs": len(docs_by_country[iso]),
            "weighted_A3_Tech_pct": round(wt, 2),
            "weighted_A2_Ethics_pct": round(we, 2),
            "weighted_T/E": round(w_te, 3),
            "weighted_dominant": wt_dominant,
            "raw_T/E": round(r_te, 3) if not isinstance(r_te, float) or r_te == r_te else "nan",
            "raw_dominant": raw_dominant,
            "flipped": "Y" if wt_dominant != raw_dominant else "",
        })

    spath = ROBUST_DIR / f"inverse_weighted_summary{suffix}.csv"
    with spath.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        w.writerows(summary_rows)

    # Console
    print(f"{'iso':<4} {'docs':>4} {'rawT/E':>7} {'wT/E':>7} {'raw_dom':<11} {'w_dom':<11} flip?")
    for r in summary_rows:
        print(f"{r['iso']:<4} {r['n_docs']:>4} {r['raw_T/E']:>7} {r['weighted_T/E']:>7.3f} "
              f"{r['raw_dominant']:<11} {r['weighted_dominant']:<11} {r['flipped']}")
    print()
    print(f"[out] {wpath}")
    print(f"[out] {spath}")

    md = ["# Inverse-corpus weighting — robustness check IV.2",
          "",
          f"Source: `{align_path.name}`. Per-(country, anchor) weighted share = mean across documents of within-doc share. Each document counts equally regardless of size.",
          "",
          "## Per-country comparison",
          "",
          "| Country | Docs | Raw T÷E | Weighted T÷E | Raw dominant | Weighted dominant | Flipped? |",
          "|---|---:|---:|---:|---|---|---|"]
    for r in summary_rows:
        md.append(f"| {r['iso']} | {r['n_docs']} | {r['raw_T/E']} | {r['weighted_T/E']:.3f} | "
                  f"{r['raw_dominant']} | {r['weighted_dominant']} | {r['flipped'] or 'no'} |")
    md += ["",
           "## Interpretation",
           "",
           "If the per-country dominant aspect is stable when each document is given equal weight, the 4-pattern bifurcation is not an artefact of single-document dominance.",
           "",
           "Flips marked 'Y' deserve special discussion in §4.6 robustness."]
    (ROBUST_DIR / f"inverse_weighting_report{suffix}.md").write_text("\n".join(md), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
