# LAYA structure — what can be upgraded for this case — and the noul drill-down design

Analysis document, 2026-11-23. No training and no pod work were run for
this document; everything below is read from the code and records on
this VM. It answers the owner's two linked questions:

1. **Part 1** — check the LAYA structure: which parts can we update or
   upgrade for this case (NewsCLIPpings + VERITE open; MMFakeBench
   solved)?
2. **Part 2** — design the owner's proposed drill-down: varied nouls
   that increase delta but lower alpha, per dataset, separately.

**Sources actually inspected** (paths on this VM):

- `~/workspace/misinfo_run/laya_trainer.py` — the workspace trainer
  (full / head-only / LoRA arms, `soft_ce` loop, calibration helper).
- The laya package source **is present on this VM** — a copy of the dev
  install (laya 0.2.0.dev0, git r33drichards/laya-vision @ 9e1e2419) at
  `~/workspace/misinfo_run/rehearsal_slice/laya_dev/laya/`:
  `vlm.py` (model + `VLMAgent.predict`), `vlm_train.py` (training loop,
  `vlm_loss`, `fit_temperatures_from`), `calibration.py`, `common.py`
  (`QTYPES = {"choice": 0, "score": 1, "noul": 2}`).
- The notebook: `~/workspace/misinfo_run/LAYA_Colab_Staged_For_Review.ipynb`
  (CONFIG: SEED 20261122, STEP_GRID [245, 490, 735], LOSSES
  [rlcd, soft_ce], LR_ENCODER 1e-5 / LR_HEAD 1e-3, MAX_LEN 1024) and
  the executed copy in the repo.
- The pack registry: `~/workspace/misinfo_run/mainrun_artifacts/runs/packs.json`
  (labels, metrics, checkpoints, both question wordings, per pack).
- Calibration records: `runs/full_soft_ce_735_calibrated/calibration.json`
  (temperatures [8.4214, 1.0, 1.0], n_calib 210),
  `runs/ncp_temperature_validation.json` (NCP gate),
  `~/workspace/misinfo_run/CALIBRATION_FINDING_2026-11-22.md` (CAL-1).
- v2 probe: `DESIGN.md` (Amendments 1–10, incl. AM6 noul attunement,
  AM8 ladder), `EVIDENCEGATE_DESIGN.md` (state machine, trigger,
  arbitration), `score_stagea.py`, `score_noul.py`, and the carve
  files (`probe_items.jsonl`, `stageb_items.jsonl`, `stageb_train.jsonl`,
  `stageb_tune.jsonl`, `verite_tune.jsonl`, `verite_test_items.jsonl`).
- Run receipts: `runs/supplementary/supplementary_table.json` and the
  per-config `result.json` files (data curve, LoRA rank ladder).

**The frozen-v1 rule, applied throughout Part 1.** v1 is closed: the
MMFakeBench test split was scored exactly once (0.6020) and the marker
`runs/.test_scored` is written; every v1 verdict (H1–H5) stands as
registered. Nothing below re-opens a v1 number. "Can be changed"
always means: changeable **for v2 / future registered runs**, in a new
pack version or a new registered amendment — never retroactively in
the v1 record.

---

# PART 1 — The LAYA structure, part by part

## 0. The system in one paragraph

`laya.load_vlm("thaitea/laya-vision" @ f2fe3c1)` loads a
`VLMDecisionModel` (201,161,347 parameters): one HF backbone stored as
`model.encoder` (vision tower + connector + language model in a single
object) plus a small typed decision head — a 2-layer TransformerEncoder
over the option markers, a question-type embedding (`type_emb`, 3
types: choice / score / noul), and a per-option `scorer`. One
`agent.predict(state={"context", "image"}, questions={...})` call
answers both of our questions per item: the **choice** question
(native classes; probabilities at
`result["answers"]["native"]["probabilities"]`) and the **noul**
question (binary fake screen; P(Fake) at
`result["answers"]["fake"]["noul"]`). Probabilities come from a
softmax over option logits divided by a **per-question-type
temperature** (stored on the model, with per-option-count buckets).
Our own harness code (packs + scoring scripts, not the library) adds:
the **arbitration rule** (choice headlines; choice/noul disagreement
⇒ `uncertain`), **per-dataset packs**, and — in v2 — **EvidenceGate**
in front of `predict`. Training goes through `laya_trainer.py`, which
wraps the library's `vlm_train.train` (rlcd) and a locally built
CE-only loop (soft_ce).

## 1. Vision tower

- **Now.** Inside `model.encoder`; produces image features via
  `encoder.get_image_features(...)`. **Frozen in both v1 arms** by
  amendment (b): `vlm_train.train` has no `train_vision` passthrough,
  and its `freeze="full"` trains language encoder + head only
  (114,728,323 of 201,161,347 params). The library's own
  `set_trainable(..., mode="full", train_vision=True)` *can* unfreeze
  it, but the training loop we use cannot reach that switch.
- **Changeable without touching v1?** Only via new trainer code in a
  future run (a `train_vision` path would have to be built and
  rehearsed). Not a configuration change.
- **Upgrade options.** (a) Leave frozen (status quo). (b) Build the
  passthrough and unfreeze the tower (or its last blocks) for a
  future run.
