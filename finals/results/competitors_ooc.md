# Competitors — NewsCLIPpings & VERITE (Out-of-Context / OOC slice)

Scouted 2026-11-22. Every accuracy below is copied from a published table or the
paper's own summary, with its source URL. Framing is labelled on every row —
on these two benchmarks the framing changes the number more than the method does.

## The study being benchmarked (LAYA-Vision, 201M params, paired image+text)

| Dataset | LAYA result | Framing |
|---|---|---|
| NewsCLIPpings | **0.5141 accuracy, zero-shot** | Merged-Balanced **validation** (7,024 rows, full stream, 0 skipped). Trained-arm verdict pending. |
| NewsCLIPpings | human reference **0.656** | Human average, 200-sample subset of Merged/Balanced (pristine 0.962 / falsified 0.350) |
| VERITE | **0.3506 accuracy** | Paired transfer (model never trained on VERITE), 1,001 local rows of the official 1,000; compare against the **multiclass** framing below |

---

## 1. NewsCLIPpings — Merged-Balanced (train 71,072 / val 7,024 / test 7,264)

### 1a. Closest to LAYA's regime — no external evidence, single model, zero-shot or fine-tuned on the pair alone

Ranked by closeness to LAYA's zero-shot 0.5141:

| # | Method (paper) | Venue / year | Model + size | Training scale | Accuracy (as published) | Source |
|---|---|---|---|---|---|---|
| 1 | **InstructBLIP zero-shot** (baseline in MAD-Sherlock) | arXiv:2410.20140, 2024 | InstructBLIP (ViT-G/14 + Vicuna) | None (zero-shot) | **48.6** — the only published zero-shot comparator near LAYA; LAYA zero-shot (51.41) sits **above** it | https://arxiv.org/html/2410.20140v1 |
| 2 | **SAFE** (Zhou et al.) | 2020; table in Neuro-Symbolic paper | Similarity-aware fact-checking encoder | Fine-tuned on NewsCLIPpings train | **50.7** — a *trained* model essentially tied with LAYA zero-shot | https://arxiv.org/pdf/2304.07633 |
| 3 | **VisualBERT** (Li et al.; table in Neuro-Symbolic paper) | 2019 / reported 2023 | VisualBERT | Fine-tuned on NewsCLIPpings train | **54.8** | https://arxiv.org/pdf/2304.07633 |
| 4 | **EANN** (Wang et al.; table in MAD-Sherlock) | 2018 / reported 2024 | Event-adversarial network | Fine-tuned | **58.1** | https://arxiv.org/html/2410.20140v1 |
| 5 | **CLIP fine-tuned — the original benchmark** (Luo, Darrell, Rohrbach, "NewsCLIPpings: Automatic Generation of Out-of-Context Multimodal Media") | EMNLP 2021 | CLIP ViT-B/32 (~151M) | Fine-tuned on NewsCLIPpings train (full split training) | **66.1** — the canonical fine-tuned reference; also ≈ human average (65.6) | https://arxiv.org/pdf/2502.00752 (comparison table) and https://aclanthology.org/2021.emnlp-main.545.pdf |
| 6 | **Neuro-Symbolic detector** (Zhang et al., "Interpretable Detection of Out-of-Context Misinformation with Neural-Symbolic-Enhanced Large Multimodal Model") | arXiv:2304.07633, 2023 | Query generation + CLIP/BLIP-2 verification | Fine-tuned components on NewsCLIPpings | **68.2** (AUC 73.0); BLIP-2 prompt-ensemble baseline in same table 62.4, VINVL 65.4, SSDL 65.6 | https://arxiv.org/pdf/2304.07633 |
| 7 | **LOGRAN** (soft-logic regularisation; backbone CLIP) | arXiv:2406.04756, 2024 (ICASSP-style) | CLIP + logic-regularised head | Fine-tuned on NewsCLIPpings | **70.51** on Merged/Balanced test (CLIP alone in same setup 67.27; per-split rows 59.03–73.14) | https://arxiv.org/pdf/2406.04756 |
| 8 | **SSDL** (Mu et al., self-supervised) | 2023; figure via LAMAR Table 3 | Self-supervised fine-tune | Fine-tuned on NewsCLIPpings | **71.0** in LAMAR's "True vs OOC" NewsCLIPpings column; **65.6** in the Neuro-Symbolic paper's table — ⚠️ the two tables use different setups; treat the method as mid-60s-to-71 depending on protocol | https://arxiv.org/pdf/2504.06010 and https://arxiv.org/pdf/2304.07633 |

