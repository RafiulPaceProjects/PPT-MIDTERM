# Mistakes & Issues Register — VisualNews / Verifier / Streaming Workstream

*Every issue in this workstream, in the format Rafiul set: **ISSUE →
EVIDENCE → SOLUTION** (or **STATUS: OPEN**). Classification follows his
framing: an **INTEGRITY DEFECT** is skipped + ledgered by the verifier;
a **DATASET PROPERTY** is census material — never a skip reason, never
a model feature (metadata ban: in October a source-metadata rule alone
scored 0.9150 — leakage, not signal). Full field evidence:
`finals/results/VISUALNEWS_FIELD_TEST_2026-11-22.md`; build history:
`finals/status/VERIFIER_BUILD_LOG.md`.*

---

## A. Workstream errors and design reversals

### A1. FALSE CLAIM: "VisualNews images are already on the Mac — nothing to fetch"
- **ISSUE:** An early working claim held that the full VisualNews image
  tree was already in the Mac workspace, so the NewsCLIPpings leg would
  need no fetching at run time.
- **EVIDENCE:** The main-run survey (2026-11-22) found the Mac's
  `data/raw/NewsCLIPpings/visual_news/origin/` tree contains exactly
  **4 images**, fetched one-by-one for an Oct 19 diagnostic
  (`acquisition_manifest.json` in `newsclippings_image_subset_v1`).
  October's NewsCLIPpings full-split numbers (val acc 0.5083, n=7,024)
  came from **streamed predictions**, not local files.
- **SOLUTION:** Plan rebuilt on the truth — images are consumed by
  streaming the official archive (`origin.tar`, 97,916,641,280 bytes,
  HEAD-verified). The correction is recorded in the run log and in
  MEMORY so no later session inherits the false claim.

### A2. SUPERSEDED PLAN: extract referenced images to disk
- **ISSUE:** The first field plan extracted the 5,943 val-referenced
  members from the 91 GB tar to pod disk (~1–2 GB).
- **EVIDENCE:** Rafiul's directive (2026-11-22): images stream in, are
  verified in memory, used, and discarded — nothing saved, to save
  space. The pod's disk (50 GB) also cannot hold the archive itself.
- **SOLUTION:** Stream-only design (`visualnews_stream.py`, tarfile
  stream mode `r|*`). Accepted consequence, documented: consumption is
  one-pass — the baseline and winner evaluations each pay one full
  stream pass. Range-resume from a ledgered offset (proven in the field
  test, sync ≤129 KB of scanning) is the recovery path, not re-reading
  disk.

### A3. TOOLING GAP: the stock baseline CLI cannot consume a stream
- **ISSUE:** The workspace baseline CLI loads images from disk paths;
  it has no way to accept an in-memory image from a stream.
- **EVIDENCE:** Established during run prep (2026-11-22) when the
  stream-only directive (A2) met the CLI's disk-path interface.
- **SOLUTION:** A custom streaming driver reuses the baseline study's
  own question construction and the same `agent.predict` calls, gated
  by a worker-equivalence check (stock worker vs in-process PIL predict
  must agree to <1e-4 on native probabilities) before any stream pass
  is trusted. The verifier module is the single source the driver and
  the notebook import.

---

## B. Module defects (caught by testing, fixed)

### B1. Missing stream timeout — a stalled server hangs the pass forever
- **ISSUE:** `stream_verified` opened HTTP streams with no timeout; a
  stalled or dead server would hang a real pass indefinitely.
- **EVIDENCE:** During synthetic testing, querying the local test
  server after shutdown hung the client with no error. (The hang was a
  test artifact — but it exposed a real missing timeout.)
- **SOLUTION:** `urlopen` now carries a **120-second per-read inactivity
  timeout** (not a total-transfer deadline — safe for a 91 GB stream).
  A stalled stream raises as a stream-level failure and the caller
  restarts/resumes the pass; bad members still never fail the pass.

### B2. Palette + byte-transparency images mishandled by direct P→RGB convert
- **ISSUE:** P-mode images carrying byte-transparency can be silently
  mishandled by a direct `convert("RGB")`.
