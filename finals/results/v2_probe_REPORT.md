# LAYA v2 Probe — Report

Probe: EvidenceGate ("search → LAYA") feasibility for the LAYA study
(owner: Rafiul Haider). Design of record: `DESIGN.md` (base registration
+ Amendments 1–5). This report is built section by section as each leg
completes; every number below is measured, with its artefact named.

---

## TinEye reverse-image side test (pilot subtask)

**Question.** Can SearXNG's TinEye engine — reverse image search by
public image URL, zero infrastructure — supply *binding* evidence
(original publication context for the image itself) for the probe items?

**Setup.** Throwaway SearXNG instance (port 8889,
`searxng_settings_tineye.yml`, tineye engine enabled, JSON format on),
separate from the probe instance on port 8888, which was never touched.
Two runs: run 1 during initial pilot work, run 2 on 2026-11-23 as the
named subtask. Raw results: `tineye_test.json`.

**Control tests.**

| Run | Control image | Result |
|---|---|---|
| 1 | Wikimedia Commons public image URL | 0 results — engine: "HTTP connection error" |
| 2 | Guardian-published news portrait (Paul Schrader, photographed for The Guardian, Nov 2026; photographer's public hosting; HEAD-verified 200 image/jpeg before querying) | 0 results — engine: "HTTP connection error" |
| 2 | Wikimedia URL repeated (comparability) | 0 results — engine: "Suspended: HTTP connection error" |

**Diagnosis (from the response + server log, not just the empty
result).** The failure is network-level, before TinEye is ever reached:
`curl -I https://tineye.com` from this VM returns 000 in ~1.2 s — the
egress proxy disconnects the connection. The SearXNG log agrees:
`searx.network.tineye: ConnectionError: the server has disconnected`,
and `curl_cffi.requests.exceptions.ConnectionError … 'tineye.com'` in
the engine processor. The first query of a run errors with "HTTP
connection error"; SearXNG then suspends the engine, so every later
query fails instantly as "Suspended". The 0-result counts are therefore
an engine/transport failure in every test — never a "no matches"
answer. Whether TinEye would *also* block this client as a scraper
cannot be observed from here and is not claimed either way.

**Probe test.** Not runnable, for a structural reason independent of
the engine: **no pilot item has a public image URL to query with.**
All 30 pilot rows of `probe_items.jsonl` and their VisualNews val
metadata entries were scanned — zero http(s) strings anywhere.
`image_path` is archive-relative and `self_article_url` is an
archive-internal filename; the images exist only as members of the
91 GB `origin.tar`. The constructed per-file URL on the Rice server
(`https://www.cs.rice.edu/~vo9/visualnews/origin/washington_post/images/0289/074.jpg`,
pilot item 1) returns HTTP 404 — the archive is not served per-file.
Run 1 additionally submitted a constructed BBC-item archive URL: same
engine error, 0 results.

**Structural verdict.** This channel **cannot supply binding evidence
for the val probe items** — two independent reasons, either sufficient:
(1) the TinEye engine cannot reach tineye.com from this VM (egress
proxy disconnect, reproduced across two runs and three control/probe
queries); (2) TinEye's query interface is a public image URL, and the
probe images are archive-held with no public URL. No paid TinEye API
and no account were used, per scope. Binding evidence for the probe
must come from the text-search channel; a self-hosted perceptual-hash
index (SSCD-style) remains the full-study route to an image-anchored
channel, as registered in `HOW_OTHERS_SOLVED_IT.md`.

**Cost.** ~10 minutes wall, $0 spend. Throwaway instance terminated;
the probe SearXNG instance (port 8888) was left running and untouched.

---

## Retrieval instrument failure, repair, and resume (2026-11-23)

**Diagnosis (verified against the snapshot files).** The concurrent
batch retrieval runs (up to ~23 simultaneous query streams) tripped
Google CSE's "unusual traffic" suspension; with DuckDuckGo
CAPTCHA-blocked through the egress proxy, SearXNG silently returned
EMPTY result lists. Those snapshots are failed retrievals, not
retrieval results. Empty-pool (item, variant) pairs, counted from the
harness files' `pool_sizes`: probe-300 **481/600**, VERITE **375/400**,
Stage B carve (variant A only) **630/700**, pilot-30 **21/52**.

**First repair attempt and its loss.** A serial repair
(`repair_retrieval.py`: one query at a time, 1 s sleep, circuit-breaker
10 consecutive empties -> 240 s pause, frozen query lists unchanged)
reached **400/481** probe pairs (log: `repair_chain.log`), but the
script wrote its outputs only at completion and the agent session
ended first — the repaired pairs were held in memory and are lost.
Verified: no repaired output files exist anywhere on disk.

**Resume (this session).** SearXNG restarted on port 8888 with the
identical settings file (`searxng_settings.yml`, SHA recorded in the
server log) — a test query returned results immediately. The repair
script was patched with (a) incremental per-pair checkpointing
(tmp-file + rename flush after every pair) and (b) idempotent resume
(pre-existing repair rows for still-empty pairs are dropped at load,
so a restarted run recomputes the todo from `pool_sizes` and never
duplicates). The probe repair was relaunched against the original
files; VERITE and Stage B repairs are queued serially behind it
(`repair_queue.sh`) — serial because concurrent streams are what
tripped the suspension. Every repaired record carries `repaired=true`
+ `repair_timestamp`; the pre-repair files remain untouched as the
record of the failure.

**Pod.** The probe pod (`mesc67xglzj5qn`, RTX 4090, $0.897/hr) was
terminated during this VM-side repair phase to stop idle burn, welded
to an artifact pull: pod logs (`pod_pull/logs/`), `val_metadata.json`,
and the 670-name carve-image list are on the VM. The two VERITE adapted
checkpoints were NOT pulled (proxy transfer ~42 MB in 4 min made the
1.5 GB pull impractical); they are re-creatable from
`verite_train.jsonl` + `train_verite.py` under the logged
configuration, and their predictions — the scored artifacts — are on
the VM in `verite_out/`. RunPod balance at termination: **$9.94**,
spend rate $0/hr after (probe-pod total burn from the $12.99 post-v1
balance: ~$3.05 across both agent sessions).

**Reproduce this stage:** `python3 repair_retrieval.py --items
probe_items.jsonl --raw-in evidence_probe.jsonl --harness-in
evidence_probe_harness.jsonl --raw-out evidence_probe_repaired.jsonl
--harness-out evidence_probe_repaired_harness.jsonl` (SearXNG on
127.0.0.1:8888 with `searxng_settings.yml`); queue: `bash
repair_queue.sh`.

---

## VERITE track — BASE / TRANSFER / ADAPTED (scored 2026-11-23)

Registration: `VERITE_SIDEARM_REGISTRATION.md` + Amendment 9. Split:
group-aware (by image identity) 80:20 of the local 1,001-row copy,
seed 20261122, frozen in `verite_sidearm_split.json`; held-out test =
**200 items** (65 true / 65 miscaptioned / 70 out-of-context). Tune
carve (100 items, train side only) selected the ADAPTED step budget:
**245 steps (tune acc 0.35) over 490 (0.31)** — the loser is reported,
per registration. ADAPTED test predictions carry checkpoint
`adapted_245` in their provenance. Scoring: `score_verite.py` ->
`verite_sidearm_results.json`; macro-F1 computed from the same
prediction files (the script reports accuracy + per-class recalls;
macro-F1 is the registration's secondary metric).

| Arm | Accuracy | Macro-F1 | Recall true (n=65) | Recall miscaptioned (n=65) | Recall out-of-context (n=70) |
|---|---|---|---|---|---|
| BASE (zero-shot) | 0.285 | 0.2154 | 0.2462 | 0.0000 | 0.5857 |
| TRANSFER (v1 MMF winner) | 0.320 | 0.2855 | 0.6615 | 0.2000 | 0.1143 |
| ADAPTED (245 steps) | 0.330 | 0.3310 | 0.3538 | 0.3846 | 0.2571 |

Paired bootstrap (2,000 resamples, seed 20261122, identical 200 items):
**ADAPTED − TRANSFER = +0.010, 95% CI [−0.080, +0.095]** — the
registered success criterion (lower bound > 0) is **NOT met**.
ADAPTED − BASE = +0.045, 95% CI [−0.030, +0.125]. In-benchmark
adaptation produced the most balanced per-class profile (it is the
only arm with non-trivial recall on all three classes, and the best
macro-F1) but no significant accuracy gain over transfer at n=200.
The parent prediction recorded in the registration (ADAPTED in the
low-to-mid 0.40s) **missed**: actual 0.330.

**Comparability warning (mandatory):** published VERITE numbers
(LAMAR 54.9, benchmark best 52.1) are full-set under their protocols;
these are a 20% carve under ours and are NOT comparable. H3's v1
verdict (transfer 0.3506 full-set, NOT MET) is untouched.

### The VERITE harness failure count (375/400) — explanation

`evidence_verite_stats.json` records `harness_flash: calls 400, fail
375`. What failed: the DeepSeek-flash triage step
(`harness.triage_and_select`) counts a "fail" when its output cannot
be parsed into a ranking (`_parse_triage` returns None), falling back
to engine-score order. The count equals the empty-pool count exactly
(375 = 375, verified pair-by-pair from `pool_sizes`): for every pair
whose SearXNG pool was empty — the retrieval failure above — the
triage prompt contained zero results, flash's reply contained no
rankable indices, the parse failed, and the fallback over an empty
pool yielded zero passages. For all 25 non-empty pairs the harness
worked end-to-end (full triage classes, selections, and passages are
in the snapshot; e.g. `verite:val:689`, pools 39/42). Nothing else
"carried" the failed 375 — variant A's deterministic path consumes
the same pools, so an empty pool means no passages under either
variant. **Whether it touches any result:** BASE / TRANSFER /
ADAPTED never consume retrieval, so their numbers above are
untouched. The EVIDENCE arm is the only consumer; pre-repair, only
**16/200** held-out items had any headline passage, so the EVIDENCE
arm was NOT run on the broken snapshots — it runs after the VERITE
retrieval repair (queued, § above) and reassembly.

**Reproduce this stage:** `python3 score_verite.py` (reads
`verite_out/preds_{base,transfer,adapted}.jsonl`, writes
`verite_sidearm_results.json`).

### Repair outcomes (probe + VERITE) and two runtime restarts

**Probe repair: COMPLETE.** 481 pairs attempted serially; final
state **597/600 pairs non-empty**. Three pairs stayed empty after the
full pass and are marked **RETRIEVAL-FAILED** (a failed retrieval,
distinct from a genuine no-evidence result): `val:3210` variant B,
`val:3694` variant A, `val:5521` variant B. Only `val:3694` loses its
headline (variant-A) pool; the other two lose only the measured
variant. Flash triage during repair: 481 calls, 3 fail (the same
empty pairs), spend **$0.35**. Reassembly (`assemble.py`, fetched-date
discipline, no `--raw` cross-check — see below): 300 items, tag calls
300/300, exclusions verdict_content 4 / factcheck_claim 0 /
same_source_exact 100, **headline coverage 193/300 = 64.3%** (above
the registered 60% claim bar). Assembled file SHA-256
`f8bc0fadaea7559d9a0d5a2fdbca0b8341d5a6130961486981c19e79859f7705`.

*Why no `--raw` cross-check:* assemble.py optionally asserts every
passage URL appears in the raw snapshot file. The pre-repair raw and
harness files came from different partial batch runs and are not
row-complete for every item (e.g. `val:1538` has a full variant-B
harness pool but zero rows in the raw file — the original assembly
necessarily skipped the check for the same reason). No URLs were lost
by the repair (verified: repaired raw is a superset of the original
raw for every item). The harness snapshots are the evidence of
record; their hashes are in the fold-in package.

**VERITE repair: COMPLETE.** Of 375 empty pairs, **324 were repaired;
51 remain empty (RETRIEVAL-FAILED)** — final state **349/400 pairs
non-empty**. The repair spanned a runtime restart (below): the first
segment reached ~90 pairs, the resumed segment finished the rest
(resume-segment flash spend $0.10). EVIDENCE-arm coverage after
assembly is reported with the VERITE track results.

**Runtime restarts (platform events, not study events).** The agent
runtime restarted twice during this session, killing all VM-side
processes each time (SearXNG, repair chains). Losses were limited to
in-flight wall time: the per-pair checkpoint flush preserved every
completed pair, and each repair resumed in place from its own flushed
outputs. SearXNG was restarted with the identical settings file after
each event.

**Second pod — deployed, unreachable, terminated.** A replacement pod
(`y60f5daqmixpqi`, SECURE NVIDIA A40 at $0.597/hr — the 4090 was
supply-constrained in both clouds) was deployed for the judging
phase, but SSH through the CONNECT proxy timed out on every attempt
(each flagged as an unanswered approval in this session), so no setup
or judging ever ran on it. It held no unique state. It was terminated
via the API to stop the burn: **$1.20 of idle burn** (balance $9.9337
-> $8.7291), reported as a probe cost with zero output — the same
"paying for an unreachable instrument" failure class as the TinEye
test, this time with a price tag. The judging phase awaits an
SSH-reachable pod; everything it needs (assembled evidence, scripts,
runbook `POD_PHASE_RUNBOOK.md`) is prepared and VM-resident.

**Reproduce this stage:** assembly —
`python3 assemble.py --items probe_items.jsonl --harness
evidence_probe_repaired_harness.jsonl --meta pod_pull/val_metadata.json
--dates fetch_dates_probe.json --out assembled_probe_repaired.jsonl`;
VERITE assembly — same shape with `verite_evidence_items.jsonl`,
`evidence_verite_repaired_harness.jsonl`, `fetch_dates_verite.json`.

**VERITE assembly (post-repair):** 200 items assembled from the
repaired snapshots (`assembled_verite.jsonl`). Exclusions:
**verdict_content 508, factcheck_claim 377**, same_source_exact 0 —
the claim-matched fact-check exclusion bit hard, exactly as
Amendment 9 anticipated for items that originate from fact-check
articles; these counts are part of the EVIDENCE arm's result.
Headline coverage after all exclusions: **89/200 items (44.5%)** with
>= 1 usable passage (pre-repair: 16/200). Date rule: all passages in
the undated stratum (VERITE items carry no publication dates), as
registered. Assembly flash spend $0.05. The EVIDENCE arm is
judge-ready (`judge_verite.py --assembled assembled_verite.jsonl`,
BASE checkpoint) and runs with the rest of the pod phase.

## Stage B — input preparation (complete; training awaits the pod phase)

The Stage B carve (700 train-split items: 500 train / 100 tune / 100
calib) went through the same instrument failure and repair as the
probe set. Repair final state: **694/700 variant-A pools non-empty**
(6 pairs RETRIEVAL-FAILED). Assembly (engine-date proxy discipline,
bound 2020-12-31, as designed for dateless train-split items):
exclusions verdict_content 10 / factcheck 0 / same-source 0; tag
calls 694/694. Training records built by `build_stageb_records.py`:
**500 train items and 100 tune items, 2 records each** (native +
noul forms, both against the evidence context per Amendment 6);
**94 of the 600 items have empty evidence blocks** and train with the
attuned question and no evidence text — the deployment reality for
no-coverage items, kept rather than dropped so the tune split stays
representative. Zero items were excluded for missing images (all 670
carved images present). The 100 calib items are reserved for the AM6
noul fit (temperature + threshold on calib only, frozen before the
probe is scored).

**Reproduce this stage:** `python3 assemble.py --items
stageb_items.jsonl --harness evidence_stageb2_repaired_harness.jsonl
--out assembled_stageb.jsonl` then `python3
build_stageb_records.py --have-file carve_images_list.txt`.

## A10 re-retrieval audit (complete)

At probe end, the 30 pilot items were re-retrieved fresh (serial,
same query lists) and their passage-URL sets compared against the
frozen repaired pools: **60 (item, variant) pairs, mean Jaccard
0.2161, median 0.1111** (`audit30_jaccard.json`). Live retrieval is
therefore **not reproducible** at a one-day lag — result sets drift
with engine availability and ranking churn. This is the quantitative
justification for the frozen-snapshot design: every number in this
study is computed against the hashed snapshots, and any replication
must start from them, not from a fresh search.

**Reproduce this stage:** `python3 retrieve_batch.py --items
probe_items.jsonl --variants AB --out-prefix evidence_audit30
--workers 1 --sleep 1.0 --limit 30`, then the Jaccard computation in
`notebook_foldin/audit/package.json`.

## Pod-phase status — BLOCKED on SSH access (all inputs ready)

Everything the judging phase needs is prepared and verified on the
VM: assembled probe evidence (coverage 64.3%), assembled VERITE
evidence (44.5%), Stage B training/tune/calib records, the frozen P0
comparator derivable from `probe_items.jsonl`, all judge/score/train
scripts, and a step-by-step `POD_PHASE_RUNBOOK.md`. What remains
pods-only: pilot judging (30 items), Stage A scoring (300 items),
Stage B training + AM6 calib fit + evaluation, the VERITE EVIDENCE
arm, and the four closing scorings. The one attempted pod this
session was unreachable over SSH (approval-gated proxy timeouts) and
was terminated unused ($1.20 idle burn, above). These stages complete
as soon as an SSH-reachable pod is available; estimated additional
pod cost $2-4 against the remaining balance of $8.73. No judging
number in this report is estimated or extrapolated — the blocked
stages are reported as blocked, with their inputs proven ready.
