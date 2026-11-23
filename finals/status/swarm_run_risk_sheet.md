# LAYA Main Run — RUN-RISK SHEET (one page)

**Built 2026-11-22 ~16:25 ET, from measured evidence only.** Rate card: secure RTX 4090
pod u4eixy0wfqbgll billing **$0.897/hr** (= 1.495 ¢/min). Balance **$9.0525** (live check);
run started at $9.77 → **$0.72 already spent**, zero grid configs run yet.
**Hard stop: total pod spend approaching $8.00 → $7.28 of allowance left.**

## Measured inputs (no guesses downstream)

| Input | Value | Source |
|---|---|---|
| Full-arm step time, batch 8 | **0.57 s/step** (20 steps / 11.4 s) | rehearsal_log.md |
| LoRA-arm step time, batch 8 | **0.68 s/step** (20 steps / 13.6 s) | rehearsal_log.md |
| Agent load | 3.7 s | rehearsal_log.md |
| Paired inference rate | ~0.09–0.12 s/item (1,000-item val in ~1.5–2 min) | mainrun_log.md |
| VisualNews stream rate, this VM via proxy | **2.49 MB/s** (2,174,559,744 B / 873.6 s) | VISUALNEWS_FIELD_TEST §1 |
| origin.tar size | 97,916,641,280 B (91.2 GiB), sequential-read | field test §1 |
| Pod stream rate | **UNMEASURED — the swing variable** | field test R1 |

## (1) GRID — 12 configs (2 arms × 2 losses × steps 245/490/735), batch 8

Steps per arm = (245+490+735) × 2 losses = 2,940. Full: 2,940 × 0.57 s = 27.9 min.
LoRA: 2,940 × 0.68 s = 33.3 min. **Pure training = 61 min.**
Per-config overhead ×12 (load 3.7 s + ~800 MB checkpoint save + tune eval on 105 items
at 0.1–1.0 s/item): +8–27 min.
**Grid total: ~70–90 min → $1.05–$1.35.** Comfortably affordable. Not the risk.

## (2) STREAM PASSES — PASS 1 (base) + PASS 2 (winner), 91.2 GiB each, read in full

A pass pays for the whole archive: sources sit in contiguous blocks and guardian
(47% of the 5,943 referenced images) is deep in the tar. Inference on 5,943 items
(~10 min) is minor next to transfer. Cost per pass at $0.897/hr:

| Pod stream rate | Time / pass | $ / pass | $ / two passes |
|---|---|---|---|
| 2.5 MB/s (= VM proxy rate) | 10.9 hr | $9.77 | **$19.54 — fatal** |
| 10 MB/s | 2.7 hr | $2.44 | $4.88 |
| 25 MB/s | 65 min | $0.98 | $1.96 |
| 50 MB/s | 33 min | $0.49 | $0.98 |
| 100 MB/s | 16 min | $0.24 | $0.49 |

**Flag: YES, the two passes threaten the budget.** Break-even: after non-stream
spend (~$2.6–3.4, below), ~$4.6–5.4 remains → the plan fits under the $8 stop only
if the pod sustains **≥ ~10–11 MB/s**, and fits comfortably at ≥ 25 MB/s. At the
VM's proxied 2.5 MB/s the passes alone cost 2.4× the entire remaining allowance.
**Decision gate: measure the pod's real rate in PASS 1's first 5 minutes** (PASS 1
runs concurrently with the grid, so its clock overlaps compute). Escalation if
slow: parallel range-segment streaming — header-sync entry is proven (≤129 KB
scan, field test §1) — then the standing descope order.

## (3) NCP ARM (amendment c) — carve + 2 configs, winner's recipe, ~2,000 train items

Training: step budgets 490 + 735 = 1,225 steps × 0.57–0.68 s = **12–14 min**.
Tune evals (250 items × 2 configs): ~1–8 min. Carve: JSON carve is minutes of CPU;
saving the ~2,500 train-split images rides a bounded stream (shares §2's rate risk,
not separately priced). **NCP compute total: ~15–22 min → $0.22–$0.33.**

## (4) TOTAL PROJECTION vs balance and the $8 hard stop

| Line | Projected spend |
|---|---|
| Already spent (sunk, deploy → now) | $0.72 |
| Grid (§1) | $1.05–1.35 |
| Test-once (9,999 items) + winner val/VERITE evals + calibration | $0.32–0.40 |
| NCP arm (§3, compute) | $0.22–0.33 |
| Publish (HF uploads), final notebook pass, idle/slack | $0.30–0.60 |
| **Subtotal, everything except stream passes** | **$2.61–3.40** |
| + streams @ 25 MB/s | **$4.57–5.36 → FITS** |
| + streams @ 10 MB/s | **$7.49–8.28 → AT / OVER the stop** |
| + streams @ 2.5 MB/s | **~$22 → IMPOSSIBLE** |

**VERDICT: TIGHT.** All compute fits with room to spare (~$2.6–3.4 of $8). The run
lives or dies on one unmeasured number: the pod's stream throughput. Descope order
(standing rule): **NCP arm first** — but note honestly that it frees only ~$0.3;
if streams measure slow, NCP descope alone does not save the run. The real levers,
in order: (i) parallel range-segment streaming, (ii) a Rafiul decision on PASS 2.
Disk: 50 GB pod volume vs ~15–20 GB projected (15 saved models × ~0.8 GB ≈ 12 GB +
MMF trees + NCP subset + base checkpoint 0.77 GB) — fits, ~2.5× headroom; prune
non-winner checkpoints after the artifact pull if it tightens.

## (5) TOP 3 SCHEDULE RISKS

1. **Stream throughput (budget-killer, §2).** Mitigation: measure in PASS 1's first
   5 min, while the grid trains in parallel; escalate to range-segment parallel
   streams (proven) before the pass burns > ~$1.50; hold PASS 2 until the rate is
   known. Never let a pass run unmeasured.
2. **Pod bills during non-compute time.** $0.72 burned before the first grid config
   (env fixes, notebook redirect, driver crash + franken-laya repair ~16:12 ET).
   Every cell failure or waiting gap costs $0.897/hr. Mitigation: run attended,
   pre-flight heavy cells, keep the descope triggers above so a stall converts to
   a decision, not a meter.
3. **MMF test-tree sync gates the finale.** Test-once needs all 10,000 test images
   hash-verified on the pod; the Mac upload was at ~280/10,000 at the redirect.
   It is off the critical path only until test-once. Mitigation: it uploads in
   parallel with the grid — verify counts early; fallback is the sanctioned
   pod-side HF test-zip download + hash-match (sync architecture, mainrun_log).

*All figures derive from the table in "Measured inputs"; the only unmeasured
quantity in this sheet is the pod stream rate, and it is labelled as such.*
