# LAYA — How the Whole Thing Works + Issues Review: Midterm → Final
Written 2026-11-22 ~17:17 ET, at Rafiul's request. Sources: situation log (28 changes, contradictions C1–C10), rehearsal log, the six swarm verification reports (2026-11-22), the field-test report + mistakes.md, and live pod state read at writing time (grid at the 735-step configs; MMF test tree complete 10,000/10,000).

## PART 1 — HOW THE WHOLE THING WORKS (the machine, end to end)
1. **October audit (the diagnosis).** Saved predictions from every October run were re-scored from disk: the paired model collapses onto "mismatch" (per-class recall 1/300 · 8/300 · 22/100 · 289/300 on test), binary accuracy equals the all-Fake floor, a TF-IDF baseline beats the zero-shot model, and a frozen-feature probe shows the signal IS learnable (+6.24 pp on NewsCLIPpings test). A metadata rule scoring 0.9150 proved source metadata leaks the label → the metadata ban.
2. **Pre-registration.** Hypotheses H1–H5, the frozen success rule (≥ +0.03 F1 AND bootstrap LB > 0 AND no recall drop > 5 pp), tune-only selection, test scored once — all written BEFORE any training.
3. **Midterm deliverable.** PaperOrchestra drafted the diagnosis-half paper from the audited bundle (verified numbers; internal reviewer score 2/10 — a working draft of the diagnosis, never submission-ready).
4. **The final run (today) — one notebook, executed on a RunPod 4090, synced to Colab per stage:**
   CONFIG (per-dataset packs: each dataset's own choice + noul questions, labels, metric, calibration, checkpoint pointer) → SETUP (pinned env) → DATA (inventory asserts) → GATES (token audit, checkpoint round-trip) → BASELINES → STREAM PASS 1 (NewsCLIPpings baseline over the 91 GB VisualNews tar, in-memory verifier, integrity-only skips, per-source accounting) → GRID (12 configs: 2 arms × 2 losses × 3 step budgets, tune-only scoring, receipts per config) → SELECTION (frozen rule → winner.json) → NCP ARM (own carve from the official train split, winner's recipe × 2 budgets, own weights) → SUPPLEMENTARY TIER (13 ablations, isolated receipts) → TRAINED EVAL → TEST-ONCE (marker-guarded, paired bootstrap vs the October baseline predictions) → VERITE TRANSFER → STREAM PASS 2 (NCP winner) → CALIBRATION (per-dataset temperatures on calib split only) → VERDICT (H1–H5 from receipts) → PUBLISH (HF model repo + Space, marker-guarded) → COMPLETE RECORD (final_results_bundle.json — every number the final paper may use).
5. **Final paper.** A second PaperOrchestra pass written ONLY from the complete record (writer = gemini-4-neon under the $10 cap), with the midterm draft's six verified defects corrected from material in hand.
6. **Public record.** GitHub finals/ (status, paper, notebook, code, results) + the HF Space (before/after demo on the pack structure).

## PART 2 — THE ISSUES, MIDTERM → FINAL

### A. Wrong-object errors (all caught and fixed; each would have silently corrupted results)
1. **Vision checkpoint identity.** The study long treated `convaiinnovations/laya` as the vision base; the rehearsal proved it is the TEXT model (421M). The vision checkpoint is `thaitea/laya-vision` @ f2fe3c1 (201M). The Space's BEFORE slot inherited the wrong repo (situation C4) — fixed in prep.
2. **Nonexistent Space API.** hf_space/app.py originally called a `score_pair` API that does not exist; the real API is load_vlm → predict → answers.native.probabilities / answers.fake.noul. Rewritten in prep; first-boot smoke check still owed at publish.
3. **PyPI laya vs dev laya (twice).** PyPI laya has no VLM code. Rehearsal flagged it; the main run STILL hit it when driver v1 crashed mid-pip-install and poisoned the install (franken-package). The notebook's fail-closed assert caught it before training. Root fix: force-reinstall into the kernel interpreter + warm-up import.

### B. Data-availability illusions (things believed present that were not)
4. **"VisualNews is on the Mac" — false.** Exactly 4 images existed; October's NCP numbers were streamed predictions. Consequence: the entire stream-only architecture + verifier + two-pass cost structure.
5. **MMFakeBench test images.** Annotations landed; images stalled at 934/10,000 on the Mac-upload leg. Closed by the whole-tree tar route; tree verified complete (10,000) at ~17:15 ET today.
6. **NewsCLIPpings train.json missing on the pod** — found by the swarm's data audit hours before the amendment-(c) carve would have failed on it. Synced + counted.
7. **VERITE 1,001 vs 1,000.** The local copy has 1,001 rows; the official release is 1,000. Every reported VERITE number must carry the local-copy qualifier (midterm draft did not).

### C. Library limits that forced design amendments (disclosed, dated)
8. **Vision tower cannot be unfrozen** through vlm_train.train → amendment (b): both arms freeze it; "full" = encoder LM + head (114.7M of 201M), labelled honestly everywhere.
9. **soft_ce is not expressible** through vlm_train.train (its objective always includes the policy-gradient term) → implemented in-module from the library's own components so the loss contrast differs ONLY in objective.
10. **LoRA has no library support** → a peft binding was built and proven in rehearsal (r16/α32, set_trainable workaround, merge + VLMAgent.save).
11. **The stock baseline CLI cannot consume a stream** → custom streaming driver + the field-tested verifier module (with its own defect history: the hang → 120 s timeout fix; palette-transparency route; oversize guard — all in mistakes.md).

