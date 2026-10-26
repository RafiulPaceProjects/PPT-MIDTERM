# NewsCLIPpings transfer probe v1: pilot report

**Date:** 2026-10-25

**Status:** Pilot (development). Validation was used to choose the regularization, so validation numbers are selection-biased. No NewsCLIPpings test or VERITE row was read.

## Run

| Item | Value |
|---|---|
| Rows featurized / wanted | 12,024 / 12,024 |
| Images missing | 0 |
| Decode failures | 0 |
| Readers reporting | 12 of 12 |
| Device | mps |
| Wall time | 58.1 min |
| Model rows per second (inference time) | 4.8 |

## Integrity gate

Validation rows checked: 7,024; unmatched: 0; maximum absolute difference 0.0001 against a tolerance of 0.001; passed.

## Results (NewsCLIPpings validation, n = 7,024, clusters = 5,942)

| Model | Train acc | Val acc | 95% range | Probe − zero-shot (pp) | 95% range (pp) | AUC | ECE | Recall pristine | Recall falsified |
|---|---|---|---|---|---|---|---|---|---|
| LAYA zero-shot | — | 50.8% | [49.7, 51.8] | — | — | 0.538 | 0.166 | 11.5% | 90.1% |
| λ = 1e-4 | 64.0% | 53.3% | [52.2, 54.5] | +2.49 | [1.06, 4.01] | 0.556 | 0.105 | 53.7% | 53.0% |
| λ = 1e-3 | 63.2% | 54.1% | [52.9, 55.2] | +3.23 | [1.80, 4.80] | 0.566 | 0.071 | 54.3% | 53.8% |
| λ = 1e-2 | 60.2% | 55.0% | [53.9, 56.2] | +4.21 | [2.77, 5.74] | 0.577 | 0.031 | 55.2% | 54.8% |
| λ = 0.1 | 57.4% | 55.2% | [54.1, 56.4] | +4.38 | [2.97, 5.88] | 0.579 | 0.008 | 54.8% | 55.6% |
| λ = 1 (selected) | 54.8% | 55.6% | [54.4, 56.7] | +4.76 | [3.45, 6.17] | 0.575 | 0.019 | 53.3% | 57.9% |

Per-strategy validation accuracy for the selected λ = 1 (strategies 0–3): 52.9%, 56.6%, 58.0%, 54.8%.

## Reading

1. The probe adds signal zero-shot does not use: every lambda's difference range lies above zero; selected lambda gives +4.76 pp [3.45, 6.17].
2. It is still near chance: best validation accuracy 55.6% and AUC 0.575 (at the selected λ), from 5,000 training rows on a frozen 201M checkpoint's 576-d feature.
3. Zero-shot calls most pairs falsified (recall falsified 90.1%, recall pristine 11.5%); the probe is balanced and better calibrated (ECE 0.019 at the selected lambda vs 0.166 zero-shot).
4. Train accuracy falls from 64.0% at the weakest regularization (λ = 1e-4) to 54.8% at the strongest (λ = 1) while validation rises (53.3% to 55.6%): overfitting with 5,000 rows. The selected lambda is the largest in the fixed grid (edge of grid); the grid stays as declared.
5. Not comparable to published results (e.g., fine-tuned CLIP 60.2%, CCN 84.7%, SNIFFER 88.4% on the test split): those train end-to-end and/or retrieve web evidence; this is validation, selection-biased.

## Full run (needs a separate go)

Featurize all 71,072 train rows and the 7,264 test rows by streaming, plus the 663 local VERITE true/out-of-context rows; fit the probe on all train rows; choose lambda on validation; score NewsCLIPpings test and VERITE once, beside LAYA zero-shot on the same rows.

Time estimate: (71,072 + 7,264) / (12,024 / 3,485.2 s) = 78,336 rows at about 3.45 rows/s ≈ **6.3 hours** (estimate from pilot throughput; uses pilot wall time, excludes the 663 VERITE rows).

## Files

- Protocol: `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md`
- Extraction: `data/workflows/transfer_probe/extract_laya_features_stream.py`
- Probe: `data/workflows/transfer_probe/train_probe.py`
- Pilot features and run record: `data/processed/protocol/ncp_transfer_probe_v1/pilot/`
- Probe results: `data/processed/protocol/ncp_transfer_probe_v1/pilot_probe.json`
- `data/processed/protocol/ncp_transfer_probe_v1/pilot_attempt1_aborted/` (CPU attempt, not a result)
