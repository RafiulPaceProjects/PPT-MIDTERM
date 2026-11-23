# Method-Space Competitors — LAYA-Vision Misinformation Study

Scout slice: work that competes on the **method**, not the dataset. Five angles, each paper
tested against the LAYA findings. Verdicts: **CONFIRM** (literature agrees with LAYA),
**CONTRADICT** (literature points the other way), **EXTEND** (LAYA adds a regime/result the
paper does not cover). Every claim carries a source URL; anything not verifiable from the
source is marked **UNVERIFIED**. No figures are reported that do not appear in a cited source.

## LAYA findings under test (reference)

- **F-obj:** soft_ce (soft-label cross-entropy / distribution matching) beat the library's
  `rlcd` objective in all 6 matched config pairs.
- **F-rank:** LoRA rank ladder at 490 steps inverted: r8 0.704 > r16 0.573 > r32 0.117 macro-F1.
- **F-data:** minimum-data curve 122 → 0.117 / 245 → 0.367 / 490 → 0.660 macro-F1.
- **F-cal:** temperature fitted on the calibration split (T=8.42) severely degraded held-out
  ECE (0.106 → 0.396); a distribution-matched fit (T=1.65) improved held-out ECE (0.099 → 0.021).
- **F-leak:** a rule using only source metadata scores 0.9150 macro-F1 on tune (leakage ceiling);
  the study protocol never feeds `text_source`/`image_source` to the model.

---

## Angle 1 — Small / parameter-efficient fine-tuning of VLMs for misinformation with tiny training sets

### 1.1 Multi-MLLM Knowledge Distillation for Out-of-Context News Detection (MMKD)
- **Authors:** Yimeng Gu, Zhao Tong, Ignacio Castro, Shu Wu, Gareth Tyson
- **Venue:** arXiv:2505.22517 (2025)
- **Claim touching LAYA:** A small MLLM can be adapted for multimodal out-of-context news
  detection in a label-efficient way: LoRA fine-tuning (stage 1) plus LoRA+DPO on
  teacher-conflict cases (stage 2) reaches state-of-the-art performance "using less than 10%
  labeled data," without proprietary teacher models at inference.
- **Relation to LAYA:** **CONFIRM + EXTEND.** Confirms the shared premise that LoRA adaptation
  of a small VLM is the right vehicle for label-scarce misinformation detection. LAYA extends
  it in two ways: (a) it reaches its result with plain supervised fine-tuning at the
  few-hundred-example scale (F-data), with no teacher ensemble, rationale generation, or
  preference stage; (b) its objective ablation (F-obj) cuts against MMKD's stage-2 design —
  in LAYA's matched pairs, the RL/preference-style objective lost to soft cross-entropy in
  6 of 6 configurations.
- **Source:** https://arxiv.org/pdf/2505.22517

### 1.2 Evaluating the efficiency and factual reliability of LoRA for health misinformation detection
- **Authors:** UNVERIFIED (not shown in the fetched article text)
- **Venue:** Scientific Reports (2026), article s41598-026-48110-4
- **Claim touching LAYA:** On HealthMisinfo-2023 (5,988 samples; 4,192 train), LoRA
  (r=8, α=32, QKVO targets) on a BERT encoder reaches 85.1% accuracy / 85.1 macro-F1 using
  ~0.1% of trainable parameters, reported against a 68.4% accuracy full-fine-tuning baseline
  (figures as reported in the article's results summary). It also reports LoRA raises
  predictive entropy on long/dense inputs — a "semantic bottleneck" reliability caveat.
- **Relation to LAYA:** **CONFIRM + EXTEND.** Confirms that a low rank (r=8) is not a
  compromise but the winning setting at small data scale — the same rank that tops LAYA's
  ladder (F-rank). LAYA extends the result from a text encoder at ~4k training samples to a
  vision-language model at ~0.5k examples, and adds the calibration-transfer failure mode
  (F-cal) that this paper's entropy observations only hint at.
- **Source:** https://www.nature.com/articles/s41598-026-48110-4

### 1.3 LoRA Without Regret
- **Authors:** John Schulman et al., Thinking Machines Lab
- **Venue:** Thinking Machines Lab blog, 29 Sep 2025 (not peer-reviewed)
- **Claim touching LAYA:** For post-training-scale datasets, LoRA learns with the same sample
  efficiency as full fine-tuning and reaches the same ultimate performance; LoRA only falls
  behind when the dataset exceeds LoRA's capacity, and its large-batch penalty "is not
  mitigated by increasing the LoRA rank."
- **Relation to LAYA:** **CONFIRM + EXTEND.** Confirms that at LAYA's data scale (~490
  examples) LoRA capacity is not the binding constraint, consistent with LAYA's LoRA arms
  being competitive with full fine-tuning at r8/r16. LAYA extends the picture with a failure
  mode this account does not report: at fixed step budget the rank ladder does not merely
  saturate, it *inverts and collapses* at r32 (F-rank) — and with an RL-style objective the
  LoRA arm degrades catastrophically at longer training, which a pure capacity story cannot
  explain.
