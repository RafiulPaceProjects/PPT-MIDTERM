# VERITE 80:20 Side-Arm — Registration (2026-11-22, owner-directed)

Registered BEFORE any VERITE training data is touched. This arm is part of the v2
study (paper fork exp/v2-retrieval). It does not modify, replace, or re-open the v1
record: H3 (transfer, NOT MET at 0.3506) stands exactly as registered and reported.

## Question
Does IN-BENCHMARK adaptation on VERITE's own rows beat TRANSFER to VERITE, for the
same model and recipe family? (v1 measured transfer only, by design.)

## Data
- Source: the local VERITE copy used in v1 — 1,001 rows, 663 image files (rows share
  images). The official benchmark is 1,000 items; the local copy's extra row is
  handled by the grouping rule below and the discrepancy is reported, not hidden.
- Split: 80:20, GROUP-AWARE — the split unit is the image identity (file/hash), so
  no image, and no near-duplicate of one, appears on both sides. Stratified by gold
  class as far as grouping allows. Seed 20261122 (the v1 seed). Split membership is
  written to verite_sidearm_split.json BEFORE training and frozen.
- From the 80% side only: a 100-item tune carve (group-aware, same rule) for step
  selection. The 20% side is the test set for this arm, scored ONCE per model below.
- Metadata ban applies (no source fields as features), as in v1.

## Arms (all scored on the identical held-out 20%)
1. BASE — thaitea/laya-vision @ f2fe3c1, zero-shot (reference).
2. TRANSFER — the v1 MMFakeBench winner (runs/full_soft_ce_735), zero-shot on
   VERITE (the H3 configuration; its full-set number was 0.3506 — here it is
   re-scored on this arm's test rows only, for pairing).
3. ADAPTED — fine-tuned from the BASE checkpoint (not from the MMF winner, so the
   comparison isolates in-benchmark training) on the train side, v1 recipe family:
   full arm, soft_ce, vision tower frozen, two-question format (VERITE native
   choice + fake noul, v1 pack wordings). Step budget selected on the tune carve
   from {245, 490}; the loser is reported too.

## Scoring (attuned to a small test set)
- Primary metric: accuracy (VERITE's native metric). Secondary: macro-F1,
  per-class recalls.
- Paired bootstrap (2,000 resamples, seed pinned) for ADAPTED − TRANSFER and
  ADAPTED − BASE on identical items; intervals reported with every number. At
  n≈200 the intervals will be wide (±~7 pp) — stated wherever the result is quoted.
- Success criterion, stated in advance: ADAPTED beats TRANSFER with the bootstrap
  95% lower bound > 0. Anything else is reported as measured, including a null.
- Comparability warning, mandatory wherever reported: published VERITE numbers
  (LAMAR 54.9, benchmark best 52.1) are on the full set under their protocols;
  this arm's numbers are on a 20% carve under ours and are NOT comparable to them.

## Budget and execution
Runs on the probe's pod session after the pilot judging leg; added pod spend cap
~$1; pod terminated welded to the artifact pull. Artifacts: split file, training
receipt, predictions for all three arms on the test rows, verite_sidearm_results.json,
and a section in the probe REPORT.md.

## Parent prediction (recorded, not a criterion)
ADAPTED lands in the low-to-mid 0.40s on the test carve — a real but modest gain
over transfer, driven by class-balance learning and the partly stylistic
miscaptioned class; it does not reach the low 0.50s.

## Amendment (2026-11-23) — EVIDENCE arm + promotion to full track

The side-arm is promoted to a scheduled track (budget cap ~$3,
actuals reported). A fourth arm is added: **EVIDENCE** — EvidenceGate
attached to the VERITE pack. For each held-out item, evidence is
retrieved (caption → harness queries → SearXNG) and frozen under the
NCP probe's contamination rules (fact-check domains excluded;
claim-matched fact-check and verdict-content passages excluded by
content class; CCN same-source filter; VERITE items carry no
publication dates, so the date rule degrades to the undated stratum,
reported as such). Judged by the BASE checkpoint, VERITE pack
questions verbatim, context = caption + §6.1 evidence block, scored
on the identical held-out 20%. Per-class recalls (true /
miscaptioned / out-of-context) are reported for every arm. Note:
VERITE items originate from fact-check articles, so claim-matched
exclusion is expected to bite hard — the exclusion counts are part of
the result. Chronology: this amendment arrived after ADAPTED training
had begun under the original registration; the EVIDENCE arm involves
no training and is registered before any evidence-arm retrieval or
judging.
