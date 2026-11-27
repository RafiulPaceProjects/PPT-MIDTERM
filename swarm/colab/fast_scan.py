#!/usr/bin/env python3
"""Fast sharded tar scanner for the VisualNews origin archive.

Replaces the tarfile-based collector (which starved the range reader at
~1.5 MiB/s). Each shard owns a byte range, resyncs to a tar header via
magic + header-checksum validation, then parses headers manually and
skips member data arithmetically, reading the stream in 4 MiB blocks
through a prefetching range reader (~1 MiB/s per connection, so
parallelism is the throughput).

Usage: fast_scan.py --shard I --shards N --wanted dest_map.json
dest_map: {normalized_member_path: [dest_file, ...]}
A member is extracted by the shard in whose range its HEADER starts.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import urllib.request

URL = "https://www.cs.rice.edu/~vo9/visualnews/origin.tar"
SEG = 16 << 20
WINDOW = 5


class ShardReader:
    def __init__(self, base, total):
        self.base = base
        self.total = total
        self.pos = 0  # relative to base
        self.buf = bytearray()
        self.segs = {}
        self.lock = threading.Lock()
        self.ex = ThreadPoolExecutor(max_workers=16)
        self.next_fetch = 0
        self._pump()

    def _fetch(self, idx):
        start = self.base + idx * SEG
        end = min(start + SEG, self.total) - 1
        want = end - start + 1
        for attempt in range(4):
            try:
                req = urllib.request.Request(
                    URL, headers={"Range": f"bytes={start}-{end}"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                if len(data) == want:
                    with self.lock:
                        self.segs[idx] = data
                    return
            except Exception:
                pass
            time.sleep(2 * (attempt + 1))
        with self.lock:
            self.segs[idx] = b""

    def _pump(self):
        while self.next_fetch * SEG < self.total - self.base and \
                self.next_fetch < (self.pos // SEG) + WINDOW:
            self.ex.submit(self._fetch, self.next_fetch)
            self.next_fetch += 1

    def read(self, n):
        out = bytearray()
        while n > 0:
            if not self.buf:
                idx = self.pos // SEG
                off = self.pos % SEG
                self._pump()
                while idx not in self.segs:
                    time.sleep(0.05)
                seg = self.segs.pop(idx)
                self.buf = bytearray(seg[off:])
                self.pos += len(self.buf)
            take = min(n, len(self.buf))
            out += self.buf[:take]
            del self.buf[:take]
            n -= take
        return bytes(out)

    def skip(self, n):
        while n > 0:
            if not self.buf:
                idx = self.pos // SEG
                off = self.pos % SEG
                self._pump()
                while idx not in self.segs:
                    time.sleep(0.05)
                seg = self.segs.pop(idx)
                self.buf = bytearray(seg[off:])
                self.pos += len(self.buf)
            take = min(n, len(self.buf))
            del self.buf[:take]
            n -= take


def header_ok(h):
    if len(h) < 512 or h[257:262] != b"ustar":
        return False
    try:
        stored = int(h[148:156].split(b"\0")[0].strip() or b"0", 8)
    except Exception:
        return False
    calc = sum(h[:148]) + 8 * 32 + sum(h[156:512])
    return calc == stored


def parse_name(h):
    name = h[0:100].split(b"\0")[0].decode("utf-8", "replace")
    prefix = h[345:500].split(b"\0")[0].decode("utf-8", "replace")
    if prefix:
        name = prefix + "/" + name
    return name


def parse_size(h):
    raw = h[124:136].split(b"\0")[0].strip()
    if not raw:
        return 0
    if h[124] & 0x80:  # base-256 size (rare)
        return int.from_bytes(h[124:136], "big") & ((1 << 95) - 1)
    return int(raw, 8)


def norm(name):
    n = name.lstrip("./")
    if n.startswith("origin/"):
        n = n[len("origin/"):]
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, required=True)
    ap.add_argument("--shards", type=int, default=3)
    ap.add_argument("--wanted", required=True)
    ap.add_argument("--total", type=int, default=91_000_000_000)
    args = ap.parse_args()

    # exact archive size
    total = args.total
    try:
        req = urllib.request.Request(URL, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            total = int(r.headers["Content-Length"])
    except Exception:
        pass
    span = total // args.shards
    start = args.shard * span
    end = total if args.shard == args.shards - 1 else (args.shard + 1) * span

    wanted = json.loads(Path(args.wanted).read_text())
    reader = ShardReader(start, total)
    found = 0
    seen = 0
    t0 = time.time()
    last_log = t0

    def stream_pos():
        return start + reader.pos - len(reader.buf)

    # resync: scan for a valid header (shard 0 starts at a header)
    if args.shard > 0:
        locked = False
        window = bytearray()
        while not locked:
            chunk = reader.read(1 << 20)
            if not chunk:
                print("shard", args.shard, "EOF during resync", flush=True)
                return
            window += chunk
            for off in range(0, len(window) - 512, 1):
                if window[off + 257:off + 262] == b"ustar" and header_ok(bytes(window[off:off + 512])):
                    # push back: rebuild reader state by discarding up to off
                    del window[:off]
                    locked = True
                    break
            if not locked:
                del window[:-512]
        # prepend the locked window into the reader buffer (its bytes
        # were already pulled from segments; growing buf rewinds the
        # logical position by exactly len(window))
        reader.buf = window + reader.buf
    longname = None
    while True:
        pos = stream_pos()
        if pos >= end and args.shard < args.shards - 1:
            break
        h = reader.read(512)
        if len(h) < 512 or h == b"\0" * 512:
            break
        if not header_ok(h):
            print(f"shard {args.shard}: header check FAILED at {pos}", flush=True)
            break
        size = parse_size(h)
        typeflag = h[156:157]
        name = longname or parse_name(h)
        longname = None
        seen += 1
        data_span = (size + 511) // 512 * 512
        if typeflag == b"L":
            longname = reader.read(size).decode("utf-8", "replace")
            reader.skip(data_span - size)
            continue
        key = norm(name)
        dests = wanted.get(key)
        if dests and typeflag in (b"0", b""):
            data = reader.read(size)
            reader.skip(data_span - size)
            for d in dests:
                p = Path(d)
                if not p.exists():
                    p.parent.mkdir(parents=True, exist_ok=True)
                    tmp = p.with_suffix(".tmp")
                    tmp.write_bytes(data)
                    tmp.rename(p)
            found += 1
        else:
            reader.skip(data_span)
        now = time.time()
        if now - last_log > 60:
            last_log = now
            gb = (stream_pos() - start) / 1e9
            print(f"shard {args.shard}: pos {stream_pos()/1e9:.1f}GB "
                  f"(+{gb:.1f}) members {seen} found {found} "
                  f"rate {gb*1000/max(now-t0,1):.1f} MB/s", flush=True)
    print(f"shard {args.shard}: DONE members {seen} found {found} "
          f"in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
