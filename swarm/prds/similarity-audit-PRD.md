# PRD: Similarity audit on the frozen snapshots

Slug: similarity-audit. Registered 2026-11-24. Status: BOARD-PASSED
2026-11-24, with the board's fixes applied (see Board pass). Avenues: research-brain avenues rows "MUSE similarity
audit on frozen snapshots" (NewsCLIPpings) and "MUSE similarity audit
on frozen snapshots" (VERITE). Pattern source: Papadopoulos et al.,
"Similarity over Factuality" (MUSE and AITR), WACV 2025, as settled
in LIT_REVIEW_2026-11-24.md, with the board's concession recorded
there: the MUSE classifier head does not transfer, only its audit
does. No experiment runs under this PRD until the owner approves the
run itself.

## Hypothesis

A similarity-only score on the frozen snapshots ranks these items
about as well as the model's screen, priced at the measured gap,
with no claim about the model's mechanism. (The draft's "surface
similarity in disguise" wording is deleted by the board: this audit
uses an external encoder, not the LAYA model, so equal ranking
power shows that two systems rank alike, not that the screen uses
similarity.)

## The exact question

On identical items, how well does image-text surface similarity alone
rank falsified against pristine (NewsCLIPpings) and fake against true
(VERITE), compared with the model's own noul screen on the same
items? The audit prices the similarity explanation of the pairing
reads before any new training is proposed.

## Baselines, quoted from the record

- NewsCLIPpings screen AUCs on the 300 probe items (record section
  3.9): Stage A pair-only 0.5911, Stage A evidence 0.5819, Stage B
  pair-only 0.5917, Stage B evidence 0.5798. The headline comparator
  for this audit is the Stage A pair-only 0.5911.
- NewsCLIPpings zero-shot screen (record section 2.2): noul AUC 0.549,
  with the baseline collapsing toward falsified (falsified recall
  0.944, pristine recall 0.084).