- **Expected gain / risk for this case.** Low gain, real risk. The
  open problems are factual pairing (NewsCLIPpings pristine recall
  0.164; VERITE miscaptioned recall 0.000 for BASE and EVIDENCE) —
  failures of *what the caption claims about the world*, not of visual
  feature quality. The one place visual features plausibly bind is
  MMFakeBench's visual-distortion class (winner test recall 0.512,
  the weakest class) — but MMFakeBench is the solved benchmark.
  Unfreezing also breaks the rehearsal-verified training contract and
  spends the scarcest resource (pod time) re-proving stability.
- **Cost.** High: new trainer path + rehearsal + full retrain per
  dataset. **Verdict: do not upgrade for this case.**

## 2. Language encoder (the backbone LM)

- **Now.** Trained in the "full" arm at LR_ENCODER 1e-5 (winner:
  full · soft_ce · 735 on MMFakeBench; full · soft_ce · 245 on
  NewsCLIPpings). This is where essentially all of v1's measured gain
  lives: tune macro-F1 0.2079 → 0.7389 across the grid on MMFakeBench.
- **Changeable?** Yes — it is the normal training surface. Any change
  is a new training run under a new registration.
- **Upgrade options.** (a) More / better-targeted training data
  (Part 1 §11 and the AM8 ladder). (b) The library's unused
  `set_trainable(mode="last_n")` — head + last *n* LM layers only — a
  middle setting between head-only and full, never tried in v1.
  (c) LR variants: the supplementary tier already priced these on
  MMFakeBench (LR 2e-5: 0.7178; LR 5e-6: 0.6438 at 735 steps, vs
  winner 0.7389 at 1e-5) — the shipped LR is already the best of the
  three tried.
- **Expected gain / risk.** Data is the binding constraint, not the
  encoder setting: the supplementary data curve at 490 steps is
  122 items → 0.1168, 245 → 0.3670, 490 → 0.6598. `last_n` is a
  plausible cheaper arm for small carves (VERITE-scale) but is
  unmeasured; expected value is speculative.
- **Cost.** (a) is the AM8 rung-4 run (priced there). (b) is one
  supplementary-tier training per dataset (~minutes of pod time each
  at v1 step counts).

## 3. Decision head (head transformer + type_emb + scorer; act_head)

- **Now.** 2-layer TransformerEncoder over option markers +
  `type_emb` (one embedding per question type — this is how the same
  head serves choice, score, and noul) + per-option `scorer`
  (LayerNorm → Linear → GELU → Linear → 1). Head-only training
  (8,462,659 params) was a supplementary arm: head · soft_ce scored
  0.4238 (490) and **degraded with more steps** (0.3098 at 735, receipt
  loss rising 0.635 → 1.020) — the head alone cannot carry the task.
  The model also carries an `act_head` (action probabilities) and
  optional value/next heads; **our pipeline never uses them** —
  verdicts come only from choice + noul.
- **Changeable?** Head architecture is library/checkpoint structure —
  changing it means a different checkpoint, i.e. a different study.
  Head *training* (as an arm) is changeable per run.
- **Upgrade options.** None worth taking for this case. The head is
  not the bottleneck: with the encoder trained, the same head reaches
  0.7389 tune F1; frozen-encoder head-only training collapses. The
  unused `act_head` is not a verdict signal we have any validation
  for.
- **Cost / verdict.** Skip. Spend nothing here.

## 4. LoRA adapters

- **Now.** peft over the encoder (r16 / α32 / dropout 0.05, LR 1e-3),
  merged and saved as a plain checkpoint. v1 grid: LoRA · soft_ce
  reached 0.7187 at 735 (vs full 0.7389); LoRA · rlcd collapsed at 735
  (0.1946).
- **Changeable?** Yes, per run — rank, alpha, targets, LR are trainer
  arguments.
- **Upgrade options.** Rank is the lever, and v1's supplementary
  ladder measured it at the winner's loss: **r8 0.7037 (490 steps) >
  r16 0.5726 (490, grid) > r32 0.1168 (490) / 0.2244 (735)** — r32's
  receipt loss *rose* during training (0.762 → 1.036), a genuine
  collapse, not a plateau.
- **Expected gain / risk.** For future *small-carve* runs
  (VERITE-scale, Stage-B-scale), r8 is the evidence-backed default
  and r32 is a measured hazard. For the headline arms, full fine-tune
  already beat every LoRA setting tried.
- **Cost.** Trivial (argument change). **Verdict: adopt r8 as the
  default for any future small-carve LoRA run; never r32 at this
  data scale.**

## 5. Loss functions (rlcd vs soft_ce) and their knobs

- **Now.** `rlcd` = the library's native objective (`vlm_loss`:
  proper-scoring-rule policy gradient over noisy logits, sigma=0.3,
  group_size=4, w_sph=0.75, plus w_ce=1.0 × soft cross-entropy).
  `soft_ce` = the cross-entropy term alone, implemented in
  `laya_trainer._train_soft_ce` because `vlm_train.train` offers no
  switch to remove the policy-gradient term. Result: **soft_ce beat
  rlcd in all 6 matched grid pairs** (average ≈ +0.10 tune F1), and
  the paper's claim is scoped to this recipe pending the rlcd-identity
  verification item.
- **Changeable?** Yes, per run. `vlm_train.train` also exposes two
  knobs v1 never used: `w_ce_schedule="anneal"` (CE weight decays to
  0 between 30% and 80% of progress) and `sigma_end` (exploration
  noise annealing).
- **Expected gain / risk.** Low expected gain: the objective question
  is already answered for this recipe family, and the open benchmarks
  fail on information (pairing facts), not on optimisation. The
  anneal knobs are cheap lottery tickets, not a plan.
