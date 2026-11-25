#!/usr/bin/env python3
"""Similarity audit on the frozen snapshots (PRD: similarity-audit, BOARD-PASSED 2026-11-24).

Encoder, named in the PRD: openai/clip-vit-base-patch32. No alternates.
Score direction, registered: higher cosine predicts pristine, so the
falsified ranking score is minus cosine. No inversion after scoring.
Nothing is fitted on any item. NewsCLIPpings images are streamed from
the VisualNews origin.tar over HTTP range requests, verified in
memory, hashed at load, embedded, and discarded (never stored).
VERITE images are the study's local dataset files, hashed at load.
"""
from __future__ import annotations

import hashlib
import io
import json
import random
import struct
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path("/home/hatch/workspace/misinfo_run")
V2 = ROOT / "v2_probe"
OUT = ROOT / "swarm_tests" / "similarity-audit"
TAR_URL = "https://www.cs.rice.edu/~vo9/visualnews/origin.tar"
SEED = 20261122
N_RESAMPLES = 10000
MODEL_ID = "openai/clip-vit-base-patch32"

sys.path.insert(0, str(ROOT))
import visualnews_stream as vs  # noqa: E402


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def auc(scores, labels):
    """Rank AUC, tie-aware. labels: 1 = positive (falsified/fake)."""
    s = np.asarray(scores, dtype=float)
    y = np.asarray(labels, dtype=int)
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=float)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[order[j + 1]] == s[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def paired_gap_interval(sim_scores, model_scores, labels, seed=SEED, n=N_RESAMPLES):
    rng = random.Random(seed)
    idx_all = list(range(len(labels)))
    gaps = []
    for _ in range(n):
        idx = [rng.choice(idx_all) for _ in idx_all]
        lab = [labels[i] for i in idx]
        if len(set(lab)) < 2:
            continue
        gaps.append(auc([sim_scores[i] for i in idx], lab)
                    - auc([model_scores[i] for i in idx], lab))
    gaps.sort()
    k = len(gaps)
    return {"gap_ci95": [gaps[int(0.025 * k)], gaps[int(0.975 * k)]],
            "n_resamples_used": k}


# ---------- VisualNews tar range scanner ----------
class RangeTar:
    def __init__(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": "laya-stream/1.0",
                                                   "Range": "bytes=0-0"})
        resp = urllib.request.urlopen(req, timeout=60)
        try:
            cr = resp.headers.get("Content-Range", "")
            if resp.status != 206 or "/" not in cr:
                raise OSError("range requests not honored")
            self.total = int(cr.rsplit("/", 1)[1])
        finally:
            resp.close()
        self.url = url

    def fetch(self, start, length):
        end = start + length - 1
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    self.url, headers={"User-Agent": "laya-stream/1.0",
                                       "Range": f"bytes={start}-{end}"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    if r.status != 206:
                        raise OSError(f"HTTP {r.status}")
                    return r.read()
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)

    def scan(self, wanted):
        """wanted: dict normalized_path -> key. Yields (key, raw_bytes)."""
        remaining = dict(wanted)
        offset = 0
        longname = None
        while offset + 512 <= self.total and remaining:
            hdr = self.fetch(offset, 512)
            if hdr == b"\x00" * 512:
                break
            name = hdr[0:100].split(b"\x00")[0].decode("utf-8", "replace")
            prefix = hdr[345:500].split(b"\x00")[0].decode("utf-8", "replace")
            if prefix:
                name = prefix + "/" + name
            size_field = hdr[124:136].split(b"\x00")[0].strip() or b"0"
            size = int(size_field, 8)
            typeflag = chr(hdr[156])
            data_start = offset + 512
            if typeflag == "L":
                data = self.fetch(data_start, size)
                longname = data.split(b"\x00")[0].decode("utf-8", "replace")
            else:
                member_name = longname or name
                longname = None
                if typeflag in ("0", "\x00"):
                    norm = vs.normalize_path(member_name)
                    if norm in remaining:
                        data = self.fetch(data_start, size)
                        yield remaining.pop(norm), data
            offset = data_start + ((size + 511) // 512) * 512
        return remaining


def main():
    t0 = time.time()
    log = {"encoder": MODEL_ID, "seed": SEED, "n_resamples": N_RESAMPLES}

    # ---- step 0: snapshot hash verification ----
    probe_asm = (V2 / "assembled_probe_repaired.jsonl").read_bytes()
    h = sha256_bytes(probe_asm)
    log["assembled_probe_repaired_sha256"] = h
    assert h == "f8bc0fadaea7559d9a0d5a2fdbca0b8341d5a6130961486981c19e79859f7705", \
        f"probe snapshot hash mismatch: {h}"
    verite_asm = (V2 / "assembled_verite.jsonl").read_bytes()
    log["assembled_verite_sha256"] = sha256_bytes(verite_asm)
    print("snapshot hashes verified", flush=True)

    # ---- encoder availability gate ----
    import torch
    from transformers import CLIPModel, CLIPProcessor
    model = CLIPModel.from_pretrained(MODEL_ID)
    proc = CLIPProcessor.from_pretrained(MODEL_ID)
    model.eval()
    torch.set_num_threads(4)
    print("encoder loaded", flush=True)

    def embed_texts(texts):
        outs = []
        for i in range(0, len(texts), 32):
            batch = texts[i:i + 32]
            inp = proc(text=batch, return_tensors="pt", padding=True,
                       truncation=True)
            with torch.no_grad():
                emb = model.get_text_features(**inp)
            outs.append(emb.numpy())
        e = np.concatenate(outs)
        return e / np.linalg.norm(e, axis=1, keepdims=True)

    def embed_image(pil_image):
        inp = proc(images=pil_image, return_tensors="pt")
        with torch.no_grad():
            emb = model.get_image_features(**inp)
        e = emb.numpy()[0]
        return e / np.linalg.norm(e)

    # ================= NewsCLIPpings =================
    items = [json.loads(l) for l in open(V2 / "probe_items.jsonl")]
    model_prob = {}
    for line in open(V2 / "preds_stageA_300.jsonl"):
        r = json.loads(line)
        if r.get("arm") == "P0":
            model_prob[r["id"]] = r["fake_probability"]
    asm = {}
    for line in probe_asm.decode().splitlines():
        r = json.loads(line)
        asm[r["item_id"]] = r

    wanted = {}
    for it in items:
        ip = it["image_path"]
        rel = ip[len("visual_news/"):] if ip.startswith("visual_news/") else ip
        wanted[vs.normalize_path(rel)] = it["id"]
    by_id = {it["id"]: it for it in items}

    tar = RangeTar(TAR_URL)
    log["tar_total_bytes"] = tar.total
    img_emb = {}
    img_hash = {}
    missing = []
    found = 0
    for item_id, data in tar.scan(wanted):
        img_hash[item_id] = sha256_bytes(data)
        ok, reason, image = vs.verify_image_bytes(data)
        if not ok:
            missing.append({"id": item_id, "reason": f"verify failed: {reason}"})
            continue
        img_emb[item_id] = embed_image(image.convert("RGB"))
        found += 1
        if found % 50 == 0:
            print(f"ncp images embedded: {found}", flush=True)
    got_ids = [it["id"] for it in items if it["id"] in img_emb]
    for it in items:
        if it["id"] not in img_emb and not any(m["id"] == it["id"] for m in missing):
            missing.append({"id": it["id"], "reason": "not found in tar scan"})
    log["ncp_images_found"] = len(got_ids)
    log["ncp_images_missing"] = missing
    print(f"ncp: {len(got_ids)} images, {len(missing)} missing", flush=True)

    cap_emb = embed_texts([by_id[i]["caption"] for i in got_ids])
    img_mat = np.stack([img_emb[i] for i in got_ids])
    cos_img_cap = (img_mat * cap_emb).sum(axis=1)
    labels = [1 if by_id[i]["gold"] == "falsified" else 0 for i in got_ids]
    sim_score = -cos_img_cap
    model_score = [model_prob[i] for i in got_ids]

    sim_auc = auc(sim_score, labels)
    model_auc = auc(model_score, labels)
    gap = sim_auc - model_auc
    interval = paired_gap_interval(list(sim_score), model_score, labels)
    ncp = {"n_items": len(got_ids), "similarity_auc_img_caption": sim_auc,
           "model_screen_auc_stageA_paironly_recomputed": model_auc,
           "gap_sim_minus_model": gap, **interval}

    # secondary: evidence features on the covered subset
    covered = [i for i in got_ids
               if asm.get(i, {}).get("arms", {}).get("A_headline", {}).get("passages")]
    log["ncp_covered_items"] = len(covered)
    if covered:
        cap_c = embed_texts([by_id[i]["caption"] for i in covered])
        ev_max, ev_mean = [], []
        for j, i in enumerate(covered):
            passages = asm[i]["arms"]["A_headline"]["passages"]
            texts = [(p.get("title") or "") + " " + (p.get("snippet") or "")
                     for p in passages]
            pe = embed_texts(texts)
            sims = pe @ cap_c[j]
            ev_max.append(float(sims.max()))
            ev_mean.append(float(sims.mean()))
        lab_c = [1 if by_id[i]["gold"] == "falsified" else 0 for i in covered]
        ncp["covered_subset"] = {
            "n": len(covered),
            "auc_neg_evidence_max": auc([-v for v in ev_max], lab_c),
            "auc_neg_evidence_mean": auc([-v for v in ev_mean], lab_c),
            "model_screen_auc_on_identical_subset":
                auc([model_prob[i] for i in covered], lab_c),
        }
    log["newsclippings"] = ncp

    # per-item output
    with open(OUT / "ncp_item_scores.jsonl", "w") as f:
        for j, i in enumerate(got_ids):
            f.write(json.dumps({
                "id": i, "gold": by_id[i]["gold"],
                "image_sha256": img_hash.get(i),
                "cos_image_caption": float(cos_img_cap[j]),
                "similarity_score_neg_cos": float(sim_score[j]),
                "model_fake_probability": model_prob[i]}) + "\n")

    # ================= VERITE (descriptive only) =================
    vitems = [json.loads(l) for l in open(V2 / "verite_test_items.jsonl")]
    vasm = {}
    for line in verite_asm.decode().splitlines():
        r = json.loads(line)
        vasm[r["item_id"]] = r
    v_img_emb = {}
    v_hash = {}
    v_missing = []
    for it in vitems:
        p = V2 / "verite_push" / it["image"]
        if not p.exists():
            v_missing.append({"id": it["id"], "reason": f"missing file {it['image']}"})
            continue
        data = p.read_bytes()
        v_hash[it["id"]] = sha256_bytes(data)
        ok, reason, image = vs.verify_image_bytes(data)
        if not ok:
            v_missing.append({"id": it["id"], "reason": f"verify failed: {reason}"})
            continue
        v_img_emb[it["id"]] = embed_image(image.convert("RGB"))
    v_ids = [it["id"] for it in vitems if it["id"] in v_img_emb]
    v_by = {it["id"]: it for it in vitems}
    v_cap = embed_texts([v_by[i]["caption"] for i in v_ids])
    v_mat = np.stack([v_img_emb[i] for i in v_ids])
    v_cos = (v_mat * v_cap).sum(axis=1)
    v_score = -v_cos
    v_fake = [0 if v_by[i]["gold"] == "true" else 1 for i in v_ids]
    ver = {"n_items": len(v_ids), "n_missing": len(v_missing),
           "missing": v_missing,
           "auc_pooled_fake_vs_true": auc(v_score, v_fake)}
    for cls in ("miscaptioned", "out-of-context"):
        sub = [i for i in v_ids if v_by[i]["gold"] in ("true", cls)]
        ver[f"auc_true_vs_{cls}"] = auc(
            [-float(v_cos[v_ids.index(i)]) for i in sub],
            [1 if v_by[i]["gold"] == cls else 0 for i in sub])
        ver[f"n_true_vs_{cls}"] = len(sub)
    v_covered = [i for i in v_ids
                 if vasm.get(i, {}).get("arms", {}).get("A_headline", {}).get("passages")]
    ver["covered_items"] = len(v_covered)
    if v_covered:
        cap_v = embed_texts([v_by[i]["caption"] for i in v_covered])
        ev_max, ev_mean = [], []
        for j, i in enumerate(v_covered):
            passages = vasm[i]["arms"]["A_headline"]["passages"]
            texts = [(p.get("title") or "") + " " + (p.get("snippet") or "")
                     for p in passages]
            pe = embed_texts(texts)
            sims = pe @ cap_v[j]
            ev_max.append(float(sims.max()))
            ev_mean.append(float(sims.mean()))
        lab_v = [0 if v_by[i]["gold"] == "true" else 1 for i in v_covered]
        ver["covered_subset_descriptive"] = {
            "n": len(v_covered),
            "auc_neg_evidence_max": auc([-v for v in ev_max], lab_v),
            "auc_neg_evidence_mean": auc([-v for v in ev_mean], lab_v)}
    log["verite"] = ver
    with open(OUT / "verite_item_scores.jsonl", "w") as f:
        for j, i in enumerate(v_ids):
            f.write(json.dumps({
                "id": i, "gold": v_by[i]["gold"],
                "image_sha256": v_hash.get(i),
                "cos_image_caption": float(v_cos[j]),
                "similarity_score_neg_cos": float(v_score[j])}) + "\n")

    log["wall_seconds"] = round(time.time() - t0, 1)
    (OUT / "similarity_results.json").write_text(json.dumps(log, indent=1))
    print(json.dumps({"newsclippings": ncp, "verite": ver}, indent=1), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
