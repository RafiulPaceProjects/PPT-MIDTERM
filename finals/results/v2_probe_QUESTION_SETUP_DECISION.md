# Question Setup Decision — Single Noul vs a Multiple-Questions Pass

Status: DECISION DOCUMENT (owner review). This document does not edit
DESIGN.md or any registration. On the owner's approval, §5 is pasted
into DESIGN.md as an update to Amendment 11 (the noul drill-down,
registered from `LAYA_STRUCTURE_AND_NOUL_DRILLDOWN.md` Part 2).
Written 2026-11-23, from the laya library source at
`~/workspace/misinfo_run/rehearsal_slice/laya_dev/laya/` and the
winner checkpoint's own config.

## 0. Plain-words summary for the owner

You asked why we bet on one winning question wording instead of
asking several wordings of the same item and combining their answers.
Short answer: we should do both, and the library makes the combined
version almost free. Asking six wordings in separate calls costs six
passes; asking them inside ONE call costs barely more than one pass,
because the image and the caption are processed once and each extra
question is just a short extra row. Picking a single "winner" wording
from 100–200 test items is also the noisiest step in the whole plan:
wording alone moves scores by about 3 points, so the "winner" can
easily be the luckiest wording, not the best one. Averaging the top
three wordings removes that lucky-pick problem, tends to lower false
alarms on real items, and keeps every rule we already registered
(frozen before reporting, scored once). So the decision is a hybrid:
screen the single wordings exactly as registered, add one battery
arm (top-3 wordings averaged) competing under the same rules, and in
training, train on the best single wording AND on the three battery
wordings together, then choose. The exact protocol text is in §5.

## 1. The owner's question, answered head-on

*"Why don't you use multiple questions pass?"*

The single-winner design was chosen for three reasons, and they are
worth stating because two of them still hold:

1. **A clean pack.** A dataset pack today carries one noul wording,
   one fitted temperature, one threshold. One winner keeps the
   deployed instrument simple to state, reproduce, and defend.
2. **A clean anti-shopping story.** One frozen winner, evaluated
   once on the reporting set, is the easiest discipline to audit.
3. **An implicit cost assumption.** The drill-down procedure
   (`LAYA_STRUCTURE_AND_NOUL_DRILLDOWN.md` §5) was written as "one
   pass per wording," pricing six wordings at six full prediction
   passes (≈15.4 min for the whole sweep). Under that assumption a
   battery looked like a luxury.

Reason 3 is simply wrong about the library (§2, facts 1–2): a
multi-question pass does not cost one full pass per question.
Reason 1 is a real convenience but not a scientific argument — a
pack can carry a three-wording battery exactly as it carries two
questions today. Reason 2 still holds, and the hybrid in §4 keeps
it intact: the battery's composition is frozen on selection data
before any reporting item is touched, and the deployed configuration
— single or battery — is still evaluated exactly once.

