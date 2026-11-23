# Changelog — v2 retrieval experiment fork

## exp-v0.7 (2026-11-23)
- First probe RESULTS land (added verified information = minor bump, per
  VERSIONING.md; artifact paths + verification status named here as required):
  - VERITE full track, four arms on the identical held-out 200 items:
    BASE 0.285 / TRANSFER 0.320 / ADAPTED 0.330 / EVIDENCE 0.325 accuracy,
    per-class recalls, macro-F1 for the three non-evidence arms
    (0.2154 / 0.2855 / 0.3310). ADAPTED − TRANSFER +0.010, 95% CI
    [−0.080, +0.095] — registered success criterion NOT MET.
    EVIDENCE − BASE +0.040, 95% CI [−0.005, +0.090]. Standing
    comparability warning carried in the text (held-out carve of the
    local copy; NOT comparable to published full-set VERITE numbers).
    Source artifacts: `~/workspace/misinfo_run/v2_probe/verite_sidearm_results.json`
    (scored 2026-11-23, verified against its prediction files by the parent)
    and `~/workspace/misinfo_run/v2_probe/REPORT.md` (VERITE track section).
  - Retrieval instrument failure + repair summary: batch retrieval's
    silent empty pools, serial repair with per-pair checkpointing;
    probe 597/600 pairs non-empty, headline coverage 193/300 = 64.3%;
    VERITE 349/400 (EVIDENCE coverage 89/200 = 44.5%); Stage B carve
    694/700. Source artifact: probe `REPORT.md` (repair sections,
    2026-11-23), verified by the parent against the repaired snapshot
    files and assembly hashes recorded there.
  - "Registered next" note: NewsCLIPpings pilot / Stage A / Stage B
    pending on the pod phase; noul drill-down registered as
    Amendment 11 (baseline screen → top three → fine-tune → choose;
    design of record: `LAYA_STRUCTURE_AND_NOUL_DRILLDOWN.md` in the
    study record).
- Gate: PASS, 0 warnings, on this branch's draft. The branch allowlist
  gained sourced entries for every number above plus six pre-existing
  fork-draft numbers that had never traced on this branch
  (0.5104, 0.5002, 11, 30, 245, 500).

## exp-v0.1 (2026-11-22)
- Fork created from the main paper line at v0.0 (main @ fe02ba3).
- Seeded: fork rules (README.md), skeleton draft (draft/paper.tex) carrying ONLY
  v1-record numbers (H2: trained 0.5104 vs baseline 0.5141, NewsCLIPpings val n=7,024;
  source: final_results_bundle.json) and the probe design summary.
- No probe results exist yet; the Results section is intentionally empty and the
  gate discipline forbids filling it from anything but verified probe artifacts.

## exp-v0.2 (2026-11-22)
- Feature section added: "Search -> LAYA" (SearXNG evidence passed into LAYA's
  context; LAYA decides), with the attuned CHOICE and NOUL question wordings
  registered verbatim and the attuned scoring sheet (paired delta, evidence
  strata, contamination arms, arbitration, CAL-1 calibration rule, coverage).
- Still no probe results; Results remains empty by gate discipline.

## exp-v0.3 (2026-11-22)
- Method staging added per owner directive: Stage A baseline (existing checkpoint,
  zero-shot evidence judging) before Stage B small fine-tune; train carve from the
  official train split (500/100) with frozen evidence snapshots; tune-only
  selection; single evaluation on the probe items; test split untouched.
- Results still empty by gate discipline; verified probe results will land as a
  later exp version.

## exp-v0.4 (2026-11-22)
- Architecture added per owner directive: EvidenceGate, a pluggable state-machine
  component (Intake -> Route -> PairOnly|Retrieve -> Judge -> Arbitrate -> Done),
  per-pack routing policy (NewsCLIPpings evidence-on, MMFakeBench evidence-off)
  plus a per-item uncertainty trigger; detach = byte-identical to v1.
- Probe scoring extended: always-on vs uncertainty-triggered modes compared.

## exp-v0.5 (2026-11-22)
- Hardening subsection added from the adversarial board review: the three
  pre-Stage-A binding requirements (binding vs corroboration tagging,
  publication-date enforcement with leakage audit, verdict-neutral
  image-description diagnostic) summarised; full 11-item ranked list in the
  study record (BOARD_EVIDENCEGATE_HARDENING.md).

## exp-v0.6 (2026-11-22)
- Field-solutions survey summarised into the draft: cross-anchoring (CCN/SNIFFER)
  and its 2026 availability limits, AVeriTeC date discipline adopted, and the two
  no-published-equivalent fixes (binding tagging + decontamination ablation;
  cluster-counting flip policy) framed as candidate contributions.
