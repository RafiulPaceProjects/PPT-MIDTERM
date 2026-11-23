# Status — 2026-11-23 (afternoon)

Paper: v0.3.0 (unchanged in this update). This note records the v2
EvidenceGate Stage A result and the Amendment 11 noul drill-down
(Phases 1 and 2). All numbers are traced to the artifacts committed
alongside this note in `finals/results/`.

## Stage A — NewsCLIPpings probe, full judging (n = 298)

Source: `v2_probe_stagea_results.json`.

| Arm | Headline acc | Acc incl. uncertain | Uncertain |
|---|---|---|---|
| P0 (pair-only) | 0.4295 | 0.5134 | 44 |
| P1A (evidence) | 0.4497 | 0.5302 | 56 |
| P2A (evidence) | 0.4497 | 0.5302 | 56 |
| P1B | 0.3792 | 0.5067 | 80 |

- P1A vs P0: Δ +0.020, 95% CI [−0.027, +0.067]. P2A identical.
- P1B vs P0: Δ −0.050, 95% CI [−0.097, −0.003].
- Read: the evidence arms sit about 2 points above pair-only with an
  interval that includes zero; P1B is significantly below P0. No
  success verdict was registered for the n = 30 pilot, and Stage A
  does not change that posture: evidence helps slightly at best on
  this probe, it does not solve NewsCLIPpings.

## Noul drill-down Phase 1 — baseline screens (BASE checkpoint)

Sources: `v2_probe_noul_drilldown_{ncp,verite,mmf}_screen_result.json`;
full write-up in `v2_probe_NOULS_SECTION.md`; setup rationale in
`v2_probe_QUESTION_SETUP_DECISION.md`.

- **NewsCLIPpings** (tune n = 100): best admissible single = **W5**
  (truth-framed), deployed as a single at T = 12.0, τ = 0.45. W5
  fitted acc 0.54, Δ +0.03. Caveat recorded in the section: W0 keeps
  the best AUC (0.5816 vs W5 0.4464) and best fitted acc (0.56); W5
  won on the registered rule. Battery B3 not admissible (Δ −0.01).
- **VERITE** (tune n = 100): best admissible single = **W3**
  (original context), deployed as a single at T = 12.0, τ = 0.475.
  W3 AUC 0.5677, fitted acc 0.62, Δ +0.03, fitted α 0.56 vs the W0
  baseline α 0.72. Battery B3 not admissible (Δ −0.04).
- **MMFakeBench** (tune+calib n = 210, tune only; test split closed):
  best single = **W1** (direct probability), AUC 0.6735, fitted acc
  0.6857, Δ +0.1048 against a W0 that ranks below chance (AUC
  0.4266). Deployed form = **battery B3 [W1, W2, W4]**, admissible:
  acc 0.6762, Δ +0.0952, α 0.4127 (baseline α 0.8254), τ = 0.475.
  The battery deploys under the registered preference rule because
  W1's Δ beats B3's by less than 2 points.

## Noul drill-down Phase 2 — fine-tune test on tune

Source: `v2_probe_noul_drilldown_p2_results.json`.

- **NewsCLIPpings: winner B (battery).** Battery (members W0, W1, W5):
  noul AUC 0.5392, acc 0.50, α 0.28 (Phase 1 baseline α 0.94).
  Single form (W5): noul AUC at T = 1 of 0.4252, fitted acc 0.50,
  fitted α 0.0.
- **VERITE: winner S (single).** Single form (W3): fitted acc 0.60,
  fitted α 0.5556, noul AUC at T = 1 of 0.5228. Battery form
  (members W0, W2, W3): noul AUC 0.6115, acc 0.54, α 0.3333.
- MMFakeBench Phase 2 had not been recorded in `p2_results.json` at
  the time of this note.

## Stage B calibration fit (AM6)

Source: `v2_probe_stageb_calib_fit.json` (n = 100 per arm).
Pair-only: T = 0.0328, threshold 0.5456, balanced acc 0.63.
Evidence: T = 0.0300, threshold 0.5200, balanced acc 0.58.

## What remains

- Phase 3 evaluations are running: one reporting evaluation per
  dataset with the frozen Phase 2 winners (NCP probe items, VERITE
  held-out 200). MMFakeBench Phase 3 reports on validation only;
  its test split stays closed.
- After Phase 3: fold the verified v2 results into the fork paper
  (exp/v2-retrieval), complete REPORT.md, pull pod artifacts,
  terminate the pod.
