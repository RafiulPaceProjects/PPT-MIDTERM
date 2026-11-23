# Paper changelog

Every version of the LAYA study paper, what changed in it, and the
evidence each change stands on. Protocol: `VERSIONING.md`.

## v0.1 — 2026-11-23 — the complete-record paper

- **Features:** full rewrite from the finalised results bundle
  (`final_results_bundle.json`) by the DeepSeek-backend PaperOrchestra
  pass (v4-pro writing stages, flash grunt stages; total DeepSeek spend
  $1.36), gated and fixed by the parent verifier before this snapshot.
- **Information:** the complete study — the 12-config fine-tuning grid
  and winner (full / soft_ce / 735, tune macro-F1 0.7389), the
  supplementary tier of 15, test-once macro-F1 0.6020 with paired
  bootstrap +0.3983 [0.3853, 0.4108] (test scored once, now closed),
  the calibration finding with its held-out qualification, the
  NewsCLIPpings trained arm (H2 NOT MET, 0.5104 vs 0.5141 baseline),
  VERITE transfer (H3 NOT MET, 0.3506), the 0.9150 metadata leakage
  ceiling, the six-protocol fragmentation audit, and the metered cost
  ledger ($5.64 metered GPU; $0.04 per 1,000 predictions).
- **Gate fixes applied at this version:** the template author block is
  replaced by the real byline (Rafiul Haider, Harika Etikela, Ananya
  Saravani Ganni, and Krishna Batula — Pace University, Analytics
  Capstone, Fall 2026); 16 seeded references merged into the
  bibliography (68 entries; all 49 cited keys resolve); the draft's
  "anonymized submission" wording corrected; all 450 numeric literals
  traced to the bundle or the run record via `tools/verified_numbers.json`
  (259 sourced entries).
- **Gate verdict:** `tools/verify_draft.py` PASS (0 warnings — the
  v0.0 section-4.6 regime-mix pattern does not appear); clean-room
  compile, 13 pages, zero undefined citations or references.

## v0.0 — 2026-11-22 — baseline archive

- **Features:** the PaperOrchestra run #2 refined draft, archived
  unchanged as the pipeline's starting point (`versions/v0.0/` —
  `paper.tex`, built `paper.pdf`, and its original `references.bib`).
- **Information:** covers **only the October diagnosis half** of the
  study — the zero-shot evaluation of LAYA-Vision (class collapse onto
  the mismatch class, degenerate-floor comparisons, the frozen-feature
  transfer probe). It contains **none** of the November main-run
  results: no fine-tuning grid, no test-once score, no calibration
  finding, no NewsCLIPpings arm verdict. Those arrive in v0.1, written
  from the finalised results bundle.
