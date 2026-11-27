# PRD: The sufficiency trigger race (N5, three-way)

Slug: sufficiency-race. Registered 2026-11-27. Status:
BOARD-PASSED 2026-11-27, with the board's fixes applied (see
Board pass). Avenue: N5, the sufficiency candidate amended into a
three-way trigger race (research-brain avenue f874e11b; candidate
file SUFFICIENCY_QUESTION_CANDIDATE.md, amendment in
NOVELTY_IDEAS_FROM_REVIEW_2026-11-24.md). Owner approval for the
Colab setup: 2026-11-27.

## Dependency (stated plainly)

This run runs AFTER the loop test (PRD: loop-test) and consumes
its outputs. It reads on the loop's frozen probes (the same 300
NewsCLIPpings validation items) and scores its triggers against
the loop run's same-session pass-1 verdicts. If the loop test has
not completed, this run does not start. Its sufficiency pass is
also the gate signal the loop's GATED-ONLY outcome points to, so
the two PRDs are one programme, run in this order.

## Hypothesis

A direct sufficiency probability, asked as a third typed question
in the same form as the other two, predicts item-level failure
better than the choice-screen disagreement signal does; and a
post-hoc selector on the frozen backbone's representations is the
control that can beat both typed signals. The race is registered
so that whichever signal wins, the claim that survives is the
honest one.

## The three triggers (fixed)

1. Disagreement. Score per item: the absolute difference between
   the choice form's falsified probability and the noul screen's
   falsified probability, from the loop run's pass-1 read.
   Abstain on the largest scores first. This is the incumbent
   signal (PrimaCons's discrepancy, in this study's two-form
   version).
2. Sufficiency. A third typed question, noul form, asked once per
   item on the identical pair-only context as pass 1 (caption, no
   evidence), with the scale probe checkpoint, at the registered
   probe setting. Wording fixed verbatim here, before any output
   exists:

       {"type": "noul",
        "instructions": "Given only the image, its caption, and
        the information supplied with them, is the supplied
        information sufficient to decide whether the caption
        truthfully describes the image in its original context?",
        "criteria": {"false": "The supplied information is not
        sufficient to decide whether the caption truthfully
        describes the image in its original context.",
                     "true": "The supplied information is
        sufficient to decide whether the caption truthfully
        describes the image in its original context."}}

   Score per item: 1 minus P(sufficient). Abstain on the largest
   scores first. Scope, registered: this race tests the pair-only
   form of the question. An evidence-context form is a separate
   registration and is not read here.
3. Representation selector. A logistic probe on the frozen scale
   probe checkpoint's backbone representations (the model's
   readout activations for the item), fit to predict pass-1
   failure. Fit set, fixed by the board (fix 2): the Amendment 15
   carve's 200 tune items only, judged pass-1 in this run for
   their failure labels, item-disjoint from the 300 probe items
   by the carve's construction. The probe is fit and frozen
   before any probe-item score is computed. Score per item: the
   probe's predicted failure probability. This is the Know When
   to Abstain family's control (representation geometry, probed
   directly; Heng and Soh, arXiv May 2025, and the
   Neyman-Pearson-optimal selector family recorded in the N5
   amendment).

Failure, defined once for all three triggers: the loop run's
pass-1 audited verdict on the item is not a decided correct
verdict (decided and wrong, or uncertain). All triggers predict
the same failure labels on the same items.

## Split

- The frozen 300-item NewsCLIPpings probe (validation split, seed
  20261122), pair-only, inherited from the loop test. Plus the
  Amendment 15 carve's 200 tune items, used only to fit trigger 3.
- HARD RULE: the MMFakeBench test set is closed. It was scored
  exactly once. Nothing in this PRD touches it.

## Protocol, in order

0. Inputs gate, fail-closed. The loop test's results JSON and
   pass-1 prediction files are present and hash-checked; the
   scale probe checkpoint passes the header completeness check;
   the 200 tune items and their images are present. Missing loop
   outputs stop this run outright (see Dependency).
1. Sufficiency pass. The third question is asked once per probe
   item (300) and once per tune item (200), rows flushed per
   item, checkpointed to Drive with verify-on-save at least
   every 30 minutes of wall time.
2. Tune pass-1 read. The scale probe checkpoint judges the 200
   tune items pair-only through the audited path, giving trigger
   3 its failure labels.
3. Representation extraction and probe fit. Readout activations
   are extracted for tune and probe items from the frozen
   checkpoint; the logistic probe is fit on the 200 tune items
   only (fixed regularisation: scikit-learn LogisticRegression,
   C = 1.0, no feature selection, no tuning on probe items), then
   frozen and applied to the 300 probe items.
4. Race scoring, on the 300 probe items only.
   a. As failure predictors: ROC AUC per trigger against the
      failure labels. The sufficiency-minus-disagreement AUC
      difference carries a paired resampling interval (10,000
      resamples, seed 20261122).
   b. As abstention triggers at matched coverage: for each
      decided fraction on the fixed grid 0.05, 0.10, ..., 1.00,
      each trigger abstains on its highest-scored items and the
      decided set is read under the study's abstention
      accounting: decided-fraction accuracy, lost-correct count
      (decided-correct items the trigger would have abstained
      on, against the no-abstention read), and delivered
      selective risk on the decided set. Curves are reported in
      full, not at one operating point (see Supporting evidence,
      Entropy Alone).
