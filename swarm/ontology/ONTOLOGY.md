# LAYA Ontology: where the three datasets can be made better

Built 2026-11-24 from first principles, out of research-brain (findings,
avenues, lessons, sources) and LIT_REVIEW_2026-11-24.md. The graph as data
is graph.json beside this file. Edge types are only: causes, measured_by,
treats, blocked_by, killed_by, depends_on, shared_across.

## The layers, base to top

1. **Primitives (8).** What the system is made of: image-caption pair,
   choice question, noul screen question, evidence set, typed decision,
   arbitration rule, calibration stage, EvidenceGate routing.
2. **Internals (7).** The LAYA parts that can be changed: question pack
   wording, screen design, arbitration thresholds, routing trigger,
   training mix and loss masking, calibration fitting, retrieval and
   reranking.
3. **Failure modes (9).** Each carries its deciding number: pristine
   collapse (falsified caught 4 of 148), mirror collapse (falsified
   accuracy 0.9122), abstention artifact, screen-choice disagreement
   (274 of 300 uncertain), calibration transfer harm (ECE 0.1056 to
   0.3955), similarity confound (screen AUCs 0.55 to 0.59), evidence
   ordering failure (coverage 100 percent, gain zero), miscaptioned
   blindness (VERITE recall 0.0), and the original versus mismatch
   boundary (61 percent of the winner errors).
4. **Datasets (3).** NewsCLIPpings, VERITE, MMFakeBench. Failure modes
   and internals are shared nodes, not copies per dataset.
5. **Interventions (20).** Every avenue and lit-review technique with its
   true status: 2 shortlisted and running, 6 proposed, 5 background,
   7 killed.
6. **Evidence (16).** The research-brain findings (9 open, 1 closed),
   the two board passes of 2026-11-24, and the headline numbers that
   anchor the failure modes.

Counts: 63 nodes, 63 edges (causes 11, measured_by 11, shared_across 11,
treats 15, killed_by 7, depends_on 6, blocked_by 2).

## The shared-internals insight

The graph's point is sharing. One internal feeds several failures across
several datasets:

- **Training mix and loss masking** is the most connected internal: it
  is the standing hypothesis behind the disagreement, and behind both
  collapses, which point in opposite directions on the same dataset.
- **The routing trigger** fired at rate 1.0 in both stages, so one
  threshold setting touches every evidence read on NewsCLIPpings.
- **The similarity confound** is the one failure mode shared across
  NewsCLIPpings and VERITE, and its audit is the one intervention that
  serves both at once for $0 to $0.45.
- **The abstention artifact** is shared across NewsCLIPpings and
  MMFakeBench: fitted reads did registered work in both places.

## The three strongest paths

1. **One training defect behind three failures.** Training mix and loss
   masking → screen-choice disagreement, pristine collapse, mirror
   collapse → the loss masking audit and commitment controls. Audit $0,
   controls $0.45 to $0.90. If a masking defect exists it outranks every
   other explanation of the two collapses, and every trained result
   gains a caveat. Already running.
2. **Price the similarity explanation before training again.** Screen
   design → similarity confound → the similarity audit on frozen
   snapshots, shared across NewsCLIPpings and VERITE. $0 to $0.45,
   stored artifacts only. Already running.
3. **The blind class with no live intervention.** Question pack wording
   → miscaptioned blindness (recall 0.0 in BASE and EVIDENCE) → the
   separate miscaptioned rescue avenue (proposed, about $0.90 to $1.80).
   The direct RED-DOT pilot was killed as drafted, so this is the one
   failure mode whose front-door intervention is dead; the rescue is
   the surviving route.

## The dead ends, and why

- **Relevance pilot (RED-DOT pattern), killed as drafted.** It tested
  nothing about RED-DOT: the same checkpoint grading its own evidence
  with one home-made question. Its weak success form sat inside the
  2.1 to 2.4 percent re-judging noise floor. An 8-point re-registration
  spec is on file.
- **Dense rerank (Arm W v2), killed by all three critics.** Pool
  widening confounds the ordering hypothesis, the dense encoder was
  unnamed at registration, and one success criterion cited a number
  that does not exist in the record.
- **MERIT, RAMA, CRAVE, the fitted abstention selectors, CLIP-IN:**
  killed in the lit review board. Protocol mismatch (binary F1 beside
  macro-F1), wrong scale, the fitted-selector bet this study already
  lost, and an encoder loss that cannot reach a frozen vision tower.
- **Background, not dead:** BCEA's three-way routing framing, IVON
  variational fine-tuning (feasibility unverified), the evidence
  pollution defenses, the fixed-hard-negatives caution, REFORM and
  DPOD as related-work references.

## A connection the sources did not support

The A8 trigger refit finding has no measured link to any failure mode:
the record never explicitly closes it, so the graph carries it as an
evidence node with no edges rather than inventing a causal line to the
routing trigger. The same holds for the Phase 3 recomputation gap and
the compressed-forms caveat finding: real findings, no sourced edge.
