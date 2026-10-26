# Fine-Tuning Handoff (2026-10-25)

**Phase:** baseline only. No fine-tuned weights, checkpoints, or candidate predictions were found (section E). Training is not authorized: `data/processed/protocol/laya_paired_head_comparison_v1/frozen_protocol.json` has `"status": "comparison_frozen_training_not_started"` and `"optimizer_steps_authorized": false`.

**Counting method:** Paths are relative to the repository root. Question counts are `wc -l` on each JSONL. Row counts are distinct `id` prefixes (split on the last `:`), counted by a read-only `python3 -I` script on 2026-10-25. Nothing was run to write this document: no tests, no dry run, no inference, no downloads.

## What exists

### A. Prepared MMFakeBench development data (700 rows)

Source: `data/processed/protocol/mmfakebench_val_grouped_split_v1/rows.csv`, partition `development`, seed 20261018 (per each `metadata.json`).

| Directory | Files | Binary question | Questions per split (train/tune/calib) | Distinct rows per split | Wording version |
|---|---|---|---|---|---|
| `mmfakebench_finetune_dev_v1/` | train, tune, calib `.jsonl`; `manifest.csv`; `metadata.json`; `environment.md` | `noul` | 980 / 210 / 210 | 490 / 105 / 105 | v1 class4 instruction "...using both the image and supplied text?"; criteria are a list of strings |
| `mmfakebench_finetune_dev_v2/` | train, tune, calib `.jsonl`; `manifest.csv`; `metadata.json` | `noul` | 980 / 210 / 210 | 490 / 105 / 105 | v2 class4 instruction "...using both the image and the supplied text?"; criteria are a dict |
| `mmfakebench_finetune_dev_choice_v1/` | same as v1 minus `environment.md` | `choice` (A/B) | 980 / 210 / 210 | 490 / 105 / 105 | as v1 |
| `mmfakebench_finetune_dev_choice_v2/` | same as v2 | `choice` (A/B) | 980 / 210 / 210 | 490 / 105 / 105 | as v2 |

- `manifest.csv` has 700 data rows (701 lines with header). Columns: `row_id,row_index,split,group_id,fake_cls,gt_answers`.
- JSONL line schema: `id` (`val:<n>:class4` or `val:<n>:binary`), `image` (path relative to the output directory), `state_text`, `question` {`type`, `instructions`, `criteria`}, `label` (int). There is no `split` field; the split is the filename.
- Labels: class4 index order is original=0, textual_veracity_distortion=1, visual_veracity_distortion=2, mismatch=3. `noul`: label 1 = Fake, 0 = True. `choice`: `A` = Fake (label 0), `B` = True (label 1).
- Class4 label counts in the v2 train file are mixed with binary labels; use the native bundle below for class counts.

### B. Frozen native-only bundle (the adaptation input)

`data/processed/protocol/laya_paired_head_comparison_v1/`
- `train.jsonl` 490 lines, `tune.jsonl` 105, `calib.jsonl` 105. One question per row, IDs suffixed `:native`. Class counts from the labels (0..3): train 147/147/49/147; tune 32/32/10/31; calib 31/31/11/32.
- `questions.json`: revision `native_and_exploratory_v1`, sha256 `d62221dc…2322509c`, same as `data/workflows/baseline_study/questions.json`.
- `populations.json`: per-partition fingerprints for train, tune, calib, and confirmation (confirmation = 300 rows, 90/90/30/90).
- `frozen_protocol.json`: protocol binding `8274226419658bc27b8d6bbfdd4d80d91f14998d0f51960e32db5b8ab53f3696`.

Instruction text in this bundle: "Using only the supplied content, which dataset label best describes this item?…". This differs from the v2 wording above (see What is missing, item 9).

### C. Incumbent and baseline runs

- `data/processed/protocol/baseline_tune_105_default_v1/`: incumbent tune run; `summary.json` reports 105 attempted and 105 usable `paired` rows.
- `data/processed/protocol/laya_paired_head_eval_baseline_v1/`: fresh incumbent `paired` run on the 300 confirmation rows. `manifest.json` run_id `db964e6d…594a3`, `purpose: evaluation`, 300 attempted / 300 usable / 0 error. `comparison_binding.json` reports `exact_population_match`, `exact_questions_match`, and `exact_model_match` all true.

### D. Scripts and reports

- `data/workflows/prepare_laya_finetune_data.py`: builds the v1/v2 dev JSONL (`--binary-mode noul|choice`).
- `data/workflows/prepare_baseline_finetune_comparison.py`: builds the frozen native bundle; `prepare()` lines 96–167 define the training, selection, and evaluation design.
- `data/workflows/run_laya_head_adaptation_v1.py`: guarded runner. Its training path is gated behind an explicit execute flag; it was not invoked for this record.
- `data/workflows/tests/test_laya_head_adaptation_runner_v1.py`: 5 test methods (counted by `grep -c "def test"`).
- `data/reports/fine_tuning_readiness_v1.md`, `data/reports/fine_tuning_preflight_incidents.md`, `data/reports/pre_finetuning_paper/main.tex`.
- `data/reports/baseline_study/frozen_head_preflight_2026-10-21.md` with evidence `frozen_head_preflight_evidence_2026-10-21_final.json`.

