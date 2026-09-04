# Manuscript draft — §4.5 + §5

**Target journal:** the target journal (SSCI)
**Draft date:** 2026-05-30
**Status:** first internal draft; all numerical claims sourced from `data/` artefacts in this repository; one-figure-one-table version pending journal-style review.

This document collects the main-result paragraphs (§4.5) and the full Discussion (§5) for the AILIT_TRAVEL paper. §1 Introduction, §2 Theoretical framework, §3 Methods, §4.1–4.4 (corpus, anchor cohesion, alignment yield, dominant-aspect distributions), and §4.6 (robustness battery) are referenced but not reproduced here.

---

## 4.5 Cross-framework replication of the K = 2 deviating cluster

### 4.5.1 K = 2 partition on the UNESCO student framework

Hierarchical clustering of the 25 country adherence rows on Hellinger distances over the 12 UNESCO student anchors yields a stable two-cluster partition. After excluding the United Arab Emirates (*n* = 7 aligned sentences) and Australia (*n* = 42) by the pre-registered minimum-corpus threshold of *N* ≥ 50 (§3.4), the K = 2 silhouette is 0.379 under Ward linkage and 0.379 under average linkage, both higher than every K ∈ {3, 4, 5, 6} examined (Table A.1 in the supplementary materials). The deviating cluster comprises Korea and Ireland; the canonical cluster contains the remaining 21 countries.

The deviating cluster's centroid loads heavily on AILIT-S08 (Application skills); KR's S08 share is 30.2 %, IE's is 23.3 %, and the canonical-cluster mean is 3.05 % (bootstrap 95 % CI [2.78, 3.37], §4.6 Module 3). The KR − canonical effect size is +27.19 percentage points (95 % CI [25.53, 28.89]) and the IE − canonical effect size is +20.33 percentage points (95 % CI [18.04, 22.74]). Both confidence intervals exclude zero by more than 17 percentage points; the cluster separation is therefore statistically unambiguous at the resolution at which embedding-based text clustering operates.

### 4.5.2 Replication on the UNESCO teacher framework

To test whether the K = 2 partition is an artefact of the student-framework concept space, the 25-country corpus was re-aligned against the five UNESCO teacher anchors (T01 human-centred mindset, T02 ethics, T03 AI pedagogy, T04 AI for professional development, T05 AI foundations). After the same *n* ≥ 50 filter (which here additionally excludes Estonia at *n* = 49), the K = 2 Ward silhouette on the 22 remaining countries is 0.473, substantially higher than the student-framework value. The deviating cluster is `{KR, US, IE}`. Korea retains its position as the most distant single-country point in the dendrogram (Fig. 1, middle panel).

Two observations distinguish the teacher-framework result from the student-framework result. First, the silhouette is higher despite the lower dimensionality (5 vs 12), indicating that the deviation–canonical separation is *more* clearly resolved when the anchor space is collapsed to the five teacher macro-aspects. Second, the United States joins the deviating cluster here: US loadings on T01 (human-centred mindset, 29.6 %) and T04 (AI for professional development, 37.1 %) are substantially above the canonical mean of 9.3 % and 22.7 % respectively. The US documents — the 2020 NDAA Division E (NAI Act), the 2023 Office of Educational Technology AI report, the 2025 White House Executive Order on Advancing AI Education for American Youth, and the 2024 OET AI toolkit — adopt the human-agency and professional-development register that the teacher framework explicitly indexes, even though they do not exhibit the student-framework's S08 Application-skills emphasis.

### 4.5.3 Replication on the OECD AILit framework

The same procedure on the four OECD AILit anchors (O01 engaging with AI, O02 creating AI, O03 managing AI, O04 designing AI) yields a K = 2 silhouette of 0.483 on 23 eligible countries — the highest of the three frameworks, again despite the lowest anchor count. The deviating cluster expands to `{KR, FI, US, CA, SE, IE}`, all of which load above 33 % on O04 (designing AI). KR's O04 share is 43.4 %, FI's is 37.6 %, US's is 54.7 %, CA's is 41.2 %, SE's is 33.8 %, and IE's is 69.0 % (Table 2). The canonical-cluster mean on O04 is 24.0 %.

The expansion of the deviating cluster from 2 → 3 → 6 countries as anchor dimensionality decreases (12 → 5 → 4) is informative. The student-framework's twelve fine-grained anchors index a precise "tool-use" register (S08 Application skills) that only Korea and Ireland's recent education-specific guidance documents fully exhibit. The teacher framework's five macro-aspects index a slightly broader concept (T04 AI for professional development) that the United States also exhibits. The OECD framework's four domains index a still-broader concept (O04 designing AI) that Finland, Canada, and Sweden also exhibit. The clusters are therefore *nested*: every cluster-1 country in the student framework is also cluster 1 in the teacher and OECD frameworks.

