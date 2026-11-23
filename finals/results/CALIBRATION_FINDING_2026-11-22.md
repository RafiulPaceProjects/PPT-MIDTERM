# Calibration finding — the calib-fitted temperature does not transfer
(Parent audit, 2026-11-22 ~20:10 ET. All numbers computed from stored
artifacts on the pod; method stated so anyone can recompute.)

## The defect
The calibration stage fitted per-type temperatures on the reserved calib
split and reported ECE on that same split: choice temperature 8.4214,
ECE 0.2664 -> 0.0865 (runs/full_soft_ce_735_calibrated/calibration.json).
That is an in-sample measurement. The temperature encodes the winner's
overconfidence on calib-pool items — a distribution adjacent to the
training data — not its behaviour on the benchmark distribution.

## Verification of the mapping
Library QTYPES = {'choice': 0, 'score': 1, 'noul': 2} (read from
laya.vlm_train on the pod), so temperatures[0] = 8.4214 is the CHOICE
temperature. temperatures[1] = temperatures[2] = 1.0.

## Held-out check (MMFakeBench val, 1,000 rows — never used for fitting
or selection; winner predictions in
data/processed/midterm/trained_mmfakebench_val_v1/paired.predictions.jsonl;
10-bin ECE on stored choice probabilities; temperature applied as
p^(1/T) renormalized; accuracy 0.769 before and after, argmax-invariant)
- Raw model: ECE 0.1056 — already under the H5 bar of 0.15.
- With calib-fitted T = 8.4214: ECE 0.3955 — the in-sample "fix"
  severely damages held-out calibration.

## The correct procedure, demonstrated (split-half on val)
Seed-20261122 shuffle of the 1,000 val rows; temperature fitted by NLL
grid search (0.5..3.45 by 0.05) on half A (500 rows); measured on the
disjoint half B:
- Fitted T = 1.65 (full-val fit for reference: 1.6)
- Half B: ECE raw 0.0994 -> 0.021 with the A-fitted temperature.
Calibration fitted and measured on disjoint data from the SAME
distribution works. A temperature is a property of model x distribution,
not of the model alone.

## Disposition
- H5's registered verdict stands as the protocol defined it (calib
  measurement 0.0865) with this finding recorded beside it in the bundle
  as a qualification — registered verdicts are not rewritten.
- The deployed model (HF Space) ships RAW probabilities (T = 1.0): the
  exact evaluated model. The calib temperature is NOT applied.
- The val-fitted T ~ 1.6 is documented as the deployment-calibration
  alternative (disclosed fitting, predictions unchanged), not applied.
- Same rule pre-registered for the NewsCLIPpings pack: fit on its calib,
  validate on held-out stream rows, ship only what survives.
- Paper framing: post-hoc calibration is distribution-bound — fit where
  you deploy, validate where you did not fit. Framing literature: Tu et
  al. 2024 (already in the bibliography).
