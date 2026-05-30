# Replication guide

End-to-end procedure for reproducing every numeric claim in the manuscript from primary sources. Designed for a reviewer or independent researcher with no privileged access to the original corpus.

The replication has three logical phases: (A) corpus harvest from primary URLs, (B) embedding and alignment pipeline, (C) clustering and the six-module robustness battery. The principal UNESCO student-framework analysis can be reproduced from `bash run_sprint1_pipeline.sh` once Phase A is complete; the cross-framework replication and the robustness battery are wrapped in additional one-line scripts described in §3 below.

---

## 0. Prerequisites

- macOS or Linux. The pipeline was developed on macOS 14 and tested on Ubuntu 22.04.
- Python 3.11+.
- 8 GB of free RAM (the sentence-transformer model occupies ~500 MB; sentence-level embedding of the 36 098-sentence corpus uses approximately 1.5 GB peak).
- Internet access for two purposes: (i) downloading the `paraphrase-multilingual-mpnet-base-v2` model from Hugging Face on first run; (ii) re-harvesting source documents from the URLs in `data/corpus_inventory/sprint1_urls.csv`.
- Approximately 4 GB of disk for source PDFs, extracted text, and embeddings.

Install dependencies:

```bash
cd ailit-ai-competency-policy-travel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` pins `sentence-transformers`, `scikit-learn`, `scipy`, `numpy`, `pandas`, `pdfminer.six`, `trafilatura`, and `python-docx` to versions consistent with the manuscript.

---

## 1. Phase A — Corpus harvest

The original national policy documents are not redistributed in this archive (see manuscript §3.1 and Data availability statement). The harvest re-downloads each document from its primary government or ministry portal using the URLs in `data/corpus_inventory/sprint1_urls.csv`.

```bash
bash scripts/01_corpus/harvest_sprint1.sh
```

Expected runtime: 15–25 minutes on a residential connection. Eight documents that required manual handling at the time of the original harvest are listed in the inventory with the `MANUAL` prefix; for these documents the inventory provides the alternative source URL and, where relevant, the format (PDF vs HTML) the script expects.

After harvest, extract text:

```bash
python3 scripts/02_pipeline/04_pdf_to_text.py
```

Verify the resulting corpus by file count and sentence-segmentation total:

```bash
ls data/corpus_full/processed/*.txt | wc -l       # expect: 67
python3 scripts/02_pipeline/06_sentence_split.py
ls data/corpus_full/processed/*.sentences.jsonl | wc -l   # expect: 67
```

A small number of source documents may have been revised by their publishers since the original harvest; in that case, the precise sentence counts may differ slightly from the manuscript's figures by a fraction of a percent. The cluster identity of every country is robust to this small drift; see §4.6 Module 3 (bootstrap CIs) in the manuscript.

---

## 2. Phase B — Embedding and alignment

Embed every sentence using the multilingual MPNet model:

```bash
python3 scripts/02_pipeline/07_embed.py
```

Expected runtime: 10–15 minutes on a CPU; <2 minutes on a CUDA GPU.

Align every sentence against the 21 anchor sentences. Three anchor frameworks are supplied:

```bash
# UNESCO Student Framework (12 anchors, version 2 — principal analysis)
python3 scripts/02_pipeline/08_anchor_align.py \
    --anchor-csv anchors/anchors_student_v2.csv \
    --threshold 0.35

# UNESCO Teacher Framework (5 anchors — cross-framework replication)
python3 scripts/02_pipeline/08_anchor_align.py \
    --anchor-csv anchors/anchors_teacher.csv \
    --threshold 0.35 \
    --tag teacher

# OECD-EC AI Literacy Framework (4 anchors — cross-framework replication)
python3 scripts/02_pipeline/08_anchor_align.py \
    --anchor-csv anchors/anchors_oecd.csv \
    --threshold 0.35 \
    --tag oecd
```

Build adherence matrices:

```bash
python3 scripts/03_analysis/build_adherence_matrix.py --tag v2
python3 scripts/03_analysis/build_adherence_matrix.py --tag teacher
python3 scripts/03_analysis/build_adherence_matrix.py --tag oecd
```

Each command writes a country × anchor CSV file to `data/adherence_matrix/`.

---

## 3. Phase C — Clustering, robustness, and figures

Each analytical block is wrapped in a one-line shell script. The scripts are idempotent — re-running with existing outputs leaves them unchanged.

### 3.1 Principal UNESCO student analysis (manuscript §4.3, §4.4)

```bash
bash run_sprint1_pipeline.sh
```

Reproduces: alignment yield, dominant-aspect classification, K=2 Ward silhouette (0.379), cluster identity `{KR, IE}`.

### 3.2 Cross-framework replication (manuscript §4.5)

```bash
bash run_phase3_step1.sh    # UNESCO teacher + OECD silhouettes and partitions
bash run_phase3_step2.sh    # framework-pair agreement + replication score
```

Reproduces: teacher silhouette 0.473 with cluster `{KR, US, IE}`; OECD silhouette 0.483 with cluster `{KR, FI, US, CA, SE, IE}`; pairwise agreement 91% / 74% / 74%; replication score 3/3 for Korea and Ireland.

### 3.3 Six-module robustness battery (manuscript §4.6)

