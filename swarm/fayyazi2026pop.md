# Extraction — Proof-of-Perception: Certified Tool-Using Multimodal Reasoning with Compositional Conformal Guarantees (protocol v1.1, §4.2)

1. **Study ID:** Fayyazi2026pop
2. **Report ID and linked reports:** arXiv:2603.00324 (submitted 27 Feb 2026); abstract page read in full 2026-11-28. Single report known.
3. **Authors:** Arya Fayyazi, Haleh Akrami.
4. **Year:** 2026.
5. **Title:** Proof-of-Perception: Certified Tool-Using Multimodal Reasoning with Compositional Conformal Guarantees
6. **Venue and publication type:** arXiv preprint.
7. **DOI or arXiv ID and link:** arXiv:2603.00324; https://arxiv.org/abs/2603.00324
8. **Extractor and date:** swarm chair, 2026-11-28 (single extraction, dual extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Abstract read in full; full text not read in this pass.
11. **Eligibility confirmation:** Meets I1 (original method and evaluation), I2 (RQ4 calibration via per-node conformal sets; RQ1 typed set-valued outputs), I3 as background (no LAYA benchmark), I4 (2026), I5 (English), I6 (full text retrievable; read in part, declared in field 10).
12. **Paper role:** Background. Multimodal QA method; no misinformation task and no LAYA benchmark.
13. **Research question or stated aim:** How to give each step of a tool-using multimodal reasoning graph its own reliability certificate, and use those certificates to allocate compute (Abstract).
14. **Method and design:** Reasoning is cast as an executable graph; each perception or logic node outputs a conformal set, giving calibrated stepwise uncertainty; a lightweight controller uses the certificates to expand with extra tool calls only when needed and stop early otherwise (Abstract).
15. **System or model described:** Proof-of-Perception (PoP) framework over tool-using multimodal backbones; code linked from the paper (per search summary).
16. **Dataset(s) used:** Document, chart, and multi-image QA benchmarks (Abstract); specific names (DocVQA, TextVQA, InfographicVQA, ChartQA, MultiDoc2Dial) appear in the HTML full-text summary, not verified against the paper's tables in this pass.
17. **Dataset construction and labelling:** Established benchmarks used as supplied.
18. **Evaluation split:** Not stated in the abstract as read; conformal sets imply a calibration split, not described in the text read.
19. **Metrics and metric definitions:** Performance and reliability against chain-of-thought, ReAct-style, and program-of-thought baselines; exact metrics not stated in the abstract as read.
20. **Threshold, abstention and decision rule:** No abstention from answering; the conformal set size drives a compute decision (accept, retry at higher fidelity, or expand), which is an abstention-adjacent control rule, not a selective-prediction rule.
21. **Headline results (as reported):** Qualitative only in the abstract: improves performance and reliability over the named baseline classes while using computation more efficiently. No number is quoted in the abstract as read, and none is recorded here.
22. **Source of each headline result:** Abstract.
23. **Calibration results and method:** Method shown: split-conformal style sets per node with a learned nonconformity score and a per-node-type threshold, giving marginal coverage under exchangeability (full-text summary). No calibration number is recorded in this pass.
24. **Abstention and selective prediction results:** None reported as selective prediction; see field 20.
25. **Evidence retrieval: method and results:** Tools ground answers in verifiable perceptual traces (Abstract); no separate retrieval-quality metric in the text read.
26. **Key points relevant to LAYA:** (Shown) A conformal set can be attached per reasoning step, not only to the final verdict, and set size can drive a budget decision. (Inference, labelled) For LAYA this suggests auditing whether a per-head set, rather than the final head alone, predicts where the pipeline fails; that is a design idea, not evidence about LAYA numbers.
27. **Key points non-relevant but notable:** The controller turns uncertainty into a compute policy (expand or stop), a framing most calibration papers, which treat the set as a passive report, do not use.
28. **Authors' stated conclusions:** PoP grounds answers in verifiable evidence, reduces error compounding and hallucinations, and enables principled accuracy-compute trade-offs (Abstract).
29. **Limitations stated by the authors:** Not read in this pass.
30. **Limitations identified by the extractor:** No misinformation evaluation; compositional coverage across a graph depends on assumptions the abstract does not state; no number in this pass can support or challenge a LAYA claim.
31. **Funding and conflicts of interest:** Not reported in the text read.
32. **Code, data and materials availability:** Code repository linked from the paper per search summary; not verified in this pass.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection — not applicable to LAYA use. (b) Missing data — not applicable. (c) Measurement — some concerns: exact metrics not read. (d) Leakage — not assessable in this pass. (e) Deviations — not applicable: no LAYA protocol is followed or claimed.
34. **Overall quality judgement:** Some concerns, for design use only.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No LAYA benchmark and no recorded number; nothing may sit beside a LAYA number. Cited only for the per-node conformal certificate design.
37. **Discrepancies and unresolved disagreements:** Board pass (chair, 2026-11-28): proponent case (per-node certificates, compute allocated by set size, explicit guarantees) against the skeptic case (QA benchmarks only, composition assumptions unstated in the text read, no misinformation evidence). Outcome: Background only. One scoped design note recorded: a conformal set used as a control signal is a different claim from a conformal set used as a report, and each needs its own audit. No discrepancies in the text read.
