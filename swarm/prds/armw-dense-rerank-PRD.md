# PRD: Lexical-then-dense rerank on the frozen Wikipedia corpus (Arm W)

Slug: armw-dense-rerank. Registered 2026-11-24. Status: DRAFT,
KILLED by the board 2026-11-24, all three critics (see Board
pass). This PRD does not run and is not patched; a rewrite is a
new draft. The body below is the killed draft, kept unmodified. Avenue: research-brain avenues row "Dense
rerank stage on the frozen Wikipedia corpus (Arm W)"
(NewsCLIPpings). Pattern source: Rashid and Hakak, Fathom, FEVER
Workshop 2025, as settled in LIT_REVIEW_2026-11-24.md (lightweight
open models, BM25 retrieval, then dense reranking). No experiment
runs under this PRD until the owner approves the run itself.

## Hypothesis

Arm W failed on ordering, not coverage (coverage was 100 percent,
gain zero); the reranked read gains with its interval clearing
zero under the registered rule.

## The exact question

Arm W pooled each item's frozen-query hits in query order, deduped
by title, and capped at five passages. If the same frozen corpus is
searched with a wider pool and the pool is then reranked (lexical
first, dense second) before the same five-passage cap, does the
Wiki-trained model's evidence read on the frozen 300 probe items
beat its pair-only read under the registered gain rule, where the
unranked pooling did not?

## Baselines, quoted from the record

Arm W (record section 5.3), all on the frozen 300 probe items,
Wiki-trained checkpoint:
- Coverage: 700 of 700 carve items and 300 of 300 probe items.
  Coverage is retrieval reach, not relevance; the live-web arm's
  headline coverage was 64.3 percent by contrast.
- Fitted accounting: pair-only headline 0.4933, evidence headline
  0.4433, paired delta −0.0500, interval [−0.1167, +0.0200].
  Evidence including-uncertain 0.5567 against pair-only 0.5233;
  evidence uncertain 63, decided fraction 0.7900; evidence
  falsified accuracy 0.5541 (82 of 148); pair-only falsified
  accuracy 0.9122 (135 of 148). The fitted operating point:
  temperatures 5.02 and 5.02, thresholds 0.5849 pair-only and
  0.2981 evidence.
- Plain 0.5 thresholds, same predictions: pair-only 0.4867,
  evidence 0.5133, delta +0.0267, interval [−0.0500, +0.1067];
  falsified accuracy 0.9189 and 0.5203. The two threshold views
  disagree in sign and both intervals cross zero: no reliable
  headline effect.
- The corpus: the English Wikipedia abstracts dump as captured on
  2024-04-20, SHA-256 9225a754...f4201, indexed as a SQLite FTS5
  table of 6,806,684 articles (record section 5.3). The corpus
  predates the study by about two and a half years by
  construction; that fact is part of the instrument and is stated
  wherever the arm is reported.
- The registered gain rule this hypothesis is read under: gain at
  temperature 1 and threshold 0.5 against the paired baseline,
  with a paired resampling interval (the corrected rule of the
  Amendment 11 addendum, applied throughout record sections 4.5
  and 5.2). A gain whose interval includes zero is not a gain.

## Split

- The frozen 300-item NewsCLIPpings probe (validation split, seed
  20261122, probe_items.jsonl), identical items to Stage A, Stage
  B, and Arm W. The probe is the study's one frozen eval set;
  stages may differ in their instrument, never in eval items.
- The judging checkpoint is the Arm W trained checkpoint (500
  train items, both question forms, base checkpoint, full arm,
  soft_ce, vision frozen, 245 steps), verified present in step 0.
- No new items, no fresh web retrieval, no corpus update. The
  corpus is the frozen FTS5 index above, hash-checked at load.
- HARD RULE: the MMFakeBench test set is closed and untouched by
  this PRD. NewsCLIPpings test stays untouched, as in v1 and v2;
  validation is the reported eval.

## The registered instrument (frozen here)

