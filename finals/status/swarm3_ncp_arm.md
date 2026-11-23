# Swarm 3 — NewsCLIPpings (NCP) arm audit (READ-ONLY)
2026-11-22, independent recomputation from pod artifacts
(pod /workspace/Misinformation via podssh; VM trainer copy read locally).
Nothing was modified on the pod.

## 1. CARVE — CONFIRMED (one cosmetic manifest note)
Directory `data/processed/protocol/newsclippings_finetune_v1/`:
- train.jsonl = **4,002 rows** = 2,001 items × 2 question forms
- tune.jsonl = **500 rows** = 250 items × 2 forms
- calib.jsonl = **500 rows** = 250 items × 2 forms
- Total = **2,501 items / 5,002 records** — exactly the design spec.
- Image files on disk under `images/`: **2,120**; unique image references
  across all records: **2,120** — exact match.
- manifest.json `splits` section agrees with the actuals to the row
  (train 2001/4002, tune 250/500, calib 250/500); `stream_ledger` records
  2,120 referenced / 2,120 seen / 2,120 verified / **0 skipped**;
  source stated as "NewsCLIPpings merged_balanced TRAIN split only",
  seed 20261122.
- NOTE (cosmetic): the manifest's `carve_targets_items.train` field reads
  2000 while its own `splits` section and the files carry 2,001. The files
  match the design; the target label is off by one. No data impact.

## 2. METADATA BAN — CONFIRMED CLEAN
Key union across **all 5,002 NCP record rows** (train + tune + calib):
**{id, image, label, question, state_text}** — exactly the permitted set.
No `text_source`, no `image_source`, no other key anywhere. No violation.

## 3. RECEIPTS + WINNER — CONFIRMED
- `runs/ncp_full_soft_ce_245/result.json`: arm **full**, loss **soft_ce**,
  steps **245**, seed 20261122, base thaitea/laya-vision @ f2fe3c1,
  lr_encoder 1e-5 / lr_head 1e-3, n_train_records 4002,
  trainable_params 114,728,323, loss 1.2660 → 0.6862,
  **tune_macro_f1 0.493000939803136**, tune_accuracy 0.508,
  per-class recall pristine 0.336 / falsified 0.680, train 112.7 s.
- `runs/ncp_full_soft_ce_735/result.json`: same recipe, steps **735**,
  loss 1.2660 → 0.6725, **tune_macro_f1 0.48090948090948094**,
  tune_accuracy 0.516, recall pristine 0.256 / falsified 0.776,
  train 306.6 s (window starts the second the 245 run ends — sequential,
  both from base).
- `runs/ncp_winner.json` picks **245 steps at 0.493000939803136** — the
  exact argmax of the two receipts, matching at full float precision.

## 4. STEP SPEC — {245, 735} IS THE EXECUTED SPEC; NO 490 RUN IS MISSING
The audit premise ("registered design said {490, 735}") is **not supported
by any document in the run record**. The executed notebook's NCP training
cell (cell 28, `LAYA_MainRun_Executed.ipynb`) — identical in the
staged-for-review notebook — writes the rule explicitly:

    budgets = sorted({245, int(winner["steps"])})
    if len(budgets) == 1:
        budgets = [245, 490]

i.e. two budgets: a fixed 245 plus **the MMF winner's own step count**.
The MMF winner ran 735 steps, so the executed budgets are **[245, 735]** —
exactly the receipts on disk. The [245, 490] fallback would have fired
only if the MMF winner had itself been the 245-step config. The §7b/§7c
markdown and amendment (c) describe the arm only as "the winner's recipe
at two step budgets — deliberately lean, not a second grid" and never
name {490, 735}; a grep of the full run record finds every "490/735"
mention referring to the MMFakeBench grid {245, 490, 735} or the October
frozen protocol, never to the NCP arm. **Verdict: the executed spec is
confirmed as written; there is no missing or deviated 490-step NCP run —
the {490, 735} figure exists only in the audit premise.**

## 5. SELECTION FORM (swarm-1 finding F1) — CONFIRMED FIXED
Both NCP receipts state **`tune_metric_form: "native"`** and
**`n_tune_class4: 250`** — the selection metric was computed on the
250 native-form tune records only, not the pooled 500 (whose binary form
has flipped label indices). Mechanism, all on record: the trainer carries
a `TUNE_FORM` switch and `_record_form` honours explicit `:native` /
`:binary` id suffixes; the NCP cell sets `laya_trainer.CLASS4_CRITERIA = 2`
(NCP's native form is binary) for its calls and restores it in a finally
block; the §7c markdown states this adaptation openly, and the run log's
F1/F2 deviation entry records the fix ("MMF forms unchanged
(class4/binary); NCP forms separate (native/binary)").

## 6. TRAINER FIXES (finding F2) — CODE FIX CONFIRMED; ONE INERT DEVIATION
- Code: `_examples()` is **parameterized** —
  `def _examples(vlm_train, path, form=None, dataset="mmfakebench")` —
  and `train_full_finetune` / `train_lora_finetune` /
  `select_and_calibrate` each accept `dataset=` and thread it through to
  every `_examples` call. The VM copy
  (~/workspace/misinfo_run/laya_trainer.py) and the pod copy
  (data/workflows/laya_trainer.py) are **md5-identical**:
  1bb5ae5c5417cfc44ac4709ec9ecad0f. The hardcode is gone.
- DEVIATION (inert): the executed NCP cell 28 does **not** pass
  `dataset=` — its kwargs carry ckpt/revision/loss/steps/seed/files/out_dir
  only, so the NCP trainings ran under the trainer's default tag
  "mmfakebench". Impact assessment: in `laya.vlm_train.jsonl_example` the
  `dataset` argument is **only stored as a tag on the produced example**
  (`"dataset": dataset` in the example dict) and is never used in the
  conversion itself — question parsing, label bounds and form handling all
  come from the record. The receipts corroborate correct NCP conversion
  (4,002 NCP train records consumed; native-form tune metrics on the
  pristine/falsified labels). So no wrong-dataset conversion occurred; the
  imperfection is that NCP training examples carry a "mmfakebench" dataset
  tag in memory. A labelling blemish, not a data defect — but the paper /
  book should not claim the NCP arm "passed dataset='newsclippings'".

## Summary of verdicts
| # | Item | Verdict |
|---|---|---|
| 1 | Carve counts / images / manifest | CONFIRMED (manifest target label off by one; files exact) |
| 2 | Metadata ban | CONFIRMED — key union exactly the permitted set |
| 3 | Receipts + winner argmax | CONFIRMED — exact, full precision |
| 4 | Step spec | CONFIRMED as executed {245, 735} per the notebook's written rule {245, winner-steps}; the premise's {490, 735} appears nowhere in the record; no run missing |
| 5 | Native-form selection (F1) | CONFIRMED — receipts state tune_metric_form "native", n = 250 |
| 6 | Trainer F2 fix | Code fix CONFIRMED in both copies (md5-identical); DEVIATION (inert): NCP cell never passed dataset=, ran under the default tag, which jsonl_example stores but never uses in conversion |
