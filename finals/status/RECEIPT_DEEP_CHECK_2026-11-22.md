# Receipt Deep Check — Main Run (2026-11-22, ~17:47 ET)
Method: independent script (receipt_audit.py) run on the pod against the raw receipt files — not the run's own summaries. VM-side October audit: data/reports/saved_results_audit.json.

## PASS — verified from the files themselves
- **All 12 grid receipts** carry: seed 20261122; base thaitea/laya-vision @ f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc; n_train_records 980; tune_metric_form "class4"; per-step loss arrays with length == steps (245/490/735), no NaN/Inf, endpoints matching loss_first/loss_last; 4-class recalls all in [0,1].
- **Trainable-parameter fingerprints are constant per arm:** full = 114,728,323 in all 6 receipts (matches amendment (b) exactly); LoRA = 12,603,715 in all 6.
- **Winner integrity:** winner.json (full · soft_ce · 735, 0.7389) is the exact argmax of the 12 receipts — recomputed independently, MATCH.
- **Gates:** token audit over 1,400 records — 0 skipped, 0.0% over MAX_LEN 1024 (mean 18.1 tokens, max 43); checkpoint round-trip 416 tensors bit-identical; pin recorded in gates.json.
- **Packs:** mmfakebench pack correct (4 labels, macro_f1, splits val/test); checkpoint pointer resolved to "WINNER" after selection; temperatures null (calibration not yet run — correct); noul_threshold 0.5 default.
- **Supplementary isolation holds:** canonical runs/ count is exactly 12; supplementary receipts live only in runs/supplementary/ (head_rlcd_490 verified: F1 0.259, seed 20261122, n_train 980, trainable 8,462,659).

## FINDING (reporting-level, not a run defect) — the val baseline moved
- October audit (saved predictions): MMFakeBench val paired **acc 0.320 / macro-F1 0.1985** (n=1,000).
- Today's pod baseline (same 1,000 val rows, same pinned checkpoint): **acc 0.293 / macro-F1 0.2079**.
- Cause, evidenced: the native choice question WORDING differs — today's pack asks "Using only the supplied content, which dataset label best describes this item? Predict the benchmark label; do not claim independent factual ve…" (packs.json), not October's original phrasing. October's own wording experiment measured swings of this size (±0.03, CI crossing zero). Checkpoint drift is excluded by the pin + round-trip gate; population drift is excluded (same val file, gold support 300/300/100/300 in both).
- Handling for the paper: the BEFORE table must use ONE wording consistently, or footnote the delta. The test-once bootstrap is unaffected — it compares against the October TEST baseline predictions (macro-F1 0.20374), a different artifact.

## MINOR NOTES
- LoRA receipts record lr_encoder = null (adapters carry their own LR, shown as lr_head 0.001). Schema nuance, not an error; the final record should label it so a reader doesn't read it as missing data.
- Head-only trainable count (8,462,659) is the same order as LoRA's — LAYA's typed head is a 2-layer module, not a linear probe. The paper should not describe the head-only arm as a "linear probe"; it is head-only fine-tuning. (October's +6.24 pp probe WAS a true linear probe on frozen features — different object, keep the two distinct.)
