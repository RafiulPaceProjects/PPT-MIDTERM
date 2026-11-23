# PaperOrchestra — FINAL PASS requirements (binding)

Set 2026-11-22 at Rafiul's instruction: "make sure you fully effectively
use paper orchestra." This pass writes the FINAL paper from the COMPLETE
record of the main run. It is not a re-run of the baseline draft with new
numbers pasted in. Operator lessons behind each rule: mistakes.md §PO-1..6.

## Inputs — the complete record, seeded properly this time
- Executed notebook + final_results_bundle.json (grid, winner, test-once +
  bootstrap, both stream passes with accounting, calibration, H1–H5
  verdicts, supplementary tier, four closing analyses, cost ledger).
- The saved-results audit, the VisualNews field test report, mistakes.md,
  both swarm rounds, the receipt deep check.
- **Seeded bibliography (PO-1):** required references placed IN the bundle:
  MMFakeBench (arXiv:2406.08772), VERITE (arXiv:2304.14133), plus
  NewsCLIPpings and LAYA citations sourced live via Semantic Scholar and
  verified (title/authors/year match the real papers) — never invented.
  The baseline's 3 verified citations (Tu 2024; Qi 2024 SNIFFER;
  Pedregosa 2011) carry over.
- **Verified benchmark table (PO-2)** in the experimental log: the
  benchmark paper's own macro-F1 table (GPT-4V Standard 51.0/48.8,
  +MMD-Agent 61.6/61.5, LLaVA Standard 25.7) and the fine-tuned/agentic
  framing kept separate (SCPO 66.1, MM-VeriAgent 71.5, T2Agent 75.9 —
  different conventions, labelled as such). The §4.6 regime mix-up cannot
  recur: the paper cites this table.
- **Author block (PO-3):** Rafiul Haider, Pace University, Analytics
  Capstone Fall 2026 (CRN 72369); Team 3 — Ananya Saravani Ganni,
  Harika Etikela.

## Pre-flight (PO-4, PO-5) — before launch, all checked
- LaTeX toolchain present (pdflatex compiles the template).
- Gemini spend headroom vs the $10 cap confirmed; run tally kept.
- Semantic Scholar pacing fixed (1 req/sec across workers) before the
  literature stage runs.
- Liveness watchdog armed at launch, alert-only.

## Run configuration — the system used fully
- All five agents, full pipeline (outline → literature → writing →
  refinement), not a partial pass.
- **Seat map (Rafiul, 2026-11-22 19:25 ET — supersedes the earlier
  Neon-writer config):**
  - **Writer = deepseek-v4-pro** (DeepSeek's best model; verified live on
    his account today — re-verify at pre-flight). It writes the section
    prose from the frozen outline + the seeded bundle.
  - **Reflection / thinking = gemini-4-neon** — it critiques DeepSeek's
    drafts, checks numbers and claims, and drives the refinement loop.
    (Neon earned this seat in the head-to-head: clean and exact, caught
    the planted inconsistency.)
  - **Grunt work = deepseek-flash** (Rafiul, 2026-11-22 19:29 ET):
    enrichment, extraction, formatting and citation mechanics, compile
    fixes — the DeepSeek flash tier takes all of it.
  - Mechanism: PaperOrchestra's agents are Gemini-wired, so the writer
    runs as a hybrid — PaperOrchestra orchestrates (outline, literature,
    refinement, compile) while v4-pro generates the prose externally and
    drafts return for Neon reflection + refinement. In-tool writer
    routing may be attempted at pre-flight ONLY if it smoke-tests clean;
    otherwise the hybrid is the default — the final run is never put at
    risk for it.
  - Budgets: the $10 cap binds the Gemini seats (now lighter — Neon
    reflects, it does not generate the paper). DeepSeek spend is
    separate and reported alongside Gemini's at delivery.
- Amendments (b) frozen vision tower, (c) NCP training arm + H2 re-aim,
  (d) supplementary tier: disclosed in the paper as amendments, with the
  pre-registered H1–H5 stated as registered.
- Known labelling duties: val-baseline wording footnote (pack wording vs
  October wording); LoRA receipts' lr recorded as lr_lora; head-only
  fine-tuning never called a linear probe; VERITE = 1,001 local rows of
  the official 1,000-item dataset, phrased that way.

## Delivery gate (PO-6) — verified BEFORE Rafiul sees a PDF
- Every number traced to final_results_bundle.json or the audit.
- Every citation present, real, and claim-matched (spot-check via
  Semantic Scholar).
- §4.6 checked against the seeded benchmark table; CI ranges in pp.
- Author block real; no placeholder text anywhere.
- Only then: PDF + tex delivered, with the Gemini spend for the pass.
