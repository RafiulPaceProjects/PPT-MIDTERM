# Swarm Audit — LAYA Trainer ↔ Notebook Contract

**Date:** 2026-11-22 · **Scope:** READ-ONLY audit, pre-grid
**Files:** `~/workspace/misinfo_run/laya_trainer.py` (607 lines) vs `~/workspace/misinfo_run/LAYA_Colab_Staged_For_Review.ipynb` (57 cells)
**Headline:** **No mismatch blocks the MMFakeBench grid.** Every function the notebook calls from `laya_trainer` exists with a matching signature, and every receipt field the selection / comparison / verdict / bundle / record cells read is a field the trainer writes. The substantive findings sit in the **NCP arm** (post-grid, §7c) and in two bootstrap/operational risks. Details below, in the required format: CELL → EXPECTS → TRAINER PROVIDES → SEVERITY.

---

## 1. Function-signature audit (notebook → trainer)

| Notebook call site | Call | Trainer signature | Verdict |
|---|---|---|---|
| Cell 19 (grid, full) | `train_full_finetune(ckpt_id, revision, loss, max_steps, lr_encoder, lr_head, seed, train_file, tune_file, out_dir)` — all kwargs | `train_full_finetune(ckpt_id, revision=None, loss="rlcd", max_steps=245, lr_encoder=1e-5, lr_head=1e-3, seed=0, train_file=None, tune_file=None, out_dir=None, batch_size=8)` | ✅ MATCH |
| Cell 19 (grid, lora) | `train_lora_finetune(ckpt_id, revision, loss, max_steps, lora_r, lora_alpha, lora_dropout, lora_targets, lr_lora, lr_head, seed, train_file, tune_file, out_dir)` — all kwargs | `train_lora_finetune(ckpt_id, revision=None, loss="rlcd", max_steps=245, lora_r=16, lora_alpha=32, lora_dropout=0.05, lora_targets=None, lr_lora=1e-3, lr_head=1e-3, seed=0, train_file=None, tune_file=None, out_dir=None, batch_size=8)` | ✅ MATCH |
| Cell 28 (NCP, both arms) | same kwarg sets as cell 19 (via `**kwargs` + arm-specific LRs) | as above | ✅ MATCH |
| Cell 43 (calibration) | `select_and_calibrate(WINNER_DIR, CALIB_FILE)` positional | `select_and_calibrate(winner_dir, calib_file, out_dir=None)` | ✅ MATCH |
| Cell 38 (bootstrap) | `from laya_trainer import macro_f1, per_class_recall`; called `(y_true, y_pred, 4)` | both defined, both in `__all__`, signature `(y_true, y_pred, n_classes)` | ✅ MATCH |
| Cell 43 (H5) | `laya_trainer._laya_modules()` → `(torch, laya, vlm_train)` | exists, returns exactly that 3-tuple | ✅ MATCH (private API, but present) |
| Cell 43 (H5) | `laya_trainer._examples(vlm_train_, TUNE_FILE)` | `_examples(vlm_train, path, form=None)` | ✅ MATCH (private API, but present) |
| Cell 28 | monkeypatch `laya_trainer.CLASS4_CRITERIA = 2` in try/finally | `_record_form` reads the module global at call time → the patch takes effect | ✅ WORKS (see Finding F1 for what it then does) |
| — | `laya_trainer.collect_logits` | **does not exist** in the trainer | ⚠️ NO CALLER: no notebook cell calls it. Cell 43 correctly calls `vlm_train.collect_logits` (the library function, obtained via `_laya_modules()`, whose existence the trainer itself guards). Not a mismatch — recorded so nobody "fixes" it later. |
| Cells 19/28 | `batch_size` never passed | trainer default `DEFAULT_BATCH_SIZE = 8` | ✅ consistent with CONFIG `BATCH_SIZE = 8`, but implicit (F10) |

Trainer-internal dependencies the notebook implicitly relies on, all guarded by `_laya_modules()` at call time: `vlm_train.train / jsonl_example / collect_logits / fit_temperatures_from / metrics_from`, `laya.load_vlm`. Fail-loud if the dev install is wrong. ✅

---

## 2. result.json receipt contract — field by field

**Trainer WRITES** (both arms, via `_finish` → `result.json` in each run dir):
`arm, loss, steps, seed, base, revision, n_train_records, trainable_params, loss_first, loss_last, losses[] (full per-step list), tune_macro_f1, tune_accuracy, tune_per_class_recall {class-name: recall}, n_tune_class4, out_dir`
Full arm adds: `lr_encoder, lr_head`. LoRA arm adds: `lora_r, lora_alpha, lora_dropout, lora_targets, lr_lora, lr_head`.

