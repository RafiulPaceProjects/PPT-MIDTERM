# Extraction — Selective Conformal Risk Control (protocol v1.1, §4.2)

1. **Study ID:** Xu2026scrc
2. **Report ID and linked reports:** arXiv:2512.12844v2 (submitted 14 Dec 2025, revised 27 Apr 2026). Abstract page (v2) read in full 2026-11-28; body not read in this pass. v2 is the main source.
3. **Authors:** Yunpeng Xu, Wenge Guo, Zhi Wei.
4. **Year:** 2026 (v2; v1 2025).
5. **Title:** Selective Conformal Risk Control
6. **Venue and publication type:** arXiv preprint, v2, posted before peer review.
7. **DOI or arXiv ID and link:** arXiv:2512.12844; https://arxiv.org/abs/2512.12844
8. **Extractor and date:** swarm chair, 2026-11-28 (single extraction, dual extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Fields rest on the v2 abstract only.
11. **Eligibility confirmation:** Meets I1 (original method plus evaluation), I2 (RQ3 abstention and selective prediction; RQ4 risk control and calibration), I3 as background (no LAYA benchmark), I4 (arXiv, v2 2026), I5 (English), I6 (abstract retrieved; full text available).
12. **Paper role:** Background. Basis: general classification datasets, not a multimodal misinformation benchmark and no LAYA dataset.
13. **Research question or stated aim:** How to get compact prediction sets with distribution-free coverage and risk guarantees when a system may first select only confident samples for prediction (Abstract).
14. **Method and design:** Two-stage formulation: stage one selects confident samples, stage two applies conformal risk control on the selected subset only. Two algorithms: SCRC-T computes thresholds jointly over calibration and test samples, preserving exchangeability with exact finite-sample guarantees at per-test recomputation cost; SCRC-I is calibration-only, with PAC-style guarantees and better computational practicality (Abstract).
15. **System or model described:** Selective conformal risk control framework over an unspecified base classifier; inputs and model family not named in the abstract.
16. **Dataset(s) used:** Two public datasets; names not given in the abstract. No LAYA dataset.
17. **Dataset construction and labelling:** Not reported in the text read.
18. **Evaluation split:** Calibration and test construction not stated in the abstract.
19. **Metrics and metric definitions:** Coverage and risk levels against stated targets, prediction set size implied by compactness claim (Abstract).
20. **Threshold, abstention and decision rule:** Selection comes first; the conformal guarantee is computed on, and applies to, the accepted subset only. Abstained items are outside the stage-two guarantee (Abstract, by construction of the method).
21. **Headline results (as reported):** Both methods achieve the target coverage and risk levels with nearly identical performance; SCRC-I is slightly more conservative on risk control and superior on computational practicality (Abstract). No numeric values are given in the abstract.
22. **Source of each headline result:** Abstract (v2) for all statements in field 21.
23. **Calibration results and method:** Risk control is conformal on the selected subset; no calibration error measure is reported in the abstract.
24. **Abstention and selective prediction results:** Selection is the abstention mechanism; no coverage or risk-at-coverage numbers are given in the abstract.
25. **Evidence retrieval: method and results:** No retrieval. Not applicable.
26. **Key points relevant to LAYA:** (Shown) The guarantee and the selection are separate stages, and the guarantee covers only what was accepted (Abstract). (Inference, labelled) A LAYA selective claim that quotes a risk guarantee without stating that it covers the accepted subset only, with the abstained set accounted for separately, overstates what the guarantee says. This matches the protocol field 20 and field 24 rule. No LAYA number is measured or changed by this paper.
27. **Key points non-relevant but notable:** Exactness and practicality trade directly: the exact variant pays per-test recomputation, the practical variant pays with a weaker, probabilistic guarantee (Abstract).
28. **Authors' stated conclusions:** Selective conformal risk control offers an effective and efficient path toward compact, reliable uncertainty quantification (Abstract).
29. **Limitations stated by the authors:** SCRC-I is more conservative; SCRC-T costs per-test recomputation (Abstract). No other limitations stated in the text read.
30. **Limitations identified by the extractor:** Abstract-only read; dataset names, splits and numbers not read; selection stage itself carries no guarantee in the abstract, so a poor selector is not ruled out by the stage-two result.
31. **Funding and conflicts of interest:** Not reported in the text read.
32. **Code, data and materials availability:** Not stated in the abstract read.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection — Some concerns: results summarised qualitatively in the abstract, no numbers in this pass. (b) Missing data — Some concerns: abstained items are outside the guarantee by design, and their accounting is not described in the abstract. (c) Measurement — Low concerns for the guarantee claim: it rests on the stated exchangeability construction. (d) Leakage — Some concerns: calibration and test separation beyond the joint-threshold construction not read. (e) Deviations — Some concerns: cannot be assessed on an abstract-only read.
34. **Overall quality judgement:** Some concerns. Supports use as an RQ3/RQ4 design prior only; no number here is comparable to a LAYA number.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No dataset, split, metric or decision rule is shared with any LAYA result. Nothing from this paper may sit beside a LAYA number.
37. **Discrepancies and unresolved disagreements:** None found in the text read. Board pass (chair, 2026-11-28): proponent case (clean two-stage separation, exact and practical variants stated honestly) against the skeptic case (abstract-only, no numbers, no LAYA task, selection stage unguaranteed). Outcome: Background only, partial extraction declared. One scoped rule recorded: state the selection stage and the accepted-subset scope beside any selective risk guarantee.
