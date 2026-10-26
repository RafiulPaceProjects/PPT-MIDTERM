# POS deviation addendum (DRAFT for instructor review, not submitted)

**Date:** 2026-10-25
**Supplements:** `POS_DEVIATION_2026-10-25.md` (not edited; its §2 table and §6 decision request remain open)
**Author:** Rafiul Haider (combined track). Unsigned. Drafted with model assistance.

## 1. Purpose

This addendum records findings and one scope change made after the deviation note, and does not replace it.

## 2. Stretch-target task mismatch

The POS targets (84.8% NewsCLIPpings, 76.3% VERITE) come from LAMAR (arXiv:2504.06010v3, Table 3). Per `dashboard/published_supplement.json`, both are binary "True vs OOC" accuracies after training end-to-end on NewsCLIPpings train: 84.8 (LAMAR E2E Attention, NewsCLIPpings test) and 76.3 (LAMAR E2E Gate, VERITE True vs OOC).

This study's VERITE result is three-class (true / miscaptioned / out-of-context). Per `dashboard/results.json`, `verite_paired`: accuracy 0.35664335664335667, shown as 35.7% on 1,001 rows. The deviation note gives 35.66%, the same value at two decimals.

The 76.3% target therefore compares a binary task with a three-class result. LAMAR's three-class VERITE figure is 54.9% (Table 4; `published_supplement.json`, entry "verite", trained on Molmo-D3 with NewsCLIPpings for OOC). The NewsCLIPpings comparison is the same binary task type, but the published 84.8% is trained end-to-end, while this study's `ncp` accuracy 0.5082574031890661 (50.8%) is zero-shot.

Proposed options (see §6):
- (a) Restate the VERITE target as the three-class figure, 54.9%, with the regime difference noted.
- (b) Report the binary True-vs-OOC task separately, with 76.3% as its non-comparable reference.

Until one is chosen, the targets stand as written, reported as not met.

## 3. Web-retrieved evidence in two published results

Per `published_supplement.json`, two higher reference points use evidence retrieved from the web at inference:
- CCN, 84.7% (NewsCLIPpings): "evidence retrieved from the web."
- SNIFFER, 88.4% (NewsCLIPpings): "web-retrieved evidence," on top of instruction tuning.

Both are marked non-comparable. The transfer probe takes only image and caption as input.

## 4. Scope change executed on 2026-10-25

With user approval, a frozen-feature linear probe was run under `NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md`. The LAYA-Vision checkpoint is not updated. A logistic probe is fit on its 576-d pooled decision feature, following the published train-on-NewsCLIPpings, test-on-target pattern. It is not a fine-tuned LAYA and not a reproduction of a published system.

Pilot results (development; `PILOT_REPORT_ncp_transfer_probe_v1_2026-10-25.md`):
- Integrity gate passed: validation zero-shot probabilities reproduced within 0.0001 (tolerance 0.001); 12,024 of 12,024 rows featurized.
- Zero-shot validation accuracy: 50.8% [49.7, 51.8].
- Validation accuracy at the selected λ = 1: 55.6% [54.4, 56.7].
- Difference: +4.76 pp, 95% range [3.45, 6.17].

λ was chosen on validation, so these figures are selection-biased. The pilot reports AUC 0.575 and calls the result near chance.

Two amendments were made before any test or VERITE row was read: Amendment 1 moved extraction to MPS; Amendment 2 widened the λ grid to add 10 and 100, because the pilot selected the edge value 1.

Full run: in progress (user-reported; no full-run artifact was read for this draft). Its results on NewsCLIPpings test and VERITE True-vs-OOC, scored once beside zero-shot on the same rows, will be added here.

## 5. Not done relative to the POS

Per `POS_GAP_PLAN_2026-10-25.md` and the deviation note:
- **Captioning pipeline:** not built. LAYA emits typed decisions, not text.
- **Fine-tuning two variants (Attention, Gate):** not started. Training is outside the baseline-only policy; the approved exception covers frozen-feature probes only.
- **Six comparison conditions:** the deviation note records four of six; the gap plan records no condition table. These must be reconciled before submission.
- **Three seeds:** not run (deviation note: "not applicable"; gap plan: "not possible today").
- **CLIP embedding classifier:** not built; needs a model download that is not authorized.

Record correction: `POS_GAP_PLAN_2026-10-25.md` §2 lists NewsCLIPpings as "Blocked," which predates the streamed run (7,024 usable, accuracy 50.8% in `results.json`). This addendum uses the streamed-run status.

## 6. Decisions needed from the instructor

1. VERITE target: option (a), three-class 54.9%; option (b), binary True-vs-OOC against 76.3%; or both.
2. Six conditions: which count stands (four of six, or none defined).
3. Deviation note §6: Options A, B or C remain unanswered. The probe is not the fine-tuning gate and does not decide it.
4. Whether the probe is reported as a separate scoped exception or inside the baseline study.
5. Whether the full-run result goes into this submission or follows it.
