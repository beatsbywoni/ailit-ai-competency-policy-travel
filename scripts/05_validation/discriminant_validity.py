#!/usr/bin/env python3
"""discriminant_validity.py — Phase 2 robustness module 6 (C&E I.4 + I.5).

Compare alignment rate (= % of sentences aligned at θ = 0.35) on three corpora:

  A. positive   — `data/corpus_full/processed/*.sentences.jsonl` (our 25-country
                   education-policy corpus); reference = 66.8 % v2 / 68.4 % v1
  B. off-domain — `data/corpus_negative/processed/OFF-*.sentences.jsonl`
                   (fiction, military history, biology, ...)
  C. hard-neg   — `data/corpus_negative/processed/HARD-*.sentences.jsonl`
                   (AI policy from health, defence, corporate domains)

If the positive corpus aligns substantially more than both negative
corpora, the 12 UNESCO anchors are measuring AI-education-policy text
*specifically* rather than generic AI-or-policy vocabulary. That is the
construct-validity claim §4.6 needs.

Outputs
-------
data/robustness/discriminant_validity_v{tag}.csv     per-doc alignment %
data/robustness/discriminant_summary_v{tag}.md       interpretation

Usage
-----
python scripts/05_validation/discriminant_validity.py --tag v2
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    sys.stderr.write("[error] sentence-transformers not installed.\n")
    sys.exit(1)

REPO = Path(__file__).resolve().parents[2]
ANCHOR_DIR = REPO / "anchors"
POS_DIR = REPO / "data" / "corpus_full" / "processed"
NEG_PROC_DIR = REPO / "data" / "corpus_negative" / "processed"
ROBUST_DIR = REPO / "data" / "robustness"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


def load_student_anchors(path: Path) -> list[dict]:
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({"anchor_id": r["anchor_id"], "sentence": r["anchor_sentence"]})
    return out


def alignment_rate(sentences: list[str], anchor_emb: np.ndarray, model, threshold: float, batch: int) -> tuple[int, int, float]:
    if not sentences:
        return 0, 0, 0.0
    emb = model.encode(sentences, normalize_embeddings=True,
                       convert_to_numpy=True, batch_size=batch, show_progress_bar=False)
    sim = emb @ anchor_emb.T
    best = sim.max(axis=1)
    aligned = int((best >= threshold).sum())
    total = len(sentences)
    return aligned, total, aligned / total if total else 0.0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--tag", default="v2", choices=["v1", "v2"])
    p.add_argument("--threshold", type=float, default=0.35)
    p.add_argument("--batch", type=int, default=64)
    args = p.parse_args()

    student_csv = ANCHOR_DIR / ("unesco_ai_student_2024.csv" if args.tag == "v2"
                                 else "unesco_ai_student_2024_v1_archived.csv")
    suffix = f"_{args.tag}"

    print(f"[load] anchors {student_csv.name}")
    anchors = load_student_anchors(student_csv)

    print(f"[init] {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    anchor_emb = model.encode([a["sentence"] for a in anchors],
                              normalize_embeddings=True, convert_to_numpy=True,
                              show_progress_bar=False)

    # Build the per-doc alignment-rate table:
    #   - positive: each *.sentences.jsonl in POS_DIR (one row per doc)
    #   - off-domain: NEG_PROC_DIR OFF-*.sentences.jsonl
    #   - hard-neg:   NEG_PROC_DIR HARD-*.sentences.jsonl
    print(f"[run ] threshold = {args.threshold}")
    rows = []

    pos_files = sorted(POS_DIR.glob("*.sentences.jsonl"))
    for path in pos_files:
        doc_id = path.stem.replace(".sentences", "")
        texts = [json.loads(l)["text"] for l in path.read_text("utf-8").splitlines() if l.strip()]
        a, t, rate = alignment_rate(texts, anchor_emb, model, args.threshold, args.batch)
        rows.append({"corpus": "positive", "doc_id": doc_id, "n_sents": t,
                     "n_aligned": a, "rate_pct": round(rate * 100, 2)})
        print(f"  positive   {doc_id:<12s}  sents={t:>6d}  aligned={a:>5d}  ({rate*100:>5.1f}%)")

    if NEG_PROC_DIR.exists():
        neg_files = sorted(NEG_PROC_DIR.glob("*.sentences.jsonl"))
        for path in neg_files:
            doc_id = path.stem.replace(".sentences", "")
            corpus = "off-domain" if doc_id.startswith("OFF-") else "hard-neg" if doc_id.startswith("HARD-") else "unknown-neg"
            texts = [json.loads(l)["text"] for l in path.read_text("utf-8").splitlines() if l.strip()]
            a, t, rate = alignment_rate(texts, anchor_emb, model, args.threshold, args.batch)
            rows.append({"corpus": corpus, "doc_id": doc_id, "n_sents": t,
                         "n_aligned": a, "rate_pct": round(rate * 100, 2)})
            print(f"  {corpus:<10s} {doc_id:<12s}  sents={t:>6d}  aligned={a:>5d}  ({rate*100:>5.1f}%)")
    else:
        print(f"[warn] {NEG_PROC_DIR} not found — run harvest + extract + split for negative corpus first")

    # Summary by corpus
    summary: dict[str, tuple[int, int]] = {}
    for r in rows:
        c = r["corpus"]
        a, t = summary.get(c, (0, 0))
        summary[c] = (a + r["n_aligned"], t + r["n_sents"])

    print("\n[summary]")
    print(f"{'corpus':<12s}  {'n_total':>8s}  {'n_aligned':>9s}  rate%")
    for c, (a, t) in summary.items():
        rate = a / t * 100 if t else 0
        print(f"{c:<12s}  {t:>8d}  {a:>9d}  {rate:>5.1f}")

    ROBUST_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = ROBUST_DIR / f"discriminant_validity{suffix}.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n[out] {out_csv}")

    pos_rate = summary["positive"][0] / summary["positive"][1] * 100 if summary.get("positive", (0, 0))[1] else 0
    off_rate = summary["off-domain"][0] / summary["off-domain"][1] * 100 if summary.get("off-domain", (0, 0))[1] else None
    hard_rate = summary["hard-neg"][0] / summary["hard-neg"][1] * 100 if summary.get("hard-neg", (0, 0))[1] else None

    md = [f"# Discriminant validity — module 6 ({args.tag} anchors, θ = {args.threshold})",
          "",
          "Construct-validity test: alignment rate (% of sentences crossing the θ = 0.35 cosine threshold to at least one UNESCO student anchor) on three corpora.",
          "",
          "## Aggregate result",
          "",
          "| corpus | n_total | n_aligned | rate % |",
          "|---|---:|---:|---:|"]
    for c, (a, t) in summary.items():
        md.append(f"| {c} | {t} | {a} | {(a/t*100 if t else 0):.1f} |")
    md += ["",
           "## Per-document detail",
           "",
           "| corpus | doc_id | n_sents | n_aligned | rate % |",
           "|---|---|---:|---:|---:|"]
    for r in rows:
        md.append(f"| {r['corpus']} | {r['doc_id']} | {r['n_sents']} | {r['n_aligned']} | {r['rate_pct']} |")

    md += ["",
           "## Interpretation",
           "",
           f"- Positive (25-country education-policy corpus) alignment rate: **{pos_rate:.1f} %**",
           f"- Off-domain negative (fiction + Wikipedia non-AI) alignment rate: **{off_rate:.1f} %**" if off_rate is not None else "- Off-domain not yet processed",
           f"- Hard-negative (AI policy in health/defence/corporate domains) alignment rate: **{hard_rate:.1f} %**" if hard_rate is not None else "- Hard-negative not yet processed",
           "",
           "Expected pattern: positive ≫ hard-negative ≫ off-domain.",
           "",
           "If both negative rates are substantially below the positive rate (e.g. > 20 pp gap), the 12 UNESCO student anchors are measuring something *specific* to AI-in-education policy text — not a generic 'is this English-language formal prose' signal. This is the C&E I.4 (off-domain discriminant) + I.5 (hard-negative discriminant) checklist requirement.",
           "",
           "If the gap is small (< 10 pp), the anchors are over-general and §3.3 (anchor cohesion) needs further sharpening — and the manuscript's construct-validity claim collapses."]
    (ROBUST_DIR / f"discriminant_report{suffix}.md").write_text("\n".join(md), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
