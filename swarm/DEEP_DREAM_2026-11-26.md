# Deep dream pass, 2026-11-26

## Method

One pass, owner-ordered as a deep version of the swarm's hourly dream
step. Inputs: all 20 findings, all 22 avenues, and all 24 lessons in
research-brain; the nine extractions from the 2026-11-26 READ passes
(SAFE-MR, Fact or Fake, Entropy Alone, MM-AQA, Evidence-Order
Calibration, ReFrain, Evidence Chain Evaluation, X-POSE/TRENT,
SIEVES); the standing novelty architecture (NOVELTY_HUNT,
DEEP_CHECK_NOVELTY, NOVELTY_IDEAS_FROM_REVIEW, all 2026-11-24); and
the seven surviving claims in LAYA_FINAL_RECORD section 7.
Combinations were built in clusters of three or more elements, not
pairs. Each candidate went through a board of three opposed critics
(novelty, methods, feasibility). Nothing already killed in the record
was re-proposed without new evidence; the kills in those files carry
owners and were treated as binding. Cost: $0, desk work only. The
MMFakeBench test set stays closed; every candidate below uses
validation, tune, probe, or published splits only.

## The candidates

**D1. The three-leg abstention audit.** The standing lead (H-A)
restates rivals by one leg: decided fraction. Three of today's
findings each supply a second and third leg. ReFrain's accounting
counts what an abstention stage discarded against the system's own
no-abstention read, and shows a net change of 0.37 points hiding 62
lost correct answers. Entropy Alone shows a trigger can post a
strong detection score while failing every strict target risk it was
tuned to, which gives a stated-target delivery check. Evidence Chain
Evaluation shows selective accuracy rising with no calibration win,
which is why the third leg is a delivery check and not another
accuracy. Cluster: H-A (avenue b9bdee75) + finding 8a61539e +
finding 772b7b41 + finding 97af04b7. Killed by: every obtainable
system delivering its stated target risk with a negligible
lost-correct count, which would leave legs two and three measuring
nothing. Cost $0 desk, gated on the same acquisition as H-A.
Datasets: all three benchmarks, published and validation splits.

**D2. The trigger race, sliced by insufficiency type.** The
registered sufficiency race (N5, avenue f874e11b) runs pooled: one
winner over all items. MM-AQA's finding (0420e10d) says abstention
behaviour tracks how the insufficiency is built: absent evidence is
refused at 86.4 percent, contradictory evidence at only 37.6
percent. A pooled race can crown a trigger that wins on the easy
slice and fails exactly where refusal is hardest. The cluster runs
the same three-way race (disagreement, sufficiency probability,
representation probe) separately on absent, degraded, and
contradictory slices of the frozen probe, and a trigger wins a slice
only under a per-slice lost-correct budget (finding 8a61539e).
Killed by: the trigger ranking coming out identical in every slice,
in which case slicing adds nothing and the pooled race stands.
Cost: inference passes shared with the H-H and N5 setup, $0 marginal
on the A100; slice tagging of the 300 probe items is desk work.
Datasets: NewsCLIPpings frozen probe, VERITE held-out as second
read. Validation and probe splits only.

**D3. Calibration expiry under evidence drift.** Record claim 3 says
a temperature fitted on one distribution harms another and a matched
split-half fit repairs it. H-C prices retrieval drift in set
membership (Jaccard 0.2161 at one day) and, queued, in verdicts.
Nobody has priced drift in the calibration fit itself: does the
snapshot-fitted temperature still calibrate on the drifted evidence
for the same items, and does a split-half refit on the drifted half
repair it, with every change read against the re-judging noise floor
(finding 743f3fce) and reported with stated-target delivery
(finding 772b7b41)? Cluster: claim 3 + avenue 02e7e80d (H-C) +
finding 743f3fce + finding 772b7b41. Killed by: the snapshot-fitted
temperature holding on drifted evidence, which kills the avenue and
hands claim 3 a stated boundary instead. Cost: rides the one
network window H-C already needs; judging passes inside the cap.
Dataset: NewsCLIPpings probe, validation only.

**D4. Temporal validity of probe evidence.** X-POSE prices a
past-only evidence rule at about 0.9 points for its own system
(finding fd3acadf), so temporal discipline is cheap. This study's
own evidence audit found zero fact-check passages in 193 non-empty
probe sets (finding b3ed2487), a fact that exists only because
someone counted. Nobody has counted the simpler leak: how much of
the frozen probe evidence was published after the claim it judges.
Step 1 is a census on held snapshots, $0. Step 2, only if timestamps
cover a stated majority of items, removes post-claim evidence and
re-judges under abstention accounting with lost-correct counts
(finding 8a61539e). Killed by: timestamps missing for most items
(the result is then a one-line recoverability note), or removal
moving nothing beyond the noise floor. Datasets: NewsCLIPpings and
VERITE probe evidence. Validation and probe splits only.

**D5. The auxiliary-signal admission test.** Fact or Fake shows an
authenticity signal injected as evidence degrading a strong verifier
on two benchmarks and suppressing its further search (finding
ab5e5e06). The similarity score is the candidate signal this study
actually holds, and it collapses under leakage control (finding
fd3acadf). Avenue 4160bc18 runs similarity as a baseline under an
evidence-quality gate; the reverse direction, admitting a signal
into the typed decision, is untested. The cluster registers an
admission test any non-evidence signal must pass on the frozen
probe: verdict movement, lost-correct and repaired-error counts
against the no-signal verdicts, and performance change inside the
strata where retrieval returned material, which is the measurable
form of evidence suppression in a one-shot system. SIEVES supplies
the gate design if a signal passes (finding 504e4ef9). Killed by:
the demonstration signal moving no verdict beyond the noise floor
and losing no correct answer. Cost: inference passes inside the cap;
the similarity leg waits for the H-D encoder window. Dataset:
NewsCLIPpings frozen probe, validation only.

