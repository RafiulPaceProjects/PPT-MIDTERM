# ===== PARALLEL STREAM ENGINE + EQUIVALENCE GATE (owner decision 2026-11-22 20:39 ET) =====
# PASS 2 restarts on a parallel engine. The measurement procedure is
# IDENTICAL to the serial engine (§5): same visualnews_stream verifier
# semantics (full PIL decode, integrity-only skips, SkipLedger
# accounting), same checkpoint, same pack questions, same predict call,
# same row schema, same reconciliation/metrics tail. Only execution
# concurrency changes: single tar reader -> multiprocess decode/verify
# pool -> parallel inference replicas -> ONE writer (this process).
# Workers live in a module file (written by this cell) and are SPAWNED:
# torch forbids CUDA in forked subprocesses ("Cannot re-initialize CUDA
# in forked subprocess") — the first fork-based attempt died on exactly
# that; spawn starts clean interpreters.
import io, json, os, sys, time
import multiprocessing as mp
from collections import Counter
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
WS = Path(WORKSPACE)
from baseline_study.config import load_config, sha_file, signature
from baseline_study.datasets import load_records
from baseline_study.metrics import score_records
from visualnews_stream import normalize_path, SkipLedger

SOURCES_NCP = ("bbc", "guardian", "usa_today", "washington_post")

_ENGINE_MODULE = '''
import io, time
from visualnews_stream import verify_image_bytes, normalize_path, _ParallelRangeReader

def reader_main(tar_url, wanted_norms, byte_q, evt_q):
    try:
        fileobj = _ParallelRangeReader.open(tar_url)
        seen_once = set()
        import tarfile
        with tarfile.open(fileobj=fileobj, mode="r|*") as tar:
            for member in tar:
                if not member.isfile():
                    continue
                norm = normalize_path(member.name)
                original = wanted_norms.get(norm)
                if original is None:
                    continue
                evt_q.put(("seen", original))
                if norm in seen_once:
                    continue
                seen_once.add(norm)
                extracted = tar.extractfile(member)
                data = extracted.read() if extracted is not None else b""
                byte_q.put((original, data))
                if len(seen_once) >= len(wanted_norms):
                    break
    except Exception as exc:
        evt_q.put(("aborted", repr(exc)))
    finally:
        evt_q.put(("reader_done", None))

def decode_main(byte_q, img_q, evt_q):
    while True:
        msg = byte_q.get()
        if msg is None:
            break
        original, data = msg
        ok, reason, image = verify_image_bytes(data)
        if not ok:
            evt_q.put(("skip", original, reason))
            continue
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        evt_q.put(("verified", original))
        img_q.put((original, buf.getvalue()))
    evt_q.put(("decode_done", None))

def infer_main(img_q, evt_q, worker_idx, checkpoint, vcfg, questions, groups,
               labels, done_ids, run_id):
    import torch
    import laya
    from PIL import Image
    from baseline_study.engine import decode_answers, validate_prediction
    agent = laya.load_vlm(checkpoint, device=vcfg["device"], dtype=vcfg["dtype"],
                          max_len=vcfg["max_len"], head_max_len=vcfg["head_max_len"])
    if worker_idx == 0:
        evt_q.put(("identity", {"checkpoint": checkpoint, "device": str(agent.device),
                                "temperature": [float(x) for x in agent.temperature],
                                "transport": "parallel engine (spawn workers): visualnews_stream verified RGB (PNG relay, lossless)"}))
    while True:
        msg = img_q.get()
        if msg is None:
            break
        original, png = msg
        image = Image.open(io.BytesIO(png)).convert("RGB")
        for row in groups[original]:
            if row["id"] in done_ids:
                continue
            item = {k: row[k] for k in ("id", "dataset", "split", "partition", "gold", "group_id")}
            item.update(run_id=run_id, branch="paired", status="blocked",
                        predicted_label=None, probabilities=None, fake_probability=None)
            start = time.monotonic()
            try:
                if not (row["text"] or "").strip():
                    raise LookupError("Required text is missing")
                state = {"context": row["text"] or "", "image": image}
                with torch.inference_mode():
                    result = agent.predict(
                        state, questions, n_permutations=vcfg["n_permutations"],
                        batch_size=vcfg["batch_size"], prefix_cache=vcfg["prefix_cache"],
                        temperature=vcfg["temperature"], strict=vcfg["strict"])
                item.update(decode_answers(result, labels))
                item["status"] = "ok"
                validate_prediction(item, labels)
                item["abstained"] = False
            except LookupError as exc:
                item.update(status="blocked", reason=str(exc))
            except Exception as exc:
                evt_q.put(("predict_error", type(exc).__name__))
                item.update(status="error", reason=repr(exc))
            item["seconds"] = round(time.monotonic() - start, 4)
            evt_q.put(("item", item))
    evt_q.put(("infer_done", None))
'''
(WS / "data/workflows/parallel_stream_engine.py").write_text(_ENGINE_MODULE)
sys.path.insert(0, str(WS / "data" / "workflows"))
import parallel_stream_engine as pse

