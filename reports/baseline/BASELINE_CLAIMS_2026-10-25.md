# What this baseline claims (and what it does not)

**Date:** 2026-10-25
**Purpose:** the one-page claim record. Every number here traces to a saved artifact; nothing is quoted from prose.
**Scope:** pretrained inference only. No training, fine-tuning, downloads, external messages, prompt selection, or threshold tuning. Every test-split number is post-hoc: the MMFakeBench official test split was inspected in earlier workspace work.

## 1. MMFakeBench — official test split

Population: 10,000 attempted rows; 9,999 usable (one image decode error, `test:3824`). Same checkpoint (`f2fe3c12…`), same paper-aligned v2 question bank, four-class target.

| Baseline | Rows | Accuracy | Macro-F1 | ECE | 95% range (accuracy) |
|---|---|---|---|---|---|
| Constant majority (`original`) | 9,999 | 0.3000 | 0.1154 | — | — |
| Source-metadata rule (fit on disjoint validation) | 9,999 | **0.9150** | **0.8510** | — | — |
| Source-metadata, in-sample ceiling | 9,999 | 0.9500 | — | — | — |
| **LAYA paired** (image + text) | 9,999 | **0.2642** | **0.2037** | 0.0815 | [0.2553, 0.2734] |
| **LAYA text-only** (same checkpoint) | 10,000 | **0.2793** | **0.2181** | 0.0123 | [0.2705, 0.2885] |

Paired − text-only, on the 9,999 rows usable in both: **−0.0151 accuracy, 95% range [−0.0244, −0.0054]**.

Image-only arm: 1,000-row seeded, non-stratified 10% sample (visual support 119), accuracy **0.2610**, macro-F1 0.1970, ECE 0.0575, 95% range [0.2358, 0.2847]. On that same 1,000 rows: paired 0.2630, text-only 0.2620, image-only 0.2610; all pairwise differences near zero with ranges spanning zero. Artifact: `controls_metrics_2026-10-25.json`.

## 2. VERITE — current repository CSV

Population: 1,001 rows; 338 true / 338 miscaptioned / 325 out-of-context; 663 distinct images. The paper and README describe 1,000 rows (338/338/324); the current CSV has 1,001. All rows are retained and the discrepancy is disclosed; no exclusion rule was invented.

| Arm | Rows | Accuracy | Macro-F1 | ECE | 95% range (accuracy) |
|---|---|---|---|---|---|
| Constant majority (`true`) | 1,001 | 0.3377 | — | — | — |
| **Paired** (image + text) | 1,001 | **0.3566** | **0.3458** | 0.0955 | [0.3317, 0.3816] |
| **Text-only** (same checkpoint) | 1,001 | **0.3586** | **0.3583** | 0.0404 | [0.3297, 0.3886] |

Paired − text-only: **−0.0020 accuracy, 95% range [−0.0360, 0.0310]**. Artifact: `controls_metrics_2026-10-25.json`.

## 3. NewsCLIPpings — streamed local evaluation

Population: all 7,024 validation annotations; images streamed from the VisualNews archive and not stored (5,943 images, 5,943 clusters). This replaces the earlier six-row publisher-rendition diagnostic, which is not a benchmark result.

| Metric | Value | 95% range |
|---|---|---|
| Accuracy | **0.5083** | [0.4978, 0.5181] |
| Balanced accuracy | 0.5083 | [0.5013, 0.5150] |
| Macro-F1 | 0.4185 | — |
| ECE / Brier | 0.1663 / 0.2817 (ECE 10-bin for this dataset) | — |
| AUC, out-of-context probe | 0.4677 | — |
| AUC, wrong-image probe | 0.4482 | — |

Per-strategy (1,756 rows each): accuracy 0.5028–0.5137. Pristine recall 0.1153; falsified recall 0.9012. Artifact: `ncp_metrics_2026-10-25.json`, computed by `data/workflows/analysis/ncp_metrics_20261025.py` with image-hash clusters.

## The six statements

