# Extraction — How Short Is Too Short? Length-Conditional Calibration and Abstention for Detecting AI-Generated Text (protocol v1.1)

1. Study ID: Janga2026lengthcal
2. Report ID: arXiv:2611.10901v1. No linked reports found.
3. Authors: Ritesh Janga, Justin Zhan.
4. Year: 2026.
5. Title: How Short Is Too Short? Length-Conditional Calibration and Abstention for Detecting AI-Generated Text
6. Venue: arXiv preprint (v1, submitted 7 Nov 2026).
7. arXiv:2611.10901; https://arxiv.org/abs/2611.10901
8. Extractor: swarm chair, 2026-11-26 (single extraction, LLM-assisted; dual-extraction fallback declared).
9. Form version: protocol v1.1 (2026-11-24)
10. Status: Partial. Abstract read in full; full text not read in this pass.
11. Eligibility: I1 original method and evaluation, I2 RQ3 abstention and RQ4 calibration, I3 background only, I4 arXiv 2026, I5 English, I6 full text retrievable, read in part and declared.
12. Role: Background. AI-generated text detection, not a LAYA benchmark.
13. Aim: Show how a threshold tuned on long passages fails on short ones, and calibrate within length bins with an abstention rule for uninformative lengths.
14. Method: Closed form for false-positive rate drift as length falls and for tokens needed for a target true-positive rate; thresholds calibrated within length bins using conformal p-values; bin-level abstention when a detector cannot be informative at that length.
15. System: Three zero-shot detectors (log-likelihood, log-rank, Binoculars), three corpora, two open-weight generators.
16. Datasets: Three corpora as named in the abstract; detail not read beyond abstract.
17. Construction: Established corpora plus generated text; detail not read.
18. Split: 300 random document-level resplits, averaged.
19. Metrics: False-positive rate per detector-length cell, true-positive rate.
20. Decision rule: Bin-level abstention when the detector cannot reach the chosen true-positive floor at that length.
21. Headline results (as reported): Binned calibration holds mean false-positive rate at 5.0 percent in every detector-length cell from 10 to 200 tokens. A single threshold set at 200 tokens gives 29 percent false positives for Binoculars at 10 tokens and about 1 percent for log-likelihood. No detector reaches an 80 percent true-positive rate; the best, Binoculars at 200 tokens, reaches 59 percent, so the rule abstains in every cell at that floor and releases only the 200-token bins at floors of 0.3 and 0.5.
22. Source: Abstract of arXiv:2611.10901v1, read 2026-11-26.
23. Calibration: Core. Calibration is conditional on a stated covariate (length); a pooled threshold is shown to fail by a predictable amount.
24. Abstention: Core. Abstention is triggered by informativeness at the bin level, not by a per-item confidence score alone.
25. Evidence retrieval: None.
26. Relevance to LAYA: (Shown, in its own setting) A threshold that is calibrated on one slice can be badly miscalibrated on another slice defined by an observable covariate, and bin-conditional calibration plus a bin-level abstention rule fixes the false-positive rate while honestly refusing uninformative bins. (Inference, labelled) For LAYA, calibration and abstention should be checked conditional on observable slices such as evidence length or coverage, not only pooled, on validation splits.
27. Notable non-relevant: The closed-form drift prediction matches the empirical failure, so the failure mode is predictable in advance, not only diagnosed after.
28. Authors' conclusions: Length-conditional calibration holds the nominal rate at every length; at demanding floors the honest answer is to abstain (abstract).
29. Limitations stated by authors: Not read in this pass.
30. Extractor limitations: Partial read, abstract only.
31. Funding and conflicts: Not reported in sections read.
32. Availability: Not reported in sections read.
33. Risk of bias: (a) Selection, low to some concerns: results averaged over 300 resplits, a strength. (b) Missing data, cannot tell. (c) Measurement, low concern for the headline: false-positive rate is directly measured per cell. (d) Leakage, cannot tell. (e) Deviations, cannot tell.
34. Overall: Some concerns, mainly partial read.
35. Comparability verdict: No, not comparable.
36. Scoping note: No number may sit beside a LAYA number: different task, detectors, and datasets. Method evidence for RQ3 and RQ4 only.
37. Discrepancies: None found. Board pass (chair, 2026-11-26): proponent (closed form plus 300 resplits, per-cell rates reported, abstention follows informativeness) against skeptic (different task, abstract-only, synthetic-score agreement may not transfer). Outcome: Background confirmed; slice-conditional calibration point recorded as a finding; no comparator number recorded.
