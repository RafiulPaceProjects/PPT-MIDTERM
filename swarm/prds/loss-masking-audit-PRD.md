# PRD: Loss masking audit and commitment controls

Slug: loss-masking-audit. Registered 2026-11-24. Status: BOARD-PASSED
2026-11-24, with the board's fixes applied (see Board pass). Avenue: research-brain avenues row "Loss masking audit and
commitment controls for the training pipeline" (MMFakeBench row; the audit
itself covers the shared training pipeline, so NewsCLIPpings is in scope).
Pattern source: Chodavarapu, "What Does Hard-Negative Fine-Tuning Teach
MLLMs?", arXiv 2611.18701, as settled in LIT_REVIEW_2026-11-24.md. No
experiment runs under this PRD until the owner approves the run itself.

## Hypothesis

The library losses score tokens unevenly across question forms, so the
noul screen trains weaker than the choice question; that is why the
scale probe left 274 of 300 uncertain.

Scope, fixed by the board: the causal claim about the scale probe is
scoped to soft_ce. The scale probe, Stage B, and the W1 arm were all
trained with soft_ce (record sections 3.6, 5.1, 5.4). The rlcd audit
table is still produced, but as a v1 grid footnote: a masking defect
in rlcd, which ran only in the v1 grid, explains none of the 274 of
300 outcome and carries no part of this hypothesis's verdict.

## The exact question

