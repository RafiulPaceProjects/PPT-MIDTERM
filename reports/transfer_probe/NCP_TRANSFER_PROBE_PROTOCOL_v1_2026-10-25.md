# NewsCLIPpings transfer probe v1: protocol (frozen before the pilot)

**Declared:** 2026-10-25, before any feature extraction or training.
**Authorized by the user (2026-10-25):** a training experiment limited to frozen-feature probes; pilot first; LAYA probe only; NewsCLIPpings images streamed and not stored. This is a scoped exception to the workspace's baseline-only policy and applies to this experiment only.

## Question

The published protocol for these benchmarks trains on one dataset and tests on the target: NewsCLIPpings train → NewsCLIPpings test, and NewsCLIPpings train → VERITE "True vs out-of-context" (LAMAR Table 3). If LAYA-Vision's frozen representation is given that supervision through a linear probe, how much image–caption pairing signal does it carry, compared with its own zero-shot answers on the same rows?

This measures the representation of one frozen 201M checkpoint. It is not a fine-tuned LAYA and not a reproduction of any published system.

## Model and features (fixed)

- Checkpoint: LAYA-Vision `f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc`, CPU, fp32, `max_len=1024`, `head_max_len=256`, `n_permutations=1`, `batch_size=1`. No weight is updated.
- Input per row: `{"image": <pixels>, "context": <caption>}` and the `native` question from `ncp_stream_infer_20261025.py` (unchanged wording). No ids, paths, source fields or labels enter the model.
- Feature: the vector `z` that LAYA's own decision head reads (`act_head` input, `laya/vlm.py:711`), captured by a forward pre-hook that records and does not modify. `z` = 576-d pooled hidden state + 4 decision scalars. **The probe uses the 576-d pooled state only.** The 4 scalars are saved for audit, not used.
- The `native` zero-shot answer from the same call is saved, so probe and zero-shot are compared on identical rows.

## Data

| Role | Population | Read in pilot? |
|---|---|---|
| Train (pilot) | 5,000 NewsCLIPpings `merged_balanced` train rows: seeded (20261025) stratified sample, 1,250 per `source_dataset` strategy, half pristine / half falsified | yes |
| Train (full run) | all 71,072 train rows | no |
| Selection / development | all 7,024 validation rows | yes |
| Target 1 (full run only, once) | NewsCLIPpings test, 7,264 rows; never read in this workspace before | **no** |
| Target 2 (full run only, once) | VERITE current CSV, `true` (338) vs `out-of-context` (325) = 663 rows; `miscaptioned` excluded because NewsCLIPpings has no miscaptioned training signal | **no** |

Label mapping for VERITE: `true` → pristine, `out-of-context` → falsified.

Images: streamed from the VisualNews archive with HTTP range reads (method of `ncp_stream_infer_20261025.py`), decoded in memory, featurized, discarded. Stored: features, zero-shot probabilities, image SHA-256, row metadata. VisualNews reuse terms remain unresolved and are disclosed; features are local and not redistributed.

## Probe (fixed)

- L2-regularized logistic regression on standardized features (mean/std from the training rows only), full-batch L-BFGS in torch, float64, deterministic.
- Regularization grid λ ∈ {1e-4, 1e-3, 1e-2, 1e-1, 1}. λ is chosen on validation accuracy (ties → larger λ).
- Primary metric: accuracy (balanced classes). Secondary: balanced accuracy, macro-F1, AUC, ECE (15 bins).
- Uncertainty: 95% bootstrap ranges, 2,000 resamples, seed 20261018, clusters = exact image bytes (SHA-256). Descriptive, not confirmatory.

## Pilot (this step)

1. One archive pass collects validation + pilot-train rows; only those rows are featurized.
2. **Integrity gate:** validation `native` probabilities must reproduce the saved zero-shot run `data/processed/ncp_stream_v1/predictions.jsonl` (max absolute difference ≤ 1e-3 on the saved 4-decimal values). Failure stops the experiment.
3. Probe trained on the 5,000 pilot rows; validation accuracy reported for every λ, labeled **development, selection-biased**, beside zero-shot on the same validation rows.
4. Throughput (rows/s) and coverage (rows featurized / wanted) recorded.

**Go/no-go for the full run is technical and returns to the user:** gate passes; coverage ≥ 99% of wanted rows; projected full-run time stated. The pilot validation score is reported but is not a reason to change this protocol.

