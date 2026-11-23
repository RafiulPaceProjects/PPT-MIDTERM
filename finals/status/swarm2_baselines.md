# Swarm-2 Baseline Audit — recomputed from raw prediction rows
Date: 2026-11-22 (pod-side read-only audit; no files modified on the pod)
Method: every metric below was recomputed by the auditor from the raw
`paired.predictions.jsonl` rows (gold vs predicted_label), never copied
from a metrics summary. Claimed values are the run's own
`paired.metrics.json` / `summary.json`, shown beside the recomputation.

## VERDICT: CLEAN
All three baseline folders' claimed metrics reproduce from raw rows to
full printed precision. The October ablation file is bootstrap-ready
with one documented caveat (a single error row — see §4).

## 1 · PASS 1 — NewsCLIPpings val baseline (streamed)
File: `data/processed/midterm/baseline_newsclippings_val_v1/paired.predictions.jsonl`
- Rows: **7,024** · status: **ok 7,024 / blocked 0 / error 0**
- Gold: pristine 3,512 · falsified 3,512 (exact Merged-Balanced split)
- Predicted: falsified 6,535 · pristine 489 (heavy Fake bias, as reported)
- **Accuracy (recomputed): 0.514095** — claimed 0.5140945330296127 ✓ MATCH
- Confusion cross-check vs claimed matrix [[294, 3218], [195, 3317]]:
  consistent with the recomputed counts (pristine recall 294/3512 = 0.0837,
  falsified recall 3317/3512 = 0.9445 — both match claimed per-class values)
- Mean per-row seconds: **0.1798** (median 0.1149, n = 7,024)
- Spot checks (first / middle / last ok rows): choice probabilities sum to
  exactly 1.0 in both `probabilities` and `raw_answers.native.probabilities`;
  `fake_probability` equals `raw_answers.fake.noul` exactly on all 3 rows
  (0.6319 / 0.7114 / 0.7796) ✓
- Stream accounting: referenced images 5,943 → seen 5,943 → verified 5,943,
  skipped 0, missing 0; per-source rows scored 954 + 3,236 + 1,652 + 1,182
  = 7,024 ✓; `stream_skip_ledger.jsonl` is 0 bytes (no skips to ledger) ✓
  (5,943 unique images < 7,024 rows because rows share images — expected.)

## 2 · MMFakeBench val baseline
File: `data/processed/midterm/baseline_mmfakebench_val_v1/paired.predictions.jsonl`
- Rows: **1,000** · status: **ok 1,000**
- Gold: original 300 · textual 300 · visual 100 · mismatch 300
- Predicted: mismatch 776 · visual 119 · original 89 · textual 16
- **Accuracy (recomputed): 0.293** — claimed 0.293 ✓ MATCH
- **Macro-F1 (recomputed): 0.207915** — claimed 0.20791501063690315 ✓ MATCH
- Per-class recall (recomputed = claimed, all four):
  original 0.046667 · textual 0.033333 · visual 0.270000 · mismatch 0.806667
- Note (already in the run record): these are the run's own pack-wording
  baselines; October's audit measured acc 0.320 / F1 0.1985 on the same
  1,000 rows under the earlier question wording.

## 3 · VERITE baseline
File: `data/processed/midterm/baseline_verite_val_v1/paired.predictions.jsonl`
- Rows: **1,001** · status: **ok 1,001**
- Gold: true 338 · miscaptioned 338 · out-of-context 325
- Predicted: out-of-context 614 · true 379 · miscaptioned 8
- **Accuracy (recomputed): 0.346653** — claimed 0.34665334665334663 ✓ MATCH
- **Macro-F1 (recomputed): 0.281886** — claimed 0.2818864153259848 ✓ MATCH
- Per-class recall (recomputed = claimed): true 0.428994 ·
  miscaptioned 0.008876 · out-of-context 0.612308

## 4 · Bootstrap readiness — October ablation baseline (test)
File: `data/reports/ablation_test_paired.predictions.jsonl`
- Rows: **10,000** · status: **ok 9,999 · error 1** (the 1 error row has
  predicted_label = null; its gold is textual, so ok-row textual support
  is 2,999 of 3,000)
- IDs: `test:0` … `test:9999`, all 10,000 unique, no gaps ✓
- Gold (all rows): original 3,000 · textual 3,000 · visual 1,000 ·
  mismatch 3,000 ✓ (matches the benchmark's test design)
- All rows: branch = paired, dataset = mmfakebench, split = test ✓
- **Macro-F1 over the 9,999 ok rows (recomputed): 0.203742** — the
  documented October baseline 0.20374 ✓ MATCH
- Accuracy over ok rows (recomputed): 0.264226
- Per-class recall over ok rows: original 0.2133 · textual 0.5238 ·
  visual 0.0260 · mismatch 0.1350
- READINESS: suitable as the paired-bootstrap reference. The pairing code
  must handle the single error row symmetrically (exclude that test id
  from both sides, or score it as an error on both sides) — with 9,999
  paired rows the effect is negligible either way, but it must be a
  stated choice, not an accident.

## Auditor notes
- No discrepancies found anywhere: every claimed accuracy, macro-F1 and
  per-class recall in all three baseline folders reproduces exactly.
- The baselines confirm the study's diagnosis quantitatively: the base
  model collapses toward one class on every dataset (NCP: 93% falsified;
  MMF val: 78% mismatch with original recall 0.047; VERITE: miscaptioned
  recall 0.009).
