# Pretrained multimodal misinformation baselines: a verified midterm report

**Author:** Rafiul Haider · Analytics Capstone, Pace University
**Date:** 2026-10-25
**Status:** complete local zero-shot baseline across three datasets; post-hoc diagnostics, not confirmation
**Companion files:** `BASELINE_CLAIMS_2026-10-25.md` (numbers), `POS_DEVIATION_2026-10-25.md` (deviations), `BASELINE_CHECKLIST_2026-10-25.md` (status board)

## 1. Question

How does an existing pretrained vision-language checkpoint perform on dataset-native misinformation tasks before any task-specific training? The study measures agreement with benchmark labels under a frozen protocol, including the controls needed to say whether the image contributes anything measurable. No training, fine-tuning, prompt selection, threshold tuning, or external evidence retrieval is involved.

## 2. Data and protocol

| Dataset | Task | Population used | Attempted / usable | Native metric |
|---|---|---|---|---|
| MMFakeBench | 4-class (original, textual, visual, mismatch) | official test split | 10,000 / 9,999 | macro-F1 |
| VERITE | 3-class (true, miscaptioned, out-of-context) | current repository CSV | 1,001 / 1,001 | macro-F1 |
| NewsCLIPpings | 2-class (pristine, falsified) | all validation annotations | 7,024 / 7,024 | accuracy |

**Checkpoint and questions.** LAYA-Vision at revision `f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc`, CPU, fp32, batch 4, no permutations, no optimizer steps. Question bank `dataset_native_paper_aligned_v2_20261021`, SHA-256 `0074694c…`. The legacy text-only run uses a different checkpoint (`laya:421m-typed-decisions-mlx-fp16`) and is reported only as a historical diagnostic.

**Arms.** MMFakeBench: paired (image + text), text-only (same checkpoint, same rows), image-only (1,000-row deterministic sample). VERITE: paired and text-only. NewsCLIPpings: paired only; a text-only arm is degenerate for an image-caption pairing task.

**Scores and uncertainty.** Every accuracy is recomputed from saved predictions without inference. Confidence ranges are percentile bootstraps over 2,000 resamples clustered by exact image bytes (seed 20261018). They are descriptive diagnostics, not confirmatory intervals: rows are not independent, and the MMFakeBench test split was inspected in earlier work.

**Coverage.** MMFakeBench attempted 10,000 and lost exactly one image decode (`test:3824`), which stays in the attempted denominator. NewsCLIPpings images were streamed from the VisualNews archive and never stored (5,943 images); this replaces the earlier six-row publisher-rendition diagnostic. VERITE covers all 1,001 CSV rows.

## 3. Results

### 3.1 MMFakeBench official test (post-hoc)

| Baseline | Accuracy | Macro-F1 | ECE | 95% range |
|---|---|---|---|---|
| Constant majority (`original`) | 0.3000 | 0.1154 | — | — |
| Source-metadata rule (fit on disjoint validation) | **0.9150** | **0.8510** | — | — |
| Source-metadata in-sample ceiling | 0.9500 | — | — | — |
| **Paired (image + text)** | **0.2642** | **0.2037** | 0.0815 | [0.2553, 0.2734] |
| **Text-only (same checkpoint)** | **0.2793** | **0.2181** | 0.0123 | [0.2705, 0.2885] |
| Image-only (1,000-row sample) | 0.2610 | 0.1970 | 0.0575 | [0.2358, 0.2847] |

Paired − text-only on the 9,999 shared rows: **−0.0151 accuracy, 95% range [−0.0244, −0.0054]**. Adding the image made the model slightly worse, and the range excludes zero. This is a pooled effect: it is not conditioned on source pair, and the metadata confound means the within-pair effect could differ. The image-only sample is an unstratified 10% draw (visual support 119), so its class supports differ from the full split; arms are compared only on the shared 1,000 rows. On that sample the three arms are not distinguishable at this sample size under a descriptive range (paired 0.2630, text-only 0.2620, image-only 0.2610; all pairwise ranges span zero), so the full-population comparison is the informative one.

Class-level performance is lopsided. The paired arm reaches macro-F1 0.2037 with textual distortion F1 0.3676 (recall 0.5238) but visual distortion F1 0.0475 (recall 0.026, 26/1,000). The image-only arm is no better on visual distortion (F1 0.031). The direct fake/true head scores AUC 0.4739, below chance.

### 3.2 VERITE (current CSV)

| Arm | Accuracy | Macro-F1 | ECE | 95% range |
|---|---|---|---|---|
| Constant majority (`true`) | 0.3377 | — | — | — |
| **Paired** | **0.3566** | **0.3458** | 0.0955 | [0.3317, 0.3816] |
| **Text-only** | **0.3586** | **0.3583** | 0.0404 | [0.3297, 0.3886] |