### E. Adaptation outputs

None. `find data/processed -maxdepth 3 -iname '*adapt*' -o -iname 'checkpoint-step*'` returned nothing.

## What is specified

Source of values: `prepare()` in `data/workflows/prepare_baseline_finetune_comparison.py` (lines 96–167), recorded in `frozen_protocol.json`.

- **Model:** LAYA-Vision, `thaitea/laya-vision` at revision `f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc`. Backbone `HuggingFaceTB/SmolVLM-256M-Instruct`. Local CPU, fp32.
- **Objective:** native four-way only, one question per training row. Installed `vlm_loss` with sigma 0.3, group_size 4, w_sph 0.75, w_ce 1.0, `train_act: false`.
- **Trainable scope:** `freeze: head`. The encoder, including the vision tower, is frozen. Preflight measured 8,462,659 trainable parameters across 35 tensors, with zero `encoder.*` tensors trainable.
- **Optimizer:** AdamW, lr_head 1e-4, weight_decay 0.01, grad clip 1.0, cosine decay to 10%, warmup 0, batch 2.
- **Seed and length:** seed 20261019; 735 steps; max 3 passes (draw budget with replacement); 60-minute runtime cap.
- **Checkpoints:** saved at steps 245, 490, 735. Candidates are `incumbent`, `step245`, `step490`, `step735`.
- **Stopping rule:** the run stops at 735 steps or the 60-minute cap. On budget or failure, artifacts are preserved and the run is marked incomplete (`write_incomplete_manifest` in the runner). Nothing is silently shrunk.
- **Selection (tune only, 105 rows):** exclude any candidate whose per-class recall drops more than 0.05 below the incumbent. Highest native macro-F1 wins; ties go to the incumbent, then the earlier step. A winner must beat the incumbent by at least +0.03 absolute macro-F1, or the incumbent is kept.
- **Metrics:** primary is four-way macro-F1 over native labels. Binary NOUL is a separate diagnostic. Incumbent tune paired macro-F1 is 0.2591490601408522.
- **Calibration:** temperatures inherited from the checkpoint; no fit on train or tune. The 105 calib rows are reserved for a later, separately frozen step after selection.
- **Evaluation:** one selected checkpoint on the 300 confirmation rows (previously exposed; descriptive only). Gate: Δmacro-F1 ≥ 0.03 AND paired bootstrap 95% lower bound > 0 (10,000 replicates, seed 20261019, unit `group_id`) AND each class recall drop ≤ 0.05 AND no added failures or abstentions.
- **Test:** no test predictions or scoring are authorized. `future_test_policy.known_overlap_test_ids` lists 76 IDs (counted); `known_corrupt_test_ids` = `test:3824`.
- **Known limitations** (`known_limitations`): exposed 300-row population; single seed; CPU feasibility not established; two tune rows overlap test image bytes; native-only adaptation may change other typed heads through shared parameters.
- **Readiness status:** `fine_tuning_readiness_v1.md` lines 13–15 say technical training feasibility has not been demonstrated. Lines 46–56 list the unchecked setup gates.

## What is missing

