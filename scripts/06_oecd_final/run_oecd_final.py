#!/usr/bin/env python3
"""run_oecd_final.py — re-run the OECD–EC anchor pipeline against the FINAL
(June 2026) AILit framework and compare with the May 2025 review-draft results.

Self-contained (does not modify the existing pipeline scripts). Mirrors the
output formats of 07_embed_and_align.py / build_adherence_matrix.py /
hellinger_cluster.py so the new files sit alongside the existing `_oecd`
outputs with an `_oecd_final` suffix.

Corpus is FROZEN at the 28–30 May 2026 harvest (author decision, 2026-09-04).
No documents are added or removed; only the four OECD–EC anchor sentences
change (draft → final; "Designing AI" → "Shape AI").

Outputs
-------
data/adherence_matrix/sprint1_alignment_full_oecd_final.jsonl
data/adherence_matrix/sprint1_25x4_counts_oecd_final.csv
data/adherence_matrix/sprint1_25x4_pct_oecd_final.csv
data/adherence_matrix/sprint1_by_doc_counts_oecd_final.csv
data/adherence_matrix/sprint1_by_doc_pct_oecd_final.csv
data/clustering/hellinger_dist_oecd_final.csv
data/clustering/clusters_oecd_final_ward_K{2..6}.csv
data/clustering/clusters_oecd_final_average_K{2..6}.csv
data/clustering/silhouette_oecd_final.csv
data/clustering/oecd_draft_vs_final_comparison.csv
data/clustering/dendrogram_oecd_final_ward.png

Usage (from repo root, with the sentence-transformers model cached locally)
-----
python scripts/06_oecd_final/run_oecd_final.py
python scripts/06_oecd_final/run_oecd_final.py --threshold 0.35 --batch-size 64
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
try:
    from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
    from scipy.spatial.distance import squareform
    from sklearn.metrics import silhouette_score
except ImportError:
    sys.stderr.write("[error] scipy / scikit-learn not installed.\n")
    sys.exit(1)

REPO = Path(__file__).resolve().parents[2]
ANCHOR_CSV = REPO / "anchors" / "oecd_ai_literacy_2026_final.csv"
DRAFT_ANCHOR_CSV = REPO / "anchors" / "oecd_ai_literacy_2025.csv"
PROCESSED = REPO / "data" / "corpus_full" / "processed"
INVENTORY = REPO / "data" / "corpus_inventory" / "sprint1_urls.csv"
MATRIX_DIR = REPO / "data" / "adherence_matrix"
CLUSTER_DIR = REPO / "data" / "clustering"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
TAG = "oecd_final"


def load_anchors(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return [
            {"anchor_id": r["anchor_id"], "aspect": r["domain"], "sentence": r["anchor_sentence"],
             "paragraph_full": r.get("paragraph_full", ""), "row": r}
            for r in csv.DictReader(f)
        ]


def split_sentences(par: str) -> list[str]:
    import re
    return [s for s in re.split(r"(?<=[.])\s+(?=[A-Z])", par.strip()) if s]


def n_tokens(model, text: str) -> int:
    """Token count as the encoder sees it (incl. special tokens)."""
    return len(model.tokenizer(text, add_special_tokens=True)["input_ids"])


def resolve_final_anchors(model, anchors: list[dict], csv_path: Path) -> list[dict]:
    """Final-framework anchor rule (pre-submission fix round, 2026-09-04):
    anchor = the longest run of *initial* sentences of the verbatim domain-opener
    paragraph that fits the encoder's window (model.max_seq_length, 128 tokens for
    paraphrase-multilingual-mpnet-base-v2). Guarantees the anchor is contiguous,
    verbatim, and entirely encoded (no silent truncation). Rewrites the CSV's
    anchor_sentence / sentences_used columns if they differ from the rule."""
    win = int(model.max_seq_length)
    changed = False
    print(f"[anchors] encoder window = {win} tokens; resolving final anchors by the initial-sentences rule")
    for a in anchors:
        full = a["paragraph_full"]
        if not full:
            print(f"  {a['anchor_id']}: no paragraph_full column — using anchor_sentence as is "
                  f"({n_tokens(model, a['sentence'])} tokens)")
            continue
        ss = split_sentences(full)
        k_fit = 0
        for k in range(1, len(ss) + 1):
            if n_tokens(model, " ".join(ss[:k])) <= win:
                k_fit = k
            else:
                break
        resolved = " ".join(ss[:k_fit])
        nt = n_tokens(model, resolved)
        nxt = n_tokens(model, " ".join(ss[:k_fit + 1])) if k_fit < len(ss) else None
        flag = ""
        if resolved != a["sentence"]:
            flag = "  ** CSV updated **"
            changed = True
            a["sentence"] = resolved
            a["row"]["anchor_sentence"] = resolved
        a["row"]["sentences_used"] = f"1-{k_fit} of {len(ss)}"
        print(f"  {a['anchor_id']}: sentences 1-{k_fit} of {len(ss)}, {nt} tokens"
              + (f" (adding sentence {k_fit+1} would give {nxt})" if nxt else " (whole paragraph)") + flag)
        assert nt <= win, f"{a['anchor_id']} exceeds the encoder window"
    if changed:
        fields = list(anchors[0]["row"].keys())
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for a in anchors:
                w.writerow(a["row"])
        print(f"[anchors] {csv_path.name} rewritten with the resolved anchor sentences")
    return anchors


def report_token_lengths(model, label: str, path: Path) -> None:
    """Informational: token length of every pre-specified anchor vs the window."""
    win = int(model.max_seq_length)
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            s = r.get("anchor_sentence") or r.get("sentence")
            nt = n_tokens(model, s)
            print(f"  {label:<16} {r['anchor_id']:<12} {len(s.split()):>4} words {nt:>4} tokens"
                  + ("  ** EXCEEDS WINDOW — encoder truncates **" if nt > win else ""))


def sha256_of(paths: list[Path]) -> dict[str, str]:
    import hashlib
    out = {}
    for p in paths:
        if p.exists():
            out[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    return out


def load_corpus() -> dict[str, list[dict]]:
    corpus: dict[str, list[dict]] = {}
    for p in sorted(PROCESSED.glob("*.sentences.jsonl")):
        doc_id = p.name.split(".")[0]
        with p.open(encoding="utf-8") as f:
            corpus[doc_id] = [json.loads(l) for l in f if l.strip()]
    return corpus


def load_country_order() -> list[str]:
    seen: dict[str, None] = {}
    with INVENTORY.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            seen[r["iso2"]] = None
    return list(seen.keys())


def hellinger(P: np.ndarray) -> np.ndarray:
    sqrtP = np.sqrt(P)
    diff = sqrtP[:, None, :] - sqrtP[None, :, :]
    H = np.sqrt(0.5 * (diff ** 2).sum(axis=2))
    np.fill_diagonal(H, 0.0)
    return (H + H.T) / 2.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--threshold", type=float, default=0.35)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--min-aligned", type=int, default=50)
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    MATRIX_DIR.mkdir(parents=True, exist_ok=True)
    CLUSTER_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- draft outputs: hash before
    draft_files = [MATRIX_DIR / "sprint1_25x4_counts_oecd.csv", MATRIX_DIR / "sprint1_25x4_pct_oecd.csv",
                   MATRIX_DIR / "sprint1_by_doc_counts_oecd.csv", MATRIX_DIR / "sprint1_by_doc_pct_oecd.csv",
                   CLUSTER_DIR / "hellinger_dist_oecd.csv", CLUSTER_DIR / "clusters_oecd_ward_K2.csv",
                   CLUSTER_DIR / "clusters_oecd_average_K2.csv"]
    h_before = sha256_of(draft_files)
    print("[hash   ] draft (May 2025) outputs before run: " + ", ".join(f"{k}={v}" for k, v in h_before.items()))

    # ---------------------------------------------------------------- model
    print(f"[model  ] {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print(f"[model  ] max_seq_length = {model.max_seq_length} tokens (pipeline default; unchanged)")

    # ---------------------------------------------------------------- anchors
    anchors = load_anchors(ANCHOR_CSV)
    anchors = resolve_final_anchors(model, anchors, ANCHOR_CSV)
    anchor_ids = [a["anchor_id"] for a in anchors]
    print(f"[anchors] {len(anchors)} final OECD–EC anchors: {anchor_ids}")
    print("[anchors] token lengths of the pre-specified anchor sets (informational; not modified):")
    report_token_lengths(model, "OECD draft", DRAFT_ANCHOR_CSV)
    report_token_lengths(model, "UNESCO student", REPO / "anchors" / "unesco_ai_student_2024.csv")
    report_token_lengths(model, "UNESCO teacher", REPO / "anchors" / "unesco_ai_teacher_2024.csv")

    # ---------------------------------------------------------------- corpus
    corpus = load_corpus()
    n_sents = sum(len(v) for v in corpus.values())
    print(f"[corpus ] {len(corpus)} documents, {n_sents:,} sentences (frozen May 2026 harvest)")

    # ---------------------------------------------------------------- embed
    A = model.encode([a["sentence"] for a in anchors], normalize_embeddings=True,
                     convert_to_numpy=True, show_progress_bar=False)

    align_out = MATRIX_DIR / f"sprint1_alignment_full_{TAG}.jsonl"
    counts: dict[tuple[str, str], int] = defaultdict(int)
    doc_counts: dict[tuple[str, str], int] = defaultdict(int)
    doc_iso: dict[str, str] = {}
    n_aligned = 0
    with align_out.open("w", encoding="utf-8") as fo:
        for doc_id, sents in corpus.items():
            texts = [s["text"] for s in sents]
            if not texts:
                continue
            E = model.encode(texts, batch_size=args.batch_size, normalize_embeddings=True,
                             convert_to_numpy=True, show_progress_bar=False)
            S = E @ A.T                       # cosine (both L2-normalised)
            best = S.argmax(axis=1)
            best_score = S[np.arange(len(texts)), best]
            iso = sents[0].get("iso2", doc_id.split("-")[0])
            doc_iso[doc_id] = iso
            for i, s in enumerate(sents):
                if best_score[i] < args.threshold:
                    continue
                a = anchors[best[i]]
                rec = {
                    "doc_id": doc_id, "iso2": iso, "sent_idx": s.get("sent_idx", i),
                    "text": s["text"], "anchor_id": a["anchor_id"], "aspect": a["aspect"],
                    "level": "", "score": float(best_score[i]),
                }
                fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
                counts[(iso, a["anchor_id"])] += 1
                doc_counts[(doc_id, a["anchor_id"])] += 1
                n_aligned += 1
            print(f"  {doc_id:<8} {len(texts):>6} sents  aligned so far {n_aligned:>7,}")
    print(f"[align  ] {n_aligned:,} / {n_sents:,} = {100*n_aligned/n_sents:.1f}% aligned @ {args.threshold}")
    print(f"[out    ] {align_out}")

    # ---------------------------------------------------------------- matrices
    country_order = [c for c in load_country_order() if any(k[0] == c for k in counts)]

    def write_matrix(keys: list[str], cnt: dict, prefix: str) -> None:
        for kind in ("counts", "pct"):
            out = MATRIX_DIR / f"{prefix}_{kind}_{TAG}.csv"
            with out.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["key"] + anchor_ids + ["total_aligned"])
                for k in keys:
                    row = [cnt[(k, a)] for a in anchor_ids]
                    tot = sum(row)
                    if kind == "pct":
                        row = [round(100 * v / tot, 2) if tot else 0.0 for v in row]
                    w.writerow([k] + row + [tot])
            print(f"[out    ] {out}")

    write_matrix(country_order, counts, "sprint1_25x4")
    write_matrix(sorted(doc_iso.keys()), doc_counts, "sprint1_by_doc")

    # ---------------------------------------------------------------- cluster
    pct_path = MATRIX_DIR / f"sprint1_25x4_pct_{TAG}.csv"
    countries, rows, totals = [], [], []
    with pct_path.open(newline="", encoding="utf-8") as f:
        rd = csv.reader(f); hdr = next(rd)
        for r in rd:
            countries.append(r[0]); rows.append([float(x) for x in r[1:-1]]); totals.append(int(r[-1]))
    P = np.array(rows)
    keep = np.array([t >= args.min_aligned for t in totals])
    excl = [(c, t) for c, t, k in zip(countries, totals, keep) if not k]
    if excl:
        print(f"[filter ] excluded (n<{args.min_aligned}): " + ", ".join(f"{c}(n={t})" for c, t in excl))
    countries = [c for c, k in zip(countries, keep) if k]
    P = P[keep]; P = P / P.sum(axis=1, keepdims=True)
    H = hellinger(P)

    dist_csv = CLUSTER_DIR / f"hellinger_dist_{TAG}.csv"
    with dist_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow([""] + countries)
        for i, c in enumerate(countries):
            w.writerow([c] + [f"{H[i, j]:.4f}" for j in range(len(countries))])
    print(f"[out    ] {dist_csv}")

    condensed = squareform(H, checks=False)
    sil_rows = []
    labels_by = {}
    for method in ("ward", "average"):
        Z = linkage(condensed, method=method)
        for K in range(2, 7):
            lab = fcluster(Z, K, criterion="maxclust")
            sil = silhouette_score(H, lab, metric="precomputed") if len(set(lab)) > 1 else float("nan")
            sil_rows.append((method, K, sil))
            labels_by[(method, K)] = lab
            out = CLUSTER_DIR / f"clusters_{TAG}_{method}_K{K}.csv"
            with out.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["country", "cluster", "n_aligned"])
                tot_kept = [t for t, k in zip(totals, keep) if k]
                for c, l, t in zip(countries, lab, tot_kept):
                    w.writerow([c, int(l), t])
        if method == "ward" and not args.no_plot:
            try:
                import matplotlib; matplotlib.use("Agg")
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(10, 5))
                dendrogram(Z, labels=countries, ax=ax, leaf_font_size=9)
                ax.set_title("OECD–EC FINAL (June 2026) anchors — Ward linkage on Hellinger distance")
                plt.tight_layout(); fig.savefig(CLUSTER_DIR / f"dendrogram_{TAG}_ward.png", dpi=150); plt.close(fig)
                print(f"[out    ] {CLUSTER_DIR / f'dendrogram_{TAG}_ward.png'}")
            except Exception as e:
                print(f"[warn   ] dendrogram plot skipped: {e}")

    sil_csv = CLUSTER_DIR / f"silhouette_{TAG}.csv"
    with sil_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["linkage", "K", "silhouette"])
        for m, K, s in sil_rows: w.writerow([m, K, f"{s:.4f}"])
    print(f"[out    ] {sil_csv}")
    print()
    print("Silhouette (final anchors):")
    for m, K, s in sil_rows:
        print(f"  {m:<8} K={K}  {s:.4f}")

    # ---------------------------------------------------------------- compare draft vs final (Ward K=2)
    draft_k2 = CLUSTER_DIR / "clusters_oecd_ward_K2.csv"
    draft = {}
    if draft_k2.exists():
        with draft_k2.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f): draft[r["country"]] = int(r["cluster"])
    final_lab = labels_by[("ward", 2)]
    # Orient cluster IDs so that "1" = the MINORITY cluster (the deviating group)
    # and "2" = the majority. (Earlier version keyed on KR's cluster, which is
    # misleading when KR sits in the majority — fixed 2026-09-04.)
    def orient(lab_map: dict[str, int]) -> dict[str, int]:
        if not lab_map: return lab_map
        from collections import Counter
        minority = min(Counter(lab_map.values()).items(), key=lambda kv: (kv[1], kv[0]))[0]
        return {c: (1 if l == minority else 2) for c, l in lab_map.items()}
    final_map = orient(dict(zip(countries, [int(x) for x in final_lab])))
    draft_map = orient(draft)
    cmp_csv = CLUSTER_DIR / "oecd_draft_vs_final_comparison.csv"
    with cmp_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["country", "draft_2025_ward_K2", "final_2026_ward_K2", "changed"])
        for c in load_country_order():
            d = draft_map.get(c, ""); fn = final_map.get(c, "")
            w.writerow([c, d, fn, "YES" if (d != "" and fn != "" and d != fn) else ""])
    print(f"[out    ] {cmp_csv}  (1 = minority/deviating cluster, 2 = majority)")
    print()
    dev_draft = sorted(c for c, l in draft_map.items() if l == 1)
    dev_final = sorted(c for c, l in final_map.items() if l == 1)
    print(f"Minority (deviating) cluster — DRAFT (May 2025):  {dev_draft}")
    print(f"Minority (deviating) cluster — FINAL (June 2026): {dev_final}")
    print(f"KR and IE both in the FINAL minority cluster: {('KR' in dev_final) and ('IE' in dev_final)}")
    print(f"Added:   {sorted(set(dev_final) - set(dev_draft))}")
    print(f"Dropped: {sorted(set(dev_draft) - set(dev_final))}")

    # ---------------------------------------------------------------- draft outputs: hash after
    h_after = sha256_of(draft_files)
    same = all(h_before.get(k) == h_after.get(k) for k in h_before)
    print()
    print(f"[hash   ] draft (May 2025) outputs unchanged by this run: {same}")
    if not same:
        print("[hash   ] ** WARNING: a draft output file changed — investigate before reporting **")

    # ---------------------------------------------------------------- verification + extension
    print()
    print("[next   ] run: python scripts/06_oecd_final/verify_oecd_final.py   (Table 3, silhouettes, A3 checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