### D. Pre-registration integrity (the paper MUST disclose; all documented)
12. **C9 — H1's arm definition changed after registration** (amendment (b)). Predictions unedited (correct); the final paper must state the redefinition explicitly or the pre-registration claim misleads.
13. **H2 re-aimed** by amendment (c) from transfer to the trained NCP arm; the base transfer number is still reported beside it.
14. **Supplementary tier added post-registration** (amendment (d)) — isolated in runs/supplementary/, never feeds selection; reported as ablations, not as part of the registered comparison.
15. **Validation↔test exposure:** 9 rows / 14 hash edges / 14 excluded test rows. An earlier record said "76 test items" (C5) — superseded by the reconciliation; the final paper uses 9/14/14.

### E. Midterm paper defects (final pass must fix; correction material verified in hand)
16. Placeholder author block ("Ambitious AI Researcher / AI Research Institute") → Rafiul Haider, Pace capstone, Team 3.
17. **§4.6 regime mix:** GPT-4V Standard 51.0 was printed alongside LLaVA MMD-Agent 49.9 (LLaVA Standard is 25.7). Correct figures exist in the bundle §12.
18. **−1.51 pp unit mix:** the paired−text CI is [−2.44, −0.54] pp.
19. **Bibliography of 3** for a paper making many sourced claims; and NO citation for NewsCLIPpings or for LAYA exists in any input — the final pass must source both (Semantic Scholar), never invent them.
20. The draft's scope is the diagnosis half only (reviewer 2/10); the final pass adds the adaptation half from the complete record.

### F. Process and tooling issues
21. **PaperOrchestra run #1 died silently** during Literature Review (buffered log lost) — run #2 completed after a mid-run LaTeX install unblocked its compile gate.
22. **Watchdog churn:** auto-restart watchdog → Rafiul switched it to alert-only → it delivered run #2's result and removed itself; its state file still describes run #2 as current (C7) and MEMORY was stale on the mode until corrected (C2).
23. **Gemini budget opacity:** the ~$20 credit was exhausted mid-afternoon (HTTP 402) and topped up; exact lifetime spend is UNVERIFIED from local records (C1). The $10 cap + Neon-writer config now govern the final pass.
24. **mas.py Semantic Scholar pacing flaw (STILL OPEN):** parallel workers burst past the 1 req/sec limit (429s); needs internal pacing before the next crew mission.
25. **RunPod route reality vs docs (C8):** community pods unreachable; secure pods + CONNECT-proxy SSH are the working route; the connector doc still describes the community spec.
26. **Stale standing records (C3, C5, C6, C10):** notebook cell counts (18 vs 19 vs 25 vs 50 vs 57 across records), the Oct-19 head-only plan still presented as current in one record, the rehearsal log's stage table, and rounding-level inconsistencies (tier-0 delta "0.0" vs "<1e-4"; NCP zero-shot F1 0.4185 vs 0.4186). Individually harmless; collectively they are how the wrong repo string survived — the class of error this review exists to catch.
27. **Drive "Research" staleness:** the Colab file held the old 25-cell notebook while the team believed it current — the direct cause of Rafiul's "I don't see it running." Fixed by the patch upload + per-stage syncs.
28. **Driver v1 crash** on a partial notebook write (plain-dict outputs vs nbformat nodes) — fixed (NotebookNode conversion; write failures can no longer kill a run); CONFIG's execution was preserved via shadow replay, disclosed in the log.
29. **Notebook cosmetic drift:** stale cell-number pointers in the visuals cell (fixed in the patch); "Midterm" naming retained in internal filenames (midterm_results.json) though this is the final run — internal only, deliberately not renamed mid-flight.

### G. Issues the swarm caught today, before they cost anything
30. **F1 — NCP label-flip pooling:** the NCP arm's two question forms have flipped label indices; the original cell pooled them into one selection metric. Fixed: native-form-only metric.
31. **F2 — trainer dataset tag hardcoded** to "mmfakebench" for all files. Fixed: parameterized before the NCP arm.
32. **F3 — bootstrap baseline file in the wrong folder** (VM staging, not a CONFIG candidate path) — would have failed the test stage closed. Fixed: landed on the pod.
33. **F4 — bootstrap gold-agreement assert** added (a row-order divergence would otherwise silently corrupt the delta).
34. **HF token fallback trap:** the publish cell's workspace scan would silently skip the Mac's .rtfd package. Routed around: token via SSH stdin → pod HF cache, presence-verified only.
35. **Stream throughput was unmeasured** — the budget's swing factor ($0.98/pass at 25 MB/s vs fatal at 2.5 MB/s). A parallel range reader was built and member-sequence-verified against the sequential reader; PASS 1 measures the pod rate in its first minutes, with segmented streaming as the sanctioned escalation.

### H. Still open at writing time
36. PASS 1's measured pod throughput (the figure the whole budget question hinges on) — pending the pass's first minutes.
37. H4's verdict (winner's minimum per-class recall ≥ 0.25) — decided at selection; one non-winning config already showed a 0.00 class.
38. Fusion chain (Harika text + Ananya image + Rafiul paired → stacker) — blocked on teammates' prediction files; Rafiul's widget decision on wiring still open.
39. Final PaperOrchestra pass — blocked on the complete record, by design.
40. The 735-step configs + NCP arm + supplementary tier + test-once + calibration + publish — in execution; the run's completion standard is one complete final report with any deviation named in it.

## PART 3 — THE PATTERN UNDERNEATH
Every serious issue in this list is the same shape: **a belief about an object that nobody had re-read since it changed** — a repo name, a file's presence, a count, a plan's currency. Every save came from the same counter-move: read the object itself (the pod, the PDF, the sent body, the receipt) and let the record follow. The final paper's methods section can honestly claim that discipline, because the run's gates enforced it mechanically: three times today a fail-closed check stopped the line before GPU money was spent on a wrong input.
