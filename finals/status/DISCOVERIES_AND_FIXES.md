# Discoveries and Fixes — VisualNews Stream Verifier (INTERIM)

*Interim document, 2026-11-22. Every discovery from the verifier workstream
so far, in the form: **what we found → how we solved it** (or → OPEN).
Classification follows Rafiul's framing: a finding is either an
**(1) INTEGRITY DEFECT** — corrupt / truncated / degenerate / empty; the
verifier skips and ledgers it — or a **(2) DATASET PROPERTY** — a
characteristic of the benchmark itself; not a defect, not a skip reason,
recorded as census. Dataset properties are **never** used as model
features or selection signals (the study's metadata ban: in October, a
source-metadata rule alone scored 0.9150 — that is leakage, not signal).*

*Field evidence base at this writing: a bounded streaming field test over
the official VisualNews `origin.tar`
(`https://www.cs.rice.edu/~vo9/visualnews/origin.tar`, 97,916,641,280
bytes) — a sequential pass over the first 1.67 GB (20,313 members) plus a
250 MB census window at the 30 GB mark (3,031 members); a third window at
65 GB was still streaming when this interim was written. Final numbers
land in `finals/results/VISUALNEWS_FIELD_TEST_2026-11-22.md`.*

---

## D1. A BBC `.jpg` that is actually a GIF

- **Found:** the field stream hit `origin/bbc/images/0241/463.jpg` at tar
  offset 1,084,710,912 — a NewsCLIPpings **val-referenced** image whose
  bytes decode as **GIF**, not JPEG. A second one followed:
  `origin/bbc/images/0093/206.jpg` at offset 1,531,603,968, also GIF.
- **Classification:** DATASET PROPERTY — the file is intact; only its name
  lies.
- **Solved:** no action needed in the verifier and no fix applied to the
  data. The verifier already normalizes **by content**: full PIL decode +
  `convert("RGB")` in memory, so the true format is what reaches the
  model and the extension is never trusted. We explicitly do **not**
  transcode GIF→JPG: re-encoding is lossy, it would break comparability
  with the October baselines (which decoded the same bytes the same way),
  and in a stream-only design a transcoded file has nowhere to live.
  Instead, the census records the **true decoded format** of every
  verified image, plus animated/multi-frame flags (the pipeline judges
  frame 0 of an animated image — a methods note, recorded as D8).

## D2. Format ≠ extension is a population, not an anecdote — ~4.9% of "JPEGs" aren't

- **Found:** in the 30 GB census window, of 3,028 images decoded, only
  2,878 were actually JPEG. The rest: **GIF 83, PNG 64, BMP 2** — all
  named `.jpg`. Combined with the head pass: 151 of 3,106 censused images
  (4.9%) carry a false extension.
- **Classification:** DATASET PROPERTY.
- **Solved:** same as D1 — decode-by-content makes the pipeline
  format-blind in the right way. The census now reports true-format
  counts as a standing characterization of the benchmark. Any tooling
  downstream that filters or dispatches on file extension would silently
  mishandle ~1 in 20 images; nothing in this pipeline does.

## D3. The non-JPEG population clusters in one BBC directory: `images/0455/`

- **Found:** the recorded mismatch examples in the 30 GB window are
  overwhelmingly from a single directory, `origin/bbc/images/0455/`
  (GIF- and PNG-in-.jpg throughout: 564, 589, 407, 227, 304, 349, 438,
  444, 347, 006, 812, 316, 318, 323, 117, 198, 250, 051, 348, 795, 821,
  206, 322, 612, 246, …). Elsewhere in the covered sections the mismatch
  rate is near zero (2 in the first 1.67 GB).
- **Classification:** DATASET PROPERTY — a per-directory quirk of how
  that BBC batch was ingested.
- **Solved:** documented as characterization. Per the metadata ban, the
  clustering is **not** used as a feature, a filter, or a selection
  signal — it is reported so the paper can describe the benchmark
  honestly. Flagged as a paper-worthy characterization finding: format
  hygiene in VisualNews is directory-dependent, not uniform.

## D4. One genuinely undecodable image — the haul's only integrity defect