# ---------------- the parallel pass (serial semantics, parallel execution) ----------------
def run_ncp_stream_parallel(pack, checkpoint, out_rel, limit_keys=None, n_decode=6, n_infer=4):
    output = WS / out_rel
    output.mkdir(parents=True, exist_ok=True)
    print(f"now serving (PARALLEL engine): newsclippings / weights: {checkpoint}")
    LABELS_NCP = tuple(pack["labels"])
    NEGATIVE_NCP = pack.get("binary_negative", ["pristine"])
    overrides = [
        "sampling.per_class=null", "sampling.limit=null",
        f'vision.python="{sys.executable}"',
        f"vision.checkpoint={json.dumps(checkpoint)}",
        f'vision.source_root="{LAYA_SOURCE_ROOT}"',
        'vision.device="cuda"', 'vision.dtype="bf16"',
    ]
    config, bank = load_config(WS / "data/workflows/baseline_study/study.json", overrides)
    rows = load_records("newsclippings", config["datasets"]["newsclippings"], "val")
    images_root = Path(config["datasets"]["newsclippings"]["images"])
    q = pack["questions"]
    vcfg = config["vision"]

    def member_key(row):
        rel = Path(row["image_path"]).relative_to(images_root)
        parts = rel.parts
        if parts[0] == "visual_news":
            rel = Path(*parts[1:])
        return str(rel)

    groups = {}
    for row in rows:
        groups.setdefault(member_key(row), []).append(row)
    if limit_keys is not None:
        groups = {k: v for k, v in groups.items() if k in limit_keys}
    print(f"rows={sum(len(v) for v in groups.values())} unique_images={len(groups)}", flush=True)

    pred_path = output / "paired.predictions.jsonl"
    saved = {}
    if pred_path.exists():
        for line in pred_path.read_text().splitlines():
            if line.strip():
                item = json.loads(line)
                saved[item["id"]] = item
    done_ids = {rid for rid, it in saved.items() if it.get("status") == "ok"}
    print(f"resume: {len(done_ids)} rows already scored", flush=True)

    run_id = signature({"method": "visualnews-stream-v2-parallel", "config": config,
                        "questions_sha256": sha_file(config["questions_file"])})

    ledger = SkipLedger()
    for p in groups:
        ledger.note_referenced(p)
    wanted_norms = {}
    for p in groups:
        wanted_norms.setdefault(normalize_path(p), p)

    ctx = mp.get_context("spawn")
    byte_q = ctx.Queue(maxsize=256)
    img_q = ctx.Queue(maxsize=256)
    evt_q = ctx.Queue()
    reader = ctx.Process(target=pse.reader_main, args=(VISUALNEWS_TAR_URL, wanted_norms, byte_q, evt_q), daemon=True)
    decoders = [ctx.Process(target=pse.decode_main, args=(byte_q, img_q, evt_q), daemon=True)
                for _ in range(n_decode)]
    inferers = [ctx.Process(target=pse.infer_main,
                            args=(img_q, evt_q, i, checkpoint, vcfg, q, groups, LABELS_NCP, done_ids, run_id),
                            daemon=True)
                for i in range(n_infer)]
    procs = [reader] + decoders + inferers
    for p in procs:
        p.start()

    sink = open(pred_path, "a")
    predict_errors = Counter()
    aborted = None
    worker_identity = None
    seen_norms = set()
    n_reader_done = n_decode_done = n_infer_done = 0
    stops_sent = False
    img_stops_sent = False
    t0 = time.monotonic()
    n_items0 = len(done_ids)
    while True:
        try:
            ev = evt_q.get(timeout=20)
        except Exception:
            ev = None
        if ev is not None:
            kind = ev[0]
            if kind == "seen":
                ledger.note_seen(ev[1]); seen_norms.add(normalize_path(ev[1]))
            elif kind == "verified":
                ledger.note_verified(ev[1])
            elif kind == "skip":
                ledger.skip(ev[1], ev[2])
            elif kind == "predict_error":
                predict_errors[ev[1]] += 1
            elif kind == "identity":
                worker_identity = ev[1]
                (output / "vision.runtime.json").write_text(json.dumps(worker_identity, indent=2) + "\n")
            elif kind == "item":
                item = ev[1]
                if item["id"] not in saved:  # single-writer guard: never duplicate a row
                    sink.write(json.dumps(item, allow_nan=False) + "\n")
                    sink.flush()
                    saved[item["id"]] = item
            elif kind == "aborted":
                aborted = ev[1]
            elif kind == "reader_done":
                n_reader_done += 1
            elif kind == "decode_done":
                n_decode_done += 1
            elif kind == "infer_done":
                n_infer_done += 1
        if n_reader_done and not stops_sent:
            for _ in range(n_decode):
                byte_q.put(None)
            stops_sent = True
        if n_decode_done == n_decode and n_reader_done and not img_stops_sent:
            for _ in range(n_infer):
                img_q.put(None)
            img_stops_sent = True
        if n_infer_done == n_infer and n_decode_done == n_decode and n_reader_done:
            break
        # dead-worker guard: if every inference worker exited without
        # completing, the pipeline can never finish — abort loudly.
        if n_infer_done < n_infer and all(not p.is_alive() for p in inferers):
            aborted = aborted or "inference workers exited without completing (tracebacks in this cell's stderr)"
            break
        if ev is None and all(not p.is_alive() for p in procs):
            aborted = aborted or "all workers exited before completion signals"
            break
    for p in procs:
        p.join(timeout=5)
        if p.is_alive():
            p.terminate()
    sink.close()
    wall = time.monotonic() - t0
    n_new = sum(1 for it in saved.values() if it.get("status") == "ok") - n_items0
    print(f"parallel pass wall: {wall:.0f}s | new ok rows: {n_new} | rate: {n_new / max(wall, 1) * 60:.1f} rows/min", flush=True)

    for norm, original in wanted_norms.items():
        if norm not in seen_norms:
            ledger.note_missing(original)

    # ---- reconciliation + artifacts: the serial tail, verbatim in substance ----
    skip_reason_by_member, missing_members = {}, set()
    if aborted is None and ledger is not None:
        skip_reason_by_member = {p: r for p, r in ledger.skips}
        missing_members = set(groups)
        for m, grows in groups.items():
            if m in skip_reason_by_member:
                missing_members.discard(m)
            elif any(r["id"] in saved for r in grows):
                missing_members.discard(m)
        with open(pred_path, "a") as sink2:
            for m in missing_members | set(skip_reason_by_member):
                reason = (f"stream_verifier_skip:{skip_reason_by_member[m]}"
                          if m in skip_reason_by_member else "member_not_in_stream")
                for row in groups[m]:
                    if row["id"] in saved:
                        continue
                    item = {k: row[k] for k in ("id", "dataset", "split", "partition", "gold", "group_id")}
                    item.update(run_id=run_id, branch="paired", status="blocked",
                                predicted_label=None, probabilities=None, fake_probability=None)
                    item["reason"] = reason
                    sink2.write(json.dumps(item, allow_nan=False) + "\n")
                    saved[item["id"]] = item

    def source_of_member(m):
        for seg in m.split("/"):
            if seg in SOURCES_NCP:
                return seg
        return "other"

    row_acct = {}
    for m, grows in groups.items():
        src = source_of_member(m)
        a = row_acct.setdefault(src, {"referenced_rows": 0, "scored_rows": 0,
                                      "skipped_rows": 0, "error_rows": 0,
                                      "skip_reasons": Counter()})
        for row in grows:
            a["referenced_rows"] += 1
            item = saved.get(row["id"])
            if item is None:
                continue
            if item["status"] == "ok":
                a["scored_rows"] += 1
            elif item["status"] == "error":
                a["error_rows"] += 1
            else:
                a["skipped_rows"] += 1
                a["skip_reasons"][str(item.get("reason", "blocked")).split(":")[0]] += 1
    for a in row_acct.values():
        a["skip_reasons"] = dict(a["skip_reasons"])

    items = list(saved.values())
    metrics = score_records(items, LABELS_NCP, NEGATIVE_NCP, config["evaluation"]["threshold"])
    metrics["purpose"] = "evaluation"
    for report in metrics["by_partition"].values():
        report["selection_eligible"] = False
    (output / "paired.metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n")
    summary = {"run_id": run_id, "purpose": "evaluation",
               "branches": {"paired": {k: metrics[k] for k in ("attempted", "usable", "error", "blocked", "abstention")}},
               "training_run": False}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with open(output / "stream_skip_ledger.jsonl", "w") as lf:
        if ledger is not None:
            for path, reason in ledger.skips:
                lf.write(json.dumps({"member": path, "source": source_of_member(path),
                                     "reason": reason,
                                     "row_ids": [r["id"] for r in groups[path]]}) + "\n")
        for m in sorted(missing_members):
            if m not in skip_reason_by_member:
                lf.write(json.dumps({"member": m, "source": source_of_member(m),
                                     "reason": "missing_from_stream",
                                     "row_ids": [r["id"] for r in groups[m]]}) + "\n")
    (output / "stream_accounting.json").write_text(json.dumps({
        "tar_url": VISUALNEWS_TAR_URL, "checkpoint": checkpoint, "aborted": aborted,
        "image_level_ledger": ledger.summary() if ledger is not None else None,
        "row_level_per_source": row_acct,
        "predict_errors": dict(predict_errors),
        "wall_seconds": round(wall, 1),
        "note": "NewsCLIPpings accuracy is computed over the scored (usable) rows only.",
        "engine": "parallel (owner decision 2026-11-22 20:39 ET): single tar reader -> multiprocess decode/verify pool -> parallel inference replicas (spawn) -> one writer. Verifier rules, checkpoint, questions, temperatures and scoring identical to the serial engine (visualnews-stream-v2); only execution concurrency changed.",
    }, indent=2) + "\n")
    (output / "manifest.json").write_text(json.dumps({
        "run_id": run_id, "method": "visualnews-stream-v2-parallel",
        "directive": "VisualNews images streamed, never saved (Rafiul, 2026-11-22); "
                     "verifier = visualnews_stream.verify_image_bytes (full PIL decode, "
                     "min dimension 8px, integrity-only skips with ledger) per directive #2. "
                     "Parallel engine per owner decision 2026-11-22 20:39 ET (wall-clock); "
                     "measurement procedure unchanged, execution concurrency only.",
        "config": config, "questions_sha256": sha_file(config["questions_file"]),
        "worker_identity": worker_identity,
    }, indent=2) + "\n")

    print(f"\n=== STREAM ACCOUNTING (PARALLEL) — {out_rel} ===")
    if ledger is not None:
        ls = ledger.summary()
        print(f"images: referenced={ls['referenced']} seen={ls['seen_in_stream']} "
              f"verified={ls['verified']} skipped={ls['skipped']} missing={ls['missing_from_stream']}")
        print(f"skip reasons: {ls['skip_reasons']}")
        print("per source (image level):")
        for s, c in ls["per_source"].items():
            print(f"  {s:16s} {c}")
    print("per source (row level):")
    for s, a in sorted(row_acct.items()):
        print(f"  {s:16s} referenced={a['referenced_rows']} scored={a['scored_rows']} "
              f"skipped={a['skipped_rows']} errors={a['error_rows']} reasons={a['skip_reasons']}")
    print(f"accuracy over SCORED rows: {metrics['native']['accuracy']:.4f} "
          f"(usable {metrics['usable']} / attempted {metrics['attempted']}) | aborted: {aborted}")
    if aborted is not None:
        raise RuntimeError(f"stream pass aborted ({aborted}) — re-run this cell; scored rows resume.")
    return metrics

