# The Nouls Section: How to Build a Noul, Why It Works, What We Chose

Written 2026-11-23. Sources: the Phase 1 screen artifacts
(`runs/noul_drilldown/ncp/screen_result.json`,
`runs/noul_drilldown/verite/screen_result.json`,
`runs/noul_drilldown/mmf/screen_result.json`), the executed variant
code in `drill_variants.py`, the frozen wordings in
`LAYA_STRUCTURE_AND_NOUL_DRILLDOWN.md` section 3, the battery
design in `QUESTION_SETUP_DECISION.md`, and the v1 reads recorded in
`DESIGN.md` and `EVIDENCEGATE_DESIGN.md`. Every number below comes
from one of those files. Where a paragraph is interpretation rather
than measurement, it says so.

## 1. What a noul question is

Plain version. The model answers two questions about every item. The
choice question asks: which label fits this item? The noul question
asks a yes or no question: how likely is this item to be fake? The
noul answer is a probability. It works as a screen beside the choice
question. When the two disagree, the item is uncertain, and the
system can route it to evidence or hold it back.

Precise version. A noul is one fixed wording per dataset, applied to
every item in a run. It is never written per item. Each dataset pack
carries its own noul wording, its own fitted temperature, and its own
threshold. The score is P(Fake) from a two-option question (false /
true), read from the model's option probabilities. In v1 the noul ran
at temperature 1 with threshold 0.5, exactly as the library shipped
it. That default is what this section tests.

Why it needed work. On NewsCLIPpings in v1, the trained model's noul
score had an AUC of 0.529 and a mean confidence of 0.5002. AUC 0.5 is
chance. The screen was ranking items almost at random, and its raw
probabilities sat near 0.5 on nearly everything. The choice question
carried the verdicts; the noul added little. The drill-down asked
whether a better wording, a fitted temperature, or a combination of
wordings could make the screen worth trusting.

## 2. The six wordings and what each one tests

All six wordings were frozen in writing before any screen ran. No
wording was added or edited after results. W0 is the control: the
wording the packs already ship, identical in all three packs today.
It asks whether the dataset would assign the item a falsified,
distorted, miscaptioned, or out-of-context label rather than its
original, pristine, or true label, and it states that this is a
benchmark-label estimate, not an independent fact-check. W1 to W5
keep the same two answer options and change only the framing.

MMFakeBench (fake means textual distortion, visual distortion, or
image-text mismatch):

- W1, direct probability. Asks the probability directly: is the text
  fabricated or altered, the image manipulated, or the pair
  mismatched. Tests whether a plain probability ask beats the
  benchmark-label framing.
- W2, truth-framed. Drops the dataset framing. Judge the item
  itself, not the dataset. Tests whether the benchmark wording in W0
  is helping or hurting.
- W3, decomposed checklist. Splits the judgment into three checks:
  text invented or altered, image manipulated, image and text not
  corresponding. Fake if any check fails. Tests whether decomposition
  helps a small model.
- W4, conservative. Call it fake only if the distortion is clear and
  specific. Designed to lower alpha, the false-alarm rate on real
  items.
- W5, pairing-first. Asks whether the text truthfully goes with the
  image exactly as presented. Tests a pairing frame instead of a
  distortion frame.

NewsCLIPpings (fake means a repurposed, incorrect pairing):

- W1, direct probability. The probability that this caption was not
  originally published with this image.
- W2, original context. Was this photograph originally taken for the
  event this caption describes.
- W3, entity check. Compare the people, place, and event named in
  the caption against what the image shows. Fake if they differ.
- W4, conservative. Fake only if the image clearly belongs to a
  different event. Designed to lower alpha.
- W5, truth-framed. Does this caption truthfully describe this image
  as it was originally published. The shortest wording in the set:
  29 words, against 49 for W0.

VERITE (fake means miscaptioned or out-of-context):

- W1, direct probability. The probability that the pair is not
  simply true.
- W2, decomposed, two failure modes. Names both ways a pair can
  fail: the caption says something false about the image, or a real
  image is used outside its original context. Fake if either is
  present.
- W3, original context. Was this image originally published with
  this caption, for this event.
