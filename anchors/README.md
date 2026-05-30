# anchors/

21 anchor texts grouping the three normative frameworks under study.

| File | Source | Anchors | Status (2026-05-29) |
|---|---|---|---|
| `unesco_ai_student_2024.csv` | UNESCO (2024) *AI Competency Framework for Students* §3.3 | 12 (4 aspects × 3 levels) | **verbatim** |
| `unesco_ai_teacher_2024.csv` | UNESCO (2024) *AI Competency Framework for Teachers* §3.2 | 5 (macro-aspects) ⚠ | **verbatim** |
| `oecd_ai_literacy_2025.csv` | OECD/EC (2025) *Empowering Learners for the Age of AI*, May 2025 Review Draft | 4 (domains) | **verbatim** |

> ⚠ **Teacher framework deviation from planning §5.2.** Planning v1 assumed parallel 4-aspect structure with the student framework. The actual UNESCO teacher framework has **5 aspects** (Human-centred mindset, Ethics of AI, AI foundations and applications, AI pedagogy, **AI for professional development**). We use all 5 because the cost is low and dropping Aspect 5 would silently misrepresent the source. The total anchor count becomes 12 + 5 + 4 = 21 instead of planning's 20. Update planning §5.2 / §5.4 in `planning_v2.md`.

## Status field semantics

- `provisional` — label and aspect/level confirmed from official summary; full anchor sentence is a placeholder pending verbatim extraction from the source PDF.
- `verbatim` — anchor sentence extracted directly from the official PDF, section numbering and cross-references stripped per planning §5.5.
- `locked` — verbatim text reviewed, cross-checked in Korean translation, and frozen for the alignment run.

## Verbatim extraction record (2026-05-29)

| File | Extracted from | Section | Method |
|---|---|---|---|
| `unesco_ai_student_2024.csv` | `data/source_pdfs/unesco_ai_student_2024.pdf` (UNESDOC 391105eng) | §3.3 Aspects | manual sentence selection; lead "Students are expected to…" sentence per competency block |
| `unesco_ai_teacher_2024.csv` | `data/source_pdfs/unesco_ai_teacher_2024.pdf` (UNESDOC 391104eng) | §3.2 Aspects of the AI CFT | manual sentence selection; aspect-level summary paragraphs |
| `oecd_ai_literacy_2025.csv` | `data/source_pdfs/oecd_ailit_review_draft_2025_05.pdf` | "Domains" section, p.15 | manual sentence selection; full domain description paragraph |

Next status transition (`verbatim` → `locked`): after Korean cross-check in `docs/anchor_sanity_check_ko.md` v1.

## Source PDFs (saved in `data/source_pdfs/` — not in repo, see `.gitignore`)

- `unesco_ai_student_2024.pdf` ← https://unesdoc.unesco.org/ark:/48223/pf0000391105_eng (80 pp)
- `unesco_ai_teacher_2024.pdf` ← https://unesdoc.unesco.org/ark:/48223/pf0000391104 (52 pp)
- `oecd_ailit_review_draft_2025_05.pdf` ← https://ailiteracyframework.org/wp-content/uploads/2025/05/AILitFramework_ReviewDraft.pdf (43 pp)

Extracted text in the same folder as `*.txt`. Re-run with `bash run_pdf_to_text.sh` from the repo root.
