"""VisualNews streaming verifier for the LAYA NewsCLIPpings leg.

The VisualNews origin.tar is consumed in ONE streaming pass over HTTP.
Images are never written to disk: each referenced member is read into
memory, verified with a full PIL decode, handed to the caller's inference
callback, and discarded. Bad images are skipped and ledgered — a bad
member never fails the pass. Only stream-level failures (cannot open,
HTTP error, broken tar stream) raise, so the caller can restart the pass.

Path normalization rule
-----------------------
Tar member names and referenced paths are normalized identically on both
sides before matching:
  1. backslashes -> forward slashes
  2. leading "./" segments stripped (repeatedly)
  3. a leading "origin/" prefix stripped (the VisualNews tar wraps its
     tree in origin/)
Matching is then done on the normalized trailing path (publisher/filename,
e.g. "bbc/<...>/<file>.jpg"). A referenced entry that itself has no
publisher segment still matches by its full normalized path.

Field evidence (2026-11-22, real-archive field test — see
VISUALNEWS_FIELD_TEST_2026-11-22.md): 9,339 images censused across three
windows of the real origin.tar. The archive's payloads are healthy
(exactly 1 decode failure) but its NAMES lie at source-dependent rates:
4.9% of .jpg-named members in the BBC window at 30 GB are actually
GIF/PNG/BMP, vs 0.05% in the guardian window at 65 GB. This module
therefore never consults the extension: every decision is made on the
decoded bytes. Non-JPEG formats, palette/RGBA modes, progressive JPEGs
and animated images are DATASET PROPERTIES (census material), never
skip reasons; only integrity failures skip.
"""

from __future__ import annotations

import io
import tarfile
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from PIL import Image

# Placeholder-integrity rule: a real news photo is never a 1x1-style stub.
# Anything with either side below this is treated as degenerate.
MIN_DIMENSION = 8

# Memory-safety ceiling on DECLARED pixels, checked from the header
# before any decode allocation. Field evidence: the largest image in
# 9,339 censused was 3.6 M pixels, so this ceiling sits ~55x above
# anything the real archive contains and can only fire on a payload
# unlike the real data (corrupt/hostile header). PIL's own
# DecompressionBomb threshold (~89.5 M px) only warns; a stream pass
# should refuse, not warn, before allocating.
HARD_PIXEL_LIMIT = 200_000_000

KNOWN_SOURCES = ("bbc", "guardian", "usa_today", "washington_post")


def normalize_path(name: str) -> str:
    p = name.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    p = p.lstrip("/")
    if p.startswith("origin/"):
        p = p[len("origin/"):]
    while p.startswith("./"):
        p = p[2:]
    return p


def source_of(path: str) -> str:
    """Publisher = first path segment naming a known source, else 'other'."""
    for seg in normalize_path(path).split("/"):
        if seg in KNOWN_SOURCES:
            return seg
    return "other"


def _reason_for_exception(exc: Exception) -> str:
    msg = f"{type(exc).__name__}: {exc}".lower()
    if "truncated" in msg or "premature" in msg or "end of file" in msg \
            or "unexpected end" in msg or "incomplete" in msg:
        return "truncated"
    return "decode_error"


def verify_image_bytes(data: bytes):
    """Full-decode check. Returns (ok, reason, RGB image or None).

    Uses Image.open + load() (a real decode), NOT verify() alone, so
    truncated/corrupt payloads that pass a header sniff still fail.
    """
    if not data:
        return False, "empty_member", None
    try:
        img = Image.open(io.BytesIO(data))
        # Oversize guard (field evidence at HARD_PIXEL_LIMIT): refuse on
        # declared dimensions BEFORE load() allocates the decode buffer.
        if img.width * img.height > HARD_PIXEL_LIMIT:
            return False, "oversize_dimensions", None
        # Full decode. Format is whatever the BYTES say (JPEG/PNG/GIF/BMP
        # all occur behind .jpg names in the real archive); the member
        # name's extension is never consulted. For animated images this
        # decodes frame 0 — frame 0 is what the pipeline judges
        # (methods note, field test D8).
        img.load()
    except Exception as exc:  # noqa: BLE001 - any decode failure is a skip
        return False, _reason_for_exception(exc), None
    if img.width < MIN_DIMENSION or img.height < MIN_DIMENSION:
        return False, "degenerate_dimensions", None
    try:
        # Palette images carrying byte-transparency (present in the real
        # guardian tree; PIL warns "Palette images with Transparency
        # expressed in bytes should be converted to RGBA images" on a
        # direct P->RGB convert, observed on the field test's stderr):
        # route through RGBA first, per PIL's own guidance, so the
        # transparency is handled instead of silently mishandled.
        if img.mode == "P" and "transparency" in img.info:
            img = img.convert("RGBA")
        rgb = img.convert("RGB")
    except Exception as exc:  # noqa: BLE001
        return False, _reason_for_exception(exc), None
    return True, None, rgb


