# Interim results — verified, mid-run (2026-11-22 ~19:10 ET)

INTERIM: the test-once, VERITE transfer, NewsCLIPpings arm, and calibration
have not run yet. Every number below was recomputed or cross-checked by an
independent audit (see finals/status/swarm2_*.md). Tune-split numbers are
selection numbers, not final claims.

## MMFakeBench — the 12-config grid (tune macro-F1, 105 items)

| config | 245 steps | 490 steps | 735 steps |
|---|---|---|---|
| full · rlcd | 0.5667 | 0.5880 | 0.6061 |
| full · soft_ce | 0.5954 | 0.6598 | **0.7389** |
| lora · rlcd | 0.4597 | 0.4505 | 0.1946 |
| lora · soft_ce | 0.6282 | 0.5726 | 0.7187 |

Winner: **full · soft_ce · 735** (winner.json = recomputed argmax, exact).
Zero-shot base on the same tune set: **0.259**.
Winner per-class recalls: original 0.66 · textual 0.97 · visual 0.70 ·
mismatch 0.61 (H4's ≥0.25 floor passed on tune).
Seed check (same recipe, seed 20261123): **0.732**.

## Supplementary ablations (tune macro-F1; quarantined from selection)

| ablation | 490 | 735 |
|---|---|---|
| head-only · rlcd | 0.2590 | 0.4899 |
| head-only · soft_ce | 0.4238 | 0.3098 |
| LoRA r8 · soft_ce | 0.7037 | 0.6362 |
| LoRA r32 · soft_ce | 0.1168 | 0.2244 |
| full · soft_ce · encoder LR 5e-6 | 0.6217 | 0.6438 |
| full · soft_ce · encoder LR 2e-5 | 0.6871 | 0.7178 |

Data-size axis (245 / 122 items at 490 steps): pending at snapshot time.

## Baselines — this run, frozen pack protocol

| dataset | split | metric | base model |
|---|---|---|---|
| MMFakeBench | val (1,000) | macro-F1 / acc | 0.2079 / 0.293 |
| MMFakeBench | test ablation (Oct, 9,999 ok) | macro-F1 | 0.20374 |
| NewsCLIPpings | val (7,024, 0 skipped) | accuracy | 0.5141 |
| VERITE | local (1,001) | accuracy | 0.3467 |

## Still to come (in order)
Winner trained eval (MMF val) · test-once + paired bootstrap vs 0.20374 ·
VERITE transfer · NewsCLIPpings arm (2 trainings) + PASS 2 · calibration ·
H1–H5 verdicts · publish.