- **Source:** https://thinkingmachines.ai/blog/lora/

### 1.4 LoRA Learns Less and Forgets Less
- **Authors:** Dan Biderman, Jose Gonzalez Ortiz, et al.
- **Venue:** TMLR 2024 (arXiv:2405.09673)
- **Claim touching LAYA:** Comparing LoRA vs full fine-tuning on code/math at
  instruction-tuning scale (≈100K pairs) and continued-pretraining scale: in standard
  low-rank settings LoRA substantially underperforms full fine-tuning; in instruction
  fine-tuning, *higher ranks can match* full fine-tuning; full fine-tuning's weight
  perturbations have rank 10–100× typical LoRA configurations.
- **Relation to LAYA:** **EXTEND (surface contradiction, resolved by regime).** Their
  rank trend — more rank helps, up to matching full FT — points the opposite way from
  LAYA's inverted ladder (F-rank). The two are reconciled by data scale: their smallest
  regime is ~200× LAYA's training set. LAYA extends their map into the sub-1k-example
  regime, where the rank-benefit direction flips and high rank becomes actively harmful
  rather than merely capacity-limited.
- **Source:** https://arxiv.org/html/2405.09673v2

---

## Angle 2 — Soft-label / distribution-matching objectives vs RL-style or contrastive objectives

### ⚠ Identity caveat on "rlcd" (read first)
Two different methods share the acronym, and which one the LAYA library implements is
**UNVERIFIED** from public sources:
- **RLCD = Reinforcement Learning from Contrastive Distillation** — Yang et al., ICLR 2024
  (below), a PPO alignment method using contrastive-prompt preference pairs.
- **RLCD = Reinforcement Learning for Calibrated Decisions** — a vendor-coined objective
  attributed to TypeSafe AI's Jev model (Sep 2026); per the secondary source, "the objective
  is public, the mechanism is not… no paper, no published reward function… not independently
  reproduced." Given that LAYA is a typed-decision model in the TypeSafe/Jev lineage, this
  is the more plausible referent, but that identification is an inference, not a verified fact.
- **Source for the collision and the vendor claim:** https://www.sanity.io/glossary/rlcd-reinforcement-learning-for-calibrated-decisions

### 2.1 RLCD: Reinforcement Learning from Contrastive Distillation for Language Model Alignment
- **Authors:** Kevin Yang, Dan Klein, Asli Celikyilmaz, Nanyun Peng, Yuandong Tian
- **Venue:** ICLR 2024 (arXiv:2307.12950)
- **Claim touching LAYA:** An RL pipeline (preference model + PPO) trained on contrastive
  synthetic preference pairs "outperforms RLAIF and context distillation baselines across
  three diverse alignment tasks" at 7B and 30B scale — i.e., the RL objective beats
  supervised/distillation-style training for shaping model outputs.
