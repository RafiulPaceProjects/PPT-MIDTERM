# The Research Book — spec (Rafiul, 2026-11-22 19:32 ET)

Rafiul's instruction: the notebook's work will finally have a BOOK which
details all the steps and working we did, with the mistakes we found and
the fixes, made academic, to supplement the full research.

## What it is
The academic companion volume to the paper. The paper argues the
findings; the book documents the whole research — how it was designed,
executed, broken, fixed, and verified — so a reader can follow, check,
and reproduce everything without rerunning anything. The executed
notebook is its primary evidence; the book is its narrative form.

## Source record (assembled before writing, nothing from memory)
The executed notebook + final_results_bundle.json, the saved-results
audit, mainrun_log.md, mistakes.md (full register incl. PO-1..6), the
verifier build log + VisualNews field test report, both verification
swarms + the receipt deep check, the situation log and issues review,
the presenter walkthrough, the PaperOrchestra verification note.

## Chapters
1. **Research design** — the questions, the two-question interface
   (choice + noul), per-dataset packs, the metadata ban and why, the
   frozen success rule, pre-registered H1–H5 as registered.
2. **Data and protocol** — the three datasets, splits, the 490/105/105
   training protocol, leakage controls, the validation↔test exposure
   accounting (9 rows / 14 edges).
3. **The baseline diagnosis** — October's zero-shot study: the mismatch
   collapse, the wording experiment, the transfer probe (+6.24 pp;
   VERITE inconclusive, stated as such).
4. **The stream verifier** — why VisualNews could not be stored
   (91 GB vs 50 GB), the verifier's design, the field test (9,339
   censused, 1 undecodable member), defects vs dataset properties, the
   transcode decision and its reasoning.
5. **The main run** — the 12-config grid and its design logic, the
   supplementary ablation tier (amendment (d)) and the data-size axis,
   the NewsCLIPpings arm (amendment (c)), PASS 1 / PASS 2 accounting.
6. **Results and verdicts** — every number from the bundle: grid,
   winner, seed check, test-once + bootstrap, transfer, calibration,
   the four closing analyses, H1–H5 verdicts with the numbers.
7. **Mistakes and fixes** — the full register, academic register: each
   issue with its evidence, its cause class (wrong object, stale belief,
   missing gate), the fix, and the gate that now prevents recurrence.
   Includes the operator lessons (narration overstatements, the carve
   misreport) and the PaperOrchestra lessons PO-1..6 — nothing airbrushed.
8. **Verification methodology** — how the work was checked: fail-closed
   gates, receipt audits, the two independent swarms (11 reports) and
   what they caught, Drive-sync read-backs, this book's own gate.
9. **Cost and operations ledger** — per-training wall time / GPU / RAM /
   dollars for all 29 trainings, per-stage durations, stream throughput,
   the balance record, the operational requirements to reproduce.
10. **Reproducibility appendix** — configs, seeds, environment pins,
    checkpoint identifiers, the complete artifact inventory with paths.

## Production
Written in the same pass window as the final paper, from the same
complete record, under the same seats (Neon coordinates / thinks /
verifies; deepseek-v4-pro writes; deepseek-flash grinds) and the same
delivery gate: every number traced, every mistake entry matched to the
register, no claim the record does not support. Delivered as a document
(PDF + source) alongside the paper, and committed to the repo with it.