- **Found:** `origin/bbc/images/0422/267.jpg` (2,959 bytes; probe-window
  offset 97,125,888, absolute ≈ 30,097,254,400) fails a full PIL decode
  outright (`decode_error`). It is the only decode failure in 3,106
  censused images, and it was **not** val-referenced.
- **Classification:** INTEGRITY DEFECT.
- **Solved:** this is exactly the verifier's reason to exist. In the real
  passes, a member that fails full decode is **skipped and entered in
  the skip ledger** with its reason; the pass continues; NewsCLIPpings
  accuracy is computed over the scored n and labelled as such (the
  study's existing missing-row discipline — cf. October's test ablation
  scored over 9,999 of 10,000 usable rows). One defect in ~3.1k images
  (≈0.03%) says the archive is fundamentally healthy.

## D5. Referenced images: 44 for 44 verified clean

- **Found:** every val-referenced member encountered in the covered
  sections — 38 in the head pass, 6 in the 30 GB window — passed full
  verification. Zero referenced skips, zero referenced defects so far.
- **Classification:** negative finding (health evidence).
- **Solved:** nothing to solve; recorded because the real passes'
  expectations should be set by evidence: referenced-image loss to
  integrity defects is tracking at ~0%, so any material skip count in a
  real pass would itself be a signal to investigate, not to accept.

## D6. The archive is source-clustered — BBC fills the first ~30+ GB

- **Found:** all 20,289 file members in the first 1.67 GB are BBC, and
  the entire 250 MB window at the 30 GB mark is BBC too
  (`source_first_seen = [bbc]` in both). Guardian — 2,776 of the 5,943
  val-referenced images (47%) — appears nowhere in the covered sections.
  Referenced density in BBC territory is low: 38 referenced in 20,289
  members (≈0.19%).
- **Classification:** DATASET PROPERTY (archive layout).
- **Solved:** the real passes are designed for it: one full streaming
  pass, no early exit, resume bookkeeping by tar offset, and no
  expectation of uniform referenced density. A partial pass is a BBC
  sample, not a NewsCLIPpings sample — progress reporting must say so.

## D7. Repeated exact file sizes — BBC's tree contains standardized payloads

- **Found:** the smallest member size, **2,959 bytes**, recurs across
  many distinct paths in both windows; the largest, **8,294,454 bytes**,
  appears at three different paths in the head pass alone
  (`0505/692.jpg`, `0491/529.jpg`, `0408/118.jpg`). Exact size repetition
  at this rate indicates standardized payloads (plausibly
  placeholder/derived renditions) inside BBC's tree.
- **Classification:** DATASET PROPERTY (size pattern).
- **Solved:** recorded in the census. Notably, size does **not** predict
  health: the single decode failure (D4) shares the modal 2,959-byte
  size with files that decode fine — so the verifier keeps judging
  bytes, never sizes. No size-based filtering anywhere.

## D8. Animated and multi-frame images — judged on frame 0

- **Found:** the archive contains palette-mode (`P`) images (87
  censused) and `RGBA` images (12) alongside `RGB` (2,976), and
  progressive JPEGs (18). GIF members (D1/D2) raise the animated case:
  a GIF may carry multiple frames.
- **Classification:** DATASET PROPERTY.
- **Solved:** the verifier's decode + `convert("RGB")` normalizes mode
  in memory (palette and RGBA convert cleanly; progressive JPEG decodes
  as ordinary JPEG). For multi-frame images, PIL decodes **frame 0**,
  and frame 0 is what the model judges — stated here as a methods note
  for the paper. The census flags animated members (frame count > 1)
  rather than treating them as defects. No transcoding anywhere (see
  D1).

## D9. Range-restart by tar-header sync works — mid-archive passes are cheap

- **Found:** spot windows at 30 GB and 65 GB were opened by HTTP Range
  request + scanning 512-aligned blocks for a checksum-valid tar header.
  Sync landed at 30,000,128,512 and 65,000,024,576 — effectively
  immediately.
- **Classification:** infrastructure finding.
- **Solved:** this validates the resume/spot-check design for the real
  passes: any section of the 91 GB archive can be re-entered at an
  arbitrary offset without re-streaming from zero, and a crashed pass
  can resume near its last ledgered offset instead of restarting.

