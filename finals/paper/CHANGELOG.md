# Paper changelog

Every version of the LAYA study paper, what changed in it, and the
evidence each change stands on. Protocol: `VERSIONING.md`.

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
