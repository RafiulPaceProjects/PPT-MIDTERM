# Pseudocode for the study codebase's important components

Each block below is a faithful compression of the real code named in
its header: same steps, same order, same constants, no invented steps.
The paper's code appendix (Appendix D) carries the same blocks; this
document is the standalone copy. Two of the four components belong to
the reported v1 study; two are v2 additions built after the study
closed and are labelled as such wherever they appear.

---

## 1. The VisualNews stream verifier (v1, part of the reported study)

**What this is:** the only route by which NewsCLIPpings evaluation
images reach the model. The VisualNews archive (91 GB) is streamed
once over HTTP; images are never written to disk. Member names in the
archive lie at source-dependent rates (payloads behind `.jpg` names
are sometimes GIF/PNG/BMP), so every decision is made on the decoded
bytes, never on the extension. Only integrity failures skip; dataset
properties (non-JPEG payloads, palette/RGBA modes, progressive JPEGs,
animated images) never do.

**Where the real code lives:** `finals/code/visualnews_stream.py`
(`verify_image_bytes`, `stream_verified`, `SkipLedger`,
`_ParallelRangeReader`).

```
function verify_image_bytes(data):          # -> (ok, reason, image)
    if data is empty:
        return (False, "empty_member", None)
    try:
        img <- PIL open(data)      # format read from the bytes,
                                   # never from the member name
        if img.width * img.height > HARD_PIXEL_LIMIT:  # 200,000,000
            return (False, "oversize_dimensions", None)
                                   # refuse on declared dimensions
                                   # BEFORE allocating a decode buffer
        img.load()                 # full decode, not a header sniff:
                                   # truncated payloads that pass
                                   # open() fail here. For animated
                                   # images this decodes frame 0,
                                   # which is what the pipeline judges.
    except any error e:
        return (False, reason_of(e), None)
                                   # "truncated" if the error reports
                                   # truncation, else "decode_error"
    if img.width < MIN_DIMENSION or img.height < MIN_DIMENSION:  # 8
        return (False, "degenerate_dimensions", None)
    if img.mode is palette and it carries byte transparency:
        img <- img.convert("RGBA") # per PIL's own guidance, so the
                                   # transparency is handled, not lost
    return (True, None, img.convert("RGB"))


procedure stream_verified(source, referenced, on_image):
    wanted <- { normalize(p) : p  for p in referenced }
    ledger <- new SkipLedger
    ledger.note_referenced(each referenced path)
    stream <- open_stream(source)          # see range reader below
    seen <- {}
    for member in tar_stream(stream, mode = "r|*"):
                                   # one pass, members consumed in
                                   # archive order; "r|*" is tarfile
                                   # stream mode, any compression
        if member is not a regular file: continue
        original <- wanted.get(normalize(member.name))
        if original is absent: continue    # unreferenced: the payload
                                   # is never read; the stream reader
                                   # discards it as it advances
        seen.add(normalize(member.name))
        ledger.note_seen(original)
        data <- read member payload (empty bytes if none)
        (ok, reason, image) <- verify_image_bytes(data)
        if not ok:
            ledger.skip(original, reason); continue
        ledger.note_verified(original)
        results.append({ path: original,
                         prediction: on_image(original, image) })
    for each referenced path never seen in the stream:
        ledger.note_missing(path)
    return (results, ledger.summary())
    # summary(): referenced / seen_in_stream / verified / skipped
    # counts, skip-reason counts, missing_from_stream, and the same
    # accounting per source (bbc, guardian, usa_today,
    # washington_post, other). A bad member never raises; only
    # stream-level failure (cannot open, HTTP error, broken tar
    # stream, stall) raises, so the caller can restart the pass.

normalize(p):  backslashes -> "/"; strip leading "./" segments
    (repeatedly); strip a leading "/" and a leading "origin/"
    prefix. Applied identically to tar member names and to
    referenced paths before matching.

open_stream(source):  an open file object is used as-is; a local
    path is opened directly; a URL is fetched through the parallel
    range reader below, falling back to a plain single stream if
    the server does not honour Range requests. Plain-stream socket
    reads carry a 120 s inactivity timeout (per read, not a total
    deadline): a stalled stream raises instead of hanging.

parallel range reader (the URL transport inside open_stream):
    probe with a 1-byte Range request; if the server answers 206
    with a Content-Range total, split the resource into 8 MiB
    segments; 12 worker threads fetch segments ahead (at most 24
    buffered, about 192 MiB) while read() serves bytes strictly in
    order from the segment buffer; each segment is retried up to
    3 times; a segment that still fails, or 120 s without a segment
    becoming available, raises OSError -- a stream-level failure
    under the same restart-the-pass contract.
```