- **Cost.** One supplementary run each. **Verdict: keep soft_ce;
  do not spend on loss variants for this case.**

## 6. The two questions — wording, criteria, option order

- **Now.** Each pack carries both questions verbatim (`packs.json`).
  The **choice** wording is shared across packs ("Using only the
  supplied content, which dataset label best describes this item? …")
  with per-dataset criteria text. The **noul** wording is currently
  **identical in all three packs** — a generic benchmark-label
  estimate ("Would the dataset assign the item a falsified, distorted,
  miscaptioned, or out-of-context label rather than its original,
  pristine, or true label? …") with generic false/true criteria. It
  asks the model to predict *the dataset's label*, not to judge the
  item — a framing choice v1 never varied. Wording is pure input:
  the criteria strings are rendered into the prompt by `predict`, so
  changing wording needs **no code and no retraining** — but it
  changes the instrument, so it belongs in a registration (Part 2).
  `predict` also supports `n_permutations > 1`: scoring under several
  option orders and averaging logits, built to reduce causal
  option-order bias; v1's closing analyses included an option-order
  robustness check, but the headline passes ran at the default.
- **Changeable?** Yes — per pack, per registered run. This is the
  cheapest moving part in the whole system.
- **Evidence on gain / risk.** Both directions are measured:
  - *Headroom:* the NewsCLIPpings noul is nearly uninformative as
    shipped (Amendment 6B records AUC 0.529, mean confidence 0.5002
    on the v1 val pass) — there is almost nothing to lose and a real
    instrument to gain. On VERITE the noul currently contributes
    nothing beyond arbitration noise (all four arms sit at
    0.285–0.330 on the held-out 200).
  - *Risk:* wording effects are large relative to our sample sizes —
    the receipt deep check found the **same rows and checkpoint**
    scoring differently in October vs the pod run (e.g. MMFakeBench
    val accuracy 0.320 → 0.293) purely from choice-question wording,
    i.e. **±~0.03 phrasing swings**. Any wording "win" smaller than
    that, selected on a small slice, is likely noise — which is
    exactly what Part 2's discipline is built against.
- **Upgrade options.** (a) The Part 2 drill-down: per-dataset noul
  wordings, selected on reserved data only. (b) Option-order
  permutation averaging (`n_permutations` ≥ 4) at inference for
  reporting passes: reduces order variance on small-n evaluations;
  cost is a multiple of predict rows, softened by the prefix cache
  (images encoded once). (c) Choice-wording variants — *not*
  recommended now: the choice question is the headline metric's
  instrument in every registered comparison; varying it mid-study
  breaks comparability. Noul first.
- **Cost.** (a) ≈ 13 minutes of GPU total (Part 2 §6). (b) ~4× the
  rows of a reporting pass — minutes at 0.16 s/item.

## 7. Arbitration rule

- **Now.** Ours, not the library's (`EVIDENCEGATE_DESIGN.md` §4,
  `score_stagea.py`): the choice verdict headlines; the noul is read
  at the pack threshold (0.5); **choice/noul disagreement ⇒ verdict
  `uncertain`**, and in headline accuracy an `uncertain` counts as
  wrong. In the EvidenceGate the same disagreement is also a routing
  signal. Amendment 5 adds a flip policy for the evidence arm (a flip
  to pristine needs ≥ 1 binding passage; a flip to falsified needs a
  binding contradiction or ≥ 2 independent-domain passages).
- **Changeable?** Yes — it is scoring code, changeable per registered
  run without touching any model. But it is part of every registered
  scoring sheet, so changing it changes what the numbers mean.
- **Upgrade options.** (a) Let the noul *veto* or *override* in
  defined bands instead of only flagging disagreement. (b) Report
  arbitration with the fitted per-pack threshold (Part 2) instead of
  the flat 0.5. (c) A learned arbitrator (stacker over choice + noul
  probabilities) — that is the fusion design, which waits on
  teammates' files and is out of scope here.
- **Expected gain / risk.** (b) is nearly free and composes with
  Part 2. (a) is dangerous while the noul is near chance on
  NewsCLIPpings (AUC 0.529): giving a coin-flip instrument veto power
  over the choice verdict would *lower* headline accuracy. Upgrade
  the noul first (Part 2); revisit arbitration only with a noul that
  has measured AUC to stand on.
- **Cost.** (b) zero beyond Part 2. **Verdict: keep the rule; feed
  it a better noul and a fitted threshold.**

## 8. Calibration — per-type temperatures + the noul threshold

- **Now.** `predict` divides logits by a stored temperature per
  question type (choice / score / noul), with per-option-count
  buckets on top. `fit_temperatures_from` fits the three temperatures
  on a reserved calib split. v1's MMFakeBench fit gave
  [8.4214, 1.0, 1.0] (choice only; noul temperature never moved from
  1.0 in any v1 fit). Every pack currently ships `temperatures: null`
  and `noul_threshold: 0.5`.
- **The CAL-1 evidence (the controlling fact for this part).** The
  calib-fitted choice temperature 8.4214 cut in-sample ECE
  0.2664 → 0.0865 but **worsened held-out ECE 0.1056 → 0.3955** on
  MMFakeBench val: a temperature is a property of model ×
  distribution, not of the model. The split-half demonstration (fit
  on half A, measure on disjoint half B) worked: T = 1.65, ECE
  0.0994 → 0.021. Disposition: the Space ships T = 1.0. The
  NewsCLIPpings gate reached the same end by its own road: fitted
  pack temperatures [3.857, 2.100, 3.053] gave held-out ECE 0.0127
  vs raw 0.0120 on 7,024 val rows — no improvement — decision
  `ship_T1.0` (`ncp_temperature_validation.json`).
- **Changeable?** Yes — temperatures and the threshold are pack-level
  numbers, fitted post-hoc, no retraining. The library even ships
  the CAL-1-safe machinery: `calibration.py`'s `out_of_fold` fit
  (each row's temperature fitted on the *other* folds).
- **Upgrade options.** (a) Per-pack temperatures fitted on reserved
  data and **validated on a disjoint held-out slice before shipping**
  (the CAL-1 rule), using out-of-fold fitting where the slice is
  small. (b) A fitted noul threshold per pack instead of the flat
  0.5 — AM6B.2 already registers exactly this for Stage B (threshold
  maximising balanced accuracy on the calib slice); Part 2
  generalises it. (c) Nothing else: temperature cannot change any
  argmax, AUC, or ranking — it buys honest probabilities (ECE) and
  better threshold behaviour, never accuracy by itself.
- **Cost.** Minutes of CPU/GPU on stored logits. **Verdict: adopt
  (a) + (b) as standing pack hygiene; never ship an unvalidated
  temperature again.**

## 9. Per-dataset packs

- **Now.** `packs.json` holds, per dataset: labels + display names,
  native metric, splits, base + deployed checkpoint pointers, both
  question wordings, `temperatures: null`, `noul_threshold: 0.5`.
  MMFakeBench → the v1 winner; NewsCLIPpings → the NCP winner;
  VERITE → the base checkpoint (its track's ADAPTED model lives in
  the side-arm record). Selecting a pack switches questions, labels,
  threshold, and checkpoint together.
- **Changeable?** Yes — packs are our configuration, versioned with
  the runs that use them. A changed pack is a new pack version; v1's
  pack state is part of the v1 record and stays as-is.
- **Upgrade options.** The pack is the *delivery vehicle* for every
  other upgrade in this list: Part 2's winner (wording + temperature
  + threshold) lands as pack fields; Arm W joins as a pack-level
  gate block (EVIDENCEGATE_DESIGN §2: additive `gate` block, v1 keys
  untouchable). No structural change needed.
- **Cost.** Zero beyond the upgrades it carries.

## 10. EvidenceGate — routing, retrieval, harness

- **Now.** A pluggable state machine in front of `predict`:
  Intake → Route → (PairOnly | Retrieve) → Judge → Arbitrate → Done,
  modes `off` / `on` / `auto` per pack (NewsCLIPpings `on`,
  MMFakeBench `off`). The `auto` trigger fires retrieval when the
  pair-only top-2 choice margin < **MARGIN_TAU = 0.20** or on
  choice/noul disagreement (NOUL_TAU = pack threshold = 0.5).
  Retrieval = SearXNG transport + a small-model harness (query
  expansion, triage with binding/corroboration tagging, selection
  into the token budget), everything frozen into hashed snapshots.
  Registered upgrades already in force: **Amendment 10 — Arm W
  (frozen local Wikipedia index, no rate wall) runs BEFORE Arm L
  (live web)** at the next registered run; pilot coverage measured
  29/30. Variant C (fine-tuned local Qwen3-8B harness) is built but
  **deferred** under Amendment 7's scoping rule; the probe's
  instrument is flash (variant B).
- **Changeable?** Yes — it is v2's own component, detached ⇒
  byte-identical to v1 (detach-correctness proven on 300 items).
- **Upgrade options.** (a) Arm W first (registered, built, coverage
  measured — the cheapest reliability upgrade in the whole system:
  it deletes the failure class that broke the probe's batch
  retrieval). (b) Trigger calibration: MARGIN_TAU 0.20 was spec'd
  before the board noted that at NewsCLIPpings' mean confidence
  0.5002 it fires on ~100% of items — fitting the trigger per pack
  on tune data (board item 7/8) turns `auto` from always-on into an
  actual budget instrument. (c) Binding-evidence quality: the board's
  #1 finding — corroboration is not binding, and text search mostly
  manufactures corroboration; the only known binding manufacturer is
  image-side search (reverse image search is dead at $0 — TinEye
  test, two independent failure reasons; a self-hosted SSCD index is
  the full-study route).
- **Expected gain / risk.** This is the only part of the system with
  a mechanism for the actual failure: per-item factual pairing.
  Every system above ~85 on NewsCLIPpings in the literature is
  evidence-based; the no-evidence ceiling is ~66–71 with 35× our
  training data. Risk is equally measured: Stage A's registered
  sheet (delta ≥ +5 pp, CI excludes 0, coverage ≥ 60%) exists
  precisely because the gain is not guaranteed — transplanted
  captions corroborate well, which is why binding tagging and the
  flip policy are already in the design.
- **Cost.** Arm W: built. Trigger fit: tune-data pass, minutes.
  Judging: the pod phase now running.

## 11. Training data (the part that is not code)

Listed because the evidence keeps pointing here: the data curve
(§2), the rank ladder (§4), and the hard-negative design in AM8
rung 4 (captions swapped within the same source/event, so the model
must learn the *pairing*) are all data upgrades. For VERITE, the
80:20 track already showed in-benchmark adaptation ≈ transfer
(+0.010, CI [−0.080, +0.095], criterion not met) at 701 training
items — more of the same data is not obviously the answer there;
for NewsCLIPpings the ladder's rung 4 (10–20k carve) is the
registered next step if Stage B is flat.

## Part 1 — ranked upgrades for THIS case

Ranking is by expected value against the two open problems
(NewsCLIPpings, VERITE), priced with the evidence above:

1. **The noul drill-down (Part 2).** The noul is the weakest
   measured instrument in the system (NCP AUC 0.529 ≈ chance; one
   generic wording shared by all packs; threshold never fitted
   outside AM6). The fix is inference-only, per-dataset, and costs
   ≈ 13 minutes of GPU. Highest value per dollar in the study.
2. **EvidenceGate with Arm W first + per-pack trigger fit.**
   Already registered and mostly built; it is the only mechanism
   aimed at factual pairing, and Arm W removes the retrieval
   failure class the probe actually suffered. Stage A/B will price
   its accuracy honestly.
3. **Hard-negative + larger-carve pair training (AM8 rung 4).**
   The data curve says data is the binding constraint on the
   training side; caption-swap negatives target the pairing skill
   directly. Executes only if Stage B is flat, per the ladder.
4. **Held-out-validated per-pack calibration as standing hygiene**
   (out-of-fold temperatures + fitted noul thresholds, shipped only
   when they survive a disjoint slice — the CAL-1 rule). Near-zero
   cost; buys honest probabilities and a sane trigger/arbitration
   operating point; never buys accuracy by itself.
5. **Option-order permutation averaging on reporting passes**
   (`n_permutations` ≥ 4). Native library support, minutes of
   compute, and it directly shrinks the ±0.03 wording/order noise
   that dominates our small-n comparisons.

Explicitly **not** ranked: unfreezing the vision tower (§1), head
architecture changes (§3), loss-schedule knobs (§5), choice-wording
variants (§6c) — each either lacks a mechanism for the open
failures, breaks comparability, or spends pod time re-proving
stability for speculative gain.

---

# PART 2 — The noul drill-down: design

The owner's proposal, in his words: *"drill down on different varied
nouls that increase delta but lowers alpha across the dataset
separate for each."* This section turns that into a registered,
contamination-safe sweep. It is a **design only** — nothing here runs
until the owner approves the amendment text in §9 (AM7).

## 1. What is being varied, and what the words mean

Per dataset pack, separately (mmfakebench / newsclippings / verite),
we vary the pack's **noul** along three axes:

- **Wording** — the noul question's instructions + criteria text
  (6 candidate wordings per dataset, §3; W0 is the current pack
  wording, kept as the control).
- **Threshold τ** — the P(Fake) cut that turns the noul into a
  binary call. Post-hoc on stored scores: costs no inference.
- **Temperature T** — the noul qtype temperature applied to the
  noul logits before the softmax. Also post-hoc **if raw logits are
  captured** (the judge harness must store the noul logit gap, via
  `predict`'s `_raw_logits` channel, not only the rounded
  probability). AUC is invariant to T and τ; ECE depends on T;
  delta and alpha depend on (wording, T, τ) jointly.

**Definitions (registered, per dataset).** For a variant
*v* = (wording, T, τ) judged by the pack's deployed checkpoint on a
set of items with gold labels:

- **delta (Δ)** — the variant's gain: paired accuracy of the noul
  binary call (noul ≥ τ ⇒ fake) **minus** the accuracy of the frozen
  baseline noul (W0, T = 1, τ = 0.5, same checkpoint) on the *same*
  items. Reported in percentage points with a paired resampling
  95% CI (2,000 resamples, seed pinned — the study's house method).
  Secondary: the **arbitration delta** — headline accuracy change
  when the variant noul replaces the baseline noul in the
  disagreement rule, choice probabilities frozen.
- **alpha (α)** — the false-positive rate, explicitly:
  **α = P(noul ≥ τ | the item is truly not fake)** — gold
  `original` (MMFakeBench), gold `pristine` (NewsCLIPpings), gold
  `true` (VERITE). This is the rate at which the screen cries fake
  on genuine items — the number a newsroom deploying the screen
  feels first.
- **AUC** — ROC AUC of the raw noul score (wording quality,
  threshold-free), computed as in `score_noul.py`.
- **ECE** — 10 equal-width bins, as in `score_noul.py`, at the
  variant's fitted T and at T = 1.

**Selection objective (the owner's "increase delta, lower alpha",
made mechanical).** Among the variants for a dataset, a variant is
*admissible* iff **α_variant ≤ α_baseline** on the selection set.
The winner is the admissible variant with the highest Δ; ties break
to lower α, then lower ECE. The full Δ–α frontier for all six
wordings is reported per dataset — the frontier is a result even
when no variant is admissible.

## 2. Which checkpoint, which context

The drill-down tunes the noul of the checkpoint each pack would
deploy:

- **MMFakeBench:** the frozen v1 winner (`full_soft_ce_735`). Its
  test split is closed; nothing here touches it (§4).
- **NewsCLIPpings:** the **Stage B model** (post-AM6 attunement),
  judged in the evidence context for the headline sweep and in the
  pair-only context as the control column — mirroring AM6's 2×2.
  Sequencing with AM6 is specified in §7.
- **VERITE:** the track's **ADAPTED** checkpoint (245 steps,
  tune-selected), with BASE carried as the control column. The
  EVIDENCE arm's noul is out of scope for AM7 (its registration
  froze the pack questions verbatim).

