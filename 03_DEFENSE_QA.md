# Defense Q&A: midterm pretrained baseline

Study sheet for explaining the midterm pretrained-baseline work in person. Evidence paths are relative to /Users/rafiulhaider/Documents/Misinformation unless they are absolute. Numbers are copied from the files listed under each answer.

## Research question and scope

**What exactly is a "pretrained baseline," and why does it come before fine-tuning?**

It is the LAYA-Vision checkpoint answering each benchmark's own question with no training, prompt tuning or threshold tuning, and its weights are never updated. Any fine-tuned result needs a reference point, and this baseline is that reference: it shows what the frozen checkpoint does before any task training.

Evidence: `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (sections 1 and 4); `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (Model and features)

**What research question does the midterm answer, and what does it leave open?**

The POS asks how well a fine-tuned model detects out-of-context image-text pairs, compared with a text-only version of the same model and a direct image-text embedding classifier. The midterm does not answer that yet. It builds the reference point by measuring the frozen checkpoint's zero-shot answers and how much pairing signal its frozen features carry, and fine-tuning is the next stage.

Evidence: `/Users/rafiulhaider/Downloads/POS_final.pdf` (Objective 5); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 1)

**Is this a misinformation detector?**

No. The task measures agreement with each dataset's labels, and the records say the results are not evidence of detecting deception. ECE describes agreement with labels only, not calibration of factual truth.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (What is not claimed); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 2, ontology rules)

**What is not done yet?**

The captioning pipeline, the fine-tuned Attention and Gate variants, three training seeds, the CLIP embedding classifier and the Objective 6 verdict application are not built. Conditions 1 to 3 of the six comparison conditions are marked done, and the two dashboards present results without being the Objective 6 application.

Evidence: `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (sections 3 and 5)

## Data and populations

**Why is VERITE 1,001 rows when the paper says 1,000, and what did you do about it?**

The current repository CSV has 1,001 rows (338 true, 338 miscaptioned, 325 out-of-context, 663 distinct images), while the paper and README describe 1,000 rows (338, 338, 324). All 1,001 rows were kept, the discrepancy is disclosed, and no exclusion rule was invented.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (section 2); `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Limits)

**How were the NewsCLIPpings images obtained, and what about their terms of use?**

The images were streamed from the VisualNews archive with HTTP range reads, decoded in memory, featurized or scored, and discarded. Only features, zero-shot probabilities, image SHA-256 hashes and row metadata are kept locally. The VisualNews reuse terms remain unresolved and are disclosed, and nothing is redistributed.

Evidence: `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (Data); `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (section 3); `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Limits)

**Do the datasets overlap, and does any overlap affect the reported numbers?**

Yes, in two places. The MMFakeBench test split contains 1,500 mismatch rows whose source is NewsCLIPpings, and nine exposed MMFakeBench validation rows share exact image bytes with test records through 14 hash edges. The probe was never scored on MMFakeBench, and excluding the overlapping test rows moves paired MMFakeBench accuracy from 0.2642 to 0.2634 (0.08 pp).

Evidence: `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 5, cross-dataset overlap); `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (Reproducibility and gates)

**What populations feed the transfer probe?**

Training uses all 71,072 merged_balanced training rows, and selection uses the 7,024 validation rows. The held-out target is the 7,264-row NewsCLIPpings test split, and the VERITE target is 663 rows (338 true and 325 out-of-context). The 338 miscaptioned rows are excluded because NewsCLIPpings has no miscaptioned training signal.

Evidence: `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (Data; Amendment 2); `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Run and gates)

## Method and controls

**Why are the confidence ranges clustered by image bytes?**

Some images appear in more than one row (for example, 9,999 MMFakeBench rows fall into 9,716 clusters), so treating rows as independent would count the same image as several pieces of evidence. The ranges resample whole clusters of exact image bytes, using 2,000 resamples and seed 20261018. They are descriptive ranges, not confirmatory tests.

Evidence: `data/reports/baseline_study/MMFAKEBENCH_SOURCE_PAIR_EFFECT_2026-10-25.md` (Method); `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (Reproducibility and gates); `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (Probe)

**Why is there no text-only arm on NewsCLIPpings?**

Each NewsCLIPpings caption appears twice, once with its own image (pristine) and once with a swapped image (falsified). A text-only model sees the same caption in both rows, so it cannot tell them apart; the report records that a text-only arm is degenerate for this pairing task, and NewsCLIPpings was run with image and text only.

Evidence: `BASELINE_REPORT_DRAFT_2026-10-25.md` (Arms); `NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (Clarifications, pilot sampling unit)

**Why run a text-only arm on the same rows?**

