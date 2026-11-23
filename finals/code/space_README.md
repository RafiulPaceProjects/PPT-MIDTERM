---
title: LAYA — Multimodal Misinformation Detection (Before / After Training)
emoji: 📰
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: apache-2.0
---

# LAYA — Multimodal Misinformation Detection, Before & After Training

**Rafiul Haider · Pace University Analytics Capstone (Fall 2026, CRN 72369) · CS 668 Team 3**
*(Ananya Saravani Ganni, Harika Etikela, Rafiul Haider)*

## What this research is

News posts pair an image with a caption, and either half can be the lie. This study evaluates — and then adapts — **LAYA-Vision**, a small typed-decision vision–language model, on the four-way judgement that defines the task: a pair is **original** (both halves truthful and matched), **textual** (the text is distorted), **visual** (the image is distorted), or **mismatch** (real image, real text, wrong pairing).

Evaluation uses three public benchmarks, each in its native metric:

- **MMFakeBench** — 4-class macro-F1 [1]
- **NewsCLIPpings** — image–caption pairing accuracy [3]
- **VERITE** — 3-class accuracy, eval-only [2]

## How we came about it

The project began as a diagnostic study, and the diagnosis was blunt. Zero-shot, the model sits near chance and **collapses onto one answer**: on 1,000 validation rows it identified 289 of 300 mismatch cases but only **1 of 300** originals. A plain TF-IDF baseline beat it. A second probe changed the conclusion — a logistic regression on the model's *frozen* features beat zero-shot by **+6.24 percentage points** on NewsCLIPpings test. The features know things the decisions don't.

So the research question became: **can proper adaptation turn that latent signal into defensible performance?** The experiment (pre-registered 2026-11-22, before any training ran) fine-tunes on 490 prepared records in two arms — **full fine-tuning** and **LoRA** [4] — selects the winner on a 105-row tune split only, scores the test split once, and calibrates on a reserved 105-row split [5]. Source metadata is never fed to the model: a metadata-only rule reaches 0.9150 on MMFakeBench in our audit, which is label leakage, not evidence.

## The app

The app **runs on changing the weights according to the dataset**. A per-dataset pack registry (mirroring the experiment notebook's `runs/packs.json`) gives each dataset its own native labels, its own two questions, its own fake threshold, and its own fine-tuned checkpoint; selecting a dataset switches all of them together, and a serving line states which weights are loaded.

The layout is a visible three-stage pipeline — **1 · Input** (the image + caption, on screen throughout, with one-click examples), **2 · Processing** (the active pack: which weights, the two questions verbatim, the arbitration rule), **3 · Output** (BEFORE and AFTER columns: class-probability bars, the fake-probability readout, the verdict, an "uncertain" badge when the two questions disagree, and a flip callout when training changed the verdict).

- **Before training** — the pretrained LAYA-Vision checkpoint (pinned revision `f2fe3c12`), zero-shot. Live now.
- **After training** — each dataset's own fine-tuned winner, published to the Hub by the experiment run (`RafiulHaiderbro/laya-vision-fullft-mmfakebench`, `RafiulHaiderbro/laya-vision-fullft-newsclippings`). A panel activates automatically when its checkpoint lands.

## Results

### Before (verified baselines)

| Dataset | Metric | Before |
|---|---|---|
| MMFakeBench (paired, val 1,000 rows) | macro-F1 | 0.2079 |
| MMFakeBench (paired, test ablation) | macro-F1 | 0.2037 |
| NewsCLIPpings (val, 7,024 rows, 0 skipped) | accuracy | 0.5141 |
| VERITE (paired) | accuracy | 0.3467 |
| Per-class recall (1,000 rows) | original / textual / visual / mismatch | 1/300 · 8/300 · 22/100 · 289/300 |
| Calibration (raw) | ECE | ≈ 0.466 |

### After (pre-registered predictions, recorded before training)

| Prediction | Target |
|---|---|
| MMFakeBench tune macro-F1 (winning arm) | 0.30–0.42 |
| NewsCLIPpings val accuracy | 0.55–0.65 |
| VERITE accuracy (transfer, eval-only) | 0.38–0.48 |
| Minimum per-class recall (tune) | ≥ 0.25 |
| Calibrated ECE | < 0.15 |

The final table replaces these targets with measured values and marks each prediction met, missed, or rejected — as it falls.

## References

[1] *MMFakeBench: A Mixed-Source Multimodal Misinformation Detection Benchmark for LVLMs.* arXiv:2406.08772.
[2] *VERITE: A Robust Benchmark for Multimodal Misinformation Detection Accounting for Unimodal Bias.* arXiv:2304.14133.
[3] Luo, G. et al. *NewsCLIPpings: Automatic Generation of Out-of-Context Multimodal Media.* EMNLP 2021.
[4] Hu, E. J. et al. *LoRA: Low-Rank Adaptation of Large Language Models.* ICLR 2022.
[5] Guo, C. et al. *On Calibration of Modern Neural Networks.* ICML 2017.
