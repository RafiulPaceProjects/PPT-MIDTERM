# Board Verdict — swarm round 3 (NCP arm, PASS 2, VERITE) + H2 discipline
Reviewer board: chair · ML experimentalist · statistician · reproducibility engineer.
Convened 2026-11-22 (evening) on: swarm3_ncp_arm.md, swarm3_pass2_verite.md,
and this board's earlier BOARD_VERIFICATION_2026-11-22.md. All findings below
rest on the swarm's independent recomputations from pod artifacts; the board
re-derived nothing it had already verified and trusted nothing it had not.

## Q1 — Is the swarm's NCP verdict set sound? YES, in full.

**Step-spec resolution — SOUND, and the board commends the method.** The swarm
went to the primary source — the executed notebook's cell 28 — and found the
rule as written: `budgets = sorted({245, int(winner["steps"])})`, with the
[245, 490] fallback firing only if the MMF winner had itself been the 245-step
config. The winner ran 735 steps, so the executed budgets are {245, 735},
exactly the receipts on disk. Amendment (c) and the §7b/§7c markdown describe
"the winner's recipe at two step budgets" and never name {490, 735}; every
"490/735" string in the record refers to the MMFakeBench grid or the October
protocol. **Ruling: there is no missing run and no deviation. The {490, 735}
figure was an error in the parent's working notes, not in the registered
design.** The board notes this is the same failure class as the run's other
documentation findings — a belief about an object nobody re-read — and the
corrective is the one the swarm applied: the notebook is the record; notes
about the notebook are not.

**F2 inert-tag deviation — a deviations-list entry IS required.** The code fix
is real (parameterized `_examples()`, md5-identical VM/pod copies), but the
executed NCP cell never passed `dataset=`, so the NCP trainings ran under the
default "mmfakebench" tag. The swarm's impact analysis is correct and the
board adopts it: in `laya.vlm_train.jsonl_example` the argument is stored on
the example dict and never used in conversion; conversion is record-driven,
and the receipts corroborate correct NCP conversion (4,002 NCP records
consumed; native-form tune metrics on pristine/falsified). Classification:
**inert labelling blemish, zero data impact — but it goes on the bundle's
deviations list**, alongside the F1 form fix it travelled with. A run that
logs a checkpoint-blind cache and a wrong-checkpoint eval does not get to
omit a harmless tag; the list's credibility is its completeness.
**Wording the paper and book must avoid:** any claim that the NCP arm "passed
dataset='newsclippings'", that its examples were "converted/tagged as
NewsCLIPpings", or any phrasing implying the tag participated in conversion.
**Required wording, in substance:** "NCP training used the shared trainer with
its dataset-tag parameter unset (default 'mmfakebench'); the tag is stored on
examples but unused in conversion, which is record-driven; receipts confirm
the NCP records and native-form metrics were consumed correctly."

**Manifest 2000-vs-2001 — cosmetic, correctly classified.** The
`carve_targets_items.train` label reads 2000; the manifest's own `splits`
section and the files on disk agree at 2,001 items / 4,002 records. No data
impact, no deviation of substance. **Ruling: one-line erratum note in the
bundle/book** ("manifest target label reads 2000; actuals 2,001, per the
splits section and file counts") so a future auditor does not burn time
re-discovering it. Nothing else.

The board also records its agreement with the swarm's two quiet confirmations
that carry real weight: the metadata ban is clean across all 5,002 NCP rows
(key union exactly {id, image, label, question, state_text}), and the F1 fix
held — both receipts state `tune_metric_form: "native"`, n = 250, so the
flipped-label pooling failure did not occur.

## Q2 — H2 outlook discipline

**What the tune numbers actually say.** Winner tune accuracy 0.508 on n = 250
native-form records. The standard error at p ≈ 0.5, n = 250 is ≈ 0.032, so
the 95% interval is roughly [0.446, 0.570]: tune accuracy is statistically
indistinguishable from chance (0.50) — and, the board notes for symmetry,
also indistinguishable from the bottom of the H2 band. Tune can neither
convict nor acquit this arm; anyone quoting it in either direction is
over-reading noise. The same applies to the winner designation itself:
0.4930 vs 0.4809 macro-F1 is a 1.2-point margin at n = 250 — the 245-step
"winner" is a selection-rule output, not an established superiority, and the
paper must describe it as such. The per-class recalls (pristine 0.336 /
falsified 0.680) show the trained arm retains the base model's falsified lean
(PASS 1 baseline predicted 93% falsified); training moved the decision
boundary modestly, not decisively.

**What MAY be claimed when PASS 2 lands — only this:** the completed
7,024-row accuracy with its interval, rendered against the registered H2
criterion (band 0.55–0.65 AND ≥ +6.24 pp over the October baseline 0.5083,
i.e. effectively ≥ 0.5707), with the run's own baseline (0.5141, same model,
run wording) reported beside it so the wording delta stays visible. The
verdict is binary against the registered criterion; there is no "near miss"
tier.

**What may NOT be claimed, whatever the number:** (a) any interim accuracy —
the stream consumes the archive in source-blocked order, the partial file is
not a sample, and the swarm was right to refuse to compute one; (b) any
learning claim sourced from the tune split or the loss curves; (c) any
reframing of the criterion after the fact — the band and the +6.24 pp bar
were registered against the October baseline before the arm was designed,
and they do not move.

