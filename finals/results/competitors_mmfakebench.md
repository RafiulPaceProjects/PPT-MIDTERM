# MMFakeBench Competitive Landscape — Scout Report (MMFakeBench slice)

**Compiled:** 2026-11-22 (ET) · **Scout slice:** every paper found that reports MMFakeBench numbers
**Study being benchmarked (the "LAYA study"):** LAYA-Vision, a 201M-parameter typed-decision VLM, fine-tuned on **490 examples**, evaluated on the **official MMFakeBench TEST set (10,000 items), 4-class macro-F1 = 0.6020**, single scored pass; its own zero-shot baseline on the same protocol = 0.2037.

---

## ⚠️ READ FIRST — there are at least SIX different "MMFakeBench numbers" in the literature, and most are not comparable

MMFakeBench officially has exactly two splits: **validation = 1,000 items** and **test = 10,000 items** (benchmark paper, §3/§5). The headline metric of the benchmark is **4-class macro-F1** (Real / Textual Veracity Distortion / Visual Veracity Distortion / Cross-modal Consistency Distortion). Later papers report numbers under at least six different protocols:

| Code | Protocol | Used by |
|---|---|---|
| **A** | Official **TEST** (10,000), 4-class macro-F1 | Benchmark paper; SCPO (Thinking as Society) |
| **B** | Official **VAL** (1,000), 4-class macro-F1 | Benchmark paper |
| **C** | The same 1,000 val items used as the *de facto* eval set by agent papers (composition 300 Real / 300 TVD / 100 VVD / 300 CCD), 4-class macro-F1 | T2Agent, AgentM3D, LRQ-FACT (as reported by T2Agent) |
| **D** | **Private re-split: 10,000 train / 1,000 eval** drawn from the 11,000-item pool — NOT the official test set | MM-VeriAgent (and every baseline in its Table 3) |
| **E** | **BINARY** (real vs fake) F1 — a different, much easier task | MERIT/MIRAGE headline numbers |
| **F** | Stratified **5,000-item subsample (50%) of the test set**, binary F1 | MERIT/MIRAGE "test" number |

**Only Protocol A numbers are directly comparable to the LAYA study's 0.6020.** Every entry below is labelled with its protocol code. Any ranking that mixes codes is meaningless.

A second trap: **answer-extraction mode.** The SCPO paper reports each model twice — "Top-1" parsing and "Recall" parsing (credit if the gold label appears anywhere in the response). Recall-mode numbers are systematically ~7–9 points higher and are the ones other papers (MM-VeriAgent) quote for SCPO. They are labelled below.

---

## The LAYA study's position, in one paragraph

On the only fully comparable protocol (A: official test, 4-class macro-F1), the LAYA study's **0.6020** sits **above every fine-tuned model ever reported on this protocol** (SCPO Top-1 0.573; DeceptionDecoded-transfer 0.5866 with split unverified) and **above GPT-4V zero-shot standard prompting (0.488)**, and **1.3 points below GPT-4V wrapped in the MMD-Agent framework (0.615)** — a frontier proprietary model with an agent scaffold, versus a 201M open model fine-tuned on 490 examples with no tools, no retrieval, and no test-time search. All higher numbers in the literature (0.66–0.82) come from non-comparable protocols: validation-subset evaluation, a private re-split, Recall-mode answer extraction, or binary classification.

---

## RANKED COMPETITORS (by closeness to the LAYA study: fine-tuned + Protocol A first)

