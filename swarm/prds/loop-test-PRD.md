# PRD: One probability-conditioned deliberation loop (H-H)

Slug: loop-test. Registered 2026-11-27. Status: BOARD-PASSED
2026-11-27, with the board's fixes applied (see Board pass). Avenue:
H-H, "One probability-conditioned deliberation loop", from
DEEP_CHECK_NOVELTY_2026-11-24.md, where the registered legs below
were fixed before this PRD was drafted. This PRD copies them; it
does not re-invent them. Owner approval for the Colab setup:
2026-11-27. No run under this PRD starts until the owner launches
the notebook himself (his Google sign-in).

## Hypothesis

LAYA is one-shot. Exactly one registered second pass, re-asking the
typed questions with the pass-1 probability state included in the
state, resolves disagreement toward accuracy rather than toward a
collapse. Pass 2's read is the decision. Not an open-ended agent
loop: one loop, typed, registered.

## The exact question

On the frozen 300-item NewsCLIPpings probe, with the scale probe
checkpoint (Amendment 15) as the primary read: does one second
judging pass, whose context carries the pass-1 probability state
and nothing else new, pass all four registered legs below? And, as
the registered ablation, does the answer change when the loop runs
only on the items pass 1 left uncertain (the disagreement-gated
arm), which is the design answer to the confidence-gated correction
risk (IoE; Li et al., arXiv 2402.12563: correction helps uncertain
items and harms confident ones)?

## Baselines, quoted from the record

Pass 1, the scale probe checkpoint on the frozen 300 probe,
pair-only P0 arm, audited verdict at THR_A (0.5 / 0.5), from
v2_probe/uplift/scale_probe_results.json and record section 5.4:

- Headline accuracy 0.0467 (14 of 300).
- Accuracy including uncertain 0.5000.
- Uncertain 274 of 300.
- Pristine headline accuracy 0.0132 (152 items); falsified headline
  accuracy 0.0811 (148 items).

Comparator on the same items: Stage A P0 headline 0.4300,
including uncertain 0.5133, uncertain 44. Screen AUCs on the probe
sit at 0.55 to 0.59; the pass-1 signal the loop conditions on is
weak, and anchoring on noise is a priced-in outcome (see
Falsifiers).

## Split

- The frozen 300-item NewsCLIPpings probe: validation split, seed
  20261122, probe_items.jsonl, IDs identical to the v1 run IDs.
  Pair-only contexts (caption, no evidence), exactly as pass 1 was
  read.
- HARD RULE: the MMFakeBench test set is closed. It was scored
  exactly once. Nothing in this PRD touches it. This run reads
  NewsCLIPpings validation items only.

## The state block (fixed verbatim by the board, fix 2)

Pass 2's context is the item's caption, then a blank line, then
this block, with the braces filled from the item's pass-1 read:

    FIRST PASS RECORD. Choice question probabilities: pristine
    {p_pristine:.4f}, falsified {p_falsified:.4f}. Screen question
    probability that the item is falsified: {p_screen:.4f}. At the
    registered thresholds the two questions {AGREE / DISAGREE}.

No evidence, no gold information, no item metadata is added. The
questions re-asked are the identical V1_NATIVE choice question and
V1_FAKE noul question, in the identical form, at the registered
probe setting (temperatures forced to 1.0, VCFG as in judge_pilot).
Pass 2 is run exactly once per item per arm. There is no pass 3.

## Protocol, in order

0. Inputs gate, fail-closed, at no cost. Before any judging: the
   scale probe checkpoint passes the safetensors header
   completeness check (804,696,880 bytes, 416 tensors); the 300
   probe images are present as byte-exact origin.tar members and
   decode; probe_items.jsonl hashes to the frozen file. If any
   input is absent or fails, the run does not start and this PRD
   returns to the board. (The probe images are not on the study VM;
   they travel in the Colab inputs bundle, see the notebook setup.)
1. Pass 1, same-session control read. The scale probe checkpoint
   judges all 300 items pair-only, through the audited path
   (judge_disk ncp mode, P0 arm). Reproduction gate: the read must
   reproduce the stored pass-1 numbers (headline 0.0467, including
   uncertain 0.5000, uncertain 274, falsified headline 0.0811).
   Tolerance: headline within one item (0.0033) and uncertain
   count within 2; every verdict that differs from the stored
   preds_scale_probe_300.jsonl is listed by item ID in the run
   log. Outside tolerance, the run stops: the checkpoint or the
   path differs from the record, and nothing proceeds on a
   mismatched pass 1.
2. Pass 2, loop-all arm (the primary read). Every item is re-asked
   once with the state block built from its own step-1 pass-1
   read. Pass 2's audited verdict is the item's decision.
3. Pass 2, disagreement-gated arm (the registered ablation). Only
   the items step 1 left uncertain are re-asked with the state
   block; decided items keep their pass-1 verdict. The arm's read
   is the combined verdict set.
4. Secondary reads, descriptive only. Steps 1 to 3 repeated with
   the Stage B checkpoint and with the Stage A winner checkpoint,
   reported beside the primary read with no verdict attached. The
   verdict comes from the primary read alone; there is no verdict
   shopping across checkpoints.