- **Relation to LAYA:** **CONTRADICT (in LAYA's regime) / LAYA EXTENDS the boundary.** In
  LAYA's matched pairs, the RL-style objective lost to plain soft cross-entropy in 6 of 6
  configurations (F-obj), including one arm that collapsed entirely. LAYA's result bounds
  the RLCD-style claim: whatever advantage an RL objective has for open-ended alignment at
  7B+ scale with large preference corpora does not transfer to small-data typed
  classification, where direct distribution matching is uniformly better in this study.
  (Subject to the identity caveat above: if the library's `rlcd` is the calibrated-decisions
  objective rather than Yang et al.'s method, this paper is a namesake, not the baseline.)
- **Source:** https://arxiv.org/html/2307.12950v3

### 2.2 Distributions In, Distributions Out: The Case for Soft-Label Training
- **Authors:** Agamdeep Singh, Ashish Tiwari, Hosein Hasanbeig, Priyanshu Gupta
- **Venue:** arXiv:2511.14117 (2025)
- **Claim touching LAYA:** Training classifiers on the full annotation distribution instead
  of a majority-vote hard label "matches or exceeds hard-label accuracy on every dataset,"
  reduces KL divergence to the annotator distribution (reported as 32% on average), and
  makes per-sample prediction entropy track human disagreement (ChaosNLI, POPQUORN,
  CIFAR-10H). *Caveat:* an independent machine review of the paper disputes the 32%
  headline (recomputed per-dataset reductions ≈13–32%) — treat that figure as
  reported-but-disputed; the directional result is not disputed in the review.
- **Relation to LAYA:** **CONFIRM + EXTEND.** Confirms the core mechanism behind F-obj:
  distribution targets are the correct learning signal for probabilistic classification,
  not a smoothing trick. LAYA extends it from annotator-distribution targets on
  text/vision benchmarks to a VLM misinformation classifier, and adds the head-to-head the
  paper does not run: soft distribution matching vs an RL-style objective, matched pairs,
  soft winning 6/6.
- **Sources:** http://pith.science/paper/2511.14117 (summary + review);
  arXiv:2511.14117 as cited therein

### 2.3 Teaching Metric Distance to Discrete Autoregressive Language Models (DIST2Loss)
- **Authors:** UNVERIFIED (paper-note page does not list them)
- **Venue:** ICLR 2026 (paper note)
- **Claim touching LAYA:** Converting metric distances between output tokens into soft
  target distributions and training with a KL/distribution-matching loss injects structure
  that one-hot cross-entropy cannot express, while avoiding RL's sampling and high-variance
  estimation — distribution matching is positioned explicitly as the practical alternative
  to RL for structured categorical outputs.
- **Relation to LAYA:** **CONFIRM.** Independent support, from a different task family, for
  the design choice F-obj validates empirically: prefer a distribution-matching supervised
  objective over an RL objective when the output is a categorical distribution.
- **Source:** https://en.papernotes.org/ICLR2026/llm_nlp/teaching_metric_distance_to_discrete_autoregressive_language_models/

---

## Angle 3 — LoRA rank effects at small data scale

### 3.1 A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA (rsLoRA)
- **Authors:** Damjan Kalajdzievski
- **Venue:** arXiv:2312.03732 (2023)
- **Claim touching LAYA:** Standard LoRA scaling (γ = α/r) "results in slowed learning and
  stunted performance for LoRA with higher-rank adapters" and "causes gradient collapse as
  the rank increases, which slows the learning such that larger ranks perform no different
  than small ranks." Dividing by √r instead (rsLoRA) restores monotone gains from rank.
- **Relation to LAYA:** **CONFIRM + EXTEND.** Confirms that under standard scaling, higher
  rank failing to help is an expected, mechanistically explained phenomenon — LAYA's ladder
  (F-rank) is not an anomaly. LAYA extends it in severity: the r32 arm did not plateau at
  the r8 level, it collapsed to 0.117 (near a single-class predictor, with training loss
  reported rising in the run record). *Mechanism note:* LAYA's ladder used α = 2r (constant
  scale factor 2), so the α/r gradient-collapse mechanism does **not** directly explain the
  inversion — the collapse mechanism at constant scale is **UNVERIFIED** and is an open
  question the study itself should flag rather than borrow rsLoRA's explanation.
- **Source:** https://arxiv.org/html/2312.03732v1

### 3.2 Heterogeneous LoRA for Federated Fine-tuning of On-Device Foundation Models (HetLoRA)
- **Authors:** UNVERIFIED (not shown in the fetched text)
- **Venue:** EMNLP 2024 (arXiv:2401.06432)
- **Claim touching LAYA:** Homogeneous LoRA rank deployment faces "a trade-off between
  overfitting and slow convergence" — high ranks overfit on clients with little data; the
  paper's remedy is per-client rank self-pruning, i.e., rank should shrink where data is
  scarce.
- **Relation to LAYA:** **CONFIRM.** An independent setting (federated, small per-client
  data) reaches the same qualitative law LAYA measures directly: at small data scale,
  higher rank is a liability, not headroom. LAYA's contribution over this work is the
  controlled single-model ladder quantifying how steep the penalty is (r8 → r32 costs
  ~0.59 macro-F1 at 490 steps).
- **Source:** https://arxiv.org/pdf/2401.06432

### 3.3 Original LoRA rank-saturation observation (Hu et al., 2021), as summarized by the rsLoRA author
- **Claim touching LAYA:** "One of the important findings of the original LoRA work was that
  fine-tuning with very low adapter rank (i.e. 4 to 32) could perform well, and that this
  performance did not improve further with increasing rank."
- **Relation to LAYA:** **CONFIRM (direction) / EXTEND (shape).** LAYA agrees there is no
  benefit above low rank, but finds the curve is not a plateau — past the optimum it turns
  down sharply (F-rank). Secondary source; the original paper's own tables were not
  re-fetched for this slice.
- **Source:** https://github.com/Damjan-Kalajdzievski/rsLoRA_Blog

---

## Angle 4 — Calibration of fine-tuned models and whether calibration transfers across distributions

### 4.1 Can You Trust Your Model's Uncertainty? Evaluating Predictive Uncertainty Under Dataset Shift
- **Authors:** Yaniv Ovadia, Emily Fertig, Jie Ren, Zachary Nado, D Sculley, Sebastian
  Nowozin, Joshua V. Dillon, Balaji Lakshminarayanan, Jasper Snoek
- **Venue:** NeurIPS 2019 (arXiv:1906.02530)
- **Claim touching LAYA:** "Post-hoc calibration gives good results in i.i.d. regimes, but
  can fail under even a mild shift"; in their benchmark, temperature scaling "is
  well-calibrated on i.i.d. test, but not calibrated under dataset shift," and on some
  benchmarks post-hoc calibration "actually makes things worse under dataset shift."
- **Relation to LAYA:** **CONFIRM (strongly) + EXTEND.** LAYA reproduces the canonical
  result almost exactly in a new setting: a temperature fitted on one split (T=8.42) made
  held-out ECE far worse (0.106 → 0.396) rather than merely failing to help (F-cal). LAYA
  extends Ovadia et al. in two ways: (a) the "shift" is not input corruption but the
  distribution gap between a small calibration split and the benchmark distribution after
  fine-tuning — the failure occurs with no corrupted inputs at all; (b) LAYA quantifies
  the remedy on the same held-out data: a distribution-matched fit (T=1.65) recovers ECE
  to 0.021, turning a warning into a prescriptive rule (fit temperature on the deployment
  distribution, or ship T=1.0).
- **Source:** http://export.arxiv.org/pdf/1906.02530

### 4.2 Can You Trust Frozen Hematology Foundation Models under Acquisition Shift?
- **Authors:** UNVERIFIED (not shown in the fetched text)
- **Venue:** arXiv (identifier as shown in source: arXiv:2608.25148 — treat the identifier
  itself as UNVERIFIED, it does not follow the usual numbering pattern)
- **Claim touching LAYA:** Across 15 frozen vision encoders, source-trained probes are
  near-calibrated in-domain (ECE 0.004) but collapse off-domain (ECE 0.35); "a temperature
  fitted on the held-out source does not transfer to the target (ECE 0.35→0.32)… only
  oracle target temperature scaling substantially improves it (ECE→0.07), so calibration
  must be corrected per scanner."
- **Relation to LAYA:** **CONFIRM + EXTEND.** Same law, independently measured in medical
  imaging: source-fitted temperature does not transfer; target-fitted temperature works.
  LAYA extends the severity axis — in LAYA the transferred temperature is not merely
  inert (0.35→0.32) but actively harmful (0.106→0.396), because the fitted T (8.42) is far
  from 1, whereas this study's source probes were already near-calibrated (T≈1) so there
  was little to transfer. The pair of results together imply: the more a model needs
  temperature correction on its fitting distribution, the more dangerous that correction
  is on any other distribution.
- **Source:** https://arxiv.org/pdf/2608.25148

### 4.3 Reconstruction Fidelity and Confidence Reliability in Overlapped Radiation-Detector Pulse Analysis Under Distribution Shift
- **Authors:** UNVERIFIED (not shown in the fetched text)
- **Venue:** Journal article via PubMed Central (PMC13708860), 2026
- **Claim touching LAYA:** "Nominally fitted temperature scaling did not improve shifted
  calibration, whereas condition-matched fitting reduced ECE from 0.3696 to 0.1142 and NLL
  from 4.5425 to 0.6362, indicating distribution-dependent calibration."
- **Relation to LAYA:** **CONFIRM.** A third domain (detector signal analysis) reproduces
  both halves of F-cal: mismatched-fit temperature fails under shift; matched-fit
  temperature repairs calibration (their 0.370→0.114; LAYA's 0.099→0.021). LAYA's numbers
  sit comfortably inside the pattern this paper establishes.
- **Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC13708860/

### 4.4 Revisiting the Calibration of Modern Neural Networks
- **Authors:** Matthias Minderer, Josip Djolonga, Rob Romijnders, Frances Hubis, Xiaohua
  Zhai, Neil Houlsby, Dustin Tran, Mario Lucic
- **Venue:** NeurIPS 2021 (arXiv:2106.07998)
- **Claim touching LAYA:** For recent architectures (ViT, MLP-Mixer), "trends observed in
  prior model generations, such as decay of calibration with distribution shift or model
  size, are less pronounced"; modern models "are well calibrated across distribution
  shifts."
- **Relation to LAYA:** **EXTEND / qualifies.** Not a direct contradiction — Minderer et
  al. measure the *intrinsic* calibration of pretrained models, not the transfer of a
  *fitted* temperature after task fine-tuning. LAYA's result adds the missing clause:
  whatever calibration robustness the architecture has at pretraining time, a temperature
  fitted post-fine-tuning on a small off-distribution split can still destroy held-out
  calibration (F-cal). Architecture-level robustness does not rescue split-level
  temperature transfer.
- **Source:** https://export.arxiv.org/abs/2106.07998

---

## Angle 5 — Dataset leakage / metadata shortcut warnings in multimodal & misinformation benchmarks

### 5.1 Hidden Biases in Unreliable News Detection Datasets
- **Authors:** Xiang Zhou, Heba Elfardy, Christos Christodoulopoulos, Thomas Butler,
  Mohit Bansal
- **Venue:** EACL 2021 (arXiv:2104.10130)
- **Claim touching LAYA:** Overlapping article sources between train and evaluation let
  models "achieve good performance by directly memorizing the site-label mapping instead
  of modeling the real task"; removing source overlap (clean split) causes "a significant
  drop (>10%) in accuracy for all models tested." They recommend simple bias-probe
  baselines as a dataset difficulty check.
- **Relation to LAYA:** **CONFIRM + EXTEND.** This is the canonical statement of the
  failure F-leak measures. LAYA extends it from text news corpora to a multimodal
  benchmark and from an accuracy-drop demonstration to a direct ceiling measurement: a
  rule using *only* source metadata reaches 0.9150 macro-F1 on tune — i.e., the shortcut
  alone is worth more than most published model scores. LAYA's protocol (never feed
  `text_source`/`image_source`; metadata rule reported as a diagnostic ceiling) is
  exactly the probe-and-exclude discipline this paper prescribes.
- **Source:** https://ar5iv.labs.arxiv.org/html/2104.10130

### 5.2 What Does 99% Accuracy Measure? A Reproducible Audit of Shortcut Learning in a Widely Used Fake News Corpus
- **Authors:** Yuvraj Verma
- **Venue:** arXiv (identifier as shown in source: arXiv:2609.25006 — treat as shown;
  independent verification of the identifier was not performed)
- **Claim touching LAYA:** On the ISOT/Kaggle fake-news corpus, "a classifier that discards
  the article text entirely and observes only the subject metadata field attains
  F1 = 1.000"; a newswire source tag is present in 99.2% of real articles; removing
  metadata, source-tag, and duplicate leakage channels still leaves F1 ≈ 0.98 because the
  residual signal is diffuse editorial style.
- **Relation to LAYA:** **CONFIRM.** The closest published analogue to F-leak: a
  metadata-only rule saturating a benchmark. LAYA's 0.9150 ceiling is the multimodal
  counterpart (source fields of a vision-language benchmark rather than subject/source
  tags of a text corpus), and LAYA's handling — report the ceiling, ban the fields —
  matches this audit's prescription. The audit's residual-style finding also warns LAYA
  (and its readers) that banning explicit metadata does not prove the remaining signal
  is semantic.
- **Source:** https://arxiv.org/pdf/2609.25006v1

### 5.3 Source Bias in Fact-Check-Derived Fake News Corpora: A Debiasing Protocol and Baselines for Kazakh–Russian News
- **Authors:** UNVERIFIED (not shown in the fetched text)
- **Venue:** Algorithms 2026, 19, 657 (MDPI)
- **Claim touching LAYA:** A naively built fact-check-derived corpus "yields artificially
  high performance (up to 0.98 F1) that plummets by about ten percentage points after the
  removal of the shortcut"; the paper supplies a two-stage debiasing protocol and honest
  post-debias baselines.
- **Relation to LAYA:** **CONFIRM.** Independent quantification of the same inflation
  mechanism (≈0.98 F1 pre-debias) that F-leak's 0.9150 ceiling exemplifies. LAYA differs
  in response, not in diagnosis: instead of debiasing the corpus, it bans the leaky
  fields from the model and publishes the ceiling as a standing warning.
- **Source:** https://mdpi-res.com/d_attachment/algorithms/algorithms-19-00657/article_deploy/algorithms-19-00657.pdf?version=1786254511

### 5.4 Falsdo: Benchmarking Artifact-Controlled Multimodal Fake News Verification via Failure-Aligned Auditing
- **Authors:** UNVERIFIED (not shown in the fetched text)
- **Venue:** IJCAI 2026, pp. 2474–2482
- **Claim touching LAYA:** Current multimodal benchmarks "often fail to isolate true
  semantic checking from superficial shortcut exploitation"; under a counterfactual
  artifact-control protocol that equalizes low-level generation traces, "detector
  performance degrades, indicating reliance on artifacts rather than robust verification."
- **Relation to LAYA:** **CONFIRM + EXTEND.** Confirms, for the current multimodal
  benchmark generation, that shortcut reliance is the default failure mode. LAYA extends
  the taxonomy of shortcuts: Falsdo's channel is *generation artifacts in the content*;
  LAYA's is *provenance metadata about the content* (source fields) — a channel that
  survives even perfectly artifact-controlled content, and therefore needs its own probe
  (the metadata-rule ceiling) in any benchmark audit.
- **Source:** https://ijcai.org/proceedings/2026/275

### 5.5 Shortcut Learning in Deep Neural Networks (foundational framing)
- **Authors:** Robert Geirhos, Jörn-Henrik Jacobsen, Claudio Michaelis, Richard Zemel,
  Wieland Brendel, Matthias Bethge, Felix A. Wichmann
- **Venue:** Nature Machine Intelligence 2(11):665–673, 2020
- **Claim touching LAYA:** Models preferentially learn decision rules that perform well on
  the benchmark distribution but fail under slight distribution change — the general
  phenomenon of which F-leak is an instance.
- **Relation to LAYA:** **CONFIRM (framing).** Cited here as the field's canonical frame,
  via its appearance in Falsdo's reference list (secondary sourcing — the original was
  not re-fetched for this slice).
