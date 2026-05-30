# AILIT_TRAVEL — Replication Archive

> Replication archive for a manuscript under anonymous peer review at *Computers & Education*.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.PLACEHOLDER.svg)](https://doi.org/10.5281/zenodo.PLACEHOLDER) <!-- replaced at publication -->
[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)

## One-line summary

A sentence-embedding-based cross-national analysis of how 25 national AI-in-education policy texts (67 documents, 9 languages, 2017–2026) take up the conceptual architecture of three independent AI competency frameworks: the UNESCO AI Competency Framework for Students (12 anchors), the UNESCO AI Competency Framework for Teachers (5 anchors), and the OECD–European Commission AI Literacy Framework (4 anchors).

## Reproduce the headline numbers

```bash
# Clone URL: see manuscript Data availability statement.
cd ailit-ai-competency-policy-travel
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Raw policy documents are not redistributed in this archive. Re-harvest the
# corpus from primary sources using the URLs in data/corpus_inventory/.
# See docs/replication.md for the full end-to-end procedure.

# Build adherence matrices, run clustering, and produce the six-module
# robustness battery:
bash run_sprint1_pipeline.sh
bash run_phase2_step1.sh
bash run_phase2_module6.sh
bash run_phase3_step1.sh
bash run_phase3_step2.sh
```

For end-to-end reproduction (corpus harvest → embedding → alignment → clustering → robustness → figures), see [docs/replication.md](docs/replication.md).

## Repository contents

| Folder | Contents |
|--------|----------|
| `anchors/` | 21 anchor sentences (12 UNESCO student v2 + 5 UNESCO teacher + 4 OECD–EC) as CSV |
| `scripts/01_corpus/` | Shell scripts for primary-source harvest by country |
| `scripts/02_pipeline/` | PDF→text extraction, sentence segmentation, embedding, alignment |
| `scripts/03_analysis/` | Adherence matrix builder, Hellinger clustering, figure generators |
| `scripts/04_robustness/` | Six-module robustness battery (inverse weighting, LOO, bootstrap, uniform-cap, temporal cohort, discriminant validity) |
| `scripts/05_validation/` | Anchor cohesion analysis, off-domain and hard-negative discriminant tests |
| `data/corpus_inventory/` | Source URLs, document genre, language metadata, access dates |
| `data/adherence_matrix/` | Country × anchor percentage tables (CSV; raw per-sentence alignment outputs excluded — see `.gitignore`) |
| `data/clustering/` | Hellinger distance matrices, dendrograms, K=2 cluster assignments |
| `data/robustness/` | Per-module robustness outputs |
| `data/validation/` | Anchor cohesion matrix, off-domain corpus results |
| `figures/` | Final figure assets (PNG) |
| `docs/manuscript.md` | Anonymised manuscript (author block withheld during peer review) |
| `docs/replication.md` | End-to-end reproduction guide |
| `notebooks/` | Exploratory Jupyter notebooks (not required for replication) |

## Code vs data licensing

- Code: MIT License — see [LICENSE](LICENSE)
- Data: CC BY 4.0

## Citation

Citation metadata is withheld during anonymous peer review. Upon acceptance, this archive will be deposited on Zenodo with a permanent DOI, and the BibTeX entry and `CITATION.cff` will be populated with the full manuscript citation.

## Contact

Code, data, or replication issues — file an issue on the anonymous mirror linked in the manuscript Data availability section.