Paired − text-only: −0.0020 accuracy, 95% range [−0.0360, 0.0310]. The image adds nothing measurable here either, and text-only is again much better calibrated (ECE 0.0404 versus 0.0955). The paper and README describe 1,000 rows (338/338/324); the current CSV has 1,001 (338/338/325). All rows are kept and the discrepancy is disclosed rather than resolved by guessing an exclusion.

### 3.3 NewsCLIPpings (streamed local evaluation)

| Metric | Value | 95% range |
|---|---|---|
| Accuracy | **0.5083** | [0.4978, 0.5181] |
| Balanced accuracy | 0.5083 | [0.5013, 0.5150] |
| Macro-F1 | 0.4185 | — |
| ECE (10-bin) | 0.1663 | — |
| AUC, out-of-context probe | 0.4677 | — |
| AUC, wrong-image probe | 0.4482 | — |

Accuracy is at chance and both probe AUCs are below 0.5. The falsified class is over-predicted: falsified recall 0.9012 against pristine recall 0.1153. Per-strategy accuracy (1,756 rows each, `source_dataset` 0–3) stays between 0.5028 and 0.5137, so the result is not carried by one subset. This is a local evaluation: the VisualNews image-use terms remain unresolved, and no image corpus is stored.

### 3.4 The validity finding

MMFakeBench labels are almost fully determined by source metadata. A two-column lookup on `(text_source, image_source)` fitted on disjoint validation rows reaches **0.9150 accuracy and 0.8510 macro-F1** on the test split without seeing a single image; 13 of 14 source pairs are label-pure, and the in-sample ceiling is 0.9500. Any aggregate MMFakeBench accuracy below that is partly a statement about which outlets the rows come from, not only about visual reasoning. Reported results must therefore carry the shortcut baseline and per-source-pair reporting; a headline number alone would be misleading. This also explains why NewsCLIPpings, where that shortcut is not available by construction, cannot be read the same way.

## 4. Threats to validity

- **Post-hoc test inspection.** The MMFakeBench official test split was examined in earlier workspace work. Every test number is a descriptive diagnostic, not blind confirmation, and none was used for prompt, threshold, or checkpoint selection.
- **Prior exposure.** The 300-row validation evaluation population was used earlier. Nine of those rows share exact image bytes with test records through 14 hash edges; that does not by itself prove score inflation, but it rules out describing the test population as untouched. Excluding those test rows moves accuracy by 0.08 pp (0.2642 → 0.2634).
- **Grouped but not IID data.** Images repeat within and across splits (9,944 preflight groups and 9,717 distinct image hashes on the MMFakeBench test; 5,943 NewsCLIPpings images; 663 VERITE images). Ranges resample clusters, and no row-level IID interval or significance test is claimed.
- **Terms and provenance.** NewsCLIPpings images were streamed under unresolved reuse terms and are not redistributed. VERITE paired evidence uses the verified archive root `data/raw/VERITE/images`; the older windmill-root paired run (0.3478) is historical and is not used. The text-only arm reads no images, so the root difference does not affect the comparison. VERITE uses a CSV whose row count differs from the documented population. No author contact or image acquisition was performed for this report.
- **One checkpoint, one protocol.** A 201M-parameter model at fp32 on CPU, one question version. Nothing here generalises to other models, prompts, or datasets.

## 5. What the results mean

The honest summary is a **negative result with a usable method**: the pipeline is operational, coverage and scoring are auditable, and the measurement says that this checkpoint barely uses the image on these tasks, that text alone is better calibrated, and that MMFakeBench aggregate accuracy is substantially a metadata shortcut. That is a defensible starting point for any later study, and it is more informative than a weak headline accuracy presented alone.

## 6. Reproduction

All work is CPU-only and local. Representative commands (the `--set` flags must precede the subcommand):

```bash
data/.venv-eda/bin/python data/workflows/run_baseline_study.py \
  --config data/workflows/baseline_study/study.json \
  --set 'questions_file="data/processed/protocol/dataset_native_baseline_20261021_v2/questions.json"' \
  --set 'sampling.per_class=null' --set 'sampling.limit=null' \
  run --dataset mmfakebench --split test --partition all --branch paired \
  --purpose evaluation --output <new-directory>
```

Scoring and checks without inference:

```bash
data/.venv-eda/bin/python data/workflows/run_baseline_study.py score --run <run-directory>
data/.venv-eda/bin/python data/workflows/analysis/controls_metrics_20261025.py
data/.venv-eda/bin/python data/workflows/analysis/pipeline_status_20261025.py gates
```

Determinism: batch 1, 4, 8 and prefix-cache on produce identical labels on a 300-row test sample (maximum probability delta < 1e-4), recorded in `tier0_equivalence.json`.

## 7. Claim boundary

This is not a misinformation detector, not a trained system, not paper parity, and not calibrated factual truth. It is a complete, gated, zero-shot baseline on the available artifacts, with the image's contribution and the metadata confound measured rather than assumed. Fine-tuning remains a separate GPU phase and is out of scope here.
