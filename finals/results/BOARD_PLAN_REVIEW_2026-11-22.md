# Board Plan Review — the forward plan (steps A–J) viewed and verified
Reviewer board: chair · ML experimentalist · statistician · reproducibility engineer.
Convened 2026-11-22 (late evening) at the owner's instruction: "view and verify
plan with board." Sources read in full before judging: PAPERORCHESTRA_FINAL_
PASS_REQUIREMENTS.md, RESEARCH_BOOK_SPEC.md, BOARD_VERDICT_2026-11-22.md,
CALIBRATION_FINDING_2026-11-22.md, mainrun_log.md (tail, incl. the PASS 2
restart entry, the NCP temperature entries, and the board-amendment entry),
plus the Situation Log / Issues Review entries carrying the two small
promises (changes #25 and #27; issues #24 and #25).

Verdict scale: SOUND (execute as written) / AMEND (execute with the stated
change) / GAP (something owed is missing).

---

## Per-item verdicts

### A. PASS 2 parallel restart — SOUND
The log confirms the plan's facts exactly: serial driver stopped cleanly
20:41 ET, partial preserved untouched at
`trained_newsclippings_val_v1_serial_partial/` with exactly 709 scored rows,
rows never mixed across engines, same verifier semantics / checkpoint
(`runs/ncp_full_soft_ce_245`) / pack questions / temperatures / row schema —
only execution concurrency changes. The H2 verdict discipline is the one
this board fixed in its earlier verdict (binary against the registered
criterion: band 0.55–0.65 AND ≥ +6.24 pp over October's 0.5083, run baseline
0.5141 shown beside it, no interim accuracy from a source-blocked stream).
One wording note, not a defect: the plan paraphrases the equivalence gate as
"labels identical"; the gate as logged is stricter — labels identical on
every shared id AND probabilities within float tolerance, else abort and
resume serial. The logged version governs; the plan should quote it in full
wherever it is restated, because a paraphrased gate is how gates get
half-run.

### B. Four free analyses — SOUND
Error gallery, option-order robustness, noul AUC/disagreement, cost table —
all computed from stored artifacts, no new training, no GPU risk beyond the
option-order tune re-score, which correctly sits before pod termination
(step F). Correctly ordered before the bundle (step C), which must contain
them (final-pass requirements list the four closing analyses as bundle
inputs).

### C. Verdict cell + final_results_bundle.json — AMEND (two changes)
1. **The deviations enumeration must be the full checklist, not a sample.**
   The plan's parenthetical lists four items (calibration qualification, F2
   inert tag, manifest erratum, engine change). This board's earlier verdict
   (Q4, item 3) fixed the complete list: amendments (b), (c), (d); the F1
   native-form fix; the F2 inert tag (with its required wording); the
   manifest erratum line; the VERITE two-layer defect and its fix protocol;
   the calibration qualification — and now the PASS 2 engine change with its
   comparability note. The plan's "incl." makes its list formally
   non-exhaustive, but this run's documented failure mode is precisely a
   bundle that silently drops an item. Step C must carry the full list
   verbatim as a checklist and check each item off against the log.
2. **Ordering vs step D** — see the ordering section: the bundle's
   calibration section is the recording surface for the temperature-gate
   outcome, so the bundle cannot be final until D has run. Either run D
   before C, or split C into verdict assembly (before D) and bundle
   finalisation (after D, before E). The board prefers D before C: the gate
   is a pure computation on the completed PASS 2 file, nothing in the
   H1–H5 verdicts depends on it, and a single-pass bundle assembly removes
   the addendum dependency entirely.

### D. NCP temperature gate — SOUND (and move it before C)
The gate as planned is exactly the mechanical, pre-committed version this
board mandated: raw vs tempered choice ECE on the completed 7,024-row PASS 2
file (asserting the completed file first), temperatures ship only if
ECE_with_T ≤ ECE_raw, both values and the decision recorded in the bundle.
The log shows the gate already encoded this way, including the correction of
the earlier "no NCP temperature was fitted" note — the pack temperatures
[3.857, 2.100, 3.053] exist, are argmax-invariant for H2, and are governed
solely by this gate for publication. No change to the gate itself; only its
position in the sequence (before C, per above).