- **EVIDENCE:** Field test window C (guardian tree): PIL emitted
  `UserWarning: Palette images with Transparency expressed in bytes
  should be converted to RGBA images` from the verifier's convert step
  (printed twice; PIL dedups repeats, so the exact count is
  unrecoverable — at least one occurrence, against 2 P-mode images
  censused in that window; 89 P-mode images across all windows).
- **SOLUTION:** Verifier change V-2 — P-mode images with `transparency`
  in info now convert via RGBA before RGB, per PIL's own guidance.
  Synthetic case N4 verifies the route with **no** PIL warning.

### B3. Oversize / decompression-bomb exposure — PIL only warns
- **ISSUE:** A corrupt or hostile header could declare an enormous
  pixel count; PIL's own DecompressionBomb threshold (~89.5 M px)
  merely warns, after which `load()` would allocate.
- **EVIDENCE:** Design review against the field census: the largest
  real image in 9,339 censused was 3.6 M px — no real payload comes
  anywhere near bomb territory, so a hard pre-decode refusal costs
  nothing on real data.
- **SOLUTION:** Verifier change V-1 — new skip reason
  `oversize_dimensions`: declared pixel count is checked from the
  header *before* `load()`; above `HARD_PIXEL_LIMIT = 200,000,000` px
  (~55× the field maximum) the member is skipped + ledgered. Synthetic
  case N5 proves the guard fires under a lowered limit and the same
  image verifies under the real limit.

---

## C. Real-data integrity defects (field test, 2026-11-22)

*Coverage: 3 windows of the real `origin.tar` — 29,583 members seen,
9,339 images censused, 58 val-referenced members verified.*

### C1. One undecodable payload — `decode_error` (count: 1 of 9,339, 0.011%)
- **ISSUE:** `origin/bbc/images/0422/267.jpg` (2,959 bytes; probe-B
  window offset 97,125,888, absolute ≈ 30,097,254,400) fails a full PIL
  decode outright.
- **EVIDENCE:** Field report §3, issue I-1. Not val-referenced.
- **SOLUTION:** By design — in a real pass this member is skipped and
  entered in the skip ledger with reason `decode_error`; the pass
  continues; accuracy is computed over the scored n and labelled as
  such. Referenced-image loss to integrity defects is tracking at 0%
  (58/58 verified), so any material skip count in a real pass is itself
  a signal to investigate, not accept.

### C2. Defect classes with real-data count ZERO (recorded deliberately)
- **ISSUE:** Truncated members, header-vs-bytes size mismatches,
  zero-size members, degenerate dimensions, empty members: **0 each**
  across all 9,339 censused images and 29,583 members.
- **EVIDENCE:** Field report §3 ("Nothing else") and §4 clean
  negatives.
- **SOLUTION:** None needed. The classes are exercised in the synthetic
  suite (truncated 1, degenerate_dimensions 1 in the 7-referenced
  fixture) so the skip paths are proven; the zero counts are the clean
  baseline against which a future anomaly becomes visible.

---

## D. Real-data dataset properties (census — NOT defects, NOT skips)

### D-P1. Format ≠ extension, at scale (154 of 9,339 censused)
- **ISSUE:** Files named `.jpg` whose bytes are not JPEG. True decoded
  formats across all windows: **JPEG 9,184 · GIF 85 · PNG 67 · BMP 2**
  — every non-JPEG was named `.jpg`.
- **EVIDENCE:** First found as a val-referenced BBC image:
  `origin/bbc/images/0241/463.jpg` @ tar offset 1,084,710,912 is a GIF;
  also `origin/bbc/images/0093/206.jpg` @ 1,531,603,968 (GIF), and
  guardian `.jpg` files decoding as PNG (e.g. `0180/964.jpg`,
  `0063/526.jpg`).
- **SOLUTION:** No fix to the data and none needed in the pipeline —
  the verifier decodes **by content** (full PIL decode +
  `convert("RGB")` in memory), so format never reaches the model and
  the extension is never consulted. A GIF→JPG transcode was considered
  and **rejected**: re-encoding is lossy, breaks comparability with the
  October baselines, and has nowhere to live in a stream-only design.
  The census records each verified image's true format instead.