**If PASS 2 lands near the baseline — the honest framing.** The efficiency
claim is dead: "2,001 items buy most of full-data fine-tuning" required the
H2 band, and a null result cannot carry it in softened form ("directionally
positive", "competitive given the data scale" — all banned). What survives,
and it is not nothing:
1. **A clean, pre-registered negative.** The MMF winner's exact recipe,
   transplanted to NCP with ~4× the winner's own training items, produces
   no measurable gain. That bounds the paper's central claim honestly:
   objective > arm > budget was measured on MMFakeBench, and its
   generalisation is dataset-conditional. A claim with a measured boundary
   is stronger than an unbounded one.
2. **A coherent pattern across the transfer tests.** MMF: large gain.
   VERITE: flat (H3 not met, 0.3506). NCP trained arm: to be read beside
   them. The pattern — the recipe repairs a collapsed classifier where the
   signal is learnable at small scale; it does not manufacture signal
   where the base model lacks it — is a finding, and it is consistent with
   the published landscape (fine-tuned CLIP reaches 66.1% on NCP with the
   full 71k training split; data scale is the known lever on this task).
3. **The infrastructure result stands independent of the accuracy:** two
   complete, verified 7,024-row stream passes (PASS 1: 0 skips), a carve
   audited to the row, and a selection that provably used the native form.
H2 is then reported NOT MET with its number, in the same table as H1's
confirmation. Pre-registration discipline is the paper's credibility asset;
spending it to soften H2 would cost more than H2 is worth.

## Q3 — NCP pack temperatures [3.857, 2.100, 3.053]: ENDORSE the steer, with one amendment.

The steer — no temperature ships in results.json until it survives a
held-out validation — is endorsed without reservation. It is the direct,
correct generalisation of the MMF calibration finding this board verified
an hour earlier: the calib-fitted 8.4214 damaged held-out ECE 0.106 → 0.396,
and a temperature is a property of model × distribution. The NCP choice
temperature (3.857) was fitted on a 250-item calib split drawn from the
same dev-pool adjacency that produced the MMF failure; it is, if anything,
a stronger candidate for the same failure mode.

Two precisions the board adds:
- **The PASS 2 eval itself is not contaminated by the temperatures.** The
  swarm verified they are recorded in the runtime manifest and row
  provenance, and temperature scaling is argmax-invariant: H2's accuracy
  verdict is unaffected. The steer's target is correctly the published
  probabilities (results.json / the Space), not the eval. Nobody needs to
  re-run PASS 2 over this.
- **Amendment — make the validation mechanical and pre-committed, using
  PASS 2 itself.** The completed PASS 2 file is the ideal held-out set:
  7,024 val rows the NCP temperatures never saw, with stored probabilities.
  Before publish, compute val ECE raw vs val ECE with [3.857, 2.100, 3.053]
  applied (choice temperature at minimum; the board's MMF scope caveat —
  choice-only — applies unless the noul probabilities are also stored and
  checked). Ship the temperatures only if they do not degrade held-out
  ECE; otherwise the NCP pack ships T = 1.0, exactly as the MMF pack does.
  Record the two ECEs and the decision in the bundle. This converts the
  steer from a judgement call at publish time into a gate with a number —
  the same fail-closed pattern the rest of the run used.

## Q4 — How far is this research, verifiably? Spend: CONTINUE, no stop concern.

**Verifiably complete** (each item independently audited at least once):
the 12-config grid and winner selection (receipt-exact, argmax at full
precision); test-once, scored exactly once and permanently closed — H1
CONFIRMED (+0.3983 [0.3853, 0.4108]); the supplementary tier 15/15 in its
isolated receipt tree; calibration with its transfer qualification —
H5 PASS-as-registered, board-verified to the digit; the VERITE provenance
chain resolved through both defect layers — H3 NOT MET on a verified eval
(0.3506, 543/1,001 predictions differing from baseline, smoke-gated fix);
the NCP carve and arm (counts, metadata ban, native-form selection, winner
argmax — all exact). H4 PASSED on the winner's tune recalls. **In flight:
exactly one measurement** — PASS 2, integrity-clean at last audit (492 rows
parsed, 0 malformed, 0 duplicate ids, 0 ids outside the baseline set,
provenance naming the NCP winner).

**What stands between here and a defensible final record** — a short,
known list, none of it research any more:
1. PASS 2 completes at 7,024/7,024 and H2 is rendered per Q2's discipline.
2. The four free analyses (error gallery, option-order robustness, noul,
   cost table) — computed from stored artifacts, no new GPU risk.
3. The verdict cell and bundle carry the COMPLETE deviations list:
   amendments (b), (c), (d); the F1 form fix; the F2 inert tag (Q1
   wording); the manifest erratum line; the VERITE two-layer defect and
   its fix protocol; the calibration qualification. Every item is already
   in the run log; the failure mode to guard is a bundle that silently
   drops one.
4. The NCP temperature gate (Q3 amendment) executed and recorded before
   publish.
5. Publish per the standing duties (bundle-sourced results.json, per-pack
   smoke checks), artifact pull with count verification, and the Drive
   sync receipts at the remaining boundaries.
6. **Pod terminated — not stopped — and the final balance read into the
   ledger**, with the cost/operations ledger verified line by line
   against receipts before the final report.

**Spend.** Live balance $5.3899 at ~20:28 ET, burn $0.897/hr, implied total
spend ≈ $4.38 against the $8 hard stop — roughly $3.6 (≈ 4 pod-hours) of
headroom against remaining work measured in tens of minutes. The descope
ladder is moot: everything it would have cut is already done. **The board's
only spend instruction is about the end, not the middle: the pod bills
until terminated, so termination follows the verified artifact pull
immediately — it is the one step that must not be deferred overnight.**

## Bottom line

The swarm's round-3 verdicts are sound in every particular, including its
correction of the board's own audit premise on the step spec. Four of five
hypotheses are decided on verified numbers; the fifth waits on a single
in-flight pass whose integrity is confirmed and whose verdict discipline
is now fixed in advance. The research is, verifiably, one completed
stream pass and a disciplined close-out away from a complete record —
and the close-out list above, not any open scientific question, is what
remains.
