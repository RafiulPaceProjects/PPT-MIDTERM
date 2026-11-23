# LAYA MAIN RUN Log — 2026-11-22

Authorized by Rafiul's "go" (2026-11-22). Design: notebook LAYA_Colab_Staged_For_Review.ipynb (amended option b: vision tower frozen in both arms). Budget: RunPod balance $9.77 at start; HARD STOP if projected pod spend approaches $8. Pod must be terminated at the end no matter what.

| Stage | Status | Notes |
|---|---|---|
| 0. Prep / survey | in progress | rehearsal log + notebook + trainer read; Mac surveyed; HF token located (hf token.rtfd, not read yet) |

## Sync architecture (decided 2026-11-22 ~15:35 ET)
- MMFakeBench val+test: pod downloads the OFFICIAL zips from HF `liuxuannan/MMFakeBench`
  (same repo files as the Mac's: MMFakeBench_val.zip / MMFakeBench_test.zip + annotation
  JSONs). Verification: repo annotation JSONs must hash-match the Mac copies already on
  this VM; every annotation image_path must exist post-extraction; sha256 spot-checks of
  extracted images vs Mac-uploaded copies.
- Finetune images are a subset of the MMF val tree (records resolve ../../../raw/...),
  double-covered by the Mac upload of the full val tree (848 files) AND the HF val zip.
- VERITE (663) + NewsCLIPpings val images (5,943; guardian 2776 / usa_today 1343 /
  washington_post 948 / bbc 876): Mac -> VM via parallel files.upload workers -> staging
  -> scp to pod. VisualNews has no usable public image mirror (HF repos carry JSONs only).
- Test population confirmed = FULL 10,000 rows (Oct 25 ablation: 9,999 usable, paired
  macro-F1 0.20374 — the baseline test number for the paired bootstrap; its saved
  predictions will be pulled from the Mac for pairing).

