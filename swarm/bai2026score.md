# Extraction — Conformal Selective Prediction with General Risk Control (protocol v1.1, §4.2)

1. **Study ID:** Bai2026score
2. **Report ID and linked reports:** arXiv:2603.24704v1 (submitted 25 Mar 2026). Abstract page read in full 2026-11-28; body not read in this pass.
3. **Authors:** Tian Bai, Ying Jin.
4. **Year:** 2026.
5. **Title:** Conformal Selective Prediction with General Risk Control
6. **Venue and publication type:** arXiv preprint (stat.ME), posted before peer review.
7. **DOI or arXiv ID and link:** arXiv:2603.24704; https://arxiv.org/abs/2603.24704
8. **Extractor and date:** swarm chair, 2026-11-28 (single extraction, dual extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Fields rest on the abstract only.
11. **Eligibility confirmation:** Meets I1 (original method plus evaluation), I2 (RQ3 abstention and selective prediction; RQ4 risk control), I3 as background (no LAYA benchmark), I4 (arXiv 2026), I5 (English), I6 (abstract retrieved; full text available).
12. **Paper role:** Background. Basis: drug discovery, health risk prediction and LLM applications, not a multimodal misinformation benchmark and no LAYA dataset.
13. **Research question or stated aim:** How to enforce strict, precise error control over the cases a system chooses to trust, for any trained model and any user-defined bounded, continuously-valued risk (Abstract).
14. **Method and design:** SCoRE (Selective Conformal Risk control with E-values) constructs a class of generalised e-values whose product with the unknown risk has expectation at most one, ensured by data exchangeability with no modelling assumptions, then passes the e-values to hypothesis testing procedures to yield binary trust decisions with finite-sample error control. The construction avoids uniform concentration and extends to distribution shift settings (Abstract).
15. **System or model described:** Model-agnostic post-hoc trust layer over any trained model; the output is a binary trust or abstain decision per case (Abstract).
16. **Dataset(s) used:** Simulations plus applications in drug discovery, health risk prediction and large language models; dataset names not given in the abstract. No LAYA dataset.
17. **Dataset construction and labelling:** Not reported in the text read.
18. **Evaluation split:** Not stated in the abstract.
19. **Metrics and metric definitions:** Risk among trusted (positive) cases, under a user-defined bounded continuous risk; finite-sample error control of the trust decisions (Abstract).
20. **Threshold, abstention and decision rule:** Trust is decided case by case by the e-value testing procedure; cases not trusted are abstentions, and the guarantee is stated on the trusted subset (Abstract).
21. **Headline results (as reported):** The methods are evaluated in simulations and shown effective in the three application areas (Abstract). No numeric values are given in the abstract.
22. **Source of each headline result:** Abstract for all statements in field 21.
23. **Calibration results and method:** No calibration error measure is reported in the abstract; control is by finite-sample testing, not by a fitted calibration map.
24. **Abstention and selective prediction results:** Abstention is the complement of the binary trust decision; no coverage or risk-at-coverage numbers are given in the abstract.
25. **Evidence retrieval: method and results:** No retrieval. Not applicable.
26. **Key points relevant to LAYA:** (Shown) The risk a guarantee controls can be a general bounded continuous loss, not only a 0-1 error, and the trust decision can be made without uniform concentration arguments (Abstract). (Inference, labelled) For LAYA, a selective claim stated only in accuracy terms leaves open whether a continuous loss, such as a probability score loss on accepted items, would still be controlled; naming the risk the guarantee covers is part of the claim. (Shown) The guarantee again covers trusted cases only, which reinforces the accepted-subset scoping rule from Xu2026scrc in the same run. No LAYA number is measured or changed by this paper.
27. **Key points non-relevant but notable:** E-values let the same construction extend to distribution shift, where standard exchangeability arguments weaken (Abstract).
28. **Authors' stated conclusions:** SCoRE gives finite-sample, distribution-free control of bounded continuous risks in selectively trusting any model (Abstract).
29. **Limitations stated by the authors:** None stated in the abstract read; the risk must be bounded and continuously-valued for the construction as described.
30. **Limitations identified by the extractor:** Abstract-only read; no numbers, splits or per-application results read; power and coverage cost of the testing procedure at small calibration sizes is not visible in the abstract.
31. **Funding and conflicts of interest:** Not reported in the text read.
32. **Code, data and materials availability:** Not stated in the abstract read.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection — Some concerns: efficacy summarised without numbers in this pass. (b) Missing data — Some concerns: abstained cases are outside the stated guarantee, accounting not described in the abstract. (c) Measurement — Low concerns for the construction claim: the e-value property is stated and rests on exchangeability alone. (d) Leakage — Some concerns: calibration and evaluation separation not read. (e) Deviations — Some concerns: cannot be assessed on an abstract-only read.
34. **Overall quality judgement:** Some concerns. Supports use as an RQ3/RQ4 design prior only; no number here is comparable to a LAYA number.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No dataset, split, metric or decision rule is shared with any LAYA result. Nothing from this paper may sit beside a LAYA number.
37. **Discrepancies and unresolved disagreements:** None found in the text read. Board pass (chair, 2026-11-28): proponent case (general continuous risk, no modelling assumptions, shift extension) against the skeptic case (abstract-only, no numbers, no LAYA task, guarantee scoped to trusted cases). Outcome: Background only, partial extraction declared. One scoped rule recorded: name the exact risk, bounded and as defined, that any selective guarantee controls, and state that it covers trusted cases only.