```bash
bash run_phase2_step1.sh        # modules 1–5: weighting, LOO, bootstrap, uniform-cap, temporal cohort
bash run_phase2_module6.sh      # module 6: discriminant validity (off-domain + hard-negative)
```

Reproduces the per-module statistics reported in §4.6, including the bootstrap 95% confidence intervals on KR-canonical (+27.19 pp [25.53, 28.89]) and IE-canonical (+20.33 pp [18.04, 22.74]) differences, the 100% Korea / 100% Ireland deviating-cluster preservation under uniform-cap N=500 sub-sampling, and the 0.0% off-domain alignment / 68.9% hard-negative alignment rates.

### 3.4 Anchor cohesion (manuscript §3.3, §4.2)

```bash
python3 scripts/05_validation/anchor_distance_check.py --anchor-csv anchors/anchors_student_v2.csv
```

Reproduces the 21 × 21 cosine distance matrix and the within-aspect to between-aspect cohesion ratios reported in §4.2 (S04 1.16, S05 1.08, S06 1.04).

### 3.5 Figures (manuscript Figs. 1, 2)

```bash
python3 scripts/03_analysis/figure_cross_framework.py
python3 scripts/03_analysis/figure_robustness_summary.py
```

Reproduces `data/clustering/figure_cross_framework_v2.png` (three Ward dendrograms + heatmap) and `data/clustering/figure_robustness_summary_v2.png` (forest plot for KR and IE across modules 1–5).

---

## 4. Sensitivity analyses

The manuscript reports two sensitivity analyses that require small parameter changes to the principal pipeline.

### 4.1 Anchor-version sensitivity (manuscript §4.6 Module 4)

Run the principal pipeline with the archived version-one anchors:

```bash
python3 scripts/02_pipeline/08_anchor_align.py \
    --anchor-csv anchors/anchors_student_v1_archived.csv \
    --threshold 0.35 \
    --tag v1
python3 scripts/03_analysis/build_adherence_matrix.py --tag v1
python3 scripts/03_analysis/hellinger_cluster.py --tag v1
```

Reproduces the 95.9% full-data K = 2 partition recovery rate (vs 99.9% under v2) reported in §4.6 Module 4.

### 4.2 Threshold sensitivity (manuscript §4.3)

```bash
for THR in 0.30 0.35 0.40 0.45 0.50; do
    python3 scripts/02_pipeline/08_anchor_align.py \
        --anchor-csv anchors/anchors_student_v2.csv \
        --threshold "$THR" \
        --tag "thr_$THR"
done
python3 scripts/04_robustness/threshold_sensitivity.py
```

Reproduces the monotonic decrease in alignment rate (39.3%, 27.8%, 19.6%, 13.6%, 9.3%) reported in §4.3.

---

## 5. Troubleshooting

### 5.1 `paraphrase-multilingual-mpnet-base-v2` download fails

The model is approximately 500 MB. On first run it is fetched from Hugging Face. If the download is interrupted, delete `~/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-mpnet-base-v2/` and re-run.

### 5.2 A source URL has changed since the original harvest

The corpus inventory in `data/corpus_inventory/sprint1_urls.csv` records the access date for every URL. Government and ministry portals occasionally restructure their URL schemes. The `MANUAL` prefix in the inventory marks documents for which an alternative URL was used at the time of the original harvest; reviewers encountering a fresh URL change can substitute a comparable document from the same publisher and update the inventory's URL column. The author's experience over the May 2026 harvest was that approximately one document in seven required URL substitution at some point during the harvest cycle.

### 5.3 Different sentence count

Sentence segmentation is sensitive to the precise content of the source documents. If your harvest produces a sentence count that differs from 36 098 by more than 2%, check whether (a) the source document version differs from the inventory's access date, (b) the `pdfminer.six` version differs from `requirements.txt`, or (c) one or more documents failed silent extraction (look for files smaller than 5 KB in `data/corpus_full/processed/*.txt`).

The bootstrap confidence intervals in §4.6 Module 3 quantify the sensitivity of every headline number to within-country sentence sampling; the cluster identity of Korea and Ireland is robust to all sentence-count drifts encountered during pipeline development.

---

## 6. Expected outputs at the end of a clean run

```
data/adherence_matrix/sprint1_adherence_v2.csv       (25 × 12)
data/adherence_matrix/sprint1_adherence_teacher.csv  (25 × 5)
data/adherence_matrix/sprint1_adherence_oecd.csv     (25 × 4)
data/clustering/hellinger_v2_ward.png                (Ward dendrogram, student framework)
data/clustering/dendrogram_teacher_ward.png
data/clustering/dendrogram_oecd_ward.png
data/clustering/figure_cross_framework_v2.png        (Manuscript Figure 1)
data/clustering/figure_robustness_summary_v2.png     (Manuscript Figure 2)
data/robustness/bootstrap_ci_v2.csv
data/robustness/loo_assignments_v2.csv
data/robustness/uniform_cap_recovery_v2.csv
data/robustness/temporal_cohort_v2.csv
data/validation/anchor_cohesion_v2.csv
data/validation/discriminant_offdomain.csv
data/validation/discriminant_hardneg.csv
```

If every file above exists and is non-empty, the replication is complete.