- Candidate pool: each item's frozen query list (the same queries
  Arm W used) searched against the FTS5 index; hits pooled across
  queries, deduped by title, widened to the top 20 per item before
  reranking (Arm W's effective pool was the unranked first 5).
- Rerank stage 1, lexical: FTS5 rank (BM25) order over the pool.
- Rerank stage 2, dense: one dense encoder, named in the run log
  before any judging, chosen once by this rule: the encoder
  already present in the study's environment if one is recorded
  there, otherwise a single named public encoder recorded in the
  log. No alternates are tried. Passages are scored by cosine
  similarity to the item's caption; the stage-1 order breaks ties.
- Final block: top 5 passages after reranking, formatted exactly
  as Arm W's evidence blocks were formatted, same token budget
  (1024, passages drop whole from the bottom).
- HyDE-style query expansion: DROPPED, registered as a choice.
  Reason: the frozen-corpus design exists so the test stays
  reproducible from the corpus alone; generated expansions would
  add a model in the query loop. The Fathom pattern is adopted
  minus that one element, and the subtraction is stated here, not
  discovered later.
- Scope note, registered: widening the pool is part of the rerank
  stage as adopted. The claim this PRD can support is about the
  rerank stage as a whole (wider pool plus rerank), not about
  ordering in the abstract.

## Protocol, in order

0. Verify the corpus hash and the Arm W checkpoint's presence;
   verify the frozen query lists are the ones Arm W used. Any
   failure stops the run and is reported.
1. Build the widened pools and rerank them per the instrument
   above. Log per item: pool size, passages kept, and how many of
   Arm W's original 5 survive the rerank (the overlap is reported,
   so a null cannot hide behind an unchanged block).
2. Judge the evidence arm on the 300 probe items with the
   reranked blocks, through the audited verdict path, thresholds
   passed explicitly. The pair-only read is Arm W's stored read;
   it is not re-judged.
3. Score both accountings: plain 0.5 thresholds as PRIMARY (the
   hypothesis is stated under the registered gain rule), and Arm
   W's fitted accounting second, beside the original Arm W reads.
   Report headline accuracy, accuracy including uncertain,
   uncertain count, decided fraction, and per-arm falsified
   accuracy for every read, per the study's abstention-accounting
   discipline: a win carried only by a moved decided fraction is
   named as such, not reported as an accuracy gain.
4. Paired delta (reranked evidence minus pair-only) with a paired
   resampling interval, 10,000 resamples, seed 20261122.
5. Write the result into research-brain with read-back; commit
   outputs under swarm/ in the repo.

## Success and failure criteria (registered numbers)

- SUCCESS: the reranked paired delta at plain thresholds is
  positive AND its interval lies entirely above zero AND the
  reranked evidence falsified accuracy is no more than 5 points
  below Arm W's original evidence read at plain thresholds
  (0.5203, so the floor is 0.4703) AND the win survives the
  abstention check in step 3 (including-uncertain accuracy also
  ahead of pair-only's 0.5233 fitted read's plain counterpart as
  reported in the run; if the headline and the including-uncertain
  reads disagree in sign, the verdict is the abstention verdict,
  not success).
- FAILURE: the interval includes or crosses zero, OR the point
  delta is at or below +0.0267 (no improvement over the unranked
  pooling it replaces), OR falsified accuracy falls below the
  0.4703 floor.
- The fitted-accounting read is reported in full either way; if
  it contradicts the plain read in sign, both signs are printed
  and the contradiction is named, as the record does for Arm W
  itself. It does not override the primary verdict.

## Budget and stop rule

$0.90 to $1.80, against the swarm's $3.00 cumulative cap
(cumulative spend is $0 today). Retrieval and reranking against
the local index are CPU work on free rungs; the spend, if any, is
the 300-item judging pass. Stop rules: this PRD stops at $1.80 of
its own spend, or the moment cumulative swarm spend reaches
$3.00, whichever comes first. Any pod started is terminated in
the same run.

## Resource

Ladder order: this VM and the owner's Mac mini first (index work,
reranking, and judging if MPS carries it), then Colab free GPU,
then Hugging Face PRO ZeroGPU, RunPod last and only inside the
budget above.

## Board pass

KILLED, 2026-11-24, by all three critics (protocol and
statistics; cost, registration, and internal fit; novelty and
venue fit). The avenue stays proposed, not shortlisted. The kill
reasons, in the board's substance:

1. The design cannot answer its own headline question. The
   hypothesis attributes the Arm W null to ordering, but the
   instrument changes two variables at once (pool widened from
   the unranked first 5 to the top 20, plus reranking), so a
   success is equally consistent with a relevant-coverage effect
   the hypothesis claims to exclude. The scope note conceded
   this in small print while the hypothesis and the paper-change
   text claimed the stronger thing. The separating control arm
   (widened pool, stage-1 lexical order only, no dense rerank)
   adds a second judging programme and breaks the budget.
2. The central instrument is unnamed at registration. The dense
   encoder was deferred to a run-log choice under a two-branch
   rule; the board cannot evaluate, and no reader can reproduce,
   a reranker chosen after registration.
3. A success criterion cites a number that does not exist. The
   abstention guard requires beating "pair-only's 0.5233 fitted
   read's plain counterpart as reported in the run"; 0.5233 is
   the fitted including-uncertain figure and its plain
   counterpart is nowhere in the record. The guard against an
   abstention-driven win, the exact failure mode of Stage B,
   was therefore unenforceable as written.
4. The primary accounting was switched under a mismatched
   citation. Arm W's registered accounting was its fitted
   accounting (original delta −0.0500); this draft made plain
   thresholds primary (original delta +0.0267) and called that
   switch "the registered gain rule" on the authority of record
   sections 4.5 and 5.2, which govern wording screens, not the
   Arm W evidence read. The choice flips the baseline's sign and
   must be owned in writing, not borrowed.
5. Borrowed novelty. With HyDE dropped, what remains is generic
   lexical-then-dense reranking; citing it as the Fathom pattern
   supplies novelty the method no longer contains.
6. Secondary defects the rewrite must also close: stage-1 BM25
   scores are not comparable across the different queries whose
   hits are merged, so the merge rule must be specified exactly;
   reranking by caption similarity works against falsified items
   by design, and the draft's falsified floor (0.4703) was
   anchored to the already damaged original evidence read
   (0.5203) instead of to pair-only (0.9189 at plain thresholds);
   the pair-only comparator was a stored read from another
   session while the reranked arm would be judged fresh, mixing
   the record's documented re-judging noise (about 2 percent of
   labels) into one side of a paired delta whose target effect
   is +0.0267; step 0 verified checkpoint presence, not
   completeness, and quoted the corpus hash in truncated form;
   the rerank compute (300 captions, up to 6,000 pool passages,
   FTS5 over 6,806,684 articles) was unpriced; and no power
   statement accompanied the interval-above-zero requirement
   (the design can only certify gains of roughly 0.08 or larger,
   so a FAILURE verdict would have meant no large gain, not no
   gain).

Rewrite spec, for a new draft if the owner wants one: a named
encoder with its full checkpoint string in the PRD; the plain
pair-only including-uncertain number computed from the stored
Arm W predictions and printed in the text before registration;
one accounting choice, owned in writing with its reason; claims
limited to the combined stage (wider pool plus rerank) unless
the lexical-only control arm is included, with the budget
re-derived for both arms and the run order across PRDs restated
against the $3.00 cap; the pair-only arm re-judged in the same
session, or the asymmetry recorded as a stated limit with the
unchanged-block count printed beside the delta; a falsified
floor anchored to pair-only; the merge rule specified; step 0
extended to a safetensors header completeness check and the
full corpus hash; a timing run pricing the rerank stage; and a
power sentence. Concession that survives any rewrite, in the
board's words: a success here is an exploratory instrument
result on a multiply reused probe, and no section 7 claim is
revised until a confirmation read on untouched items exists.

## What would change the paper's claims, and what changes nothing

- If success: record section 5.3's verdict is revised for the
  reranked instrument. The Arm W null becomes an ordering null
  (the unranked pooling buried the usable passages), and the
  evidence programme gains its first registered positive read on
  NewsCLIPpings, scoped to the frozen-corpus rerank stage as
  registered here.
- If failure: the Arm W null hardens. Coverage was already total
  and ordering is now excluded too, which leaves the relevance
  and quality of encyclopedia abstracts as the standing
  explanation, and closes the frozen-corpus route at this model
  size.
- What does not change either way: the live-web Stage A and Stage
  B reads, the scale probe, and every registered verdict in the
  record. This PRD tests one instrument change on one frozen eval
  set; it re-judges nothing else.