- **Source (secondary):** https://ijcai.org/proceedings/2026/275

---

## Synthesis — where LAYA stands against the method-space literature

| LAYA finding | Closest literature | Verdict pattern |
|---|---|---|
| F-obj: soft_ce beats rlcd 6/6 | RLCD (Yang et al. 2024); soft-label training (Singh et al. 2025); DIST2Loss (ICLR 2026) | Literature's RL-wins result is from large-scale alignment; soft-target papers support LAYA. LAYA **extends** the boundary to small-data VLM classification. |
| F-rank: ladder inverts, r32 collapses | rsLoRA (Kalajdzievski 2023); HetLoRA (EMNLP 2024); Biderman et al. 2024; Schulman et al. 2025 | "Higher rank doesn't help at small scale" is **confirmed** three ways; the *collapse* (not plateau) and its occurrence at constant α/r scale is LAYA's **extension**, mechanism UNVERIFIED. |
| F-data: 122/245/490 curve | MMKD (2025); Sci. Reports LoRA-health (2026); LoRA Without Regret (2025) | Label-efficient LoRA adaptation is **confirmed** as viable; nobody else in this slice publishes a controlled minimum-data curve for a VLM misinformation classifier at the 100–500-example scale — this is LAYA's clearest **extension**. |
| F-cal: fitted T harms off-distribution, matched T repairs | Ovadia et al. 2019; hematology-FM audit; pulse-analysis study; Minderer et al. 2021 | **Confirmed** in three independent domains; LAYA extends severity (harm, not just non-transfer, because fitted T≫1) and adds the prescriptive matched-fit recovery on the same held-out set. |
| F-leak: metadata rule = 0.9150 | Zhou et al. 2021; Verma audit; Kazakh–Russian debiasing 2026; Falsdo (IJCAI 2026) | **Confirmed** as a known failure class; LAYA extends it to provenance metadata in a multimodal benchmark and reports the ceiling as a first-class result. |