## 3. The candidate wordings (registered verbatim; no additions after results)

W0 is the current pack wording, identical in all three packs today:

> **W0 (control).** Instructions: "Would the dataset assign the item
> a falsified, distorted, miscaptioned, or out-of-context label
> rather than its original, pristine, or true label? This is a
> benchmark-label estimate, not an independent fact-check."
> Criteria — false: "The native benchmark label is original,
> pristine, or true." / true: "The native benchmark label denotes a
> distortion or incorrect pairing."

Each variant below replaces the instructions; criteria stay
false = "the item is not fake under this question's framing" /
true = "the item is fake under this question's framing" unless a
dataset-specific criteria pair is written out. (Criteria wording is
part of the instrument and is frozen with the variant.)

### MMFakeBench (fake = textual distortion, visual distortion, or mismatch)

- **W1 — direct probability.** "What is the probability that this
  item is not an original, undistorted benchmark item — that its
  text is fabricated or altered, its image is manipulated, or the
  image and text do not match?"
- **W2 — truth-framed (drops the benchmark-label framing).** "Judge
  the item itself, not the dataset: is anything about this
  image–text pair fabricated, manipulated, or mismatched?"
- **W3 — decomposed checklist.** "Check three things: (1) is the
  text's factual content invented or altered? (2) is the image
  visually manipulated? (3) do the image and text fail to
  correspond? If any answer is yes, the item is fake."