The text-only arm uses the same checkpoint and the same rows, so the paired minus text-only difference isolates the image. On the 9,999 MMFakeBench rows usable in both arms, the difference is -0.0151 accuracy, with 95% range [-0.0244, -0.0054]. The paired arm has 9,999 rows only because one image failed to decode (test:3824), while the text-only arm covers all 10,000 rows.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (section 1); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 4, same rows across arms)

**Why no prompt selection or threshold tuning, and what does the model see?**

The zero-shot arms use one fixed question bank (the paper-aligned v2 bank for MMFakeBench, and the unchanged native question for NewsCLIPpings), with no prompt selection and no threshold tuning, so the scores are not fitted to any split. The model receives the image and caption only, and source names and paths are never model inputs.

Evidence: `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (sections 2 and 4); `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (section 1); `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (Model and features)

**Do batch size or the prefix cache change the answers?**

On the tested sample, no. Batch sizes 1, 4 and 8 and the prefix cache produce identical labels on a 300-row test sample, and the saved artifact records a maximum probability difference of 0.0 for every comparison. One sentence in the claims record says "below 1e-4"; the artifact value, 0.0, is the one to quote.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (Reproducibility and gates; Tier-0 determinism); `data/processed/protocol/dataset_native_baseline_20261026_baseline_v1/tier0_equivalence.json`

## Results

**Why is the model below the constant-majority score on MMFakeBench, and does that make the result useless?**

On the 9,999 usable test rows, always answering "original" scores 0.3000 accuracy, while the paired model scores 0.2642 (text-only 0.2793). The paired model's macro-F1 of 0.2037 is above the constant guess's 0.1154, and macro-F1 gives each class equal weight. The result is not useless as a measure of agreement with labels, but it is not evidence of content detection, which is why the source-name rule is reported beside it.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (section 1); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 4, floors beside every score)

**What does the 91.5% source-name rule show, and why is it not a model?**

A lookup on text source and image source, fitted on disjoint validation rows and never shown an image, reaches 0.9150 accuracy and 0.8510 macro-F1 on the 9,999 MMFakeBench test rows, against an in-sample ceiling of 0.9500. Thirteen of 14 source pairs are label-pure, so the labels are largely predictable from metadata. It is an audit of a shortcut, not a model: it reads only source names, which the project treats as audit variables and never as model inputs.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (section 1; six statements, item 3); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 2, ontology rules); `data/reports/baseline_study/MMFAKEBENCH_SOURCE_PAIR_EFFECT_2026-10-25.md` (Method; Reading)

**What does the pooled -1.51 pp hide?**

The pooled paired minus text-only difference of -1.51 pp (9,999 rows) averages within-pair differences that run from -18.0 pp to +18.4 pp across 14 source pairs. Of the pair ranges, 7 lie below zero, 2 lie above and 5 span zero, and the equal-weight mean is -2.78 pp. Because both arms score the same rows, the weighted mean equals the pooled figure, so conditioning on source pair reveals the spread rather than changing the average. The positive pairs are those where a shift in predicted-label mix happens to land on the pair's label, which is not evidence that the image helped the model judge each item.

Evidence: `data/reports/baseline_study/MMFAKEBENCH_SOURCE_PAIR_EFFECT_2026-10-25.md` (Result; Reading items 1 to 3); `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (six statements, item 1)

**What are the headline zero-shot numbers, and how do the arms compare?**

On MMFakeBench, the paired arm scores 0.2642 accuracy and 0.2037 macro-F1, against 0.2793 and 0.2181 for text-only. On VERITE (1,001 rows), the paired arm scores 35.7% against 35.9% for text-only, with a paired minus text-only difference of -0.0020 (95% range [-0.0360, 0.0310]). On the NewsCLIPpings validation set (7,024 rows), zero-shot accuracy is 50.8% with 95% range [0.4978, 0.5181] and macro-F1 0.4185.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (sections 1 to 3); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 3, E1 and E2)

**How well calibrated is the model, and what does that measure?**

The text-only arm is better calibrated on both benchmarks: ECE is 0.0123 against 0.0815 on MMFakeBench, and 0.0404 against 0.0955 on VERITE. ECE here measures agreement with labels, so it says nothing about whether the model knows factual truth.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (sections 1 and 2; six statements, item 2; What is not claimed)

**How well does the model detect visual distortion, and what happens with AI-generated images?**

The paired arm's test F1 for visual distortion is 0.048, with 2.6% recall (26 of 1,000), and the image-only arm is no better (F1 0.031). Textual distortion is the only class predicted with any skill (F1 0.37). In the two visual-distortion pairs that use AI-generated images, the paired arm predicts visual distortion in at most 4.9% of rows.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (six statements, item 4); `data/reports/baseline_study/MMFAKEBENCH_SOURCE_PAIR_EFFECT_2026-10-25.md` (Reading item 5)