@dataclass
class SkipLedger:
    referenced: int = 0
    seen_in_stream: int = 0
    verified: int = 0
    skipped: int = 0
    missing_from_stream: int = 0
    skips: list = field(default_factory=list)          # [(path, reason)]
    _reason_counts: Counter = field(default_factory=Counter)
    _per_source: dict = field(default_factory=lambda: defaultdict(Counter))

    def note_referenced(self, path: str) -> None:
        self.referenced += 1
        self._per_source[source_of(path)]["referenced"] += 1

    def note_seen(self, path: str) -> None:
        self.seen_in_stream += 1
        self._per_source[source_of(path)]["seen"] += 1

    def note_verified(self, path: str) -> None:
        self.verified += 1
        self._per_source[source_of(path)]["verified"] += 1

    def skip(self, path: str, reason: str) -> None:
        self.skipped += 1
        self.skips.append((path, reason))
        self._reason_counts[reason] += 1
        src = source_of(path)
        self._per_source[src]["skipped"] += 1
        self._per_source[src][f"skip:{reason}"] += 1

    def note_missing(self, path: str) -> None:
        self.missing_from_stream += 1
        self._per_source[source_of(path)]["missing_from_stream"] += 1

    def summary(self) -> dict:
        return {
            "referenced": self.referenced,
            "seen_in_stream": self.seen_in_stream,
            "verified": self.verified,
            "scored_candidates": self.verified,
            "skipped": self.skipped,
            "skip_reasons": dict(self._reason_counts),
            "missing_from_stream": self.missing_from_stream,
            "per_source": {s: dict(c) for s, c in sorted(self._per_source.items())},
        }


def _open_stream(source):
    """Return (fileobj, closer) for a URL, local path, or binary file object.

    Raises on stream-level failure (HTTP error, missing file) — by design.
    """
    if hasattr(source, "read"):
        return source, (lambda: None)
    if isinstance(source, (str,)) and source.startswith(("http://", "https://")):
        req = urllib.request.Request(source, headers={"User-Agent": "laya-stream/1.0"})
        # timeout = inactivity timeout on the socket (per read), NOT a
        # total-transfer deadline — a stalled stream raises so the caller
        # can restart the pass instead of hanging forever.
        resp = urllib.request.urlopen(req, timeout=120)  # raises HTTPError/URLError
        if getattr(resp, "status", 200) >= 400:
            resp.close()
            raise OSError(f"HTTP {resp.status} for {source}")
        return resp, resp.close
    f = open(source, "rb")  # local path; raises if absent
    return f, f.close


def stream_verified(source, referenced, on_image):
    """Stream a tar once, verifying referenced images in memory.

    referenced: set[str] of paths, or dict keyed by path (values ignored).
    on_image(path, PIL.Image) -> prediction record (collected into results).
    Returns (results, ledger). Never raises on a bad member; raises only
    on stream-level failure so the caller can restart the pass.
    """
    ref_paths = list(referenced.keys()) if isinstance(referenced, dict) else list(referenced)
    wanted = {}
    for p in ref_paths:
        wanted.setdefault(normalize_path(p), p)

    ledger = SkipLedger()
    for p in ref_paths:
        ledger.note_referenced(p)

    results = []
    seen_norm = set()
    fileobj, closer = _open_stream(source)
    try:
        # 'r|*' = stream mode, any compression; members must be consumed
        # in order and unreferenced payloads are skipped by the reader.
        with tarfile.open(fileobj=fileobj, mode="r|*") as tar:
            for member in tar:
                if not member.isfile():
                    continue
                norm = normalize_path(member.name)
                original = wanted.get(norm)
                if original is None:
                    # Not referenced: do not read its bytes; in stream
                    # mode tarfile discards the payload as it advances.
                    continue
                seen_norm.add(norm)
                ledger.note_seen(original)
                extracted = tar.extractfile(member)
                data = extracted.read() if extracted is not None else b""
                ok, reason, image = verify_image_bytes(data)
                if not ok:
                    ledger.skip(original, reason)
                    continue
                ledger.note_verified(original)
                record = on_image(original, image)
                results.append({"path": original, "prediction": record})
    finally:
        closer()

    for norm, original in wanted.items():
        if norm not in seen_norm:
            ledger.note_missing(original)

    return results, ledger