- VERITE: no model screen AUC on the held-out 200 exists in the
  record (the tune control W0 reads 0.5252 on 100 tune items,
  record section 4.2; the Phase 3 W3 form reads 0.4764 on the
  held-out 200, record section 4.4, a different exercise from this
  audit's screen). The board therefore cut the VERITE leg to a
  standalone descriptive number: similarity AUCs on the held-out
  200 with no comparator sentence and no verdict bands. The
  headline comparison is NewsCLIPpings only.
- VERITE held-out four-arm reads (record section 3.8), for context on
  the same 200 items the audit scores: BASE accuracy 0.285, TRANSFER
  0.320, EVIDENCE 0.325, ADAPTED 0.330.
- Frozen evidence state (record sections 3.2 and 3.3): probe pools
  597 of 600 pairs non-empty, headline coverage 193 of 300 probe
  items; VERITE 349 of 400 pools, coverage 89 of 200 held-out items.
  Every v2 number is computed against the hashed snapshots; this
  audit does the same and runs no fresh retrieval.

## Split

- NewsCLIPpings: the frozen 300-item probe (validation split, seed
  20261122, probe_items.jsonl), with its frozen evidence snapshots.
  Evaluation images are streamed and never stored, per the v1
  discipline; embeddings are computed in the pass and the images are
  discarded.
- VERITE: the frozen held-out 200 (group-aware 80:20 carve of the
  1,001 local rows, seed 20261122; 65 true, 65 miscaptioned, 70
  out-of-context), with its frozen snapshots.
- No training items are scored as evaluation, and no element of
  this audit is fitted on any item. The draft's fitted secondary
  read (a logistic fit on the similarity features) is DELETED by
  the board: it is the MUSE classifier head returning under
  another name, and the lit-review concession this PRD claims to
  obey is that the head does not transfer, only the audit does.
- HARD RULE: the MMFakeBench test set is closed and is not part of
  this audit in any form. MMFakeBench items are not used.

## Protocol, in order

0. Verify snapshot hashes at load (the study's A10 discipline);
   a mismatch fails closed and is logged. Verify the registered
   encoder (step 1) is available; if it is not, the run stops and
   the PRD returns to the board. Log a per-image content hash for
   every streamed NewsCLIPpings image at load. Concession,
   recorded by the board: the images are streamed and never
   stored, and no prior-run image hashes exist to match against,
   so item identity rests on the frozen item IDs and the
   dataset's own indexing; that limit is stated in the report.
1. The encoder, named here in the PRD (not deferred to the run
   log): OpenAI CLIP ViT-B/32, checkpoint string
   openai/clip-vit-base-patch32. No alternates are tried; encoder
   shopping is banned by this PRD, and any run using a different
   checkpoint is a different audit requiring a new PRD. The run
   log only confirms the registered encoder was used.
2. Per item, compute the raw similarity features: cosine similarity
   between the image and its caption; and, where the item has frozen
   evidence passages, the maximum and mean cosine similarity between
   the caption and its passages (the MUSE feature family, reduced to
   an audit, not a trained head). The passage count is bounded and
   counted at drafting from the assembled files: the headline-arm
   pools hold 512 passages over 193 covered NewsCLIPpings items and
   244 passages over 89 covered VERITE items, 756 passages in total.
   Score direction, registered: higher cosine predicts pristine, so
   the falsified ranking score is minus cosine. No inversion of the
   direction is permitted after scoring.
3. Primary read: AUC of the image-caption score against gold, on the
   identical items the model screens were read on (NewsCLIPpings
   300; VERITE 200, descriptive only). Secondary read: AUC of the
   evidence-similarity features on the covered subsets, reported
   with their coverage beside them, descriptive only; any sentence
   comparing a subset read to a model AUC must use the model's
   screen AUC recomputed on the identical covered subset, printed
   beside it, or the comparison is not printed.
4. VERITE per-class reads: beside the pooled VERITE similarity AUC,
   print true-against-miscaptioned and true-against-out-of-context
   AUCs. The two fake classes fail pairing in different ways, and a
   pooled figure can hide a strong read on one class and a chance
   read on the other; the pooling is a stated limit of the leg.
5. Report: NewsCLIPpings similarity AUC, the model's screen AUC on
   the same items, the gap, and the paired resampling interval for
   the gap (10,000 resamples, seed 20261122); VERITE similarity
   AUCs as standalone descriptives. Write the result into
   research-brain with read-back; commit outputs under swarm/ in
   the repo.

## Success and failure criteria (registered numbers)

NewsCLIPpings (headline leg), against the Stage A pair-only screen
AUC of 0.5911 on the same 300 items, verdicts read off the paired
resampling interval for the gap (similarity AUC minus model AUC),
not off point estimates alone, because an AUC near 0.59 on 300
items carries a standard error of roughly 0.03 to 0.04:
- Hypothesis SUPPORTED if the gap interval lies entirely within
  plus or minus 0.05. Strong form: the similarity AUC point
  estimate at or above 0.5911 with the interval's lower end above
  minus 0.05.
- Hypothesis FAILS if the similarity AUC is at or below 0.549 (the
  zero-shot screen's own AUC) AND the gap interval lies entirely
  below minus 0.05.
- Anything else is INCONCLUSIVE in those words: the ranking is
  priced at the measured gap and its interval, and no stronger
  sentence is written.
VERITE (descriptive leg): the similarity AUCs are reported alone,
with their item counts. No bands, no comparator, no verdict word.

## Budget and stop rule

$0 to $0.45, against the swarm's $3.00 cumulative cap. The
expected cost is $0: embedding 500 items and 756 passages is a
free-rung job. Stop rules: this PRD stops at $0.45 of its own
spend, or the moment cumulative swarm spend reaches $3.00,
whichever comes first; and a wall-clock stop of 4 hours on the
first rung, after which the PRD returns to the board instead of
climbing the ladder silently. Any pod started is terminated in
the same run.

Shared cap allocation (fixed by the board, in run order, cheapest
first): (1) loss-masking-audit, at most $0.90; (2)
similarity-audit, at most $0.45; (3) relevance-question-pilot,
killed as drafted, its former $1.65 share unallocated pending a
re-registered pilot; (4) armw-dense-rerank, killed, $0. Reserved
for board-passed PRDs: $1.35 of $3.00. Every run reads the
research-brain runs ledger at its start for the true cumulative
figure; no PRD assumes the cap is untouched.

## Resource

Ladder order: the owner's Mac mini (MPS) first, then this VM, then
Colab free GPU, then Hugging Face PRO ZeroGPU, RunPod last and only
inside the budget above.

## Board pass

BOARD-PASSED 2026-11-24. Three critics (protocol and statistics;
cost, registration, and internal fit; novelty and venue fit) argued
against the draft. All three returned PASS WITH FIXES, conditional
on the blockers below. The fixes they won, applied above:

1. The fitted secondary read is DELETED in full (protocol step,
   reporting, criteria). Two critics would have settled for
   registering or demoting it; the novelty critic's blocker wins,
   because the lit-review board's concession was that the MUSE
   head does not transfer, and a logistic fit on similarity
   features is that head under another name.
2. The "in disguise" mechanism claim is deleted everywhere. The
   hypothesis now claims only that a similarity score ranks these
   items about as well as the screen, priced at the measured gap.
3. The encoder is named in the PRD (openai/clip-vit-base-patch32),
   not deferred to the run log, with an availability gate at
   step 0.
4. The VERITE leg is cut to a standalone descriptive number. No
   same-item model screen AUC on the held-out 200 exists in the
   record, and the draft's two comparators (0.5252 on tune items,
   0.4764 on a different form) offered two chances to land in a
   favourable band. Per-class VERITE AUCs are printed beside the
   pooled figure, and the pooling is a stated limit.
5. Verdicts are read off a paired resampling interval for the
   AUC gap, registered here; the failure line is corrected to
   0.549 (the draft called 0.53 "near" the zero-shot 0.549, which
   sits above it). The score direction is registered (higher
   cosine predicts pristine) and may not be inverted after
   scoring.
6. Subset comparisons require the model's screen AUC recomputed
   on the identical covered subset, printed beside the subset
   read, or no comparison is printed.
7. The passage count is stated (756 headline-arm passages), a
   4-hour wall-clock stop is added, and the shared cap allocation
   table is added.

Concessions recorded: streamed-image provenance cannot be proven
retroactively (step 0 states the limit); and on NewsCLIPpings, in
the words the board required: this audit prices a near
definitional baseline, and a supported result adds a priced
baseline to the paper, not a new explanation of the null.

## What would change the paper's claims, and what changes nothing

No claim in record section 7 changes in either direction: the
record already reports screen AUCs of 0.55 to 0.59 and already
concludes the pair carries almost no learnable signal. The only
paper change either outcome produces is one priced baseline
sentence in the NewsCLIPpings interpretation paragraph:
- If supported: the sentence states that a named CLIP similarity
  score ranks the probe items about as well as the model's
  screen, at the measured gap and interval.
- If it fails: the sentence states that surface similarity was
  priced and ruled out at the measured gap, so the null does not
  rest on an unpriced rival explanation.
This audit runs no training and reopens nothing: the MMFakeBench
verdict, both nulls, and every registered read stay exactly as
they are.