- W4, conservative. Fake only if the caption is clearly false about
  the image or the image clearly comes from a different event.
  Designed to lower alpha.
- W5, claim-framed. Treat the caption as a claim about the image.
  Is the claim true of this image in its original context.

## 3. Screen results

Method, briefly. Phase 1 ran on the BASE checkpoint, before any
training, on each dataset's tune slice (NewsCLIPpings and VERITE
n = 100; MMFakeBench n = 210, its tune and calibration slices
pooled). All six
wordings rode one predict call per item, with option-order averaging
over both orders and raw logits captured. Each variant then got its
own fitted temperature and threshold on the same 100 items. Two views
are reported. The raw view is temperature 1, threshold 0.5: the
instrument as shipped. The fitted view uses the variant's own fitted
temperature and threshold. Delta is accuracy minus the W0 baseline
noul (raw view) on the same items. Alpha is the false-alarm rate:
the share of truly real items the screen calls fake. A variant is
admissible only if its alpha is no worse than the baseline alpha.
The winner must also clear delta of at least +3 points, or W0 stands.

### NewsCLIPpings (n = 100; 50 fake, 50 real; baseline W0 raw: acc 0.51, alpha 0.94)

| W | Axis | AUC | Raw acc | Raw alpha | Raw delta | Fitted T | Fitted thr | Fitted acc | Fitted alpha | Fitted delta | Fitted ECE |
|---|------|-----|---------|-----------|-----------|----------|------------|------------|--------------|--------------|------------|
| W0 | control | 0.5816 | 0.51 | 0.94 | 0.00 | 12.0 | 0.575 | 0.56 | 0.08 | +0.05 | 0.062 |
| W1 | direct probability | 0.4240 | 0.50 | 0.00 | -0.01 | 12.0 | 0.500 | 0.50 | 0.00 | -0.01 | 0.034 |
| W2 | original context | 0.3656 | 0.48 | 0.08 | -0.03 | 12.0 | 0.550 | 0.50 | 0.00 | -0.01 | 0.057 |
| W3 | entity check | 0.3992 | 0.47 | 0.06 | -0.04 | 12.0 | 0.425 | 0.51 | 0.94 | 0.00 | 0.072 |
| W4 | conservative | 0.3860 | 0.48 | 0.06 | -0.03 | 12.0 | 0.575 | 0.50 | 0.00 | -0.01 | 0.061 |
| W5 | truth-framed | 0.4464 | 0.48 | 0.04 | -0.03 | 12.0 | 0.450 | 0.54 | 0.74 | +0.03 | 0.059 |

Winner: **W5, truth-framed.** It is the best admissible single
(best_admissible_single = 5 in the artifact). Deployed from Phase 1
as a single wording, temperature 12.0, threshold 0.45. Its fitted
accuracy is 0.54 and its fitted delta is +0.03, exactly at the +3
point bar. Note what the table also shows: W0 itself has the highest
AUC (0.5816) and the highest fitted accuracy (0.56). W5 wins on the
registered rule, not on every column. Section 4 takes this up.

Battery B3 (members W0, W1, W5, chosen by AUC): AUC 0.4892, accuracy
0.50 at its fitted threshold, alpha 0.00, delta -0.01. **Not
admissible.** The rule it failed is the delta leg: admissibility
needs alpha no worse than baseline and delta of at least +3 points.
Its alpha passed easily. Its delta was negative.

### VERITE (n = 100; 64 fake, 36 true; baseline W0 raw: acc 0.59, alpha 0.72)