**D6. Operating-point provenance as a fourth restatement tag.**
Combine finding 77d29bf1 (fitted reads silently replaced the
registered rule in this study's own scorer), record claim 6 (16 of
18 fitted temperatures at the grid cap), and N1's provenance tags:
tag each comparator with whether its reported operating point was
fitted on the split it is reported on.

**D7. The sufficiency label ceiling.** SAFE-MR's sufficiency labels,
drafted by a frontier model with mostly single human review, reached
only 82 percent pre-adjudication agreement. If sufficiency labels
agree that loosely, the sufficiency trigger in the N5 race has a
ceiling set by label agreement, and the race should report trigger
performance against that ceiling.

**D8. Structural explicitness as a cross-dataset predictor.** Code
each benchmark's evidence by structural explicitness (MM-AQA) and
predict each system's abstention profile per dataset in advance,
extending record claim 2 (adaptation gains are dataset-conditional)
from training outcomes to abstention behaviour.

## The board, in short

Novelty critic. D1's three legs are each owned in their home
settings (ReFrain owns lost-correct accounting in QA, Entropy Alone
owns the stated-target check in short-form QA, H-A owns the decided
fraction), but the composed instrument, an outward three-leg audit
on these benchmarks, is occupied by no one in the record; it is the
lead growing, not a new field. D2 is the first candidate the pooled
race cannot absorb, because its claim is about the ranking flipping
by slice. D5 survives only narrowed: Fact or Fake owns the detector
version inside an agent pipeline, so the claim must be the
typed-decision version under this accounting, nothing broader. D8
walks into a grave the record already dug.

Methods critic. D1's legs two and three need rivals' no-abstention
reads and stated target risks, which many systems never published;
those cells will land as not recoverable. That is the H-A answer,
not a defect: recoverability is the finding. D2's slices shrink the
probe to roughly a hundred items each and every interval widens; the
registered falsifier (identical rankings) is what keeps the design
honest. D3's ECE reads on a few hundred items are coarse; the paired
split-half comparison on identical items carries it. D4 stands or
falls on timestamp coverage, which is why the census gates the
experiment. D5's suppression leg had to be narrowed at the board:
this system has no iterative search to suppress, so the strata read
is the honest form. D6 and D7 are real, and both are parts of
registered avenues rather than avenues.

Feasibility critic. D1 starts tonight at $0 on this study's own
systems. D4's first step is $0 and answers in one pass whether the
avenue exists. D2 shares its whole setup with H-H and N5. D3 and
D5's similarity leg each wait on a window that is already planned
for another reason, so neither asks for a new approval. D8 needs a
fourth-dataset run nobody has authorised; that is the end of it.

## Ranked survivors (all registered as proposed, none shortlisted)

1. **D1, three-leg abstention audit** (strengthens the lead, H-A).
   Avenue ddee4bdc-8569-4182-95df-992627e10c58.
2. **D2, trigger race sliced by insufficiency type** (new territory
   beside N5 and H-H). Avenue cd9428b4-de3a-468f-9625-e56d9ec24693.
3. **D3, calibration expiry under drift** (strengthens H-C and
   record claim 3). Avenue ae033c65-4d0d-44a1-ae2d-340d1fd6338e.
4. **D4, temporal validity audit of probe evidence** (new
   territory). Avenue fd744bd3-5901-46c7-8d50-47281b4580af.
5. **D5, auxiliary-signal admission test** (new territory,
   narrowed). Avenue 560aaafc-4b45-4d4a-bc6b-abcbf1a95554.

## Kills and demotions, with owners

- **D6 killed as a standalone avenue. Owner: N1** (avenue e2f7f728,
  already registered). Operating-point provenance is a fourth tag
  inside the provenance restatement, folded in there the way the N2
  residue folded into N1 in the 2026-11-24 pass. Not registered
  separately.
- **D7 demoted to a protocol note inside N5. Owner: the sufficiency
  race** (avenue f874e11b). The label-agreement ceiling is a scoping
  measurement the race's protocol should carry, not an avenue.
- **D8 killed. Owner: the C8 kill** (Calvo and Laureano, ACL 2026;
  the IJSWIS cross-corpus audit; MANYFAKE), which owns
  dataset-typing that predicts system behaviour, plus the record's
  own ruling that a retrodiction on the same datasets cannot fail.
  The rescue named in the hunt, a pre-registered prediction on a
  fourth dataset with the run authorised, is not met.

## Lesson registered

"An abstention claim travels in three numbers, not one: decided
fraction, lost-correct count against the no-abstention read, and
delivery of the stated target risk." Lesson
ccdd8682-c0a1-4d2a-8300-1c9febb20d46, confidence 0.8, read back.
Why: every single-number form has a measured failure in the record
(ReFrain's hidden 62 losses, Entropy Alone's strict-target failure,
Evidence Chain Evaluation's calibration-free selective accuracy, and
this study's own Stage B headline).

Run row: 6841d306-2715-4443-abe5-f8728b1de878. Total cost: $0.
