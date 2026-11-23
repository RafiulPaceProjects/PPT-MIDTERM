# Changelog — v2 retrieval experiment fork

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
