# Inverse-corpus weighting — robustness check IV.2

Source: `sprint1_alignment_full_v1.jsonl`. Per-(country, anchor) weighted share = mean across documents of within-doc share. Each document counts equally regardless of size.

## Per-country comparison

| Country | Docs | Raw T÷E | Weighted T÷E | Raw dominant | Weighted dominant | Flipped? |
|---|---:|---:|---:|---|---|---|
| AE | 2 | 0.0 | 0.000 | A2 Ethics | A2 Ethics | no |
| AU | 3 | 1.0 | 2.848 | A1 HCM | A4 SysDes | Y |
| BR | 2 | 0.122 | 0.131 | A4 SysDes | A4 SysDes | no |
| CA | 3 | 0.5 | 0.746 | A4 SysDes | A4 SysDes | no |
| CN | 2 | 2.353 | 0.174 | A4 SysDes | A2 Ethics | Y |
| DE | 3 | 0.572 | 0.667 | A4 SysDes | A4 SysDes | no |
| EE | 2 | 0.1 | 0.100 | A4 SysDes | A4 SysDes | no |
| ES | 2 | 1.237 | 1.003 | A4 SysDes | A4 SysDes | no |
| FI | 4 | 0.732 | 0.593 | A2 Ethics | A2 Ethics | no |
| FR | 3 | 0.338 | 0.456 | A4 SysDes | A4 SysDes | no |
| GB | 4 | 0.459 | 0.733 | A4 SysDes | A4 SysDes | no |
| IE | 2 | 1.416 | 1.226 | A1 HCM | A1 HCM | no |
| IL | 2 | 0.332 | 0.172 | A4 SysDes | A4 SysDes | no |
| IN | 3 | 0.383 | 0.421 | A4 SysDes | A4 SysDes | no |
| IT | 2 | 0.403 | 0.407 | A4 SysDes | A4 SysDes | no |
| JP | 3 | 0.634 | 0.798 | A4 SysDes | A4 SysDes | no |
| KR | 5 | 1.141 | 2.391 | A3 Tech | A3 Tech | no |
| MX | 2 | 0.212 | 0.098 | A2 Ethics | A2 Ethics | no |
| NL | 2 | 0.485 | 0.485 | A4 SysDes | A1 HCM | Y |
| NO | 2 | 0.449 | 0.893 | A2 Ethics | A4 SysDes | Y |
| SA | 2 | 0.836 | 1.576 | A4 SysDes | A4 SysDes | no |
| SE | 2 | 2.414 | 1.880 | A4 SysDes | A4 SysDes | no |
| SG | 3 | 0.545 | 0.767 | A4 SysDes | A1 HCM | Y |
| US | 4 | 0.737 | 0.972 | A2 Ethics | A4 SysDes | Y |
| ZA | 2 | 0.267 | 0.372 | A2 Ethics | A4 SysDes | Y |

## Interpretation

If the per-country dominant aspect is stable when each document is given equal weight, the 4-pattern bifurcation is not an artefact of single-document dominance.

Flips marked 'Y' deserve special discussion in §4.6 robustness.