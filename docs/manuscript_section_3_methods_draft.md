# 3. Methods

This section describes the corpus construction, anchor extraction and validation, multilingual text pipeline, embedding and alignment procedure, adherence matrix construction, Hellinger-distance clustering, six-module robustness battery, cross-framework replication design, and reproducibility infrastructure. The analytical strategy was pre-specified in a planning document drafted in May 2026 (file `AILIT_TRAVEL_planning_v1.md` in the project repository); deviations from that plan, where they occur, are flagged in the corresponding subsection.

## 3.1 Sampling frame and corpus selection

The sampling frame comprises 25 countries, selected to provide coverage of (a) all four OECD regional groupings (Europe, Asia–Pacific, Americas, Middle East and Africa), (b) a range of GDP-per-capita quartiles, (c) a mix of pre- and post-September 2024 publication dates relative to the UNESCO AI competency framework release, and (d) at least one publicly accessible national AI-in-education policy document per country. The list of countries was finalised before alignment results were inspected.

The corpus contains 67 documents harvested between 28 and 30 May 2026. Inclusion criteria, set during the planning phase, required that each document (i) be a national government, ministry, or government-commissioned report; (ii) address artificial intelligence either explicitly in the educational context or with substantive implications for education; and (iii) be available in full text in HTML, PDF, or .docx form from a verifiable institutional source. Eight documents that initially failed automated extraction were either replaced with alternative sources from the same publisher (n = 5; e.g., ZA-01 substituted from the South African Department of Communications portal page to the gov.za direct PDF) or extracted manually by the author (n = 3; e.g., DE-02 KI-Aktionsplan from the BMBF press release). One Chinese document (CN-03) consisting of a scanned PDF was dropped from analysis because Chinese-language OCR was outside the pipeline's automated capabilities; this exclusion is documented in §6.

The corpus design choice to focus on AI-in-education policy texts specifically, rather than general national AI strategies, distinguishes the present sample from the 24-country corpus analysed by Schiff (2022), whose study found that the instrumental value of education in supporting an AI-ready workforce dominated national AI strategy documents while AI-in-education itself was largely absent. The present corpus inverts that focus and asks how the educational dimension is articulated when it is the explicit subject of the document.

## 3.2 Verbatim anchor extraction

Three framework documents supplied the anchor sentences against which corpus sentences were aligned. The UNESCO AI Competency Framework for Students (Miao & Shiohira, 2024a) provided twelve anchors organised into a 4-aspect × 3-level matrix (human-centred mindset, ethics of AI, AI techniques and applications, AI system design, each at understand, apply, and create levels). The UNESCO AI Competency Framework for Teachers (Miao & Shiohira, 2024b) provided five anchors corresponding to the five macro-aspects (human-centred mindset, ethics of AI, AI pedagogy, AI for professional development, AI foundations). The OECD–European Commission AI Literacy Framework Review Draft of May 2025 (OECD & European Commission, 2025) provided four anchors corresponding to the four domains (engaging with AI, creating AI, managing AI, designing AI).

Anchors were extracted verbatim from each framework's principal definition paragraph for each sub-principle. The verbatim principle excluded paraphrasing or summarising of the framework text. When verbatim extraction produced two adjacent anchors with insufficient cohesive separation (defined in §3.3), the affected anchor was rewritten using only material drawn from the same framework section; these revised anchors are flagged in the project's anchor CSV files with the status `verbatim_revised`, and the rationale for each revision is documented in `anchor_revision_rationale.md`. Three of the twelve student anchors (S04, S05, S06) were revised under this procedure; the original versions are archived for sensitivity analysis under the tag `v1_archived`.

## 3.3 Anchor cohesion validation

Anchor cohesion was operationalised as the ratio of mean cosine distance within an aspect to mean cosine distance between adjacent aspects, computed on the 21-anchor distance matrix. Cohesion ratios above 1.05 were treated as adequate; below 1.00 indicated that anchors within the same aspect were further apart in the embedding space than anchors in adjacent aspects, a failure mode requiring revision. Under the v1 student anchors, AILIT-S04 and AILIT-S06 returned ratios of 0.97; revising those anchors and AILIT-S05 (Path A in `anchor_revision_rationale.md`) yielded v2 ratios of 1.16, 1.08, and 1.04 respectively. All three anchor frameworks (student v2, teacher, OECD) passed the cohesion threshold at the macro-aspect level. The full 21 × 21 cosine distance matrix is provided as Supplementary Table S1.