| Consumer cell | Fields READ | Trainer provides? |
|---|---|---|
| 19 (grid return + resume path) | `tune_macro_f1`, `trainable_params` | ✅ both |
| 21 (selection) | `arm`, `loss`, `steps`, `tune_macro_f1` | ✅ all |
| 28 (NCP) | `tune_macro_f1`, `tune_accuracy` (+ `.get("tune_accuracy")`) | ✅ both |
| 30 (factor isolation) | `arm`, `loss`, `steps`, `tune_macro_f1`, `tune_accuracy`, `tune_per_class_recall` (by class name), `trainable_params` | ✅ all |
| 31 (difference views) | same set as 30 | ✅ all |
| 33 (method verdict) | `tune_macro_f1`, `tune_per_class_recall`, `trainable_params` | ✅ all |
| 45 (verdict) | `.get()` on `arm, loss, steps, tune_macro_f1, tune_accuracy, tune_per_class_recall, trainable_params, loss_first, loss_last` | ✅ all |
| 47 (plot a) | `arm`, `loss`, `steps`, `tune_macro_f1` | ✅ all |
| 48 (plot b) | `tune_per_class_recall` (name-normalized) | ✅ |
| 55 (complete record) | `arm`, `loss`, `steps`, `tune_macro_f1`, `tune_accuracy`, `tune_per_class_recall` (+ embeds whole receipts) | ✅ all |

**Key-name dependency — VERIFIED on real data:** cells 30/31/33/45 look up `tune_per_class_recall` by class name (`original`, `textual_veracity_distortion`, `visual_veracity_distortion`, `mismatch`). The trainer keys that dict from the laya example's criteria (`tune_examples[0]["q"]["crit"]`). The actual protocol file (rehearsal-slice copy of `mmfakebench_finetune_dev_choice_v2/tune.jsonl`, read directly) has **210 records = 105 class4 (criteria keys = the 4 class names) + 105 binary (criteria `A`/`B`)**. The trainer's form filter (`len(criteria) == 4`) isolates exactly the 105 class4 records → recall keys are the class names the cells expect. ✅ (The rehearsal exercised this same path end-to-end.)

---

## 3. winner.json / ncp_winner.json contracts

**Cell 21 WRITES** `runs/winner.json` = `{arm, loss, steps, tune_macro_f1, out_dir: "runs/<arm>_<loss>_<steps>" (relative), lora_available: true (hardcoded — no consumer reads it; informational only)}`.
**Cell 28 WRITES** `runs/ncp_winner.json` = `{arm, loss, steps, tune_macro_f1, tune_accuracy, out_dir: "runs/ncp_<arm>_<loss>_<steps>"}`.

| Consumer | Expects | Provided? |
|---|---|---|
| Cell 24 `pack_checkpoint()` | `winner.json["out_dir"]`, `ncp_winner.json["out_dir"]`; calibrated variant at `str(dir) + "_calibrated"` | ✅ both; the `_calibrated` suffix matches the trainer's `select_and_calibrate` default out-dir naming exactly |
| Cell 37 (test) | kernel var `winner`; `pack_checkpoint("mmfakebench")` **uncalibrated** | ✅ (test precedes calibration in cell order regardless) |
| Cell 41 (PASS 2) | `pack_checkpoint("newsclippings")` → `ncp_winner.json["out_dir"]`; `run_stream_pass` adapter handles the §5 function's 3-arg `(pack, checkpoint, out_rel)` signature (verified: cell 15 defines it with 3 params; cell 17's direct 3-arg call is consistent) | ✅ |
| Cell 45 | `winner.json["out_dir"]` → that dir's `result.json` | ✅ |
| Cell 48 | `winner.json["out_dir"]` | ✅ |
| Cell 51 (publish) | `winner[arm/loss/steps/tune_macro_f1]`; calibrated dir fallback `runs/<arm>_<loss>_<steps>_calibrated` | ✅ matches trainer default naming |
| Cell 53 (bundle) | `winner.json` `arm/loss/steps/tune_macro_f1` (method line composed from the receipt — arm-neutral fallback present) | ✅ |
| Cell 55 | `winner.get(arm/loss/steps)` → `runs/<…>_calibrated/calibration.json` | ✅ path matches |

