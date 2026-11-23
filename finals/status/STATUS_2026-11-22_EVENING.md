# Status — evening of the main run (2026-11-22, ~19:10 ET)

Snapshot taken mid-run. Everything below traces to a receipt, a predictions
file, or an independent audit report in this folder. The run is NOT complete;
the final record replaces this snapshot when the run terminates.

## Done and verified
- **12-config grid complete.** Winner = full fine-tune · soft_ce · 735 steps,
  tune macro-F1 **0.7389** (MMFakeBench tune, 105 items, 4-class form).
  Base model on the same set: 0.259. Winner per-class recalls
  0.66 / 0.97 / 0.70 / 0.61 — the zero-shot collapse (1/300 originals) is gone.
- **Seed check:** winner recipe retrained at seed 20261123 → **0.732**
  (delta −0.007). The result is the recipe, not a lucky seed.
- **PASS 1 (NewsCLIPpings baseline stream): complete.** 7,024 / 7,024 rows
  scored, 0 skipped, accuracy **0.5141** (recomputed independently from the
  raw predictions file; gold split exactly 3,512 / 3,512).
- **Baselines (this run, pack protocol):** MMFakeBench val F1 0.2079 /
  acc 0.293; VERITE acc 0.3467. October test-ablation baseline F1 0.20374
  (9,999 ok rows) is the test-once comparator.
- **Supplementary ablation tier: 13 of 15 receipts in** (head-only ×4,
  LoRA r8 ×2, r32 ×2, encoder-LR 5e-6 ×2, 2e-5 ×2, seed check). Remaining:
  the two data-size runs (245 / 122 items), which execute last by design.
  Headline ablations: soft_ce beats rlcd in every matched pair; LoRA rank
  cliff at r32 (0.117 / 0.224); head-only saturates then degrades; the
  registered encoder LR (1e-5) is bracketed — 5e-6 never catches up
  (0.644 @735), 2e-5 is strong but does not pass the winner (0.718 @735).
- **Independent verification (two swarms, 11 agent reports in this folder):**
  receipts CLEAN (winner argmax exact, zero NaN/Inf in 25 loss arrays);
  baselines CLEAN (every metric recomputed from raw rows to full precision);
  protocol hygiene NO VIOLATIONS (test untouched, metadata ban key-verified
  on all 980 MMF records, calibration not yet fitted); budget WITHIN
  BUDGET (balance $6.59 at 19:06 ET, spend $3.19, effective $0.898/hr);
  Space v2 READY (pack questions 20/20 diff match vs the notebook registry).
  Two catches were actioned: (1) the October ablation file holds exactly
  one error row — the paired bootstrap must exclude that id symmetrically;
  (2) Drive sync receipts — the run now logs a timestamped read-back at
  each remaining stage boundary.

## In flight
- **NewsCLIPpings arm:** the 18:06 ET carve failure (missing train metadata)
  was fixed by rebuilding the metadata pod-side from the archive's data.json
  (coverage 59,876/59,876 ids; loader-verified splits 71,072 / 7,024 /
  7,264; captions matched to the Mac files). The carve SPEC is computed —
  **2,501 items over 2,120 unique images (train 2,001 / tune 250 /
  calib 250)** — and the stream-save of its images is in progress
  (hundreds saved at snapshot time; record files are written when the pass
  completes). Its two trainings (winner's recipe × 490 / 735) follow.
  NOTE: an earlier chat summary described the carve as "landed" from the
  spec line alone; the on-disk state at this snapshot is images-only.
  The spec is verified; the save is not yet complete.
- **Main closing sequence (queued):** winner trained eval on MMF val →
  test-once + paired bootstrap (H1) → VERITE transfer (H3) → PASS 2 with
  the NCP winner (H2) → calibration (H5) → four closing analyses →
  H1–H5 verdict → publish (both HF winner repos + Space v2) → artifact
  pull → pod terminated → final report.

## Money
Balance $6.5852 (live read 19:06 ET) · spent $3.19 · projected total
$7.24–7.69 vs the $8 hard stop · PASS 2 is the swing item; descope order
(supplementary → NCP arm → never the core) is the relief valve.

## Documentation in this commit
- status/: this snapshot, mainrun_log.md (the run's own log), both swarm
  rounds (swarm_*.md, swarm2_*.md), RECEIPT_DEEP_CHECK, the midterm→final
  issues review, the Space design decision, the refreshed presenter
  walkthrough, mistakes.md (updated).
- results/: INTERIM_RESULTS_2026-11-22.md (verified numbers so far).
- code/: space_app.py = Space v2 (per-dataset weight switching, visual
  input → processing → output), space_README.md.