### D-P2. The mismatch rate differs ~100× by source
- **ISSUE:** BBC window B (30 GB, full census): 149/3,028 non-JPEG
  (4.92%). Guardian window C (65 GB, full census): 3/6,233 (0.048%).
  BBC head sample: 2/78 (2.6%).
- **EVIDENCE:** Field report §4, P-2.
- **SOLUTION:** Documented as benchmark characterization (paper-worthy).
  Per the metadata ban it is never used as a feature, filter, or
  selection signal.

### D-P3. Mismatches cluster by directory — BBC `images/0455/`
- **ISSUE:** Nearly all window-B mismatch examples come from one
  directory, `origin/bbc/images/0455/` (25 examples logged before the
  example cap: GIF and PNG payloads throughout).
- **EVIDENCE:** Field report §4, P-3.
- **SOLUTION:** Census only; counts come from the format counters, not
  the capped example list. Not used as a signal (metadata ban).

### D-P4. Progressive JPEG is a per-source signature
- **ISSUE:** Guardian window: 6,227/6,233 images (99.9%) are
  progressive JPEGs; BBC windows: 18/3,106 (0.6%).
- **EVIDENCE:** Field report §4, P-4.
- **SOLUTION:** None — progressive encoding decodes identically through
  PIL (zero pipeline impact). Recorded as characterization, and as a
  standing warning: properties this source-separable are exactly why
  the metadata ban exists.

### D-P5. Sources ship different renditions
- **ISSUE:** BBC: largest payload 8,294,454 B, largest image 3,597,750
  px. Guardian: largest payload 105,672 B, largest image 309,504 px.
  Modes overall: RGB 9,236 · P 89 · RGBA 13.
- **EVIDENCE:** Field report §4, P-5.
- **SOLUTION:** None needed — the verifier's RGB conversion normalizes
  modes in memory. Recorded as characterization.

### D-P6. Repeated exact payload sizes (standardized BBC payloads)
- **ISSUE:** The modal smallest size, 2,959 bytes, recurs across many
  distinct BBC paths in both BBC windows; the largest size, 8,294,454
  bytes, appears at three different paths in window A alone
  (`0505/692.jpg`, `0491/529.jpg`, `0408/118.jpg`).
- **EVIDENCE:** Field report §4, P-6.
- **SOLUTION:** Census only. Size does **not** predict health — the
  single decode failure (C1) shares the modal 2,959-byte size with
  files that decode fine — so the verifier judges bytes, never sizes.
  No size-based filtering anywhere.