For each question form (the choice question and the noul question) and
each loss the study used (the library's rlcd objective and soft_ce),
which tokens does the loss actually score: prompt tokens, placeholder
tokens, or answer tokens? And, second, does a commitment control run
on validation items only (a gray-image ablation judging pass, with a
shuffled-image arm as its positive control) move the uncertain count
and the headline read in the direction the hypothesis predicts? (The
option-order control from the first draft is deleted; see Board
pass, fix 5.)

## Baselines, quoted from the record

- Scale probe (Amendment 15, record section 5.4): trained at 10,040
  items, read on the frozen 300 probe items pair-only. Headline 0.0467,
  accuracy including uncertain 0.5000, uncertain 274 of 300, pristine
  headline 0.0132, falsified headline 0.0811. Stage A P0 on the same
  items: headline 0.4300, including uncertain 0.5133, uncertain 44.
  Paired headline delta −0.3833, interval [−0.4433, −0.3267].
- Stage A probe (record section 3.5): P0 headline 0.4300, P1A evidence
  headline 0.4500, scored at the registered noul threshold of 0.5.
- Screen AUCs on the probe (record section 3.9): Stage A pair-only
  0.5911, Stage A evidence 0.5819, Stage B pair-only 0.5917, Stage B
  evidence 0.5798. The v1 NewsCLIPpings trained arm's screen sat at AUC
  0.529 with mean confidence 0.5002 (record section 4.1).
- MMFakeBench confirmation partition (record section 5.1): the
  W1-trained model's noul AUC is 0.8730 at its frozen form
  (temperature 2.462, threshold 0.65); the base model's W0 screen on
  the same items is 0.4308. Per-class recalls on that partition:
  visual distortion 0.4000 and original 0.4333 are the two weakest
  classes; mismatch is third at 0.4556. (First-draft misquote of
  this ranking corrected by the board; see Board pass, fix 1.)
- The record's own caution (section 2.1): which published method the
  library's rlcd corresponds to was never verified against the library
  source. This audit reads the library source, so it closes that gap
  for the loss implementations as installed.

## Split

- Audit leg: no items. It reads the installed laya package (dev install,
  laya 0.2.0.dev0) and the study's record-building code only.
- Controls leg, NewsCLIPpings: the frozen 300-item probe (validation
  split, seed 20261122, probe_items.jsonl, IDs identical to the v1 run
  IDs) and, for the Stage B checkpoint, the Stage B carve's 100 tune
  items. Validation and tune items only.
- Controls leg, MMFakeBench: the 300-item confirmation partition of
  mmfakebench_val_grouped_split_v1, item-disjoint from the 700-item
  development partition by construction. Concession, recorded by the
  board: this partition already served as the confirmation read for
  the W1 screen, so every MMFakeBench result under this PRD is an
  exploratory mechanism check, never a confirmation.
- HARD RULE: the MMFakeBench test set is closed. It was scored exactly
  once. Nothing in this PRD touches it, re-scores it, or reads it.

## Protocol, in order

0. Inventory as a fail-closed gate, at no cost. Confirm each
   checkpoint the controls leg needs (scale probe, Stage A winner,
   W1-trained) by file presence AND by a safetensors header
   completeness check (byte count against the header's data end;
   the truncated VERITE adapted pull in record section 5.4 is the
   failure this guards against). The drafting-pass inventory is
   appended below: the scale probe checkpoint
   (v2_probe/uplift/pulled_uplift/runs/scale10k_4900/model.safetensors),
   the Stage B checkpoint, the Arm W checkpoint, and the VERITE
   adapted checkpoints are present locally; the Stage A winner and
   the W1-trained checkpoint were not located in that pass and must
   be confirmed here (the Stage A winner's recorded route is its
   Hugging Face repo). If a required checkpoint is absent or fails
   the header check, the controls leg does not run and this PRD
   returns to the board for re-registration of its criteria; it
   does not silently deliver the audit leg alone. The same gate
   confirmed that no per-order logit files exist under any name the
   drafting pass could find, so the first draft's option-order
   control is deleted (Board pass, fix 5).
0.5. Version provenance: record the training-time laya package
   version from the run logs or receipts and diff the loss files
   against the installed copy. If the versions cannot be matched,
   every audit conclusion is scoped in writing to "the loss as
   installed on 2026-11-24," not to the study's trainings.
1. Read the loss implementations in the installed package. For each
   loss and each question form, produce a token-accounting table
   with three registered numbers: absolute scored answer tokens per
   record, the scored share that is answer tokens (with placeholder
   and prompt shares beside it), and mean loss weight per answer
   token. Verify the table against one tiny synthetic batch run
   locally (no training, no scored items).
2. Compare the table against the Chodavarapu pattern (a loss scoring
   mostly placeholder tokens, a corrected loss on answer tokens, a
   fine-tuning commitment bias) and state, per loss and form, whether
   the pattern is present.
3. Gray-image ablation judging pass, with a positive control.
   Pair-only judging in three arms per item, every input and the
   scoring path identical, thresholds passed explicitly: the item's
   own image (a same-session control read), a uniform gray image,
   and a shuffled image drawn from another item (the positive
   control: a read that survives a wrong image but not a gray one
   is reading something other than pairing, and the two arms keep
   input shock and image use apart). NewsCLIPpings probe 300 with
   the scale probe checkpoint as the PRIMARY read (its baselines:
   headline 0.0467, including uncertain 0.5000, uncertain 274 of
   300), and with the Stage A winner as the secondary read
   (baselines: headline 0.4300, uncertain 44). MMFakeBench
   confirmation 300 with the W1-trained checkpoint at its frozen
   form, temperature 2.462 and threshold 0.65, matching the baseline
   read. Report headline accuracy, accuracy including uncertain,
   uncertain count, and noul AUC per read, each gray delta with a
   paired resampling interval (10,000 resamples, seed 20261122).
4. Write the result into research-brain (findings or lessons) with
   read-back, and commit the run outputs under swarm/ in the repo.

## Success and failure criteria (registered numbers)

Audit leg:
- The deliverable is the token-accounting table itself; it either
  exists for both losses and both forms or the audit has failed on
  its own terms. The table is reported in full, for all shares,
  whatever the verdict.
- Masking defect CONFIRMED (soft_ce only, for the scale probe
  claim) if the noul form scores zero answer tokens, OR its
  absolute scored answer-token count is under half the choice
  form's AND its scored share is under half AND the share gap is
  at least 25 points. The count condition exists because the two
  forms have different prompt lengths: a share ratio alone can
  fall below one half through prompt length, not masking.
- Masking defect RULED OUT if the two forms' scored answer-token
  shares sit within 10 points of each other for both losses.
- Any result between those bands is INDETERMINATE, a registered
  third outcome: the hypothesis verdict is then neither confirmed
  nor ruled out, and no verdict word may be improvised afterward.

Controls leg:
- Commitment problem SUPPORTED on NewsCLIPpings if the gray-image
  fall in headline accuracy, against the same-session own-image
  read, is under 0.03 as a point estimate AND the paired
  resampling interval for the fall lies entirely below 0.03. If
  the point fall is under 0.03 but the interval crosses 0.03, the
  leg is INCONCLUSIVE. The shuffled-image arm is reported beside
  it; if the shuffled read falls materially more than the gray
  read, the gray result is read as input shock, not commitment,
  and the leg is INCONCLUSIVE in those words.
- The MMFakeBench gray read is a text-dominance DESCRIPTIVE read
  only, with its interval reported and no commitment verdict
  attached: record section 7 already establishes that MMFakeBench
  falsity is largely stylistic and text-carried, so a model keeping
  its read without the image is the record's own prediction there,
  not a defect signal.
- Hypothesis NOT SUPPORTED overall if the audit rules the defect
  out and the NewsCLIPpings control lands outside its margin. The
  274 of 300 disagreement then stands unexplained by masking or
  commitment, and stays an open finding in those words. A control
  dropped for any reason blocks the NOT SUPPORTED verdict: the
  outcome is then PARTIAL, naming the missing control.

## Budget and stop rule

Audit leg: $0. Controls leg: $0.45 to $0.90. Before the full pass,
a 20-item timing run measures seconds per judging call; the
measured figure is printed in the run log and the dollar range is
re-derived from it. Pod setup and idle time count against the
stop. Leg priority if spend runs short: the scale probe gray read
first, the MMFakeBench descriptive read second, the Stage A gray
read third. Stop rules: this PRD stops at $0.90 of its own spend,
or the moment cumulative swarm spend reaches $3.00, whichever
comes first. The audit leg completes regardless, because it is
free. Any pod started is terminated in the same run.

## Shared cap allocation (all four PRDs, fixed by the board)

The four PRDs' stated maxima sum to $4.95 against the $3.00
cumulative cap, so the board fixed one allocation, in run order,
cheapest first: (1) loss-masking-audit, at most $0.90; (2)
similarity-audit, at most $0.45; (3) relevance-question-pilot,
killed as drafted, its former $1.65 share unallocated and returned
to the cap pending a re-registered pilot; (4) armw-dense-rerank,
killed, $0. Reserved for board-passed PRDs: $1.35 of $3.00. Every
run reads the research-brain runs ledger at its start for the true
cumulative figure; no PRD assumes the cap is untouched.

## Resource

Ladder order: this VM and the owner's Mac mini first (code read and
embedding-free recomputation), then Colab free GPU, then Hugging
Face PRO ZeroGPU, RunPod last and only inside the budget above.

