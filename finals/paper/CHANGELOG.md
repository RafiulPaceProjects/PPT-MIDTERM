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
