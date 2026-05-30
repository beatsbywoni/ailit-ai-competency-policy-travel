#!/usr/bin/env python3
"""07_embed_and_align.py — embed corpus sentences and align to 21 anchors.

Paper C settings (transferred verbatim):
- model: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
- L2-normalised embeddings
- cosine similarity = dot product after normalisation
- alignment = argmax over anchors; threshold (default 0.35) excludes unaligned
- one sentence aligns to at most one anchor

For Sprint 0 we run alignment against the 12 UNESCO student anchors as the
primary set (used in the adherence matrix). Teacher (5) + OECD (4) anchors
are scored on the same sentence set but reported separately for the
cross-organisational analysis (RQ4) — Sprint 1 deliverable.

Outputs
-------
data/corpus_pilot/processed/{doc_id}.alignment.jsonl
  one line per *aligned* sentence: {doc_id, iso2, sent_idx, text, anchor_id,
  aspect, level, score}

data/adherence_matrix/pilot_alignment_full.jsonl
  concatenation of all per-doc alignment files for downstream analysis.

Usage
-----
python scripts/02_pipeline/07_embed_and_align.py
python scripts/02_pipeline/07_embed_and_align.py --threshold 0.40
python scripts/02_pipeline/07_embed_and_align.py --batch-size 32
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
    sys.stderr.write(
        "[error] sentence-transformers not installed. Run:\n"
        "    pip install -r requirements.txt\n"
    )
    sys.exit(1)

REPO = Path(__file__).resolve().parents[2]
ANCHOR_DIR = REPO / "anchors"
MATRIX_DIR = REPO / "data" / "adherence_matrix"

CORPUS_PATHS = {
    "pilot": REPO / "data" / "corpus_pilot" / "processed",
    "full": REPO / "data" / "corpus_full" / "processed",
}
CORPUS_PREFIX = {"pilot": "pilot", "full": "sprint1"}
PROCESSED_DIR = CORPUS_PATHS["pilot"]  # default for back-compat

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

DEFAULT_STUDENT_CSV = ANCHOR_DIR / "unesco_ai_student_2024.csv"


def load_anchors(student_csv: Path | None = None) -> list[dict]:
    """Load all anchors. `student_csv` overrides the default student CSV path
    (used by the dual-anchor Sprint 0.5 / Sprint 1 sensitivity runs)."""
    anchors: list[dict] = []
    student_path = student_csv or DEFAULT_STUDENT_CSV

    # Student (12)
    with student_path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            anchors.append({
                "anchor_id": r["anchor_id"],
                "anchor_set": "student",
                "aspect": r["aspect"],
                "level": r["level"],
                "block_name": r["block_name"],
                "sentence": r["anchor_sentence"],
            })

    # Teacher (5)
    with (ANCHOR_DIR / "unesco_ai_teacher_2024.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            anchors.append({
                "anchor_id": r["anchor_id"],
                "anchor_set": "teacher",
                "aspect": r["aspect"],
                "level": "",
                "block_name": r["aspect"],
                "sentence": r["anchor_sentence"],
            })

    # OECD (4)
    with (ANCHOR_DIR / "oecd_ai_literacy_2025.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            anchors.append({
                "anchor_id": r["anchor_id"],
                "anchor_set": "oecd",
                "aspect": r["domain"],
                "level": "",
                "block_name": r["domain"],
                "sentence": r["anchor_sentence"],
            })

    return anchors


def load_corpus(processed_dir: Path | None = None) -> dict[str, list[dict]]:
    """Return {doc_id: [sentence_record, ...]}."""
    out: dict[str, list[dict]] = {}
    pd = processed_dir or PROCESSED_DIR
    for path in sorted(pd.glob("*.sentences.jsonl")):
        doc_id = path.stem.split(".")[0]
        recs = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                recs.append(json.loads(line))
        out[doc_id] = recs
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--threshold", type=float, default=0.35)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--anchor-set", default="student",
                        choices=["student", "teacher", "oecd", "all"],
                        help="set used for primary alignment "
                             "(student = 12 anchors, teacher = 5, oecd = 4, "
                             "all = 21; planning §7.4 + Phase 3 cross-org)")
    parser.add_argument("--student-csv", type=Path, default=None,
                        help="override the student-anchor CSV path; default "
                             "anchors/unesco_ai_student_2024.csv. Use to run "
                             "the v1 archived anchors or any alternate set.")
    parser.add_argument("--tag", default="",
                        help="suffix appended to per-doc and full alignment "
                             "outputs (e.g. 'v1', 'v2'); empty = default names.")
    parser.add_argument("--corpus", default="pilot", choices=["pilot", "full"])
    args = parser.parse_args()

    processed_dir = CORPUS_PATHS[args.corpus]
    corpus_prefix = CORPUS_PREFIX[args.corpus]
    MATRIX_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.tag}" if args.tag else ""

    print(f"[load] anchors  (student_csv={args.student_csv or DEFAULT_STUDENT_CSV.name})")
    anchors = load_anchors(args.student_csv)
    if args.anchor_set in {"student", "teacher", "oecd"}:
        primary = [a for a in anchors if a["anchor_set"] == args.anchor_set]
    else:
        primary = anchors
    print(f"       {len(primary)} primary anchors (set={args.anchor_set})")

    print(f"[load] corpus  ({args.corpus} = {processed_dir.name})")
    corpus = load_corpus(processed_dir)
    n_sents = sum(len(v) for v in corpus.values())
    print(f"       {len(corpus)} documents, {n_sents:,} sentences")

    print(f"[init] embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print(f"[embed] anchors")
    anchor_emb = model.encode(
        [a["sentence"] for a in primary],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    print(f"[embed] corpus sentences (batch_size={args.batch_size})")
    full_out = MATRIX_DIR / f"{corpus_prefix}_alignment_full{suffix}.jsonl"
    n_aligned_total = 0
    with full_out.open("w", encoding="utf-8") as full_g:
        for doc_id, recs in corpus.items():
            texts = [r["text"] for r in recs]
            if not texts:
                continue
            emb = model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                batch_size=args.batch_size,
                show_progress_bar=False,
            )
            # similarity = emb @ anchor_emb.T
            sim = emb @ anchor_emb.T  # shape (n_sents, n_anchors)
            best_anchor = sim.argmax(axis=1)
            best_score = sim.max(axis=1)

            per_doc_out = processed_dir / f"{doc_id}.alignment{suffix}.jsonl"
            n_aligned = 0
            with per_doc_out.open("w", encoding="utf-8") as g:
                for i, rec in enumerate(recs):
                    if best_score[i] < args.threshold:
                        continue
                    a = primary[best_anchor[i]]
                    out_rec = {
                        "doc_id": doc_id,
                        "iso2": rec["iso2"],
                        "sent_idx": rec["sent_idx"],
                        "text": rec["text"],
                        "anchor_id": a["anchor_id"],
                        "aspect": a["aspect"],
                        "level": a["level"],
                        "score": float(best_score[i]),
                    }
                    json.dumps(out_rec, ensure_ascii=False)  # eager validation
                    g.write(json.dumps(out_rec, ensure_ascii=False) + "\n")
                    full_g.write(json.dumps(out_rec, ensure_ascii=False) + "\n")
                    n_aligned += 1
            n_aligned_total += n_aligned
            pct = n_aligned / len(recs) * 100 if recs else 0
            print(f"  {doc_id:<8s}  sents={len(recs):>6d}  aligned={n_aligned:>5d}  ({pct:5.1f}%)")

    print(f"\n[summary] total aligned sentences: {n_aligned_total:,} "
          f"({n_aligned_total/n_sents*100:.1f}%) at threshold {args.threshold}")
    print(f"[out    ] {full_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
