# PRD: Relevance as a typed question inside the EvidenceGate Judge (pilot)

Slug: relevance-question-pilot. Registered 2026-11-24. Status:
DRAFT, KILLED AS DRAFTED by the board 2026-11-24 (see Board pass).
This PRD does not run. The body below is the killed draft, kept
unmodified; the re-registration spec is in the Board pass section. Avenue: research-brain avenues row "Typed
relevance question inside EvidenceGate Judge" (VERITE). Pattern
source: Papadopoulos et al., RED-DOT, IEEE Transactions on
Computational Social Systems, 2025, as settled in
LIT_REVIEW_2026-11-24.md, with its concessions: RED-DOT's VERITE
gain (up to +33.7 percent) is their protocol and is motivation only,
never a comparator; the Aletheia coverage-scoring pattern merges
into this one and is not a separate avenue. No experiment runs
under this PRD until the owner approves the run itself.

## Hypothesis

VERITE miscaptioned recall rises above 0.0 on the held-out 200
without accuracy dropping below the adapted read 0.330.

## The exact question

The EVIDENCE arm of the VERITE four-arm track never calls an item
miscaptioned (recall 0.0000) while recovering out-of-context items
(recall 0.6429). Does inserting one typed relevance question per
evidence passage into the Judge stage, dropping passages the model
itself scores as not relevant to this pairing before the verdict
call, let the evidence arm call miscaptioned items miscaptioned,
at no cost to its overall read?

## Baselines, quoted from the record

VERITE held-out 200 (record section 3.8; 65 true, 65 miscaptioned,
70 out-of-context):

| Arm | Accuracy | Macro-F1 | Recall true | Recall miscaptioned | Recall OOC |
| --- | --- | --- | --- | --- | --- |
| BASE | 0.285 | 0.2154 | 0.2462 | 0.0000 | 0.5857 |
| TRANSFER | 0.320 | 0.2855 | 0.6615 | 0.2000 | 0.1143 |
| EVIDENCE | 0.325 | 0.2497 | 0.3077 | 0.0000 | 0.6429 |
| ADAPTED | 0.330 | 0.3310 | 0.3538 | 0.3846 | 0.2571 |

- The arm this pilot modifies is EVIDENCE: the adapted checkpoint
  (245 steps) judged with evidence. Its numbers are accuracy 0.325,
  macro-F1 0.2497, miscaptioned recall 0.0000.
- The accuracy floor in the hypothesis is ADAPTED's 0.330.
- Evidence coverage on the held-out 200 after the registered
  exclusions: 89 of 200 items (44.5 percent), record section 3.2.
  The other 111 items carry no passages; the relevance gate has
  nothing to filter on them and they are judged exactly as the
  EVIDENCE arm judged them.
- ADAPTED minus TRANSFER is +0.010, interval [−0.080, +0.095], and
  its registered success criterion was NOT MET (record section 3.8).
  This pilot does not re-open that verdict; it tests a mechanism
  the four-arm track did not have.

## Split

- The frozen VERITE held-out 200 only: the group-aware 80:20 carve
  of the local 1,001 rows, seed 20261122, frozen before the four-arm
  track ran. Identical items, identical assembled evidence pools,
  identical checkpoint as the EVIDENCE arm.
- No item is added, swapped, or dropped. An item that cannot be run
  is reported as a failure with counts, per the study's thorough-test
  discipline (DESIGN.md Amendment 6A).
- HARD RULE: the MMFakeBench test set is closed and untouched by
  this PRD. NewsCLIPpings is out of scope for the pilot; it is the
  named second step only if this pilot succeeds, under its own PRD.

## The registered instrument (frozen here, before any item is run)

- Relevance question, one per passage, asked of the adapted
  checkpoint with the item's image and caption in state, wording
  frozen verbatim: "Does this passage report facts about the
  specific people, place, event, or original publication of this
  image and caption, rather than about the general topic?" Options:
  relevant / not relevant. This is a typed question in the study's
  sense: probabilities over the two options, no free text.
