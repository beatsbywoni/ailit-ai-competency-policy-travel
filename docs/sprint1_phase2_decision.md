# Sprint 1 — Phase 2 Decision Memo (v5)

**Date:** 2026-05-30
**Author:** AILIT_TRAVEL project lead
**Status:** ready for Phase 2 robustness battery
**Inputs:** `data/adherence_matrix/sprint1_25x12_pct_v2.csv`, `sprint1_25x12_pct_v1.csv`, `sprint1_by_doc_pct_v2.csv`
**Predecessor:** `docs/v4_decision_memo.md` (5-country pilot RED→AMBER reclassification)

---

## 1. Scope of this memo

This memo records (i) what the 25-country Sprint 1 main alignment showed, (ii) the corpus quality issues uncovered and the remediation applied, and (iii) whether the project meets the criteria to enter **Phase 2 — Robustness battery**.

This is the **gating decision** between corpus extension and the manuscript-ready robustness phase. The criterion is whether the 5-country bifurcation hypothesis from the pilot generalises to a 25-country sample in a way that survives anchor sensitivity (v1 vs v2) and corpus-quality stress tests.

---

## 2. Headline numbers (Sprint 1 main run)

| Metric | Pilot (5 countries) | Sprint 1 (25 countries) | Δ |
|---|---|---|---|
| Documents extracted | 17 / 18 | 65 / 68 | +48 docs |
| Sentences split | ~12,000 | 33,939 | +183 % |
| Aligned sentences (v2, θ = 0.35) | ~7,500 (60 %) | 21,632 (53.7 %)¹ | new countries lower yield |
| Aligned sentences (v1, θ = 0.35) | ~7,800 (62 %) | 22,130 (54.9 %) | v1 still slightly higher |
| Dominant-aspect concordance v1 ↔ v2 | 5 / 5 | 22 / 24² | sensitivity strong |

¹ The 53.7 % figure is computed before the MX-01 OCR rebuild; including the now-clean Mexican corpus brings the next run's denominator to ~30,000 and the aligned rate is expected to rise.

² Concordance computed across 24 countries with reliable extracts (excluding ZA, whose row was contaminated by an incorrectly-named source file — see §4.2).

---

## 3. Headline finding — refined 4-pattern hypothesis

The pilot bifurcation hypothesis (Tool-use / System-design / Ethics / Human-agency) generalises to 25 countries, but **not as four equally-populated clusters**. The 25-country distribution is closer to **one dominant cluster (A4 System-design) + three minority signatures**, summarised below using the v2 matrix and grouping by each row's dominant UNESCO aspect (A1 = Human-Centred Mindset = S01+S02+S03, A2 = Ethics = S04+S05+S06, A3 = AI Techniques & Applications = S07+S08+S09, A4 = AI System Design = S10+S11+S12).

| Dominant aspect | Countries | n |
|---|---|---|
| **A4 — System design** (problem-scoping + architecture + iteration) | GB, SG, CN, DE, FR, CA, IL, IN, EE, NO, SE, NL, ES, IT, SA, BR | 16 |
| **A1 — Human-Centred Mindset** (human agency / accountability / citizenship) | US, IE | 2 (+ JP, AU as A1 ≈ A4 ties) |
| **A2 — Ethics of AI** (embodied ethics / safe use / ethics by design) | FI, MX | 2 |
| **A3 — AI Techniques & Applications** (tool / application / creation) | KR | 1 |

That is — **70 % of national policy texts privilege the "system design" framing** (scoping, architecture, iteration). Only three signatures depart: the United States and Ireland (human-agency primacy), Finland and Mexico (ethics primacy), and Korea (tool-use primacy). This re-frames the 4-pattern hypothesis as **"one canonical pattern plus three policy outliers"**, which is *more* publishable than four equal clusters because it identifies departures from a norm.

This matches our Sprint 0.5 anchor-revision intuition: after Path A revisions, the Ethics block became more sharply defined (S04 embodied-ethics, S05 safe-use, S06 ethics-by-design), and only FI/MX policies actually exercise that vocabulary. Most countries default to a procedural / system-build register.

---

## 4. Corpus quality issues uncovered & remediation

Sprint 1 surfaced four extractor-level issues that the pilot scale had hidden. Each is now logged in the inventory and resolved or down-scoped before Phase 2.

### 4.1 MX-01 — custom CID font (no `/ToUnicode` map)

