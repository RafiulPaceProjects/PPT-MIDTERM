# Extraction — Tail-CRC / Decoupling Solving from Abstention (protocol v1.1, §4.2)

1. **Study ID:** Chen2026tailcrc
2. **Report ID and linked reports:** arXiv:2611.31065v1 (HTML full text opened, 2026-11-27). Single report.
3. **Authors:** Qianyi Chen, Bo Li.
4. **Year:** 2026 (submitted 23 Nov 2026).
5. **Title:** Decoupling Solving from Abstention: Single-Rollout Conformal Risk Control for Hard-Budget LLM Reasoning
6. **Venue and publication type:** arXiv preprint.
7. **DOI or arXiv ID and link:** arXiv:2611.31065; https://arxiv.org/abs/2611.31065
8. **Extractor and date:** swarm chair, 2026-11-27 (single extraction, LLM-assisted; dual-extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Abstract and Sections 1 to 3 read; results tables beyond Figure 1 and Table 2 references not read section by section in this pass.
11. **Eligibility confirmation:** Meets I1 (original method and evaluation), I2 (RQ3 abstention, RQ4 calibration), I4, I5, I6.
12. **Paper role:** Background. Math reasoning under token budgets, no LAYA benchmark, so no number enters the comparability table.
13. **Research question or stated aim:** Under a hard token budget, can solving and abstention be decoupled so a frozen solver gains finite-sample control of wrong submissions from a single rollout (Abstract, §1).
14. **Method and design:** Two stages. Stage 1: RL with pure binary correctness rewards adapts the solver to budget forcing. Stage 2: solver frozen; conformal risk control on an upper-tail token-surprise score over the answer span (mean of the largest 10 percent of token surprises) sets the submission cutoff. Theory covers penalty-induced exploration starvation and length-induced ranking reversal in summed scores (§§2, 3).
15. **System or model described:** Tail-CRC over Qwen3.5-4B and Qwen3-8B; score from returned token log probabilities only; no auxiliary verifier (§1).
16. **Dataset(s) used:** DAPO (TEST500) and Omni-MATH (TEST300), 4K and 8K token budgets (§1, Figure 1).
17. **Dataset construction and labelling:** Not reported in the sections read.
18. **Evaluation split:** Named test sets above; calibration on labeled families separate from test, one rollout per family (§2).
19. **Metrics and metric definitions:** Coverage, correct and wrong submission rates, net score R minus W, precision, selective error; risk target is expected marginal wrong-submission rate, distinct from error conditional on submission (§2).
20. **Threshold, abstention and decision rule:** Submit iff the candidate is valid and its tail score is below a cutoff chosen by conformal risk control at target alpha (0.065 in Figure 1); invalid or empty spans get score plus infinity and are never submitted (§2).
21. **Headline results (as reported):** 50 RL updates on 400 problems raise correct submissions by 15.0 to 29.6 points on DAPO and 4.3 to 12.8 points out of domain on Omni-MATH over inference-only budget forcing; on 8B Omni-MATH, target-domain calibration cuts wrong submissions from 30.3 percent to 5.8 percent at 4K and from 41.8 percent to 6.5 percent at 8K (Abstract).
22. **Source of each headline result:** Abstract and §1 of arXiv:2611.31065v1, read 2026-11-27.
23. **Calibration results and method:** Conformal risk control on the frozen solver; recalibration to a new risk target or domain needs only a few hundred labeled target problems and no retraining (§§1, 3).
24. **Abstention and selective prediction results:** On DAPO at 4K, Tail-CRC submits more overall than budget forcing and penalty RL (41.0 vs 39.2 and 39.6 percent coverage) with fewer wrong submissions (7.1 vs 10.6 and 10.2 percent), so the gain is not trivial extra abstention (§1).
25. **Evidence retrieval: method and results:** No retrieval. Not applicable beyond noting the score uses only the model's own rollout.
26. **Key points relevant to LAYA:** (Shown) Solving and submission control can be separated: freeze the generator, calibrate the gate alone, and the risk guarantee survives a change of target or domain by recalibration only. (Shown) Summed negative log likelihood over a span carries a length multiplier that can invert rankings; a tail-mean score removes that factor. Any LAYA gate built on summed scores inherits the same risk. (Inference) For LAYA, a gate change should be treated as a calibration event on a frozen screen, not as a model change.
27. **Key points non-relevant but notable:** Wrong-answer penalties in group-relative RL create failure-only comparisons and can starve exploration; caution is better added after training than inside the reward.
28. **Authors' stated conclusions:** Decoupled solving and single-rollout calibration give a practical path to reliable, efficient budgeted reasoning (Abstract).
29. **Limitations stated by the authors:** The guarantee holds under exchangeability; out-of-domain use needs target-domain recalibration (§§1, 2).
30. **Limitations identified by the extractor:** Partial read; math answers with exact equivalence checking, not veracity verdicts; single-rollout token scores may not exist for LAYA's typed small models in the same form; v1 preprint, no replication.
31. **Funding and conflicts of interest:** Not reported in the sections read. Corresponding author at Tsinghua University.
32. **Code, data and materials availability:** GitHub and Hugging Face links shown on the arXiv page; liveness not checked in this pass.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection, Low concern: penalty and explicit-abstain baselines reported alongside, including after matched post-hoc calibration. (b) Missing data, Low concern: no-submission is an explicit outcome class counted in coverage. (c) Measurement, Low concern: marginal risk and selective error are defined separately in §2. (d) Leakage, Cannot tell in this pass. (e) Deviations, Low concern: failure modes of rival scores are derived and shown, not hidden.
34. **Overall quality judgement:** Some concerns, driven by the partial read and v1 status.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No number from this paper may sit beside a LAYA number. Blocking differences: math reasoning tasks rather than NewsCLIPpings, VERITE or MMFakeBench veracity; token-budget submission rather than verdict accuracy; no shared split or decision rule.
37. **Discrepancies and unresolved disagreements:** None found in the sections read.