- **W4 — conservative.** "Call this item fake only if the distortion
  is clear and specific — a fabricated claim, a visible
  manipulation, or an obvious mismatch. If the item looks like an
  ordinary original, answer not fake." *(Designed to lower α.)*
- **W5 — pairing-first.** "Does the text truthfully go with this
  image, exactly as presented? If the pairing, or either part, has
  been distorted in any way, the item is fake."

### NewsCLIPpings (fake = falsified: a repurposed / incorrect pairing)

- **W1 — direct probability.** "What is the probability that this
  caption was not originally published with this image — that the
  pairing was repurposed from a different event, place, or time?"
- **W2 — original context.** "Was this photograph originally taken
  for the event this caption describes? If the photo comes from a
  different occasion than the caption claims, the pairing is fake."
- **W3 — entity check.** "Compare the people, place, and event named
  in the caption against what the image actually shows. If the image
  shows a different person, place, or event than the caption
  describes, the pairing is fake."
- **W4 — conservative.** "Call this pairing fake only if the image
  clearly belongs to a different event than the caption describes.
  Ordinary news photos with matching captions are not fake."
  *(Designed to lower α — the pristine-recall failure (0.164) is an
  α-side failure of the choice head; this tests whether a strict
  noul can hold the line the choice head cannot.)*
