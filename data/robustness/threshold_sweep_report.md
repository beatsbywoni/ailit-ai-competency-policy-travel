# Threshold sensitivity report

Planning §7.9 robustness step. Thresholds swept: [0.3, 0.35, 0.4, 0.45, 0.5].

## Tool ÷ Ethics ratio across thresholds

| Threshold | Aligned (%) | KR | GB | SG | FI | US | Countries with T÷E ≥ 3× |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.30 | 39.3 | 1.04 | 1.00 | 0.59 | 0.60 | 0.24 | 0 |
| 0.35 | 27.8 | 1.14 | 1.00 | 0.63 | 0.73 | 0.35 | 0 |
| 0.40 | 19.6 | 1.44 | 1.00 | 0.73 | 0.82 | 0.52 | 0 |
| 0.45 | 13.6 | 1.82 | 1.25 | 0.75 | 0.90 | 0.79 | 0 |
| 0.50 | 9.3 | 2.02 | 1.00 | 0.91 | 1.02 | 0.90 | 0 |

## Interpretation

If the bifurcation pattern (Korea tool-leaning vs US/FI/SG ethics-leaning) survives the threshold sweep — i.e., per-country T÷E rank order is stable — the finding is robust to the §7.3 threshold choice.

If the pattern collapses (e.g., US T÷E rises above 1 at threshold 0.45), the Sprint 0 verdict was a threshold artefact and the §10.1 RED → AMBER reframing must be reconsidered.

Outputs: `threshold_sweep_5x12_t{NN}.csv` per threshold, `threshold_sweep_summary.csv` aggregated.