**Calibration chain — fully consistent end to end:** trainer default out-dir (`<winner_dir>_calibrated`) = cell 24's calibrated resolution = cell 51's fallback = cell 55's `calibration_json` path = cell 49's glob (`runs/*_calibrated/calibration.json`, reading `ece_before` / `ece_after` / `temperatures` — all written by the trainer). `select_and_calibrate` never mutates the winner dir. ✅

---

## 4. Test-once guard + bootstrap pairing (cells 37–38)

**Guard — CONFIRMED.** Cell 37 checks `runs/.test_scored` first: if the marker exists it prints a refusal and makes **no** eval call. The marker (containing the winner dict + output path) is written only after `run_eval_cli` returns. Residual windows, both benign: (a) a crash mid-scoring leaves no marker, and `run_eval_cli`'s own logic then reuses completed artifacts or `--resume`s partial ones — the re-run cannot double-count because cell 38 reads the single predictions file; (b) the guard is a plain file check (deletable by hand) — a protocol guard, not a lock, as designed.

**Bootstrap pairing file — VERIFIED on disk** (`~/workspace/misinfo_run/mainrun_stage/ablation_test_paired.predictions.jsonl`):
- **10,000 rows; 9,999 with `status == "ok"`** (1 error row) — the "9,999 usable" figure is the ok-subset, and cell 38's `ok_pairs` filters on `status == "ok"` on both sides, so the effective pairing pool is correct.
- Schema is exactly what cell 38 consumes: `id`, `status`, `gold`, `predicted_label` all present on every row.
- IDs are `test:0` … `test:9999`, all unique — the baseline CLI's own id scheme; the winner's test predictions come from the same CLI (`run_eval_cli`, cell 13) over the same split, so ids join by construction. Cell 38 joins ablation ↔ winner predictions by id (it never joins to the raw annotation file; gold is carried inside both prediction files).
- Gold distribution in the file: original 3000 / textual 3000 / mismatch 3000 / visual 1000 — matches the known MMFakeBench test composition, corroborating that the ids enumerate the full test split in annotation order.

---

## 5. Calibration contract (cell 43 vs `select_and_calibrate`)

Trainer WRITES summary (returned dict + `<out>/calibration.json`): `winner_dir, out_dir, temperatures, n_calib, ece_before, ece_after, acc_calib, nll_before, nll_after`.
Cell 43 READS: `out_dir, temperatures, ece_before, ece_after, n_calib` — ✅ **all provided, exact names**. Cell 43 then writes `runs/h5_tune_calibration.json` with `tune_ece_before/after, tune_acc_before/after` — cell 45's H5 reads exactly those names. ✅

---

## Findings (every mismatch / risk, in CELL → EXPECTS → PROVIDES → SEVERITY form)

### F1 — NCP tune metric pools both question forms, with flipped label indices
- **CELL 28 →** sets `CLASS4_CRITERIA = 2` expecting the trainer's "class4" filter to isolate NCP's native binary form for the tune metric.
- **TRAINER PROVIDES →** `_record_form` classifies *any* 2-criteria choice record as "class4". Cell 26 writes **two** 2-criteria forms per item into the NCP tune file: `:native` (label 0 = pristine) and `:binary` (criteria `{A: "Yes, falsified", B: "No, pristine"}`, label 0 = **falsified**). Both pass the filter → `_tune_metrics` pools ~500 records (250 items × 2 forms) in which index 0 means *pristine* in one form and *falsified* in the other. Pooled `tune_macro_f1` / `tune_accuracy` mix two label spaces; `tune_per_class_recall` is keyed from the first example's criteria names and mislabels the other form's classes; `n_tune_class4` reports ~500, not 250.
- **SEVERITY: MEDIUM-HIGH** — NCP arm only (post-grid; the MMF grid is unaffected — its 4-criteria filter verifiably excludes the A/B form). The 2-budget NCP selection compares both candidates under the *same* pooled metric, so the ranking is internally consistent; but the NCP receipts' headline numbers are not the clean native-form binary metrics the design describes, and any per-class reading of an NCP receipt is wrong. Fix direction (not applied — read-only audit): filter NCP tune metrics to the `:native` form only, or give the trainer a form/id-suffix filter.

### F2 — Trainer hardcodes `dataset="mmfakebench"` for NCP records
- **CELL 28 →** trains on the NewsCLIPpings protocol expecting NCP examples.
- **TRAINER PROVIDES →** `_examples()` calls `vlm_train.jsonl_example(rec, root, dataset="mmfakebench")` unconditionally; there is no dataset parameter to pass. NCP records are converted under the mmfakebench dataset tag inside the library.
- **SEVERITY: MEDIUM** — effect depends on `jsonl_example` internals (unverifiable from this VM); at minimum the tag is wrong for the NCP arm, and if the tag conditions prompt/example construction, the NCP arm trains on subtly wrong examples. MMF grid unaffected.

