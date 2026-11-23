# Competitor & Research-Impact Analysis — LAYA-Vision Study
*Slice: research-impact measurement · Compiled 2026-11-22 · All citation figures sourced or marked UNVERIFIED. Semantic Scholar's API rate-limited (HTTP 429) during this pass; S2 counts below come from indexed snapshots (Liner/OpenAlex) and are flagged accordingly.*

## 1. The competitor set — who actually matches this study

| Paper | Venue | What it is | MMFakeBench number (their convention) | Citations |
|---|---|---|---|---|
| **MMFakeBench + MMD-Agent** (Liu et al.) | **ICLR 2025** (arXiv:2406.08772) | The benchmark itself + an LVLM agent framework (decompose → rationale → tool use) | GPT-4V Standard 51.0 val / 48.8 test; GPT-4V + MMD-Agent 61.6 val / 61.5 test; LLaVA-1.6-34B 25.7 → 49.9 | Liner snapshot: **27** cited-by — https://liner.com/review/mmfakebench-a-mixedsource-multimodal-misinformation-detection-benchmark-for-lvlms · S2 live count UNVERIFIED |
| **T²Agent** (Cui et al.) | **AAAI 2026 Oral** (arXiv:2505.19768) | Tool-augmented agent + Monte Carlo Tree Search, training-free, GPT-4o backbone | **F1 0.759 / Acc 0.753 (val)** — https://arxiv.org/pdf/2505.19768 | New (2025–26) — UNVERIFIED |
| **MM-VeriAgent** | arXiv (2025–26) | RL-trained tool use on Qwen2.5-VL-7B; no tool search at inference | Multi-class **F1 71.5**, Acc 70.4 (val table) — https://arxiv.org/pdf/2609.30698v1.pdf | New — UNVERIFIED |
| **SNIFFER** (Qi et al.) | **CVPR 2024** (arXiv:2403.03170) | Two-stage instruction-tuned InstructBLIP + internal/external checking, explainable OOC detection | NewsCLIPpings acc 88.4% (binary OOC task — different framing); VERITE True-vs-OOC 74.0% | Liner snapshot: **60** cited-by — https://liner.com/review/sniffer-multimodal-large-language-model-for-explainable-outofcontext-misinformation-detection · S2 live count UNVERIFIED |
| **NewsCLIPpings** (Luo, Darrell, Rohrbach) | **EMNLP 2021** (arXiv:2104.05893) | The OOC dataset paper (VisualNews-derived) | Fine-tuned CLIP 66.1% acc (Merged-Balanced) | OpenAlex: **54** cited_by_count — https://api.openalex.org/works/doi:10.18653%2FV1%2F2021.EMNLP-MAIN.545 · Liner snapshot says 102 (sources disagree; OpenAlex is the API figure) |
| **VERITE** (Papadopoulos et al.) | arXiv:2304.14133; **accepted IJMIR** per https://api.sciforum.net/events_files/1063/customs/0d28fea302c4bfeff8e841c4c24163ec.pdf | Bias-controlled benchmark (1,000 items) + CHASMA synthetic training | Published framing: 52.1% multiclass / 72.7% True-vs-OOC binary | UNVERIFIED (S2 API blocked this pass) |

**The honest competitive picture:** on MMFakeBench *validation*, the fine-tuned/agentic frontier has moved past LAYA's test number — T²Agent 75.9 and MM-VeriAgent 71.5 (both val, both frontier-model or RL pipelines with web tools). LAYA's **0.6020 is a TEST number** — the split T²Agent's headline table does not use the same way (its 0.759 is val; AgentM3D-lineage work evaluates on a 1,000-item val subset). Against the benchmark paper's own published TEST regime, LAYA sits: above GPT-4V Standard (48.8) by ~11 pp, ~1.3 pp below GPT-4V + MMD-Agent (61.5). No competitor reaches its number with a 201M model, 490 training examples, no web retrieval, and no frontier API at inference. That constraint profile — not the raw F1 — is the differentiator.

## 2. Where work of this scale actually lands

