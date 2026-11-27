# Extraction — ReMMD (protocol v1.1, §4.2)

1. **Study ID:** Dang2026remmd
2. **Report ID and linked reports:** arXiv:2606.24112v2 (PDF text opened, 2026-11-27). Single report.
3. **Authors:** Chenhao Dang, Dantong Zhu, Jun Yang, Conghui He, Weijia Li.
4. **Year:** 2026.
5. **Title:** ReMMD: Realistic Multilingual Multi-Image Agentic Verification for Multimodal Misinformation Detection
6. **Venue and publication type:** arXiv preprint.
7. **DOI or arXiv ID and link:** arXiv:2606.24112; https://arxiv.org/pdf/2606.24112
8. **Extractor and date:** swarm chair, 2026-11-27 (single extraction, LLM-assisted; dual-extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Partial. Abstract, introduction, related work and benchmark design read; full results tables not read in this pass.
11. **Eligibility confirmation:** Meets I1 (original benchmark and system), I2 (RQ2 benchmark standing, RQ5 evidence), I4, I5, I6.
12. **Paper role:** Background. ReMMDBench is a new benchmark, not a LAYA benchmark; its MMFakeBench mention is a competitiveness note, not a reported LAYA-comparable result in the sections read, so no number enters the comparability table.
13. **Research question or stated aim:** Existing benchmarks isolate short captions, single images, binary labels or one manipulation source; can a benchmark and agent match real posts: long multilingual narratives, several images, mixed provenance and subtle cross-modal framing errors (Abstract).
14. **Method and design:** ReMMDBench: 500 samples, 2,756 images, five monolingual evaluations, two cross-lingual settings, three text-length tiers, five-way veracity labels, eight distortion labels, evidence provenance and rationales, with yearly refresh. ReMMD-Agent decomposes posts into atomic points, builds a reusable persistent evidence set, and predicts structured verdicts, distortion diagnoses and rationales (Abstract, Table 2).
15. **System or model described:** ReMMD-Agent with GPT-5.2 as the headline backbone; also compared against proprietary systems, open LVLMs, MMD-Agent and T2-Agent (Abstract).
16. **Dataset(s) used:** ReMMDBench (own benchmark, 500 samples); MMFakeBench named only for a competitiveness note in the sections read.
17. **Dataset construction and labelling:** Seed posts scraped from Weibo, X, WeChat and international fact-check centres, then transformed by an automated multi-agent pipeline (Planner, Text, Search and Image workers) into controlled samples with prescribed veracity, distortion, language and visual budget, validated against evidence and provenance before inclusion (§Benchmark Design, Figure 2).
18. **Evaluation split:** Not stated in the sections read.
19. **Metrics and metric definitions:** Five-way veracity accuracy and macro-F1; cost relative to baselines (Abstract).
20. **Threshold, abstention and decision rule:** No abstention in evaluation as reported in the sections read.
21. **Headline results (as reported):** ReMMD-Agent with GPT-5.2: 41.80 percent accuracy and 39.12 percent macro-F1 on five-way veracity, at 17.5 percent lower cost than MMD-Agent and 79.9 percent lower than T2-Agent (Abstract).
22. **Source of each headline result:** Abstract of arXiv:2606.24112v2, read 2026-11-27.
23. **Calibration results and method:** None reported in the sections read.
24. **Abstention and selective prediction results:** None reported in the sections read.
25. **Evidence retrieval: method and results:** The agent retrieves web, image and social evidence into a persistent, reusable memory bank; reuse is presented as the cost saving mechanism. No separate retrieval quality result in the sections read.
26. **Key points relevant to LAYA:** (Shown) Typed, structured output is the direction of travel: five-way veracity plus eight distortion labels plus a rationale, not a binary label. (Shown) Evidence reuse across claims in one post is a cost lever LAYA does not currently price. (Inference) ReMMDBench is a candidate future external check, not a replacement for the three LAYA datasets, and would need its own registered split discipline before any use.
27. **Key points non-relevant but notable:** Benchmark construction by transforming real seed posts with a multi-agent pipeline, with yearly refresh to reduce contamination, is a notable shift from static scraped benchmarks. Most samples contain an AI-touched image (384 of 500 have at least one).
28. **Authors' stated conclusions:** ReMMD-Agent sets the best ReMMDBench result and remains competitive on MMFakeBench (Abstract, Introduction).
29. **Limitations stated by the authors:** Not stated in the sections read.
30. **Limitations identified by the extractor:** Partial read; small benchmark (500 samples); benchmark items are pipeline-transformed, so realism is constructed, not observed; five-way labels are not lineable against LAYA binary or three-way verdicts.
31. **Funding and conflicts of interest:** Not reported in the sections read.
32. **Code, data and materials availability:** Project page https://dang-ai.github.io/ReMMD as printed in the abstract; liveness not checked in this pass.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection, Some concerns: the authors evaluate their own agent on their own benchmark. (b) Missing data, Cannot tell in this pass. (c) Measurement, Low concern: accuracy and macro-F1 named for the headline result. (d) Leakage, Some concerns: yearly refresh is claimed to reduce contamination, not demonstrated in the sections read. (e) Deviations, Cannot tell in this pass.
34. **Overall quality judgement:** Some concerns, driven by the partial read and the own-benchmark evaluation.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No number from this paper may sit beside a LAYA number. Blocking differences: ReMMDBench five-way veracity on multi-image multilingual posts rather than NewsCLIPpings, VERITE or MMFakeBench splits; no shared metric definition or decision rule in the sections read.
37. **Discrepancies and unresolved disagreements:** None found in the sections read. The MMFakeBench competitiveness claim carries no number in the sections read and is recorded as a claim only, not a result.
