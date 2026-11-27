# Extraction — Evaluating the Robustness of Fact-Checking LLMs on Multilingual Evidence (protocol v1.1)

1. Study ID: Shah2026multilingual
2. Report ID: arXiv:2611.18623v1. No linked reports found.
3. Authors: Radhika Shah.
4. Year: 2026.
5. Title: Evaluating the Robustness of Fact-Checking LLMs on Multilingual Evidence
6. Venue: arXiv preprint (v1, submitted 17 Sep 2026); comments note Accepted at COLM Sci-FM 2026.
7. arXiv:2611.18623; https://arxiv.org/abs/2611.18623
8. Extractor: swarm chair, 2026-11-26 (single extraction, LLM-assisted; dual-extraction fallback declared).
9. Form version: protocol v1.1 (2026-11-24)
10. Status: Partial. Abstract read in full; full text not read in this pass.
11. Eligibility: I1 original evaluation, I2 RQ5 evidence retrieval and robustness, I3 background only, I4 arXiv 2026, I5 English, I6 full text retrievable, read in part and declared.
12. Role: Background. No NewsCLIPpings, VERITE, or MMFakeBench result.
13. Aim: Test how verdict accuracy holds up when evidence is corrupted and when it is in lower-resource languages.
14. Method: Gold evidence sets for 190 claims in each of English, German, Greek, and Romanian, built on EuroVerdict; four corruption strategies at two severity levels; rubric-based LLM-as-a-judge scores reasoning quality alongside verdict accuracy.
15. System: Fact-checking LLMs as tested; Llama 3.1 8B named in the headline result in the abstract.
16. Datasets: EuroVerdict-derived sets, 190 claims per language, four languages.
17. Construction: Established claims plus author-constructed gold evidence and corruptions; detail not read beyond abstract.
18. Split: Not read in this pass.
19. Metrics: Verdict accuracy, and judge scores for reasoning quality.
20. Decision rule: No abstention rule reported in the abstract.
21. Headline results (as reported): A misleading edit cut Llama 3.1 8B English accuracy from 80.00 percent to 16.84 percent; losses widen as language resource level decreases; machine-translating Greek and Romanian claims into English recovers much but not all of the low-resource gap; judge scores decline more slowly than accuracy.
22. Source: Abstract of arXiv:2611.18623v1, read 2026-11-26.
23. Calibration: None reported in the abstract.
24. Abstention: None reported in the abstract.
25. Evidence retrieval: Core. Evidence quality and language are the interventions; corrupted evidence drives large accuracy losses, and a reasoning judge under-detects that degradation.
26. Relevance to LAYA: (Shown, in its own setting) Evidence corruption can collapse accuracy even in English, and an LLM judge of reasoning quality declines more slowly than accuracy, so judge scores cannot substitute for verdict accuracy under corrupted evidence. (Inference, labelled) For LAYA, any judge-based audit on validation splits should be paired with a direct accuracy read, especially under evidence perturbation.
27. Notable non-relevant: Translation into English recovers much of the low-resource gap, a practical mitigation worth noting for multilingual deployment.
28. Authors' conclusions: Caution against deploying LLM fact-checkers on noisy multilingual evidence; datasets and code released.
29. Limitations stated by authors: Not read in this pass; recorded as not reported in sections read.
30. Extractor limitations: Partial read, abstract only.
31. Funding and conflicts: Not reported in sections read.
32. Availability: Authors state evidence datasets and evaluation code are released (abstract).
33. Risk of bias: (a) Selection, some concerns: headline is a single-model extreme drop, up-to style framing possible. (b) Missing data, cannot tell. (c) Measurement, some concerns: judge is an LLM rubric, itself shown to lag accuracy. (d) Leakage, cannot tell. (e) Deviations, cannot tell.
34. Overall: Some concerns, mainly partial read.
35. Comparability verdict: No, not comparable.
36. Scoping note: No number may sit beside a LAYA number: different datasets, text-only evidence setting, different models and decision rules. Method and risk evidence for RQ5 only.
37. Discrepancies: None found. Board pass (chair, 2026-11-26): proponent (controlled corruptions, four languages, accuracy and judge measured separately) against skeptic (single author, abstract-only, extreme single-model headline). Outcome: Background confirmed; judge-lags-accuracy point recorded as a finding; no comparator number recorded.