### E. Publish — SOUND, with two dependency notes
Standing duties are all present: both HF repos, Space v2, results.json
sourced from the bundle (never hand-entered), per-dataset examples,
per-pack smoke checks, Drive sync with read-back receipts (the v48 receipt
pattern: timestamp, size-exact read-back). Notes: (1) results.json must be
generated from the FINALISED bundle — i.e. after D and after C's
finalisation — so the NCP temperature decision and the MMF T=1.0 rule both
land in it mechanically; the plan should state this dependency rather than
leave it implicit. (2) The Drive sync receipt must cover the MERGED executed
notebook, including the pending transplant of kernel B's cells 17/26 outputs
noted in the log; a sync of the pre-transplant file would receipt the wrong
object — the exact failure class this run keeps catching.

### F. Artifact pull + termination — SOUND
Pull with count verification, pod TERMINATED (not stopped), final balance
read — matches this board's standing instruction that termination follows
the verified pull immediately and is the one step that must not be deferred
overnight (the pod bills until terminated; balance $15.16 at last read,
burn $0.897/hr, no spend concern).

### G. Final report + cost/operations ledger — SOUND, one addition
Scope is right: all 29 trainings (12 grid + 15 supplementary + 2 NCP) with
wall time / GPU memory / cost, per-stage durations, money ledger reconciled
against receipts and the final balance from F — correctly ordered after F,
since G consumes F's balance read. Addition: the ledger must carry the
PASS 2 restart honestly as stage lines — the serial segment (709 rows, its
wall time) and the parallel segment as separate lines — or the stage
durations will not reconcile with the pod's billed hours. (Rate note for
the ledger: use the $0.90/hr total pod rate the plan states; the observed
burn of $0.897/hr is the same figure at console precision — reconcile, don't
mix.)

### H. Walkthrough slots + final git commit — SOUND
Correctly last in the run's own sequence: the walkthrough's pending slots
(test-once, calibration-with-qualification, verdict block, cost ledger, PASS
accounting) can only be filled from C and G outputs, and the final commit
carries the executed notebook + final results. No change.

### I. Final PaperOrchestra pass + Research Book — AMEND (split the step; govern the DeepSeek decision)
The step as written bundles four separable things and lets the largest one
hide inside an "OR" clause. Split it:

- **I-1. Pre-flight, with the mas.py pacing fix NAMED and VERIFIED.** The
  final-pass requirements already bind this ("Semantic Scholar pacing fixed
  — 1 req/sec across workers — before the literature stage runs"), and the
  record carries it as an open, owned promise (Situation Log change #25;
  Issues Review #24, STILL OPEN: the audit mission lost 3 of 4 S2 searches
  to 429s). The plan does not name it. Covered-by-reference is not enough —
  this project's recurring failure class is a step that lives only in a
  referenced document being silently skipped. Promote it to a line item
  with a verification method: the shared rate limiter present in mas.py /
  the literature path, read back in code, plus a bounded dry run showing no
  429s. Same treatment for the rest of the requirements' pre-flight
  (pdflatex compiles the template; Gemini headroom vs the $10 cap
  confirmed with a run tally; watchdog armed at launch, alert-only —
  run #1 died silently without one).
- **I-2. The backend decision gate (see the dedicated section below).**
- **I-3. The run + delivery gate**, unchanged from the requirements:
  seeded bibliography (MMFakeBench arXiv:2406.08772, VERITE arXiv:2304.14133,
  NewsCLIPpings + LAYA sourced live via Semantic Scholar and verified —
  never invented), verified benchmark table (the §4.6 regime mix-up cannot
  recur), real byline (Rafiul Haider, Pace University, Analytics Capstone
  Fall 2026 CRN 72369; Team 3 named), amendments (b)/(c)/(d) disclosed, the
  labelling duties (wording footnote, lr_lora, head-only ≠ linear probe,
  VERITE 1,001-local-of-1,000 phrasing), and PO-6: every number traced to
  the bundle, every citation claim-matched, verified BEFORE any PDF reaches
  the owner. The Research Book rides the same window, seats, and gate per
  its spec — its source record is assembled from F's pulled artifacts,
  nothing from memory; the plan's ordering (F before I) already guarantees
  this.

### J. Fusion + publication path — SOUND
Correctly conditional and off the close-out critical path: it consumes
teammates' prediction files that do not yet exist, and the arXiv → workshop
→ journal sequence consumes the delivered paper. No verdict discipline is
needed now beyond what the record already holds (shared prediction schema,
stacker fitted on tune, one scoring). No change.

### K. (NEW — GAP) RunPod connector doc update
The plan omits a small owed item entirely: Situation Log change #27 /
contradiction C8 (Issues Review #25) — the RunPod connector doc still
describes the community-pod deploy spec and a stale balance, while the
working route all run was secure pods + CONNECT-proxy SSH. Owner: main
agent. It blocks nothing, which is exactly why plans drop it; the record
owes it, and its facts (final route, termination, final balance) only
become final at step F. Add it as a housekeeping step immediately after F,
before institutional attention moves to the paper.

---

## Ordering risks (question 2) — one real inversion, the rest clean

The spine A → B → C/D → E → F → G → H → I → J is correct: nothing is
published before the gate that validates it (E after D), nothing is
terminated before the pull that preserves it (F after E's sync), the ledger
(G) reads the final balance (F), the walkthrough (H) reads the verdicts and
ledger (C, G), and the writing (I) reads the complete pulled record (F).

**The one inversion is C before D.** The bundle's calibration section must
record the temperature gate's two ECEs and its decision (board amendment,
already in the log); a bundle assembled at C cannot contain the outcome of
a gate that runs at D without an addendum pass. The run has survived on
record-addendum cells all evening, but a plan should not schedule a known
addendum as its primary mechanism. Fix per step C/D above: D before C, or
C split into assembly/finalisation with finalisation explicitly after D
and before E. With that single change, every consumer in the plan reads a
validated, finalised input.

A second, softer ordering note: step B's option-order analysis re-scores
the winner on tune and therefore needs the pod alive; it is correctly
placed long before F. And step A's equivalence gate correctly precedes the
full pass it validates — the plan's strongest ordering feature, learned
from the VERITE reuse-cache defect the same evening.

## The DeepSeek decision point (question 3) — the board flags a verification-independence problem

**What the record actually authorises today.** The binding seat map
(Rafiul, 2026-11-22 19:29–19:30 ET, in the final-pass requirements) is a
HYBRID: PaperOrchestra orchestrates on Gemini; deepseek-v4-pro writes the
prose; gemini-4-neon coordinates, reflects, and VERIFIES; deepseek-flash
grinds. The same document permits in-tool writer routing "at pre-flight
ONLY if it smoke-tests clean; otherwise the hybrid is the default — the
final run is never put at risk for it." That authorises, at most, routing
the WRITER seat through the OpenAI-compatible backend. It does not
authorise an all-DeepSeek run: the plan's step I "OR" clause silently
extends a writer-routing permission into the replacement of the
coordinator/verifier seat. That extension is a new decision, not an
execution detail.

**Why the board flags it.** The entire evidentiary architecture of this
project is independence of the checker from the producer: the parent audit
caught the VERITE defect and the calibration failure precisely because the
checker had not produced the numbers; this board verified the calibration
finding by recomputation, not by asking its author; the swarms read raw
artifacts, not summaries. An all-DeepSeek pipeline closes that loop —
v4-pro writes, v4-pro-class reflection critiques it, and a DeepSeek seat
"verifies" numbers and citations in text its own family generated. PO-6's
gate ("verified BEFORE Rafiul sees a PDF") would still exist in form and
be weaker in fact. The failure it invites is not hypothetical in kind: it
is the baseline draft's failure (a 2/10 internal score, a §4.6 regime
mix-up, an incomplete bibliography) arriving with a verifier that has no
independent purchase on the text.

**Ruling.**
1. **Generation may move; verification may not close.** If the smoke test
   passes, in-tool routing of the writer (and grunt) seats to DeepSeek is
   approved under the existing requirements. The verification seat must
   remain independent of the writing seat: Neon as configured, OR the
   independent verification protocol used tonight (number-tracing to the
   bundle + citation spot-checks executed by a non-DeepSeek seat — parent
   / board — before delivery). An all-DeepSeek run in which DeepSeek also
   performs the PO-6 verification is NOT approved by this board; if the
   owner elects it anyway, this objection and the compensating gate he
   names must both be recorded in the run log before launch.
2. **Who decides: the owner, Rafiul — explicitly, in advance, on the
   evidence pack.** The seat map is his instruction; only he can amend it.
   The board's role is to fix what evidence the decision requires and to
   record the independence consequence. The decision must not be taken by
   default at pre-flight ("the smoke test passed, so we just ran it") —
   that drift is the precise mechanism the pre-flight gate exists to
   prevent.
3. **Evidence the smoke test must produce** (per stage, on realistic
   payloads — a hello-world chat proves nothing):
   - **Call-shape coverage:** every agent's call exercised through
     `utils/openai_utils.py` / `llm_backend_utils.py` against DeepSeek —
     outline, literature, section writing, refinement (the plotting agent
     stays off, as in both prior runs, and the test says so explicitly).
     The inspection already established the favourable fact: all agents
     funnel through `utils/gemini_utils.py`, with the live SDK calls at
     exactly two sites — the routing surface is small and auditable.
   - **Parser fidelity:** the pipeline's output parsers (e.g.
     `parse_gemini_latex_results`) are named for Gemini's output habits.
     The smoke test must show DeepSeek's outputs passing the SAME parsers
     on realistic stage payloads — schema-valid JSON/LaTeX per stage, no
     silent truncation or fallback — not merely that text comes back.
   - **Context behaviour at real size:** the largest payload class the
     pass will actually send (refinement over a full draft + the seeded
     bundle) run end-to-end, with token counts and latency recorded;
     DeepSeek's context and the pipeline's assumptions must be shown to
     meet on the real bundle, not a summary of it.
   - **A quality probe:** one real section generated via the candidate
     route and, for comparison, via the authorised hybrid, both checked
     by the independent verifier seat against the bundle (numbers traced,
     citations matched). The owner decides with that comparison in hand.
   - **Failure behaviour:** rate-limit / error handling and pipeline state
     on a forced backend failure — run #1 died silently on its backend;
     the watchdog (alert-only) must be shown to watch the DeepSeek route
     too, and a mid-stage failure must leave a resumable, inspectable
     state.
   - **Spend readout:** DeepSeek spend for the probe reported alongside
     the (near-zero) Gemini spend, per the requirements' rule that
     DeepSeek spend is reported at delivery — the cost rationale for the
     swap must be a measured figure, not the memory of run #2's Gemini
     bill (which the record attributes to the pro-preview pipeline run,
     a different configuration from the final pass's hybrid in any case).

## Completeness (question 1) — what the record owes that the plan omits

- **mas.py Semantic Scholar pacing fix** — owed (change #25; Issues Review
  #24 STILL OPEN; binding pre-flight item in the final-pass requirements).
  The plan omits it by name. Disposition: AMEND step I per I-1 above —
  named, verified, gated before the literature stage. Not a separate step;
  it has a natural home and a hard deadline (before literature runs).
- **RunPod connector doc update** — owed (change #27 / C8). The plan omits
  it entirely. Disposition: GAP → new step K after F (see above).
- Everything else the board could find in the record is present: the
  deviations completeness (as amended in C), the temperature gate (D), the
  Drive-sync receipts (E), termination discipline (F), the ledger's line-by
  -line verification (G), the walkthrough and repo commit (H), the seeded
  bibliography / benchmark table / byline / labelling duties (inside I via
  the requirements — the plan should cite them as I-3 checklist items so
  they are executed, not merely incorporated by reference), and the book
  (inside I, same gate).

## Steps to drop, split, or add (question 4)
- **Drop:** none. Every step A–J is owed to the record or the owner.
- **Split:** step I → I-1 (pre-flight, pacing fix named+verified), I-2
  (backend decision gate: smoke-test evidence pack + recorded owner
  election), I-3 (run + delivery gate). Step C → optionally split
  (assembly / finalisation) if D is not moved before it.
- **Add:** step K (connector doc update, after F). Add the ledger's
  PASS 2 two-segment stage lines (inside G). Add the explicit
  "results.json generated from the finalised bundle" dependency (inside E).

## Overall verdict (question 5) — FIT TO EXECUTE, AS AMENDED

The plan's spine is complete and correctly ordered; its verdict discipline
(H2 binary, temperature gate mechanical, bundle as single source, publish
only from the finalised bundle, termination immediately after the verified
pull) faithfully carries everything the swarms and this board established
tonight. Six amendments, none requiring new science:

1. Run D before C (or finalise the bundle after D, before E).
2. Step C carries the complete deviations checklist verbatim (board Q4
   list + the engine change), checked off item by item.
3. Step I-1 names and verifies the mas.py pacing fix before literature.
4. Step I's DeepSeek clause narrowed to what the record authorises:
   smoke-tested writer/grunt routing; the verifier seat stays independent
   — removing it is a separate, recorded owner decision, against this
   board's flagged objection, with a named compensating gate.
5. Step K added: RunPod connector doc updated after termination.
6. Ledger (G) carries the PASS 2 serial + parallel segments as separate
   stage lines so durations reconcile with billed hours.

With those adopted, the board approves the plan for execution as written.
The research itself is one in-flight pass from a complete record; this
plan, amended, is a close-out worthy of the run that produced it.