### D-P7. Animated / multi-frame images — frame 0 is judged
- **ISSUE:** GIF payloads (85 censused) may be animated; the pipeline
  decodes frame 0 (PIL's default) and frame 0 is what the model judges.
- **EVIDENCE:** Field report §4, P-7; the rule is also documented in
  the module's `verify_image_bytes`.
- **SOLUTION:** Recorded as a **methods note** for the paper — defined,
  consistent behaviour, not a defect. The exact animated share is
  unmeasured (see OPEN-2).

### D-P8. Archive layout: sources occupy large contiguous blocks
- **ISSUE:** All 20,289 file members in window A are BBC; all 3,028 in
  window B are BBC; all 6,233 in window C are guardian. Referenced
  density in BBC territory is ~0.19% (38 in 20,289); guardian — 47% of
  all referenced images — sits deep in the archive. (Ordering for
  usa_today / washington_post is an inference from alphabetical layout,
  labelled as such.)
- **EVIDENCE:** Field report §4, P-9.
- **SOLUTION:** The real passes are built around it: one full streaming
  pass, no early exit, offset-based resume bookkeeping, and progress
  reporting that never calls a partial pass a NewsCLIPpings sample.

---

## E. Open items

### OPEN-1. Stream throughput on the pod is unmeasured (field report R1)
- **ISSUE:** Observed throughput from the test VM via its egress proxy
  was ≈2.5 MB/s, implying ~10.9 hours per full pass at that rate — and
  the design needs two passes (baseline + winner).
- **STATUS: OPEN** — the pod's direct connection may be much faster;
  the rate must be measured in the first minutes of the first real
  pass and the budget decided on that measurement. Proven escalation
  if it is not faster: parallel range-segment streaming (header-sync
  entry works at arbitrary offsets, D-P8/field report §1).

### OPEN-2. Animated-image rate unmeasured (field report R3)
- **ISSUE:** The field census did not retain per-image frame counts, so
  the exact animated share of the archive is unknown.
- **STATUS: OPEN** (low risk) — frame-0 judging is defined and
  consistent with the October baselines; only the exact share is
  unknown. Measurable in the first real pass's census if wanted.

### OPEN-3. usa_today and washington_post territory unsampled (field report R2)
- **ISSUE:** No field-test window covered usa_today (1,343 referenced)
  or washington_post (948 referenced). D-P2 proves per-source rates
  vary ~100×, so their integrity/format profile is genuinely
  unmeasured.
- **STATUS: OPEN** — the verifier's rules are source-agnostic and
  content-based, so the risk is surprise, not mishandling: the first
  real pass is also their field test, and its skip ledger + per-source
  accounting will show it.

### OPEN-4. One-pass semantics (field report R4)
- **ISSUE:** A member missed through a mid-pass stream failure is
  recoverable only by re-streaming or by range-resume from the last
  ledgered offset.
- **STATUS: OPEN** (accepted design consequence of A2) — mitigated:
  the driver keeps scored rows on abort and resumes; range-resume is
  field-proven.

## PAPERORCHESTRA OPERATOR LESSONS (2026-11-22, noted at Rafiul's instruction)

How the baseline paper was run, what the operator (Muse) did wrong, and the
binding fixes for the final pass. Full requirements:
PAPERORCHESTRA_FINAL_PASS_REQUIREMENTS.md.

### PO-1. Bibliography never seeded
- **ISSUE:** The input bundle carried no dataset/model citations, so the
  paper shipped with 3 references and none for MMFakeBench, VERITE,
  NewsCLIPpings, or LAYA itself.
- **EVIDENCE:** literature_agent_output/citation_map.json holds exactly 3
  entries (Tu 2024 calibration; Qi 2024 SNIFFER; Pedregosa 2011 sklearn).
- **FIX (final pass):** seed a required-references list into the bundle;
  source NewsCLIPpings + LAYA citations via Semantic Scholar — never invent.

### PO-2. Published benchmark numbers not source-checked in the bundle
- **ISSUE:** §4.6 mixes regimes (GPT-4V Standard 51.0 beside LLaVA
  MMD-Agent 49.9; LLaVA Standard is 25.7) because the agent assembled
  published numbers itself.
- **FIX (final pass):** put a verified benchmark table in the experimental
  log; the paper cites the table, not its own search.

### PO-3. Author block left blank
- **ISSUE:** No author details in the bundle → the draft invented
  "Ambitious AI Researcher / AI Research Institute."
- **FIX (final pass):** bundle carries Rafiul Haider, Pace University,
  Analytics Capstone Fall 2026 (CRN 72369), Team 3 names.

### PO-4. Environment and budget not pre-flighted
- **ISSUE:** Run #2 stalled on a missing LaTeX compiler (installed
  mid-run) and on the Gemini key hitting its cap (402, topped up mid-run).
- **FIX (final pass):** pre-flight checklist before launch — toolchain
  present, key balance vs the $10 cap, Semantic Scholar pacing in place.

### PO-5. Run #1 died silently, unmonitored
- **ISSUE:** The first run stopped during Literature Review with no error;
  only an after-the-fact watchdog noticed.
- **FIX (final pass):** liveness monitoring from minute one, alert-only.

### PO-6. Verification was post-hoc, not a gate
- **ISSUE:** Numbers verified (all matched) but the 6 flags were found
  after the PDF existed.
- **FIX (final pass):** pre-delivery gate — citations present and
  claim-matched, byline real, benchmark lines sourced, amendments
  (b)/(c)/(d) disclosed, VERITE local-vs-official phrasing, CI units —
  checked BEFORE delivery, not after.