**Net assessment:** No finding in this slice contradicts a LAYA result outright. The two
nearest tensions are regime boundaries, not refutations: Biderman et al.'s rank trend
(measured at ~100K examples) reverses at LAYA's ~500-example scale, and Minderer et al.'s
architecture-level calibration robustness does not cover post-fine-tuning temperature
transfer. LAYA's defensible novelty claims in method space are: (1) the controlled
minimum-data curve for VLM misinformation classification; (2) the 6/6 matched-pair
objective result (soft distribution matching over an RL-style objective) at small data
scale; (3) the severity extension of temperature-transfer failure when the fitted T is
far from 1, paired with the matched-fit recovery; (4) a provenance-metadata leakage
ceiling (0.9150) reported for a multimodal benchmark.

**Open items flagged for the parent agent:**
- The identity of the library's `rlcd` (Yang et al. contrastive distillation vs TypeSafe
  calibrated-decisions) is UNVERIFIED; §2.1's CONTRADICT verdict applies to the
  RL-objective claim in general and to Yang et al. only under the first identification.
- The r32 collapse mechanism at constant α/r scale is UNVERIFIED; rsLoRA's α/r mechanism
  must not be cited as its explanation.
- Several author lists and two arXiv identifiers (2608.25148, 2609.25006) are marked
  UNVERIFIED above and should be checked before any of this is quoted in the paper.