## 3.4 Text extraction and sentence segmentation

Documents were extracted using `pdfminer.six` 20240706 for PDFs, `trafilatura` 1.6.0 for HTML (with `include_tables=True` and `favor_recall=True`), and `python-docx` 1.2.0 for the one Australian .docx document. For one Mexican PDF (MX-01, 143 pages, custom CID fonts without a Unicode cmap), automated text extraction returned glyph codes rather than readable characters; this document was re-extracted using a `pdftoppm` to `tesseract` OCR pipeline at 150 dpi resolution. Eight languages are represented in the resulting plain-text corpus (English, Korean, Chinese, Japanese, German, French, Spanish, Italian, Portuguese).

Sentence segmentation used a multilingual regular expression matching terminal punctuation (`.!?。`) followed by whitespace, with a length filter retaining sentences between 40 and 600 characters. This range was selected based on a prior validation by the present author against a national education-policy reference corpus, which found that this window captured policy-relevant sentences while excluding headings (under 40 characters) and unsegmented blocks (over 600 characters). The full 67-document corpus produced 36,098 sentences after segmentation.

## 3.5 Sentence embedding and alignment

Embeddings were computed using `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (Reimers & Gurevych, 2019), a 109-million-parameter model trained on 50 languages that produces 768-dimensional sentence vectors. Each sentence vector was L2-normalised so that cosine similarity reduces to a dot product. Alignment proceeded by computing the cosine similarity between every corpus sentence and every anchor, then assigning each sentence to the anchor with maximum similarity. Assignments below a pre-specified threshold of 0.35 were classified as unaligned and excluded from the adherence matrix.

The threshold of 0.35 was inherited from the present author's prior validation work on national education policy texts and was specified before alignment was executed on the present corpus. A sensitivity sweep across thresholds 0.30, 0.35, 0.40, 0.45, and 0.50 is reported in §4.3 and Supplementary Table S2.

The methodological strategy of aligning policy or curriculum sentences against framework anchors via sentence embeddings has recent precedent in educational measurement. Butterfuss and Doran (2025) used a closely related approach to support content mapping of state academic standards against framework taxonomies, demonstrating that pre-trained transformer embeddings can complement subject-matter expert judgements in standards-alignment work. The present design extends this approach from within-jurisdiction standards alignment to cross-national policy adoption analysis, and adds a six-module robustness battery (§3.8) and a cross-framework replication design (§3.9) that, to the author's knowledge, have not previously been applied together to AI-in-education policy text.

## 3.6 Adherence matrix construction

For each country c and each anchor a, the count of corpus sentences from c assigned to a was tallied and divided by the total number of aligned sentences from c, yielding a row-normalised percentage. The resulting 25 × *N* adherence matrix (where *N* is 12 for the UNESCO student framework, 5 for UNESCO teacher, 4 for OECD) is the primary input to the clustering analysis in §3.7. By-document adherence matrices (67 × *N*) were also produced to support the leave-one-out and bootstrap analyses described in §3.8. All matrices are released as comma-separated value files in the data repository (§3.10).

## 3.7 Hellinger distance clustering and silhouette

Each row of the adherence matrix can be interpreted as a probability distribution over the *N* anchors. Pairwise distances between countries were computed using the Hellinger distance:

H(p, q) = (1/√2) · √[ Σ_i (√p_i − √q_i)² ]                                (Eq. 1)

which is bounded in [0, 1] and treats the anchor distribution as a categorical distribution. The Hellinger distance was selected over Jensen–Shannon, total variation, and cosine alternatives because it is a proper metric on the probability simplex, symmetric, and standard for clustering categorical-distribution data.

The 25 × 25 (or 23 × 23 after the *N* ≥ 50 alignment-count filter described below) distance matrix was then submitted to agglomerative hierarchical clustering using both Ward and average linkage as implemented in `scipy.cluster.hierarchy`. Silhouette scores were computed for K ∈ {2, 3, 4, 5, 6} using `sklearn.metrics.silhouette_score` with `metric='precomputed'` against the Hellinger distance matrix. The K value maximising the silhouette score under Ward linkage was reported as the principal partition; agreement between Ward and average linkage at the optimal K was reported as a secondary check.

Countries with fewer than 50 aligned sentences under a given anchor framework were excluded from the clustering analysis for that framework, on the grounds that Hellinger distance computed on a distribution with very few observations is dominated by sampling noise rather than substantive content. Under the UNESCO student framework this filter excluded the United Arab Emirates (n = 7) and Australia (n = 42); under the UNESCO teacher framework it additionally excluded Estonia (n = 49); under the OECD framework it excluded the United Arab Emirates (n = 6) and Australia (n = 32).

## 3.8 Robustness battery: six pre-specified modules

Six robustness checks were specified before alignment results were inspected, motivated by the §4.6 criteria laid out in the author's pre-submission methodology checklist (`ce_rigour_checklist.md` in the project repository). The six modules address distinct sources of artefactual cluster identity.

*Module 1 — Inverse-corpus weighting* recomputes each country's adherence row as the unweighted mean of its per-document rows, addressing concerns that single dominant documents (notably KR-02 at 89 % of Korea's aligned-sentence count, FI-01 at 98 % of Finland's, and FR-03 at 73 % of France's) may drive country-level cluster assignment.

*Module 2 — Leave-one-out per country* drops each country's largest single document and recomputes the cluster assignment using only the remaining documents, addressing concerns that cluster identity depends on one specific document rather than the country's overall policy posture.

*Module 3 — Bootstrap 95 % confidence intervals* resamples aligned sentences with replacement within each country, 1,000 iterations with seed 20260530, and reports percentile-method confidence intervals on per-country focal-anchor shares and on the difference between focal-country shares and the canonical-cluster mean.

*Module 4 — Uniform-cap sub-sampling* caps every country at *N* = 500 randomly-sampled aligned sentences per iteration, 1,000 iterations, and reports the cluster-assignment rate for each country across resamples. This module is the most aggressive size-correction available in the protocol.

*Module 5 — Temporal cohort split* partitions the corpus into pre- and post-September 2024 sub-corpora (corresponding to the UNESCO student framework release) and recomputes cluster assignments separately in each cohort, addressing the alternative explanation that cluster identity reflects the timing of policy text drafting relative to UNESCO's publication.

*Module 6 — Discriminant validity* aligns two negative corpora against the UNESCO student anchors: an off-domain set comprising literary fiction, military history, and biology (3,271 sentences) and a hard-negative set comprising corporate AI policy documents (328 sentences). Alignment rates substantially below the positive-corpus rate would support the construct validity of the anchor-based measurement.

## 3.9 Cross-framework replication

The cross-framework replication design re-runs the full pipeline (§§3.4–3.7) using the UNESCO teacher anchors and then the OECD AILit anchors as primary anchor spaces. This produces, for each anchor framework, an independent K = 2 cluster partition. Two summary statistics are reported. First, the framework-pair agreement rate is the proportion of eligible countries assigned to the same cluster identity by both frameworks of a given pair. Second, the country-level replication score is the count of frameworks (out of three) under which a country falls in the deviating cluster (defined as the cluster containing Korea and Ireland in the principal UNESCO student analysis). This design, to the author's knowledge, has not previously been applied to AI competency framework adoption analysis.

## 3.10 Reproducibility infrastructure

The full analytical pipeline is implemented as a series of shell-orchestrated Python scripts in the project repository. Every step is idempotent: re-running a step with existing output files leaves them unchanged. The single command `bash run_sprint1_pipeline.sh` reproduces the principal UNESCO student analysis end to end, including text extraction, sentence segmentation, embedding, alignment, adherence matrix construction, and dominant-aspect summary. Separate one-line wrappers reproduce the cross-framework replication (`run_phase3_step1.sh`, `run_phase3_step2.sh`) and each robustness module. All code, corpus inventory (with verifiable source URLs and access dates), anchor CSV files, and per-document alignment outputs are released under an open license; the persistent identifier and access URL are provided in the Data Availability statement at the end of this article.

---

[End of §3. Word count: approximately 1,820 words. References cited: Butterfuss & Doran (2025); Miao & Shiohira (2024a, 2024b); OECD & European Commission (2025); Reimers & Gurevych (2019); Schiff (2022).]
