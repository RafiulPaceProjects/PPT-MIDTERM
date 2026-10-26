# NewsCLIPpings transfer probe v1: full-run report

**Date:** 2026-10-25 (run finished 23:53)
**Protocol:** `NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md`, with Amendment 1 (Apple GPU) and Amendment 2 (wider λ grid, full-run populations). Both were recorded before any test row was read.
**Data:** `data/processed/protocol/ncp_transfer_probe_v1/full_probe.json`, `full/run.json`, `verite/run.json`

## What was done

The published papers train on NewsCLIPpings and then test on the target. This run follows the same protocol with one frozen checkpoint. LAYA-Vision `f2fe3c12…` read every image and caption once, and a hook recorded the 576-d state its decision head uses. A logistic-regression probe was trained on those features for all 71,072 NewsCLIPpings train rows. The regularization was chosen on the 7,024 validation rows. The selected probe was then scored once on the 7,264-row NewsCLIPpings test split and once on the 663 VERITE true and out-of-context rows. LAYA's weights never changed. Images were streamed from the VisualNews archive and not stored.

The NewsCLIPpings test split had not been read in this workspace before this scoring, so its result is held out. The MMFakeBench test numbers elsewhere in the study are post-hoc.

## Run and gates

| Item | Value |
|---|---|
| NewsCLIPpings rows featurized (train + test) | 78,336 / 78,336 |
| Images missing / decode failures | 0 / 0 |
| Readers reporting / reconnects / range-boundary cuts | 12 of 12 / 0 / 11 |
| Device / wall time | mps / 4.58 h |
| VERITE rows featurized | 663 / 663 |
| Rows used: train / val / test / VERITE | 71,072 / 7,024 / 7,264 / 663 |
| Integrity gate (validation vs saved baseline) | 7,024 rows, max difference 0.0001 (tolerance 0.001), passed |
| Reproducibility (pilot train rows re-featurized) | 5,000 / 5,000 rows, max feature difference 0.00e+00, passed |

## Regularization (selected on validation)

| λ | Train acc. | Val acc. | 95% range | Val − zero-shot (pp) | 95% range (pp) |
|---|---|---|---|---|---|
| 0.0001 | 58.1% | 56.5% | [55.42, 57.60] | +5.68 | [4.29, 7.17] |
| 0.001 (selected) | 57.8% | 56.6% | [55.55, 57.74] | +5.81 | [4.42, 7.22] |
| 0.01 | 57.3% | 56.5% | [55.39, 57.65] | +5.67 | [4.26, 7.16] |
| 0.1 | 56.4% | 55.9% | [54.70, 56.97] | +5.04 | [3.59, 6.51] |
| 1 | 55.1% | 55.6% | [54.50, 56.74] | +4.81 | [3.50, 6.22] |
| 10 | 53.7% | 54.2% | [53.06, 55.35] | +3.39 | [2.16, 4.77] |
| 100 | 53.5% | 53.8% | [52.64, 55.01] | +3.02 | [1.73, 4.40] |

LAYA zero-shot validation accuracy: 50.8%.

## Targets (scored once with the selected λ)

### NewsCLIPpings test (held-out) (n = 7,264, clusters = 6,146)

| Arm | Accuracy | 95% range | Balanced acc. | Macro-F1 | AUC | ECE (15 bins) | Recall pristine | Recall falsified |
|---|---|---|---|---|---|---|---|---|
| LAYA zero-shot (own choice) | 51.1% | [50.10, 52.14] | 51.1% | 42.1% | 0.528 | 16.4% | 11.6% | 90.6% |
| Frozen-feature probe | 57.4% | [56.26, 58.44] | 57.4% | 57.4% | 0.598 | 1.1% | 57.0% | 57.8% |

Probe − zero-shot on the same rows: **+6.24 pp**, 95% range [4.76, 7.70] pp.

| Group | n | Probe accuracy | Zero-shot accuracy |
|---|---|---|---|
| 0 | 1,816 | 53.5% | 50.5% |
| 1 | 1,816 | 60.0% | 51.7% |
| 2 | 1,816 | 58.9% | 51.3% |
| 3 | 1,816 | 57.1% | 51.0% |

### VERITE true vs out-of-context (binary) (n = 663, clusters = 663)

| Arm | Accuracy | 95% range | Balanced acc. | Macro-F1 | AUC | ECE (15 bins) | Recall pristine | Recall falsified |
|---|---|---|---|---|---|---|---|---|
| LAYA zero-shot (own choice) | 50.5% | [46.76, 54.45] | 51.2% | 44.3% | 0.544 | 16.0% | 16.9% | 85.5% |
| Frozen-feature probe | 54.9% | [51.13, 58.52] | 54.6% | 53.6% | 0.569 | 6.1% | 70.1% | 39.1% |

