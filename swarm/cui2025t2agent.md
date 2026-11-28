# Extraction — T2Agent: A Tool-augmented Multimodal Misinformation Detection Agent with Monte Carlo Tree Search (protocol v1.1, §4.2)

1. **Study ID:** Cui2025t2agent
2. **Report ID and linked reports:** arXiv:2505.19768v2 (submitted 26 May 2025, revised 17 Nov 2025); abstract page read in full 2026-11-28, plus a secondary paper-note summary of its results tables. AAAI 2026 Oral per the secondary note, not verified from the arXiv page.
3. **Authors:** Xing Cui, Yueying Zou, Zekun Li, Peipei Li, Xinyuan Xu, Xuannan Liu, Huaibo Huang.
4. **Year:** 2025 (v2 Nov 2025).
5. **Title:** T2Agent: A Tool-augmented Multimodal Misinformation Detection Agent with Monte Carlo Tree Search
6. **Venue and publication type:** arXiv preprint v2; AAAI 2026 Oral per secondary note (unverified in this pass).
7. **DOI or arXiv ID and link:** arXiv:2505.19768; https://arxiv.org/abs/2505.19768
8. **Extractor and date:** swarm chair, 2026-11-28 (single extraction, dual extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Abstract read in full; results numbers come from a secondary summary, not the paper's own tables, and are quarantined (field 37).
11. **Eligibility confirmation:** Meets I1 (original system with results), I2 (RQ2 MMFakeBench; RQ5 tool-based evidence), I3 as comparator candidate only (dataset and metric named in secondary summary; split and decision rule differ from LAYA, see fields 35-36), I4 (2025), I5 (English), I6 (full text retrievable; read in part, declared in field 10).
12. **Paper role:** Background, comparator candidate. Basis: board pass 2026-11-28 (field 37) quarantined its numbers.
13. **Research question or stated aim:** How to verify mixed-source multimodal misinformation with dynamic reasoning instead of a static pipeline (Abstract).
14. **Method and design:** Training-free agent: an extensible toolkit (web search, forgery detection, consistency analysis) with standardized tool templates; a greedy selector picks a task-relevant tool subset as the MCTS action space; MCTS is extended with multi-source verification, decomposing detection into subtasks per forgery source; a dual reward (reasoning trajectory score plus confidence score) balances exploration and exploitation (Abstract).
15. **System or model described:** As field 14; backbone MLLMs vary (GPT-4o, GPT-4o-mini, GPT-4.1-nano per secondary summary).
16. **Dataset(s) used:** MMFakeBench and AMG (Abstract and secondary summary).
17. **Dataset construction and labelling:** Inherited benchmarks, not built by the authors.
18. **Evaluation split:** MMFakeBench test set per secondary summary; not confirmed from the paper's own tables in this pass.
19. **Metrics and metric definitions:** F1 and accuracy per secondary summary; whether F1 is macro-F1 as LAYA defines it is not confirmed.
20. **Threshold, abstention and decision rule:** No abstention. Decision is the MCTS-selected verification path's verdict; confidence enters only as a reward term.
21. **Headline results (as reported, QUARANTINED):** Secondary summary reports MMFakeBench F1 0.759 and accuracy 0.753 with GPT-4o, against MMD-Agent 0.614 / 0.616. A separate included paper (MM-VeriAgent extraction) tabulates T2Agent (GPT-4o) at 75.3 / 75.9 on the MMFakeBench test partition under its own framing. The two secondary sources do not agree exactly, which is itself a reason the numbers stay quarantined until read from the paper's tables.
22. **Source of each headline result:** Secondary paper-note summary and the MM-VeriAgent extraction, not the T2Agent tables. No number from this extraction may sit beside a LAYA number.
23. **Calibration results and method:** None reported in the text read. Confidence is a search reward, not a calibrated probability.
24. **Abstention and selective prediction results:** None. The agent always decides.
25. **Evidence retrieval: method and results:** Web search is one tool among several, chosen by the selector and MCTS; no separate retrieval-quality metric is reported in the text read.
26. **Key points relevant to LAYA:** (Shown from Abstract) Search over verification paths, with a confidence-bearing reward, beats a fixed sequential agent pipeline on the authors' benchmarks. (Inference, labelled) This is an inference-time compute design, the opposite end of the cost scale from LAYA's small fitted heads; any comparison is a cost-and-protocol comparison, not a head-to-head score comparison.
27. **Key points non-relevant but notable:** Tool descriptions use standardized templates so new tools can be added without redesigning the agent, a modularity point independent of misinformation.
28. **Authors' stated conclusions:** T2Agent consistently outperforms existing baselines on mixed-source multimodal misinformation benchmarks as a training-free detector (Abstract).
29. **Limitations stated by the authors:** Not read in this pass.
30. **Limitations identified by the extractor:** Headline numbers not yet read from the paper itself; two secondary sources disagree slightly; API-backbone cost is material (secondary summary lists hundreds of dollars per benchmark run for the GPT-4o agent baseline class) and is not comparable to LAYA's local fitted cost basis.
31. **Funding and conflicts of interest:** Not reported in the text read.
32. **Code, data and materials availability:** Code repository named in the secondary summary; not verified in this pass.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection — some concerns: benchmark-only evaluation. (b) Missing data — not applicable as read. (c) Measurement — high concern for comparator use until fields 18-19 are read from the paper. (d) Leakage — training-free, so no fitted leakage; backbone pretraining exposure to the benchmark cannot be ruled out from the text read. (e) Deviations — not assessable in this pass.
34. **Overall quality judgement:** Some concerns; usable as Background only in this pass.
35. **Comparability verdict:** No, not comparable as extracted.
36. **Comparability scoping note:** Numbers quarantined. Split, F1 definition, and decision rule (training-free MCTS agent on a commercial backbone versus LAYA's fitted small heads, four-class macro-F1) do not line up field by field, and the numbers were not read from the paper's own tables.
37. **Discrepancies and unresolved disagreements:** Board pass (chair, 2026-11-28): proponent case (direct MMFakeBench follow-up, training-free, ablations named in the Abstract) against the skeptic case (numbers only from secondary sources that disagree, 0.759/0.753 versus 75.3/75.9; protocol and backbone class unlike LAYA; cost basis unlike LAYA). Outcome: Background, comparator candidate, numbers quarantined. No LAYA claim is changed by this paper in this pass.
