# Extraction — Entropy Alone is Insufficient for Safe Selective Prediction in LLMs (protocol v1.1, §4.2)

1. **Study ID:** Phillips2026entropy
2. **Report ID and linked reports:** arXiv:2603.21172v1 (submitted 22 Mar 2026). Abstract page read in full 2026-11-28; body not read in this pass.
3. **Authors:** Edward Phillips, Fredrik K. Gustafsson, Sean Wu, Anshul Thakur, David A. Clifton.
4. **Year:** 2026.
5. **Title:** Entropy Alone is Insufficient for Safe Selective Prediction in LLMs
6. **Venue and publication type:** arXiv preprint, v1, posted before peer review.
7. **DOI or arXiv ID and link:** arXiv:2603.21172; https://arxiv.org/abs/2603.21172
8. **Extractor and date:** swarm chair, 2026-11-28 (single extraction, dual extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Fields rest on the abstract only.
11. **Eligibility confirmation:** Meets I1 (original evaluation with own results), I2 (RQ3 selective prediction and abstention; RQ4 calibration), I3 as background (no LAYA benchmark), I4 (arXiv 2026), I5 (English), I6 (abstract retrieved; full text available).
12. **Paper role:** Background. Basis: text QA benchmarks only, no multimodal misinformation task and no LAYA dataset.
13. **Research question or stated aim:** Whether entropy-based uncertainty, evaluated inside the wider selective prediction policy at low target error rates, can be trusted to drive abstention, and whether adding a correctness probe signal fixes its failure mode (Abstract).
14. **Method and design:** Entropy-based uncertainty methods are evaluated as abstention signals across model families, a model-dependent failure mode (the confidently wrong, low-entropy regime) is identified, and a combined entropy plus correctness probe score is compared against entropy-only baselines (Abstract; introduction as indexed).
15. **System or model described:** Selective prediction policies over LLMs from four model families; uncertainty signals are entropy scores and a supervised correctness probe (Abstract).
16. **Dataset(s) used:** TriviaQA, BioASQ, MedicalQA (Abstract). No LAYA dataset.
17. **Dataset construction and labelling:** Not reported in the text read.
18. **Evaluation split:** Not reported in the abstract.
19. **Metrics and metric definitions:** Risk-coverage trade-off (AURC in the indexed full text) and calibration performance; a target calibration error measure is defined in the body, not read in this pass (Abstract; indexed introduction).
20. **Threshold, abstention and decision rule:** Abstention is driven by the uncertainty score against a target error rate; the paper's point is that the policy must be evaluated at the stated risk level, not by AUROC alone (Abstract; indexed introduction).
21. **Headline results (as reported):** The combined entropy plus probe score generally improves both the risk-coverage trade-off and calibration performance relative to entropy-only baselines across three QA benchmarks and four model families. No single headline number is given in the abstract (Abstract).
22. **Source of each headline result:** Abstract for all statements in field 21.
23. **Calibration results and method:** Calibration performance is reported as improved by the combined score; the measure and values were not read in this pass.
24. **Abstention and selective prediction results:** Entropy-only abstention is unreliable in a model-dependent way: low-entropy hallucinations form a confidently wrong regime where entropy fails to flag errors (Abstract; indexed introduction).
25. **Evidence retrieval: method and results:** No retrieval. Not applicable beyond noting the system uses none in the text read.
26. **Key points relevant to LAYA:** (Shown) A single distributional uncertainty signal can fail exactly where abstention matters most, on confident errors, and the failure varies by model (Abstract). (Inference, labelled) Any LAYA abstention rule that rests on one signal, such as temperature-scaled confidence alone, carries the same structural risk; a second, correctness-trained signal is the paper's remedy and is testable on frozen validation predictions. No LAYA number is measured or changed by this paper.
27. **Key points non-relevant but notable:** The paper argues for deployment-facing evaluation: strong AUROC does not imply reliable selective prediction at a strict stated risk level (indexed introduction).
28. **Authors' stated conclusions:** Entropy alone is insufficient for safe selective prediction; combining entropy with a correctness probe generally improves the trade-off and calibration, and uncertainty methods should be evaluated by whether the system can be trusted at a stated risk level (Abstract).
29. **Limitations stated by the authors:** The entropy failure mode is model-dependent, so no single behaviour can be assumed across model families (Abstract).
30. **Limitations identified by the extractor:** Abstract-only read; text QA only, no multimodal verdicts; "generally improves" is unquantified in the abstract, so effect sizes are unknown in this pass.
31. **Funding and conflicts of interest:** Not reported in the text read.
32. **Code, data and materials availability:** Not stated in the text read.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection — Some concerns: abstract reports a general improvement without per-benchmark values. (b) Missing data — Some concerns: not addressed in the abstract. (c) Measurement — Low concerns for the design claim: risk-coverage and target-risk evaluation are the right measures for the claim made. (d) Leakage — Some concerns: probe training data and its separation from evaluation were not read. (e) Deviations — Some concerns: cannot be assessed on an abstract-only read.
34. **Overall quality judgement:** Some concerns. Supports use as an RQ3/RQ4 design prior only; no number here is comparable to a LAYA number.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No dataset, split, metric or decision rule is shared with any LAYA result. Nothing from this paper may sit beside a LAYA number.
37. **Discrepancies and unresolved disagreements:** Board pass (chair, 2026-11-28): proponent case (directly on the single-signal abstention question, four model families, honest model-dependence) against the skeptic case (abstract-only, unquantified improvement, text QA only). Outcome: Background only, partial extraction declared. One scoped rule recorded: an abstention claim resting on one uncertainty signal is incomplete until a second, differently trained signal has been checked against it. No internal numeric discrepancies in the text read.
