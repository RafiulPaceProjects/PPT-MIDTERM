# MMFakeBench official test: modality ablation (pre-declared)

**Declared:** 2026-10-25, before any test-split inference in this protocol.
**Scope:** pretrained inference only. No training, fine-tuning, downloads, external messages, prompt selection, or threshold tuning.

## Why

The existing baseline has no clean paired evaluation on the official test split and no
matched control isolating the image. Every current number is a validation subset
(tune 105, exposed 300), a legacy text-only test artifact without a pinned revision, or
the six-row NewsCLIPpings diagnostic. Without a same-checkpoint text-only route on the
same rows, the study cannot say whether the image contributes anything measurable.

## Population

- MMFakeBench official `test` split, `--partition all`, all 10,000 rows.
- Sampling overrides: `sampling.per_class=null`, `sampling.limit=null` (the study default
  of three rows per class must not apply).
- Preflight (2026-10-25, read-only): 10,000 rows, 10,000 image paths present, 9,999
  decodable, 1 decode failure (`test:3824`), 9,944 distinct groups.
- `test:3824` stays in the attempt as a blocked row. Attempted denominator is 10,000;
  usable population is reported as 9,999 and coverage is explicit. No image is replaced.

## Design

One checkpoint, two input routes on identical rows and identical question bank:

| Branch | Sees | Role |
|---|---|---|
| `paired` | image pixels + supplied text | primary baseline |
| `vision_text` | supplied text only, same checkpoint | image-contribution control |

An `image`-only branch may be added later as a further diagnostic. The `text` branch uses
a different checkpoint (`laya:421m-typed-decisions-mlx-fp16`) and is therefore not a
modality control for this comparison.

Identity: checkpoint `f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc`; question bank
`dataset_native_paper_aligned_v2_20261021`, SHA-256
`0074694cf4f77784cb0f77d9868b4b9acf75e33f350154a43dcf7eef670f9de9`; CPU, fp32,
batch 4, no permutations, no optimizer steps.

## Metrics and analysis

- Primary: four-class macro-F1. Secondary: accuracy, per-class precision/recall/F1,
  confusion matrices, constant-majority reference on the same usable rows.
- Coverage accounting: attempted / usable / blocked / error / abstention.
- Uncertainty: grouped percentile bootstrap (2,000 resamples over `group_id`, seed
  20261018) reported as a **diagnostic range**, not a confirmatory interval. Groups exist
  because image paths repeat (10,000 rows, 9,944 groups) and rows are not independent.
- Paired comparison: `paired` versus `vision_text` on the rows usable in both, reported
  as a descriptive difference with the same grouped bootstrap. No significance test is
  claimed.

## Claim boundary

The official test split was inspected in earlier workspace work. This run is therefore a
**post-hoc diagnostic**, not blind confirmation, not a pristine held-out result, and not
paper parity. No test-set number from this run may be used to select prompts, thresholds,
checkpoints, or wording. Tune-set results remain the only selection surface.

## Commands

```bash
# preflight (read-only, completed 2026-10-25)
data/.venv-eda/bin/python data/workflows/run_baseline_study.py \
  --config data/workflows/baseline_study/study.json \
  --set 'questions_file="data/processed/protocol/dataset_native_baseline_20261021_v2/questions.json"' \
  --set 'sampling.per_class=null' --set 'sampling.limit=null' \
  validate --dataset mmfakebench --split test --partition all --decode-images

# paired baseline
data/.venv-eda/bin/python data/workflows/run_baseline_study.py \
  --config data/workflows/baseline_study/study.json \
  --set 'questions_file="data/processed/protocol/dataset_native_baseline_20261021_v2/questions.json"' \
  --set 'sampling.per_class=null' --set 'sampling.limit=null' \
  run --dataset mmfakebench --split test --partition all --branch paired \
  --purpose evaluation \
  --output data/processed/protocol/dataset_native_baseline_20261025_test_ablation_v1/mmfakebench_test_paired

# same rows, text-only through the same checkpoint
... --branch vision_text --purpose evaluation \
  --output data/processed/protocol/dataset_native_baseline_20261025_test_ablation_v1/mmfakebench_test_vision_text
```

Scores are recomputed from saved predictions; no inference is repeated for scoring.

## Comparability note (added after review)

`paired` reports 9,999 usable rows and `vision_text` reports 10,000. The difference is
`test:3824`, whose image cannot be decoded: the paired route opens it and records an error,
while the text-only route never opens an image and therefore scores the row normally. All
paired-versus-text comparisons above are computed on the **9,999 rows usable in both
arms**, so the delta is like-for-like.

Calibration: ECE uses 15 equal-width confidence bins for both arms. The reported
`bins_used` differs (9 versus 5) only because the text-only arm concentrates its confidence
into fewer bins; the bin grid is identical, so the ECE values are comparable.