1. **The image did not help on MMFakeBench.** On identical test rows, adding pixels lowered accuracy by 1.5 points and the grouped range excludes zero. On VERITE and on the 1,000-row image-only sample the differences are near zero. The −1.51 pp is pooled across source pairs, not conditioned on source pair; because the label is largely determined by source metadata, the within-pair image effect could differ. One checkpoint, one protocol: this is not evidence that pixels are useless in general.
2. **Text-only is far better calibrated.** ECE 0.0123 versus 0.0815 on MMFakeBench; 0.0404 versus 0.0955 on VERITE.
3. **MMFakeBench is largely solvable from source metadata.** A two-column lookup fitted on disjoint validation rows reaches 0.9150 accuracy and 0.8510 macro-F1 without seeing an image; 13 of 14 source pairs are label-pure. Aggregate accuracy without this shortcut baseline would be misleading.
4. **The model is near-blind to the visual-distortion class.** Paired test F1 0.048 with 2.6% recall (26 of 1,000); the image-only arm is no better (F1 0.031). Textual distortion is the only class predicted with any skill (F1 0.37).
5. **NewsCLIPpings shows no pairing skill.** Accuracy 50.8% with a range spanning chance, and both probe AUCs below 0.5. The falsified class is over-predicted (recall 0.90) while pristine recall is 0.12.
6. **The direct fake/true head is not useful here.** AUC 0.474, below chance. Artifact: `mmfakebench_test_paired/paired.metrics.json` → `binary_noul`.

## Reproducibility and gates

- Every accuracy above is recomputed from saved predictions without inference; `pipeline_status_20261025.py gates` checks coverage arithmetic, gold/manifest agreement, probability sums, and accuracy recomputation.
- Batch 1/4/8 and prefix-cache on produce identical labels on a 300-row test sample (max probability delta < 1e-4): `tier0_equivalence.json`.
- Clusters are exact image bytes; 2,000 resamples, seed 20261018. Ranges are descriptive diagnostics, not confirmatory intervals.
- MMFakeBench validation exposures remain disclosed: nine exposed validation rows share exact image bytes with test records through 14 hash edges; excluding those test rows changes accuracy by 0.08 pp (0.2642 → 0.2634).

## What is not claimed

- Not a misinformation detector. The task measures agreement with a dataset's labels.
- Not confirmation, paper parity, or a pristine held-out result. The test split was previously inspected.
- Not a trained model and not comparable to trained systems (CCN 84.7%, SNIFFER 88.4%, LAMAR 84.8%), which train on the benchmark or retrieve external evidence.
- Not calibration of factual truth. ECE describes label agreement only.
- Not a source-faithful replication of every official population: VERITE uses the current 1,001-row CSV; NewsCLIPpings is a streamed local evaluation whose VisualNews image terms remain unresolved; MMFakeBench's official-test result is post-hoc.
- Not evidence that the image is useless in general: one checkpoint, 201M parameters, one protocol.

## VERITE image-root provenance

Two VERITE paired runs exist on different image roots:

| Run | Image root | Accuracy | Status |
|---|---|---|---|
| `c4749c27…` (site, dashboard, closeout) | verified 664-file archive, `data/raw/VERITE/images/` | 0.3566 | current |
| `90742b57…` | older windmill root, 495 files | 0.3478 | historical, not used |

The root difference does not affect the text-only comparison. The `vision_text` branch's model state is `{context: text}` only; no image enters the model (`engine.py`, `model_state`). An empirical check re-ran the text-only arm against the canonical root: the first 202 completed rows returned identical `input_state_sha256`, labels and probabilities (maximum delta 0.0). Rows, text and gold align 1,001/1,001 between the arms, so paired minus text-only is computed on the same inputs. Only the paired arm consumes images, and it uses the verified recovered archive. See `VERITE_IMAGE_ROOT_DISCREPANCY_2026-10-25.md`.

**Tier-0 determinism.** Batch 1, 4 and 8 and prefix-cache on produce identical labels and probabilities on the same 300-row test sample (maximum probability delta 0.0). Artifact: `tier0_equivalence.json`.
