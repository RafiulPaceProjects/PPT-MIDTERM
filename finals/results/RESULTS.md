# Results

## Status — 2026-11-22

**Main run IN PROGRESS.** The training grid (full + LoRA arms × 2 losses ×
3 step budgets = 12 configs), the winner's single test scoring, and the
H1–H5 verdicts will be added here on completion. Nothing below the BEFORE
table is a result yet.

## BEFORE — verified baseline numbers (zero-shot LAYA-Vision, paired route)

| Measure | Value | Source |
|---|---|---|
| MMFakeBench test ablation — paired macro-F1 | 0.2037 | Oct 25 test ablation (paired − text = −1.51 pp [−2.44, −0.54]) |
| MMFakeBench validation — paired macro-F1 | 0.1985 | Saved-predictions audit, recomputed (1,000 rows) |
| NewsCLIPpings validation accuracy | 0.5083 | Oct 25 full-split run (7,024 rows) |
| VERITE paired-arm accuracy | 0.3566 | Oct 25 full-split run (1,001 local rows) |
| VERITE text-only arm accuracy | 0.3586 | Oct 25 full-split run (1,001 local rows) |

Paired per-class recall, MMFakeBench validation (1,000 rows) — the baseline
model collapses onto "mismatch":

| Class | Recall |
|---|---|
| original | 1/300 |
| textual distortion | 8/300 |
| visual distortion | 22/100 |
| mismatch | 289/300 |

Transfer probe (frozen features + logistic probe, the one positive held-out
result): NewsCLIPpings test 57.4% vs zero-shot 51.1% (**+6.24 pp [4.76, 7.70]**).

## AFTER — trained results

*Pending the main run. Will contain: the 12-config grid table (tune
macro-F1), the winner, test-scored-once metrics with the paired bootstrap CI,
H1–H5 verdicts, calibration ECE before/after, and the published model +
Space links.*