### F3 — Ablation predictions: on-pod placement is an unclosed operational dependency
- **CELL 38 →** asserts `ABLATION_TEST_PREDS` resolved (cell 9) from CONFIG candidates `data/reports/ablation_test_paired.predictions.jsonl` or `/root/drivers/ablation_test_paired.predictions.jsonl`.
- **PROVIDES →** the verified file currently sits in VM staging at `mainrun_stage/ablation_test_paired.predictions.jsonl` — **neither candidate path**. Cell 9 reports "NOT FOUND" non-fatally; cell 38 then fails closed at its assert.
- **SEVERITY: MEDIUM (operational)** — not a code mismatch; the run must land the file at a candidate path on the pod before cell 38. Verify on-pod before the test stage, not during it.

### F4 — Bootstrap pairing never cross-checks gold agreement
- **CELL 38 →** `ok_pairs` pairs ablation ↔ winner items by id and `bootstrap_delta` takes ground truth from the winner item only (`yt` from `w["gold"]`); the baseline item's `gold` is never compared.
- **PROVIDES →** both files carry `gold` per row (verified in the ablation file), so the check is possible but absent. If row enumeration ever diverged between the two CLI runs, pairing would silently mix rows and the delta would be garbage with no signal.
- **SEVERITY: MEDIUM-LOW** — mitigated by identical CLI + identical overrides (`sampling.per_class=null`, `sampling.limit=null`, partition `all`) on both runs; a one-line gold-agreement assert in `ok_pairs` would close it.

### F5 — Receipt glob fragility if calibration ever writes a result.json copy
- **CELLS 21/30/31/33/47/55 →** glob `runs/*/result.json`, filter only the `ncp_` prefix; cells 21/33 assert exactly 12.
- **TRAINER PROVIDES →** `select_and_calibrate` saves the calibrated checkpoint into `runs/<winner>_calibrated/` via `VLMAgent.save` and writes `calibration.json` itself. Nothing in the trainer writes a `result.json` there — but if `VLMAgent.save` (library code, unverifiable from this VM) copies the source dir wholesale, a `result.json` would appear in the calibrated dir *after* cell 43. Cells 47/55 run after 43: cell 55 would then fold the calibrated copy into `receipts` under the winner's own name key (identical values — cosmetic), and any *re-run* of cells 21/33 after calibration would fail their ==12 asserts.
- **SEVERITY: LOW** — single forward pass unaffected; re-run hazard only, contingent on unverified library behavior.

### F6 — H5 measurement population differs from the protocol's tune population
- **CELL 43 →** measures H5 via `_examples(vlm_train_, TUNE_FILE)` with **no form filter** → 210 records (both question forms).
- **TRAINER PROVIDES →** the selection metric path (`_tune_metrics`) is class4-only (105). The H5 file therefore reports `n_tune = 210` against a differently-defined population than every other tune number in the run.
- **SEVERITY: LOW** — cell 45's H5 verdict reads only the ECE/accuracy fields, so the verdict is unaffected; it's a definitional inconsistency the paper should footnote (or the cell should pass `form="class4"`).

### F7–F10 — Informational
- **F7:** Cell 28's `CLASS4_CRITERIA` monkeypatch is sound (try/finally restores it; the trainer reads the global at call time). No action.
- **F8:** The trainer writes the full per-step `losses` list into every receipt; cell 55 embeds all receipts into `final_results_bundle.json`. Harmless size cost.
- **F9:** `winner.json`'s `lora_available: true` is hardcoded by cell 21 and read by nobody. Harmless.
- **F10:** `batch_size` is never passed by the notebook; the trainer's default (8) happens to equal CONFIG's `BATCH_SIZE`. Consistent today, silently divergent if CONFIG is ever edited.

---

## Bottom line for the grid start
The grid → selection → test-once → calibration → verdict → bundle → complete-record chain is **contract-exact**: signatures match, receipt fields match field-by-field, the winner/calibrated path naming is consistent across five independent cells, the test-once marker refuses re-scoring, and the bootstrap's baseline file is verified (10,000 rows / 9,999 ok / correct schema / joinable ids). **F1 and F2 should be fixed before the NCP arm (§7c) trains, and F3 verified on the pod before cell 38 — none of the three gates the grid.**