---

## 2. The parallel stream engine and its equivalence gate (v1)

**What this is:** the engine that executed the NewsCLIPpings trained
arm's streamed validation pass (PASS 2). The serial pass was bounded
by a single sequential tar traversal, so the pass was restarted on a
parallel engine under an owner decision, with an equivalence gate
that had to pass before the parallel numbers could be trusted. The
measurement procedure is identical to the serial engine's: same
verifier semantics, same checkpoint, same pack questions, same
temperatures, same prediction call, same row schema. Only execution
concurrency changed.

**Where the real code lives:** `finals/code/parallel_stream_engine.py`
(the worker processes) and `finals/code/parallel_gate_cell.py` (the
orchestration `run_ncp_stream_parallel` and the gate, exported from
the executed notebook cell).

```
procedure run_parallel_pass(pack, checkpoint, rows, out_dir):
    groups <- rows grouped by image member (one image, many rows)
    saved  <- prediction rows already in out_dir (resume support)
    done   <- ids of saved rows with status ok
    start processes under the SPAWN context (never fork: CUDA
    cannot be re-initialised in a forked subprocess):
        1 reader process, 6 decode processes, 4 inference processes
        queues: byte_q (reader -> decoders), img_q (decoders ->
        inferers), evt_q (everyone -> coordinator)

    reader process:
        stream the tar once, in archive order, through the range
        reader; for each member whose normalised name is wanted
        and not yet sent, emit a "seen" event and put
        (path, payload bytes) on byte_q; at end of stream, signal
        reader_done (on stream failure, signal aborted instead)

    decode process (x6):
        loop: take (path, bytes) from byte_q (stop on sentinel)
            (ok, reason, image) <- verify_image_bytes(bytes)
            if not ok: emit skip(path, reason)
            else: emit verified(path); put (path, image relayed as
                  lossless PNG bytes) on img_q
        signal decode_done

    inference process (x4):
        load the checkpoint once; worker 0 also reports the runtime
        identity (checkpoint, device, temperatures)
        loop: take (path, image) from img_q (stop on sentinel)
            for each row of this image whose id is not in done:
                predict with the pack's questions and temperatures
                emit the item record on evt_q (status ok; blocked
                if the row's text is missing; error, with the
                exception counted, if predict raises)
        signal infer_done

    coordinator (this process; the single writer):
        consume evt_q: update the SkipLedger from seen / verified /
        skip events; append each item record to
        paired.predictions.jsonl, never writing an id that is
        already saved; when reader_done arrives, send stop
        sentinels to the decoders; when all decoders report done,
        send stop sentinels to the inferers; finish when all
        inference workers report done
        dead-worker guard: if every inference process has exited
        without reporting done, abort loudly -- the pipeline can
        never finish; likewise if all processes exit before their
        completion signals
    on abort: raise; scored rows stay on disk and the next run
        resumes from them
    reconciliation (only when not aborted): every member the
        verifier skipped, and every member missing from the stream,
        gets explicit blocked rows for its unscored rows (reason:
        stream_verifier_skip:<reason> or member_not_in_stream), so
        every referenced row is accounted for exactly once; then
        the serial tail computes metrics and the per-source
        accounting from the completed prediction file

equivalence gate (runs before the full parallel pass):
    shared <- items scored by BOTH the preserved serial partial
              and a parallel run limited to the serial-scored
              members (the serial file order is tar order, so the
              gate reads the tar head only)
    require |shared| >= 100
    require predicted labels identical on every shared item
    require max |p_parallel - p_serial| <= 0.001 over shared items
    any failure -> abort the restart and resume the serial pass
    executed run: 120 shared items, zero label mismatches, zero
    measured probability drift -- the gate passed, and the parallel
    pass produced the reported PASS 2 file
```