- **Known flags carried, not fixed** (recorded in `NOTE.md` and the
  run's verification note): the §4.6 published-comparison passage mixes
  regimes (GPT-4V Standard 51.0 beside LLaVA MMD-Agent 49.9; LLaVA
  Standard is 25.7) — the CI gate warns on this pattern; VERITE is
  stated as 1,001 items (the local copy) without the qualifier; one
  ablation range mixes units (−1.51 pp with a proportion-scale CI);
  the bibliography holds only the draft's three citations.
- **Pipeline change (not a paper change):** the living draft in
  `draft/` starts as a copy of this version with two deliberate,
  documented differences — the template author block is replaced by
  the real byline (Rafiul Haider, Pace University), and a header marks
  it as the pre-final skeleton awaiting the complete-record rewrite.
  The v0.0 snapshot itself is byte-identical to the PaperOrchestra
  output.
- **Gate:** `tools/verify_draft.py` passes on the living draft
  (3 cited keys resolve; 143 numeric literals traced against
  `tools/verified_numbers.json`; 1 warning — the §4.6 pattern above).
  Authorising record for the October numbers: the October saved-results
  audit, as summarised in `VERIFICATION_NOTE_2026-11-22.md`.

## v0.1.1 — 2026-11-23 (patch: title, framing, byline rendering)
- Title restored to the three-track study's submitted title, per the author's
  direction: "Three Modalities, Three Tracks", with the new subtitle
  "The Combined Track, Completed: Pre-registered Fine-Tuning across Three
  Benchmarks".
- Introduction gains a continuity paragraph framing this paper as the
  completion of the combined track of the three-track study whose abstract
  specified the fine-tuning programme this paper executes.
- Final-copy mode enabled (\iclrfinalcopy): the PDF now prints the real
  byline (Rafiul Haider, Harika Etikela, Ananya Saravani Ganni, and Krishna
  Batula — Pace University, Analytics Capstone, Fall 2026) and drops the
  review ruler. Note: v0.1's PDF rendered "Anonymous authors" because the
  style was in review mode; the names were in the v0.1 source throughout.
- No scientific content changed. Gate: PASS, 0 warnings; 13 pages,
  0 undefined citations/references.

## v0.1.2 — 2026-11-23 (patch: SARD title and author order)
- The author supplied the abstract actually accepted to SARD (Seidenberg
  Annual Research Day 2026, December 11, 2026). Its title supersedes the
  October three-track draft title used in v0.1.1: the paper is now titled
  "Testing Input Evidence and System 1 Decisions in Misinformation
  Classification", subtitle "Pre-registered Fine-Tuning of a Typed-Decision
  Vision-Language Model across Three Benchmarks".
- Author order now matches the accepted abstract: Ananya Saravani Ganni,
  Harika Etikela, Rafiul Haider, and Krishna Batula.
- The introduction continuity paragraph is rewritten against the accepted
  abstract: the companion study varied input evidence at evaluation time
  with frozen models; this paper varies it at training time.
- No scientific content changed. Gate: PASS, 0 warnings; 13 pages,
  0 undefined citations/references.

## v0.1.3 — 2026-11-23 (patch: terminology, author direction)
- The word "bootstrap" is removed from the paper at the author's direction.
  The procedure is unchanged and is now described in plain terms throughout:
  "paired resampling", "paired-resampling 95% CI", "2,000 resamples". The
  pre-registered criterion reads "paired-resampling 95% CI lower bound
  greater than zero". Run records and the results bundle keep the standard
  term; only the paper's prose changed.
- No numbers, results, or claims changed. Gate: PASS, 0 warnings; 13 pages,
  0 undefined citations/references; the compiled PDF contains zero
  occurrences of the removed term.

## v0.1.4 — 2026-11-23 (patch: title numeral spelled out, author direction)
- "System 1" becomes "System One" in the title and in the introduction's
  reference to the companion study, at the author's direction (no numeral
  in the title). Note: the SARD programme listing itself prints the
  numeral; the paper's title page now spells the word out.
- No other change. Gate: PASS, 0 warnings; 13 pages, 0 undefined.

## v0.1.5 — 2026-11-23 (patch: Gemini row removal and humanizer pass, author direction)
- Table 1 (cost ledger): the "Gemini spend" row is removed at the author's
  direction. It was the paper's only mention of an AI system used in the
  research process; the surrounding cost prose does not reference the row
  and is unchanged. (The DeepSeek-V3 bibliography entry is a literature
  citation and stays, as do all compared-system mentions.)
- Humanizer pass: all nine LaTeX em dashes are removed. Four were prose
  (introduction): the companion-study parenthetical now uses parentheses,
  and "outcomes, positive and negative," now uses commas. Five were
  missing-value cells in the NewsCLIPpings and VERITE tables (baseline
  falsified recall, binary-screen AUC, and the three baseline per-class
  recalls), now marked "n/a"; those cells carried no values and none are
  added. "We additionally report" becomes "We also report" (related work).
- No numbers, results, or claims changed. Gate: PASS, 0 warnings; 13 pages,
  0 undefined citations/references; the compiled PDF contains zero
  occurrences of "Gemini", zero rendered em dashes, and zero "additionally".

## v0.2.0 — 2026-11-23 (minor: figures and baseline details, author direction)
- Seven figures added at the author's direction, so reviewers can see the
  results and the system rather than only read tables: (1) the companion
  study's three evidence tests redrawn from its SARD abstract (its Figure 1
  is a schematic of the three tests; the chart plots the abstract's own
  stated accuracies — WELFake 96.5 → 96.2, CIFAKE 96.3 → 85.6, MMFakeBench
  frozen 27.93 text-only vs 26.42 image+text), captioned as the companion
  study's results; (2) a LAYA-Vision architecture diagram (frozen vision
  tower, trainable encoder/head, choice + noul questions, arbitration);
  (3) the frozen experiment pipeline flow; (4) the 12-configuration tune
  grid as a heatmap with the winner outlined; (5) before/after headline
  bars per dataset on native metrics, with the NewsCLIPpings null and the
  VERITE near-flat results shown at the same scale; (6) the data-size
  curve and LoRA rank ladder from the supplementary tier; (7) an appendix
  collage of verbatim excerpts from the executed run notebook (frozen
  configuration, environment/GPU check, grid table, winner selection,
  test-once marker, H1–H5 verdicts; repeated library deprecation warnings
  omitted, no values altered).