### 1b. Evidence-based and LLM-system SOTA — the 84–93% band (different sport: web evidence and/or frontier LLMs)

These numbers are **not comparable** to LAYA's no-evidence, no-retrieval setting.
Every one of them either retrieves external web evidence per item or runs a frontier LLM.

| # | Method (paper) | Venue / year | Model + size | Training / evidence | Accuracy (as published) | Source |
|---|---|---|---|---|---|---|
| 9 | **CCN — Consistency-Checking Network** (Abdelnabi, Hasan, Fritz, "Open-Domain, Content-Based, Multi-Modal Fact-Checking of Out-of-Context Images via Online Resources") | CVPR 2022 | ResNet152 + BERT + fine-tuned CLIP ViT-B/32; detector 20.92M params | Trained on NewsCLIPpings train **+ web evidence collected per item** | **84.7** (+19 pp over its own CLIP-only baseline 66.1 — i.e. the evidence, not the encoder, earns the gap) | https://openaccess.thecvf.com/content/CVPR2022/papers/Abdelnabi_Open-Domain_Content-Based_Multi-Modal_Fact-Checking_of_Out-of-Context_Images_via_Online_Resources_CVPR_2022_paper.pdf |
| 10 | **Delvecchio et al.** ("Zero-Shot Warning Generation for Misinformative Multimodal Content") | arXiv:2502.00752, 2025 (Bologna/NII) | Frozen MiniGPT-4 + consistency-check head; lightweight 5.2M trainable params | Evidence via reverse/direct web search; minimal training (lightweight trains in ~3.6 h on 1 GPU) | **Lightweight 84.8 / Full-scale 87.04** on Merged/Balanced | https://arxiv.org/pdf/2502.00752 |
| 11 | **SEN** 87.1 and **ECENet** 87.7 (as tabulated by Papadopoulos et al., "Similarity over Factuality") | 2024–2025 comparison table | ResNet/BERT/CLIP evidence networks | Evidence-based, trained on NewsCLIPpings + evidence | **87.1 / 87.7** | https://mever.gr/publications/similarity_over_factuality.pdf |
| 12 | **SNIFFER** (Qi, Yan, Hsu, Lee) | CVPR 2024 (arXiv:2403.03170) | InstructBLIP: ViT-G/14 + **Vicuna-13B** (~14B class) | Two-stage instruction tuning; GPT-4-generated OOC instruction data + extensive NewsCLIPpings fine-tuning; internal + external consistency | **88.4** overall test (Fake 86.9 / Real 91.8); without fine-tuning 84.5 | https://www.alphaxiv.org/abs/2403.03170 |
| 13 | **LLaVA-SNIPPER** (scene-graph + MLLM) | ACM, Aug 2025 | LLaVA + scene-graph extraction (size UNVERIFIED from fetched text) | Fine-tuned/evaluated on NewsCLIPpings | **89.7** overall (Fake 88.1 / Real 93.5) | https://dl.acm.org/doi/10.1145/3709020.3734830 |
| 14 | **E-FreeM2** (training-free multi-scale verification via MLLMs) | arXiv:2506.20944, 2025 | MLLM pipeline (backbone size UNVERIFIED) | **Training-free**; retrieval-based; evaluated on Merged/Balanced **test** (7,264) | **90.0** overall (OOC 90.67 / NOOC 89.49) | Search-result table from the paper (ResearchGate copy): https://www.researchgate.net/publication/393065762_E-FreeM2_Efficient_Training-Free_Multi-Scale_and_Cross-Modal_News_Verification_via_MLLMs |
| 15 | **MAD-Sherlock** (Lakara, Channing et al., multi-agent debate) | ICML 2025 Workshop CFAgentic (arXiv:2410.20140) | **GPT-4o** agents + Bing reverse-image-search retrieval | **No fine-tuning**; debate + external retrieval | **90.17** in the arXiv HTML comparison table; **90.8** in the PDF (v3) Table 2 — ⚠️ version discrepancy, both published forms exist; GPT-4o alone (no debate) 70.7 in the same table | https://arxiv.org/html/2410.20140v1 and https://arxiv.org/pdf/2410.20140 |
| 16 | **MUSE-MLP / AITR** (Papadopoulos et al., "Similarity over Factuality: Are We Making Progress on Multimodal Out-of-Context Misinformation Detection?") | 2025 | CLIP ViT-L/14 similarity features + MLP / attentive Transformer | Evidence similarities (MUSE) to retrieved web evidence; trained classifier | **MUSE-MLP (L/14) 90.0; AITR (L/14) 93.3** — the highest published NewsCLIPpings numbers found; the paper's own point is that these come from surface similarity shortcuts in the evidence, not factuality reasoning | https://mever.gr/publications/similarity_over_factuality.pdf |
| — | **RED-DOT** (evidence re-ranking Transformer; same comparison table) | 2024 | CLIP B/32 / L/14 variants | Evidence-based | **87.8 (B/32) / 90.3 (L/14)** | https://mever.gr/publications/similarity_over_factuality.pdf |
| — | **DT-Transformer** | reported 2023–2025 | Transformer over evidence/features | ⚠️ **77.1** in the MAD-Sherlock / E-FreeM2 tables vs **65.7** in the Neuro-Symbolic table — two different protocols under one name; UNVERIFIED which is canonical. Do not quote without the protocol. | https://arxiv.org/html/2410.20140v1 vs https://arxiv.org/pdf/2304.07633 |