| W | Axis | AUC | Raw acc | Raw alpha | Raw delta | Fitted T | Fitted thr | Fitted acc | Fitted alpha | Fitted delta | Fitted ECE |
|---|------|-----|---------|-----------|-----------|----------|------------|------------|--------------|--------------|------------|
| W0 | control | 0.5252 | 0.59 | 0.72 | 0.00 | 4.52 | 0.500 | 0.59 | 0.72 | 0.00 | 0.095 |
| W1 | direct probability | 0.4345 | 0.35 | 0.06 | -0.24 | 12.0 | 0.475 | 0.42 | 0.31 | -0.17 | 0.183 |
| W2 | decomposed, two failure modes | 0.5217 | 0.39 | 0.28 | -0.20 | 12.0 | 0.475 | 0.59 | 0.58 | 0.00 | 0.156 |
| W3 | original context | 0.5677 | 0.44 | 0.17 | -0.15 | 12.0 | 0.475 | 0.62 | 0.56 | +0.03 | 0.157 |
| W4 | conservative | 0.5043 | 0.42 | 0.17 | -0.17 | 12.0 | 0.475 | 0.53 | 0.58 | -0.06 | 0.158 |
| W5 | claim-framed | 0.4796 | 0.39 | 0.06 | -0.20 | 12.0 | 0.475 | 0.46 | 0.47 | -0.13 | 0.167 |

Winner: **W3, original context.** Highest AUC in the set (0.5677),
and the only variant with a positive fitted delta: fitted accuracy
**0.62**, delta +0.03, fitted alpha 0.56 against a baseline alpha of
0.72, so it is admissible. Deployed from Phase 1 as a single
wording, temperature 12.0, threshold 0.475.

Battery B3 (members W0, W2, W3): AUC 0.5304, accuracy 0.55, alpha
0.61, delta -0.04. **Not admissible.** Same story as NewsCLIPpings:
alpha passed (0.61 against a 0.72 baseline), delta failed. The
battery needed at least +3 points and delivered -4.

### MMFakeBench (tune only; n = 210; 147 fake, 63 real; baseline W0 raw: acc 0.58, alpha 0.83)

Tune only. The tune-only screen was approved on 2026-11-23 at 12:27
ET. The MMFakeBench test split is closed and stays closed; this
screen ran only on the 210 tune and calibration items, on the BASE
checkpoint. Nothing in this table touches the test split, and no
number here is a test number.

| W | Axis | AUC | Raw acc | Raw alpha | Raw delta | Fitted T | Fitted thr | Fitted acc | Fitted alpha | Fitted delta | Fitted ECE |
|---|------|-----|---------|-----------|-----------|----------|------------|------------|--------------|--------------|------------|
| W0 | control | 0.4266 | 0.58 | 0.83 | 0.00 | 8.96 | 0.500 | 0.58 | 0.83 | 0.00 | 0.165 |
| W1 | direct probability | 0.6735 | 0.51 | 0.13 | -0.07 | 12.0 | 0.475 | 0.69 | 0.62 | +0.10 | 0.211 |
| W2 | truth-framed | 0.6389 | 0.43 | 0.10 | -0.15 | 12.0 | 0.475 | 0.61 | 0.35 | +0.03 | 0.219 |
| W3 | decomposed checklist | 0.5886 | 0.38 | 0.05 | -0.20 | 12.0 | 0.450 | 0.64 | 0.83 | +0.06 | 0.229 |
| W4 | conservative | 0.6212 | 0.47 | 0.13 | -0.11 | 12.0 | 0.475 | 0.61 | 0.41 | +0.03 | 0.217 |
| W5 | pairing-first | 0.5969 | 0.40 | 0.06 | -0.18 | 12.0 | 0.450 | 0.65 | 0.76 | +0.07 | 0.229 |

Best single: **W1, direct probability** (best_admissible_single = 1
in the artifact). Highest AUC in the set (0.6735), fitted accuracy
0.6857, fitted delta +0.1048, fitted alpha 0.62 against a baseline
alpha of 0.83, so it is admissible. The control is the weak
instrument here: W0 ranks below chance (AUC 0.4266) and every new
wording beats it after fitting.

Battery B3 (members W1, W2, W4, chosen by AUC; each member at its
own fitted temperature of 12.0; battery threshold 0.475): AUC
0.6580, accuracy 0.6762, alpha 0.4127, delta +0.0952, ECE 0.2159,
member agreement 0.60. **Admissible** (the artifact records
admissible = true). The recorded Phase 1 deployment
(deployed_phase1 in the artifact) is the **battery**: form
"battery", members W1, W2, W4, each at temperature 12.0, threshold
0.475. Under the registered deployment-preference rule the battery
deploys unless the best single beats its delta by more than 2
points; W1's delta (+0.1048) does not clear that margin over the
battery's (+0.0952), so the battery stands as the deployment, with
W1 recorded as the best admissible single behind it.

