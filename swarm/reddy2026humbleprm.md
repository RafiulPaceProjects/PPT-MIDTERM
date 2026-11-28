# Extraction — HumblePRM: Improving VLM Abstention in Ambiguous Inputs (protocol v1.1, §4.2)

1. **Study ID:** Reddy2026humbleprm
2. **Report ID and linked reports:** arXiv:2611.33452v1 (posted 24 November 2026, per the ReadSearch listing read 2026-11-28). Single report known. Abstract read in full; body not read in this pass.
3. **Authors:** Saket Reddy, Ke Yang, ChengXiang Zhai.
4. **Year:** 2026.
5. **Title:** HumblePRM: Improving VLM Abstention in Ambiguous Inputs (title as listed; the listing truncates it).
6. **Venue and publication type:** arXiv preprint only, posted before peer review.
7. **DOI or arXiv ID and link:** arXiv:2611.33452; listing at https://readsearch.ai/paper/arxiv/2611.33452v1
8. **Extractor and date:** swarm chair, 2026-11-28 (single extraction, dual extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Fields rest on the abstract only.
11. **Eligibility confirmation:** Meets I1 (original method with own results), I2 (RQ3 abstention; RQ4 calibration of expressed confidence), I3 as background (no LAYA benchmark), I4 (arXiv 2026), I5 (English), I6 (abstract retrieved; full text available).
12. **Paper role:** Background. Basis: VLM abstention on ambiguous visual inputs, not NewsCLIPpings, VERITE or MMFakeBench, and no misinformation task.
13. **Research question or stated aim:** Whether scoring perception and calibration as separate stages, rewarding agreement between evidence and expressed confidence rather than outcome correctness alone, improves abstention on ambiguous inputs (Abstract).
14. **Method and design:** Reasoning split into two stages: perception (factual scene description) and calibration (judging whether the evidence is sufficient to commit). HumblePRM, a lightweight process reward model, scores each stage independently and is used in training (Abstract).
15. **System or model described:** HumblePRM process reward model applied to VLMs; transfer to Gemma 4 E4B reported (Abstract).
16. **Dataset(s) used:** Not named in the text read. No LAYA dataset.
17. **Dataset construction and labelling:** Not reported in the text read.
18. **Evaluation split:** Not reported in the text read.
19. **Metrics and metric definitions:** Abstention due to uncertainty on ambiguous inputs, and accuracy on clear images; no numeric values in the text read (Abstract).
20. **Threshold, abstention and decision rule:** Not reported in the text read; abstention is trained through stage-wise process reward, not a stated post-hoc threshold.
21. **Headline results (as reported):** Training with HumblePRM increases abstention due to uncertainty on ambiguous inputs considerably while leaving accuracy on clear images roughly unchanged; the improvement transfers to Gemma 4 E4B. No numbers in the text read (Abstract).
22. **Source of each headline result:** Abstract for all statements in field 21.
23. **Calibration results and method:** The calibration stage judges evidence sufficiency before commitment; no calibration measure is reported in the text read.
24. **Abstention and selective prediction results:** The qualitative result in field 21 (Abstract).
25. **Evidence retrieval: method and results:** No retrieval. Evidence here means what is visible in the image.
26. **Key points relevant to LAYA:** (Shown) Outcome-only supervision rewards a confident answer regardless of whether the evidence supports one; scoring the perception stage and the commitment stage separately changes abstention behaviour without a stated accuracy cost on clear inputs (Abstract). (Inference, labelled) For LAYA, this supports auditing which stage drives an abstention, perception failure or evidence insufficiency, rather than treating abstention as one undifferentiated event. No LAYA number is measured or changed by this paper.
27. **Key points non-relevant but notable:** The method assumes existing approaches can presuppose an objective verdict always exists; the paper treats no-verdict inputs as a real category (Abstract).
28. **Authors' stated conclusions:** Process reward supervision is a promising route to better calibrated abstention in VLMs (Abstract).
29. **Limitations stated by the authors:** None stated in the text read.
30. **Limitations identified by the extractor:** Abstract-only read with no numbers, datasets or splits; effect sizes cannot be weighed.
31. **Funding and conflicts of interest:** Not reported in the text read.
32. **Code, data and materials availability:** Not stated in the text read.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection — Some concerns: datasets not named in the text read. (b) Missing data — Some concerns: not addressed. (c) Measurement — Some concerns: headline claims are qualitative in the abstract. (d) Leakage — Some concerns: not addressed. (e) Deviations — Some concerns: cannot be assessed on an abstract-only read.
34. **Overall quality judgement:** Some concerns. Supports use as an RQ3 stage-design prior only; no number here is comparable to a LAYA number.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No dataset, split, metric or decision rule is shared with any LAYA result. Nothing from this paper may sit beside a LAYA number.
37. **Discrepancies and unresolved disagreements:** Board pass (chair, 2026-11-28): proponent case (clean two-stage split, directly on RQ3, with a transfer result) against the skeptic case (abstract-only, no numbers, VLM ambiguity task rather than verification). Outcome: Background only, partial extraction declared. One scoped consequence recorded: abstention audits should name the stage that drove the abstention. No internal numeric discrepancies in the text read.