---

## 3. EvidenceGate state machine (v2 addition -- not part of the v1 study)

**What this is:** a pluggable component, built after the v1 study
closed for the v2 probe, that wraps the v1 paired judgement with a
routing decision: judge the pair alone, or retrieve external
evidence first and judge with it. Detached (`mode = off`) it is
behaviour-identical to the v1 pipeline. No v1 result uses it.

**Where the real code lives:** design specification in
`v2_probe/EVIDENCEGATE_DESIGN.md` section 4 (states, guards, trigger
math, RETRIEVE internals, registered questions); probe
implementation in the v2 probe scripts.

```
EvidenceGate: a per-item state machine around the v1 judgement.
The gate config lives in the pack: mode in {off, on, auto}.

    INTAKE    item + pack config + checkpoint enter; the image is
              verified under the stream discipline of block 1
    ROUTE     the routing decision is computed and recorded, with
              its reason
    PAIR_ONLY the v1 judgement: pack questions verbatim,
              caption-only context. In mode auto its verdict is
              provisional until the trigger is evaluated.
    RETRIEVE  the retrieval pipeline below produces the item's
              frozen evidence bundle
    JUDGE     the model judges image + caption + evidence context
              with the registered evidence questions
    ARBITRATE the v1 arbitration rule: the choice verdict
              headlines; choice/noul disagreement -> "uncertain"
    DONE      terminal: exactly one output record for the item
    ABSTAIN   terminal, unscored: integrity skip or unrecoverable
              model failure; counted in the run accounting.
              Distinct from "uncertain", which is a scored outcome
              produced by arbitration.

    transitions and guards:
      INTAKE -> ROUTE        image verified; pack + gate config load
      INTAKE -> ABSTAIN      image fails verification (skip
                             ledgered), or pack/checkpoint unloadable
      ROUTE -> PAIR_ONLY     mode off (reason pack_off), or mode
                             auto (the pair runs first, as the
                             trigger's input)
      ROUTE -> RETRIEVE      mode on (reason pack_on)
      PAIR_ONLY -> ARBITRATE mode off; or mode auto and the trigger
                             does not fire (reason certain). The
                             pair-only verdict is the headline.
      PAIR_ONLY -> RETRIEVE  mode auto and the trigger fires
                             (reason margin or disagreement). The
                             provisional pair-only verdict is kept
                             in the record as the control.
      RETRIEVE -> JUDGE      bundle assembled with at least one
                             selected passage (reason evidence_found)
      RETRIEVE -> ARBITRATE  bundle empty or unusable (no results,
                             all excluded, or transport failure):
                             the pair-only control verdict headlines
                             (in mode on the control pass always
                             runs, so it exists); trace flagged
      JUDGE -> ARBITRATE     always; headline = evidence verdict
      ARBITRATE -> DONE      always
      any -> ABSTAIN         predict raises, or the snapshot hash
                             check fails on a bundle about to be
                             judged (never judge on unverified
                             evidence)

    trigger math (mode auto): the pair-only pass returns the
    choice distribution P and the noul fake probability q.
      margin       = largest P - second-largest P
      disagreement = (the choice headline is on the pack's
                     fake-side labels) != (q >= 0.5)
      RETRIEVE fires iff margin < 0.20 or disagreement
      (0.20 and 0.5 are registered knobs, frozen before results;
      the trigger measurements are recorded in every item's state
      trace whether or not retrieval fires)

    RETRIEVE internals (five steps; the search index is transport
    only -- it fetches, it does not rank, select, or decide):
      1. extraction (deterministic): named entities plus noun
         chunks from the caption; variant A queries are built from
         these spans by a fixed template -- same caption, same
         queries, forever
      2. harness query expansion: a small model returns a one-line
         claim restating the caption and 2-3 further queries
         (variant B); it never sees gold labels or the image, and
         the claim text is used for queries only -- it is never
         placed inside the judge's evidence block
      3. transport: both variants' queries issued to the search
         index (20 s per-query timeout); results unioned and
         deduplicated by URL; every result, used or not, is
         written into the snapshot with URL, title, snippet,
         engine, timestamp, query, and variant
      4. triage: fact-check domains on the versioned contamination
         list and the item's own source article are excluded from
         the headline pools (kept in the snapshot, counted);
         results that merely repeat the caption's own claim are
         down-ranked, not deleted (the repetition trap: the claim
         echoing itself is not independent evidence), and
         near-duplicate clusters collapse to their best member;
         survivors are ordered by whether they bear on the claim's
         checkable content (the named people, places, events,
         dates)
      5. selection + freeze: the top 5 passages (at most 600
         characters each) are selected in triage order and packed
         under the token budget; the bundle is written to disk and
         SHA-256 hashed -- from this moment the item's evidence
         is fixed
```

