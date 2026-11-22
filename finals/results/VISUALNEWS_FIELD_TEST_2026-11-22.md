# VisualNews Stream Verifier — Real-Data Field Test

**Date:** 2026-11-22 · **Module under test:** `visualnews_stream.py`
(final version — this test is what finalized it)
**Stream source:** official VisualNews distribution,
`https://www.cs.rice.edu/~vo9/visualnews/origin.tar`
(HEAD-verified before streaming: `200 OK`, `Content-Type:
application/x-tar`, `Content-Length: 97,916,641,280` bytes ≈ 91.2 GiB,
`Accept-Ranges: bytes`, Last-Modified 2022-04-17)

**Classification used throughout (Rafiul's framing):** every finding is
an **(1) INTEGRITY DEFECT** (corrupt / truncated / degenerate / empty —
verifier skips + ledgers it) or a **(2) DATASET PROPERTY** (a
characteristic of the benchmark — census material, never a skip reason,
and never a model feature or selection signal under the study's
metadata ban: in October a source-metadata rule alone scored 0.9150,
which is leakage, not signal).

---

## 1. Method and coverage

One bounded streaming exercise in three windows, wrapped early under
the speed directive once the haul was sufficient — no further segments
were started after that directive.

| Pass | Window (tar offsets) | Bytes read | Time | Members | Images censused |
|---|---|---|---|---|---|
| A — main, sequential from 0 | 512 → 1,673,044,992 | 1,674,220,032 | 660.4 s | 20,313 | 78 (all 38 referenced + every-500th sampling) |
| B — range probe @ ~30 GB | 30,000,128,512 → ~30,250,000,000 | 250,122,752 | 99.7 s | 3,031 | 3,028 (full census) |
| C — range probe @ ~65 GB | 65,000,024,576 → ~65,250,000,000 | 250,020,352 | 107.3 s | 6,239 | 6,233 (full census) |
| **Total** | **3 windows** | **2,174,559,744 (2.22% of the archive)** | **873.6 s streaming** | **29,583** | **9,339** |

- Pass A verified **every** val-referenced member encountered (38) plus
  a 1-in-500 spot census of unreferenced members (40). Passes B and C
  censused **every** image member in their windows (referenced or not).
- Probes B and C were opened by HTTP Range + tar-header checksum sync
  (sync found within ≤129 KB of scanning in both cases) — mid-archive
  entry works as designed.
- The referenced set was built locally from the NewsCLIPpings copies on
  this VM (`merged_balanced/val.json` annotations → `metadata/val.json`
  image paths, keyed exactly as the run's driver keys them) and
  reproduced the expected set **exactly**: **5,943 unique images**
  (bbc 876 / guardian 2,776 / usa_today 1,343 / washington_post 948),
  all of the single shape `origin/<source>/images/<NNNN>/<N>.jpg`.
- Mean throughput observed from this VM (via its egress proxy):
  **≈2.5 MB/s**. See residual risk R1 — this number matters.

## 2. Headline results

- **Referenced integrity: 58 / 58 verified, 0 skips.** Every
  val-referenced member encountered across all three windows (38 + 6 +
  14) passed full decode verification.
- **Exactly one integrity defect in 9,339 censused images (0.011%)** —
  see issue I-1. The archive is fundamentally healthy.
- **~1 in 20 "JPEGs" in BBC territory is not a JPEG** — and the rate is
  ~100× lower in guardian territory. Format hygiene is a per-source,
  per-directory property of this benchmark (P-1…P-3), invisible to
  anything that trusts extensions, and fully handled by
  decode-by-content.

## 3. Issue catalogue — (1) INTEGRITY DEFECTS

### I-1. One undecodable payload — `decode_error` (count: 1)
- `origin/bbc/images/0422/267.jpg`, 2,959 bytes, probe-B window offset
  97,125,888 (absolute ≈ 30,097,254,400). Fails a full PIL decode
  outright. Not val-referenced.
- **Handling (by design):** in a real pass this member is skipped and
  entered in the skip ledger with reason `decode_error`; the pass
  continues; accuracy is computed over the scored n and labelled.
- Rate in census: 1 / 9,339 (0.011%); referenced rate: 0 / 58.

### Nothing else
Zero truncations, zero header-vs-bytes size mismatches, zero zero-size
members, zero degenerate dimensions, zero empty members across all
9,339 censused images and 29,583 members. Negative results are recorded
deliberately: they are the baseline against which a future anomaly is
visible.

## 4. Issue catalogue — (2) DATASET PROPERTIES (census, not defects)

### P-1. Format ≠ extension, at scale (count: 154 of 9,339 censused)
True decoded formats across all windows: **JPEG 9,184 · GIF 85 ·
PNG 67 · BMP 2** — every non-JPEG was named `.jpg`. First found as a
val-referenced BBC image: `origin/bbc/images/0241/463.jpg` @
1,084,710,912 (GIF), then `origin/bbc/images/0093/206.jpg` @
1,531,603,968 (GIF). A GIF→JPG transcode was considered and rejected:
the verifier normalizes by content (full decode + `convert("RGB")` in
memory), so format never reaches the model; re-encoding would be
lossy, would break comparability with the October baselines, and has
nowhere to live in a stream-only design.

### P-2. The mismatch rate differs ~100× by source — PAPER-WORTHY
| Window | Source | Non-JPEG behind `.jpg` | Rate |
|---|---|---|---|
| B (30 GB, full census) | bbc | 149 / 3,028 | **4.92%** |
| A (head, sampled census) | bbc | 2 / 78 | 2.6% |
| C (65 GB, full census) | guardian | 3 / 6,233 | **0.048%** |

Format hygiene in VisualNews is a property of the source's ingestion
pipeline, not of the archive as a whole. Reported as characterization
only — per the metadata ban it is not used as a feature, filter, or
selection signal anywhere.

### P-3. Mismatches cluster by directory — BBC `images/0455/`
Nearly all recorded mismatch examples in window B come from one
directory, `origin/bbc/images/0455/` (25 examples logged before the
example cap: GIF and PNG payloads throughout — 564, 589, 407, 227,
304, 349, 438, 444, 347, 006, 812, 316, 318, 323, 117, 198, 250, 051,
348, 795, 821, 206, 322, 612, 246). The catalogue counts in P-1/P-2 come
from the format counters, not the capped example list.

### P-4. Progressive JPEG is a per-source signature — PAPER-WORTHY
Guardian window: **6,227 / 6,233 images (99.9%) are progressive JPEGs**.
BBC windows: 18 / 3,106 (0.6%). Progressive encoding decodes
identically through PIL, so this has zero pipeline impact — but as
benchmark characterization it is a near-perfect source fingerprint,
which is precisely why the metadata ban matters: properties this
source-separable must never leak into features.

### P-5. Sources ship different renditions — size profiles differ sharply
BBC: largest payload 8,294,454 B; largest image 3,597,750 px.
Guardian: largest payload 105,672 B; largest image 309,504 px.
Guardian's tree holds small web renditions; BBC's holds large
originals. Modes across all windows: RGB 9,236 · P 89 · RGBA 13 — all
normalized by the verifier's RGB conversion.

### P-6. Repeated exact payload sizes (standardized BBC payloads)
The modal smallest size, **2,959 bytes**, recurs across many distinct
BBC paths in both BBC windows; the largest size, **8,294,454 bytes**,
appears at three different paths in window A alone (`0505/692.jpg`,
`0491/529.jpg`, `0408/118.jpg`). Consistent with standardized
(placeholder/derived) payloads inside BBC's tree. Size does **not**
predict health: the single decode failure (I-1) shares the modal
2,959-byte size with files that decode fine. The verifier judges
bytes, never sizes.

### P-7. Animated / multi-frame images — frame 0 is judged
GIF payloads (85 censused) may be animated. The pipeline decodes frame
0 (PIL's default) and frame 0 is what the model judges — recorded here
as a **methods note** for the paper. Multi-frame members are a dataset
property, not a defect. (The field census did not retain per-image
frame counts, so an exact animated rate was not captured before the
wrap directive — see R3.)

### P-8. Palette images with byte-transparency exist (guardian tree)
During window C, PIL emitted `UserWarning: Palette images with
Transparency expressed in bytes should be converted to RGBA images`
from the verifier's convert step (printed twice on stderr; PIL dedups
repeat warnings per location, so the exact occurrence count is not
recoverable — at least one, against 2 P-mode images censused in that
window). A direct P→RGB convert can mishandle that transparency. This
finding drove verifier change V-2 below.

### P-9. Archive layout: sources occupy large contiguous blocks
All 20,289 file members in window A are BBC; all 3,028 in window B are
BBC; all 6,233 in window C are guardian. The archive is laid out in
source blocks (consistent with alphabetical order: bbc … guardian …
then presumably usa_today, washington_post — the latter two were not
reached in the covered windows and that ordering for them is an
inference, labelled as such). Consequences the real passes are built
around: referenced density in BBC territory is low (38 referenced in
20,289 members ≈ 0.19%); a partial pass is a BBC sample, not a
NewsCLIPpings sample; guardian — 47% of all referenced images — sits
deep in the archive.

### Clean negatives (layout & naming)
Across 29,583 members: **zero** duplicate member names, **zero** path
anomalies (no `./` prefixes, double slashes, backslashes, case
variants, or unexpected depth — every member matches
`origin/<source>/images/<NNNN>/<N>.jpg` or its directory entries),
**zero** DecompressionBomb-range images (max 3.6 M px), **zero** PIL
warnings inside the census harness itself.

## 5. Verifier changes made (finalization)

Public API unchanged (`verify_image_bytes` / `stream_verified` /
`SkipLedger`); the main run's driver and the notebook import this file
as the single source. Each change cites its field evidence:

- **V-1 — Oversize guard (new skip reason `oversize_dimensions`).**
  Declared pixel count is checked from the header *before* `load()`
  allocates; above `HARD_PIXEL_LIMIT = 200,000,000` px the member is
  skipped. Evidence: field max was 3.6 M px, so the ceiling sits ~55×
  above anything real and can only fire on a corrupt/hostile header;
  PIL's own bomb threshold merely warns, and a stream pass should
  refuse before allocating, not warn after.
- **V-2 — Palette+transparency conversion route.** P-mode images with
  `transparency` in info now convert via RGBA before RGB, per PIL's
  own guidance. Evidence: P-8's warning on real guardian data.
- **V-3 — Documentation in code.** The module docstring and
  `verify_image_bytes` now record, with the census numbers, why the
  extension is never consulted (P-1/P-2), and that animated images are
  judged on frame 0 (P-7). Behavior was already correct; the evidence
  is now attached to the code it justifies.

## 6. Synthetic re-test (finalized module)

Full suite rebuilt and re-run: the original assertions (7 referenced →
seen 6 → verified 3 → skipped 3 with reasons {truncated 1,
decode_error 1, degenerate_dimensions 1} → missing 1; per-source table
exact) pass identically over **both** transports (local file and
HTTP), plus stream-level failures raise correctly (missing file →
`FileNotFoundError`, HTTP 404 → `HTTPError`). New cases, one per new
rule: GIF payload verifies (N1), animated GIF verifies on frame 0
(N2), BMP payload verifies (N3), palette+transparency verifies with
**no** PIL warning (N4), oversize guard fires under a lowered limit
and the same image verifies under the real limit (N5),
empty/degenerate reasons unchanged (N6). **ALL TESTS PASSED.**

## 7. Residual risks for the real passes

- **R1 — Throughput (flagged prominently).** Observed ≈2.5 MB/s from
  this VM through its egress proxy implies ~10.9 hours per full pass
  at that rate, and the design needs two passes (baseline + winner).
  The pod's direct connection may be much faster — this must be
  measured in the pass's first minutes. If it is not, the proven
  header-sync (P-9/D9 in the discoveries doc) enables parallel
  range-segment streaming as the escalation. Budget decisions belong
  to the run, but they must be made on a measured pod rate, not this
  VM's proxied one.
- **R2 — Unsampled sources.** usa_today (1,343 referenced) and
  washington_post (948) territory was not covered by any window.
  P-2 proves per-source rates vary by ~100×, so their integrity/format
  profile is genuinely unmeasured. The verifier's rules are
  source-agnostic and content-based, so the risk is surprise, not
  mishandling — the first real pass is also their field test, and its
  ledger will show it.
- **R3 — Animated rate unmeasured.** See P-7. Frame-0 judging is
  defined and consistent with the baselines; only the exact animated
  share is unknown.
- **R4 — One-pass semantics.** A member missed through a mid-pass
  stream failure is recoverable only by re-streaming or by a
  range-resume from the last ledgered offset (proven feasible, §1).
  The driver already keeps scored rows on abort and resumes.

---

*Companion documents: `finals/status/DISCOVERIES_AND_FIXES.md`
(interim, commit 01312ab), `finals/status/VERIFIER_BUILD_LOG.md`,
`finals/status/mistakes.md`. Raw field data:
`/tmp/vn_fieldtest_results.json` on the test VM (ephemeral) — all
numbers above are transcribed from it.*
