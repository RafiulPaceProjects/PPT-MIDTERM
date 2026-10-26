# Fine-tuning pre-registration (DRAFT, 2026-10-25)

**DRAFT pre-registration — not authorized to run; requires user and instructor sign-off before any optimizer step.**

Read-only review; no inference, training, download, or network use.

## 1. Question

Does task-specific adaptation of LAYA-Vision's head improve native macro-F1 beyond (a) zero-shot, (b) the frozen-feature linear probe, and (c) the 91.5% source-metadata rule? Does any gain survive within source pairs? NewsCLIPpings is binary; MMFakeBench is four-way native.

## 2. Recommended order

**Option A (recommended): NewsCLIPpings head adaptation.** Train on the 71,072 `merged_balanced` train rows, select on the 7,024 validation rows, and score NewsCLIPpings test (7,264 rows) and VERITE true vs out-of-context (663 rows) once each. Features and streaming come from transfer probe v1. It is the cleaner test: a proper train split and an unread held-out test. MMFakeBench's 490 training rows partition its validation split, and its source columns give a shortcut (13 of 14 source pairs are label-pure).

Before A runs:
- The 2026-10-25 authorization covers frozen-feature probes only; a trainable head beyond that needs new authorization.
- The probe protocol fits L2 logistic regression on the 576-d pooled state (577 parameters, derived). The handoff's head has 8,462,659 trainable parameters. Until the trainable module is named, Option A may be identical to control (b).

**Option B: existing MMFakeBench frozen-head protocol.** 490 train, 105 tune, 105 calibration, and 300 confirmation rows. Limits: small training set; confirmation rows already exposed (descriptive only); no test scoring authorized; single seed; CPU only.

## 3. Fixed design (declare before training)

| Item | Option A | Option B |
|---|---|---|
| Trainable scope | Head only, encoder frozen; module to be named (§2) | Head only; encoder and vision tower frozen; 8,462,659 trainable parameters in 35 tensors; zero `encoder.*` trainable (preflight) |
| Objective | Binary | Native four-way; vlm_loss sigma 0.3, group_size 4, w_sph 0.75, w_ce 1.0, train_act false |
| Optimizer and steps | Not declared. Probe uses full-batch L-BFGS, float64 | AdamW, lr_head 1e-4, weight decay 0.01, grad clip 1.0, cosine to 10%, warmup 0, batch 2; 735 steps; checkpoints 245, 490, 735; 60-minute cap |
| Seeds | Three, to be named. A deterministic full-batch convex probe gives the same result for any seed | Handoff declares one seed (20261019); two more must be added |

**Selection**
- A: λ chosen on validation. The probe protocol selects on accuracy (ties to larger λ). Proposed: macro-F1, to match the gate; needs amendment before the full run.
- B: tune only (105 rows). Exclude any candidate whose per-class recall drops more than 0.05 below the incumbent. Highest tune macro-F1 wins; ties go to the incumbent, then the earlier step. A winner must exceed the incumbent's 0.2591490601408522 by at least 0.03, or the incumbent is kept.

**Success gate** (copied from the handoff): Δmacro-F1 ≥ 0.03, AND paired bootstrap 95% lower bound > 0, AND each class recall drop ≤ 0.05, AND no added failures or abstentions.

**Evaluation unit:** cluster bootstrap by exact image bytes (SHA-256), as instructed. Two conflicts to resolve: the handoff bootstraps by `group_id` with 10,000 replicates (seed 20261019), while the transfer probe uses 2,000 resamples (seed 20261018). Choose one unit and one replicate count.

**Mandatory controls**
- Zero-shot. A: validation 50.8% [49.7, 51.8]; test and VERITE not computed. B: incumbent paired run on the 300 confirmation rows (value in `paired.metrics.json`).
- Linear probe. A: pilot probe 55.6% validation [54.4, 56.7] at λ = 1 (development, selection-biased). Full-run probe not run. B: not computed.
- Majority. Not computed for either option.
- Source-metadata rule (MMFakeBench). 91.5% fitted on disjoint validation rows; 95.0% in-sample ceiling. NewsCLIPpings has no equivalent rule; pilot per-strategy accuracies are not one.
- Per-source-pair table. MMFakeBench test: 14 pairs, paired minus text-only from −18.0 to +18.4 pp. Fakeddit, the only mixed pair, has within-pair macro-F1 of 11.2% paired vs 14.2% text-only. For A: a per-strategy table on NewsCLIPpings test, after confirming the test rows carry `source_dataset`.

## 4. Prerequisites still missing

From the handoff's "What is missing" list:
1. No backward pass, optimizer step, 735-step run, or 60-minute cap has been tested (item 2).
2. No trainer configuration, trained-checkpoint reload, resume, or evaluation binding (items 3, 6–8).
3. Instruction wording differs between the v1/v2 dev files and frozen `questions.json` (item 9); the probe's wording is not verified against it.
4. Input key: the bundle uses `state_text`, the harness uses `context` (item 14).
5. Two macro-F1 implementations (`class_metrics`, `metrics._native`) are not tied together (item 15).
6. Weight license unchecked (item 13). GPU requirement unspecified (item 12).
7. Option A only: VisualNews reuse terms are unresolved. The NewsCLIPpings access closeout reports 6 usable of 7,024 attempted, while the pilot featurized 12,024 of 12,024 rows. Reconcile before any test score. The full run also needs a separate user go.

## 5. Compute

Transfer-probe Amendment 1: CPU about 2.27 s/row vs MPS 0.27 s/row (20 validation images; native probabilities identical to four decimals; 576-d features max absolute difference 2.4e-4). The pilot's full-run estimate is about 6.3 h at 3.45 rows/s, excluding VERITE.

Derived, not measured: Option B's 735 steps × batch 2 = 1,470 row draws × 2.27 s ≈ 56 minutes for forward passes alone on CPU. That leaves about 4 minutes of the 60-minute cap for all backward passes, so the run would very likely hit the cap on CPU. An older environment note (`mmfakebench_finetune_dev_v1/environment.md`) records MPS as unavailable; on 2026-10-25 MPS was available in the vision environment and ran the forward pass at 0.27 s/row (transfer probe v1, Amendment 1). Backward-pass speed on MPS is not measured.

## 6. Sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| User | | | |
| Instructor | | | |

Date of sign-off: ____________