5. Results are written to a results JSON (notebook, Run 2) and,
   back on the study VM, into research-brain with read-back.

## Success and failure criteria (registered)

- Sufficiency WINS the typed race if its failure-prediction AUC
  exceeds the disagreement signal's AUC on the same items AND
  the paired resampling interval for the difference excludes
  zero on the positive side, AND at matched coverage its
  decided-fraction accuracy is at or above the disagreement
  trigger's at every grid point from 0.25 to 0.75 decided.
- The PROBE WINS if its AUC exceeds both typed signals' AUCs
  with intervals excluding zero against each. The honest claim
  then becomes: abstention quality in this system is geometric,
  not typed. That outcome is a result, recorded in those words.
- The race is a TIE between the typed signals if the AUC
  difference interval includes zero; the sufficiency claim is
  then NOT SUPPORTED, and the incumbent disagreement trigger
  stands.
- FALSIFIERS for the sufficiency candidate itself, copied from
  its registration: sufficiency AUC at or below the disagreement
  signal's; or sufficiency fires uniformly (its score has no
  discrimination: AUC interval includes 0.5); or sufficiency and
  disagreement identify the same items with no gain (top-quartile
  abstention sets overlap above 0.95 AND the matched-coverage
  curves are within 0.005 accuracy at every grid point).
- Secondary check, descriptive only, from the candidate file:
  whether the sufficiency-low items overlap the class-blindness
  items (the falsified items pass 1 missed entirely). Reported
  as an overlap count, no verdict attached.
- A descriptive read of all three triggers against the loop's
  pass-2 verdicts may be reported, labelled descriptive. No race
  verdict reads on pass 2 (board fix 4).

## Supporting evidence (recorded, not load-bearing)

- HumblePRM (research-brain finding, 2026-11-26): a separately
  supervised sufficiency step raised abstention on ambiguous
  items from 48.34 to 61.55 with clear-item accuracy nearly
  unchanged (54.08 vs 54.67). That step is supervised; this
  race's sufficiency signal is a zero-shot typed question.
  HumblePRM supports the direction, not the mechanism, and the
  PRD claims nothing from it beyond that.
- Entropy Alone (research-brain finding, 2026-11-26): a
  single-signal abstention trigger can fail at strict target
  risks. Hence the matched-coverage curves across the full grid
  instead of a verdict at one threshold.

## Budget and stop rule

$0. Colab free GPU (owner approval 2026-11-27). Cost basis:
500 sufficiency judgements, 200 tune judgements, and activation
extraction over 500 items, all inference on a 256M model; well
inside one free session. Checkpointing and resume as in the loop
PRD: per-item flush, Drive copies with verify-on-save at least
every 30 minutes, resume skips completed items. No leg reads on
a partial item set.

## Prior art, as bounded in the record

PrimaCons owns discrepancy as a failure predictor in this typed
family (published AUC 0.91 in its own setting; this race computes
the disagreement AUC fresh on these items and never compares
against 0.91 directly, board fix 3). Know When to Abstain owns
representation probing for abstention in language models.
Explicit Abstention Knobs owns abstention as an output option.
The unoccupied slice, as recorded: a three-way race inside one
fine-tuned typed-decision VLM, read under abstention accounting,
with the strongest rival registered as a control.

## Board pass

BOARD-PASSED 2026-11-27, with fixes. Four critics argued against
the draft: novelty, methods, statistics, feasibility. The
sharpest objection came from the methods critic: as first
drafted, the representation selector's fit set was unspecified,
and a probe fit on the probe items would have manufactured its
own win; a race whose control can leak is worse than no race.
The fixes they won, applied above:

1. The sufficiency question's wording is fixed verbatim in this
   PRD before any output exists; any rewording is a new
   registration.
2. Trigger 3's fit set is fixed to the Amendment 15 carve's 200
   tune items, disjoint from the probe by construction; the
   probe is frozen before probe items are scored, and its
   fitting recipe is fixed (no tuning on probe items).
3. The race is judged on same-items AUCs computed in this run.
   PrimaCons's published 0.91 is context, never the bar.
4. Race verdicts read against pass-1 failure only. Pass-2 reads
   are descriptive, so the race cannot borrow the loop's result.
5. Matched coverage is a fixed grid (0.05 steps, 0.05 to 1.00),
   fixed before the run, with the win band (0.25 to 0.75)
   named in advance.
6. The dependency on the loop test is stated as a hard gate
   (protocol step 0), not a preference.

Concession recorded: the sufficiency question is asked of the
same model whose blindness it is meant to catch, and the pass-1
signals are weak (screen AUCs 0.55 to 0.59). A sufficiency loss
is a live, priced-in outcome; the falsifiers name it in advance.

## Follow-on, registered but not in this run

The sliced variant (avenue cd9428b4, from the 2026-11-26 deep
dream): the same race run separately on absent, degraded, and
contradictory evidence slices. It is a separate registration and
does not ride on this PRD's verdict.

## What would change the paper's claims, and what changes nothing

- If sufficiency wins: the typed-primitive claim survives its
  strongest registered rival, and the composition (sufficiency
  gates the loop) becomes paper two's mechanism claim, testable
  against the loop run's GATED-ONLY question.
- If the probe wins: the claim becomes geometric, not typed,
  and the sufficiency primitive is retired in those words.
- If the race ties or sufficiency falsifies: the disagreement
  trigger stands as the study's abstention signal, the negative
  is reported, and no number in the paper changes.