## Notebook contract (fresh staged notebook, 25 cells, read 2026-11-22)
- Grid receipts: runs/{arm}_{loss}_{steps}/result.json; winner: runs/winner.json.
- Calibration: runs/<winner>_calibrated/calibration.json (select_and_calibrate default).
- Comparison table: data/reports/midterm_results.json (plot b's preferred baseline source).
- Step 8 execution plan: nbconvert --execute on the pod; the two heavy compute cells
  (baseline CLI sweep, training grid) will read back the run's real artifacts instead of
  re-spending GPU (disclosed in the executed notebook + final report); gates, plots,
  bundle cells execute for real.

## NewsCLIPpings image problem — FOUND + plan (2026-11-22 ~15:40 ET)
- The Mac NEVER held the VisualNews archive: its visual_news tree contains exactly 4
  images, fetched one-by-one from publisher CDNs for an Oct 19 four-row diagnostic
  (acquisition_manifest.json in newsclippings_image_subset_v1). The Oct full-split NCP
  numbers (val acc 0.5083, n=7,024) were computed from streamed predictions in October;
  the image archive itself is not in the workspace. Parent-context claim that the Mac
  held the visual_news tree was WRONG — corrected here.
- Official VisualNews distribution (Rice): origin.tar = 91 GB (too big to store; pod
  disk 50 GB). PLAN: on the pod, stream the tar over HTTP and extract ONLY the 5,943
  val-referenced members (tar -T), discarding the rest — disk cost ~1-2 GB, transfer
  runs in background while the grid trains (grid does not need NCP).
- The 3 remaining NCP upload workers were closed (their lists are unfillable from the
  Mac); val x2 + VERITE workers continue.

## DIRECTIVE CHANGE (Rafiul, 2026-11-22 ~15:36 ET) — VisualNews is STREAM-ONLY
- The extract-to-disk plan for NewsCLIPpings is SUPERSEDED. VisualNews images must be
  streamed in, NOT saved, to save space: a single streaming pass over the official
  origin.tar over HTTP (tarfile stream mode 'r|*'), members matched against the
  val-referenced path set (5,943), each image loaded in memory -> PIL -> paired-route
  inference -> prediction rows recorded -> image discarded. NO VisualNews image file
  is written to pod disk at any point.
- Consequence (noted per instructions): this is one-pass consumption — a member missed
  in a pass can only be recovered by re-streaming the pass, not by re-reading disk.
  Baseline and winner NCP evals therefore cost one full stream pass EACH.
- Implementation: a custom streaming driver reusing the workspace baseline_study
  question construction + the same laya predict calls as the vision worker (the stock
  CLI loads images from disk paths and cannot consume a stream). MMFakeBench + VERITE
  legs are unaffected (CLI from disk). Training grid unaffected.

## DIRECTIVE #2 (Rafiul, 2026-11-22 ~15:37 ET) — VERIFIER at the VisualNews stream
- For each streamed member matching a referenced path: verify bytes IN MEMORY before
  inference — full PIL decode must succeed and dimensions must be non-degenerate.
  On failure: SKIP the row, append {path, reason} to a skip ledger, continue the pass;
  never fail the stream on a bad image.
- Binding refinements: (1) skips are INTEGRITY-ONLY — never on content, model
  uncertainty, or anything label/prediction-related; (2) accounting reported per
  SOURCE (bbc / guardian / usa_today / washington_post): referenced -> scored ->
  skipped with reasons, so a source-clustered failure is visible as a finding;
  (3) NewsCLIPpings accuracy is computed over the SCORED n and labelled as such.
  Mirrors the study's missing-row discipline (Oct 25 test ablation: 9,999/10,000 usable).
- Implementation in the stream driver: skipped rows are written as status='blocked'
  prediction items (the engine's own semantics; score_records computes over usable),
  plus a stream_skip_ledger.jsonl and a per-source stream_accounting.json per pass.

## Stream core swapped to the prep-built module (2026-11-22 ~15:42 ET)
- visualnews_stream.py (built + test-passed by a parallel prep) is now the
  stream/verify/accounting core of stream_ncp.py: verify_image_bytes (full PIL
  decode, degenerate = either side < 8px; reasons decode_error / truncated /
  degenerate_dimensions / empty_member) + stream_verified (tarfile 'r|*',
  120 s per-read inactivity timeout; raises only on stream-level failure) +
  SkipLedger per-source summary. My driver's blocked-row semantics, incremental
  prediction writes (resume across an aborted pass), metrics and manifest
  wrap around it. Inference runs in-process on the module's verified RGB image;
  the stock-worker vs in-process-PIL equivalence gate (<1e-4) runs before any
  stream pass.

## Stage 1 — pod + env (2026-11-22)
- SECURE RTX 4090 pod u4eixy0wfqbgll deployed (~15:33 ET), SSH via CONNECT proxy.
  Balance at deploy: $9.7725, spend/hr $0.89.
- Env aligned + verified: torch 2.14.1+cu130 (CUDA ok on 4090), transformers
  5.19.0, peft 0.22.0, torchvision 0.29.1+cu130 (old 0.19.1 broke torch 2.14 —
  replaced), torchaudio removed, dev laya 0.2.0.dev0 from git 9e1e2419 (all
  vlm_train members present). Base checkpoint snapshot (thaitea/laya-vision
  @ f2fe3c1) downloaded to models/laya-vision-base (771 MB).
- Sync: wave 1 (workflows code, finetune jsonls, manifests, annotations,
  metadata) on pod; val tree (1,000) + VERITE (663) complete in VM staging and
  syncing; MMF test tree (10,000) uploading from the Mac in parallel chunks;
  NewsCLIPpings = stream-only (no files).

## Stage 2 — GATES: PASS (2026-11-22 ~15:47 ET)
- Trainer record check: 1,400 records (980/210/210), forms exactly class4+choice2
  halves, missing_images=0 (--strict-images).
- Gate 1 token audit: mean 18.07, p50 17, p95 32, max 43; 0 skipped = 0.00% over
  MAX_LEN 1024 (threshold 2%) — identical to the rehearsal.
- Gate 2 round-trip: 416 tensors, bit-identical.
- Stream fidelity gate: stock vision worker (path) vs in-process PIL predict
  (visualnews_stream verified RGB) on 3 val items — max abs probability delta 0.0.
  PASSED. (One fix en route: --set override values must be JSON-encoded strings.)

## REDIRECT — NOTEBOOK-ONLY EXECUTION (Rafiul decision, 2026-11-22 ~15:50 ET)
- "Run the whole on the notebook only — fix up and only run on the notebook —
  so I can see as the process runs." Headless stage execution is STOPPED.
  A separate fix-up pass is rebuilding LAYA_Colab_Staged_For_Review.ipynb into
  a fully self-contained executable notebook (every stage as real cells,
  including the VisualNews stream leg via visualnews_stream.py). When it
  lands, THAT notebook is executed end-to-end on this pod's Jupyter kernel,
  cell by cell, and the in-progress executed notebook is synced into the
  Drive "Research" file after each stage so Rafiul can watch outputs
  accumulate. No run logic lives in agent-side scripts from here on.
- POD STATE (preserved, NOT terminated): pod u4eixy0wfqbgll (SECURE RTX 4090,
  $0.89/hr) is RUNNING and billing — it becomes the notebook's runtime.
  Balance at deploy $9.7725; ~$0.35 spent by the redirect.
- POD CONTENTS (all preserved): aligned env (torch 2.14.1+cu130, transformers
  5.19.0, peft 0.22.0, torchvision 0.29.1+cu130, dev laya 0.2.0.dev0 @ 9e1e2419);
  base checkpoint at models/laya-vision-base (thaitea/laya-vision @ f2fe3c1);
  workspace /workspace/Misinformation with workflows code + laya_trainer.py,
  finetune jsonls (1,400 records), MMF manifests, MMF val tree 1,000/1,000,
  VERITE tree 663/663 + VERITE.csv, NCP annotations + metadata (images are
  stream-only — none on disk, by design); drivers + visualnews_stream.py +
  ablation test predictions under /root/drivers (agent-side scaffolding —
  superseded as run logic by the notebook; visualnews_stream.py is the
  notebook's stream module).
- COMPLETED HEADLESS RESULTS (pre-redirect; the notebook run will reproduce
  or supersede them as the record of the experiment):
  * Gates PASS (runs/gates.json): token audit 0.00% over MAX_LEN; round-trip
    416 tensors bit-identical; trainer check 1,400 records, 0 missing images.
  * Stream fidelity gate PASS: stock worker vs in-process PIL predict,
    max probability delta 0.0 on 3 val items.
  * MMF val baseline (paired, this pod): accuracy 0.293, macro-F1 0.2079,
    1,000/1,000 usable. Per-class recall: original .047 / textual .033 /
    visual .270 / mismatch .807.
  * VERITE baseline (paired, this pod): accuracy 0.3467, macro-F1 0.2819,
    1,001/1,001 usable, 0 errors.
  * NOT started: grid, NCP stream passes, winner evals, calibration, verdict,
    publish, notebook execution.
- VM staging: MMF test tree uploading from the Mac (4 workers on chunks 0-3
  of 10; ~280/10,000 at last count) — staging only, ready for the notebook's
  sync stage.
- STATUS: HOLDING for the fixed-notebook signal (local file + Drive).
- Correction to the spend line above: actual RunPod balance at the redirect
  check (15:51 ET) = $9.5757, currentSpendPerHr $0.897 — i.e. $0.197 spent
  since deploy, not ~$0.35. Pod remains RUNNING by design (notebook runtime).
- Upload workers final: val chunks 424/424 + 424/424, VERITE 663/663 — all
  verified in staging. MMF test chunks 0-3 still uploading.
- HOLDING for the fixed-notebook signal.

## ADDITION (Rafiul, 2026-11-22 ~15:53 ET) — COMPLETE ARTIFACT SET REQUIRED
- The final output must show the ENTIRE picture (it is the context the final
  paper is written from). Required artifacts, nothing summarized away:
  * all 12 runs/<arm>_<loss>_<steps>/result.json receipts + runs/winner.json
  * calibration: runs/<winner>_calibrated/calibration.json + temperatures
    (+ the H5 tune-calibration record)
  * BOTH NewsCLIPpings stream passes: stream_accounting.json +
    stream_skip_ledger.jsonl (+ metrics/summary/manifest per pass)
  * gates output (runs/gates.json + the gate cells' printed audit)
  * baseline + winner prediction files for EVERY dataset (MMF val + test,
    NCP val stream, VERITE val)
  * test-once predictions + the bootstrap detail (delta, CI, per-class
    recalls, recall drops)
  * data/reports/final_results_bundle.json (assembled by the notebook) +
    midterm_results.json
  * pod cost + wall time; this log as the deviations record.
- Committed step: BEFORE pod termination, pull the full artifact trees
  (runs/, data/processed/midterm/, data/reports/, executed notebook) from the
  pod to ~/workspace/misinfo_run/mainrun_artifacts/ and verify counts, so the
  returned record survives termination. The final report inventories every
  artifact with its path.
- Still HOLDING for the fixed-notebook signal.

## PRIORITY CHANGE (Rafiul, 2026-11-22 ~15:57 ET) — TRAINING FIRST
- "I want to start training — main training." When the fixed notebook lands,
  execution order is: setup -> data -> gates -> GRID (straight to training).
  MMF/VERITE baseline cells run immediately before the grid ONLY if they cost
  minutes (headless paired runs took ~1.5-2 min each); the NewsCLIPpings
  stream PASS 1 runs CONCURRENTLY with the grid (background), never in front
  of it. Gates remain fail-closed; all hard rules stand.
- Pod already deployed (u4eixy0wfqbgll) — no deploy needed; it is warm, env
  aligned, data synced, gates already proven once headlessly.
- Milestones to report: (a) pod state, (b) gates pass, (c) first config
  training start, (d) first tune F1 in the grid table.

## AMENDMENT (c) (Rafiul, 2026-11-22 ~15:59 ET) — NewsCLIPpings TRAINING ARM ADDED
- The fixed notebook will contain NCP training cells: NCP records carved from
  the official TRAIN split (lean ~2,000 train / 250 tune / 250 calib);
  the winner's recipe trained at 2 step budgets; the NCP pack serves its own
  weights; NCP val still evaluated via the stream; NCP test UNTOUCHED.
- Sanctioned exception to stream-only: the bounded TRAIN-split image subset
  (~2,500 images) is SAVED to the pod for training. Train split only — val
  remains stream-only, test is never touched.
- H2 RE-AIM: H2 (fine-tuned NCP val accuracy 0.55-0.65 AND >= +6.24 pp over
  the 0.5083 zero-shot) is now judged on the dedicated NCP arm's own
  fine-tuned model, not on transfer of the MMFakeBench winner. The MMF
  winner's NCP transfer number is still reported as a secondary observation.
- Execution rules (binding): (1) MMF grid FIRST — never delayed by the NCP
  arm; (2) NCP data prep proceeds DURING the MMF grid; (3) BUDGET GUARD —
  projected total spend is tracked; if it approaches the balance, the NCP
  arm is descoped FIRST (and reported) — the MMF grid, test-once, and
  publish are never starved.

## GO — MAIN TRAINING STARTED (Rafiul, 2026-11-22 ~16:06 ET)
- Execute the LANDED notebook (57 cells as on disk — packs registry, stream
  function + PASS 1, NCP carve + NCP training, method comparison, test
  bootstrap, complete record all present) cell by cell on the pod's live
  Jupyter kernel. Do NOT wait for the fix-up agent's remaining additions;
  its patch is picked up at the next stage boundary after grid/selection.
  Never re-run an executed cell; never re-score test.
- Order: setup -> data -> GATES (fail-closed) -> baselines (cells reuse
  complete artifacts by the notebook's own design) -> GRID immediately.
  Stream PASS 1 runs CONCURRENTLY with the grid in a second kernel
  (shadow setup cells; only its own cells' outputs are recorded).
- Drive syncs: after gates, and after each grid config completes ([done]
  lines in the grid cell's streamed output trigger a snapshot sync).
- Machinery: /root/kernel_driver.py on the pod (jupyter_client driving a
  live python3 kernel; per-cell outputs written back into the executing
  notebook /workspace/Misinformation/LAYA_MainRun_Executed.ipynb under a
  file lock; status at /root/driver_status_{A,B}.json).

## GO — MAIN TRAINING STARTED (Rafiul, 2026-11-22 ~16:06 ET)
- Execute the LANDED notebook (57 cells as on disk — packs registry, stream
  function + PASS 1, NCP carve + NCP training, method comparison, test
  bootstrap, complete record all present) cell by cell on the pod's live
  Jupyter kernel. Do NOT wait for the fix-up agent's remaining additions;
  its patch is picked up at the next stage boundary after grid/selection.
  Never re-run an executed cell; never re-score test.
- Order: setup -> data -> GATES (fail-closed) -> baselines (the notebook's
  cells reuse complete artifacts by design) -> GRID immediately. Stream
  PASS 1 runs CONCURRENTLY with the grid in a second kernel (shadow setup
  cells; only its own cells' outputs are recorded).
- Drive syncs: after gates, and after each grid config completes ([done]
  lines in the grid cell's streamed output trigger a snapshot sync).
- Machinery: /root/kernel_driver.py on the pod (jupyter_client driving a
  live python3 kernel; per-cell outputs written back into the executing
  notebook /workspace/Misinformation/LAYA_MainRun_Executed.ipynb under a
  file lock; status at /root/driver_status_{A,B}.json).

## DEVIATION + FIX (2026-11-22 ~16:12-16:16 ET) — SETUP assert / laya install
- Driver v1 crashed on a partial notebook write (plain-dict outputs vs
  nbformat nodes) ~20s into cell 8, killing its kernel mid-pip-install.
  Fixed (NotebookNode conversion; write failures can no longer kill a run).
  Cell 6's recorded execution was NOT re-run (shadow replay only).
- The interrupted pip run poisoned the laya install (franken-package:
  dist-info 0.2.0.dev0, __init__ 0.1.7, vlm_train unbound). Cell 8's
  fail-closed assert fired correctly on the resume attempt.
- Fix applied: pip force-reinstall --no-deps --no-cache-dir of the dev laya
  from git 9e1e2419 into the kernel interpreter (/usr/bin/python3);
  verified `from laya import vlm_train` + train() present.
- Residual notebook quirk (for the patch): the dev package's __init__ does
  NOT eagerly bind vlm_train, so cell 8's hasattr assert fails on a bare
  `import laya` even in a healthy env. Kernel warm-up (unrecorded state
  prep, same class as the CONFIG shadow replay) runs `import laya.vlm_train`
  before cell 8. No notebook cell was edited.

## CONSOLIDATED FIX LIST (Rafiul, 2026-11-22 ~16:29 ET) — status at receipt
"Fix all and run well so you don't push back after done." Applied at stage
boundaries, verified in this log; run end to end; escalate only on a fix
failing verification twice or a frozen-rule violation.
(1) MMF test tree: archive route in flight (VM staging 5,539+ files and
    growing via 10 chunk workers; 4.42 GB tar ~41% to the pod at check).
    Grid does NOT wait on it; catch-up delta before the test stage.
    HF zip fallback probed: 401 anonymous (gated) — NOT pursued; the HF
    token stays publish-time-only per the prescribed route.
(2) NCP train.json + test.json: DONE — synced to pod, verified on pod:
    train 71,072 / test 7,264 / val 7,024 annotations.
(3) F3: DONE — ablation_test_paired.predictions.jsonl (10,000 lines) at the
    CONFIG candidate path data/reports/ on the pod.
(4) F1: trainer-side groundwork DONE (see F2 entry); cell-28 patch
    (TUNE_FORM="native" + dataset kwarg) applied at the post-selection
    boundary; receipts carry tune_metric_form.
(5) F2: DONE — see deviation entry below.
(6) F4: gold-agreement assert — applied to cell 38 at the post-selection
    boundary (patch pickup; verified then).
(7) F5: watch item for the calibration stage — verified then.
(8) Stream throughput: MEASURED from the pod — single stream 1.88 MB/s
    (per-connection cap); 8 parallel range reads 14.63 MB/s. ESCALATION
    BUILT + VERIFIED: _ParallelRangeReader in visualnews_stream.py
    (12 workers x 8 MiB segments, in-order, bounded window, 120 s stall =
    stream-level failure; falls back to the plain stream if ranges are
    refused). On the real tar: member sequence identical to the plain
    transport (first 60), sustained 19.47 MB/s through tarfile iteration
    -> a full 91.2 GiB pass ~= 84 min. PASS 2 projection is SAFE at this
    rate; no Rafiul decision needed. In-pass measurement will also be
    logged when PASS 1 runs.
(9) hf_space/: DONE — app.py + requirements.txt + README.md synced to
    /workspace/Misinformation/hf_space/ on the pod. HF token: publish-time
    SSH-stdin route to ~/.cache/huggingface/token (600), presence-only
    verification — staged later, at the publish boundary.
(10) Completion standard: full artifact pull-back to
    ~/workspace/misinfo_run/mainrun_artifacts/ + count verification BEFORE
    pod termination; one complete final report.

## DEVIATION — F2 trainer dataset parameter (2026-11-22, swarm audit fix)
- laya_trainer._examples() hardcoded dataset="mmfakebench" in its
  jsonl_example call; the NCP arm would have converted its records under
  the wrong dataset tag. FIXED in both copies (VM
  ~/workspace/misinfo_run/laya_trainer.py and the pod's
  data/workflows/laya_trainer.py + /root/drivers copy): _examples takes
  dataset="mmfakebench"; train_full_finetune / train_lora_finetune /
  select_and_calibrate thread a dataset kwarg (default "mmfakebench" —
  MMFakeBench behavior unchanged).
- Same patch carries the F1 groundwork: _record_form honors explicit id
  suffixes (":native" / ":binary") before criteria counting, a module
  TUNE_FORM switch (default "class4") selects the tune-metric population,
  and _tune_metrics records tune_metric_form in every receipt. Verified:
  MMF forms unchanged (class4/binary); NCP forms separate (native/binary)
  even at CLASS4_CRITERIA=2; py_compile + signature checks pass.

## MILESTONES (2026-11-22 ~16:35-16:37 ET)
- DATA (cell 12) PASS on resume (test tree non-empty; full tree still
  syncing in parallel — staging 8,458/10,000 at last count, archive +
  catch-up transfers running; required complete only at the test stage).
- GATES (cell 14) PASS: token audit 1,400 records, mean 18.07, p95 32,
  max 43, 0.00% over MAX_LEN 1024; round-trip 416 tensors bit-identical.
  Receipt: runs/gates.json. Drive synced 16:35:20 ET.
- BASELINES (cell 16) completed via the notebook's reuse of the verified
  on-disk artifacts (MMF val acc 0.293 / macro-F1 0.2079; VERITE acc
  0.3467 / macro-F1 0.2819).
- GRID (cell 24) STARTED: first config full_rlcd_245 training (step 105 at
  0.9 min, loss 0.7551). One resume fix en route: the grid cell's first
  attempt failed on ModuleNotFoundError (cell 8's sys.path insert had died
  with its kernel) — kernel warm-up now replays the path insert; the cell
  itself is unmodified and nothing had trained.
- Kernel B launched concurrently: stream PASS 1 (base checkpoint) + the
  NCP carve (cells 18/20/22), per the concurrency directive.

## AMENDMENT (d) (Rafiul, 2026-11-22 ~16:37 ET) — FULL SUPPLEMENTARY TIER
- New notebook section §7d SUPPLEMENTARY ABLATIONS after the §7c NCP
  training cells (post-selection patch zone; nothing pre-selection
  changes). 13 configs, each trained -> tune-scored -> printed step by
  step with a running supplementary table:
  (1) HEAD-ONLY arm x {rlcd, soft_ce} x {490, 735} = 4 — head-only
      training in laya_trainer (only the head's parameters trainable;
      encoder + vision frozen; same in-module pattern as _train_soft_ce).
  (2) LoRA rank variants r8 and r32 (alpha = 2r, same targets/dropout)
      at the MMF WINNER's loss x {490, 735} = 4.
  (3) FULL-arm encoder-LR variants 5e-6 and 2e-5 (head LR 1e-3) at the
      winner's loss x {490, 735} = 4 — trainer lr/seed kwargs with
      defaults reproducing canonical behavior exactly.
  (4) SEED CHECK: the winner config retrained with seed 20261123 = 1.
- HARD ISOLATION: supplementary receipts ->
  runs/supplementary/{name}/result.json (depth 3 — outside the canonical
  runs/*/result.json glob); supplementary results NEVER feed selection,
  calibration, or test-once. §16 bundle + §17 complete record must
  include the supplementary table + receipts (patch-zone assembly).
- Budget ~+$1.20-1.45. NEW DESCOPE ORDER if the budget tightens:
  supplementary tier FIRST, then the NCP arm, never the core
  grid/test-once/publish.
- Each supplementary receipt verified as it lands (arm/loss/steps/seed +
  tune_macro_f1 + per-class recall); the supplementary table is its own
  section in the final report.

## MILESTONE (d) — FIRST TUNE F1 (2026-11-22 ~16:41 ET)
- full_rlcd_245: tune macro-F1 = 0.5667 (baseline 0.2079; H1 band was
  0.30-0.42 — the first config already clears the +0.03 gain leg).
- Head-only trainer arm BUILT (amendment d): train_head_only_finetune in
  laya_trainer (library freeze="head"; rlcd via vlm_train.train, soft_ce
  via set_trainable("head") + the CE loop), both copies synced + verified.
- Kernel B pass-1 first attempt errored instantly (LAYA_SOURCE_ROOT is a
  cell-8 variable; B never ran cell 8). Relaunched with the value replayed
  in the warm-up; cell 18 replayed as shadow (its record untouched).

## CHECKLIST (1) DONE — MMF TEST TREE COMPLETE + VERIFIED (2026-11-22 ~17:15 ET)
- Pod test tree: 10,000 annotation rows -> 10,000 image files present,
  0 missing (annotation cross-check on the pod). 12-file sha256 spot-check
  (seeded sample): pod hashes == VM staging hashes, 12/12 match.
- Route taken: Mac->VM staging (10 chunk workers, 10,000/10,000) then
  bulk tar transfers VM->pod (full archive 6,595 + delta 3,405). The HF
  zip fallback was probed and not used (401 anonymous; token kept
  publish-time-only).

## BUDGET WATCH (2026-11-22 ~17:20 ET)
- PASS 1's slow early pace is CPU contention: the training kernel holds
  ~10 cores (data pipeline; GPU only 32%); the stream kernel gets scraps.
  It accelerates when the grid ends; the pass is resume-safe regardless.
- Projection at balance $8.30 (spend $1.53): grid finish ~$0.27; PASS 1
  remainder ~$1.35-1.80 (stream-read floor 84 min + inference); carve
  ~$1.35; NCP training ~$0.36; supplementary ~$1.17; trained eval + test
  ~$0.36; PASS 2 ~$1.35-1.80; calibration/publish/bundle ~$0.36.
  Projected total spend $7.75-8.65 vs the $8 hard stop — TIGHT.
- Pre-authorized descope order (amendment d): supplementary tier FIRST,
  then the NCP arm, never the core. Decision point: when PASS 1 + carve
  complete and the remaining estimate is firm — if projected total >
  $7.60, the supplementary tier is descoped (and reported), per Rafiul's
  standing order. No core stage is at risk.

## AMENDMENT (d) EXTENSION (Rafiul, 2026-11-22 ~17:24 ET) — DATA-SIZE AXIS + ANALYSES
- §7d is now 15 configs: + the WINNER's arm+loss at FIXED 490 steps, seed
  20261122, trained on (a) the first 245 items and (b) the first 122 items
  of the frozen 490-item train set (train-file order, no re-shuffle, both
  question forms per item: 490 / 244 records). The 490-item curve point is
  the grid's own {winner_arm}_{winner_loss}_490 receipt — NOT retrained.
  Receipts -> runs/supplementary/data_245/ and .../data_122/ with
  n_train_items recorded; the supplementary table gains a data-curve row
  set (122 / 245 / 490 items at 490 steps). Same isolation rules.
- Four zero-training analyses fold into the COMPLETE RECORD + final
  report (from saved predictions/logits/checkpoints; a tune re-score of
  an existing checkpoint is inference-only and allowed):
  (1) ERROR GALLERY — winner's tune errors + (post-test) test errors as a
      viewable set (id, gold, predicted, both probabilities, image path).
  (2) OPTION-ORDER ROBUSTNESS — winner re-scored on tune with shuffled
      choice-option order; verdict flip rate beside October's ~35.7%
      base-model figure.
  (3) NOUL ANALYSIS — on the winner's eval populations: fake-noul AUC +
      choice-vs-noul disagreement rate per dataset where available.
  (4) COST TABLE — per-config train seconds + estimated dollars at
      $0.897/hr into final_results_bundle.json.
  Any of the four that cannot be produced from available artifacts is
  named as a deviation in the final report, not improvised.

## COMPLETION STANDARD ADDITION (Rafiul, 2026-11-22 ~17:27 ET) — COST + OPS LEDGER
- The final report AND final_results_bundle.json carry a verified cost +
  operations ledger: (1) per-training rows for all 29 trainings (wall
  seconds, GPU peak memory, host RAM snapshot, cost = s x $0.897/hr);
  (2) per-stage durations incl. both stream passes with measured MB/s and
  byte counts; (3) money ledger — RunPod balance at start ($9.77) vs at
  termination (measured before terminating), total pod spend, pre-run sunk
  costs itemized separately (rehearsal $0.17, pre-grid burn $0.72), Gemini
  spend for THIS run = $0 stated explicitly; (4) operational requirements
  (secure 4090, 50 GB disk + observed peak, CONNECT-proxy SSH, env pins,
  data volumes per leg, total wall GO->terminated). Every figure traces
  to a receipt, log line, or balance read; estimates labelled.
- GPU/RAM SAMPLER STARTED on the pod (2026-11-22 ~17:28 ET): nvidia-smi
  memory.used + utilization and host RAM every 5 s -> /root/gpu_samples.csv.
  Trainings before the sampler started get their peak marked
  sampled-at-eval / not-recorded per the instruction's allowance.
- Pod disk at check: 23G/50G used; workspace 17G.

## GRID COMPLETE + SELECTION (2026-11-22 ~17:52 ET)
| arm | loss | steps | tune macro-F1 |
| full | rlcd | 245 | 0.5667 |
| full | rlcd | 490 | 0.5880 |
| full | rlcd | 735 | 0.6061 |
| full | soft_ce | 245 | 0.5954 |
| full | soft_ce | 490 | 0.6598 |
| full | soft_ce | 735 | **0.7389** |
| lora | rlcd | 245 | 0.4597 |
| lora | rlcd | 490 | 0.4505 |
| lora | rlcd | 735 | 0.1946 |
| lora | soft_ce | 245 | 0.6282 |
| lora | soft_ce | 490 | 0.5726 |
| lora | soft_ce | 735 | 0.7187 |
WINNER: full / soft_ce / 735 — tune macro-F1 0.7389 (runs/winner.json).
Baseline 0.2079 -> +0.531 on tune. Selection on tune only; test untouched.
- Boundary merge DONE: patched notebook (62 cells) + transplanted outputs;
  F1 + cell-28 timing + F4 applied; section 7d (15 configs) and section
  14b analyses inserted; sections 16/17 include supplementary + analyses.
  Kernel C executing the merged file (packs section 7a first); kernel B
  still on PASS 1 (2,273+ rows) then the carve; cells 17/26 outputs get a
  final transplant when B finishes. Balance $8.0060 (spend $1.77).

## LEDGER CORRECTION (2026-11-22 17:54 ET, from Rafiul's RunPod console screenshot)
- Pod TOTAL rate = **$0.90/hr** = compute $0.89/hr + container storage
  $0.007/hr (50 GB). The cost ledger uses $0.90/hr with this split noted
  (supersedes the $0.897/hr API figure used in earlier projections and in
  the analyses cost-table cell, which will be footnoted in the record).
- Pod facts (console-verified): pod u4eixy0wfqbgll "laya-mainrun",
  RTX 4090 1x, 16 vCPU (AMD EPYC 7K62), host memory 41 GB, container
  disk 50 GB, US secure cloud, image
  runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04; uptime
  2h 20m at 17:53 ET (started ~15:33 ET). Screenshot:
  screenshots/runpod_pod_details_2026-11-22_1753ET.png.

## TELEMETRY / WORKLOAD PROFILE (2026-11-22 17:54 ET, Rafiul's console screenshot during PASS 1)
- Container disk 26 GB of 50 GB (53%) — matches the ~25 GB peak projection.
- Host RAM 6.419 GiB of 38.18 GiB (16%).
- CPU load 100% (EPYC 7K62) while GPU sat at 6% utilization /
  3 GiB of 24 GiB VRAM / 27 C / 78 W.
- Workload profile for the ops ledger: the run alternates GPU-bound
  training bursts with CPU-bound stream passes (tar read + image decode)
  on the same pod; stream phases leave the GPU nearly idle.
  Screenshot: screenshots/runpod_telemetry_2026-11-22_1754ET.png.
- Status at the same minute: PASS 1 at 4,538 / 7,024 rows scored
  (accelerating now that the grid freed the CPU); kernel C phase 2
  driver running section 7d (supplementary) cell 30 shadows -> cell.

## STREAM PASS 1 COMPLETE (2026-11-22 ~18:20 ET, kernel B cell 20)
- Accounting (stream_accounting.json): referenced 5,943 unique images ->
  seen 5,943 -> verified 5,943 -> scored 5,943; skipped 0; missing 0.
  Per source (referenced=seen=verified): bbc 876, guardian 2,776,
  usa_today 1,343, washington_post 948. Skip ledger EMPTY (0 lines).
  All 7,024 val rows scored (usable 7,024, error 0, blocked 0).
- Base-checkpoint NCP val (scored n = 7,024 rows): the model collapses
  toward "falsified" (falsified recall 0.945, pristine recall ~0.084) —
  full metrics in paired.metrics.json; accuracy in the record bundle.
  This is the H2 transfer comparison number for the trained NCP arm.
- CARVE (cell 22) ERRORED: FileNotFoundError
  data/raw/NewsCLIPpings/metadata/train.json. Root cause: the loader
  joins merged_balanced annotations with per-split VisualNews caption
  metadata (metadata/{split}.json); only val.json (37 MB) was ever
  synced. Mac holds train.json (352 MB) + test.json (37 MB), but
  files.upload caps at 50 MB — the device route cannot move train.json.
  Fix in progress: the metadata is derived from VisualNews
  origin/data.json (a member of the same tar PASS 1 streamed);
  probing the tar member order to extract just that member pod-side,
  then rebuilding train/test metadata keyed by id and VERIFYING the
  build by reproducing metadata/val.json exactly from the same source.
- Kernel C phase 2 (section 7d) running concurrently: head-only x4 and
  lora_r8_soft_ce_490 receipts landed by ~18:25 ET.
- Balance $7.4071 at ~18:26 ET (spend $2.37 at the corrected $0.90/hr).

## POSITION (2026-11-22 18:16 ET, parent position check)
- Section 7d receipts 5/15: head_rlcd_490 0.2590, head_rlcd_735 0.4899,
  head_soft_ce_490 0.4238, head_soft_ce_735 0.3098,
  lora_r8_soft_ce_490 0.7037. No errors, no retries in section 7d.
- EXECUTING NOW: lora_r8_soft_ce_735 (started ~18:09 ET, right after the
  r8_490 receipt; its dir lands at completion). Remaining order:
  lora_r32_soft_ce_490, lora_r32_soft_ce_735, full_lr5e-6 x{490,735},
  full_lr2e-5 x{490,735}, seed_check (winner @ seed 20261123),
  data_245, data_122 (subsets were written up front; those two
  trainings run LAST in the cell by design). ETA section 7d done
  ~19:10-19:25 ET.
- NCP ARM: the carve did NOT complete — cell 22 errored 18:06 ET
  (metadata/train.json missing); newsclippings_finetune_v1/ on disk is
  the EMPTY directory the cell created before failing. Fix in flight:
  data.json header located in the tar tail (scan running); then build
  + verify metadata, re-run carve (stream-save pass), then cell 28.
  First NCP training realistically ~19:45-20:30 ET. Descope order
  stands if the budget tightens (supplementary first, then NCP arm).

## HF SPACE RE-SYNCED (2026-11-22 ~18:22 ET)
- Parent updated ~/workspace/misinfo_run/hf_space/ (pack questions
  verbatim from runs/packs.json; BEFORE tables carry the run's own
  baselines: MMF val F1 0.2079, test ablation 0.2037, NCP PASS 1
  accuracy 0.5141, VERITE 0.3467; examples/ support in app.py).
  Re-synced to pod /workspace/Misinformation/hf_space/ — app.py md5
  92a80364ee95e4ea305e0d5dd83e5f2e matches the VM copy exactly.
  The older pod copy must NOT be published.
- PUBLISH-STAGE DUTIES (added): (a) fill the Results AFTER section from
  final_results_bundle.json in BOTH app.py RESULTS_MD and README.md
  before pushing (no "AFTER — pending" ships); (b) stage examples/:
  4 MMF VAL items, one per gold class, images + examples.json with
  true captions (VAL only, never test); (c) smoke check includes one
  live predict call on an example.
- PENDING Rafiul decision (do not act): Space serving the NCP pack
  (second checkpoint + dataset selector). Publish structured so the
  MMF path is never blocked by it.
- NOTE: PASS 1 base-model NCP val accuracy = 0.5141 (per the updated
  Space tables; consistent with paired.metrics.json on the pod).

## SPACE DECISION — BOTH PACKS (2026-11-22 ~18:24 ET, Rafiul via parent)
- The Space serves BOTH packs with per-dataset weights ("run on
  changing the weights according to the datasets"), visual
  input->processing->output layout, images visible. Parent rebuilt
  hf_space/app.py as v2 on the VM (pack registry mirroring
  runs/packs.json, verbatim questions for both packs, three-stage
  layout, before/after compare with flip callout + uncertain badge,
  results.json-driven scoreboard, per-dataset examples).
- RE-SYNCED v2 to the pod: app.py md5 af9837546fbf36157253206a16860a78
  matches the VM copy. Never publish an older pod copy.
- UPDATED PUBLISH DUTIES: (1) push BOTH winner repos:
  RafiulHaiderbro/laya-vision-fullft-mmfakebench AND
  RafiulHaiderbro/laya-vision-fullft-newsclippings; (2) write
  results.json (scoreboard_md + after_md + per-pack choice
  temperatures) from final_results_bundle.json; (3) examples:
  examples/mmfakebench/ = 4 VAL items, one per gold class, true
  captions; examples/newsclippings/ = items from the NCP carve/tune
  SAVED images with true captions (never test, never streamed val);
  (4) smoke check = boot + one live predict PER PACK on an example.
- Decision note: SPACE_DESIGN_DECISION_2026-11-22.md.

## CARVE UNBLOCKED — metadata rebuilt pod-side (2026-11-22 ~18:35 ET)
- Located origin/data.json in the tar: header at byte 97,560,363,520,
  size 356,272,348 (the tar's LAST member). Extracted pod-side via
  parallel range reads (16 workers) — no Mac transfer needed.
- Built metadata/train.json (59,876 referenced ids) + test.json (6,147)
  from data.json records, applying the Mac convention transform
  image_path/article_path "./X" -> "visual_news/origin/X".
  Referenced-id coverage: train 59,876/59,876, test 6,147/6,147,
  missing 0. Captions verified identical to the Mac val.json entries;
  the loader consumes only caption/image_path/id (enriched fields in
  the Mac files — entities/title/timestamp — are not read by any run
  code path; noted as a provenance difference, no metric impact).
- VERIFIED through the run's own loader: load_records returns
  train 71,072 / val 7,024 / test 7,264 rows.
- Kernel B resumed at the carve cell (driver B2, shadows 6/10/18);
  the carve stream-save pass is now the NCP critical path, running
  concurrent with section 7d in kernel C2.

## SWARM CATCHES APPLIED (2026-11-22 ~19:08 ET)
- BOOTSTRAP SYMMETRY: ablation file verified on the pod — exactly one
  error row: test:3824, gold textual_veracity_distortion,
  predicted_label null, status "error" (9,999 ok / 10,000). The
  existing ok_pairs filter (status ok on BOTH sides) already excludes
  it symmetrically; cell 40 (merged numbering) is PATCHED before the
  test stage to (a) also require non-null predicted_label on both
  sides, (b) print a symmetry audit naming the excluded ids, and
  (c) record pairing_symmetry {rule, excluded_ids} in
  runs/test_once.json. Chosen rule: EXCLUDE from both sides (the
  audit's recommended option). Local merged copy patched + compiles;
  pod copy patched at the phase-3 boundary before cell 40 executes.
- CARVE KEY DISCIPLINE: the carve cell's records carry exactly
  {id, image, state_text, question, label} — the MMF key union; no
  text_source / image_source anywhere. Will re-verify on the written
  jsonls when the carve lands (282+ images saved at 19:08 ET).
- DRIVE SYNC EVIDENCE: at the next stage boundary (section 7d
  completion — 13/15 receipts at 19:08 ET — or NCP training start),
  sync the executed notebook to Drive WITH a timestamped receipt +
  Drive read-back (modifiedTime/version); same discipline at
  test-once, verdict, and pre-termination boundaries.

## SECTION 7d DATA-AXIS BUG + FIX (2026-11-22 ~19:15-19:35 ET)
- BUG (mine, in the section 7d cell design): the data-axis subset files
  were written into runs/supplementary/data_*/ carrying the records'
  ORIGINAL relative image paths ("../../../raw/...", valid only from
  the protocol dir). The trainer resolves images relative to the train
  file's own dir, so every data-axis training image missed and was
  skipped per-record. The cell produced a 7,053,646-line skip stream
  (1.41 GB of notebook output) and was STOPPED (kernel C2 killed)
  before either data config wrote a receipt. NO garbage receipts exist.
- UNAFFECTED: configs 1-13 (head x4, LoRA r8/r32 x4, encoder-LR x4,
  seed check) trained from the original train file in place — receipts
  valid, including lora_r8_soft_ce_490 = 0.7037.
- FIX: notebook surgery on the pod copy — (1) cell 30's giant stream
  trimmed to head+tail 120 lines with an explicit truncation marker
  (notebook 1.50 GB -> 6.5 MB; the receipts carry the numbers, the
  spam was one repeated message); (2) a completion cell inserted at
  index 31 (all later cells shift +1; bootstrap is now cell 41,
  test-once cell 40, publish cell 57, bundle cell 59, record cell 61)
  that regenerates both subsets with paths rebased to
  "../../../data/raw/...", VERIFIES the first image resolves, trains
  both data configs, and assembles supplementary_table.json + the
  data curve. Driver C3 executing it now.
- Carve note: image count grew slowly under CPU contention with
  section 7d (292 saved by ~19:30 ET); expected to accelerate now.

## SECTION 7d COMPLETE (2026-11-22 ~19:45 ET) — 15/15 receipts
seedcheck_full_soft_ce_735_seed20261123 0.7320 | full_lr2e-5_735 0.7178 |
lora_r8_soft_ce_490 0.7037 | full_lr2e-5_490 0.6871 |
full_lr5e-6_735 0.6438 | lora_r8_735 0.6362 | full_lr5e-6_490 0.6217 |
head_rlcd_735 0.4899 | head_soft_ce_490 0.4238 | data_245 0.3670 |
head_soft_ce_735 0.3098 | head_rlcd_490 0.2590 | lora_r32_735 0.2244 |
lora_r32_490 0.1168 | data_122 0.1168.
DATA CURVE (490 steps, winner recipe): 122 items -> 0.1168 (collapsed
to "original" only), 245 -> 0.3670 (2 of 4 classes), 490 -> 0.6598.
Seed check: winner recipe at seed 20261123 = 0.7320 vs 0.7389 (tight).
- DRIVE SYNC RECEIPT (stage boundary, per swarm steer): merged
  notebook pushed to Drive "Research" (1QGTWMo0cBP5aw5Zm2vUVtrh1Ak__r8j7)
  at 2026-11-22 19:26:04 ET; read-back: modifiedTime
  2026-11-23T00:26:03.737Z, size 6,754,363 bytes (exact match),
  version 45. Same receipt discipline at test-once, verdict, and
  pre-termination boundaries.
- Balance $6.3617 at ~19:47 ET (spend $3.41 at $0.90/hr).