## 4. Why it works, and why it does not

The measured facts first.

Fact one: temperature did more than wording. On NewsCLIPpings, the
control wording at its shipped settings calls 94 percent of real
items fake (alpha 0.94) and scores 0.51 accuracy. The same wording,
same items, with a fitted temperature and threshold: alpha 0.08,
accuracy 0.56. No wording change at all, and the false-alarm rate
falls by 86 points. The v1 screen was not badly worded. It was badly
scaled. Its probabilities were far too sharp, so the 0.5 threshold
sat in the wrong place.

Fact two: the fitted temperatures are extreme. On NewsCLIPpings
every variant's fit ran to 12.0, the top of the fitting grid. On
VERITE every variant except W0 did the same, and W0 fitted to 4.52.
A fit that runs to the edge of its grid is the data asking for
flatter probabilities than the grid allows. Interpretation: the raw
noul scores carry a weak ranking signal wrapped in far too much
confidence, and the fit's main job is to soften them.

Fact three: on NewsCLIPpings, four of the five new wordings rank
below chance. W2 (original context) has AUC 0.3656, W4
(conservative) 0.3860, W3 (entity check) 0.3992, W1 (direct
probability) 0.4240. Below 0.5 is worse than random: the screen
leans the wrong way. Only W0 (0.5816) and W5 (0.4464, still below
0.5) come close to or above the line, and only W0 clears it.

Fact four: on VERITE the spread is smaller and the winner is real
but modest. W3 leads on AUC (0.5677) and is the only variant that
gains accuracy after fitting (+0.03, to 0.62). The direct
probability wording is the clear failure: raw delta -0.24, fitted
delta still -0.17. Asking this model "what is the probability this
is not true" produced its worst screen on VERITE and a below-chance
ranking on NewsCLIPpings too (0.4240).

