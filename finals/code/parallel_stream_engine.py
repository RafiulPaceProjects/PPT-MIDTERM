
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