Probe − zero-shot on the same rows: **+4.37 pp**, 95% range [−1.36, 9.95] pp.

| Group | n | Probe accuracy | Zero-shot accuracy |
|---|---|---|---|
| out-of-context | 325 | 39.1% | 85.5% |
| true | 338 | 70.1% | 16.9% |


## Reading

On the held-out NewsCLIPpings test, the probe scores 57.4% against 51.1% for LAYA zero-shot on the same 7,264 rows. That is +6.24 pp, 95% range [4.76, 7.70]. All four generation strategies gain, from 53.5% to 60.0% against 50.5% to 51.7% zero-shot. The probe is also balanced (recall 57.0% pristine, 57.8% falsified) and well calibrated (ECE 1.1% against 16.4%). Zero-shot calls 90.6% of falsified pairs falsified and only 11.6% of pristine pairs pristine.

So LAYA's frozen representation carries some image-caption pairing signal that its zero-shot answer does not use. The signal is weak: AUC is 0.598 and accuracy stays under 60%.

Validation picked λ = 0.001, inside the widened grid. With 71,072 training rows, train and validation accuracy are close (57.8% and 56.6%), so the pilot's overfitting at 5,000 rows is gone. Validation accuracy (56.6%) and test accuracy (57.4%) agree, which is what a held-out split should show.

Transfer to VERITE is weaker. The probe reaches 54.9% on the 663 true and out-of-context rows, 95% range [51.13, 58.52], above a coin flip. Its gain over zero-shot is +4.37 pp with a range of [−1.36, 9.95] pp, which spans zero. On VERITE this result cannot separate the probe from zero-shot. The two arms also fail in opposite directions. The probe favors "true" (recall 70.1% true, 39.1% out-of-context), while zero-shot favors "out-of-context" (16.9% and 85.5%).

## Against published results

These are reference points, not a ranking. Published figures come from `dashboard/published_supplement.json` and the study ledger, checked against the papers.

| System | NewsCLIPpings test | VERITE true vs OOC | Training and evidence |
|---|---|---|---|
| LAYA zero-shot (this study) | 51.1% | 50.5% | none |
| LAYA frozen features + linear probe (this study) | 57.4% | 54.9% | linear probe on 71,072 rows, LAYA frozen |
| CLIP ViT-B/32 (original NewsCLIPpings paper) | 60.2% | not reported | fine-tuned |
| LAMAR [E2E, Gate] | 84.7% | 76.3% | trained end to end on NewsCLIPpings |
| CCN | 84.7% | not reported | trained, plus web-retrieved evidence |
| SNIFFER | 88.4% | not reported | instruction-tuned, plus web-retrieved evidence |

The probe trails a fine-tuned CLIP by about 3 points and the trained systems by about 27 to 31 points on the same test split. Those systems update their whole model, and CCN and SNIFFER also look up evidence on the web for each item. On VERITE true vs OOC, LAMAR's 76.3% is about 21 points above the probe.

## Limits

- One checkpoint (201M parameters), one question, one linear probe. A trained head or full fine-tuning could behave differently. The fine-tuning pre-registration draft covers that.
- Validation was used to select λ, so the validation numbers are selection-biased. The test and VERITE numbers are not, because each was scored once with the selected λ.
- VERITE uses the current 1,001-row CSV, of which 663 rows are true or out-of-context. The documented release has 1,000 rows. Miscaptioned rows are excluded because NewsCLIPpings has no miscaptioned training signal.
- VisualNews image reuse terms remain unresolved. Images were streamed and discarded, and only features and predictions were kept locally.
- Ranges are 95% cluster-bootstrap ranges over exact image bytes (2,000 resamples, seed 20261018). They are descriptive, not formal tests.

## Reproduce (saved features, no inference)

```bash
B=data/processed/protocol/ncp_transfer_probe_v1
/Users/rafiulhaider/Documents/windmill/.venv-vision/bin/python -I data/workflows/transfer_probe/score_probe_full.py \
  --train-run $B/full --val-run $B/pilot --test-run $B/full --verite-run $B/verite --pilot-run $B/pilot \
  --reference data/processed/ncp_stream_v1/predictions.jsonl --output $B/full_probe.json
python3 -I data/workflows/transfer_probe/write_report_tables.py --probe $B/full_probe.json \
  --run $B/full/run.json --verite-run $B/verite/run.json
```
