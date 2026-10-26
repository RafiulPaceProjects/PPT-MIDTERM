# POS gap check and plan — combined track (Laya)

**Date:** 2026-10-25
**Against:** `POS_final.pdf` (submitted 2026-09-28; Saravani, Etikela, Haider), Objective 5 (combined track) and Objective 6 (integrated deliverable)
**Prepared by:** orchestrator (opencode) with four read-only review workers (Claude haiku ×2, Codex gpt-6-luna low ×2)
**Scope note:** the POS covers three tracks and three students. This plan assesses only the combined/Laya track and the team-level deliverable it feeds.

## 1. Verdict

The POS promises a **fine-tuning study**: two fine-tuned Laya variants, six comparison conditions, three seeds, paired 95% CIs, and a captioning pipeline. What exists is a **verified zero-shot baseline** on two of three datasets. The repository's active policy explicitly excludes training and fine-tuning. Those two statements cannot both stand — the POS must be amended, or the scope must change. Everything else is downstream of that one decision.

One further finding changes how the baseline should be read: on the official MMFakeBench test split, a rule that reads only the `(text_source, image_source)` columns scores **9,500 / 10,000 = 95.0% in-sample** (a ceiling, since it is fitted on the same labels it scores), and **91.5% when fitted on validation rows that exclude the evaluated set**. Thirteen of the 14 source pairs are label-pure. LAYA's zero-shot accuracy is 26.4% on that split. Quote 91.5% as the transferable baseline; 95.0% is only an upper bound.

## 2. POS requirement → reality

| POS Objective 5 requirement | State | Evidence |
|---|---|---|
| Captioning pipeline that describes the image without the article caption | **Not built** | No captioning code or outputs in `data/workflows` or `data/processed`. LAYA emits typed decisions, not text; a separate captioner is required. |
| Fine-tune two Laya variants (Attention, Gate) for consistent vs out-of-context | **Not started, and out of policy** | No training artifacts. `data/workflows/baseline_study/AGENTS.md` and root `AGENTS.md`: training/fine-tuning is outside active scope. |
| Six comparison conditions | **Not defined or run** | Two routes exist (paired, vision_text) plus a text route on a different checkpoint. No condition table exists. |
| Text-only Laya baseline | **Partial** | `text` route uses `laya:421m-typed-decisions-mlx-fp16` (Ollama), a different checkpoint from LAYA-Vision. Usable as a baseline, not as a same-model ablation. |
| Direct image-text embedding classifier (CLIP) | **Not built** | No CLIP classifier artifacts. |
| NewsCLIPpings evaluation | **Blocked** | 6 usable / 7,024 attempted; 7,018 image-blocked. `news_access_closeout_2026-10-22/`. |
| VERITE evaluation | **Done (artifact)**, population caveat | 1,001/1,001 usable, accuracy 35.66%, macro-F1 0.3458. 1,000 vs 1,001 unresolved. |
| MMFakeBench evaluation | **In flight** | Official test, 10,000 rows, paired + vision_text, declared in `MMFAKEBENCH_TEST_ABLATION_2026-10-25.md`. |
| Accuracy and macro-F1 with paired 95% CIs across three seeds | **Not possible today** | Single checkpoint, single seed, no CIs. Grouped bootstrap is planned as a diagnostic, not the paired-over-seeds design the POS promises. |
| Stretch targets 84.8% NewsCLIPpings / 76.3% VERITE | **Not met, and not closable as written** | NewsCLIPpings untestable (images); VERITE zero-shot is 35.66% against 76.3%. Both targets are published SOTA (LAMAR), not baseline expectations. |
| Shared prediction-output schema across tracks | **Not established** | No schema file in the repo; team-level dependency. |
| Streamlit app (Objective 6) | **Not started** | No app artifacts. Team-level deliverable. |

## 3. What is actually done (artifact-backed)

- Four paired runs with manifests, run IDs, pinned checkpoint `f2fe3c12…` and question bank `0074694c…`; saved-score verifier passes on all four and rejects a wrong run ID.
- 54 baseline tests pass in both the working project and `main/`.
- Data-access investigation is documented to a standard most teams never reach: HEAD evidence, byte-range finding, zero body bytes, unsent drafts, no substitutions.
- Exposure and overlap disclosure (300 rows, 9 rows, 14 hash edges) with all rows preserved.
- Runtime/provenance capture: environment inventories, source hashes, recipes. Portability itself is unverified.

## 4. What is in flight

| Item | State | Owner |
|---|---|---|
| MMFakeBench test, paired | running, started 2026-10-25, 10,000 rows | me (orchestrator) |
| MMFakeBench test, vision_text (same checkpoint) | queued after paired | me |
| Grouped bootstrap + convergence of the two branches | not started, plan written | me |

A prior attempt exists at `data/processed/protocol/dataset_native_baseline_20261024_test_v1/`, stopped at 1,729/10,000 with no metrics. It is not a result and must stay labelled partial.

## 5. Corrections that cost no inference