- **W5 — truth-framed.** "Does this caption truthfully describe
  this image as it was originally published?"

For the evidence context, each wording is used with the registered
evidence preamble exactly as AM6B.1 composes Stage B records (state =
caption + §6.1 evidence block); the wording text itself does not
change between contexts.

### VERITE (fake = miscaptioned or out-of-context)

- **W1 — direct probability.** "What is the probability that this
  image–caption pair is not simply true — that the caption
  misdescribes the image, or the image is being used outside its
  original context?"
- **W2 — decomposed, two failure modes.** "A pair fails in two ways:
  the caption says something false about the image (miscaptioned),
  or a real image is used to support a claim from a different
  context (out-of-context). If either failure is present, the pair
  is fake."
- **W3 — original context.** "Was this image originally published
  with this caption, for this event? If it was taken from an earlier
  or different event, the pair is fake."
- **W4 — conservative.** "Call this pair fake only if the caption is
  clearly false about the image or the image clearly comes from a
  different event. If the caption plausibly describes the image,
  answer not fake." *(Designed to lower α; VERITE's BASE arm already
  shows the opposite disease — true recall 0.246 against OOC recall
  0.586 — so α discipline is the live question on this pack.)*
- **W5 — claim-framed.** "Treat the caption as a claim about the
  image. Is the claim true of this image in its original context?"

## 4. Item sets (exact; all from files already on disk)

Selection happens **only** on reserved train-side data. Reporting
splits are touched exactly once, by the frozen winner (§5).

| Dataset | Selection set (variants compared here) | n items | Reporting set (winner only, once) | n |
|---|---|---|---|---|
| MMFakeBench | finetune-dev **tune** (105 items) + **calib** (105 items), pooled — both are train-side dev slices; neither is val or test | 210 | **val** (the v1 reporting split; test stays closed) | 1,000 |
| NewsCLIPpings | Stage B carve **tune-100 + calib-100** (`stageb_items.jsonl` splits; official TRAIN split; evidence from the frozen snapshots) | 200 | **probe 300** (`probe_items.jsonl`, val; 152 pristine / 148 falsified) — sequenced after Stage B scoring freezes (§7) | 300 |
| VERITE | side-arm **tune carve** (`verite_tune.jsonl`: 100 items × native+binary records, from the train side of the frozen 80:20 split) | 100 | **held-out 200** (`verite_test_items.jsonl`) | 200 |

Notes on reuse, disclosed rather than hidden: the MMFakeBench calib
slice carried v1's temperature fit and the VERITE tune carve carried
the side-arm's step selection — both are *selection-side* reuses
(fitting on data already used for fitting), never reporting-side.
The NewsCLIPpings probe 300 already carries Stage A/B's registered
comparisons; the AM7 winner's single evaluation there is a new,
separate registered comparison (§7), reported beside — never folded
into — the Stage A/B verdicts.

## 5. Procedure and holdout discipline