---

## 4. The retrieval repair loop (v2 addition -- not part of the v1 study)

**What this is:** the repair pass for a v2 instrument failure. The
concurrent batch retrieval runs (up to about 23 simultaneous query
streams) tripped the search engine's "unusual traffic" suspension,
and the search layer silently returned empty result lists for most
item-variants; those empty lists were recorded as if they were
retrieval results. The repair re-runs only the failed pairs,
serially and at a disciplined rate. Nothing about the items changed:
same frozen query lists, same date and contamination rules.

**Where the real code lives:** `v2_probe/repair_retrieval.py`
(diagnosis in its docstring; outcomes in the probe REPORT.md).

```
procedure repair_retrieval(items, raw_in, harness_in, raw_out,
                           harness_out, variants, sleep = 1 s):
    repair_list <- every (item, variant) whose recorded pool
                   size is 0
    new_raw     <- all raw records except stale repair records
                   for pairs in repair_list (untouched pairs are
                   copied through verbatim; the original files
                   remain as the pre-repair record)
    streak <- 0
    for each (item, variant) in repair_list:
        pool <- {}
        for q in the item's frozen query list (unchanged):
            results <- search(q)     # one query at a time; up to
                                     # 3 attempts, waiting between
            if results is empty:
                streak <- streak + 1
                if streak reaches 10:        # circuit breaker
                    sleep 240 s              # engine suspension:
                    streak <- 0              # pause, then resume
            else:
                streak <- 0
            for each result, in rank order:
                build its record (query, rank, URL, title, snippet,
                engine, score, published date, fact-check-domain
                flag, self-hit flag, timestamp, repair flag set)
                append the record to new_raw
                keep the best-scoring record per URL in pool
            sleep 1 s                # the disciplined serial rate
        pool_list <- pool values, best score first
        record the item's new pool size for this variant
        try: re-run triage and passage selection on pool_list;
             store the triage record and both passage sets
             (headline: fact-check excluded; second set: included)
        on failure: store the error, empty passage sets, count it
        mark the item repaired, with the repair timestamp
        flush()                      # per-pair checkpoint: both
                                     # output files are rewritten
                                     # atomically after every pair,
                                     # so a stopped run loses nothing
                                     # (the first repair chain lost
                                     # its end-of-run output exactly
                                     # because it saved only at the
                                     # end; this flush is the fix)
    flush()
    write the run statistics (pairs repaired, harness call counts
    and failures, balance before / after, spend)
    # pairs still empty after the repair are reported downstream
    # as RETRIEVAL-FAILED -- a different state from a genuine
    # no-evidence item, whose search ran and found nothing usable
```