1. **Add the source-pair baseline.** 91.5% on test when fitted on disjoint validation rows (95.0% is the in-sample ceiling; 95% on the 1,000-row validation split per the vault note). Report the held-out figure in every MMFakeBench table, with the ceiling labelled as such. Without it the MMFakeBench numbers invite a false reading.
2. **Report per-source-pair performance**, not only aggregate macro-F1. The aggregate is dominated by a class↔source confound.
3. **Rescore the test result with the 9 overlapping rows excluded** and report both.
4. **Add ECE/Brier** to the saved predictions. LAYA's card claims ECE 0.041 and warns to recalibrate off-domain; the study currently reports no calibration at all.
5. **Fix the dashboard drift**: `paired_official_test_macro_f1` is still null; the 10-22 dashboard is linked as current while a 10-24 one exists.
6. **Confirm the pre-declaration timestamp** against the run manifest before publishing the ablation as pre-declared.

## 6. The decision the POS forces

**Option A — amend the POS to a baseline-and-diagnostic study.** Defensible, cheap, honest. Deliver: verified zero-shot baseline across three datasets, modality ablation, source-shortcut diagnostic, calibration, explicit blockers. Drop: fine-tuning, six conditions, seeds, Streamlit for this track. Requires an instructor conversation, not just a note.

**Option B — execute Objective 5 as written.** Requires, in order: (1) a captioning checkpoint and cached outputs, (2) compute for fine-tuning two variants × three seeds, (3) NewsCLIPpings images or a documented population change, (4) a CLIP embedding classifier, (5) a condition table frozen before training. On CPU this is not feasible; the POS assumed free Colab GPU. Estimate: weeks, not days, and the 84.8%/76.3% targets remain unlikely for a 201M model.

**Option C — hybrid (recommended).** Keep the baseline as the pre-registered contribution, close every cheap gap in §5, and treat fine-tuning as a documented post-midterm decision with an explicit go/no-go gate. Present the source-shortcut finding as a contribution in its own right — it is the most interesting result the project currently has.

## 7. Plan

### Phase 0 — finish the running experiment (now, ~2h total)
- Paired test, 10,000 rows → `dataset_native_baseline_20261025_test_ablation_v1/mmfakebench_test_paired`.
- vision_text control, same rows.
- Score both from saved predictions; compute per-class P/R/F1, confusion matrices, majority reference, grouped bootstrap (2,000 × `group_id`, seed 20261018).
- Acceptance: `paired.metrics.json` and `vision_text.metrics.json` exist, attempted = 10,000, blocked = 1, and both branches share identical row IDs and gold labels.

### Phase 1 — corrections with no inference (~half day)
- Source-pair baseline on test (91.5% held-out; 95.0% ceiling) and on validation (95%); per-pair table.
- Rescore excluding the 9 overlapping rows.
- ECE/Brier from saved probabilities.
- Update dashboard JSON + the ablation report; state the 9,999 denominator.
- Acceptance: every MMFakeBench table carries majority, source-pair, paired, vision_text.

### Phase 2 — close the records gap (~half day)
- Vault: add 2026-10-22 … 10-25 logs; close the VERITE 724/277 note; correct the mesh's 1,000-vs-1,001 entry; mark the 18 Oct handoff historical.
- Repo: `CHECKLIST.md` line 41 ("Obtain VERITE image access") and the fine-tuning gates must say resolved or deferred, with dates.
- Acceptance: newest vault log ≥ newest repo artifact; no vault statement contradicts a closeout.

### Phase 3 — POS decision gate (needs you + instructor)
- Choose A, B, or C; write the deviation note either way.
- If C: define the fine-tuning go/no-go — compute available, captioner chosen, images resolved, condition table frozen.
- If B: freeze the condition table *before* any training; register the three seeds; pre-declare the pairing unit for CIs.
- Acceptance: one page, dated, signed off by the team, before any optimizer step.

### Phase 4 — POS deliverables that survive either option
- Shared prediction schema (label, score, route, dataset, run_id, row_id) — unblocks the Streamlit app and the team integration.
- Streamlit shell that reads saved predictions; no live model needed for the demo.
- Acceptance: the app returns a verdict and an explanation from saved artifacts; a teammate can run it.

## 8. Honest risk register

| Risk | Consequence | Mitigation |
|---|---|---|
| POS↔policy contradiction discovered at review | Credibility damage beyond the track | Decide §6 now; document the deviation |
| 95% source shortcut goes unreported | Any MMFakeBench claim is refuted in one question | Phase 1, first item |
| NewsCLIPpings images stay blocked | 84.8% target untestable; one third of POS unmet | State plainly; propose the pairing task on an image-available substitute only with approval |
| CPU-only compute | Fine-tuning impossible; 3 seeds impossible | Escalate for GPU or descope in writing |
| Vault drift | Supervisor reads a stale status | Phase 2 |
| Single checkpoint | "Image adds nothing" generalizes to one model only | Say so; do not overclaim |

## 9. What I would tell the committee, today

"We have a verified zero-shot baseline on two of three datasets, a modality ablation in progress, and a benchmark-validity finding: MMFakeBench's official test split is 91.5% predictable from its source metadata alone when the rule is fitted on disjoint validation rows (95.0% in-sample). Fine-tuning as scoped in the POS has not started and is not covered by the current working policy; that scope decision is the next gate, not a hidden gap."