## Full run (requires a separate go from the user)

Featurize all train rows, test rows and the 663 VERITE rows; fit the probe on all train rows; select λ on validation; then score NewsCLIPpings test and VERITE True-vs-OOC **once**, beside LAYA zero-shot on the same rows and the published references (non-comparable). No protocol change after test features exist.

## Artifacts

- Code: `data/workflows/transfer_probe/`
- Outputs: `data/processed/protocol/ncp_transfer_probe_v1/`
- Reports: `data/reports/transfer_probe/`

## Clarifications recorded before the pilot (2026-10-25)

Made after a 41-row validation smoke test (`data/processed/protocol/ncp_transfer_probe_v1_smoke`, not a result) and before any train row was read. Neither changes the design.

1. **Row key.** NewsCLIPpings caption `id`s are not unique: each appears once pristine and once falsified. Rows are keyed by (`id`, `image_id`). The integrity gate uses that key. On the smoke rows it reproduced the saved zero-shot probabilities exactly (41/41, max difference 0.0).
2. **Pilot sampling unit.** The 5,000 pilot rows are 2,500 caption ids (625 per strategy, seed 20261025) with both rows of each id. This yields exactly the declared 1,250 rows per strategy, half pristine and half falsified, and keeps the dataset's design in which the caption alone cannot predict the label.
3. **Code paths checked.** LAYA `predict` with the three-question set or `native` alone, prefix cache on or off, gave identical `native` probabilities on three local MMFakeBench validation images. Asking only `native` is therefore equivalent to the baseline call.

## Amendment 1: device (2026-10-25, user-approved, before any train row was featurized)

**Change:** feature extraction runs on the Apple GPU (`--device mps`) instead of CPU. Everything else is unchanged: checkpoint, fp32, question, feature, probe, data, gates.

**Why:**
- Pilot attempt 1 (CPU, `pilot_attempt1_aborted/`, not a result) ran at 0.42 rows/s and would have exceeded its budget.
- Moving the archive readers to separate processes did not help.
- The model itself now runs at about 2.3 s/row on this machine's CPU, against a 0.31 s/row median in the 03:48–04:34 baseline run. That puts the pilot at about 7.5 h and the full run at about 49 h.

**Evidence of equivalence** (20 local MMFakeBench validation images, `native` question):

| Measure | Result |
|---|---|
| MPS speed | 0.27 s/row |
| CPU speed | 2.27 s/row |
| `native` probabilities | identical to 4 decimals |
| Pooled 576-d features | max absolute difference 2.4e-4; max relative difference 6.7e-6 |

**Safeguard (unchanged and now decisive):** all 7,024 validation zero-shot probabilities from the MPS feature run must reproduce the saved CPU baseline (`ncp_stream_v1`) within 1e-3. Otherwise nothing is trained.

## Amendment 2: full-run specification (2026-10-25, user-approved, before any full-run feature, test row or VERITE row was read)

1. **Regularization grid widened.** The grid is now λ ∈ {1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 100}. Reason: the pilot selected λ = 1, the edge of the declared grid. The decision was made on pilot validation only; test and VERITE remain unread. Selection rule unchanged: highest validation accuracy, ties go to the larger λ.
2. **Populations:**
   - Train: all 71,072 `merged_balanced` train rows, re-featurized in one streaming pass together with the 7,264 test rows (`data/processed/protocol/ncp_transfer_probe_v1/full/`).
   - Validation: the 7,024 pilot validation rows, reused unchanged. They passed the integrity gate, and the model, device and code are the same.
   - VERITE: the 663 `true` / `out-of-context` rows of `data/raw/VERITE/VERITE.csv` with local images from `data/raw/VERITE/images` (the verified archive). Featurized with the same model, question and hook (`.../verite/`).
3. **Scoring:**
   - The probe is fit once on all train rows for each λ, and λ is selected on validation.
   - The selected probe is applied once to NewsCLIPpings test and once to VERITE.
   - Reported beside LAYA zero-shot (its own `native` choice) on the same rows.
   - Same metrics and the same cluster bootstrap (exact image bytes).
   - The NewsCLIPpings test result is a held-out result: the split was never read before this step.
4. **Streaming robustness:** if a reader's download drops before the end of its archive range, it reconnects from the last complete member (up to 5 retries). Members that straddle a range boundary can still be lost; any missing images are counted and reported.