- The five baseline cells left "n/a" in v0.1.5 are now filled from the
  saved baseline prediction files (BASELINE_DETAILS_2026-11-23.md;
  recomputation reproduces the published baseline accuracies exactly):
  NewsCLIPpings baseline falsified recall 0.944 and binary-screen AUC
  0.549; VERITE baseline recalls 0.429 (truthful), 0.009 (miscaptioned),
  0.612 (out-of-context). No "n/a" cells remain.
- Every figure number traces to `tools/verified_numbers.json` (271
  entries; the six companion-study accuracies, the five baseline details,
  and the ResNet18 name digit added with their sources). Gate: PASS,
  0 warnings; 17 pages, 0 undefined citations/references; the compiled
  PDF still contains zero occurrences of the prohibited terminology and
  zero rendered em dashes.

## v0.3.0 — 2026-11-23 (minor: code appendix with pseudocode, author direction)
- New Appendix D, "Code Appendix: Pseudocode", at the author's
  direction ("put in pseudocode for the NewsCLIPpings verifier and
  the codebase on the important additions"). Each block is a faithful
  compression of the real code: same steps, same order, the source's
  named constants, no invented steps. Contents: (1) the VisualNews
  stream verifier — `verify_image_bytes` (full decode, oversize and
  degenerate-dimension refusals, decode-by-content, palette
  transparency route) and `stream_verified` (single-pass tar stream,
  path normalisation, referenced-member matching, skip ledger with
  per-source accounting, 120 s inactivity timeout); (2) the parallel
  stream engine that executed PASS 2 and its equivalence gate
  (spawn-context reader/decode/inference processes, single writer,
  dead-worker guard, reconciliation; gate: at least 100 shared
  items, labels identical, probability drift at most 0.001 — the
  executed run compared 120 items with zero mismatches and zero
  drift); (3) under an explicit "post-study additions" label, the
  v2 EvidenceGate state machine (Intake → Route → PairOnly|Retrieve
  → Judge → Arbitrate, with its trigger math and five-step RETRIEVE)
  and the v2 retrieval repair loop (serial re-run of empty pools,
  1 s pacing, circuit breaker of 10 consecutive empties → 240 s
  pause, per-pair checkpoint flush). The v2 blocks state in the
  appendix itself that no result in the paper depends on them.
- The same four blocks are committed as a standalone document,
  `finals/code/PSEUDOCODE.md`, with "what this is / where the real
  code lives" headers. The real sources are now in `finals/code/`:
  `visualnews_stream.py` and `laya_trainer.py` refreshed to the
  final run versions (the earlier copies predated the parallel
  range reader and the tune-form patch), and
  `parallel_stream_engine.py` + `parallel_gate_cell.py` added.
- Five new allowlist entries, all code constants with their source
  files named (276 entries): the 200,000,000 declared-pixel
  ceiling, the 600-character passage cap, the 20 s retrieval
  timeout, the 240 s circuit-breaker pause, and the SHA-256 name
  digit (same convention as the ResNet18 entry). No results,
  numbers, or claims of the study changed. Gate: PASS, 0 warnings;
  22 pages, 0 undefined citations/references, 0 overfull lines; the
  compiled PDF still contains zero occurrences of the prohibited
  terminology and zero rendered em dashes.

## v0.4.0 — 2026-11-23 (minor: the merged paper — Part II integrated, author direction)

- **Features:** the ONE merged paper the owner directed (2026-11-23
  13:17 ET shape decision; build authorised 16:36 ET). Part II is now
  written into the body, not framed as future work: new sections
  EvidenceGate (design, retrieval collapse and repair, reproducibility
  audit, pilot, Stage A, Stage B with the pristine collapse, the
  scorer defect and audit, the VERITE four-arm track, the AM6 screen
  read), the noul drill-down (eighteen frozen wordings, three tune
  screens, corrected-rule verdicts, Phases 2 and 3, the temperature
  lesson), Closing Experiments (MMFakeBench Phase 3, the G12
  confirmation screen, Arm W), Situations Faced, and Threats to
  Validity and Warnings. Conclusion rewritten to the whole-study
  claims (surviving and dead). Appendix A gains the Part II
  registration and deviation record; Appendix D's v2 subsection is
  reframed as Part II machinery (its "no result depends on them"
  label removed).
- **Information:** every Part II number traces to
  `~/workspace/misinfo_run/LAYA_FINAL_RECORD.md` (board-fixed,
  critical-check clean) or `v2_probe/ANALYSIS_GAPS.md`; 274 new
  entries added to `tools/verified_numbers.json` with sources (550
  total). Folded in during the build, as they landed mid-build: the
  VERITE full-set scoring (Amendment 14,
  `v2_probe/uplift/verite_fullset_results.json`) and the Stage B tune
  read (Amendment 16, `v2_probe/uplift/stageb_tune_read.json`).
- **Features (uplift changes 2+3):** three new figures —
  fixed-coverage curves for Stages A and B
  (`figures/fig_coverage.pdf`, data from `v2_probe/SCORER_AUDIT.md`
  section 3), the CAL-1 calibration picture
  (`figures/fig_cal1.pdf`, record 2.3), and the standalone data-size
  curve (`figures/fig_datasize.pdf`, record 2.1) — plus the tables
  the analysis supports (Stage A, Stage B, Stage B per-class,
  VERITE held-out and full-set). The two honest contributions are
  named explicitly in the abstract, the introduction, and the body:
  the abstention-accounting standard, and the warnings section
  (leakage ceiling 0.9150, calibration transfer harm, fragile fitted
  operating points, the abstention trap).
- **Information (record-consistency fixes to Part I):** the cost
  ledger now follows the final record (total pod spend about $6.83;
  metered training $2.14 over 29 trainings; rehearsal $0.17; pre-grid
  burn $0.72), replacing the $5.64 metered figure; the winner's
  validation macro-F1 0.7571 is removed (the record cites validation
  accuracy 0.7690 only) and the validation-to-test gap is restated on
  accuracy; H2 and H5 statements aligned to the record's registered
  wording; H4 minimum tune recall stated as 0.6129; the calibration
  table gains the tune row (0.1941 to 0.0778); the winner's test
  error analysis (3,870 errors, 2,375 on the original/mismatch
  boundary) added from ANALYSIS_GAPS 4a; byline surname corrected to
  Krishna Bathula per the SARD abstract of record.
- **Pending slot (one):** the NewsCLIPpings scale probe (Amendment
  15) was still running at cut time. Its subsection carries the
  registered design and a clearly marked result slot with no numbers
  claimed; a fold-in pass follows when it lands, before any version
  is called final.
- **Gate verdict:** `tools/verify_draft.py` PASS (0 warnings);
  TinyTeX compile clean, 35 pages, zero undefined citations or
  references; no "bootstrap" wording, no em dashes in prose.

## v0.4.1 — 2026-11-23 (patch: defense-hardening pass, owner direction)

- **Purpose:** red-team pass over v0.4.0 as a hostile examiner would
  read it; full matrix in `~/workspace/misinfo_run/PAPER_DEFENSE_AUDIT.md`
  (39 attacks graded: 34 defended by the paper as written, 5 thin,
  all 5 fixed here; 2 open items, both named in the audit). No new
  claims; every added number traces to the final record or
  ANALYSIS_GAPS, with 4 new sourced entries in
  `tools/verified_numbers.json` (554 total).
- **Fixes:** (1) NewsCLIPpings macro-F1 pair added (baseline 0.4036,
  trained 0.4436; record 2.2), in the text and in Table tab:ncp,
  with the verdict stated to read on the native metric, accuracy.
  (2) Cost ledger completed with the probe's remaining metered spend
  from record 8.1 (about $3.05 first pod, $1.20 unreachable pod,
  about $0.14 wedged pod, about $0.50 of retrieval and assembly
  calls), so the abstract's complete-ledger claim is itemised in
  the body. (3) Stage B carve provenance stated in the Stage B
  section: train-side, disjoint from the probe items, zero item and
  image overlap between its splits (670 unique images across 700
  items; ANALYSIS_GAPS 5). (4) VERITE four-arm BASE identified as
  the base checkpoint read on the held-out 200 only, not the v1
  full-set baseline. (5) The small difference between the Amendment
  14 full-set BASE/TRANSFER reads and the v1 reads on the same rows
  (0.3526 against 0.3467; 0.3586 against 0.3506) is now disclosed in
  the full-set paragraph, with each verdict stated to rest on its
  own run's reads.
- **Pending slot (one, unchanged):** the NewsCLIPpings scale probe
  (Amendment 15); fold-in still owed before any version is called
  final.
- **Gate verdict:** `tools/verify_draft.py` PASS (0 warnings);
  TinyTeX compile clean, 35 pages, zero undefined citations or
  references; no "bootstrap" wording, no em dashes in prose.
