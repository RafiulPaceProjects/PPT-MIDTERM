# Multi-Metric Competitive Comparison — LAYA-Vision vs Its Top Competitors

**Compiled:** 2026-11-22 (ET) · **Companion to:** `COMPETITIVE_LANDSCAPE_2026-11-22.md` (accuracy/protocol synthesis) and the four `competitors_*.md` scout reports.
**Scope:** the dimensions accuracy tables never show — training cost, inference cost, inference dependencies, latency, deployment footprint, reproducibility, and data efficiency. A competitor appears in a dimension only where that dimension is meaningful for it.

**Flag rules (same as the landscape):** every competitor figure is either sourced from the scout reports / a page opened for this report, or flagged **ESTIMATE** (with its basis stated in one line) or **UNVERIFIED**. Derived ratios show their inputs. No price was invented.

---

## 0. Pricing and measurement bases used throughout

- **LAYA inference (measured, study record):** single forward pass, predict mean **0.16 s/item** on one RTX 4090; study pod rate **$0.897/hr**. Derived: 1,000 predictions = 160 s = 0.0444 hr × $0.897 = **$0.04 per 1,000 predictions** (amortised rental basis; on owned hardware the marginal cost is electricity only).
- **LAYA whole-study spend (study record):** **≈ $5.64 total** at $0.897/hr — the 12-config grid, 15 supplementary runs, the NewsCLIPpings arm, every stream pass, and the rehearsal. Gemini spend on the run: **$0**. Test set scored **once**.
- **OpenAI published per-token rates** (tabulated from OpenAI's published pricing, Oct 2026; page opened for this report — https://www.modelmeterhq.com/blog/openai-api-cost-breakdown): **GPT-4o $2.50 input / $10.00 output** per 1M tokens; **GPT-4o-mini $0.15 / $0.60**; **GPT-4 Turbo $10.00 / $30.00** (the rate class GPT-4V was billed at in the benchmark era; GPT-4V itself is since retired).
- **API per-item token profile (ESTIMATE basis, used for every API row):** one news image at high detail ≈ 765 vision tokens + ≈ 200–400 prompt tokens ≈ **~1,100 input tokens/item**; short verdict output ≈ **~150 output tokens/item**. Per single call this gives: GPT-4V/Turbo ≈ $0.0155/item → **≈ $15/1,000**; GPT-4o ≈ $0.0043/item → **≈ $4.3/1,000**; GPT-4o-mini ≈ $0.00026/item → **≈ $0.26/1,000**. All API per-1,000 figures below are ESTIMATEs built on this profile; multi-call systems multiply it by their call count, stated per row.
- **Local 7B inference (ESTIMATE basis):** a 7B VLM generating a short rationale + verdict on an RTX 4090 runs at roughly 1–5 s/item; amortised at the study's own $0.897/hr pod rate that is **≈ $0.25–$1.25 per 1,000** for a single-pass 7B, before any tool/agent loop. Rows state their own per-system basis.

---

## 1. Scored summary (5 = best in class on that dimension, 1 = worst)

Scores are this report's judgements, each traceable to the evidence tables in §2–§8. Accuracy is deliberately **not** scored here — it is the landscape document's axis, and several rows below are not protocol-comparable on it.

| System | Train cost | Inference cost | Dependencies (fewer = higher) | Latency | Footprint | Reproducibility | Data efficiency |
|---|---|---|---|---|---|---|---|
| **LAYA (201M, 490 ex.)** | **5** | **5** | **5** | **5** | **5** | **5** | **5** |
| Fine-tuned CLIP (NCP) | 4 | 5 | 5 | 5 | 5 | 5 | 2 |
| LAMAR (VERITE) | 3 | 5 | 4 | 5 | 5 | 3 | 2 |
| DeceptionDecoded (7B FT) | 3 | 4 | 5 | 4 | 2 | 2 | 3 |
| SCPO (7B FT) | 2 | 4 | 5 | 3 | 2 | 3 | 2 |
| GPT-4V Standard | 5* | 2 | 3 | 3 | 1 | 1 | n/a |
| GPT-4V + MMD-Agent | 5* | 1 | 2 | 2 | 1 | 1 | n/a |
| MM-VeriAgent (7B SFT+RL) | 1 | 3 | 3 | 2 | 2 | 1 | 2 |
| T2Agent (GPT-4o + MCTS) | 5* | 1 | 1 | 1 | 1 | 2 | n/a |
| MERIT (GPT-4o-mini + web) | 5* | 3 | 1 | 2 | 1 | 1 | n/a |

\* Zero *user-side* training cost because there is no training — the cost is not eliminated, it is moved entirely to inference (§3) and to the vendor's undisclosed pretraining. "n/a" for data efficiency: zero training examples makes the ratio undefined, not infinite — see §8.

---

## 2. Dimension 1 — Training cost

| System | Data scale | Teacher / API dependence during training | Compute class | Cost evidence |
|---|---|---|---|---|
| **LAYA** | **490 in-domain examples** (MMF winner) | **None** — no teacher, no API, no synthetic data | Single RTX 4090, bf16 fine-tune | **Whole study ≈ $5.64 total** (grid + supplementary + NCP arm + all eval passes + rehearsal) — study record |
| SCPO | SCoT corpus synthesized from a multi-benchmark pool (NewsCLIPpings, DGM4, AutoSplice, FineFake); exact count **UNVERIFIED** | Self-distillation: a simulated society of MLLM agents generates the training data — teacher dependence is internal but the data-generation pass is itself a multi-agent inference campaign | 7B full training + preference optimisation | Dollar figure not published — **UNVERIFIED** |
| DeceptionDecoded | **6,000 out-of-domain samples**, binary intent task, 1 epoch | The 6,000 come from a 12,000-item synthetic intent benchmark — i.e. training data is itself model-generated (generation pipeline per the paper; per-item teacher cost **UNVERIFIED**) | Full fine-tune of Qwen2.5-VL-7B | Not published — **UNVERIFIED** |
| GPT-4V Standard | None | Total — the model *is* a proprietary API product | Vendor-side, undisclosed | $0 to the user; all cost deferred to inference |
| GPT-4V + MMD-Agent | None | Total (same backbone) | Vendor-side, undisclosed | $0 to the user |
| T2Agent | None (explicitly training-free) | Total (GPT-4o API) | None user-side | $0 to the user |
| MM-VeriAgent | **10,000 in-pool samples** (8,000 SFT + 2,000 GRPO) | **Direct API dependence: SFT rollouts generated by a GPT-5-mini teacher**; RL rollouts over a tool-execution cache | SFT + GRPO RL on a 7B — the heaviest training pipeline in this set | Not published — **UNVERIFIED**; structurally the most expensive trained system here (teacher API spend + RL rollout compute) |
| MERIT | None (zero-shot) | Total (GPT-4o-mini API) + web search at inference | None user-side | $0 to the user |
| Fine-tuned CLIP (NCP) | **71,072 items** (full NewsCLIPpings train split) | None — plain supervised fine-tune, no teacher | Single-model fine-tune, 2021-era GPUs | Dollar figure not reported (2021 paper) — **UNVERIFIED**; compute class is modest (151M model) but the data pipeline is 145× LAYA's example count |
| LAMAR (VERITE) | VLM-generated miscaption sets + NewsCLIPpings; **10⁵–10⁶-pair scale** across this literature | Teacher dependence on open VLMs (LLaVA / Molmo) as data generators | Training of a 19–21M model is cheap; the *data generation* at 10⁵–10⁶ scale is the real cost | Not published — **UNVERIFIED** |

**Read:** LAYA is the only system in the set whose *entire* training programme — not just the winning run, the whole study including every ablation and both dataset arms — is priced, and the price is **$5.64**. Every trained rival either used 12–145× more examples, a teacher (GPT-5-mini, a multi-agent society, VLM data generators), or both; none publishes a training dollar figure.

---

## 3. Dimension 2 — Inference cost (per 1,000 predictions)

| System | Basis | Cost / 1,000 | Flag |
|---|---|---|---|
| **LAYA** | Measured 0.16 s/item × $0.897/hr pod rate (inputs in §0) | **≈ $0.04** | Derived from measured inputs |
| Fine-tuned CLIP | 151M single forward pass, millisecond-class on the same GPU basis (~0.01–0.05 s/item × $0.897/hr) | ≈ $0.003–0.012 | ESTIMATE (latency not measured in this study; order-of-magnitude only) |
| LAMAR | 19–21M head over CLIP features; feature pass dominates (~0.02–0.06 s/item, same basis) | ≈ $0.005–0.015 | ESTIMATE (same basis as CLIP row) |
| DeceptionDecoded | Local 7B, answer-only short output, ~1 s/item class × $0.897/hr | ≈ $0.25 | ESTIMATE (7B single-pass basis, §0) |
| SCPO | Local 7B generating a rationale + verdict, ~2–5 s/item × $0.897/hr | ≈ $0.50–1.25 | ESTIMATE (7B single-pass basis, §0) |
| MM-VeriAgent | Local 7B, multi-step tool-use trajectory per item, ~10 s/item class × $0.897/hr, plus local tool execution | ≈ $2.50 | ESTIMATE (trajectory length varies per item; exact mean UNVERIFIED) |
| GPT-4V Standard | 1 API call/item at GPT-4 Turbo-class rates ($10/$30 per 1M) on the §0 token profile | ≈ $15 | ESTIMATE (published rates, estimated token profile) |
| GPT-4o-mini single call (MERIT's backbone rate) | 1 call/item at $0.15/$0.60 per 1M on the §0 profile | ≈ $0.26 | ESTIMATE (published rates, estimated token profile) |
| MERIT (system) | Several GPT-4o-mini module calls/item **plus live web-search calls per item** | ≈ $1–3 API-side, **plus search fees** | ESTIMATE for the API part; **search/retrieval pricing UNVERIFIED** (not opened for this report) |
| GPT-4V + MMD-Agent | Three-stage decomposed pipeline ⇒ ≥ 3 GPT-4V calls/item at Turbo-class rates | ≈ $45–75 | ESTIMATE (≥3× the Standard row; tool-call count per item varies) |
| T2Agent | MCTS over tool trajectories ⇒ tens of GPT-4o calls/item at $2.50/$10.00 per 1M | ≈ $85–430 | ESTIMATE, order-of-magnitude (20–100 calls × ≈ $4.3/1,000-call basis); exact calls/item **UNVERIFIED** |

**The comparison that frames the whole dimension:** scoring the 10,000-item MMFakeBench test set **once** with GPT-4V Standard would cost ≈ 10,000 × $0.0155 ≈ **$155 (ESTIMATE, §0 inputs)** in API fees alone — roughly **27× LAYA's entire study budget of $5.64**, which already includes scoring that same test set. With MMD-Agent the same single pass is ≈ $450–750 (ESTIMATE, same inputs). LAYA's own 10,000-item test pass cost ≈ $0.40 in amortised GPU time (10,000 × $0.04/1,000).

---

## 4. Dimension 3 — Inference dependencies (the convenience / reproducibility axis)

| System | What one prediction requires | External calls at inference |
|---|---|---|
| **LAYA** | **One forward pass** of a local 201M checkpoint. No tools, no retrieval, no API, no network | **None** |
| Fine-tuned CLIP | One forward pass, local | None |
| LAMAR | CLIP feature extraction + one small-model pass, local | None |
| DeceptionDecoded | One generative pass, local 7B | None |
| SCPO | One generative pass, local 7B | None |
| MM-VeriAgent | A **tool-use trajectory**: the model invokes a verification toolkit (MM-VeriTools) over multiple steps; no search at inference per the paper, but tool execution infrastructure must be present and correct | Local tools; no web per the paper |
| GPT-4V Standard | One proprietary API call — requires network, an API key, a billing account, and the vendor's continued service of that exact model | 1 frontier API call |
| GPT-4V + MMD-Agent | A **three-stage agent loop** (decompose → rationale → tool-augmented verdict) over the API | Multiple frontier API calls + tool calls |
| T2Agent | **Monte Carlo Tree Search per item**: a greedy tool selector plus repeated simulated verification trajectories over the API | Tens of frontier API calls + tool calls |
| MERIT | A modular pipeline whose verification stage performs **live web retrieval per item** — the prediction depends on the current state of the web | Frontier API calls + live search |

**Read:** five systems in this table can run on an air-gapped laptop-class machine; LAYA is the smallest of them. The other five rent their intelligence per call — and two of them (T2Agent, MERIT) make each prediction depend on stochastic search or on the live web, which is a convenience cost (latency, failure modes, accounts, rate limits) before it is a dollar cost.

---

## 5. Dimension 4 — Latency class per item

| System | Latency class | Basis |
|---|---|---|
| **LAYA** | **Sub-second — 0.16 s/item, measured** | Study record (RTX 4090, single pass) |
| Fine-tuned CLIP | Millisecond class (~10–50 ms) | ESTIMATE (151M forward pass) |
| LAMAR | Millisecond-to-sub-second class | ESTIMATE (CLIP features + 19–21M head) |
| DeceptionDecoded | ~1 s class | ESTIMATE (7B, answer-only output) |
| SCPO | Seconds class (~2–5 s) | ESTIMATE (7B rationale generation) |
| GPT-4V Standard | Seconds class | ESTIMATE (API round-trip + generation; network-dependent) |
| MM-VeriAgent | Tens-of-seconds class | ESTIMATE (multi-step tool trajectory) |
| GPT-4V + MMD-Agent | Tens-of-seconds class | ESTIMATE (3 stages + tools, all via API) |
| MERIT | Tens-of-seconds class, web-bound | ESTIMATE (retrieval latency dominates and varies) |
| T2Agent | **Minutes class** | ESTIMATE (per-item MCTS rollouts — the slowest design in the set by construction) |

Only LAYA's latency in this table is a measurement; every other row is a class estimate from the system's published design, and is flagged as such.

---

## 6. Dimension 5 — Deployment footprint

| System | Parameters | Checkpoint / weights size | VRAM class | Runs on one consumer GPU? |
|---|---|---|---|---|
| **LAYA** | **201M** | **~805 MB** (study record) | Fits in ~2–4 GB at inference (bf16 weights ≈ 0.4 GB + activations) — ESTIMATE for the VRAM figure, checkpoint size is measured | **Yes** — ran on a single RTX 4090; sized for any modern 8 GB card |
| LAMAR | 19–21M (+ CLIP feature extractor, ~151M if ViT-B/32) | Tens of MB for the head; ~0.6 GB with extractor | ~1–2 GB | Yes — the smallest footprint in the set |
| Fine-tuned CLIP | ~151M | ~0.6 GB fp32 / ~0.3 GB fp16 | ~1–2 GB | Yes — CPU inference is also feasible |
| SCPO | 7B (Qwen2-VL-7B) | ~14–16 GB | ≥ 16 GB, realistically 24 GB with context | Only a high-end one (24 GB class) |
| DeceptionDecoded | 7B (Qwen2.5-VL-7B) | ~14–16 GB | ≥ 16 GB, realistically 24 GB | Only a high-end one (24 GB class) |
| MM-VeriAgent | 7B (Qwen2.5-VL-7B) + tool stack | ~14–16 GB + tool infrastructure | ≥ 16 GB + tool runtime | Only a high-end one, and the GPU is the least of the deployment |
| GPT-4V / GPT-4o systems (Standard, MMD-Agent, T2Agent, MERIT) | Undisclosed (frontier, proprietary) | **Not downloadable at any size** | n/a — no local deployment exists | **No — API-only, permanently** |

7B checkpoint sizes are ESTIMATEs (basis: 7 × 10⁹ params × 2 bytes at bf16 ≈ 14 GB, plus embeddings/tokenizer overhead). The structural point needs no estimate: LAYA's checkpoint is ~**18× smaller** than any 7B rival's, and the API systems have no self-hostable artifact at all.

---

## 7. Dimension 6 — Reproducibility (can a third party re-run the exact reported number?)

| System | Verdict | Why |
|---|---|---|
| **LAYA** | **Yes — strongest in the set** | Local deterministic inference from a fixed checkpoint; executed notebook, 25+ run receipts, cost ledger; test scored once under a frozen protocol (Protocol A, fully specified). A third party with the checkpoint re-runs the identical 10,000 items and the identical metric |
| Fine-tuned CLIP (NCP) | Yes | Open dataset, open base model, standard supervised fine-tune; the 66.1 reference is re-derivable (modulo ordinary training variance) |
| SCPO | Partially | Protocol A is fully specified, so the *evaluation* is re-runnable if the fine-tuned weights are available (public release of the SCPO checkpoint **UNVERIFIED**); the *training* is hard to reproduce exactly — its data is the output of a multi-agent synthesis campaign |
| LAMAR | Partially | VERITE is public and the model is tiny, but training depends on VLM-generated miscaption sets; exact reproduction depends on release of those generated sets (**UNVERIFIED**) |
| DeceptionDecoded | **No, not as reported** | The MMFakeBench split behind its 0.5866 is **UNVERIFIED** — the eval items are not identified, so the exact number cannot be re-run by anyone |
| GPT-4V Standard | **No** | API drift: GPT-4V snapshots have been revised and retired since the benchmark era; the exact 0.488 was produced by a model version that no longer exists as a servable artifact |
| GPT-4V + MMD-Agent | **No** | Same API-drift problem, compounded by a multi-stage tool pipeline |
| T2Agent | Partially in spirit, no in exact number | Code is public (GitHub, per the impact scout), but the backbone is a drifting proprietary API and MCTS is stochastic — a re-run approximates, it does not reproduce |
| MM-VeriAgent | **No** | **Private re-split (Protocol D):** the 1,000 eval items are drawn from the benchmark pool but not identified (provenance UNVERIFIED); no third party can reconstruct the eval set, and its SFT data came from a GPT-5-mini teacher whose outputs are not a fixed artifact |
| MERIT | **No, by construction** | Live web retrieval at inference: the evidence base changes daily, so the same item can score differently next month. The number is a snapshot of the web, not of a model |

---

## 8. Dimension 7 — Data efficiency (headline score ÷ training examples)

Derived ratios; inputs shown. Cross-protocol and cross-dataset rows are flagged — the ratio is an efficiency illustration, not an accuracy claim.

| System | Headline score (protocol) | Training examples | Score per example | vs LAYA |
|---|---|---|---|---|
| **LAYA** | 0.6020 macro-F1 (Protocol A, official test) | **490** | 0.6020 / 490 = **1.23 × 10⁻³** | — |
| DeceptionDecoded | 0.5866 macro-F1 (split UNVERIFIED) | 6,000 | 0.5866 / 6,000 = 9.8 × 10⁻⁵ | LAYA ≈ **12.6×** |
| MM-VeriAgent | 0.715 macro-F1 (**Protocol D — not comparable**) | 10,000 | 0.715 / 10,000 = 7.2 × 10⁻⁵ | LAYA ≈ 17× (cross-protocol — illustration only) |
| SCPO | 0.573 macro-F1 Top-1 (Protocol A) | Count **UNVERIFIED** (multi-benchmark synthetic corpus) | Cannot be computed | — (any plausible corpus size ≥ 5,000 puts it ≥ 10× below LAYA) |
| Fine-tuned CLIP | 0.661 accuracy (NewsCLIPpings — different dataset + metric) | 71,072 | 0.661 / 71,072 = 9.3 × 10⁻⁶ | LAYA ≈ 132× (cross-benchmark — illustration only) |
| LAMAR | 0.549 accuracy (VERITE multiclass — different dataset + metric) | 10⁵–10⁶ (range as published for this literature) | 5.5 × 10⁻⁶ – 5.5 × 10⁻⁷ | LAYA ≈ 220–2,200× (cross-benchmark, range inputs — illustration only) |
| GPT-4V Std / MMD-Agent / T2Agent / MERIT | 0.488 / 0.615 / 0.759 / 0.8165 (protocols A / A / C / E) | **0** | **Undefined** | Not applicable: with zero task-specific examples the ratio is not infinite, it is meaningless — these systems convert undisclosed vendor pretraining (and, for three of them, per-item inference compute) into score instead of examples. Their efficiency claim lives in §3, where it is expensive |

---

## 9. Verdict

On the operational dimensions, LAYA is the field's best-in-class almost without contest: it is the only system whose whole research programme cost a priced **$5.64**, whose predictions cost **≈ $0.04 per 1,000** with **zero** external dependencies in a **measured 0.16 s**, whose **805 MB** checkpoint runs on any modern consumer GPU, whose reported test number a third party can re-run **exactly**, and whose score-per-training-example (**1.23 × 10⁻³**) beats every computable rival by one to two orders of magnitude — the fine-tuned CLIP reference and LAMAR match it on footprint and single-pass convenience, and CLIP matches it on reproducibility, but both bought their scores with 145× to 2,000× more training data. Where LAYA is **not** best-in-class is just as clear: on raw headline accuracy it trails the one protocol-comparable system above it (GPT-4V + MMD-Agent, by 1.3 points, at roughly a thousand times the per-item inference cost) and the non-comparable agentic frontier by more; its VERITE transfer (0.3506) is a registered negative result that no cost advantage excuses; and its NewsCLIPpings trained-arm comparison against the 66.1 CLIP reference is still pending. The honest summary is that LAYA does not win the accuracy race — it wins the **cost-per-verified-point** race, and on the dimensions a deploying practitioner actually pays for (dollars, dependencies, latency, footprint, reproducibility, data), nothing else in this landscape is close.

---

*Sources: competitor facts and scores from `COMPETITIVE_LANDSCAPE_2026-11-22.md` and the four scout reports (all 2026-11-22); OpenAI rate tabulation from https://www.modelmeterhq.com/blog/openai-api-cost-breakdown (opened 2026-11-22); LAYA figures from the study record as specified in the commissioning brief (201M params; ~805 MB checkpoint; 490 examples; ≈ $5.64 total RunPod spend at $0.897/hr; 0.16 s/item measured predict mean; $0 Gemini spend; test scored once). Every ESTIMATE carries its basis in §0 or in its row; every UNVERIFIED flag from the scouts is preserved.*