- Threshold, registered and asserted, not fitted: a passage is kept
  if and only if P(relevant) is at least 0.5, at temperature 1.0.
  No threshold sweep is run on held-out items, before or after the
  verdicts; a sweep would be fitting on the evaluation set.
- Passage cap, registered: at most 4 passages enter the verdict
  call, the packing cap the study already uses (DESIGN.md
  Amendment 5, section 6.1). If more than 4 passages pass the
  relevance filter, the first 4 in the assembled order are kept
  and the rest are logged as cap-dropped.
- If every passage on an item is filtered out, the item is judged
  with an empty evidence block and logged as relevance-emptied;
  the count is reported.
- The verdict call is the registered evidence-arm choice question
  verbatim (DESIGN.md section 3), judged by the adapted checkpoint,
  scored through the same path as the four-arm track, so the reads
  are comparable line by line. Before judging, the run logs a
  configuration diff against the four-arm track's judging setup;
  any difference beyond the relevance gate itself stops the run
  until it is explained in the log.

## Protocol, in order

0. Verify the frozen snapshots' hashes at load; a mismatch fails
   closed and is logged (the study's A10 discipline). Verify the
   adapted checkpoint is the retrained, verified checkpoint of
   record section 5.4 (held-out label agreement 200 of 200 with
   the original run).
1. For each of the 89 covered items, score each assembled passage
   with the relevance question. Log per item: passages in,
   passages kept, passages dropped by the filter, passages dropped
   by the cap.
2. Judge all 200 items: covered items with their filtered evidence
   blocks, uncovered items exactly as the EVIDENCE arm judged them.
3. Score through the audited verdict path. Report accuracy,
   macro-F1, per-class recalls, the relevance-emptied count, mean
   passages kept, and the paired delta against the EVIDENCE arm
   with a paired resampling interval (10,000 resamples, seed
   20261122, the study's registered interval method).
4. Write the result into research-brain with read-back; commit
   outputs under swarm/ in the repo.

## Success and failure criteria (registered numbers)

- SUCCESS (weak form): miscaptioned recall above 0.0 (at least 1
  of 65) AND accuracy at least 0.330 AND macro-F1 at least 0.2497.
- SUCCESS (strong form): miscaptioned recall at least 0.10 (at
  least 7 of 65) AND accuracy at least 0.330 AND macro-F1 at least
  0.2497. The report must state which form was met, in those words.
- FAILURE: miscaptioned recall still 0.0, OR accuracy below 0.325
  (below the EVIDENCE arm this pilot modifies), OR macro-F1 below
  0.2497.
- Anything between (recall above 0.0 but accuracy in [0.325,
  0.330), or macro-F1 held but accuracy below the floor) is
  INCONCLUSIVE, a reportable outcome, not a licence to adjust the
  threshold and re-run.

## Budget and stop rule

$0.90 to $1.80, against the swarm's $3.00 cumulative cap
(cumulative spend is $0 today). The call count is bounded: at most
89 items times their passages (at most 5 each in the snapshot) of
relevance calls, plus 200 verdict calls. Stop rules: this PRD
stops at $1.80 of its own spend, or the moment cumulative swarm
spend reaches $3.00, whichever comes first. If the budget runs out
mid-run, the covered items are judged first and the partial scope
is reported as a scope note with counts, never silently presented
as the full 200. Any pod started is terminated in the same run.

## Resource

Ladder order: the owner's Mac mini (MPS) first (a 201M model, a few
hundred calls), then Colab free GPU, then Hugging Face PRO
ZeroGPU, RunPod last and only inside the budget above. If the free
rungs carry the run, spend stays $0 and the saving is reported.

## Board pass

KILLED AS DRAFTED, 2026-11-24. Three critics argued against the
draft. Protocol and statistics: PASS WITH FIXES. Cost,
registration, and internal fit: PASS WITH FIXES. Novelty and
venue fit: KILL, on the ground that the draft's defects are its
framing, not its details: as a RED-DOT test it tests nothing
about RED-DOT (a scored relevance step in another system, on
their protocol; this pilot is the same 201M checkpoint grading
its own evidence with one home-made binary question), its weak
success form is a single item, and its failure sentence claims a
route closure the data cannot carry. That critic's own ruling
was that a renamed self-filtering pilot with the fixes below
would be a NEW PRD, not this one passed. The chair accepts the
kill: the board did not pass this PRD, and the avenue stays
proposed, not shortlisted.

The attacks all three critics won, recorded as the
re-registration spec. A future pilot PRD must:
1. Drop RED-DOT from the hypothesis and from every success and
   failure inference, and be titled a self-filtering pilot. Its
   failure sentence may close only this wording, at this
   threshold, on this checkpoint and this carve; the sentence
   claiming the transfer route closes for a model of this size
   is deleted as an over-claim.
2. Delete the weak success form (1 of 65 is inside the study's
   own documented re-judging noise: 21 to 24 label flips per
   1,001 on re-judging, record section 5.4). Any success form
   requires miscaptioned recall of at least 0.10, with the paired
   interval for the recall change reported in the same sentence.
3. Never re-judge unchanged items: splice the stored EVIDENCE
   arm verdicts verbatim for the 111 uncovered items and for any
   covered item whose filtered block is byte-identical to its
   original; judge only items whose evidence block changed.
4. Set the accuracy floors on the EVIDENCE arm it modifies
   (0.325), with any higher bar (ADAPTED's 0.330) stated as a
   deliberate design choice scored INCONCLUSIVE by design, and
   rewrite the outcome bands with one floor term (the draft's
   bands used "floor" for both 0.325 and 0.330, leaving 0.320
   arguable into either word).
5. Specify the relevance call exactly (option orders averaged in
   logit space, temperature, the audited scoring path) and extend
   the configuration diff to cover it, not only the verdict call.
   Rank cap survivors by P(relevant), not by assembled order.
6. Report covered items by gold class before judging, including
   how many of the 65 miscaptioned items are among the 89
   covered (the recall ceiling the filter can reach), restate
   success as recall on covered miscaptioned items as well as on
   all 65, and register that if more than half of covered items
   are relevance-emptied, the outcome is an evidence-removal
   result and no success form can be claimed.
7. Carry a measured budget: a 20-item timing run first, the true
   call count (up to 445 relevance calls plus verdict calls on
   changed items only) priced from it, pod setup counted, all
   inside the shared allocation. A budget-stopped run reports
   ABORTED with counts only and no accuracy, F1, or recall
   figures; the draft's partial-scope clause is deleted.
8. Say "the retrained, verified checkpoint of record section
   5.4," never "identical checkpoint": equivalence was proven by
   200 of 200 label agreement on the verdict question only, and
   relevance probabilities are a first read on this checkpoint
   with no original-checkpoint comparator.

Concessions recorded: one asserted threshold cannot separate
mechanism failure from threshold failure (a train-side fitted
threshold, registered before judging, is the alternative the
re-registration must choose between, in writing); and the venue
limit stands in the board's words: this pilot can add at most
one carve-scoped mechanism sentence to the paper, and it cannot
support a NewsCLIPpings follow-up claim on its own.

## What would change the paper's claims, and what changes nothing

- If either success form is met: the paper's VERITE evidence read
  gains a registered exception. The sentence "the evidence arm
  recovers out-of-context items at the cost of never calling
  miscaptioned" stops being the whole story, and EvidenceGate gains
  a mechanism with a number, not only nulls. A NewsCLIPpings
  follow-up PRD becomes the next avenue.
- If it fails: miscaptioned blindness is shown to survive relevance
  filtering too, at the one registered operating point. The null
  deepens, the RED-DOT transfer route is closed for a model of
  this size, and that closure is itself a reportable result.
- What does not change either way: H3 (the v1 full-set VERITE
  verdict), the four-arm track's registered reads, and the
  Amendment 14 full-set table. This pilot is a mechanism test on
  the frozen carve, not a re-run of any registered verdict.
