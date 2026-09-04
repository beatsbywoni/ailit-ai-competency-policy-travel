# OECD–EC final-framework re-run — how to run locally

The sandbox cannot reach the Hugging Face Hub, so the embedding step runs on the author's Mac
(model already cached from the pre-specified runs). Two scripts, run in order from the repo root:

```bash
cd ~/Desktop/AILIT_TRAVEL/ailit-ai-competency-policy-travel
source .venv/bin/activate
python scripts/06_oecd_final/run_oecd_final.py 2>&1 | tee /tmp/oecd_final_run.log
python scripts/06_oecd_final/verify_oecd_final.py 2>&1 | tee /tmp/oecd_final_verify.log
```

What `run_oecd_final.py` does (2026-09-04 fix-round version)

1. Hashes the pre-specified draft (May 2025) outputs before and after — they must be unchanged.
2. Loads the encoder and **resolves the four final anchors by rule**: each anchor is the longest run of
   *initial* sentences of the verbatim domain-opener paragraph (`paragraph_full` column of
   `anchors/oecd_ai_literacy_2026_final.csv`) that fits the encoder's 128-token window. It prints the
   token count of every anchor, rewrites the CSV's `anchor_sentence` / `sentences_used` columns if
   they differ from the rule, and prints the token lengths of the pre-specified anchor sets for the record.
3. Embeds the frozen corpus, aligns at 0.35, writes all `*_oecd_final*` outputs (draft outputs untouched).
4. Prints the K = 2 Ward partition with "1" = the *minority* cluster (earlier version keyed on Korea's
   cluster, which read misleadingly when Korea sits in the majority).

`verify_oecd_final.py` needs no model: it recomputes Table 3, the Hellinger matrix, silhouettes, the
Estonia-excluded and n ≥ 100 re-clusterings, mean pairwise Hellinger distances (draft / final / UNESCO
student / UNESCO teacher) and the Korea/Ireland distances to the canonical centroid, and writes
`data/clustering/oecd_final_verification.{json,md}`.

Paste both logs back; the manuscript numbers (Table 3, Appendix D, E.7a, Results/Discussion sentences)
are then patched from `oecd_final_verification.md`.