# ---------------- EQUIVALENCE GATE ----------------
# Re-score ~100 val items the SERIAL pass already scored, with the parallel
# engine, into a scratch dir. Labels must be identical on every shared id
# and probabilities within float tolerance. ANY mismatch aborts the restart
# (the serial pass then resumes from its preserved partial file).
_serial_dir = WS / f"{MIDTERM_DIR}/trained_newsclippings_val_v1_serial_partial"
_serial_items = {}
for line in (_serial_dir / "paired.predictions.jsonl").read_text().splitlines():
    if line.strip():
        _it = json.loads(line)
        if _it.get("status") == "ok":
            _serial_items[_it["id"]] = _it
print(f"serial partial: {len(_serial_items)} ok rows available for the gate")
_cfg_tmp, _ = load_config(WS / "data/workflows/baseline_study/study.json",
                          ["sampling.per_class=null", "sampling.limit=null"])
_rows_tmp = load_records("newsclippings", _cfg_tmp["datasets"]["newsclippings"], "val")
_img_root_tmp = Path(_cfg_tmp["datasets"]["newsclippings"]["images"])
def _mk(row):
    rel = Path(row["image_path"]).relative_to(_img_root_tmp)
    parts = rel.parts
    if parts[0] == "visual_news":
        rel = Path(*parts[1:])
    return str(rel)