**What does the direct binary head show?**

The direct fake/true head reaches AUC 0.474 on MMFakeBench, below chance, and the records state that it is not useful here. Its metrics are in the paired run's metrics file under the binary_noul entry.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (six statements, item 6); `data/processed/protocol/dataset_native_baseline_20261025_test_ablation_v1/mmfakebench_test_paired/paired.metrics.json`

## Validity and threats

**What does "post-hoc" mean for the MMFakeBench test numbers?**

The official MMFakeBench test split was inspected in earlier workspace work before these evaluations, so every test-split number is labelled post-hoc. Those numbers are diagnostics on the test split, not a pristine held-out result and not a confirmation.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (scope; What is not claimed); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 5, held-out test)

**Does the negative pooled image effect mean images are useless?**

No. The records describe one checkpoint (201M parameters) under one zero-shot protocol, which is not evidence that pixels are useless in general. The effect also varies by source pair (-18.0 pp to +18.4 pp), so the pooled figure describes the source mix in this test split rather than a typical per-item image effect.

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (six statements, item 1; What is not claimed); `data/reports/baseline_study/MMFAKEBENCH_SOURCE_PAIR_EFFECT_2026-10-25.md` (Reading item 1; Limits)

**What is the VERITE image-root discrepancy, and does it change the comparison?**

Two VERITE paired runs use different image roots. The current run, on a verified 664-file archive, gives 0.3566, while an older 495-file root gives 0.3478 and is marked historical and not used. The text-only arm is unaffected because its model state takes text only, and its rerun on the canonical root matched on the first 202 rows (maximum delta 0.0).

Evidence: `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (VERITE image-root provenance); `data/reports/baseline_study/VERITE_IMAGE_ROOT_DISCREPANCY_2026-10-25.md`

**Is the VERITE "miscaptioned" mapping to textual distortion an established fact?**

No. The synthesis treats it as a bridge and an interpretation, not a fact from VERITE's documentation: a real image keeps its true context and the caption is rewritten, so the falsity enters through the text.

Evidence: `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 2)

**What are the main limitations?**

The study uses one 201M-parameter checkpoint under one protocol. The MMFakeBench test numbers are post-hoc, VERITE uses the 1,001-row CSV, NewsCLIPpings is a streamed local evaluation with unresolved VisualNews terms, and the ranges are descriptive rather than confirmatory. On the probe, the VERITE gain spans zero, and the NewsCLIPpings test AUC is 0.598.

Evidence: `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Limits; Reading); `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (What is not claimed)

## The transfer probe

**What is a linear probe, and does training it violate "zero-shot"?**

A linear probe is a logistic-regression classifier trained on frozen features. Here the features are the 576-dimensional pooled state that the checkpoint's own decision head reads, standardized with training rows only. The checkpoint's weights never change, and the zero-shot answers are reported separately on the same rows, so the zero-shot claims stand; the probe is a separate, trained layer that the protocol records as a scoped exception to the baseline-only policy, authorized by the user for this experiment.

Evidence: `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (header; Model and features; Probe); `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (What was done)

**Is the NewsCLIPpings test really held out, and how do we know?**

Amendment 2 was recorded before any full-run feature, test row or VERITE row was read, and the NewsCLIPpings test split was never read in this workspace before the single scoring step. The regularization strength was chosen on validation only, and the selected probe was applied once to the 7,264 test rows. Validation accuracy (56.6%) and test accuracy (57.4%) agree, which is what a held-out split should show.

Evidence: `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (Data; Amendment 2); `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (What was done; Reading)

**Why did the probe move from CPU to the Apple GPU, and could that change the results?**

The CPU pilot ran at 0.42 rows/s and would have exceeded its budget, so Amendment 1 moved feature extraction to the Apple GPU before any training row was featurized. On 20 validation images the native probabilities matched to four decimals, pooled features differed by at most 2.4e-4, and the MPS run took 0.27 s/row against 2.27 s/row on CPU. The integrity gate on all 7,024 validation rows passed with a maximum difference of 0.0001 against a tolerance of 0.001, so small numerical differences are possible and the records measure them as small.

Evidence: `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (Amendment 1); `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Run and gates)

**How was the regularization strength chosen, and why did the grid widen?**

The regularization strength is chosen on validation accuracy, with ties going to the larger value. The pilot selected the largest value in the first grid (the grid ended at 1), so Amendment 2 added 10 and 100 before any test or VERITE row was read. The full run selected 0.001 with validation accuracy 56.6%, and that validation figure is selection-biased, while the test and VERITE numbers were scored once.

