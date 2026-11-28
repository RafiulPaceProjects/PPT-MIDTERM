# Extraction — When Retrieval Is Not Enough (protocol v1.1, §4.2)

1. **Study ID:** Poikarayil2026obsolete
2. **Report ID and linked reports:** arXiv:2610.36308v1 (HTML full text, abstract through discussion read, 2026-11-27). Single report. Accepted at the NeurIPS 2026 Workshop on Personalized, Aligned, Long-Term Memory for AI Systems (PALM).
3. **Authors:** Oleeviya Babu Poikarayil, Tony Basil Babu, Abdulrahman Nahhas, Het Darshan Mehta, Jawid Ahmad Baktash, Ernesto William De Luca, Klaus Turowski.
4. **Year:** 2026 (submitted 26 Oct 2026).
5. **Title:** When Retrieval Is Not Enough: Obsolete Facts in Agent Memory
6. **Venue and publication type:** arXiv preprint, workshop paper (PALM, NeurIPS 2026).
7. **DOI or arXiv ID and link:** arXiv:2610.36308; https://arxiv.org/abs/2610.36308v1
8. **Extractor and date:** swarm chair, 2026-11-27 (single extraction, LLM-assisted; dual-extraction fallback declared per protocol §3.3/§4.1).
9. **Form version:** protocol v1.1 (2026-11-24)
10. **Extraction status:** Substantially complete for the main text (§§1 to 4 and Tables 1 to 2 read); appendices not read in this pass.
11. **Eligibility confirmation:** Meets I1 (original controlled evaluation), I2 (RQ5 evidence retrieval and version selection), I4, I5, I6.
12. **Paper role:** Background. Agent memory, not a LAYA benchmark, so no number enters the comparability table.
13. **Research question or stated aim:** When the correct update is retrieved, how do evidence budget, unrelated distractors, and an older competing fact affect whether a model uses it (§1).
14. **Method and design:** Three parts: a BM25 evidence-budget sweep (64 to 512 tokens), stratification by whether an obsolete competitor is present, and an equal-size paired intervention replacing one unrelated statement with the obsolete competitor while reader, prompt, latest fact and context size stay fixed (§§1, 2).
15. **System or model described:** Qwen2.5-7B-Instruct and Qwen3-14B readers over BM25 retrieval, temperature 0, seed 42 (§2).
16. **Dataset(s) used:** MemoryAgentBench FactConsolidation, Conflict_Resolution split: 6K history (455 statements, 100 questions; 74 with an older conflict, 26 without) and 32K history (2,310 statements, 100 questions) (§2).
17. **Dataset construction and labelling:** Synthetic chronological statements; higher numbers replace lower conflicting statements; the benchmark truth is the later synthetic statement, which can contradict ordinary world knowledge (§§1, 2).
18. **Evaluation split:** The two named histories above; the 74 conflict questions were also used for prompt development, so the intervention is a within-cohort paired comparison, not held-out confirmation (§2, stated by the authors).
19. **Metrics and metric definitions:** Accuracy by the benchmark normalized substring metric, with manual audit of semantic edge cases; paired exact McNemar tests used as diagnostics (§§2, 3).
20. **Threshold, abstention and decision rule:** No abstention rule; the frozen prompt instructs the reader to use only supplied numbered memories and treat higher-numbered conflicts as newer (§2).
21. **Headline results (as reported):** On 6K, accuracy falls monotonically from 45 percent at a 64-token budget to 32 percent at 512 tokens, although a gold-assisted audit finds the latest statement in every retrieved set. In the equal-size intervention, replacing one unrelated statement with the obsolete competitor drops Qwen2.5 from 100 to 44.6 percent and Qwen3-14B from 100 to 87.8 percent, and every harmful paired flip selects the stale value. The 32K replication shows the same direction, 69 versus 58 percent (Abstract, §§3.1 to 3.3).
22. **Source of each headline result:** Abstract, §3 and Tables 1 to 2 of arXiv:2610.36308v1, read 2026-11-27.
23. **Calibration results and method:** None reported.
24. **Abstention and selective prediction results:** None in the main design; an earlier abstaining-prompt experiment is in Appendix F, not read in this pass.
25. **Evidence retrieval: method and results:** BM25 over individual statements, restored to chronological order. Retrieval success and reader selection are measured separately: the latest statement is present in all retrieved sets at every budget, so the accuracy loss is a selection failure, not a retrieval failure (§§2, 3.1).
26. **Key points relevant to LAYA:** (Shown) Retrieval metrics and end-to-end accuracy can both hide the operative variable, which is the composition of the retrieved set: whether a superseded competitor is present beside the current version. (Shown) More evidence can hurt when the added evidence compounds an unresolved version conflict. (Inference) For LAYA evidence work, every frozen evidence set should log three separate fields: latest or decisive evidence present, superseded competitor present, and which version the verdict follows. That is the same separation StaleBench (already in the review) argues for, reached here by a controlled intervention rather than a benchmark audit.
27. **Key points non-relevant but notable:** Obsolete values in this benchmark often match familiar world knowledge while the synthetic updates contradict it, so the result establishes susceptibility to competitors, not that temporal obsolescence alone drives the effect (§4, stated by the authors).
28. **Authors' stated conclusions:** Retrieving an update does not guarantee a model will use it; memory systems should retire, down-weight, or explicitly mark superseded facts while preserving provenance (§4).
29. **Limitations stated by the authors:** Two Qwen-family models only, deterministic decoding, one synthetic benchmark, single-hop chains of length at most two, lexical retrieval only; gold-assisted audits are diagnostic, not deployable; questions share one history, limiting population-level interpretation (§4).
30. **Limitations identified by the extractor:** The 100 percent condition-A ceiling makes the intervention contrast unusually clean and may overstate the effect size available in noisier settings; appendices not read in this pass.
31. **Funding and conflicts of interest:** Not reported in the sections read.
32. **Code, data and materials availability:** Benchmark is MemoryAgentBench (prior work); run inventory in Appendix B, not read in this pass.
33. **Risk of bias and quality appraisal, by domain:** (a) Selection, Low concern: conflict status reconstructed for all 100 questions. (b) Missing data, Low concern: excluded runs documented in Appendix J per §4. (c) Measurement, Some concern: substring metric produced one false negative and one false positive in the authors' own manual audit; official scores kept and disclosed. (d) Leakage, Some concern by design and disclosed: intervention cohort also used for prompt development. (e) Deviations, Low concern: frozen prompt protects the paired contrast.
34. **Overall quality judgement:** Some concerns, mainly the disclosed prompt-development overlap and the single benchmark.
35. **Comparability verdict:** No, not comparable.
36. **Comparability scoping note:** No number from this paper may sit beside a LAYA number. Blocking differences: synthetic agent-memory task rather than NewsCLIPpings, VERITE or MMFakeBench veracity; reader accuracy over numbered statements; no shared split, metric or decision rule.
37. **Discrepancies and unresolved disagreements:** None found in the sections read. The paper's direction agrees with StaleBench (Murshed2026stalebench, already in sources) by an independent method, which is recorded as convergence, not as a settled LAYA claim.