_gate_keys = []
_seen_ids = set()
_key_by_id = {_r["id"]: _mk(_r) for _r in _rows_tmp}
for _line in (_serial_dir / "paired.predictions.jsonl").read_text().splitlines():
    if not _line.strip():
        continue
    _it = json.loads(_line)
    if _it.get("status") == "ok" and _it["id"] not in _seen_ids:
        _gate_keys.append(_key_by_id[_it["id"]])  # serial file order = tar order: the gate reads the tar head only
        _seen_ids.add(_it["id"])
    if len(_seen_ids) >= 120:
        break
_gate_keys = sorted(set(_gate_keys))
print(f"gate members: {len(_gate_keys)}")
_ck = pack_checkpoint("newsclippings")
_gate_metrics = run_ncp_stream_parallel(PACKS["newsclippings"], _ck,
                                        f"{MIDTERM_DIR}/pass2_equivalence_gate_v1",
                                        limit_keys=set(_gate_keys))
_gate_items = {}
for line in (WS / f"{MIDTERM_DIR}/pass2_equivalence_gate_v1/paired.predictions.jsonl").read_text().splitlines():
    if line.strip():
        _it = json.loads(line)
        _gate_items[_it["id"]] = _it
_shared = [i for i in _serial_items if i in _gate_items and _gate_items[i].get("status") == "ok"]
_label_mismatch = [i for i in _shared if _gate_items[i]["predicted_label"] != _serial_items[i]["predicted_label"]]
_max_dp = 0.0
for _i in _shared:
    _a, _b = _serial_items[_i], _gate_items[_i]
    for _k, _v in (_a.get("probabilities") or {}).items():
        _max_dp = max(_max_dp, abs(float(_v) - float((_b.get("probabilities") or {}).get(_k, 0.0))))
    if _a.get("fake_probability") is not None and _b.get("fake_probability") is not None:
        _max_dp = max(_max_dp, abs(float(_a["fake_probability"]) - float(_b["fake_probability"])))
print(f"EQUIVALENCE GATE: shared ok ids={len(_shared)} label mismatches={len(_label_mismatch)} max |dp|={_max_dp:.6f}")
assert len(_shared) >= 100, f"gate compared only {len(_shared)} items (<100) — do not proceed"
assert not _label_mismatch, f"LABEL MISMATCH on {_label_mismatch[:5]} — ABORT restart; resume the serial pass"
assert _max_dp <= 1e-3, f"probability drift {_max_dp} > 1e-3 — ABORT restart; resume the serial pass"
print("EQUIVALENCE GATE: PASS — parallel engine is measurement-identical to serial on the shared items")
