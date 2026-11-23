# Board Situation Update — after the PASS 2 restart, deadlock, and profile
Reviewer board: chair · ML experimentalist · statistician · reproducibility engineer.
Convened 2026-11-22 (late evening) at the owner's request for an updated
assessment of the current situation. Sources read in full before judging:
BOARD_VERDICT_2026-11-22.md (this board's standing verdict),
BOARD_PLAN_REVIEW_2026-11-22.md, and mainrun_log.md from "PASS 2 RESTART"
onward (restart decision, board close-out amendments compliance plan,
deadlock + fix, gate result, live profile). Facts taken as measured per the
parent's brief and the log; the board invented no numbers.

Verdict scale: SOUND / AMEND / CONCERN.

---

## Q1 — Does anything since the verdict change the research's standing or any hypothesis's status? SOUND — no change.

Nothing since the standing verdict touches a decided hypothesis, and the one
open hypothesis is procedurally unaffected:

- **H1 (CONFIRMED), H3 (NOT MET), H4 (PASSED), H5 (PASS-as-registered with
  the calibration qualification)** all rest on artifacts completed before the
  restart. The restart changed how one in-flight measurement executes; it
  re-opened nothing.
- **H2 remains undecided, and the engine change does not contaminate it.**
  The log enumerates what did not change: same `visualnews_stream` verifier
  semantics (full PIL decode, integrity-only skips, skip ledger + per-source
  accounting), same checkpoint (`runs/ncp_full_soft_ce_245`), same pack
  questions and temperatures as the serial runtime manifest, same row
  schema. Only execution concurrency changed. The temperatures' argmax
  invariance — already established in the standing verdict (Q3) — is
  untouched.
- **The equivalence gate came back stronger than the standard this board
  set for it.** The pre-committed gate required labels identical on every
  shared id AND probabilities within float tolerance. The recorded result:
  120 shared ok items re-scored, **label mismatches = 0, max probability
  difference = 0.000000 — bitwise identical to the serial rows** — with gate
  accounting clean (108 members referenced → seen → verified, 0 skipped,
  0 missing). The engine change therefore carries a bitwise-equivalence
  receipt, not a tolerance argument. If anything, the record is stronger
  than when the standing verdict was written.
- **One coverage note, for the bundle (see Q2):** the gate's 120 shared
  items are necessarily drawn from the head of the stream the serial pass
  had already scored — the stream is source-blocked, so the gate sample is
  the first-scored region, not a random draw from the 7,024. That is
  inherent to the pre-committed design and is not a defect; it should be
  stated in one line wherever the gate result is quoted, so no reader
  over-generalises the equivalence evidence.
- **PASS 1 comparability stands.** PASS 1 completed under the serial engine
  before the restart existed; the restart's comparability note (eval
  semantics identical across engines) is in the log, and the gate result
  now substantiates it empirically.