1. **Adapted weights.** No checkpoint directory exists (section E).
2. **Gradient path.** The 2026-10-21 preflight did a two-row forward and objective check only. It did not run a backward pass, an optimizer step, the 735-step budget, or the 60-minute cap (`frozen_head_preflight_2026-10-21.md`).
3. **Trainer configuration.** There is no Hugging Face `Trainer` or `TrainingArguments`, no PEFT, and no `datasets` or `accelerate` config. Grep for `push_to_hub|TrainingArguments|Trainer(|peft|LoraConfig` over `data/workflows` and `data/notebooks` returned nothing. The only trainer is LAYA's `train(...)` call in `run_laya_head_adaptation_v1.py`, with settings read from the frozen protocol plus literals (`lr_backbone=2e-5`, `n_last=4`, `num_workers=0`, `warmup=0`) in `run_training`.
4. **Requirements.** `data/workflows/requirements-laya.txt` contains only `huggingface_hub`. There is no fine-tune requirements file. The readiness report says PEFT, `datasets`, and `accelerate` are absent (`fine_tuning_readiness_v1.md` line 15).
5. **Tokenizer and processor.** The processor is read from the checkpoint's `processor/` subdirectory. The preflight tokenized 700/700 rows with zero truncations, but only for the untrained checkpoint.
6. **Checkpoint export.** The runner writes `checkpoint-step-<N>/` with `agent.save(..., include_backbone=True)`. The save/reload was verified only for the untrained model (about 805 MB `model.safetensors`). No trained-checkpoint reload test and no Hugging Face-format export or Hub upload script exist.
7. **Resume.** The runner refuses a nonempty output directory. The protocol's `training_design.resume` text requires sampler-state restore for exact continuation, and no such code exists.
8. **Evaluation binding.** No config or run scores an adapted checkpoint on the 300 confirmation rows. The runner records `confirmation_evaluation_performed: false`.
9. **Wording mismatch.** The v1/v2 dev JSONL four-way instruction differs from the frozen native instruction in `questions.json`. The criteria keys and descriptions match. The runner reads only the frozen bundle, so the v1/v2 files are not its input. `fine_tuning_readiness_v1.md` line 58 says "baseline wording"; the instruction text does not match `questions.json`.
10. **Choice polarity.** The `choice` descriptions name Fake and True. Semantic neutrality is not assured (`fine_tuning_readiness_v1.md` line 30; `fine_tuning_preflight_incidents.md`, incident 2).
11. **Hashes in metadata.** `metadata.json` in the v1/v2 directories stores no hashes. `prepare_laya_finetune_data.py` lines 150–151 carry TODOs for this. Hashes live in `data/reports/preparation_schema_audit.md`.
12. **GPU.** No GPU requirement is specified. The protocol and environment are CPU fp32 on Apple M4, 16 GB, MPS unavailable at runtime (`mmfakebench_finetune_dev_v1/environment.md`). `fine_tuning_readiness_v1.md` says GPU is optional and unverified.
13. **Weight license.** Unchecked gate in `fine_tuning_readiness_v1.md` line 48.
14. **Input key mismatch.** The bundle uses `state_text`, which `prepare_laya_finetune_data.py` lines 55–56 note the installed loader maps to `context`. The historical baseline used `note`. `data/reports/pre_finetuning_paper/README.md` records the two as not equivalent. The harness's `model_state` uses `context` (`engine.py` lines 37–47).
15. **Two macro-F1 implementations.** Tune selection uses `class_metrics` in the runner; the harness uses `metrics._native`. Nothing in the record ties them together.

## Interface contract

- **Branches** (`baseline_tune_105_default_v1/manifest.json`): `text`, `vision_text`, `image`, `paired`, `final`, `fusion`. `final` needs `text` and `image` estimates. `fusion` needs `text` and `paired`. The frozen primary route is `paired` (`frozen_protocol.json` `primary_route`).
- **Vision backend:** `data/workflows/baseline_study/backends.py` (`VisionClient`) launches `vision_worker.py` with `study.json` `vision.python` (`/Users/rafiulhaider/Documents/windmill/.venv-vision/bin/python`). The worker calls `laya.load_vlm(checkpoint, device, dtype, max_len=1024, head_max_len=256)`. The checkpoint must be a directory that `laya.load_vlm` accepts: `backbone/config.json`, `model.safetensors`, `processor/`, `vlm_agent_config.json`.
- **Config binding:** `study.json` `vision.checkpoint` names the checkpoint. `engine.py` line 179 hashes its `.json`, `.safetensors`, and `.model` files. A candidate is set with `run_baseline_study.py --set` (line 25, `KEY=JSON`).
- **Prediction record** (one JSON object per line, e.g. `paired.predictions.jsonl`): `id`, `dataset`, `split`, `partition`, `gold`, `group_id`, `run_id`, `branch`, `status`, `predicted_label`, `probabilities` (dict over the four native labels), `fake_probability`, `raw_answers`, `raw_logits`, `option_order`, `model_provenance`, `auxiliary`, `backend_usage`, `truncation`, `abstained`, `seconds`, `input_state_sha256`. Written by `decode_answers` (`engine.py` lines 86–99).
- **Validity:** `validate_prediction` (`engine.py` lines 50–84) requires `status` in {`ok`, `error`, `blocked`}. An `ok` record needs `predicted_label` and `probabilities` keyed by the four labels, summing to 1 within 0.00021, with the predicted label at the maximum within 0.00011. `fake_probability` must be None or finite in [0, 1]. `metrics.score_records` also rejects duplicate IDs and invalid gold.
- **Recomputation:** `run_baseline_study.py score --run <dir> --branch paired` calls `score_records(predictions, LABELS['mmfakebench'], NEGATIVE['mmfakebench'], threshold)` (`run_baseline_study.py` line 85). `NEGATIVE['mmfakebench'] = ['original']` (`config.py` line 11). `verify_baseline_closeout.py` lines 70–78 require recomputed values to equal the stored `paired.metrics.json`.
- **Metrics file** (`paired.metrics.json`) keys: `attempted`, `usable`, `error`, `blocked`, `abstention`, `native`, `binary_noul`, `selection_eligible`, `labels`, `binary_negative_labels`, `by_partition`, `pooled_diagnostic`, `purpose`.
- **Output directory:** `run` requires a new directory (`run_baseline_study.py` line 39; `engine.py` line 159 refuses existing output unless `--resume`).

## Status of this record

Nothing training-related was executed. This file is a record of what exists in the repository as of 2026-10-25, not a run plan.