**Where LAYA sits on NewsCLIPpings:** zero-shot 51.41 is above the only published
zero-shot comparator (InstructBLIP 48.6) and level with a *trained* SAFE (50.7);
it is −14.7 pp below the fine-tuned CLIP reference (66.1) and the human average
(65.6), and −33 to −42 pp below the evidence/LLM band (84.7–93.3) — a band that
buys its accuracy with per-item web evidence or frontier-LLM inference, neither
of which LAYA uses. The trained-arm verdict (pending) is the number that will be
compared against the 66.1 fine-tuned reference.

---

## 2. VERITE — 1,000 pairs (338 True / 324 OOC / 338 Miscaptioned), real fact-checked data

⚠️ **Framing is everything here.** Three different tasks circulate under the name "VERITE accuracy":
**(A) Multiclass** (True vs MC vs OOC, chance = 33.3%) — the framing LAYA's 0.3506 belongs to.
**(B) Binary True vs OOC** (chance = 50%).
**(C) Binary True vs MC** (chance = 50%).
Evidence-based papers additionally report (B) under out-of-distribution cross-validation with web evidence.

### 2A. Multiclass — LAYA's framing

| # | Method (paper) | Venue / year | Model + size | Training scale | Accuracy (as published) | Source |
|---|---|---|---|---|---|---|
| 1 | **VERITE original benchmark — best model** (Papadopoulos, Koutlis, Papadopoulos, Petrantonakis, "VERITE: A Robust Benchmark for Multimodal Misinformation Detection Accounting for Unimodal Bias") | IJMIR 2023; arXiv:2304.14133 | Transformer detector D(I,C) over CLIP features | Trained on synthetic corpora at ~1M-pair scale (CHASMA-D 145,891–1,007,744 pairs; CLIP-NESt 847,693; NC-t2t 258,036 for the OOC class) | **52.1** overall multiclass (per-class: True 70.7 / MC 33.4 / OOC 52.2). Other training mixes in the same table: 47.7–50.8 | https://arxiv.org/pdf/2304.14133 |
| 2 | **AITR** (same authors, comparison in LAMAR Table 4) | 2025 | Attentive Transformer over CLIP features | Trained on CHASMA / VLM-generated sets + NewsCLIPpings for OOC | **51.4–52.0** depending on training set | https://arxiv.org/pdf/2504.06010 |
| 3 | **LAMAR** (Papadopoulos et al., "Latent Reconstruction from Generated Data for Multimodal Misinformation Detection" — "MisCaption This!") | arXiv:2504.06010, 2025 | Latent-reconstruction Transformer, **19–21M params** | Trained on VLM-generated miscaption sets (LLaVA-D₃ / Molmo-D₃) + NewsCLIPpings for OOC; **no external evidence** | **54.9** multiclass (Molmo-D₃ training) — current multiclass SOTA found; 54.2 (LLaVA-D₃), 53.2 (CHASMA) | https://arxiv.org/pdf/2504.06010 |
| — | **LAYA-Vision (this study)** | 2026 | 201M, paired | **Zero VERITE training** — transfer from MMFakeBench fine-tune | **35.06** — only ~1.7 pp above the 33.3% chance floor; −17.0 pp below the original benchmark's trained best (52.1), −19.8 pp below LAMAR (54.9). Every comparator above was *trained for this task* on 10⁵–10⁶ synthetic pairs; LAYA was not trained on VERITE at all. | Study record |

### 2B. Binary True vs OOC — do NOT compare with 2A