Where the single-winner design genuinely breaks is statistical, not
procedural. Selection slices are 100–210 items. A paired delta at
n = 100 carries a standard error of roughly ±5 pp, and v1 measured
±~0.03 accuracy swings from phrasing alone on identical rows. The
Amendment 11 freeze rule (winner needs Δ ≥ +3 pp) sits *inside*
that noise: the maximum of six noisy wording estimates is biased
upward (the winner's curse), so a "winner" at +3–4 pp is as likely
to be the luckiest draw as the best wording, and its reporting-set
score will tend to regress. A battery does not need to pick the
maximum of anything for its deployed score, which removes exactly
that failure mode.

## 2. Library facts (from the source)

1. **Many questions ride one `predict` call, and the image is
   encoded once.** `VLMAgent.predict(state, questions)`
   (`vlm.py:1007`) takes a dict of questions. Its docstring
   (`vlm.py:1022`): "Images are encoded once and their features
   reused for every question row." The image features are computed
   once (`vlm.py:1060–1065`) and repeated across row chunks
   (`vlm.py:1107`). There is **no maximum-questions limit** anywhere
   in the code; rows = Σ over questions of option-order rows, and
   cost grows with the number of rows, not with full re-encodings.
2. **With our checkpoint, the shared prefix is also computed once.**
   The winner checkpoint's config (`mainrun_artifacts/runs/
   full_soft_ce_735_calibrated/vlm_agent_config.json`) records
   `readout = "terminator"`, `option_attention = "block"`. For the
   terminator readout, `predict` builds a prefix cache whenever the
   row count exceeds `batch_size` (auto on CUDA, `vlm.py:1089–1094`):
   the shared prefix — image run + state text, per
   `shared_prefix_len` (`vlm.py:833`) — goes through the backbone
   once, and each question row then computes only its short suffix
   (question + options), batched at `SUFFIX_BATCH_FACTOR ×
   batch_size` = 32 rows per pass (`vlm.py:830`). So the marginal
   cost of an extra noul wording inside one call is one short suffix
   row, **not** the ~0.16 s/item full-predict rate the drill-down
   cost table assumed per wording.
3. **Option order is already averaged, in logit space, before
   temperature.** `n_permutations` (`vlm.py:1011`) scores each
   question under several option orders — identity, reversed, then
   seeded shuffles (`_permutations`, `vlm.py:813`) — and the logits
   are averaged in label order (`vlm.py:1118–1132`). For a noul
   (k = 2 options) `n_permutations = 2` exhausts both orders, so
   order bias is fully removable for the price of one extra suffix
   row per wording.
4. **Temperature is per question TYPE, never per question — inside
   `predict`.** After permutation averaging, logits are divided by
   one temperature (`vlm.py:1129–1132`) resolved per qtype
   (`QTYPES = {choice: 0, score: 1, noul: 2}`, `common.py:11`),
   either from a per-call override keyed by type name
   (`resolve_temperature`, `calibration.py:58`) or from the
   checkpoint's bucket for (qtype, option-count)
   (`temp_bucket`, `common.py:263`; `_checkpoint_temperature`,
   `vlm.py:1179`). Every noul variant has qtype 2 and k = 2, i.e.
   the same bucket `"noul:2"` — **six variants in one call all
   receive the same temperature in the returned probabilities.**
   Per-variant temperatures inside `predict` are impossible.
5. **The escape hatch exists and is the intended one: `_raw_logits`.**
   Passing a dict as `_raw_logits` makes `predict` store each
   question's permutation-averaged logits **before any temperature**
   (`vlm.py:1127–1128`; docstring `vlm.py:1040–1041`) — this is the
   channel `calibrate` itself uses (`vlm.py:1225–1230`). All
   per-variant temperature fitting and all battery combination math
   must run on these captured logits, outside `predict`. (The
   returned answer probabilities are also rounded to 4 decimals —
   another reason not to do battery math on them.) The drill-down
   already requires logit capture (§1 of the drill-down: "the judge
   harness must store the noul logit gap, via `predict`'s
   `_raw_logits` channel"); this decision makes that load-bearing.
6. **Question structure and a truncation caveat that matters for
   wording design.** A question is `{type, instructions, criteria}`
   (`_to_internal`, `vlm.py:996–1005`); for a noul, the criteria are
   the false/true pair and the answer is `p[1]` = P(true option).
   Inputs are cut to budgets (`max_len` 1024, `head_max_len` 256):
   options are cut to 48 tokens each and instructions to what the
   head budget leaves; any cut is flagged per question in the
   answer's `"truncated"` field, and `strict=True` raises instead.
   Two consequences: (a) the longest wording (W3, the checklist)
   must be verified untruncated, or its score is measuring a cut
   question; (b) `build_vlm_inputs` cuts the *state* to the room
   each question's tail leaves (`vlm.py:837` and the
   `shared_prefix_len` note), so on long states — the evidence
   context above all — a longer wording literally sees slightly
   less state text than a short one. That difference is part of the
   instrument as deployed, but it must be recorded per variant
   (truncation flags + `state_tokens_dropped`), not discovered
   later.
7. **Training takes one question per example — multi-wording
   training sets are native.** A training example is
   `{state, q, target}` (`vlm_train.py:39`); JSONL records each
   carry their own `question` (`vlm_train.py:14–15`, `:531`), and
   option order is randomised per example in training
   (`vlm_train.py:125–134`). Replicating an item under several noul
   wordings is therefore just more records — the same pattern v1
   already used when every item appeared in both question forms
   (490 items → 980 records). No trainer change is needed for
   either Phase-2 arm in §5.

## 3. What a battery does, in our numbers

- **Variance.** Averaging m scorers with pairwise error correlation
  ρ multiplies variance by (1 + (m−1)ρ)/m. Our variants share the
  checkpoint, the item, and the image encoding, so ρ is high
  (plausibly 0.7–0.9): at m = 3, ρ = 0.8 the factor is ≈ 0.87 — a
  modest ~13% variance cut. The battery's main value is **not** raw
  variance; it is removing the winner's-curse step (§1) and
  stabilising the deployed score against any single wording's
  quirks.
- **AUC.** The mean of several rankings that are correlated but not
  identical is typically at or above the *median* single AUC, and —
  the comparison that matters — at or above the *expected* AUC of a
  single wording picked by a noisy argmax on 100–200 items. It will
  usually sit below the best single wording's *selection-set* AUC;
  that gap is mostly the curse, not real quality.
- **Alpha.** Averaging pulls extreme P(Fake) values toward the
  middle, so at a fixed threshold fewer genuine items cross it:
  α tends to fall. The battery's threshold is then re-fitted on the
  selection set (analytic, on the averaged score), which spends
  part of that α gain back on Δ — the same frontier, but reached
  from a more stable score.
- **Cost.** Phase-1 capture as one call per item (six noul variants,
  `n_permutations = 2`, logits captured) costs one image encode +
  one prefix pass + twelve short suffix rows per item — estimated
  at or below the v1 full-predict rate of ~0.16–0.2 s/item, versus
  ~0.96 s/item for six separate full passes. The whole selection
  capture (510 items + the 200-item NCP evidence column) drops from
  ≈11.4 min to an estimated ≈2–3 min of GPU. (Estimate, from facts
  1–2; the suffix-row cost is small but not zero, and the pod stage
  should log the measured rate when it runs.)

## 4. DECISION

**Hybrid.** Amendment 11's Phase 1 screens the six single wordings
exactly as registered — the Δ–α frontier stays a reported result.
Added to it: one **battery arm** (the top-3 wordings' noul
probabilities averaged, each variant first temperature-fitted on
its own captured logits) competing in the same table under the same
admissibility rule, with a pre-registered preference for the battery
at deployment unless a single wording clearly beats it. Phase 2
fine-tunes **both** the best single wording and the battery's three
wordings as a multi-noul training set, and chooses on tune as
registered. The single-winner-only design is rejected: at our
selection sizes it deploys the noisiest statistic we compute. A
battery-only design is also rejected: the single-wording frontier is
itself a finding (it prices what wording alone can do), and Phase 2
needs the single-wording arm to tell whether training on one
consistent framing beats training on three.

## 5. Revised protocol text (registration-ready)

> **Amendment 11 — Update 1: the multiple-questions pass (battery
> arm).** This update changes the *capture and deployment* mechanics
> of the noul drill-down. The wordings (W0–W5 per dataset), item
> sets, definitions of Δ / α / AUC / ECE, contexts, and holdout
> discipline of Amendment 11 are unchanged.
>
> **11U.1 Capture — one call per item.** For each item in a
> selection set, the six noul variants ride ONE `predict` call as
> six questions (qids `noul_W0`…`noul_W5`), with
> `n_permutations = 2` and `_raw_logits` captured for every variant.
> The choice question is not re-judged (Amendment 11 §5 step 1
> stands). Capture runs with `strict=True`; any variant whose
> answer carries a truncation flag on any item is reported with
> that count, and its `state_tokens_dropped` distribution is
> recorded beside its scores. Per-variant temperatures are fitted
> on the captured logits (selection-set NLL, the AM6B.2 method) —
> never inside `predict`, whose temperature is per question type.
>
> **11U.2 Battery composition — frozen in Phase 1.** The battery
> **B3** for a dataset = the three wordings with the highest
> selection-set AUC (W0 is in the candidate pool; ties break to
> lower α at the variant's fitted (T, τ), then to the lower wording
> index). B3's membership is written into the stage report before
> any reporting-set item is judged, and never changes afterwards.
>
> **11U.3 Combination rule.** For each item: apply each member
> variant's own fitted temperature to its captured logits, softmax
> to P(Fake), then take the **arithmetic mean** of the three
> probabilities. (Mean of probabilities, after per-variant
> temperature — not a mean of raw logits: variants have different
> logit scales, and a raw-logit average lets the sharpest wording
> dominate; per-variant temperature puts the three on a common
> probability scale first, which is the scale the calibration
> machinery is built on.) The battery's threshold τ_B3 is fitted on
> the selection set over the same 17-point grid as the singles.
>
> **11U.4 The battery's own metrics and the deployment preference.**
> B3 is reported in the same table as the six singles, with its own
> Δ (vs the W0 baseline noul, same items), α, AUC, and ECE.
> Admissibility is the Amendment 11 rule applied to B3 itself:
> α_B3 ≤ α_baseline and Δ_B3 ≥ +3 pp on the selection set.
> **Deployment preference, registered in advance:** the deployed
> configuration is B3 unless the best admissible single wording
> exceeds Δ_B3 by **more than +2 pp** on the selection set, in
> which case that single wording is deployed. (The margin favours
> the robust instrument, mirroring the +3 pp phrasing-noise logic:
> a small selection-set edge for a single wording is not evidence
> it is really better.) If neither B3 nor any single is admissible,
> W0 stands and the full frontier — singles and battery — is the
> finding.
>
> **11U.5 Phase 2 — training uses both.** Per dataset, two training
> sets are built from the same carve and recipe as Amendment 11
> Phase 2: **(S)** records carry the single best admissible wording
> (or the 11U.4 deployed single, if a single was deployed) in the
> noul form; **(B)** records carry each of B3's three wordings as
> the noul form — every train item appears once per battery wording
> (plus its native choice form, as registered). Both are trained at
> the registered step count and selected on the same tune slice by
> the pack's native metric, with noul AUC + α reported beside it.
> The deployed instrument matches the winning training set: (S) →
> that single wording at inference; (B) → the three-wording battery
> at inference, combined by 11U.3, its membership re-frozen as the
> trained model's top-3 by tune AUC under the 11U.2 rule before any
> reporting evaluation.
>
> **11U.6 One evaluation.** The single frozen deployed
> configuration (single or battery, base-screened or fine-tuned per
> the Amendment 11 phase order) is evaluated **once** on the
> reporting set, exactly as Amendment 11 §5 step 4 specifies, with
> the battery's and all singles' selection-set numbers published
> beside it. No composition, temperature, or threshold is refitted
> after that evaluation.

## 6. Named risks of the battery (stated in advance)

- **A battery can hide a bad member.** One poor wording dilutes two
  good ones. Mitigated by 11U.2 (membership by measured AUC, top-3
  only) and by publishing every member's single scores.
- **Correlation caps the gain.** If the variants' errors are nearly
  identical (ρ → 1), B3 ≈ any single and the battery buys only the
  curse removal. That is still worth its near-zero cost, but the
  stage report must not describe B3 as an ensemble breakthrough if
  the members' agreement rate is ~100% — the agreement rate is
  reported with the result.
- **The deployed instrument is heavier to describe.** A pack whose
  noul is a three-wording battery needs the three wordings, three
  temperatures, and the combination rule in its provenance. The
  library records per-question temperatures used and a hash of the
  exact inputs in every result's provenance block, so this is
  bookkeeping, not new machinery.
- **Truncation asymmetry (fact 6).** On evidence-context items the
  longer wordings may see less state text. If B3 mixes wordings
  with materially different `state_tokens_dropped`, the battery is
  partly averaging different *inputs*, not only different
  questions; 11U.1's recording requirement exists so this is
  visible in the report rather than buried.