## Board pass

BOARD-PASSED 2026-11-24. Three critics (protocol and statistics;
cost, registration, and internal fit; novelty and venue fit) argued
against the draft. All three returned PASS WITH FIXES. The fixes
they won, applied above:

1. Misquote corrected: the confirmation partition's two weakest
   classes are visual distortion (0.4000) and original (0.4333);
   mismatch (0.4556) is third. The draft had named original and
   mismatch as the two weakest.
2. The hypothesis is scoped to soft_ce for the scale probe claim;
   the rlcd table is a v1 grid footnote with no bearing on the
   274 of 300 verdict.
3. The token-accounting criteria now register three numbers per
   loss and form (absolute scored answer tokens, scored share,
   mean loss weight per answer token), and CONFIRMED requires the
   count condition as well as the share conditions, so prompt
   length alone cannot confirm a defect. INDETERMINATE is a
   registered third outcome between CONFIRMED and RULED OUT.
4. Step 0 is a fail-closed gate with a safetensors header
   completeness check; a missing checkpoint returns the PRD to
   the board instead of narrowing the design mid-run. Step 0.5
   adds training-time package version provenance, with a written
   scope limit if versions cannot be matched.
5. The option-order control is DELETED. The drafting-pass
   inventory found no per-order logit files (the drill-down
   captured order-averaged logits), and the board ruled that a
   control which would be dropped mid-run may not sit in a
   board-passed PRD. Concession recorded with the deletion: had
   it run, it would have been a base-checkpoint, tune-item result
   only, unable to support or refute any claim about a trained
   checkpoint.
6. The gray-image control now runs on the scale probe checkpoint
   as the primary NewsCLIPpings read (the draft had named the
   Stage A winner, whose 44 uncertain items are not the
   phenomenon under test), carries a paired resampling interval
   for every delta with the verdict read off the interval, and
   adds a shuffled-image positive control arm. The MMFakeBench
   gray read is relabelled a text-dominance descriptive read with
   no commitment verdict, and its frozen operating point
   (temperature 2.462, threshold 0.65) is stated.
7. Budget discipline: a 20-item timing run precedes the full
   pass, pod setup and idle time count against the stop, leg
   priorities are named, and the shared cap allocation table is
   added. A dropped control blocks the NOT SUPPORTED verdict
   (outcome PARTIAL, naming the control).

Concessions recorded, no fix available inside this PRD: the
MMFakeBench confirmation partition has already served as a
confirmation read once, so its results here are exploratory
mechanism checks, never confirmation; and the rlcd published
identity question stays open (claims section).

## What would change the paper's claims, and what changes nothing

- If a masking defect is confirmed: the paper's trained numbers stand
  (they are scored facts), but every training-side explanation is
  re-scoped, the recipe claim gains a caveat that the screen was
  trained under a defective loss accounting, and a corrected-loss
  retrain becomes the first follow-up avenue. Scope limit, recorded
  by the board: this audit closes token accounting for the
  installed code only, and the published method identity of rlcd
  stays open.
- If the gray-image control supports the commitment problem on
  NewsCLIPpings: the pairing null gains a mechanism (the model was
  not reading the image), which strengthens the null's interpretation
  without changing any number.
- If nothing is found: no claim changes. The scale probe's 274 of 300
  disagreement remains an open, unexplained finding, and this PRD's
  value is that two named explanations were priced and ruled out.
