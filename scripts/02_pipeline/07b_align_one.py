#!/usr/bin/env python3
"""07b_align_one.py — incremental alignment for a single doc, append to full.

Same model + threshold + anchors as 07_embed_and_align.py, but only
processes the named doc(s) and *appends* their alignment lines to the
existing `sprint1_alignment_full_{tag}.jsonl`. Use after manually
fixing one source file without redoing the entire 67-doc embed pass.

Usage
-----
python scripts/02_pipeline/07b_align_one.py --doc-id ZA-02 --tag v2 \\
       --student-csv anchors/unesco_ai_student_2024.csv
python scripts/02_pipeline/07b_align_one.py --doc-id ZA-02 --tag v1 \\
       --student-csv anchors/unesco_ai_student_2024_v1_archived.csv
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
MATRIX_DIR = REPO / "data" / "adherence_matrix"
PROCESSED_DIR = REPO / "data" / "corpus_full" / "processed"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


def load_student_anchors(path: Path) -> list[dict]:
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({
                "anchor_id": r["anchor_id"],
                "aspect": r["aspect"],
                "level": r["level"],
                "sentence": r["anchor_sentence"],
            })
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--doc-id", required=True, action="append",
                   help="doc_id to (re-)align; may be repeated")
    p.add_argument("--threshold", type=float, default=0.35)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--student-csv", type=Path,
                   default=ANCHOR_DIR / "unesco_ai_student_2024.csv")
    p.add_argument("--tag", default="v2")
    args = p.parse_args()

    suffix = f"_{args.tag}" if args.tag else ""
    full_path = MATRIX_DIR / f"sprint1_alignment_full{suffix}.jsonl"
    if not full_path.exists():
        sys.stderr.write(f"[error] {full_path} not found. Run full pipeline first.\n")
        return 1

    print(f"[load] anchors  {args.student_csv.name}")
    anchors = load_student_anchors(args.student_csv)
    print(f"       {len(anchors)} primary anchors")

    print(f"[init] {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    anchor_emb = model.encode([a["sentence"] for a in anchors],
                              normalize_embeddings=True, convert_to_numpy=True,
                              show_progress_bar=False)

    # Read existing full file, drop lines for any --doc-id we're re-aligning
    keep = []
    drop_ids = set(args.doc_id)
    with full_path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["doc_id"] not in drop_ids:
                keep.append(line)
    print(f"[load] existing full: kept {len(keep)} lines (dropped lines for {sorted(drop_ids)})")

    new_lines: list[str] = []
    for doc_id in args.doc_id:
        sent_path = PROCESSED_DIR / f"{doc_id}.sentences.jsonl"
        if not sent_path.exists():
            sys.stderr.write(f"[warn] {sent_path} missing; skip\n")
            continue
        recs = [json.loads(l) for l in sent_path.read_text("utf-8").splitlines() if l.strip()]
        if not recs:
            print(f"  {doc_id:<8s}  sents=0  skip")
            continue
        texts = [r["text"] for r in recs]
        emb = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True,
                           batch_size=args.batch_size, show_progress_bar=False)
        sim = emb @ anchor_emb.T
        best_anchor = sim.argmax(axis=1)
        best_score = sim.max(axis=1)

        per_doc_out = PROCESSED_DIR / f"{doc_id}.alignment{suffix}.jsonl"
        n_aligned = 0
        with per_doc_out.open("w", encoding="utf-8") as g:
            for i, rec in enumerate(recs):
                if best_score[i] < args.threshold:
                    continue
                a = anchors[best_anchor[i]]
                out = {
                    "doc_id": doc_id,
                    "iso2": rec["iso2"],
                    "sent_idx": rec["sent_idx"],
                    "text": rec["text"],
                    "anchor_id": a["anchor_id"],
                    "aspect": a["aspect"],
                    "level": a["level"],
                    "score": float(best_score[i]),
                }
                line = json.dumps(out, ensure_ascii=False) + "\n"
                g.write(line)
                new_lines.append(line)
                n_aligned += 1
        pct = n_aligned / len(recs) * 100 if recs else 0
        print(f"  {doc_id:<8s}  sents={len(recs):>6d}  aligned={n_aligned:>5d}  ({pct:5.1f}%)")

    # Rewrite full file
    with full_path.open("w", encoding="utf-8") as f:
        f.writelines(keep)
        f.writelines(new_lines)
    print(f"\n[out] {full_path}  (now {len(keep) + len(new_lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
