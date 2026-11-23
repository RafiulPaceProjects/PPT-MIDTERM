# Baseline Details — the paper's "n/a" cells, computed from the prediction files

Computed 2026-11-23 from the v1 main-run prediction files pulled from the pod.
Every value below was recomputed from the per-row predictions (gold vs predicted
label, and the noul `fake_probability` for the AUC) — not copied from prose.
The run's own stored `paired.metrics.json` agrees with the recomputation to full
float precision on every field checked.

## 1. NewsCLIPpings — baseline column

Source file:
`~/workspace/misinfo_run/mainrun_artifacts/data/processed/midterm/baseline_newsclippings_val_v1/paired.predictions.jsonl`
(PASS 1 baseline stream; checkpoint `/workspace/Misinformation/models/laya-vision-base`)
Rows: **7,024** (all status ok; gold split 3,512 pristine / 3,512 falsified)

### Proof check (must reproduce the paper's published baseline numbers)
| Published | Recomputed | Match |
|---|---|---|
| Accuracy 0.5141 | 0.5140945330296127 | ✓ exact |
| Pristine recall 0.084 | 0.0837129840546697 | ✓ exact |
| Predicts "falsified" for 93% of rows | 0.9303815489749431 (6,535 / 7,024) | ✓ |

### Confusion matrix (gold rows × predicted columns)
|  | pred pristine | pred falsified |
|---|---|---|
| gold pristine | 294 | 3,218 |
| gold falsified | 195 | 3,317 |

### The missing cells
| Cell | Value (full precision) | Paper rounding |
|---|---|---|
| **Falsified recall** | 0.9444760820045558 (3,317 / 3,512) | **0.944** |
| **Binary-screen AUC** (noul `fake_probability`, positive = falsified, tie-correct Mann–Whitney) | 0.5488011977158691 | **0.549** |

The baseline predictions DO carry a noul probability per row (`fake_probability`,
also at `raw_answers.fake.noul`), so the AUC is computed, not approximated.

## 2. VERITE — baseline column

Source file:
`~/workspace/misinfo_run/mainrun_artifacts/data/processed/midterm/baseline_verite_val_v1/paired.predictions.jsonl`
(baseline paired run; checkpoint `/workspace/Misinformation/models/laya-vision-base`)
Rows: **1,001** (all status ok; gold split 338 true / 338 miscaptioned / 325 out-of-context)

### Proof check (must reproduce the paper's published baseline numbers)
| Published | Recomputed | Match |
|---|---|---|
| Accuracy 0.3467 | 0.34665334665334663 | ✓ exact |
| Macro-F1 0.2819 (recorded 0.281886) | 0.2818864153259848 | ✓ exact |

### Confusion matrix (gold rows × predicted columns: true / miscaptioned / out-of-context)
|  | pred true | pred miscaptioned | pred out-of-context |
|---|---|---|---|
| gold true | 145 | 2 | 191 |
| gold miscaptioned | 111 | 3 | 224 |
| gold out-of-context | 123 | 3 | 199 |

### The missing cells
| Cell | Value (full precision) | Paper rounding |
|---|---|---|
| **Truthful recall** | 0.4289940828402367 (145 / 338) | **0.429** |
| **Miscaptioned recall** | 0.008875739644970414 (3 / 338) | **0.009** |
| **Out-of-context recall** | 0.6123076923076923 (199 / 325) | **0.612** |

## Unfillable cells

**None.** All five "n/a" cells are filled from the prediction files, and both
files pass the proof check against the paper's already-published headline
numbers exactly. The baseline's near-zero VERITE miscaptioned recall (0.009 —
3 of 338) and its high NewsCLIPpings falsified recall (0.944, against pristine
recall 0.084) are real properties of the frozen baseline, not missing data:
the baseline over-predicts "falsified" on NewsCLIPpings (93.0% of rows) and
almost never predicts "miscaptioned" on VERITE (8 of 1,001 rows).
