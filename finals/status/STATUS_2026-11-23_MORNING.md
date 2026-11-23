# Status — 2026-11-23 (morning, ET)

## v1 paper
- Main line is at **v0.2.0** (commit d1e2dbf, tag paper-v0.2.0): seven
  figures added (SARD companion chart, architecture, pipeline, grid
  heatmap, headline bars, ablations, Colab collage appendix) and the
  five baseline "n/a" cells filled from the saved prediction files
  (proof checks reproduce the published baseline accuracies exactly;
  record: `finals/results/BASELINE_DETAILS_2026-11-23.md`).

## v2 probe (EvidenceGate) — state this morning
- **VM-side work complete.** The batch-retrieval instrument failure
  (concurrent queries tripped a search-engine suspension; empty pools
  were silent) was diagnosed and repaired serially with per-pair
  checkpointing: NewsCLIPpings probe 597/600 (item, variant) pairs
  non-empty, headline coverage 193/300 = 64.3%; VERITE 349/400;
  Stage B carve 694/700. A10 re-retrieval audit: live search is not
  reproducible at a one-day lag (mean Jaccard 0.2161) — the frozen
  snapshots are the experiment. Full record:
  `finals/results/v2_probe_REPORT.md`.
- **VERITE track complete.** Four arms on the identical held-out 200:
  BASE 0.285 / TRANSFER 0.320 / EVIDENCE 0.325 / ADAPTED 0.330.
  ADAPTED − TRANSFER +0.010, 95% CI [−0.080, +0.095] — the registered
  success criterion is NOT MET. EVIDENCE − BASE +0.040, CI
  [−0.005, +0.090]; the evidence arm recalls zero miscaptioned items.
  Record: `finals/results/v2_probe_verite_sidearm_results.json`
  (comparability warning inside: held-out carve of the local copy,
  NOT comparable to published full-set VERITE numbers).
- **Pod phase running** on a fresh pod (after one SSH-approval block
  and one driver-dead GPU pod, both recorded in the probe report):
  pilot judging → Stage A → Stage B + Amendment-6 noul attunement →
  noul drill-down (Amendment 11: baseline screen of varied noul
  wordings, top three into fine-tuning, one winner per dataset;
  design: `finals/results/v2_probe_LAYA_STRUCTURE_AND_NOUL_DRILLDOWN.md`).
  Runbook: `finals/results/v2_probe_POD_PHASE_RUNBOOK.md`.
- **Fork paper:** exp-v0.7 on branch `exp/v2-retrieval` carries the
  VERITE results + repair record in its Results section
  (tag paper-exp-v2-0.7, gate PASS).

## Balances (as recorded in the probe REPORT.md)
- RunPod: $8.7291 after the unreachable replacement pod was
  terminated ($1.20 idle burn, zero output); the current pod phase
  draws against the remaining balance (~$8.73 at the report's
  writing, hard stop $5 for the phase).
- Retrieval repair flash spend: $0.35 (probe), $0.10 (VERITE resume
  segment), $0.05 (VERITE assembly).

## Copy note
The committed `v2_probe_REPORT.md` is the copy taken 2026-11-23
~16:08 UTC; its final section still describes the earlier SSH block.
The pod phase has since started and the VERITE EVIDENCE arm has been
scored (in the results JSON above); the report's stage sections for
pilot / Stage A / Stage B land with the pod phase's completion and
will be committed then.
