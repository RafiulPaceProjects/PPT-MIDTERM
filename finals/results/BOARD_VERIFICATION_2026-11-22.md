# Board Verification — calibration & VERITE claims (2026-11-22, evening)

Independent board: methodologist · statistician · reproducibility engineer.
Method: every number below was recomputed by the board from the raw
artifacts on the pod (read-only). Nothing the parent computed was trusted;
the parent's stated procedures were reproduced exactly, then stress-tested
under an alternative binning convention.

## Verdict table

| # | Claim (parent) | Verdict | Board's recomputed value |
|---|---|---|---|
| 1 | QTYPES = {choice 0, score 1, noul 2}; temperatures[0] = 8.4214 is the choice temperature | **CONFIRMED** | `laya.vlm_train.QTYPES` read live = {'choice': 0, 'score': 1, 'noul': 2}. calibration.json: temperatures [8.421399116516113, 1.0, 1.0], ece_before 0.2664268950621287, ece_after 0.08650865100678941, acc_calib 0.7047619047619048, n_calib 210 — all as stated. |
| 2 | Val raw ECE = 0.1056, accuracy = 0.769 (1,000 ok rows) | **CONFIRMED** | ECE 0.105641, accuracy 0.769 (769/1,000), n = 1,000 ok rows with probabilities. |
| 3 | Val with calib T = 8.4214: ECE = 0.3955, accuracy still 0.769 | **CONFIRMED** | ECE 0.395507, accuracy 0.769 — unchanged, as temperature scaling mathematically requires (argmax-invariant). |
| 4 | Split-half (seed 20261122): fit T = 1.65 on half A; half B ECE raw 0.0994 → 0.021 with T; full-1000 fit T = 1.6 | **CONFIRMED** | Fitted T on A = 1.65 exactly. Half B: raw 0.099432, with A-fitted T 0.020971. Full-1000 NLL fit T = 1.6 (in-sample ECE at that T: 0.016535). |
| 5 | VERITE trained file identical to baseline: 1,001 compared, 0 labels differ, both accuracies 0.346653 | **DISAGREED — superseded by the fix (see below)** | On the CURRENT artifacts: 1,001 ids compared, **543 predicted_labels differ**; baseline accuracy 0.346653, trained accuracy **0.350649**; probability dicts differ on all 1,001 rows. |
| 6 | Method soundness (ECE reproduction, split-half validity, artifact risk) | **SOUND, with caveats** | See §Method judgment. |

## Claim 5 — what actually happened

The parent's claim described the state of the files at their check
(~19:52 ET), and that state no longer exists — because the fix the parent
ordered replaced the file. Evidence chain, all independently read:

- The current trained file's provenance names checkpoint
  `/workspace/Misinformation/runs/full_soft_ce_735` (the winner); the
  baseline's names `models/laya-vision-base`. Different run_ids.
- The trained file's mtime (2026-11-23 00:57:20 UTC = 19:57 ET) postdates
  the parent's check.
- The run log's own defect record ("VERITE TRANSFER DEFECT — FIXED +
  VERIFIED, ~20:55 ET") states the pre-fix file held base predictions
  with "0/1,001 rows differ from baseline, accuracy identical 0.346653" —
  the parent's historical claim, corroborated word for word. It also
  records a second defect layer the parent had not seen: the first fix
  attempt was defeated by a checkpoint-blind output-dir reuse cache.
- The log's corrected number — winner VERITE transfer accuracy 0.3506,
  with 543/1,001 predictions differing from baseline — matches the
  board's recomputation exactly (0.350649; 543 diffs).

So: the parent's defect detection was correct; the claim is not
reproducible today only because the remediation succeeded. **The
corrected H3 number (0.3506) is CONFIRMED.** Against the pre-registered
0.38–0.48 band, H3 is NOT MET — a real finding on a verified eval, per
the log.

## Method judgment

- **ECE on stored probabilities is a sound reproduction.** Temperature
  applied as p^(1/T) renormalized is mathematically identical to scaling
  the logits by 1/T before softmax — exact, not an approximation.
- **Not a binning artifact.** The board recomputed every ECE under a
  second convention (floor binning): raw 0.106024 vs parent-convention
  0.105641; T = 8.4214 gives 0.395507 under both; split-half values
  identical under both. Convention differences are ~0.0004; the effects
  are 0.08–0.29. The conclusions are insensitive to binning.
- **Not a row-ordering artifact.** Full-set ECE/accuracy are
  order-invariant aggregates. The split-half depends on order only
  through the seeded shuffle, which the board reproduced exactly
  (same seed → same halves → same T, same ECEs).
- **The split-half is a valid held-out demonstration.** Fit on 500,
  measured on the disjoint 500 from the same distribution: ECE
  0.099 → 0.021 is honest evidence that same-distribution temperature
  fitting transfers, in direct contrast to the calib→val transfer
  failure (0.106 → 0.396). Caveat: at n = 500, a 10-bin ECE carries
  estimator noise on the order of ±0.01–0.02; the qualitative contrast
  (0.021 vs 0.396) is far outside that noise.
- **Scope caveat.** All ECE figures concern the choice question's
  probabilities. The noul temperature never moved from 1.0; nothing
  here speaks to the binary screen's calibration.
- **Internal consistency check passed.** Accuracy identical before and
  after temperature (0.769) is a mathematical necessity; its holding
  exactly confirms the stored probabilities, the gold labels, and the
  board's pipeline are aligned.

## Board opinion on the parent's disposition

**Sound, on both parts.**

1. *Ship raw probabilities (T = 1.0) in the Space.* The calib-fitted
   temperature demonstrably damages the benchmark distribution
   (ECE 0.106 → 0.396). Shipping it would have put badly calibrated
   probabilities in front of users while wearing a "calibrated" label.
   T = 1.0 serves the exact model the paper evaluates.
2. *H5 stands as registered, with the qualification recorded.* The
   registered protocol fitted and measured on the calib split; its
   verdict (0.0865 < 0.15, accuracy unchanged) is what the
   pre-registration specified, and post-hoc verdict-shopping would be
   the actual misconduct. The qualification — held-out transfer failure
   plus the split-half demonstration — converts a checkbox pass into a
   finding (post-hoc calibration is distribution-bound), and the run's
   own tune-split measurement (accuracy 0.7857 → 0.7857) further
   supports that nothing about the verdict was hidden.

The board notes, for the paper: report all three calibration
measurements (calib in-sample, val transfer, val split-half) together.
Presented together they are stronger than any one of them alone.