### 1. SCPO — "Thinking as Society: Multi-Social-Agent Self-Distillation for Multimodal Misinformation Detection"
- **Authors / venue:** Yifei Gao, Ning Xu, Wenhui Li, Hongshuo Tian, Lanjun Wang, An-An Liu (Tianjin University) — **ICLR 2026**.
- **Method (one line):** Simulated society of MLLM agents generates Social Chain-of-Thought (SCoT) data; the model is then aligned with SCPO, a preference-optimization variant that weights training by "social correction value."
- **Base model:** Qwen2-VL-**7B** (35× the LAYA model's size).
- **Training data:** SCoT data synthesized from a curated multi-source pool aggregated from *other* benchmarks (NewsCLIPpings, DGM4, AutoSplice, FineFake) — MMFakeBench itself is eval-only for them. Exact SCoT sample count **UNVERIFIED** from sources opened.
- **MMFakeBench numbers — Protocol A (official TEST set), open prompting, LLM-parsing:**
  - **Top-1 extraction: macro-F1 57.3, Accuracy 59.2** (Precision 58.0, Recall 62.4)
  - Recall extraction: macro-F1 66.1, Accuracy 66.0 — ⚠️ *different extraction mode; this is the figure MM-VeriAgent quotes for SCPO*
  - Base Qwen2-VL-7B, same protocol, Top-1: F1 37.8 / Acc 41.0; Recall: F1 49.2 / Acc 50.8
- **Comparability:** ✅ Closest competitor in the literature — a *trained* model on the *official test set* with *4-class macro-F1*. On the like-for-like Top-1 reading, **LAYA 0.6020 beats SCPO by +2.9 points** with a 35× smaller model and a far smaller, in-domain training set (490 vs a multi-benchmark synthetic corpus).
- **Sources:** https://proceedings.iclr.cc/paper_files/paper/2026/file/54dd78de6883c365bd17a930941e48f3-Paper-Conference.pdf (Table 2 + §4.2 text "59.2% accuracy"); summary at https://en.papernotes.org/ICLR2026/multimodal_vlm/thinking_as_society_multi-social-agent_self-distillation_for_multimodal_misinfor/

### 2. DeceptionDecoded transfer — "Seeing Through Deception: Uncovering Misleading Creator Intent in Multimodal News with Vision-Language Models"
- **Authors / venue:** Jiaying Wu, Fanxiao Li, Zihang Fu, Min-Yen Kan, Bryan Hooi (NUS) — **ICLR 2026**.
- **Method (one line):** A benchmark of 12,000 intent-labelled synthetic news items; as a utility experiment, models are full-fine-tuned on it and transferred to external MMD benchmarks.
- **Base models:** Qwen2.5-VL-**7B** and LLaVA-v1.6-**7B**.
- **Training data:** **6,000 DeceptionDecoded samples** (out-of-domain; the fine-tuning task itself is *binary* misleading-intent Yes/No, answer-only supervision, 1 epoch).
- **MMFakeBench numbers (their Table 6, macro-F1 %):**
  - Qwen2.5-VL-7B: 27.96 (zero-shot) → **58.66** after fine-tuning (+30.70)
  - LLaVA-v1.6-7B: 44.41 → 52.37 (+7.96)
  - ⚠️ **Which MMFakeBench split was evaluated is UNVERIFIED** from the sources opened, and the eval protocol details (prompting/extraction) are not stated in the extracted text. Treat 58.66 as *probably* test-set macro-F1 but not confirmed.
- **Comparability:** 🟡 Fine-tuned-model framing matches the LAYA study (this is the only other "train a VLM, report MMFakeBench macro-F1" result found). If the split is the official test, **LAYA 0.6020 beats it by +3.5 points** — with 12× less training data (490 vs 6,000), in-domain rather than transfer data, and a 35× smaller model.
- **Sources:** https://proceedings.iclr.cc/paper_files/paper/2026/file/262ba7d20578417435414ce00e69fb12-Paper-Conference.pdf (Table 6); https://en.papernotes.org/ICLR2026/multimodal_vlm/seeing_through_deception_uncovering_misleading_creator_intent_in_multimodal_news/

### 3. The benchmark paper's zero-shot rows — "MMFakeBench: A Mixed-Source Multimodal Misinformation Detection Benchmark for LVLMs" (incl. MMD-Agent)
- **Authors / venue:** Xuannan Liu, Zekun Li, Peipei Li, Shuhan Xia, Xing Cui, Linzhi Huang, Huaibo Huang, Weihong Deng, Zhaofeng He — **ICLR 2025**, arXiv:2406.08772.
- **Method (one line):** The benchmark itself (11,000 pairs; 1,000 val / 10,000 test); 15 LVLMs evaluated zero-shot under standard prompting (SP), plus the authors' MMD-Agent framework (three-stage decomposed tool-augmented reasoning over a frozen LVLM).
- **Training data:** none (zero-shot).
- **MMFakeBench numbers — Table 2 of the paper, macro-F1 % / Accuracy %:**

| Model | Framing | VAL F1 | VAL Acc | TEST F1 | TEST Acc |
|---|---|---|---|---|---|
| GPT-4V | Standard prompting | 51.0 | 54.0 | **48.8** | 54.2 |
| GPT-4V | MMD-Agent framework | 61.6 | 62.1 | **61.5** | 61.0 |
| LLaVA-1.6-34B | Standard prompting | 25.7 | 40.4 | 25.4 | 40.5 |
| LLaVA-1.6-34B | MMD-Agent | 49.9 | 48.7 | 47.7 | 46.6 |
| LLaVA-1.6-13B | MMD-Agent | 38.0 | 40.6 | 34.5 | 37.4 |
| BLIP-2 (FlanT5-XXL) | MMD-Agent | 31.6 | 34.4 | 28.8 | 32.1 |
| LLaVA-1.6-7B | Standard prompting | 17.4 | 30.8 | 19.0 | 32.3 |

- **Comparability:** ✅ Protocol A/B exactly — these are the canonical reference numbers. **LAYA 0.6020 (test) beats GPT-4V Standard by +11.4 points and every open-source zero-shot row by ≥ +12 points; it trails only GPT-4V + MMD-Agent (0.615) by −1.3 points.** Note the benchmark paper also reports a *binary* table (its Table 6) — e.g. GPT-4V + MMD-Agent binary F1 74.0 on val — which is the number agent papers later quote as if it were the headline (see MERIT below).
- **Source:** https://arxiv.org/html/2406.08772v2 (Table 2; split definition §3/§5.1)

### 4. MM-VeriAgent — "Learning to Use Extensive Tools to Verify Multimodal Misinformation with Reinforcement Learning"
- **Authors / venue:** Peipei Li, Shuhan Xia, Shengyang Liu, Zekun Li, Ran He — arXiv:2609.30698 (Sep 2026, v2 Nov 2026).
- **Method (one line):** SFT + GRPO reinforcement learning teaches a VLM to operate an extensive verification toolkit (MM-VeriTools), with a Tool-Execution Cache to make RL rollouts affordable; no search at inference.
- **Base model:** Qwen2.5-VL-**7B**.
- **Training data:** **10,000 samples** — 8,000 for SFT (rollouts generated by a GPT-5-mini teacher) + 2,000 for GRPO.
- **MMFakeBench numbers — ⚠️ Protocol D (private re-split):** the paper states verbatim *"We use 10,000 samples for training and 1,000 samples for testing"* — i.e., it re-splits the 11,000-item pool and trains on 10,000 of them. Its "test" is **not** the official test set. On that 1,000-item eval:
  - **MM-VeriAgent: multi-class Acc 70.4, macro-F1 71.5**; binary Acc 83.2, binary F1 85.1
  - Baselines reproduced in the same table (same re-split eval): T2Agent (GPT-4o) multi Acc 75.3 / F1 75.9; SCPO multi Acc 66.0 / F1 66.1 (= SCPO's Recall-mode numbers, see entry 1); MMD-Agent (GPT-4V) multi Acc 62.1 / F1 61.6, binary F1 74.0; Gemini-2.5-Pro direct multi Acc 69.8 / F1 69.5; GPT-5.5 direct multi Acc 71.8 / F1 69.0; GPT-4o direct multi Acc 60.9 / F1 49.2; Qwen2.5-VL-7B direct multi Acc 34.3 / F1 25.0.
  - 🔎 *Forensic note:* several of these reproduced values coincide exactly with official **validation-set** numbers from the benchmark paper (MMD-Agent GPT-4V F1 61.6 = val, not test 61.5), which is consistent with the 1,000-item eval being drawn from — or identical to — the official validation split. The paper does not name the provenance of its 1,000 eval items; **identity UNVERIFIED**, but the eval is 1,000 items either way, not 10,000.
- **Comparability:** ❌ Headline 71.5 is **not comparable** to the LAYA study: different eval set (1,000 vs 10,000 items), and the model was trained on 10,000 in-pool samples (vs 490). It is, however, the strongest *trained-agent* result and the paper to cite for "RL-trained tool use."
- **Sources:** https://arxiv.org/abs/2609.30698 ; full text https://arxiv.org/pdf/2609.30698v1.pdf (Table 3; Datasets § "10,000 samples for training and 1,000 samples for testing"; Implementation § SFT 8,000 / RL 2,000)

### 5. T2Agent — "A Tool-augmented Multimodal Misinformation Detection Agent with Monte Carlo Tree Search"
- **Authors / venue:** Xing Cui, Yueying Zou, Zekun Li, Peipei Li, Xinyuan Xu, Xuannan Liu, Huaibo Huang — arXiv:2505.19768 (May 2025); AAAI 2026 (oral, per paper notes).
- **Method (one line):** Training-free agent: a greedy tool selector builds an action space, then Monte Carlo Tree Search with a dual reward plans multi-source verification trajectories over a frozen proprietary VLM.
- **Base models:** GPT-4o / GPT-4o-mini / GPT-4.1-nano (proprietary, undisclosed size).
- **Training data:** none (explicitly "training-free"; all gains are test-time compute).
- **MMFakeBench numbers — ⚠️ Protocol C:** the paper states it samples **1,000 validation instances** (300 Real / 300 TVD / 100 VVD / 300 CCD). 4-class macro-F1 / Accuracy:
  - **T2Agent GPT-4o: F1 0.759, Acc 0.753**; GPT-4o-mini: 0.631 / 0.629; GPT-4.1-nano: 0.568 / 0.569
  - Same table: MMD-Agent GPT-4o 0.614 / 0.616; LRQ-FACT GPT-4o 0.716 / 0.708; Standard Prompt GPT-4o 0.492 / 0.609; Standard LLaVA-1.6 0.257 / 0.404; Standard BLIP-2 0.167 / 0.328
- **Comparability:** ❌ 0.759 is a **validation-subset** number from a frontier model doing MCTS tool search per item — not a test-set number and not a trained model. It is the most-quoted "SOTA" figure for MMFakeBench and the one most often mis-compared against test-set results.
- **Sources:** https://arxiv.org/abs/2505.19768 ; table + protocol in https://arxiv.org/html/2505.19768v2/ (Table 1; "We sample 1,000 validation instances…")

### 6. AgentM3D — "Agentic Mixed-Source Multi-Modal Misinformation Detection with Adaptive Test-Time Scaling"
- **Authors / venue:** Wei Jiang, Tong Chen, Wei Yuan, Quoc Viet Hung Nguyen, Hongzhi Yin — arXiv:2603.02519 (Mar 2026).
- **Method (one line):** Zero-shot multi-agent cascade of modality-specific VLM agents with Best-of-N test-time scaling and a critic agent; a planning agent adapts the search budget per sample.
- **Base models:** Qwen3-VL-4B and Qwen3-VL-**8B** (open).
- **Training data:** none (zero-shot; gains are inference-time compute).
- **MMFakeBench numbers — ⚠️ Protocol C** (same 1,000-validation-instance protocol as T2Agent, stated in the paper): Acc / macro-F1 / Recall / Precision (%):
  - **AgentM3D Qwen3-VL-8B: Acc 62.0, F1 62.6**; Qwen3-VL-4B: Acc 58.1, F1 58.0
  - Reproductions under their protocol: MMD-Agent Qwen3-VL-8B F1 60.2; T2Agent Qwen3-VL-8B F1 54.0; Standard Qwen3-VL-8B F1 37.0
- **Comparability:** ❌ Validation subset + zero-shot test-time scaling. Notable as the strongest *open-model* agent result, and its F1 (62.6, on 1,000 val items) is numerically near the LAYA test number (60.2, on 10,000 test items) despite the protocol gap.
- **Source:** https://arxiv.org/html/2603.02519v1 (Table 1; §4.1 protocol statement); https://arxiv.org/abs/2603.02519

### 7. LRQ-FACT — "LRQ-FACT: LLM-Generated Relevant Questions for Multimodal Fact-Checking"
- **Authors / venue:** Beigi et al. 2024 — arXiv:2410.04616 (as cited in MM-VeriAgent's references).
- **Method (one line):** Fixed-workflow agent that generates relevant questions and answers them with tools/evidence before verdict (no training, no search).
- **MMFakeBench numbers:** as reported in T2Agent's Table 1 (Protocol C, GPT-4o backbone): **F1 0.716, Acc 0.708**. LRQ-FACT's own-paper MMFakeBench protocol **UNVERIFIED** beyond this second-hand table.
- **Comparability:** ❌ Validation-subset, second-hand. Included because it is a standard baseline row in the agent literature.
- **Sources:** https://arxiv.org/html/2505.19768v2/ (Table 1); reference identity via https://arxiv.org/pdf/2609.30698v1.pdf (References)

### 8. MERIT (v1 title: MIRAGE) — "Modular Framework for Multimodal Misinformation Detection with Web-Grounded Reasoning"
- **Authors / venue:** Mir Nafis Sharear Shopnil, Sharad Duwal, Abhishek Tyagi, Adiba Mahbub Proma — arXiv:2510.17590 (v1 "MIRAGE" Oct 2025; v2 "MERIT" Apr 2026). **Same paper, two titles — do not count twice.**
- **Method (one line):** Inference-time modular pipeline (visual forensics → cross-modal alignment → retrieval-augmented claim verification with live web search → calibrated judgment) over a frozen VLM.
- **Base model:** GPT-4o-mini (proprietary).
- **Training data:** none (zero-shot, but with **live web retrieval at inference** — external evidence the LAYA study does not use).
- **MMFakeBench numbers — ⚠️ Protocols E/F (BINARY real-vs-fake F1, with sensitivity/specificity reported):**
  - Validation (1,000): **F1 81.65**, Acc 75.1
  - "Test": **F1 81.44**, Acc 75.08 — on a **stratified random 5,000-sample (50%) subsample of the test set, seed 42**, not the full test set
  - Its quoted baselines are also binary: GPT-4V Standard "72.3 F1", GPT-4V + MMD-Agent "74.0 F1" (= the benchmark paper's *binary* val F1, Table 6 — not the 61.6 macro-F1 headline)
  - 🔎 The paper also describes the benchmark as having a "train (6,000) / validation (1,000) / test (10,000)" split totalling 17,000 items, which contradicts the benchmark paper's 11,000 items in 1,000 val + 10,000 test. Flagged as an internal inconsistency in MERIT.
- **Comparability:** ❌❌ The 81.65 figure is the single most misleading number in this landscape: **binary F1** (a 2-class task where the LAYA study's own binary readout would also be far higher), on validation, with web retrieval. It must never be placed on the same axis as 4-class macro-F1 test results.
- **Sources:** https://arxiv.org/abs/2510.17590 ; https://arxiv.org/html/2510.17590v1 (Table 1; test-subsample footnote)

### 9. "Fact or Fake? Assessing the Role of Deepfake Detectors in Multimodal Misinformation Detection" (secondary, partially verified)
- **Venue:** IEEE Access (accepted 2026; DOI 10.1109/ACCESS.2026.3686437).
- **Method (one line):** Systematic study of image-only deepfake detectors vs an evidence-driven fact-checking system (MCTS tool search + multi-agent debate) and a hybrid.
- **Reported:** deepfake detectors alone reach F1 0.26–0.53 on MMFakeBench; the evidence-driven fact-checking system reaches **F1 ≈ 0.81**; injecting detector outputs *hurts* (−0.04–0.08 F1).
- **Comparability:** ⚠️ **Split and metric framing UNVERIFIED** (abstract only was opened). The ≈0.81 is an agent-system number in the T2Agent lineage; do not rank it until the full text's protocol is checked.
- **Source:** https://acikerisim.fsm.edu.tr/bitstreams/85ba3e03-a226-458b-8d70-81f3a4c67330/download (accepted manuscript, abstract)

---

## Head-to-head vs the LAYA study (TEST macro-F1 = 0.6020, 201M params, 490 training examples)

| # | Competitor | Their headline | Protocol | Comparable? | LAYA vs them |
|---|---|---|---|---|---|
| 1 | SCPO (Qwen2-VL-7B, fine-tuned) | F1 0.573 (Top-1) / 0.661 (Recall-mode) | A | ✅ Top-1 only | **+2.9 pts** vs Top-1 |
| 2 | DeceptionDecoded FT (Qwen2.5-VL-7B) | F1 0.5866 | A? (split UNVERIFIED) | 🟡 | **+1.5 pts** if test |
| 3 | GPT-4V + MMD-Agent (zero-shot) | F1 0.615 | A | ✅ | **−1.3 pts** |
| 3 | GPT-4V Standard (zero-shot) | F1 0.488 | A | ✅ | **+11.4 pts** |
| 4 | MM-VeriAgent (Qwen2.5-VL-7B, SFT+RL) | F1 0.715 | D (re-split, 1k eval) | ❌ | n/a |
| 5 | T2Agent (GPT-4o, MCTS) | F1 0.759 | C (val 1k) | ❌ | n/a |
| 6 | AgentM3D (Qwen3-VL-8B, zero-shot TTS) | F1 0.626 | C (val 1k) | ❌ | n/a |
| 7 | LRQ-FACT (GPT-4o) | F1 0.716 | C (val 1k, 2nd-hand) | ❌ | n/a |
| 8 | MERIT/MIRAGE (GPT-4o-mini + web) | F1 0.8165 | E/F (binary) | ❌ | n/a |
| 9 | Fact or Fake? system | F1 ≈ 0.81 | UNVERIFIED | ⚠️ | n/a |

**Efficiency context for the ranking:** every trained competitor used a 7B backbone (35× LAYA's 201M). Training-data scale: SCPO = multi-benchmark synthetic corpus (count unverified); MM-VeriAgent = 10,000 in-pool samples + a GPT-5-mini teacher; DeceptionDecoded = 6,000 out-of-domain samples. LAYA used **490 in-domain examples** — 12–20× less data than any trained rival — and no tools, retrieval, teacher model, or test-time search at inference.

---

## Framing traps to police in any write-up

1. **MERIT/MIRAGE 81.65** — binary F1 on validation with web retrieval. The most inflated headline in the space.
2. **T2Agent 75.9** — 4-class, but on 1,000 validation items with GPT-4o + MCTS per-item search; routinely cited as if it were a test result.
3. **MM-VeriAgent 71.5** — trained on 10,000 of the benchmark's own 11,000 items and evaluated on the remaining 1,000; its split is not the official test set, and its reproduced baselines match official *validation* numbers.
4. **SCPO 66.1** — real, but it is the *Recall-extraction* reading on test; the same model's Top-1 reading is 57.3. Quote the mode or don't quote the number.
5. **Benchmark binary table** — the original paper's Table 6 binary F1s (e.g., 74.0 for GPT-4V + MMD-Agent) circulate as "the MMD-Agent score" in agent papers; the benchmark's headline macro-F1 for the same system is 61.6 val / 61.5 test.
6. **MERIT's split description** (6,000 train / 1,000 val / 10,000 test = 17,000) contradicts the benchmark's actual 11,000 items — a sign of careless protocol reporting in that paper.
7. **Subsampled test sets** — MERIT's "test" result covers 5,000 of 10,000 test items (seed-42 stratified). The LAYA study scored the full test set in a single pass.

## Verification status
Every number above was read from the cited source during this scout pass, except items explicitly marked UNVERIFIED (DeceptionDecoded eval split; SCPO SCoT sample count; LRQ-FACT's own protocol; Fact-or-Fake framing). No figures were invented or carried over from memory without a source.