1. **Capture.** For each dataset, for each of the 6 wordings, run
   the pack's deployed checkpoint over the selection set, storing
   per item: gold, the raw noul logit gap, P(Fake) at T = 1, and
   the frozen choice probabilities (choice is *not* re-judged —
   arbitration deltas reuse it). One pass per wording; the choice
   question is not re-run.
2. **Fit per wording, on the selection set only.** AUC per wording
   (T-invariant). Temperature per wording: scalar minimising
   selection-set NLL (the AM6B.2 method). Threshold per wording:
   grid τ ∈ {0.300, 0.325, …, 0.700} (17 points, post-hoc), chosen
   by the §1 objective (max Δ subject to α ≤ α_baseline).
3. **Freeze.** Apply the §1 selection rule. A winner is frozen into
   the pack **only if Δ ≥ +3 pp** on the selection set (the margin
   exists because v1 measured ±~0.03 pure-phrasing swings — a
   smaller "win" is inside instrument noise) **and** it is
   admissible on α. If no variant clears, **W0 stands** and the
   frontier is reported as the finding — the same flat-is-a-finding
   discipline as AM6B.3. No wording may be added, edited, or
   re-run after selection results are seen.
4. **Evaluate once.** The frozen winner (or W0, if none) is run
   **once** on the reporting set and reported with Δ, α, AUC, ECE
   beside the baseline noul's numbers on the same items. All six
   wordings' *selection-set* numbers are published with it, so the
   size of the selection search is never hidden.
5. **Pack write-back.** The winner's wording + fitted T + fitted τ
   are written into the pack as a new pack version, with the
   selection provenance recorded (set, n, date, this amendment).
   v1 pack state is untouched.

**Multiple-comparison control, stated plainly.** Five non-control
wordings × three datasets is fifteen chances to fool ourselves, and
the per-wording τ/T fits add more. The controls are: (i) selection
and reporting on disjoint sets, always; (ii) the +3 pp freeze
margin, set at the measured phrasing-noise scale; (iii) full
publication of every variant's selection numbers; (iv) exactly one
reporting evaluation of exactly one frozen winner per dataset;
(v) Δ reported with its resampling CI on both sets. A Bonferroni
correction across the five wordings is *not* applied to the
selection rule — the holdout discipline above is the stronger and
more honest control at these sample sizes — but the uncorrected
selection CIs are labelled as such wherever they appear.

## 6. Size and cost

Per wording, one predict per item on the selection set (noul-only
capture; the 0.16 s/item figure is the v1-measured full-predict
rate, so this is a conservative upper bound):

| Phase | Calls | GPU time @ 0.16 s |
|---|---|---|
| Selection: 6 wordings × (210 MMF + 200 NCP + 100 VERITE) items | 3,060 | ≈ 8.2 min |
| NCP evidence-context column (second context, selection set) | +1,200 | ≈ 3.2 min |
| Reporting: 1 winner × (1,000 + 300 + 200) items | 1,500 | ≈ 4.0 min |
| **Total** | **≈ 5,760** | **≈ 15.4 min ≈ $0.25 at $0.897/hr** |

The τ grid (17 points) and T fits are analytic on stored logits:
zero additional inference. For scale: this entire sweep costs less
than one supplementary training run from v1.

## 7. How AM7 composes with AM6 (attunement) — order of operations

AM6 **trains** the noul; AM7 **selects its wording, threshold, and
temperature**. They compose in this fixed order, and neither
re-opens the other:

1. **AM6B.1** — Stage B training: both question forms (registered
   attuned choice + noul wordings) against the evidence context.
2. **AM6B.2** — the registered calib fit: noul temperature + pack
   threshold fitted on the carve calib-100. *This fit is the AM7
   control configuration's fitted values for W0 in the evidence
   context* — AM7 does not refit it inside Stage B's own report.
3. **AM6B.3** — the 2×2 before/after noul report on the probe 300,
   computed with the registered wordings, **frozen**. AM7 runs only
   after this report exists; nothing AM7 finds changes it.
4. **AM7** — the drill-down of this section, on the Stage B model,
   selecting on carve tune+calib (200 items — a superset of AM6's
   calib-100, all train-side). If a winner freezes, it becomes the
   NCP pack's *next* version and is evaluated once on the probe as
   a separate post-Stage-B comparison.
5. For MMFakeBench and VERITE there is no AM6; AM7 applies directly
   to their deployed checkpoints (§2) under the same discipline.

AM6B.3's rule — "no re-fitting, no threshold shopping on probe
items" — is inherited by AM7 unchanged: **all** shopping happens on
carve data; the probe and the other reporting sets are only ever
*evaluated*, once, by a frozen configuration.

## 8. Failure risks, named in advance

- **Wording overfitting at small n.** Selection sets are 100–210
  items; a 95% CI on a single accuracy at n = 100 is ±~10 pp, and
  v1 measured ±~0.03 swings from phrasing alone. Mitigations: the
  +3 pp freeze margin, paired (same-item) deltas instead of raw
  accuracies, full-frontier publication, and the standing
  possibility that the honest result is "no variant beats W0" —
  which is itself a publishable measurement of the noul's ceiling
  under wording alone.
- **The noul may simply have no signal to unlock.** On
  NewsCLIPpings the shipped noul sits at AUC 0.529; wording changes
  redistribute a fixed representation's errors — they can trade α
  against Δ along a frontier, but if the underlying ranking is
  chance, no point on the frontier is good. AM7 measures the
  frontier; it does not promise a point on it. (This is why AM7
  ranks *with* the evidence and training upgrades in Part 1, not
  instead of them.)