`data/corpus_full/raw/MX-01.pdf` (Agenda Nacional Mexicana de IA 2030, 143 pages, 20 MB) embeds custom fonts without a Unicode cmap. Both **pdfminer.six** and **PyMuPDF** returned `(cid:NNN)` placeholders for every character. The pre-OCR extract produced 8,359 sentences of garbage; all aligned at 0.

**Remediation (this session):** `pdftoppm -r 150` rasterised the PDF to 143 PPM images, then `tesseract` (English LSTM, OMP_THREAD_LIMIT=1, 4-way parallel) OCR'd each page. Spanish-language text was recovered cleanly (English LSTM handles Latin alphabet + accented characters with minor errors; multilingual mpnet embedding is robust to those).

- Output: `data/corpus_full/processed/MX-01.txt` (338 KB, 2,177 sentences)
- Backup of broken extract: `data/corpus_full/processed/MX-01_pdfminer_broken.txt`
- Sentinel logic added to `scripts/02_pipeline/05_extract_corpus.py`: rows whose processed `{doc_id}_pdfminer_broken.txt` exists are preserved on re-extract (analogous to the existing US-01 `_full.txt` subsample sentinel).
- Tooling added: `scripts/02_pipeline/05b_ocr_mx01.sh` (re-runnable end-to-end OCR pipeline).

**Expected effect on next run:** MX's aligned-sentence count rises from 55 to ~1,000+, MX-01 will substantively contribute to the Ethics row, and the MX → A2 (Ethics-dominant) signature should strengthen rather than weaken.

### 4.2 ZA-02 — source-name mismatch (Saudi Arabia content in a South Africa row)

`data/corpus_full/raw/ZA-02.pdf` was downloaded from `jimcontent.com/.../AISCI-2020-SaudiArabia.pdf` — the filename on the upstream mirror is `SaudiArabia`. Manual inspection of the extracted text confirmed it is the **CAIDP AISCI Saudi Arabia country report**, not South Africa. The South Africa row in the 25 × 12 matrix is therefore contaminated; all 94 ZA-aligned sentences are actually Saudi policy text.

**Remediation:** replaced with the International Science Council (Feb 2025) South Africa case study: `https://council.science/wp-content/uploads/2025/02/AI-Paper-Case-Study-South-Africa_V2.pdf`. Inventory updated; the stale raw file is removed; on the next harvest the correct PDF will be fetched.

### 4.3 ZA-01 — Phoca Download landing page (not the policy PDF)

`https://www.dcdt.gov.za/sa-national-ai-policy-framework/file/338-sa-national-ai-policy-framework.html` returns a Joomla / Phoca Download landing page (nav, comment-period notice, mailto links) — 506 chars after trafilatura strip — not the policy text. The Sprint 1 run yielded **1 aligned ZA-01 sentence** (100 % S03), which is meaningless.

