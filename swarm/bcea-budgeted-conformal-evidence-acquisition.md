# Extraction — BCEA / Look Again Before You Abstain (protocol v1.1, §4.2)

1. **Study ID:** Xu2026bcea
2. **Report ID and linked reports:** arXiv:2606.16667 (HTML full text opened, 2026-11-27). Single report.
3. **Authors:** Jian Xu, Yanning Wu, Delu Zeng, John Paisley, Qibin Zhao.
4. **Year:** 2026.
5. **Title:** Look Again Before You Abstain: Budgeted Conformal Evidence Acquisition for Reliable Vision-Language Models
6. **Venue and publication type:** arXiv preprint.
7. **DOI or arXiv ID and link:** arXiv:2606.16667; https://arxiv.org/html/2606.16667
8. **Extractor and date:** swarm chair, 2026-11-27 (single extraction, LLM-assisted; dual-extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Abstract and Sections 1 to 4 read; results tables not read section by section in this pass.
11. **Eligibility confirmation:** Meets I1 (original method and evaluation), I2 (RQ3 abstention, RQ4 calibration, RQ5 evidence), I4, I5, I6.
12. **Paper role:** Background. COCO and POPE claim grounding, no LAYA benchmark, so no number enters the comparability table.
13. **Research question or stated aim:** Can a vision-language model acquire more visual evidence instead of abstaining, without losing the conformal guarantee on the hallucination rate among asserted claims (Abstract, §1).
14. **Method and design:** Three-way decision: answer, abstain, or acquire (zoom crops or a claim-specific intervention) under a compute budget. The whole acquisition policy is folded into the score and the conformal threshold is recalibrated on post-acquisition scores. Naive acquisition, calibrating on the pre-acquisition score, is shown to break the guarantee (§§1, 4).
15. **System or model described:** BCEA filter over four open VLMs: LLaVA-1.5, Qwen3-VL, LLaVA-NeXT, InternVL2. Scores: global ungrounding (likelihood drop when the image is removed) and targeted intervention scores, for example a horizontal flip for spatial relations (§4.1).
16. **Dataset(s) used:** COCO and POPE existence and relation claims; 1,440 balanced object-existence claims in Figure 1; free-form captions (§§1, 3).
17. **Dataset construction and labelling:** Not reported in the sections read.
18. **Evaluation split:** 300 splits for the exact certificate, as reported in the abstract; split names not stated in the sections read.
19. **Metrics and metric definitions:** Coverage (fraction asserted), selective risk (hallucination rate among asserted claims), AUROC for relation verification (§3).
20. **Threshold, abstention and decision rule:** Assert iff score is at or above a conformally calibrated threshold; borderline claims trigger acquisition; the threshold must be calibrated on post-acquisition scores, with a Bonferroni corrected Clopper-Pearson bound over a fixed threshold grid (§§3, 4).
21. **Headline results (as reported):** A conformal filter must abstain on over 80 percent of claims to hold hallucination below 5 percent; a horizontal flip lifts spatial-relation verification from 0.57 to 0.77 AUROC; on free-form captions (20.6 percent hallucinated) BCEA certifies 34 percent of claims at a guaranteed at most 10 percent rate against 24 percent for abstention; zero empirical violations over 300 splits for the exact variant (Abstract).
22. **Source of each headline result:** Abstract and §§1, 3, 4 of arXiv:2606.16667, read 2026-11-27.
23. **Calibration results and method:** Split-conformal selective risk control with exact Clopper-Pearson bounds; recalibration on post-acquisition scores restores the finite-sample guarantee (§3).
24. **Abstention and selective prediction results:** Abstention-only coverage is the baseline BCEA beats at moderate risk; certified coverage figures are in Table 1, not read in this pass (Abstract, Figure 1).
25. **Evidence retrieval: method and results:** Evidence is visual, not retrieved text: zoom crops and claim-type interventions re-encode new views. Model-guided crops beat a uniform grid; per-claim budget allocation does not help (§1).
26. **Key points relevant to LAYA:** (Shown) Any step that changes a score after calibration breaks the guarantee unless that step is folded into the score and recalibrated. That applies directly to any LAYA gate that re-checks evidence after a first score. (Shown) A third action, acquire more evidence, can recover coverage that pure abstention gives up. (Inference) A LAYA evidence-acquisition avenue must state, in its PRD, that calibration is done on post-acquisition scores only.
27. **Key points non-relevant but notable:** Claim-type interventions can supply signal a global score cannot: one flip separates left-of from right-of claims that image removal cannot.
28. **Authors' stated conclusions:** BCEA is, to their knowledge, the first method to couple guaranteed VLM hallucination filtering with visual evidence acquisition (Abstract, §2).
29. **Limitations stated by the authors:** The practical variant is uncertified; the exact variant beats abstention only at moderate risk (Abstract).
30. **Limitations identified by the extractor:** Partial read; claim grounding on COCO and POPE, not veracity verdicts on news items; no LAYA dataset; results tables not read in this pass.
31. **Funding and conflicts of interest:** Not reported in the sections read.
32. **Code, data and materials availability:** Not stated in the sections read.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection, Low concern: baselines and both certified and practical variants reported. (b) Missing data, Low concern: abstained claims are the explicit subject and are counted as lost coverage. (c) Measurement, Low concern: coverage and risk defined in §3. (d) Leakage, Cannot tell in this pass. (e) Deviations, Low concern: the naive, guarantee-breaking variant is reported as a failure, not hidden.
34. **Overall quality judgement:** Some concerns, driven by the partial read.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No number from this paper may sit beside a LAYA number. Blocking differences: COCO and POPE claim grounding rather than NewsCLIPpings, VERITE or MMFakeBench veracity; claim-level coverage and risk rather than verdict accuracy; no shared split or decision rule.
37. **Discrepancies and unresolved disagreements:** None found in the sections read.
