# Verifier Build Log — `visualnews_stream.py`

*The build and test history of the VisualNews stream verifier, in
order. Companion documents: `finals/results/VISUALNEWS_FIELD_TEST_2026-11-22.md`
(field evidence), `finals/status/mistakes.md` (issue register),
`finals/status/DISCOVERIES_AND_FIXES.md` (interim discoveries, commit
01312ab). All work 2026-11-22.*

---

## 1. Design (before any code)

Binding decisions the module was built to:

- **Stream-only.** VisualNews images are consumed in one streaming pass
  over the official `origin.tar` over HTTP (tarfile stream mode `r|*`),
  in memory → PIL → inference → predictions recorded → image discarded.
  No VisualNews image file is ever written to disk. Consequence
  accepted up front: one-pass consumption — baseline and winner
  evaluations each cost a full stream pass.
- **Verify before inference.** Every referenced image is verified in
  memory before the model sees it: full PIL decode must succeed and
  dimensions must be non-degenerate.
- **Integrity-only skips.** A bad image is skipped + ledgered and the
  pass moves on. Skips are never based on content, labels, or model
  uncertainty. Skipped rows are written by the driver as
  `status='blocked'` prediction items.
- **Accounting.** Every pass produces `stream_skip_ledger.jsonl` and
  `stream_accounting.json`: referenced → seen → verified (= scored
  candidates) → skipped with reason counts + `missing_from_stream`,
  plus a per-source table. Accuracy is computed over the scored n and
  labelled as such.
- **Defects vs properties.** Findings classify as (1) INTEGRITY DEFECT
  → skip + ledger, or (2) DATASET PROPERTY → documented census, never
  a skip if it decodes, and never a model feature (metadata ban).
- **No GIF→JPG transcode.** The verifier decodes by content +
  `convert("RGB")` in memory, so format never reaches the model;
  re-encoding would be lossy, would break comparability with the
  October baselines, and stream-only has nowhere to store conversions.
  Instead the census records each image's true format and flags
  animated/multi-frame members (model judges frame 0).

## 2. Module v1 built

`visualnews_stream.py` — public API (unchanged through finalization):

- `verify_image_bytes(data)` → `(ok, reason, RGB image)`. Full decode
  via `Image.open` + `load()` (not `verify()` alone, so payloads that
  pass a header sniff but are truncated/corrupt still fail). Reasons:
  `empty_member`, `truncated`, `decode_error`,
  `degenerate_dimensions` (either side < 8 px — placeholder-integrity
  rule, commented as such in code).
- `stream_verified(source, referenced, on_image)` → `(results,
  ledger)`. Source = http(s) URL, local path, or binary file object.
  Never raises on a bad member; raises only on stream-level failure.
- `SkipLedger.summary()` → the accounting dict described above.
- Path normalization applied identically to tar member names and
  referenced paths: backslashes → `/`, leading `./` stripped, the
  `origin/` wrapper stripped; matching on publisher/filename.
- `py_compile` clean on first build.

## 3. Synthetic suite v1 — ALL PASSED

A synthetic tar fixture with known contents, run over **both**
transports (local path and `http://127.0.0.1`) with identical
accounting:

| | Count |
|---|---|
| Referenced | 7 |
| Seen in stream | 6 |
| Verified (scored candidates) | 3 |
| Skipped | 3 — `truncated` 1, `decode_error` 1, `degenerate_dimensions` 1 |
| Missing from stream | 1 |
| Unreferenced members | ignored (bytes never read) |

Per-source table exact. Stream-level failures raise correctly.

## 4. Defect found by testing: missing stream timeout → FIXED

Querying the local test server after shutdown **hung the client
indefinitely** — the stream open had no timeout. The hang itself was a
test artifact (server already down), but it exposed a real defect: a
stalled server would hang a real 91 GB pass forever.

**Fix:** `urlopen` carries a **120-second per-read inactivity timeout**
— per read, not a total-transfer deadline, so a healthy long stream is
unaffected while a stalled one raises and the caller restarts the
pass. (Register: mistakes.md B1.)

## 5. Field test on the real archive

Source HEAD-verified first: `https://www.cs.rice.edu/~vo9/visualnews/origin.tar`
→ 200 OK, `application/x-tar`, 97,916,641,280 bytes (≈91.2 GiB),
`Accept-Ranges: bytes`. The referenced set was built locally from the
NewsCLIPpings copies on the test VM and reproduced the expected set
**exactly**: 5,943 unique images (bbc 876 / guardian 2,776 /
usa_today 1,343 / washington_post 948), all of the single shape
`origin/<source>/images/<NNNN>/<N>.jpg`.

Three windows, wrapped early under the speed directive once the haul
was sufficient:

| Pass | Window | Bytes read | Time | Members | Images censused |
|---|---|---|---|---|---|
| A — sequential from 0 | 512 → 1,673,044,992 | 1,674,220,032 | 660.4 s | 20,313 | 78 (all 38 referenced + every-500th sample) |
| B — range probe @ ~30 GB | 30,000,128,512 → ~30.25 GB | 250,122,752 | 99.7 s | 3,031 | 3,028 (full census) |
| C — range probe @ ~65 GB | 65,000,024,576 → ~65.25 GB | 250,020,352 | 107.3 s | 6,239 | 6,233 (full census) |
| **Total** | | **2,174,559,744 (2.22% of archive)** | **873.6 s** | **29,583** | **9,339** |

- Probes B and C entered mid-archive by HTTP Range + tar-header
  checksum sync (sync found within ≤129 KB of scanning in both cases)
  — arbitrary-offset entry and offset-resume are proven, not assumed.
- **Referenced integrity: 58/58 verified, 0 skips.**
- **Exactly one integrity defect in 9,339 censused images (0.011%)** —
  `origin/bbc/images/0422/267.jpg`, `decode_error`, not referenced.
- Dataset properties catalogued (field report §4, P-1…P-9): format ≠
  extension at scale (154/9,339; BBC ~4.9% vs guardian ~0.05%),
  directory clustering in BBC `images/0455/`, progressive-JPEG source
  signature (guardian 99.9%), per-source rendition profiles, repeated
  standardized payload sizes, animated images, palette+transparency
  images (PIL warning observed live), contiguous per-source archive
  layout. Clean negatives recorded: zero truncations, size mismatches,
  zero-size or degenerate members, duplicate names, or path anomalies.
- Mean throughput from the test VM via its egress proxy: ≈2.5 MB/s —
  flagged as residual risk R1 for the real passes (measure on the pod;
  parallel range-segment streaming is the proven escalation).
- An interim discoveries document (D1–D15, found → solved format) was
  committed mid-test: commit `01312ab`,
  `finals/status/DISCOVERIES_AND_FIXES.md`.

## 6. Finalization — three changes, each with its field evidence

Public API unchanged; the main run's driver and the notebook import
this file as the single source.

- **V-1 — Oversize guard (new skip reason `oversize_dimensions`).**
  Declared pixel count checked from the header *before* `load()`
  allocates; above `HARD_PIXEL_LIMIT = 200,000,000` px the member is
  skipped. Evidence: field maximum was 3.6 M px, so the ceiling sits
  ~55× above anything real and can only fire on a corrupt/hostile
  header; PIL's own bomb threshold merely warns, and a stream pass
  should refuse before allocating, not warn after.
- **V-2 — Palette+transparency conversion route.** P-mode images with
  `transparency` in info convert via RGBA before RGB, per PIL's own
  guidance. Evidence: the `UserWarning` observed on real guardian data
  during window C (register: mistakes.md B2).
- **V-3 — Documentation in code.** The module docstring and
  `verify_image_bytes` now record, with the census numbers, why the
  extension is never consulted (P-1/P-2) and that animated images are
  judged on frame 0 (P-7). Behaviour was already correct; the evidence
  is now attached to the code it justifies.

## 7. Synthetic re-test of the finalized module — ALL TESTS PASSED

- The original assertions (7 referenced → seen 6 → verified 3 →
  skipped 3 {`truncated` 1, `decode_error` 1, `degenerate_dimensions`
  1} → missing 1; per-source table exact) pass identically over both
  transports (local file and HTTP).
- Stream-level failures raise correctly: missing file →
  `FileNotFoundError`; HTTP 404 → `HTTPError`.
- New cases, one per new rule:
  - **N1** — GIF payload verifies.
  - **N2** — Animated GIF verifies on frame 0.
  - **N3** — BMP payload verifies.
  - **N4** — Palette+transparency image verifies with **no** PIL
    warning (V-2).
  - **N5** — Oversize guard fires under a lowered limit; the same
    image verifies under the real limit (V-1).
  - **N6** — Empty/degenerate reasons unchanged.

## 8. Handoff state

- Final module: `finals/code/visualnews_stream.py` (247 lines,
  `py_compile` clean).
- Field report: `finals/results/VISUALNEWS_FIELD_TEST_2026-11-22.md`.
- Issue register: `finals/status/mistakes.md`.
- Residual risks carried into the real passes (field report §7):
  **R1** pod throughput unmeasured; **R2** usa_today /
  washington_post territory unsampled — first real pass is their field
  test; **R3** animated rate unmeasured (frame-0 rule defined);
  **R4** one-pass semantics, mitigated by proven range-resume.
- Raw field data (`/tmp/vn_fieldtest_results.json`, pass log) lived on
  the test VM's ephemeral `/tmp` and is gone; every number in the
  field report and this log was transcribed from it before the wrap.