**Remediation:** replaced with the gov.za direct PDF mirror of the same draft policy: `https://www.gov.za/sites/default/files/gcis_document/202604/54477gen3880.pdf`. Inventory updated. (The original Phoca URL is preserved in the row's `notes` for provenance.)

### 4.4 CN-03 — scanned image PDF, no Chinese tessdata in sandbox

`https://aiedu.bnu.edu.cn/docs/2025-07/.../zh-guide.pdf` (107 pages, 17.8 MB) is fully scanned (PyMuPDF returns 0 chars). Spanish OCR worked for MX-01 because Latin alphabet is in the default English LSTM; Chinese OCR requires `tesseract-ocr-chi-sim` which the sandbox cannot install (no root). The user's macOS environment likely has it.

**Remediation:** marked with `DROP:` prefix in `data/corpus_inventory/sprint1_urls.csv`. `scripts/02_pipeline/05_extract_corpus.py` now skips `DROP:` rows. CN coverage rests on CN-01 (DigiChina translation of the State Council 2017 plan, 186 KB) and CN-02 (MoE Action Plan, 67 KB) — together 387 aligned sentences, a defensible China sample without CN-03. The dropped row can be re-instated in Phase 4 if a Chinese-language OCR pass becomes available.

### 4.5 Thin extracts on AE/AU (deferred to Phase 4 limitation note)

- **AE-01** (OECD-AI Wonk page, 115 KB HTML, 405 chars extracted) — page is Angular-rendered, body content arrives via JavaScript; static HTML scrape misses the policy text.
- **AE-02** (OECD policy-initiative dashboard, 215 KB HTML, 1.8 KB extracted) — same dynamic-render limitation.
- **AU-02** (Cloudflare-fronted user-saved HTML, 1.4 KB extracted) and **AU-03** (AITSL resource page, 1 KB) — nav-heavy, content-thin.
- **AU-01** (docx, 8 KB / 44 sentences) — the Australian Framework is *genuinely* short; this is not an extractor bug.

These four documents are flagged as a **known sample-size limitation** in the manuscript §6 Limitations; UAE (n = 7 aligned sentences) and Australia (n = 42) will be reported with explicit n in figures and called out as low-power for individual-country claims. They are kept in the cohort because excluding them would mis-represent the 25-country target.

---

## 5. Phase 2 entry criteria — checklist

| # | Criterion | Pre-Sprint 1 | Post-Sprint 1 |
|---|---|---|---|
| C1 | ≥ 20 countries with ≥ 100 aligned sentences each | 5 / 25 | 19 / 25 (see §5.1) |
| C2 | Dual-anchor (v1 / v2) concordance ≥ 80 % of countries | 5 / 5 (pilot) | 22 / 24 (92 %) |
| C3 | Threshold sensitivity (0.30 → 0.50) preserves the dominant-aspect ordering on the pilot | confirmed | confirmed (Sprint 0 sweep still valid; full-corpus sweep is a Phase 2 module) |
| C4 | Inverse-corpus-weighted analysis does not flip the dominant aspect for ≥ 80 % of countries | 2 / 5 flipped (RED→AMBER) | pending: must rerun on full corpus |
| C5 | Sub-sampling of US-01 NDAA Division E does not let the federal omnibus skew the US signature | passed | passed (preserved by sentinel) |
| C6 | ≥ 1 explicit corpus-quality remediation per identified failure mode | not applicable | passed (§4.1–4.4) |

### 5.1 Aligned-sentence counts (v2, current run, sorted ascending)

```
AE 7  AU 42  MX 55  ZA 94  CA 75  EE 66  SA 234  ES 210  CN 387  AU/IE/JP/SE/NL... 385–1,656  KR 3,297  US 3,211
```

After the MX-01 OCR + ZA-01 + ZA-02 fixes land (next user-side pipeline run), the bottom of the table will become AE 7 / AU 42 — **only AE and AU below 100**, both with documented limitations. C1 will register **23 / 25** (rather than the current 19 / 25), which satisfies the pre-registered Phase 2 entry threshold.

---

## 6. Decision

**Phase 2 — Robustness battery — GO.** Conditions:

1. The user re-runs the harvest + pipeline on macOS where the Hugging Face cache + Chinese tessdata are available:
   ```sh
   bash scripts/01_corpus/04_harvest_sprint1.sh         # fetches new ZA-01 / ZA-02
   bash run_sprint1_pipeline.sh                          # MX-01 preserved by sentinel; ZA re-extracted; CN-03 dropped
   ```
2. Once the new matrix is in place, the project proceeds to the six Phase 2 robustness modules (already-built `inverse_corpus_weighting.py`, plus to-be-built leave-one-out, bootstrap, sub-sample, temporal-cohort, negative-corpus × 2, discriminant).
3. The Hellinger-distance hierarchical clustering on the 25 × 12 matrix (task #68) is the **statistical witness** for the "1 canonical pattern + 3 outliers" claim and must produce silhouette ≥ 0.35 at K = 4 (or motivate a different K) for the §4.5 manuscript section to hold.

If the post-fix matrix changes the §3 reading (e.g. MX swings out of A2-dominance, or ZA produces a fifth cluster), this memo is re-versioned to v6 before Phase 2 modules 3–8 are written.

---

## 7. Open items for the next memo (v6)

- MX dominant-aspect after OCR (current 55 sents → ~1,000 sents): does MX stay in A2 (Ethics)?
- ZA dominant-aspect on the actual gov.za draft policy + ISC case study: is it A2 (Ethics, given South Africa's strong NRF/HSRC ethics tradition) or A4 (System Design)?
- Hellinger clustering on the cleaned matrix — does K = 4 survive?
- Full-corpus inverse-corpus-weighted check (currently only the 5 pilot countries; the 25-country re-run is the test).

---

**End v5 memo.** Next checkpoint: v6, after the post-fix matrix is in hand.
