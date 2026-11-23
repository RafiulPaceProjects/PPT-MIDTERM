# Swarm 3 audit — PASS 2 integrity/provenance, VERITE provenance chain, spend
(Read-only audit, 2026-11-22 ~20:28 ET. All checks run live against the pod's
on-disk artifacts via podssh; nothing modified. Accuracy was NOT computed for
the in-flight PASS 2 file — see item 1.)

## 1. PASS 2 INTEGRITY — VERDICT: PASS (partial file, stream still running)
File: `data/processed/midterm/trained_newsclippings_val_v1/paired.predictions.jsonl`
- Row count grew during the audit itself: 489 (first read) → **492 rows** at the
  final parse, against the baseline's 7,024. Scoring is still in flight.
- Every parsed row is well-formed JSON: **0 malformed lines**.
- Every row carries a `status` field: 0 missing; status values so far are
  uniformly `ok` (492/492).
- **Duplicate ids: 0.**
- **Ids outside the baseline id set: 0** — all PASS 2 ids are a subset of
  `baseline_newsclippings_val_v1` ids (7,024).
- **No interim accuracy is reported, deliberately.** The stream consumes the
  archive in source-blocked order, so the rows scored so far are not a
  representative sample of the validation split; any partial accuracy would be
  misleading. The H2 verdict waits for the completed 7,024-row pass.

## 2. PASS 2 PROVENANCE — VERDICT: CONFIRMED, checkpoint = NCP winner
- `trained_newsclippings_val_v1/vision.runtime.json` names the checkpoint
  explicitly: `/workspace/Misinformation/runs/ncp_full_soft_ce_245` — the
  NewsCLIPpings arm winner (full · soft_ce · 245), as expected.
- Each prediction row independently carries `model_provenance.checkpoint.id`
  with the same path (verified on the file's first row), plus backbone
  `HuggingFaceTB/SmolVLM-256M-Instruct`, bf16, cuda.
- Observation (not a defect): the runtime manifest records temperatures
  [3.857, 2.100, 3.053] applied in this eval — the NCP pack's own fitted
  temperatures. Temperature scaling is argmax-invariant, so labels/accuracy
  are unaffected; it is recorded here only because it is part of the rows'
  provenance.

## 3. VERITE PROVENANCE CHAIN — VERDICT: RESOLVED, numbers recompute exactly
The three directories, established by content, checksums, and the run log:
- **`trained_verite_winner_v1/`** — the corrected winner re-run itself: a full
  1,001-row pass in a fresh directory. Recomputed accuracy from its rows:
  **0.35064935064935066** — matches the expected 0.350649 exactly. Its rows'
  `model_provenance.checkpoint.id` = `runs/full_soft_ce_735` (the MMFakeBench
  winner).
- **`trained_verite_val_v1/`** — byte-identical to the winner file (md5
  `92cafcad93ca460f6665a01e35ebbee1` for both): the corrected re-run installed
  under the canonical name. Per mainrun_log.md (~20:15 ET entry), the
  verdict/bundle/record cells read **`trained_verite_val_v1`** as "winner".
- **`verite_winner_smoke_v1/`** — the smoke check: **12 rows**, all usable
  (summary.json: attempted 12 / usable 12 / error 0). Per the log, 12/12 smoke
  predictions differed from baseline before the full pass was allowed.
- (Context: the original base-model eval is preserved separately at
  `pack_verite_val_v1/`, accuracy 0.3467.)

What mainrun_log.md records about the defect (~20:55 ET entry,
"VERITE TRANSFER DEFECT — FIXED + VERIFIED"):
- **Layer 1:** the transfer cell served the VERITE pack's BASE registry
  pointer instead of the winner, so the first "trained" file held base-model
  predictions — 0/1,001 rows differing from baseline, accuracy identical at
  0.346653.
- **Layer 2:** the first fix attempt passed the winner correctly, but the eval
  helper **reuses any populated output dir checkpoint-blindly**, so the winner
  was still never scored.
- **Fix protocol:** 12-row smoke into a scratch dir (12/12 differ) → full pass
  into a FRESH dir → row-by-row verification (543/1,001 predictions differ
  from baseline) → installed as `trained_verite_val_v1`.
- **Corrected H3 number (log):** winner transfer accuracy **0.3506**,
  macro-F1 0.2798 vs baseline 0.3467 / 0.2819 — transfer is flat; against the
  pre-registered 0.38–0.48 band, **H3 = NOT MET**. The audit's independent
  recomputation (0.350649) confirms the log's figure.

## 4. SPEND — VERDICT: within budget; live balance $5.39
- `python3 pod.py balance` has no such subcommand — it prints the usage text
  (the same failure seen earlier). The usage text documents `whoami` as the
  account + balance check; run read-only, it returned:
  **clientBalance = 5.3899372067** (≈ **$5.39**), currentSpendPerHr = 0.897,
  read ~20:28 ET. No balance figure here is guessed.
- Last balance/spend figures recorded in mainrun_log.md:
  - Run start balance **$9.77** (money-ledger entry).
  - Balance **$8.0060** (spend $1.77).
  - Balance **$7.4071 at ~18:26 ET** (spend $2.37 at the corrected $0.90/hr).
  - Balance **$6.3617 at ~19:47 ET** (spend $3.41) — the log's last recorded
    balance before this audit.
- Implied total spend at the live read: $9.77 − $5.39 ≈ **$4.38**, still well
  clear of the $8 hard stop, with PASS 2 the main remaining consumer.
