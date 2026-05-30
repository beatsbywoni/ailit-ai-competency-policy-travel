#!/usr/bin/env python3
"""threshold_sensitivity.py — Sprint 0 robustness step #2.

Embeds the 12 UNESCO student anchors and all corpus sentences ONCE, computes
the full similarity matrix per document, then enumerates threshold values
{0.30, 0.35, 0.40, 0.45, 0.50}. For each threshold:
- builds the 5×12 country × anchor adherence matrix
- computes tool ÷ ethics ratio per country
- writes per-threshold matrix CSV and a summary row

Planning §7.9 robustness check #1 (threshold sensitivity).

Outputs
-------
data/robustness/threshold_sweep_5x12_t{T}.csv     per-threshold matrix
data/robustness/threshold_sweep_summary.csv       summary across thresholds
data/robustness/threshold_sweep_report.md         markdown summary

Usage
-----
python scripts/04_robustness/threshold_sensitivity.py
python scripts/04_robustness/threshold_sensitivity.py --thresholds 0.30 0.35 0.40
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    sys.stderr.write("[error] sentence-transformers not installed.\n")
    sys.exit(1)

REPO = Path(__file__).resolve().parents[2]
ANCHOR_CSV = REPO / "anchors" / "unesco_ai_student_2024.csv"
PROCESSED_DIR = REPO / "data" / "corpus_pilot" / "processed"
OUT_DIR = REPO / "data" / "robustness"
PILOT_CSV = REPO / "data" / "corpus_inventory" / "pilot_urls.csv"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

ASPECT_2 = ["AILIT-S04", "AILIT-S05", "AILIT-S06"]
ASPECT_3 = ["AILIT-S07", "AILIT-S08", "AILIT-S09"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--thresholds", type=float, nargs="+",
                        default=[0.30, 0.35, 0.40, 0.45, 0.50])
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load anchors
    with ANCHOR_CSV.open(encoding="utf-8") as f:
        anchors = list(csv.DictReader(f))
    anchor_ids = [a["anchor_id"] for a in anchors]

    # Load country order
    with PILOT_CSV.open(encoding="utf-8") as f:
        country_order: list[str] = []
        seen: dict[str, None] = {}
        for r in csv.DictReader(f):
            if r["iso2"] not in seen:
                seen[r["iso2"]] = None
                country_order.append(r["iso2"])

    # Load all sentences
    sent_records: list[dict] = []
    for path in sorted(PROCESSED_DIR.glob("*.sentences.jsonl")):
        with path.open(encoding="utf-8") as f:
            for line in f:
                sent_records.append(json.loads(line))
    if not sent_records:
        sys.stderr.write("[error] no sentences found; run 06_sentence_split.py first.\n")
        return 1
    print(f"[load] {len(sent_records):,} sentences across "
          f"{len({r['doc_id'] for r in sent_records})} documents")

    print(f"[init] {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print(f"[embed] anchors (12)")
    anchor_emb = model.encode(
        [a["anchor_sentence"] for a in anchors],
        normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False,
    )

    print(f"[embed] corpus sentences")
    texts = [r["text"] for r in sent_records]
    sent_emb = model.encode(
        texts, normalize_embeddings=True, convert_to_numpy=True,
        batch_size=args.batch_size, show_progress_bar=False,
    )
    sim = sent_emb @ anchor_emb.T                  # (N, 12)
    best_anchor = sim.argmax(axis=1)               # (N,)
    best_score = sim.max(axis=1)                   # (N,)

    # Per-threshold tally
    summary_rows: list[dict] = []
    print()
    print(f"{'thr':>5}  {'aligned':>7}  {'%aligned':>8}  " +
          "  ".join(f"{c:>4s}" for c in country_order) +
          "    " + "  ".join(f"{c}:T/E" for c in country_order))
    matrices_per_threshold: dict[float, dict] = {}
    for thr in args.thresholds:
        # Build counts
        cc: dict[tuple[str, str], int] = defaultdict(int)
        tot: dict[str, int] = defaultdict(int)
        n_above = 0
        for i, r in enumerate(sent_records):
            if best_score[i] < thr:
                continue
            iso = r["iso2"]
            aid = anchor_ids[best_anchor[i]]
            cc[(iso, aid)] += 1
            tot[iso] += 1
            n_above += 1
        # Write per-threshold matrix
        tstr = f"{int(thr*100):03d}"
        mpath = OUT_DIR / f"threshold_sweep_5x12_t{tstr}.csv"
        with mpath.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["iso"] + anchor_ids + ["total_aligned"])
            for c in country_order:
                if c not in tot:
                    continue
                row = [c] + [round(cc[(c, a)] / tot[c] * 100, 2) for a in anchor_ids] + [tot[c]]
                w.writerow(row)
        # Summary metrics per country
        s_row = {"threshold": thr, "n_aligned": n_above,
                 "pct_aligned": round(n_above / len(sent_records) * 100, 1)}
        country_te = []
        for c in country_order:
            t = sum(cc[(c, a)] / max(tot[c], 1) * 100 for a in ASPECT_3)
            e = sum(cc[(c, a)] / max(tot[c], 1) * 100 for a in ASPECT_2)
            ratio = round(t / e, 2) if e > 0 else float("inf")
            s_row[f"{c}_tool_pct"] = round(t, 2)
            s_row[f"{c}_ethics_pct"] = round(e, 2)
            s_row[f"{c}_T/E"] = ratio
            s_row[f"{c}_total"] = tot.get(c, 0)
            country_te.append(ratio)
        s_row["n_meet_3x"] = sum(1 for r in country_te if r != float("inf") and r >= 3)
        summary_rows.append(s_row)
        matrices_per_threshold[thr] = s_row
        totals = "  ".join(f"{tot.get(c, 0):>4d}" for c in country_order)
        tes = "  ".join(f"{s_row[c+'_T/E']:>5.2f}" if s_row[c+'_T/E'] != float('inf') else "  inf"
                        for c in country_order)
        print(f"{thr:>5.2f}  {n_above:>7,d}  {s_row['pct_aligned']:>7.1f}%  {totals}    {tes}")

    # Summary CSV
    spath = OUT_DIR / "threshold_sweep_summary.csv"
    with spath.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        w.writerows(summary_rows)

    # Markdown report — bifurcation stability
    md = [
        "# Threshold sensitivity report",
        "",
        f"Planning §7.9 robustness step. Thresholds swept: {args.thresholds}.",
        "",
        "## Tool ÷ Ethics ratio across thresholds",
        "",
        "| Threshold | Aligned (%) | " + " | ".join(country_order) + " | Countries with T÷E ≥ 3× |",
        "|---|---:|" + "---:|" * len(country_order) + "---:|",
    ]
    for s in summary_rows:
        cells = " | ".join(
            f"{s[c+'_T/E']:.2f}" if s[c+'_T/E'] != float('inf') else "inf"
            for c in country_order
        )
        md.append(f"| {s['threshold']:.2f} | {s['pct_aligned']:.1f} | {cells} | {s['n_meet_3x']} |")
    md += [
        "",
        "## Interpretation",
        "",
        "If the bifurcation pattern (Korea tool-leaning vs US/FI/SG ethics-leaning) survives the threshold sweep — i.e., per-country T÷E rank order is stable — the finding is robust to the §7.3 threshold choice.",
        "",
        "If the pattern collapses (e.g., US T÷E rises above 1 at threshold 0.45), the Sprint 0 verdict was a threshold artefact and the §10.1 RED → AMBER reframing must be reconsidered.",
        "",
        f"Outputs: `threshold_sweep_5x12_t{{NN}}.csv` per threshold, `threshold_sweep_summary.csv` aggregated.",
    ]
    (OUT_DIR / "threshold_sweep_report.md").write_text("\n".join(md), encoding="utf-8")

    print()
    print(f"[out] {spath}")
    print(f"[out] {OUT_DIR / 'threshold_sweep_report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