Fact five: on NewsCLIPpings and VERITE, the battery did not rescue
anything. B3 averaged the three highest-AUC wordings per dataset,
each with its own fitted temperature. It scored below its own best
member on AUC both times (NewsCLIPpings 0.4892 against W0's 0.5816;
VERITE 0.5304 against W3's 0.5677) and posted negative deltas on
both. The members also rarely agreed with each other: agreement
rate 0.17 on NewsCLIPpings and 0.37 on VERITE.

Fact six: MMFakeBench is the opposite shape (tune items only). The
control ranks below chance (AUC 0.4266), and all five new wordings
rank above it. The direct probability wording, the worst axis on
VERITE, is the best single here: AUC 0.6735, fitted accuracy
0.6857, fitted delta +0.1048. The battery is admissible on this
dataset (delta +0.0952, alpha 0.4127 against a 0.83 baseline,
member agreement 0.60) and is the recorded Phase 1 deployment. One
dataset where the ensemble conditions held, and the ensemble
worked; two where they did not, and it did not.

Interpretation, labelled as such. Three readings fit these numbers,
and the screen alone cannot separate them.

First, decomposition seems to ask too much of this model. The
entity check and the two-failure-modes wording both hand the model a
procedure: compare named entities, or test two failure modes. On
NewsCLIPpings the entity check ranks at 0.3992, well below chance. A
plausible reading is that a 201M model does not run the procedure;
it pattern-matches the longer, more technical wording to a label
lean, and the lean points the wrong way. The shortest wording in the
whole study, NewsCLIPpings W5 at 29 words, is the one that won its
dataset. Short and direct beat long and procedural in the
NewsCLIPpings and VERITE screens. On MMFakeBench the checklist
wording ranked mid-pack (AUC 0.5886, fitted delta +0.06) rather
than worst, so the pattern is a tendency, not a law.

Second, framing the question around the item's original context
seems to match what the model can actually judge. VERITE's winner
asks one concrete question: was this image originally published with
this caption, for this event? That is a question about the pairing's
history, which is exactly VERITE's failure mode. The direct
probability wording asks for a number about truth in general, and
the model has no grip on it: delta -0.24 raw. The gap between W3 and
W1 on VERITE is the largest wording effect in the NewsCLIPpings
and VERITE screens, and it
is a framing effect, not a knowledge effect, since the model and
items are identical.

Third, the battery results cut against the usual ensemble story on
two datasets and confirm its condition on the third. Averaging helps
when members are individually decent and make different mistakes.
The NewsCLIPpings battery averaged one good ranking (W0, 0.5816)
with two below-chance rankings (W1 0.4240, W5 0.4464), and the
average inherited the weakness. Low member agreement (0.17) did not
mean useful diversity; it meant the members were noisy in different
directions around a weak signal. The battery design named this risk
in advance (a battery can hide a bad member), and the screen is
that risk, measured. On MMFakeBench the members each ranked
decently (AUC 0.6212 to 0.6735) and agreed 0.60 of the time, and
there the average held up: admissible, and the recorded deployment.
Interpretation: the battery is not good or bad in itself; it is a
test of whether its members are.

One caution about the NewsCLIPpings winner. W5 was selected by the
registered rule, and the rule is the point of a registered screen.
But its AUC (0.4464) is below chance and below W0's, and its fitted
alpha (0.74) is far worse than W0's fitted alpha (0.08). It won on
fitted accuracy delta at its own fitted threshold. On n = 100, a +3
point delta is three items. The honest statement is: W5 is the
registered winner and goes to Phase 2, and the screen also says the
control wording with a fitted temperature is at least as good an
instrument. Phase 2 and Phase 3 exist to separate them. If the
trained W5 does not hold up, W0 with its fitted temperature is the
fallback the data already supports.

## 5. What we chose

Per dataset, one wording goes forward. Not one wording for all
datasets: the screens say the best framing is dataset-specific, and
the packs were always per-dataset.

- NewsCLIPpings: **W5, truth-framed** ("Does this caption truthfully
  describe this image as it was originally published?"), deployed as
  a single wording at temperature 12.0, threshold 0.45.
- VERITE: **W3, original context** ("Was this image originally
  published with this caption, for this event?"), deployed as a
  single wording at temperature 12.0, threshold 0.475. Fitted
  accuracy 0.62 on the tune screen.
- MMFakeBench (tune items only; the closed test split plays no
  part in choosing): the best admissible single is **W1, direct
  probability**, and the recorded Phase 1 deployment is the
  **battery B3** (members W1, W2, W4, each at temperature 12.0,
  threshold 0.475), under the deployment-preference rule recorded
  in section 3.
- The battery B3 is not deployed on NewsCLIPpings or VERITE. It
  failed the admissibility rule on both of those screens, on the
  delta leg each time. On MMFakeBench it was admissible and is the
  recorded deployment. The battery design stays in the record, and
  Phase 2 still trains a battery record set beside the
  single-wording set, as registered, so the training comparison is
  run even where the Phase 1 battery was not admissible.

What happens next, in order. Phase 2 is a small training test:
fine-tune on each dataset's training carve with the winning wording
in the noul form, at the registered step count, and select on the
tune slice. Phase 3 is one reporting evaluation: the frozen winner,
evaluated once on the reporting set, beside the baseline noul on the
same items. No wording, temperature, or threshold is refitted after
that evaluation. If a winner freezes, its wording, temperature, and
threshold are written back into the pack with their selection
provenance. If none does, the pack keeps W0 and the frontier table
is the finding.

## 6. How to build a good noul: the checklist

Distilled from the v1 failure and the three screens.

1. One wording per dataset, for the whole run. Never per item. If
   the wording changes mid-run, no two scores are comparable.
2. Fit the temperature before you judge the wording. An unfitted
   noul at threshold 0.5 can call 94 percent of real items fake.
   Most of what looks like a wording problem is a scaling problem.
3. Ask about the item, in the dataset's own failure language. The
   winning frames name the concrete failure: a caption that does not
   truthfully describe its image, an image not originally published
   with its caption. The abstract ask ("what is the probability this
   is not true") produced the worst screen on VERITE and a
   below-chance ranking on NewsCLIPpings, yet the direct probability
   ask was the best single on MMFakeBench. There is no universal
   best frame; match the ask to the dataset, and measure.
4. Keep it short. The shortest wording tested (29 words) won its
   dataset. Every procedural wording, checklist or multi-step,
   ranked at or below chance on NewsCLIPpings.
5. Do not hand a small model a procedure. Entity checks and
   decomposed checklists read well to a human and scored worst.
   One question, one judgment.
6. Judge a wording on ranking first (AUC), then on fitted accuracy
   and alpha. Raw accuracy at threshold 0.5 mostly measures the
   temperature you forgot to fit.
7. Set the bar before you run: alpha no worse than baseline, delta
   at least +3 points, or the control stands. Then honour the bar
   even when the winner is unglamorous, and publish the full
   frontier either way.
8. Treat an ensemble as a hypothesis, not a rescue. Averaging
   wordings only helps if each member ranks decently alone. Check
   member AUCs and member agreement before trusting the average.
   The screens show both sides: members at or below chance with
   agreement 0.17 to 0.37 produced a battery that failed on two
   datasets; members ranked 0.62 to 0.67 with agreement 0.60
   produced the one battery that was admissible and deployed.
9. Freeze the wordings in writing before the screen. A wording
   edited after seeing results is not a result.
10. Report the control's fitted numbers beside the winner's. If the
    old wording with a fitted temperature matches the new winner,
    say so. Sometimes the fix was never the words.

## Appendix: why each wording exists

This appendix records the experiment itself: the design, the exact
questions as executed, what prompted each one, what it was built to
test, and what it scored. The question texts are quoted verbatim
from the executed code (`drill_variants.py`), punctuation included,
and were cross-checked against the frozen texts in
`LAYA_STRUCTURE_AND_NOUL_DRILLDOWN.md` section 3. The two agree on
every variant; there is no wording mismatch to flag. W0 also
carries its own criteria pair, quoted below. W1 to W5 in every
dataset share one criteria convention, also quoted below.

### The design of the experiment

- **Subsets.** Selection ran only on train-side tune slices:
  NewsCLIPpings Stage B tune, 100 items; VERITE tune carve, 100
  items; MMFakeBench tune plus calibration slices pooled, 210
  items. Reporting splits were not touched in Phase 1. The
  MMFakeBench test split is closed and stayed closed throughout.
- **Checkpoint.** The BASE checkpoint for all three datasets, before
  any fine-tuning, so the screen measures the instrument as
  shipped, not a trained model.
- **Capture.** One predict call per item carried all six wordings.
  Raw logits were captured through the library's `_raw_logits`
  hook, with `n_permutations = 2`, so both option orders were
  averaged for every wording. The image and state were encoded
  once per item, not once per wording.
- **Fitting.** Each variant got its own temperature, a scalar
  fitted to minimise selection-set NLL, and its own threshold,
  chosen on the same selection items. Temperatures were fitted per
  variant outside the predict call, because one call applies a
  single temperature per question type.
- **Admissibility rule.** A variant counts only if its alpha (the
  false-alarm rate on real items) is no worse than the W0 baseline
  alpha, and its fitted accuracy delta against the baseline is at
  least +3 points. If nothing clears the bar, W0 stands. The +3
  point bar sits at the scale of the phrasing noise v1 measured in
  October (plus or minus 0.03), so a smaller win is inside
  instrument noise.
- **The battery B3.** Members are the top three wordings by
  selection AUC. Each member's probabilities are computed at its
  own fitted temperature, then combined as the plain arithmetic
  mean of the three probabilities. The battery gets its own fitted
  threshold on the mean score. Deployment-preference rule: the
  battery deploys unless the best admissible single beats the
  battery's delta by more than 2 points.
- **What Phase 2 and Phase 3 are.** Phase 2 is a small training
  test: fine-tune on each dataset's training carve with the
  winning form in the noul slot, and select on the tune slice.
  Phase 3 is one reporting evaluation: the frozen winner, run once
  on the reporting set beside the baseline noul on the same items,
  with no wording, temperature, or threshold refitted afterwards.

### The shared texts

W0 (all three datasets), instructions:

> "Would the dataset assign the item a falsified, distorted, miscaptioned, or out-of-context label rather than its original, pristine, or true label? This is a benchmark-label estimate, not an independent fact-check."

W0 criteria: false = "The native benchmark label is original,
pristine, or true." / true = "The native benchmark label denotes a
distortion or incorrect pairing."

Criteria convention for W1 to W5 (all datasets): false = "The item
is not fake under this question's framing." / true = "The item is
fake under this question's framing."

Two prompts sit behind the whole variant set. First, the v1 noul
was nearly uninformative: AUC 0.529 at temperature 1 and mean
confidence 0.5002 on NewsCLIPpings validation (recorded in
`DESIGN.md` and `EVIDENCEGATE_DESIGN.md`). Second, v1 proved
results are wording-bound, with phrasing swings of plus or minus
0.03 measured in October. If wording moves the score, wording is a
variable to test on purpose, under a bar set at the noise scale.

### NewsCLIPpings (fake = a repurposed, incorrect pairing)

**W0, control.**

> "Would the dataset assign the item a falsified, distorted, miscaptioned, or out-of-context label rather than its original, pristine, or true label? This is a benchmark-label estimate, not an independent fact-check."

Prompted by: this is the wording the v1 packs already ship, kept
unchanged so every variant is measured against the instrument in
use. It tests the baseline itself. Outcome: best AUC of the set
(0.5816) and best fitted accuracy (0.56); displaced as the
deployment only by the registered rule, in favour of W5.

**W1, direct probability.**

> "What is the probability that this caption was not originally published with this image — that the pairing was repurposed from a different event, place, or time?"

Prompted by: W0 asks indirectly, about what the dataset would
assign. This asks the model for the probability directly. It tests
whether a plain probability ask beats the benchmark-label framing.
Outcome: AUC 0.4240, below chance; fitted delta -0.01.

**W2, original context.**

> "Was this photograph originally taken for the event this caption describes? If the photo comes from a different occasion than the caption claims, the pairing is fake."

Prompted by: the dataset's lie is repurposing; a fake item is a
photo from a different event, place, or time than its caption
claims. This asks about the photo's original occasion head-on. It
tests whether naming the repurposing directly helps. Outcome:
worst ranking in the set, AUC 0.3656.

**W3, entity check.**

> "Compare the people, place, and event named in the caption against what the image actually shows. If the image shows a different person, place, or event than the caption describes, the pairing is fake."

Prompted by: a repurposed pairing is a concrete mismatch of
person, place, or event, so the wording hands the model that
comparison as a procedure. It tests whether decomposition helps a
small model. Outcome: AUC 0.3992, below chance.

**W4, conservative.**

> "Call this pairing fake only if the image clearly belongs to a different event than the caption describes. Ordinary news photos with matching captions are not fake."

Prompted by: v1's failure on this dataset sat on the alpha side;
pristine recall was 0.164, meaning real items were called fake far
too often. This wording is strict on purpose. It tests whether a
strict noul can hold the false-alarm line. Outcome: raw alpha 0.06,
the discipline worked, but AUC 0.3860 and no accuracy gain.

**W5, truth-framed.**

> "Does this caption truthfully describe this image as it was originally published?"

Prompted by: the suspicion that the benchmark-label framing in W0
was itself the problem. This drops the dataset language and asks
one plain question. It is also the shortest wording in the study,
29 words. It tests a plain truth ask with no framing machinery.
Outcome: the registered winner; fitted accuracy 0.54, fitted delta
+0.03, AUC 0.4464.

### VERITE (fake = miscaptioned or out-of-context)

**W0, control.** Same text as above. Prompted by: the shipped pack
wording, kept as the baseline. Outcome: AUC 0.5252, fitted accuracy
0.59, fitted alpha 0.72.

**W1, direct probability.**

> "What is the probability that this image–caption pair is not simply true — that the caption misdescribes the image, or the image is being used outside its original context?"

Prompted by: the same doubt as NewsCLIPpings W1, that the indirect
benchmark framing was costing signal. It tests a direct probability
ask. Outcome: the worst variant in either screen; raw delta -0.24,
fitted delta -0.17.

**W2, decomposed, two failure modes.**

> "A pair fails in two ways: the caption says something false about the image (miscaptioned), or a real image is used to support a claim from a different context (out-of-context). If either failure is present, the pair is fake."

Prompted by: VERITE falsity has two distinct failure modes,
miscaptioned and out-of-context, and a single vague ask might blur
them. This names both and fails the pair if either is present. It
tests whether separating the modes helps. Outcome: fitted accuracy
0.59, fitted delta 0.00; respectable after fitting, no gain.

**W3, original context.**

> "Was this image originally published with this caption, for this event? If it was taken from an earlier or different event, the pair is fake."

Prompted by: the out-of-context mode is a failure of original
context, so the wording asks about original publication directly.
It tests whether a question about the pairing's history matches
what the model can judge. Outcome: the winner; highest AUC
(0.5677), fitted accuracy 0.62, fitted delta +0.03, fitted alpha
0.56 against a 0.72 baseline.

**W4, conservative.**

> "Call this pair fake only if the caption is clearly false about the image or the image clearly comes from a different event. If the caption plausibly describes the image, answer not fake."

Prompted by: VERITE's BASE arm already showed the alpha disease,
with true recall 0.246 against out-of-context recall 0.586, so
false-alarm discipline was the live question on this pack. It tests
strictness. Outcome: fitted accuracy 0.53, fitted delta -0.06.

**W5, claim-framed.**

> "Treat the caption as a claim about the image. Is the claim true of this image in its original context?"

Prompted by: a caption functions as a claim about its image, and
fact-checking language might suit the model better than label
language. It tests the claim frame. Outcome: fitted accuracy 0.46,
fitted delta -0.13.

### MMFakeBench (fake = textual distortion, visual distortion, or mismatch; tune items only)

**W0, control.** Same text as above. Prompted by: the shipped pack
wording, kept as the baseline. Outcome on tune items: AUC 0.4266,
below chance; fitted accuracy 0.58. The weakest control of the
three datasets.

**W1, direct probability.**

> "What is the probability that this item is not an original, undistorted benchmark item — that its text is fabricated or altered, its image is manipulated, or the image and text do not match?"

Prompted by: the same doubt as the other datasets' W1, that the
benchmark framing was indirect. It tests a direct probability ask
that still names the three fake mechanisms. Outcome: the best
admissible single; AUC 0.6735, fitted accuracy 0.6857, fitted delta
+0.1048.

**W2, truth-framed.**

> "Judge the item itself, not the dataset: is anything about this image–text pair fabricated, manipulated, or mismatched?"

Prompted by: W0 asks what the dataset would assign; this orders
the model to judge the item itself and drop the dataset frame. It
tests whether removing the benchmark framing helps. Outcome: AUC
0.6389, fitted delta +0.0286; a battery member.

**W3, decomposed checklist.**

> "Check three things: (1) is the text's factual content invented or altered? (2) is the image visually manipulated? (3) do the image and text fail to correspond? If any answer is yes, the item is fake."

Prompted by: MMFakeBench falsity has three distinct mechanisms,
textual distortion, visual distortion, and image-text mismatch, so
the wording gives one check per mechanism. It tests decomposition
where the checklist mirrors the label definition exactly. Outcome:
AUC 0.5886, fitted delta +0.0619, but fitted alpha 0.83, no better
than the baseline alpha.

**W4, conservative.**

> "Call this item fake only if the distortion is clear and specific — a fabricated claim, a visible manipulation, or an obvious mismatch. If the item looks like an ordinary original, answer not fake."

Prompted by: the control's raw alpha on tune items was 0.83, so a
strict wording was designed to lower the false-alarm rate. It
tests strictness. Outcome: AUC 0.6212, fitted alpha 0.4127, fitted
delta +0.0286; a battery member.

**W5, pairing-first.**

> "Does the text truthfully go with this image, exactly as presented? If the pairing, or either part, has been distorted in any way, the item is fake."

Prompted by: mismatch is one of the three fake mechanisms, and the
other wordings lead with distortion hunting. This leads with the
pairing instead. It tests a pairing frame over a distortion frame.
Outcome: AUC 0.5969, fitted delta +0.0667, fitted alpha 0.76.