| Method | Setup | Accuracy | Source |
|---|---|---|---|
| VERITE paper's proposed method (headline as summarised by the authors) | Binary, OOC pairs | **72.7** (and 63.9 on MC pairs) — the figure the study brief cites as "the 72.7% binary baseline" | https://mever.gr/post/overcoming-unimodal-bias-in-multimodal-misinformation-detection/ |
| SAFE (trained on NewsCLIPpings, LAMAR Table 3) | True vs OOC, no external evidence | **72.7** on VERITE (coincidentally the same number, different source table) | https://arxiv.org/pdf/2504.06010 |
| MUSE (LAMAR Table 3) | True vs OOC, no external evidence | **72.0** | https://arxiv.org/pdf/2504.06010 |
| AITR (LAMAR Table 3) | True vs OOC, no external evidence | **74.1** | https://arxiv.org/pdf/2504.06010 |
| LAMAR [E2E, Gate] (LAMAR Table 3) | True vs OOC, no external evidence | **76.3** — best no-evidence binary | https://arxiv.org/pdf/2504.06010 |
| MUSE-MLP (L/14) / AITR (L/14) ("Similarity over Factuality" Table 2) | True vs OOC **with web evidence**, OOD cross-validation | **80.6 / 82.7** (±6.1) | https://mever.gr/publications/similarity_over_factuality.pdf |
| MAD-Sherlock (GPT-4o + retrieval, no fine-tuning) | True vs OOC | **79.5** (their pooled binary "VERITE (all)" = **85.2**; True vs MC = 80.7) | https://arxiv.org/pdf/2410.20140 (Appendix Table 5) |
| CRAVE (Dey et al. 2025, as tabulated by MAD-Sherlock) | VERITE (framing as in MAD Table 2) | **82.0** | https://arxiv.org/pdf/2410.20140 |

### 2C. Binary True vs MC and zero-shot VLMs (context for how hard VERITE is)

- Zero-shot VLMs on True vs MC (LAMAR Table 5): LLaVA 1.6 (7B) **66.9**, Molmo (7B) 63.0, Llama 3.2 (11B) 59.3 — even 7–11B VLMs, zero-shot, only reach the 60s on the *binary* task; on the post-cutoff VERITE 24/25 set they drop 5–7 pp while fine-tuned LAMAR (21M) holds 70.0. Source: https://arxiv.org/pdf/2504.06010
- MultiReflect (MAGMaR 2025 workshop): GPT-4V best binary F1 **0.74** (F1, not accuracy); all its variants **underperform the original VERITE baseline in multiclass**. Source: https://aclanthology.org/anthology-files/anthology-files/pdf/magmar/2025.magmar-1.1.pdf

**Where LAYA sits on VERITE:** in its own framing (multiclass, no task training),
35.06 is near the floor — the honest read is that MMFakeBench adaptation did not
transfer to real fact-checked data (the study's H3 was registered as NOT MET).
The published multiclass band for *trained* systems is narrow and low (47.7–54.9)
because VERITE was built to defeat unimodal shortcuts; the eye-catching 72–85%
figures are all binary framings and/or evidence-based systems.

---

## 3. Cross-cutting notes for the comparison write-up

1. **The evidence divide is the story.** On NewsCLIPpings, no-evidence methods
   top out at 66–71%; adding per-item web evidence jumps the same encoders to
   84.7–93.3%. Papadopoulos et al. ("Similarity over Factuality", 2025) argue
   the evidence band is substantially a similarity-shortcut artifact — retrieved
   evidence for these four news sources often *is* the original article.
2. **Training scale asymmetry.** The VERITE multiclass leaders trained on
   10⁵–10⁶ synthetic pairs; SNIFFER fine-tuned a ~13B LLM on GPT-4-generated
   instruction data; LAYA's NewsCLIPpings arm trains on 2,501 carved items and
   its VERITE number uses zero VERITE training. Any table that hides the
   training-scale column misleads.
3. **Discrepancies flagged, not smoothed:** MAD-Sherlock NewsCLIPpings 90.17
   (HTML) vs 90.8 (PDF v3); DT-Transformer 77.1 vs 65.7 across tables; SSDL
   71.0 vs 65.6 across tables. Quote with the protocol attached or not at all.
4. **UNVERIFIED items:** LLaVA-SNIPPER parameter count; E-FreeM2 backbone size;
   which DT-Transformer protocol is canonical. Everything else above traces to
   a table or author summary at the URL given.