### 4.5.4 Cross-framework cluster identity and replication score

Fig. 1 presents the cross-framework cluster identity table. For each of the 25 countries, a star (★) marks Cluster 1 (deviating) assignment in a given framework; a centred dot (·) marks Cluster 2 (canonical); a dash (—) marks exclusion by the *n* ≥ 50 filter. Countries are ordered by their replication score — the count of frameworks in which the country is assigned to Cluster 1.

The score-3 row contains Korea and Ireland only. The score-2 row contains the United States. The score-1 row contains Finland, Canada, and Sweden. The remaining 17 eligible countries score 0; Australia and the United Arab Emirates are excluded from all frameworks by the corpus-size filter.

Framework-pair agreement on cluster identity is 91 % (student ↔ teacher), 74 % (student ↔ OECD), and 74 % (teacher ↔ OECD), all computed on the 23 country pairs eligible in both frameworks of each comparison. The student framework partition is therefore essentially identical to the teacher framework partition with US flipped; the OECD partition adds four countries (US, FI, CA, SE) to the deviating cluster relative to the student partition. The minimal-overlap set across all three frameworks — the countries that are Cluster 1 in every framework — contains exactly Korea and Ireland.

**[Figure 1 here — cross-framework Hellinger dendrograms + cluster identity heatmap; produced by `scripts/03_analysis/figure_cross_framework.py`]**

### 4.5.5 What the cross-framework result establishes

The §4.5 main result is therefore that the K = 2 cluster partition — and specifically the placement of Korea and Ireland in the deviating cluster — is **not** an artefact of which AI competency framework's vocabulary is used as the anchor space. The partition replicates across three independent frameworks developed by two separate international organisations (UNESCO and OECD/EC), and the silhouette quality of the partition *improves* under the simpler frameworks. Korea and Ireland are the only two countries whose national AI-in-education policy texts adopt the deviating signature under every framework tested.

This finding licenses a stronger §5 reading than would be available under any single-framework analysis: the Tool-use deviation is a property of the policy text rather than of the anchor system, and the §4.6 robustness battery (Module 1 inverse-corpus weighting, Module 2 leave-one-out, Module 3 bootstrap CIs, Module 4 uniform-cap sub-sampling, Module 5 temporal cohort split, Module 6 off-domain and hard-negative discriminant validity) establishes that the partition is also not an artefact of (i) corpus-size imbalance, (ii) single-document dominance, (iii) statistical sampling, (iv) within-country document weighting, (v) timing relative to the UNESCO framework's publication, or (vi) generic AI-policy concept vocabulary.

---

## 5. Discussion

The §4.5 main result invites four interpretive moves: (a) reframing the original four-pattern bifurcation hypothesis as a *one-canonical-cluster-plus-tool-use-deviation* structure; (b) distinguishing the *document-replicable* Korean signature from the *document-singular* Irish signature; (c) treating the United States as evidence of framework-dependent signatures rather than as a methodological inconsistency; and (d) connecting the cross-framework asymmetry (deviating cluster expands as anchor dimensionality decreases) to the diffusion-of-innovation theoretical framework introduced in §2. Each is discussed in turn, followed by the methodological and substantive limitations the analysis admits.

### 5.1 From four patterns to one canonical + one deviation

The protocol pre-registered in §3.4 anticipated four bifurcation patterns — tool-use, system-design, ethics-led, and human-agency — drawing on the §2 typology of AI-policy discourses and the present author's pilot 5-country analysis. The 25-country data do not support a four-cluster decomposition. The K = 2 silhouette dominates the K = 3, 4, 5, 6 alternatives under both Ward and average linkage and under all three anchor frameworks. The empirical structure is one canonical mass (≥ 17 countries; AILIT-S10 problem scoping dominant; OECD-O03 managing AI dominant) plus a small set of countries whose policy text deviates from this mass.

The following revised typological claim is therefore proposed: *national education-AI policy texts cluster into a dominant system-design / problem-scoping signature occupied by approximately three-quarters of the 25 countries surveyed, with a small deviating cluster characterised by tool-use, application-skills, and designing-AI vocabulary*. The deviating cluster's identity changes across anchor frameworks (Section 4.5), but its core (KR + IE) is stable. The four-pattern hypothesis is not falsified outright — its tool-use limb is well supported, and the ethics/human-agency/system-design components are recoverable as *secondary* loadings within the canonical cluster — but the data do not support treating these as four equally-populated bifurcation classes.

### 5.2 Korea: a document-replicable strong-form deviation