Evidence: `data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md` (Probe; Amendment 2); `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Regularization)

**What does the probe show on the held-out NewsCLIPpings test and on VERITE?**

On the held-out NewsCLIPpings test (7,264 rows), the probe scores 57.4% against 51.1% for zero-shot on the same rows, a difference of +6.24 pp with 95% range [4.76, 7.70]. On VERITE true versus out-of-context (663 rows), the probe scores 54.9% against 50.5%, a difference of +4.37 pp with range [-1.36, 9.95], which spans zero. The NewsCLIPpings signal is weak, with an AUC of 0.598.

Evidence: `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Targets; Reading); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 6)

## Comparison with published work

**Why is the 76.3% VERITE target not comparable with the 35.7% result?**

The 76.3% is LAMAR [E2E, Gate]'s binary true versus out-of-context result on VERITE, trained end to end on NewsCLIPpings. The 35.7% is this study's three-class accuracy over all 1,001 rows (true, miscaptioned, out-of-context), so the two measure different tasks. The fair comparison is the probe's 54.9% on the binary task, and the three-class result stays in its own column.

Evidence: `dashboard/published_supplement.json` (VERITE entries); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 5); `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (section 2)

**Why is the study far below 84.8% and 88.4%?**

84.8% is LAMAR [E2E, Attention] and 88.4% is SNIFFER, both on the NewsCLIPpings test split. Those published systems update their whole model, and CCN and SNIFFER also retrieve web evidence for each item, whereas this study trains one linear head on a frozen checkpoint. The probe's 57.4% sits about 27 to 31 points below the trained systems, and the original fine-tuned CLIP ViT-B/32 result of 60.2% sits about 3 points above the probe.

Evidence: `dashboard/published_supplement.json`; `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Against published results); `data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md` (What is not claimed)

**What is the 54.9% in the LAMAR results, and how does it differ from the probe's 54.9%?**

LAMAR [E2E, Gate], trained on Molmo-D3 with NewsCLIPpings for out-of-context, reports 54.9% on VERITE's native three-way task. The probe's 54.9% is a binary true-versus-out-of-context result on 663 rows from a frozen checkpoint with a linear head. The two numbers match but measure different tasks and different systems, so they should not be placed side by side as equivalent.

Evidence: `dashboard/published_supplement.json` (VERITE three-way entry); `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Targets; Against published results); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 5)

**Did the study meet the POS stretch targets?**

No. On the held-out NewsCLIPpings test, the probe reaches 57.4% against the 84.8% target, and on VERITE true versus out-of-context it reaches 54.9% against 76.3%. The POS asks that unmet targets be reported transparently rather than treated as failure, and the synthesis states both as not met.

Evidence: `/Users/rafiulhaider/Downloads/POS_final.pdf` (Objective 5; Success Criteria; Obstacles); `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 7, item 5); `data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` (Targets)

## Next steps

**What is the "Attention and Gate" issue?**

The POS asks for two fine-tuned variants of the model named Attention and Gate. In the published work, Attention and Gate are LAMAR integration methods ([E2E, Attention] and [E2E, Gate]), and the model has no such variants. The proposed resolution is to implement them as fusion heads over frozen features, a direct extension of the linear probe, and to name them that way.

Evidence: `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 5, model identity); `/Users/rafiulhaider/Downloads/POS_final.pdf` (Objective 5)

**What are the six comparison conditions?**

The POS names six comparison conditions without listing them, so the proposal for the team is: (1) zero-shot image plus text, (2) zero-shot text only, (3) frozen-feature linear probe, (4) Attention head, (5) Gate head and (6) CLIP embedding classifier. Conditions 1 to 3 are marked done, but the records show the text-only arm on MMFakeBench and VERITE only, so a text-only NewsCLIPpings run is not established in the current records.

Evidence: `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (section 3, E2; section 5, six comparison conditions); `/Users/rafiulhaider/Downloads/POS_final.pdf` (Objective 5)

**What would you do next for the final submission?**

Train Attention and Gate fusion heads on frozen features using NewsCLIPpings train, select on validation, and score NewsCLIPpings test and VERITE true-versus-out-of-context once, following the probe pipeline. Add the CLIP embedding classifier on the same rows, run three seeds for any stochastic head with the paired cluster bootstrap (the probe itself is deterministic, so seeds do not vary it), and audit image-hash overlap before any MMFakeBench evaluation of a NewsCLIPpings-trained model. The captioning pipeline is also an open item for the fine-tuning stage.

Evidence: `MIDTERM_PRETRAINED_BASELINE/01_PROJECT_SYNTHESIS.md` (sections 5 and 7); `/Users/rafiulhaider/Downloads/POS_final.pdf` (Objective 5)