5. Scoring. Audited verdicts at THR_A (0.5 / 0.5) via
   audit_scorer, per arm: headline accuracy, accuracy including
   uncertain, uncertain count, pristine and falsified headline
   accuracy. The headline delta of pass 2 against pass 1 carries a
   paired resampling interval (10,000 resamples, seed 20261122),
   computed on per-item headline correctness.
6. Results are written to a results JSON (notebook, Run 1) and,
   back on the study VM, into research-brain with read-back.

## Success and failure criteria (the registered legs, copied)

Scored on the primary read (scale probe checkpoint, loop-all arm).
ALL four legs must pass; the legs are joint by design, so a
collapse-driven resolution fails by construction.

- Leg 1: pass-2 uncertain count below 137.
- Leg 2: pass-2 headline accuracy above 0.0467, AND its paired
  resampling interval against pass 1 lies above the pass-1 read
  (the interval for the delta excludes zero on the positive side).
- Leg 3: pass-2 accuracy including uncertain at or above 0.5000.
- Leg 4: pass-2 falsified headline accuracy at or above 0.0811.

Strong form, reported separately: pass-2 headline accuracy at or
above Stage A P0's 0.4300 on the same items.

Named outcomes:

- SUPPORTED: loop-all passes all four legs.
- GATED-ONLY: loop-all fails at least one leg, and the
  disagreement-gated arm passes all four legs scored the same way.
  The claim then narrows to a gated loop, which is the registered
  composition with the sufficiency race (N5): a trigger decides
  which items earn the loop.
- NOT SUPPORTED: neither arm passes all four legs. The falsifier
  branches are themselves the result, and are reported in these
  words: the uncertain count fell while falsified accuracy
  collapsed toward zero (the Stage B pristine signature,
  amplification instead of resolution); or including-uncertain
  accuracy fell; or disagreement was unchanged (the state was
  ignored and the loop is inert).

## Budget and stop rule

$0. Colab free GPU is the registered runtime for this run (owner
approval 2026-11-27); the resource ladder otherwise stands (this
VM, Hugging Face PRO ZeroGPU, RunPod last and only inside the
swarm cap, which this run does not draw on). Judging cost basis
from the record: about 0.65 seconds per item per pass on pod GPU;
the full protocol is three checkpoints by two passes by 300 items,
well inside one free session. Checkpointing: progress is flushed
per item (the study's judging pattern) and copied to Drive with
verify-on-save at least every 30 minutes of wall time; a session
death resumes from the newest verified copy, skipping completed
(id, arm) pairs. Any leg scored on a partial item set is void:
the legs read on exactly the 300 frozen items or not at all.

## Prior art, as bounded in the deep check

PrimaCons (arXiv 2610.38623) owns consistency measurement in this
typed family, including discrepancy predicting failure at ROC AUC
0.91; its fix is a trained residual network, not inference-time
state feedback. Reinforcement Inference (Sun, February 2026)
triggers a second attempt from entropy and maximum softmax
probability, prompt-only, on free-text models, carrying no
probability values into state. The confidence-gated correction
literature (IoE; Li et al., arXiv 2402.12563) bounds the design
risk and is answered by the gated ablation. What this PRD claims,
at most: a single typed probability-state feedback pass in a
fine-tuned typed-decision VLM, read under abstention accounting.
No wider novelty claim may be made from its result.

## Board pass

BOARD-PASSED 2026-11-27, with fixes. Four critics argued against
the draft: novelty, methods, statistics, feasibility. The sharpest
objection came from the methods critic: as first drafted, the
state block's wording was described, not fixed, and a wording
chosen after seeing pass-1 outputs would make the run a wording
search, the exact failure the C7 kill (wording as a training
variable) recorded. The fixes they won, applied above:

1. The state block template is fixed verbatim in this PRD (see
   "The state block"), before any pass-2 output exists. Any
   wording change is a new registration, not an edit.
2. The pass-1 reproduction gate (protocol step 1) with named
   tolerances and per-item deviation listing. A pass 2 built on
   an unreproduced pass 1 would be uninterpretable.
3. Verdict discipline across arms and checkpoints: loop-all is
   the primary read, the gated arm is a named outcome
   (GATED-ONLY), secondary checkpoints are descriptive only.
4. The inputs gate (protocol step 0) names the probe images as a
   fail-closed input, since they are not stored on the study VM.
5. Novelty scope: the PRD carries the bounded slice wording from
   the deep check and forbids a wider claim from the result.
6. Statistics: the interval leg reads on the per-item headline
   correctness delta, resamples and seed as registered in the
   study's audit convention (10,000, seed 20261122).

Concession recorded, no fix available inside this PRD: the
pass-1 screen signal is weak (AUCs 0.55 to 0.59), so the loop may
be conditioning on noise. That is priced into the falsifiers; it
is not a reason to widen the design.

## What would change the paper's claims, and what changes nothing

- If SUPPORTED: paper two gains a mechanism result, one typed
  probability-state feedback pass resolves disagreement toward
  accuracy on the frozen probe, and the sufficiency race's
  composition (a trigger gating the loop) becomes the next
  registered question with a working loop to gate.
- If GATED-ONLY: the claim narrows to gated looping, and the
  race (N5) decides the gate. Still a result, in those words.
- If NOT SUPPORTED, on any falsifier branch: the disagreement at
  scale stands as a measured anomaly that one deliberation pass
  does not fix, each branch names which failure occurred, and no
  number in the paper changes.