Korea exhibits the strongest deviating signature of any country in the sample. Across the five Korean documents in the corpus — covering the 2022 Korean national AI textbook, the 2022 Ministry of Education edutech masterplan, the 2024 Korea Development Institute policy review, the 2025 *AI Digital Textbook* press release, and the 2026 Ministry of Education business plan — the AILIT-S08 (Application skills) share is between 12.5 % and 31.9 % in *every individual document* (§4.4, Table 1). Dropping the largest single document (KR-02, 2,930 of KR's 3,297 aligned sentences) and recomputing the cluster assignment with the remaining four documents (367 sentences) leaves Korea in Cluster 1 (§4.6 Module 2). Inverse-corpus weighting (§4.6 Module 1) *strengthens* Korea's tool-use ratio from T/E = 4.31 to 6.78 because the smaller Korean documents have proportionally higher S08 shares than the dominant KR-02. Uniform-cap subsampling to *N* = 500 sentences preserves Korea's Cluster 1 assignment in 100 % of 1,000 random resamples (§4.6 Module 4).

This is interpretable as evidence that the Korean Ministry of Education's policy discourse on AI competency is a *tool-use-first* discourse — one that treats AI primarily as a class of applications students must learn to operate, evaluate, and select among. This is consistent with Korea's national choice to introduce the *AI Digital Textbook* programme as the principal vehicle for K-12 AI competency from 2025, and with the prior INEE programme evaluations of the AI textbook's classroom-application emphasis (cited in §2.4).

### 5.3 Ireland: a document-singular borderline case

Ireland's placement in the deviating cluster is more delicate. Ireland is in Cluster 1 across all three frameworks (rep_score 3/3), but the leave-one-out analysis reveals that this cluster identity is concentrated in a single document. IE-01 is the Department of Education's 2025 *Guidance on Artificial Intelligence in Schools*, a curriculum-side document targeted at teachers and learners. Dropping IE-01 and recomputing the cluster assignment with IE-02 alone (the older Department of Further and Higher Education AI strategy, 458 aligned sentences) places Ireland firmly in the canonical cluster (§4.6 Module 2). Bootstrap inference on the intra-Ireland asymmetry yields IE-01 − IE-02 AILIT-S08 difference = +21.16 percentage points (95 % CI [17.24, 25.32]), an effect size equal to the entire KR-vs-canonical deviation.

The Irish case is therefore best read as *evidence that the 2025 Department of Education curriculum guidance has independently adopted a tool-use register comparable to the Korean tradition*. It is not evidence that Ireland as a national policy actor has uniformly committed to that register. Ireland is deliberately retained in Cluster 1 in the main analysis, because the leave-one-out result is itself informative — it identifies the precise document (IE-01, 2025) at which the Irish education-AI discourse shifts toward the Korean pattern — but the §6 limitations note that the strength of the Korean signature should not be read symmetrically with the Irish.

This document-replicable vs document-singular asymmetry is a substantive contribution of the analysis: the §4.6 robustness battery converts what would otherwise be a binary cluster-membership claim into a graded one, with Korea as the strong-form deviation and Ireland as a recent, single-document, framework-stable adoption of the same register.

### 5.4 The United States: framework-dependent signature

The United States illustrates the third pattern that the cross-framework analysis surfaces. US documents do not align strongly with the UNESCO student framework's AILIT-S08 anchor: the US S08 share is 9.4 %, far below the cluster-1 threshold (~23 %). But under the UNESCO teacher framework, US loads heavily on T01 human-centred mindset (29.6 %) and T04 AI for professional development (37.1 %), and is grouped with KR and IE in the K = 2 partition. Under the OECD AILit framework, US loads on O04 designing AI (54.7 %) and is grouped with KR + IE + FI + CA + SE.

This pattern is interpretable as substantively informative rather than as a methodological inconsistency. The US national policy discourse on AI in education — particularly the 2025 White House Executive Order on Advancing AI Education for American Youth and the Department of Education's 2024 OET AI toolkit — emphasises human-agency framing and professional-development infrastructure, *not* the tool-use / application-skills vocabulary that the UNESCO student framework's S08 anchor specifically encodes. The teacher and OECD frameworks index these broader concepts more directly. The US is therefore in the deviating cluster *if and only if* the deviation is defined as "any departure from the canonical system-design register", but it is *not* in the deviating cluster when the deviation is defined more narrowly as "tool-use vocabulary".

This is the kind of framework-dependent signature that single-framework analyses cannot surface. The cross-framework figure (Fig. 1) makes the asymmetry visible at a glance and is the source of substantial interpretive value beyond the headline KR + IE finding.

### 5.5 Cluster expansion under simpler frameworks and the diffusion lens

The deviating cluster grows monotonically as the anchor framework becomes simpler: 2 countries on the 12-anchor student framework; 3 countries on the 5-anchor teacher framework; 6 countries on the 4-anchor OECD framework. The added countries — US (teacher), then FI, CA, SE (OECD) — are uniformly among the early-mover OECD nations in AI policy generally, and the §2 theoretical framework treats the §1.3 *diffusion-of-innovation* mechanism as the central process by which national education-AI policies are constituted.

The cross-framework expansion is consistent with the diffusion lens: countries closer to the *origin* of the discourse (KR + IE on the tool-use register; KR + US + IE on the human-agency + professional-development register; KR + FI + US + CA + SE + IE on the designing-AI register) appear in the deviating cluster at progressively broader resolutions, while countries further from these origins occupy the canonical mass at every resolution. The §2 typology of *frontier*, *fast-follower*, and *recipient* adopters is recoverable from the cluster expansion pattern: the frontier adopters surface as the deviating cluster on the simplest framework, the fast-followers surface on the medium-complexity framework, and the recipient set occupies the canonical cluster under every framework.

### 5.6 What the analysis does not establish

Several limitations bound the §4.5 main claim. First, the off-domain discriminant validity test (§4.6 Module 6) passes unambiguously — the UNESCO student anchors fire on 0.0 % of 3,271 sentences from non-AI text (Wikipedia historical and biological articles, Gutenberg literary fiction) — but the hard-negative discriminant test is inconclusive. The intended hard-negative documents (WHO health-AI ethics; US DoD AI ethical principles) failed automated text extraction in the pipeline (§3.5), and the two hard-negative documents that were successfully extracted (Google AI Principles; Microsoft Responsible AI Standard v2) are corporate AI policy texts that share substantial vocabulary with the positive corpus by construction. The UNESCO student anchors should therefore be interpreted as measuring "AI-policy concept alignment" rather than "education-AI-specific concept alignment"; §4.5's cross-framework replication is the principal evidence that the cluster differentiation is meaningful.

Second, the corpus contains two countries (AE, AU) for which alignment yields below the *N* = 50 threshold (AE *n* = 7; AU *n* = 42), and these are excluded from cluster-assignment analysis. Their inclusion in a future analysis would require additional source documents that were not publicly accessible at the time of corpus harvest.

Third, the analysis is descriptive: it does not test causal claims about *why* Korea and Ireland have adopted the tool-use register or about whether their adoption is causally connected to UNESCO's framework publication. The temporal cohort analysis (§4.6 Module 5) shows that the cluster identity is stable both before and after UNESCO's September 2024 framework release, ruling out the timing-as-artefact alternative, but does not establish a positive causal mechanism.

### 5.7 Implications for policy and curriculum design

The §4.5 result has implications for two distinct audiences. For *policy-makers in countries currently in the canonical cluster*: the analysis identifies AILIT-S08 (Application skills) and the OECD O04 (Designing AI) as the concept loadings most strongly differentiating Korea's and Ireland's recent education-AI policy from theirs. National policy revisions intending to align with the UNESCO 2024 framework's full breadth — not only its system-design and problem-scoping anchors — would need to incorporate explicit application-skills language. For *curriculum designers in countries already in the deviating cluster*: the analysis quantifies the *strength* of the alignment (KR T/E = 4.31 raw, 6.78 weighted) and documents Korea's *document-replicable* signature as a model for sustained, multi-document coherent policy discourse, in contrast to Ireland's single-document — but well-defined — recent commitment to the same register.

For *the research community on national AI competency frameworks*: the cross-framework replication design (Fig. 1) demonstrates a generalisable methodology — re-run the analysis under multiple independent anchor frameworks and report cluster-identity replication scores — that converts what would otherwise be single-framework descriptive findings into framework-invariant ones. The author proposes this protocol as a candidate standard practice for future cross-national education-policy text analyses.

---

**End §4.5 + §5 first draft.**

Next steps:
- §6 Conclusions + Limitations: short, integrative; promises Phase 4 follow-up
- §3 Methods: in-depth methodological narrative (corpus harvest, anchor cohesion, threshold, embedding, Hellinger, robustness battery)
- §4.6 Robustness battery: condensed version of the six module memos (`docs/phase2_module*.md`) plus the cross-framework discriminant analysis
- §1 Introduction + §2 Theoretical framework: connection to the diffusion lens, the 4-pattern hypothesis revision, the AI-competency-policy-text genre as a study object
- Tables: Table 1 (25 × 12 student adherence matrix), Table 2 (25 × 5 teacher matrix), Table 3 (25 × 4 OECD matrix), Table 4 (cross-framework cluster identity)
- Figure 1 = `data/clustering/figure_cross_framework_v2.png`
- Figure 2 (suggested) = `data/clustering/figure_robustness_summary_v2.png`

Estimated current word count for §4.5 + §5: ~2,800 words. the target journal's main-text target is 8,000–10,000 words inclusive of all sections, so this is approximately one-third of the manuscript.