The board also records, with approval, that the profile section of the log
corrects the run's own earlier inference in writing: the serial pace had
been read as inference-bound (~2.5 s/row inferred from wall rate); the rows'
own seconds field (mean predict 0.16 s/item, vs PASS 1's 0.18 s) refutes
it. A record that refutes itself in the open is the standard this project
has set; the correction must be the version the cost table and the paper
use (see Q2, item 5).

## Q2 — Engine-change deviation + deadlock episode: is the documentation at the required standard? AMEND — the log is at standard; the bundle must inherit the whole episode, not its summary.

What the log already carries, and the board verifies as complete:
the restart as an attributed owner decision (Rafiul, 20:39 ET) with its
reason (wall-clock); the serial partial preserved untouched at exactly 709
rows in its own directory, rows never mixed across engines; the unchanged
measurement procedure enumerated item by item; the gate spec pre-committed
before the full pass; the gate result with its numbers; the deadlock's
symptom (parent telemetry + process tree: 4 inference workers defunct,
reader + decoders blocked on full queues), its root cause in the workers'
own traceback (CUDA re-initialisation in forked subprocesses), the fix
(spawn context via a real module, `data/workflows/parallel_stream_engine.py`,
plus a dead-worker guard that aborts loudly and terminates stragglers), and
the failed attempt's accounting (zero rows produced, scratch dir discarded).
The close-out compliance plan already folds the engine change into the
bundle's deviations checklist and splits the ledger into serial / parallel
stage lines. This is the standard the record requires — in the log.

The amendments concern inheritance. The failure mode this run keeps
catching is a downstream surface that silently drops or softens an item
the log holds. Before close-out, the board requires:

1. **The bundle's engine-change entry must contain the deadlock episode
   itself** — fork attempt, zero rows, root cause, spawn fix, dead-worker
   guard — not only the checklist's current shorthand "PASS 2 engine
   change + comparability note." A bundle entry reading "concurrency
   changed; gate passed" would be true and materially incomplete. The log
   already rules the failure + fix "part of the engine-change deviation
   entry"; the bundle must honour that ruling literally.
2. **The gate result is quoted with its coverage line** (Q1): 120 shared
   items from the serial-scored head of the stream, 0 mismatches, bitwise
   on probabilities, gate wall 278 s.
3. **Final accounting reconciliation:** the completed parallel pass's
   `stream_accounting.json` (rows written + skipped + missing against
   7,024, per-source) is checked against PASS 1's accounting format at
   close-out, and the preserved 709-row serial partial is explicitly
   accounted in the artifact pull — retained or excluded, the bundle says
   which and points to the log entry that explains it, so a future auditor
   meeting two files is not left to reconstruct the story.
4. **The ledger keeps the "measurement code untouched" attestation**
   attached to the post-gate `wall_seconds` patch (output bookkeeping
   only), as the compliance plan already states — the attestation must
   survive into the bundle alongside the two-segment stage lines
   (serial: 709 rows, ~00:52→01:41 UTC; parallel: wall + rows from its
   accounting).
5. **The cost table uses the profile's corrected attribution** —
   traversal-bound, inference mean 0.16 s/item — and the superseded
   inference-bound reading appears, if at all, only as a corrected
   inference in the book's mistakes account, never as a live claim.

## Q3 — The pass itself: let it grind, or intervene? SOUND — let it run. No intervention is justified on the evidence now available.

The profile answered the question the intervention debate was waiting on,
and the answer removes the case for intervening:

- **The constraint is identified and it is external.** The binding limit
  is the single sequential tar traversal at ~18–19 MiB/s — the Rice host's
  practical ceiling with 12 range workers — multiplied by the archive's
  reference-density profile. Every compute stage is starved, not slow:
  GPU util median 0%, under 1 of 16 cores busy across reader + decoders +
  inference workers combined, both queues effectively empty, per-item
  predict 0.16 s. Parallel decode did not beat serial materially because
  decoding was never the cost. This also retroactively explains the serial
  pass's pace — traversal + density + serialisation — with no defect
  anywhere in the chain.
- **Neither named lever addresses that constraint.** More range workers:
  uncertain gain against a possible per-IP/host cap, and applying it means
  stopping the pass, re-running the gate, and adding a second engine
  variant to the deviation surface — to attack a ceiling that may not
  move. Dual segmented readers: a new engine variant requiring full
  re-verification, and two readers still share the same host pipe the
  12 range workers already saturate. Both levers spend the record's
  cleanliness to buy, at best, an unproven fraction of a bandwidth-bound
  wall.
- **The pessimistic ETA should not drive a decision.** The flat-rate
  extrapolation (~22 rows/min → 02:15–04:30 ET) assumes the early rate is
  the rate. The profile documents why it is not: the archive's head is
  sparse BBC material, and guardian — 47% of all references — comes later;
  rows arrive per referenced image while cost accrues per byte traversed,
  so rows/min rises as density rises. The profile's density-aware
  projection is a total wall of ~90–110 min, about PASS 1's traversal of
  the same archive — PASS 1 being the empirical anchor: the same ceiling,
  the same archive, already traversed once tonight. The board does not
  adjudicate between the two estimates; it notes they differ because one
  models the archive and the other doesn't, and that the realized rate in
  the guardian region — observable as the pass proceeds — will settle
  which is right long before either finish time arrives.
- **Money does not argue for intervention.** Balance ~$14.5 at $0.897/hr
  covers even the pessimistic finish several times over; the standing
  verdict's spend instruction (CONTINUE; terminate immediately after the
  verified pull) is unchanged.