- **α–Δ trade-off masquerading as improvement.** A conservative
  wording (W4) can lower α by calling almost nothing fake — Δ
  computed on accuracy will punish that on balanced sets, and the
  admissibility rule (α ≤ baseline *and* max Δ) plus the frontier
  publication keep the trade visible rather than letting one
  number hide it.
- **Instrument drift between contexts.** A wording selected in the
  pair-only context may behave differently against evidence
  context; hence the NCP sweep runs both contexts on the selection
  set (§6) and the pack records which context its winner was
  selected in.
- **VERITE tune-carve double use.** The 100-item tune carve already
  selected ADAPTED's step count. Reusing it for noul selection is
  disclosed in §4; the held-out 200 remains untouched by any
  selection, which is what protects the reporting number.

## 9. Registration-ready amendment text (AM7 — proposal, not yet registered)

> ## Amendment 7 — Noul drill-down: per-dataset wording / threshold /
> temperature selection (PROPOSED 2026-11-23; not in force until the
> owner approves)
>
> Owner proposal: vary the noul per dataset to find variants that
> increase delta while lowering alpha. This amendment registers that
> sweep. It changes no v1 record, no Stage A/B registration, and no
> AM6 term; AM6B.3's ban on threshold shopping on probe items is
> inherited unchanged.
>
> 1. **Scope.** Per pack (mmfakebench / newsclippings / verite),
>    separately: the pack's deployed checkpoint (MMF: v1 winner;
>    NCP: the Stage B model; VERITE: ADAPTED) is judged with six
>    noul wordings — W0 (the current pack wording, control) and
>    W1–W5 as written verbatim in
>    `LAYA_STRUCTURE_AND_NOUL_DRILLDOWN.md` Part 2 §3. No wording
>    may be added or edited after any selection result is seen.
> 2. **Selection sets (only).** MMF: finetune-dev tune + calib
>    pooled (210 items). NCP: Stage B carve tune-100 + calib-100
>    (200 items, frozen evidence snapshots; pair-only context as
>    control column). VERITE: side-arm tune carve (100 items).
>    Reporting sets (MMF val 1,000; NCP probe 300; VERITE held-out
>    200) are never used for selection, fitting, or comparison of
>    variants.
> 3. **Measurements.** Per variant: raw noul logits are captured.
>    AUC (threshold-free); temperature fitted per wording by
>    selection-set NLL; threshold from the grid 0.300–0.700 by
>    0.025. **delta** = paired accuracy of the noul binary call
>    minus the frozen baseline noul (W0, T = 1, τ = 0.5) on the same
>    items, with a 2,000-resample paired 95% CI. **alpha** =
>    P(noul ≥ τ | gold original / pristine / true). ECE in 10
>    equal-width bins at fitted T and at T = 1. The arbitration
>    delta (variant noul in the disagreement rule, choice frozen)
>    is reported as a secondary measure.
> 4. **Selection rule.** A variant is admissible iff its alpha ≤
>    the baseline noul's alpha on the selection set. The winner is
>    the admissible variant with the highest delta (ties: lower
>    alpha, then lower ECE), and it is frozen into the pack **only
>    if delta ≥ +3 pp**; otherwise W0 stands and the full delta–
>    alpha frontier for all six wordings is reported as the finding.
>    All variants' selection-set numbers are published with the
>    result.
> 5. **Evaluation.** The frozen winner (or W0) is evaluated **once**
>    on the pack's reporting set and reported beside the baseline
>    noul on the same items. For NewsCLIPpings this evaluation runs
>    only after Stage B's registered scoring (incl. the AM6B.3
>    report) is frozen, and is reported as a separate post-Stage-B
>    comparison. The MMFakeBench test split is not touched; it
>    remains closed.
> 6. **Pack write-back.** A frozen winner's wording, temperature,
>    and threshold are written into the pack as a new pack version
>    with selection provenance (set, n, date, this amendment). If
>    no winner freezes, the pack is unchanged and the frontier is
>    the deliverable.

*(Numbering note: DESIGN.md already carries an "Amendment 7" — the
variant-C deferral recorded 2026-11-23. If the owner approves this
proposal, it should be pasted as **Amendment 11** (the next free
number) with the label adjusted; the text above is otherwise
paste-ready.)*

## 10. Plain-words summary (for the owner)

LAYA is a small judge with a few moving parts: eyes (frozen, and
fine as they are), a reading brain (this is what training improves,
and it improves mostly when we feed it more and better-matched
examples), a scoring head (not the problem), the exact questions we
ask it, a rule for when its two answers disagree, and per-dataset
settings packs. The weakest measured part is the second question —
the "noul", our fake-screen: on NewsCLIPpings it is barely better
than a coin flip, and all three datasets currently share one generic
wording that asks the model to guess the dataset's label instead of
judging the item. Your drill-down idea is the cheapest strong move
left: for each dataset separately, try six wordings of that
question, tune its cut-off and its confidence scaling on practice
data only, keep the version that catches more fakes (higher delta)
while crying fake less often on genuine items (lower alpha), lock
it in, and test it once on the real exam set. The whole sweep costs
about fifteen minutes of GPU time. It composes cleanly with the
attunement already registered: attunement trains the noul,
the drill-down then picks how the trained noul is asked and read.
And it is honest about its own limit — if no wording beats the
current one by a real margin, we keep the current one and publish
the full map of what we tried.