**Workshops (the natural home):**
- **CheckThat!** (CLEF lab) — shared-task + working-notes culture (CEUR proceedings); rewards system papers, error analysis, reproducibility. https://test.dblp.org/db/conf/clef/clef2025w.html
- **CONSTRAINT** (AAAI workshop, Springer CCIS proceedings; extensions invited to a Neurocomputing special issue) — fake-news/hostility detection community. https://constraint-shared-task-2021.github.io/
- **WOAH** (ACL/NAACL/EMNLP workshop, ACL Anthology; 9th ed. ACL 2025: 72 archival submissions, ~53% accepted; 10th ed. EMNLP 2026, Budapest) — explicitly welcomes dataset-bias/limitations and evaluation-methodology papers, which is this study's second half. https://www.thewoah.org/2026/

**Journals (the realistic journal ladder):**
- **Expert Systems with Applications** — IF **9.4** (2025 JCR; https://en.wikipedia.org/wiki/Expert_Systems_with_Applications ; CiteScore 15.0–17.0 per ScienceDirect) — the reach target; selective, wants a clear methodological advance.
- **Multimedia Tools and Applications** — IF ~3.0 — a well-worn home for applied multimodal-detection papers.
- **IEEE Access** — IF ~3.4 (dated CV-sourced figure; treat as approximate) — fast, broad, APC-based.
- **PLOS ONE / PeerJ Computer Science** — soundness-over-novelty review; exact current IFs UNVERIFIED this pass. PLOS ONE in particular is a legitimate home for a rigorous negative/conditional result with full artifacts.

## 3. What distinguishes cited from ignored in this space

Reading the citation pattern above: the papers that accumulate citations are (1) **benchmarks/datasets** (MMFakeBench, NewsCLIPpings, VERITE — every later paper must cite them), (2) **the first credible method on a new benchmark** (MMD-Agent rode its own benchmark; T²Agent is positioned to do the same), and (3) **warning/measurement papers** that change how others evaluate (VERITE's unimodal-bias finding is cited by method papers — SNIFFER's supplement, RED-DOT — precisely because it tells them their numbers might be wrong). Pure "we fine-tuned X on Y for +Z points" papers without one of those three hooks are the ignored majority. Reproducibility artifacts (code, checkpoints, executed notebooks) correlate with the method papers that *do* get built on — T²Agent and MM-VeriAgent both ship GitHub repos (https://github.com/cuixing100876/T2Agent).

## 4. Sober placement of the LAYA study

Assets: (a) 0.6020 test F1 at 201M/490-examples/no-retrieval; (b) pre-registered hypotheses, single scored test pass; (c) verified calibration-transfer finding (temperature fitted on one distribution degrades ECE on another — held-out proven); (d) **0.9150 metadata-leakage ceiling** (a source-metadata rule nearly solves tune — a benchmark-integrity warning in VERITE's lineage); (e) a full reproducibility record (executed notebook, 25+ receipts, cost ledger).

**Verdict: a solid workshop paper with one top-decile asset — not a top-decile paper as a whole.** The F1 result alone is incremental against the 2025–26 agentic frontier. The pre-registration + single-test-pass discipline is rarer than the field admits and reviewers at CheckThat!/WOAH will credit it. The leakage ceiling (d) is the asset with genuine citation potential: it is a *warning about the benchmark itself*, the category of contribution this field demonstrably cites. The calibration-transfer finding (c) is a respectable second hook (deployment-relevant, counterintuitive, verified).

## 5. The single strongest impact lever

**Split the leakage finding out as its own short benchmark-warning paper/preprint, fast, with the artifact attached.** Rationale: warnings get cited by every subsequent MMFakeBench user (the VERITE precedent); the main paper's F1 will be superseded within a year, the warning will not. Concretely: arXiv the main paper and the warning note together (same week), ship the Hugging Face Space + checkpoints + executed notebook as the artifact bundle, and target the warning note at WOAH/CheckThat! and the main paper at the journal ladder (MTAP → ESWA reach). Timing matters: MMFakeBench is ICLR-2025-fresh and its user base is forming now — a warning published while the benchmark is being adopted gets cited by the adopters.

*Sources: arXiv/ICLR/CVPR/AAAI records and OpenAlex/Liner snapshots as linked inline. Any figure not linked above is marked UNVERIFIED and was not used in the assessment.*