**Evidence that would change this answer:** (i) the realized rate failing
to rise as the traversal enters the guardian-dense region — the density
model falsified by measurement, pushing the finish to the flat-rate ETA's
far end with hours of pure traversal still ahead; (ii) a lever demonstrated
against the actual constraint on a scratch segment — e.g. a range-worker
increase sustaining rx materially above ~19 MiB/s — rather than asserted;
(iii) any integrity anomaly in the parallel output (skip-ledger divergence
from PASS 1's pattern, provenance gaps, malformed or duplicate rows) —
that stops the pass regardless of speed, on the standing rules; (iv) a
hard external deadline entering the record — none exists tonight; the
owner's constraints are cost and attention, and neither binds.

## Q4 — Risks the later finish creates for the close-out chain: CONCERN — the chain is sound; the hour is the risk. Mitigations named.

The chain itself (temperature gate → bundle → publish → artifact pull →
termination → final report/ledger → paper pass + book) was re-ordered
correctly by the plan review and the compliance plan: gate before bundle
finalisation, results.json generated from the finalised bundle, publish
only from validated inputs, termination immediately after the verified
pull. A finish anywhere in the ~22:30–04:30 ET window does not break that
logic. It stresses the humans executing it:

1. **Termination deferral — the standing risk, now likelier.** The board
   has already ruled termination is the one step that must not be deferred
   overnight: the pod bills until terminated ($0.897/hr — affordable, but
   an unterminated pod is also an unclosed record: no final balance read,
   no reconciled ledger, no step F, and steps G/K and the paper window all
   queue behind it). A 03:00 finish makes "terminate in the morning" the
   path of least resistance. **Mitigation:** termination stays welded to
   the verified artifact pull as a single operation, executed whenever the
   pull completes, at whatever hour; the balance is read in the same
   operation. Nothing else in the chain has this property — everything
   downstream of F can safely wait for morning; F cannot.
2. **Read-back fatigue.** The steps a tired operator waves through are
   precisely the verification steps this run keeps proving necessary:
   count verification on the pull, per-pack smoke checks, the Drive sync
   receipt covering the *merged* executed notebook (including the pending
   transplant of kernel B's cells 17/26 outputs — a sync of the
   pre-transplant file receipts the wrong object, the plan review's named
   failure class). **Mitigation:** the checklist is executed as written,
   at whatever pace the hour dictates; no step is marked done from memory;
   where a step can be pre-staged during the pass's remaining wall
   (bundle patch, publish assets, Space examples, gate cell — already
   planned as a notebook cell after the PASS 2 cell), it is prepared now,
   in daylight hours, so the post-pass sequence is mechanical rather than
   inventive.
3. **Order compression at the gate.** The temperature gate is a pure
   computation on the completed file and nothing in H1–H5 depends on it —
   which is exactly why, at the end of a long night, it will tempt someone
   to run it "in parallel with" bundle assembly. The plan review closed
   that door (D before C, or finalisation after D); the compliance plan
   encodes it. **Mitigation:** none needed beyond holding the order — the
   board restates it here because the temptation is predictable.
4. **Downstream windows compress, but do not degrade.** The PaperOrchestra
   pass and the Research Book consume the pulled artifacts, not the pod;
   step K (connector doc) reads facts finalised at F. A late finish delays
   these; it cannot contaminate them — provided F itself is executed
   properly, which is why risks 1–2 carry the weight.

## Q5 — The researchers' update to the owner (one paragraph)

Tonight the research finished everything except one measurement: four of
the five registered hypotheses are decided on numbers that independent
audits have recomputed and confirmed — the headline result stands (the
fine-tune takes the model from 0.204 to 0.602 macro-F1 on the test set,
scored exactly once, with the gain's confidence interval nowhere near
zero) — and the one open question, whether the same recipe lifts
NewsCLIPpings, is being answered right now by a verified pass over all
7,024 validation items, roughly 600 rows in and integrity-clean; the pass
was restarted tonight under a parallel engine at your decision, its first
attempt deadlocked and was root-caused and fixed in the open, the fixed
engine proved itself bitwise-identical to the original on a 120-item gate
before being trusted with the full run, and the profiling since shows the
remaining wait is the archive host's bandwidth, not the science — when the
pass lands, its verdict is rendered binary against the criterion
registered before the arm was designed, and what remains after it is a
known, mechanical close-out: temperature gate, bundle, publish, pod
termination, and the paper written from the complete record.

## Bottom line

The standing verdict is unchanged in every particular. The restart was an
execution decision, honestly logged; its failure was found in the open,
fixed at the root, and sealed with a gate stronger than the one this board
required; the profile then showed the remaining wait is a bandwidth fact
about a 91 GB archive on someone else's host, not a problem in the work.
Let the pass run. Guard the two things the late hour actually threatens —
the bundle's inheritance of the full deviation record, and a termination
that happens when the pull completes rather than when the morning comes —
and the research closes the way it was run: on receipts.