## D10. Clean negatives: no name anomalies, duplicates, truncations, or bombs in covered sections

- **Found:** across 23,344 members seen so far — zero duplicate member
  names, zero zero-size members, zero header-vs-bytes size mismatches,
  zero path-normalization surprises (no `./` prefixes, double slashes,
  backslashes, or case variants; every member matches
  `origin/<source>/images/<NNNN>/<N>.jpg`), zero PIL warnings, and a
  modest size ceiling (largest payload 8.3 MB; largest image 3.6 M
  pixels — no DecompressionBomb territory).
- **Classification:** negative findings (health evidence).
- **Solved:** the verifier's normalization rules, written from the
  documented layout, match the real archive as observed. The
  finalization keeps the guards (they cost nothing) and records these
  negatives so a future anomaly is visible against a clean baseline.

## D11. The referenced set itself checks out — exact counts, one shape

- **Found:** building the val-referenced set from the local NewsCLIPpings
  copies (merged_balanced `val.json` annotations → `metadata/val.json`
  image paths) reproduces the expected **5,943** unique images exactly —
  bbc 876 / guardian 2,776 / usa_today 1,343 / washington_post 948 —
  every path of the single shape `origin/<source>/images/<NNNN>/<N>.jpg`,
  every one named `.jpg` (whatever its true format, per D1/D2).
- **Classification:** verification result.
- **Solved:** the verifier's wanted-set construction and the driver's
  member-key derivation agree with the data; matching risk for the real
  passes is confined to the format question, which D1/D2 already settle.

## D12. "VisualNews is already on the Mac" was wrong — the archive was never local

- **Found:** the run's survey of the Mac workspace found the
  `visual_news` tree holds exactly **4 images**, fetched one-by-one for
  an October diagnostic. An earlier working claim that the full tree was
  already on the Mac (so "nothing needs fetching at run time") was
  false; October's NewsCLIPpings numbers came from streamed predictions.
- **Classification:** workstream error (recorded in full in
  `mistakes.md`).
- **Solved:** the plan was rebuilt on the truth: images are consumed by
  streaming the official archive (D9 makes this resumable), nothing is
  stored, and the claim's correction is recorded in the run log and in
  MEMORY so no later session inherits it.

## D13. Extract-to-disk was superseded by stream-only

- **Found:** the first field plan extracted the 5,943 referenced members
  to pod disk (~1–2 GB) from the 91 GB tar.
- **Classification:** design change (Rafiul's directive, 2026-11-22).
- **Solved:** superseded — images are streamed, verified in memory, used,
  and discarded; no VisualNews image file is written to disk at any
  point. Consequence, accepted and documented: consumption is one-pass,
  so the baseline and winner evaluations each pay one full stream pass.

## D14. The stock baseline CLI cannot consume a stream

- **Found:** the workspace baseline CLI loads images from disk paths; it
  has no way to accept an in-memory image from a stream.
- **Classification:** tooling limitation.
- **Solved:** a custom streaming driver (`drivers/stream_ncp.py`) reuses
  the baseline study's own question construction and the same
  `agent.predict` calls, gated by a worker-equivalence check (stock
  worker vs in-process PIL predict must agree to <1e-4 on native
  probabilities) before any stream pass is trusted.

## D15. A hung test server exposed a missing stream timeout

- **Found:** during synthetic testing, querying the local test server
  after shutdown hung the client indefinitely — the stream open had no
  timeout, so a stalled server would hang a real pass forever.
- **Classification:** module defect (test-caught).
- **Solved:** `urlopen` now carries a **120-second inactivity timeout**
  (per-read, not a total-transfer deadline — safe for a 91 GB stream).
  A stalled stream raises, and the caller restarts the pass (D9 makes
  restarts cheap). The verifier raises only on stream-level failures;
  bad members never fail the pass.

---

*Status at this interim: discoveries D1–D15 recorded from the haul so
far. The field test is being wrapped at its current stopping point per
the speed directive; the finalized verifier, the full field report
(`finals/results/VISUALNEWS_FIELD_TEST_2026-11-22.md`), the build log
(`finals/status/VERIFIER_BUILD_LOG.md`), and the mistakes record
(`finals/status/mistakes.md`) follow in the final push.*
