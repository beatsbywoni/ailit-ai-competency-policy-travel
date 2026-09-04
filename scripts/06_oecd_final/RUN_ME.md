# OECD–EC final-framework re-run — one-line local execution

**Why this runs locally:** the Cowork sandbox cannot reach huggingface.co (proxy 403), so the
`paraphrase-multilingual-mpnet-base-v2` model must load from your Mac's HF cache (it was cached
when Sprint 1 ran in May 2026). Everything else (corpus, anchors, clustering) is in the repo.

**What it does:** embeds the 36,098 frozen corpus sentences once, aligns them to the 4 FINAL
OECD–EC anchors (`anchors/oecd_ai_literacy_2026_final.csv`, extracted verbatim from
DOI 10.1787/65cd27d4-en pp. 26/32/36/40), builds the 25×4 adherence matrix, runs Hellinger +
Ward/average + K=2–6 silhouette, and prints a draft-vs-final comparison of the deviating set.

**Runtime:** ~5–15 min on Apple Silicon CPU (36K sentences). No GPU needed.

## Run

```bash
cd ~/Desktop/AILIT_TRAVEL/ailit-ai-competency-policy-travel
source .venv/bin/activate        # or whatever env you used for Sprint 1
python scripts/06_oecd_final/run_oecd_final.py
```

If the model is not cached and you have internet, it will download (~1 GB) on first run.

## What to send back / what I'll read from the mounted folder

The script writes everything into the repo, so I can read it directly once you tell me it finished:

- `data/clustering/oecd_draft_vs_final_comparison.csv`  ← the headline: did {KR, IE} hold?
- `data/clustering/silhouette_oecd_final.csv`
- `data/adherence_matrix/sprint1_25x4_pct_oecd_final.csv`
- `data/clustering/clusters_oecd_final_ward_K2.csv`

Just paste the last ~8 lines of the terminal output (the "Deviating set — DRAFT / FINAL" block)
into the chat and I'll take it from there.

## Nothing is overwritten

All outputs carry the `_oecd_final` suffix. The May 2025 draft results (`_oecd`) stay untouched
so Appendix D can report both side by side.
