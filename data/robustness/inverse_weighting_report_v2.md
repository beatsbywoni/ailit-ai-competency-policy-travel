# Inverse-corpus weighting — robustness check IV.2

Source: `sprint1_alignment_full_v2.jsonl`. Per-(country, anchor) weighted share = mean across documents of within-doc share. Each document counts equally regardless of size.

## Per-country comparison

| Country | Docs | Raw T÷E | Weighted T÷E | Raw dominant | Weighted dominant | Flipped? |
|---|---:|---:|---:|---|---|---|
| AE | 2 | 0.0 | 0.000 | A1 HCM | A1 HCM | no |
| AU | 3 | 1.251 | 3.625 | A1 HCM | A4 SysDes | Y |
| BR | 2 | 0.172 | 0.198 | A4 SysDes | A4 SysDes | no |
| CA | 3 | 0.563 | 0.912 | A4 SysDes | A4 SysDes | no |
| CN | 2 | 3.48 | 3.476 | A4 SysDes | A4 SysDes | no |
| DE | 3 | 0.985 | 1.519 | A4 SysDes | A4 SysDes | no |
| EE | 2 | 0.111 | 0.111 | A4 SysDes | A4 SysDes | no |
| ES | 2 | 1.382 | 1.014 | A4 SysDes | A4 SysDes | no |
| FI | 4 | 0.846 | 0.843 | A2 Ethics | A1 HCM | Y |
| FR | 3 | 0.603 | 0.697 | A4 SysDes | A4 SysDes | no |
| GB | 4 | 0.829 | 1.189 | A4 SysDes | A4 SysDes | no |
| IE | 2 | 3.213 | 2.504 | A1 HCM | A1 HCM | no |
| IL | 2 | 0.685 | 0.349 | A4 SysDes | A4 SysDes | no |
| IN | 3 | 0.558 | 0.637 | A4 SysDes | A4 SysDes | no |
| IT | 2 | 0.842 | 0.850 | A4 SysDes | A4 SysDes | no |
| JP | 3 | 1.098 | 1.730 | A4 SysDes | A4 SysDes | no |
| KR | 5 | 4.305 | 6.781 | A3 Tech | A3 Tech | no |
| MX | 2 | 0.374 | 0.160 | A1 HCM | A1 HCM | no |
| NL | 2 | 0.842 | 0.842 | A4 SysDes | A1 HCM | Y |
| NO | 2 | 0.701 | 1.825 | A4 SysDes | A4 SysDes | no |
| SA | 2 | 2.753 | 5.672 | A4 SysDes | A4 SysDes | no |
| SE | 2 | 2.817 | 1.701 | A4 SysDes | A4 SysDes | no |
| SG | 3 | 0.852 | 1.080 | A4 SysDes | A1 HCM | Y |
| US | 4 | 1.224 | 1.540 | A1 HCM | A4 SysDes | Y |
| ZA | 2 | 0.352 | 0.578 | A1 HCM | A4 SysDes | Y |

## Interpretation

If the per-country dominant aspect is stable when each document is given equal weight, the 4-pattern bifurcation is not an artefact of single-document dominance.

Flips marked 'Y' deserve special discussion in §4.6 robustness.