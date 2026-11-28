# Extraction — System 1 Confidence Audit (protocol v1.1, §4.2)

1. **Study ID:** Delaunay2026system1audit
2. **Report ID and linked reports:** arXiv:2611.12521v1 (HTML full text, abstract, introduction and methods overview read, 2026-11-27). Single report.
3. **Authors:** Julien Delaunay.
4. **Year:** 2026.
5. **Title:** Can the Confidence and Decisions of System 1 Models Be Trusted? An Explainability and Perturbation Audit of Jev-Style Decision Models
6. **Venue and publication type:** arXiv preprint.
7. **DOI or arXiv ID and link:** arXiv:2611.12521; https://arxiv.org/html/2611.12521v1
8. **Extractor and date:** swarm chair, 2026-11-27 (single extraction, LLM-assisted; dual-extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Abstract, introduction, related work and methods overview read; results tables not read section by section in this pass.
11. **Eligibility confirmation:** Meets I1 (original audit and evaluation), I2 (RQ1 typed decisions, RQ4 calibration), I4, I5, I6.
12. **Paper role:** Background. No LAYA benchmark, no misinformation task, so no number enters the comparability table. Board-scoped this run (see run log): it touches the live claim family about System One confidence and calibration.
13. **Research question or stated aim:** Whether Jev-style System 1 confidence scores are genuinely calibrated, stable under label-preserving perturbations, free of cross-question interference when questions are bundled, and faithfully explainable by post-hoc attribution (Abstract, §1).
14. **Method and design:** Open deterministic audit benchmark: calibration under perturbations, bundled versus single question interference, and LOO, LIME, KernelSHAP and logit-link KernelSHAP (S1-SHAP) attribution faithfulness, with responses cached by weight digest (§§1, 3).
15. **System or model described:** Five open-weight System 1 models (Tev1-0.8B, Tev1-4B, Nimble-9B, Clef-Flash-9B, Clef-27B) against generative System 2 baselines (single-token log probability, structured JSON, chain-of-thought). Jev itself and LAYA are not evaluated.
16. **Dataset(s) used:** e-SNLI, HANS, synthetic clinical triage vignettes (N=900), Tensor Trust prompt injection (N=250), and an 86-case programmatic logic-gate suite (Abstract, §1).
17. **Dataset construction and labelling:** As reported in the sections read; the triage vignettes are synthetic and class-balanced.
18. **Evaluation split:** Named benchmark sets above; no LAYA split.
19. **Metrics and metric definitions:** Weighted ECE, Brier score, AUROC, recall at fixed false alarm, binary flip rate under bundling, attribution comprehensiveness and sufficiency style measures (§§1, 2).
20. **Threshold, abstention and decision rule:** No abstention rule of its own; the audit measures the models' returned distributions and confidence field.
21. **Headline results (as reported):** (1) The provider confidence field is an exact closed-form dispersion transform (1 minus H(p)/ln K on sub-10B models, normalized margin on Clef-27B), not empirical accuracy. (2) Bundling questions induces directional cross-question interference, 11.7 to 22.4 percent binary flips on Tev1-0.8B versus 0.1 to 0.2 percent on Tev1-4B. (3) System 1 models at 4B and above are better calibrated under adversarial syntactic shift (weighted ECE 0.030 to 0.087) than log probability (0.144) and structured JSON (0.378) baselines. (4) Prompt injection guardrail AUROC 0.988 to 0.998 at 48 to 60 ms. (5) Logit-link SHAP improves interaction recovery on disjunctive gates (Abstract).
22. **Source of each headline result:** Abstract and §1 of arXiv:2611.12521v1, read 2026-11-27.
23. **Calibration results and method:** Weighted ECE under label-preserving perturbations and adversarial syntactic shift (HANS); see field 21 item (3).
24. **Abstention and selective prediction results:** None reported in the sections read.
25. **Evidence retrieval: method and results:** No retrieval.
26. **Key points relevant to LAYA:** (Shown, in the audited models) A returned confidence field can be a dispersion transform of the distribution itself, not a measured accuracy; reading it as accuracy is a category error. (Shown, in the audited models) Bundled questions can interfere, and the size of the effect depends on architecture and training recipe, so bundling safety is per-model, never assumed. (Inference) For LAYA, any bundled multi-question call needs its own flip-rate diagnostic on frozen validation items before its outputs are pooled with single-question outputs.
27. **Key points non-relevant but notable:** Single-pass inference makes 512-coalition SHAP interactive (1.3 to 3.2 s per input), so attribution audits that are impractical on generative models are cheap on decision models.
28. **Authors' stated conclusions:** System 1 confidence can be trusted only after audit; the confidence field definition and bundling behavior are structural properties deployments must check (Abstract, §1).
29. **Limitations stated by the authors:** Not extracted in this partial pass.
30. **Limitations identified by the extractor:** Single author, independent researcher, v1 preprint, no replication; the audited models are decoder-style open weights, while LAYA's option-marker encoder design may not share the causal-ordering mechanism behind the interference result; partial read.
31. **Funding and conflicts of interest:** Not reported in the sections read.
32. **Code, data and materials availability:** Audit benchmark described as open and deterministic (§1); liveness not checked in this pass.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection, Some concern: model set is the available open-weight ecosystem, not a sample. (b) Missing data, Low concern in sections read. (c) Measurement, Low concern: confidence-field claim is an exact closed-form match, checkable by construction. (d) Leakage, Cannot tell in this pass. (e) Deviations, Cannot tell in this pass.
34. **Overall quality judgement:** Some concerns, driven by the partial read, single authorship and v1 status.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No number from this paper may sit beside a LAYA number. Blocking differences: no NewsCLIPpings, VERITE or MMFakeBench task; different models; audit metrics rather than verdict accuracy under a shared split and decision rule.
37. **Discrepancies and unresolved disagreements:** Board note: the interference mechanism the paper names (causal prompt ordering) is architecture-specific; it must not be recorded as a property of System One models in general.
