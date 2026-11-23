"""laya_trainer — the workspace trainer for the LAYA midterm experiment.

Built 2026-11-22 for the main run, after the full-pipeline rehearsal proved
that no trainer module existed anywhere in the Mac workspace (13,192 files
searched) while the experiment notebook calls ``laya_trainer.train_full_finetune``
/ ``train_lora_finetune``. This module is that trainer, written on the laya
library's own rehearsal-proven primitives — nothing here re-implements what
the library already does:

  * ``laya.load_vlm`` / ``VLMAgent.save``      — checkpoint load / save
  * ``laya.vlm_train.train``                   — the native training loop (rlcd)
  * ``laya.vlm_train.jsonl_example``           — prepared-record -> example
  * ``laya.vlm_train.collect_logits``          — label-order logits for scoring
  * ``laya.vlm_train.fit_temperatures_from`` / ``metrics_from`` — calibration

Placement: this file ships with the workspace sync into ``data/workflows/``
(the notebook inserts that directory into ``sys.path`` before importing it).

Environment (pinned, rehearsal-verified): the laya DEV install from git
r33drichards/laya-vision @ 9e1e2419d855ad3e1a2af4d4bd1ef6be5418842c
(``laya 0.2.0.dev0``) — PyPI ``laya`` has no VLM code at all and is rejected
loudly below. torch 2.14.1 / transformers 5.19.0 / peft 0.22.0.

Design amendment (Rafiul's decision, option b, 2026-11-22): the vision tower
stays FROZEN in both arms. ``laya.vlm_train.train`` has no ``train_vision``
passthrough, and its ``freeze="full"`` trains the language encoder + decision
head only (114,728,323 of 201,161,347 params, rehearsal-measured). The "full"
arm below is exactly that; the LoRA arm adapts the encoder with peft while the
base (vision tower included) stays frozen.

Losses (the notebook grid's LOSSES = ["rlcd", "soft_ce"]):
  * ``rlcd``    — the library's native objective, exactly as rehearsed:
                  ``vlm_train.train`` with sigma=0.3, group_size=4,
                  w_sph=0.75, w_ce=1.0 (proper-scoring-rule policy gradient
                  over noisy logits + soft cross-entropy, ``vlm_loss``).
  * ``soft_ce`` — soft cross-entropy ALONE. This is NOT expressible through
                  ``vlm_train.train``: its objective always adds the
                  policy-gradient term and offers no switch to remove it
                  (sigma -> 0 makes that term degenerate). It is therefore
                  implemented in this module (``_train_soft_ce``) from the
                  library's own pieces — ``ItemStream``, ``collate_vlm``,
                  the model's forward, and ``vlm_loss``'s cross-entropy term
                  verbatim — with the same parameter grouping, LR schedule,
                  clipping and autocast as ``train()``, so the two grid
                  losses differ ONLY in the objective, which is the point of
                  comparing them.

Data: prepared MMFakeBench records
(``data/processed/protocol/mmfakebench_finetune_dev_choice_v2/{train,tune,calib}.jsonl``).
Each item appears in two question forms (4-class ``choice`` + binary
``choice``); training uses every record in the train file (both forms, as
prepared), while the selection metric — tune macro-F1 — is computed on the
4-class form ONLY, via ``collect_logits``, as the protocol requires.
Image paths inside records are relative to the directory holding the .jsonl
file, exactly as ``jsonl_example`` resolves them.

Selection / calibration helpers: ``select_and_calibrate`` implements the
protocol's post-selection step (temperatures fitted ONLY on the reserved
calib split, after selection). No notebook cell calls it — the notebook's
eval/verdict step runs through the baseline CLI + metrics module — it is
provided for that step and for H5 (calibration) reporting.

Smoke check (no GPU, no laya install needed — stdlib only):
    python laya_trainer.py check TRAIN.jsonl TUNE.jsonl CALIB.jsonl [--strict-images]
"""

import json
import math
import os
import sys

__all__ = [
    "train_full_finetune",
    "train_lora_finetune",
    "select_and_calibrate",
    "load_records",
    "validate_records",
    "macro_f1",
    "per_class_recall",
    "LOSSES",
]

LOSSES = ("rlcd", "soft_ce")

# The native objective's constants, as rehearsed on the pod 2026-11-22.
RLCD_SIGMA = 0.3
RLCD_GROUP_SIZE = 4
RLCD_W_SPH = 0.75
RLCD_W_CE = 1.0

DEFAULT_BATCH_SIZE = 8  # the notebook CONFIG's BATCH_SIZE (not passed per-call)

CLASS4_CRITERIA = 4  # the native MMFakeBench four-way choice form
TUNE_FORM = "class4"  # the form the tune (selection) metric is computed on;
# the NewsCLIPpings arm patches this to "native" (its two forms share a
# criteria count but carry FLIPPED label indices — pooling them corrupts
# the metric). See the F1/F2 deviation note, main run 2026-11-22.


# ---------------------------------------------------------------------------------------------------------
# Heavy imports (lazy: the record-validation helpers and `check` run on stdlib alone)
# ---------------------------------------------------------------------------------------------------------


def _laya_modules():
    """Import torch + the dev laya package, or raise with the precise fix."""
    try:
        import torch
        import laya
        from laya import vlm_train
    except ImportError as exc:
        raise ImportError(
            "laya_trainer needs torch and the laya DEV install (git "
            "r33drichards/laya-vision @ 9e1e2419, laya 0.2.0.dev0) — PyPI "
            "'laya' has no VLM code. Original error: %r" % (exc,)
        ) from exc
    for name in ("train", "jsonl_example", "collect_logits", "fit_temperatures_from", "metrics_from"):
        if not hasattr(vlm_train, name):
            raise ImportError(
                "laya.vlm_train has no %r — this is not the dev laya-vision "
                "package the rehearsal verified. Refusing to train." % name
            )
    if not hasattr(laya, "load_vlm"):
        raise ImportError("laya has no load_vlm — not the dev laya-vision package. Refusing to train.")
    return torch, laya, vlm_train


# ---------------------------------------------------------------------------------------------------------
# Records: loading + validation (pure stdlib — also used by the `check` smoke path)
# ---------------------------------------------------------------------------------------------------------


def load_records(path):
    """Read a prepared .jsonl file into a list of record dicts. Fails loudly."""
    if not os.path.isfile(path):
        raise FileNotFoundError("prepared records file not found: %s" % path)
    records = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError("%s line %d is not valid JSON: %s" % (path, lineno, exc)) from exc
    if not records:
        raise ValueError("prepared records file is empty: %s" % path)
    return records


def _record_form(rec):
    """'class4' for the native four-way choice form, else the question type/shape."""
    rid = str(rec.get("id") or "")
    if rid.endswith(":native"):
        return "native"
    if rid.endswith(":binary"):
        return "binary"
    q = rec.get("question") or {}
    if q.get("type") == "choice" and isinstance(q.get("criteria"), dict) and len(q["criteria"]) == CLASS4_CRITERIA:
        return "class4"
    if q.get("type") == "choice":
        return "choice%d" % len(q.get("criteria") or {})
    return str(q.get("type"))


def validate_records(records, path="<records>", check_images=False):
    """Schema-check prepared records; returns a summary dict. Raises on any defect.

    Required per record: id, image (or images), state_text, question{type,
    instructions, criteria}, label within the criteria range. With
    ``check_images``, image paths are resolved relative to the directory
    holding ``path`` (the same resolution ``jsonl_example`` applies) and
    missing files are counted (reported, not raised — see ``check`` CLI).
    """
    root = os.path.dirname(os.path.abspath(path))
    forms, missing_images = {}, 0
    for i, rec in enumerate(records):
        where = "%s record %d (id=%r)" % (path, i, rec.get("id"))
        for key in ("id", "state_text", "question", "label"):
            if key not in rec:
                raise ValueError("%s is missing required field %r" % (where, key))
        if not rec.get("image") and not rec.get("images"):
            raise ValueError("%s has neither 'image' nor 'images'" % where)
        q = rec["question"]
        if not isinstance(q, dict) or "type" not in q or "criteria" not in q:
            raise ValueError("%s has a malformed 'question' (needs type + criteria)" % where)
        if q["type"] == "choice":
            crit = q["criteria"]
            k = len(crit) if isinstance(crit, (dict, list)) else 0
            if not k or not 0 <= int(rec["label"]) < k:
                raise ValueError("%s label %r is outside its %d criteria" % (where, rec["label"], k))
        forms[_record_form(rec)] = forms.get(_record_form(rec), 0) + 1
        if check_images:
            imgs = [rec["image"]] if rec.get("image") else list(rec.get("images") or [])
            for rel in imgs:
                if not os.path.isfile(os.path.normpath(os.path.join(root, rel))):
                    missing_images += 1
    return {"n": len(records), "forms": forms, "missing_images": missing_images}


def _examples(vlm_train, path, form=None, dataset="mmfakebench"):
    """Prepared records -> laya training/eval examples via ``jsonl_example``.

    ``form="class4"`` keeps only the native four-way choice records (the
    selection metric's population). Records the converter drops (returns
    None: duplicate criteria strings, out-of-range label) are counted and
    reported; if ALL are dropped the file is unusable and this raises.
    """
    records = load_records(path)
    validate_records(records, path)
    root = os.path.dirname(os.path.abspath(path))
    out, dropped = [], 0
    for rec in records:
        if form is not None and _record_form(rec) != form:
            continue
        ex = vlm_train.jsonl_example(rec, root, dataset=dataset)
        if ex is None:
            dropped += 1
            continue
        out.append(ex)
    if dropped:
        print("laya_trainer: %s: %d record(s) dropped by jsonl_example (invalid for training)" % (path, dropped))
    if not out:
        raise ValueError("no usable examples in %s (form=%r, %d records read)" % (path, form, len(records)))
    return out


# ---------------------------------------------------------------------------------------------------------
# Metrics (pure python — the selection metric, computed from collect_logits records)
# ---------------------------------------------------------------------------------------------------------


def per_class_recall(y_true, y_pred, n_classes):
    """Recall per class index; 0.0 for a class with no support."""
    out = []
    for c in range(n_classes):
        support = sum(1 for t in y_true if t == c)
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c)
        out.append(tp / support if support else 0.0)
    return out


def macro_f1(y_true, y_pred, n_classes):
    """Unweighted mean of per-class F1 (the study's native MMFakeBench metric)."""
    if len(y_true) != len(y_pred):
        raise ValueError("y_true / y_pred length mismatch: %d vs %d" % (len(y_true), len(y_pred)))
    if not y_true:
        raise ValueError("macro_f1 of an empty population is undefined")
    f1s = []
    for c in range(n_classes):
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != c and p == c)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == c and p != c)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(f1s) / n_classes


def _tune_metrics(vlm_train, agent, tune_examples):
    """Tune macro-F1 + per-class recall from ``collect_logits`` (class4 only).

    ``tune_examples`` must already be the class4 population. Logits come back
    in label order; the class names are the first example's criteria order.
    """
    records = vlm_train.collect_logits(agent.model, agent.processor, tune_examples, batch_size=16)
    y_true, y_pred = [], []
    for r in records:
        logits = [float(v) for v in r["logits"].tolist()]
        y_pred.append(max(range(len(logits)), key=lambda j: logits[j]))
        y_true.append(int(r["label"]))
    names = list(tune_examples[0]["q"]["crit"].keys())
    k = len(names)
    recalls = per_class_recall(y_true, y_pred, k)
    acc = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)
    return {
        "tune_metric_form": TUNE_FORM,
        "tune_macro_f1": macro_f1(y_true, y_pred, k),
        "tune_accuracy": acc,
        "tune_per_class_recall": {name: recalls[i] for i, name in enumerate(names)},
        "n_tune_class4": len(y_true),
    }


# ---------------------------------------------------------------------------------------------------------
# soft_ce: the cross-entropy-only loop (see the module docstring for why this exists)
# ---------------------------------------------------------------------------------------------------------


def _train_soft_ce(torch, vlm_train, model, processor, examples, *, steps, batch_size, seed,
                   lr_encoder_group, lr_head_group):
    """Soft cross-entropy alone, built from the library's own pieces.

    Mirrors ``vlm_train.train`` in everything except the objective: same
    ``ItemStream`` sampling, same ``collate_vlm`` batching, same forward,
    same encoder/head parameter grouping (``"encoder."`` prefix), the same
    warmup-free cosine LR shape (1.0 -> 0.55 -> held shape of train(): f =
    0.1 + 0.45 * (1 + cos(pi * progress))), AdamW(0.01), grad-clip 1.0, bf16
    autocast on CUDA. The loss is ``vlm_loss``'s cross-entropy term verbatim.
    Assumes the caller has already set ``requires_grad`` (set_trainable for
    the full arm, peft for the LoRA arm) — this loop never touches freezing.
    Returns the per-step losses.
    """
    import functools
    import random

    from laya.vlm import collate_vlm

    torch.manual_seed(seed)
    random.seed(seed)
    device = torch.device(next(model.parameters()).device)
    dtype = model.encoder.dtype
    enc = [p for n, p in model.named_parameters() if p.requires_grad and n.startswith("encoder.")]
    head = [p for n, p in model.named_parameters() if p.requires_grad and not n.startswith("encoder.")]
    if not enc and not head:
        raise ValueError("soft_ce: no trainable parameters — freezing was not configured by the caller")
    groups = ([{"params": head, "lr": lr_head_group}] if head else []) + \
             ([{"params": enc, "lr": lr_encoder_group}] if enc else [])
    base_lrs = [g["lr"] for g in groups]
    opt = torch.optim.AdamW(groups, weight_decay=0.01)
    stream = vlm_train.ItemStream(processor, examples, seed)
    loader = torch.utils.data.DataLoader(
        stream, batch_size=batch_size, num_workers=0,
        collate_fn=functools.partial(collate_vlm, pad_id=processor.tokenizer.pad_token_id),
    )
    amp = device.type == "cuda"
    model.to(device).train()
    losses, step = [], 0
    for batch in loader:
        if step >= steps:
            break
        progress = step / max(1, steps)
        f = 0.1 + 0.45 * (1 + math.cos(math.pi * progress))
        for g, lr in zip(groups, base_lrs):
            g["lr"] = lr * f
        b = {}
        for key, v in batch.items():
            if torch.is_tensor(v):
                v = v.to(device, non_blocking=True)
                if key == "pixel_values":
                    v = v.to(dtype)
            b[key] = v
        with torch.autocast(device.type, dtype=torch.bfloat16, enabled=amp):
            logits, _act = model(
                b["input_ids"], b["attention_mask"], b["marker_pos"], b["marker_mask"], b["qtype"],
                pixel_values=b["pixel_values"], pixel_attention_mask=b["pixel_attention_mask"],
                option_span=b["option_span"], raw_pixels=b.get("raw_pixels"), image_mask=b.get("image_mask"),
            )
        logits = logits.float()
        mask = b["marker_mask"]
        target = b["target"].float()
        loss = -(target * torch.log_softmax(logits.masked_fill(~mask, -1e4), -1)).sum(-1).mean()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_([p for g in groups for p in g["params"]], 1.0)
        opt.step()
        losses.append(float(loss.item()))
        if step % 10 == 0:
            print("soft_ce step %d | loss %.4f | lr %.2e" % (step, losses[-1], groups[0]["lr"]), flush=True)
        step += 1
    model.eval()
    return losses


# ---------------------------------------------------------------------------------------------------------
# Shared run plumbing
# ---------------------------------------------------------------------------------------------------------


def _check_common(loss, max_steps, train_file, tune_file):
    if loss not in LOSSES:
        raise ValueError("loss must be one of %s, got %r" % (list(LOSSES), loss))
    if not isinstance(max_steps, int) or max_steps <= 0:
        raise ValueError("max_steps must be a positive int, got %r" % (max_steps,))
    for p in (train_file, tune_file):
        if not os.path.isfile(p):
            raise FileNotFoundError("records file not found: %s" % p)


def _finish(agent, out_dir, result):
    """Save the trained agent + a result.json receipt; return the result dict."""
    os.makedirs(out_dir, exist_ok=True)
    agent.save(out_dir)
    result = dict(result, out_dir=str(out_dir))
    with open(os.path.join(out_dir, "result.json"), "w") as f:
        json.dump(result, f, indent=1)
    return result


def _trainable_count(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# ---------------------------------------------------------------------------------------------------------
# The two arms (notebook signatures — see the experiment notebook's trainer cell)
# ---------------------------------------------------------------------------------------------------------


def train_full_finetune(ckpt_id, revision=None, loss="rlcd", max_steps=245,
                        lr_encoder=1e-5, lr_head=1e-3, seed=0,
                        train_file=None, tune_file=None, out_dir=None,
                        batch_size=DEFAULT_BATCH_SIZE, dataset="mmfakebench"):
    """FULL arm: language encoder + decision head trained, vision tower frozen.

    Runs ``vlm_train.train(freeze="full")`` for ``loss="rlcd"`` (the native
    objective), or the module's CE-only loop for ``loss="soft_ce"``. Saves the
    trained agent to ``out_dir`` and returns a dict whose ``tune_macro_f1``
    (class4 form only, via ``collect_logits``) is the selection metric.
    """
    _check_common(loss, max_steps, train_file, tune_file)
    if out_dir is None:
        raise ValueError("out_dir is required")
    torch, laya, vlm_train = _laya_modules()
    agent = laya.load_vlm(ckpt_id, revision=revision)
    train_examples = _examples(vlm_train, train_file, dataset=dataset)
    tune_examples = _examples(vlm_train, tune_file, form=TUNE_FORM, dataset=dataset)
    if loss == "rlcd":
        losses = vlm_train.train(
            agent.model, agent.processor, train_examples,
            steps=max_steps, batch_size=batch_size, freeze="full",
            lr_head=lr_head, lr_backbone=lr_encoder, seed=seed,
            sigma=RLCD_SIGMA, group_size=RLCD_GROUP_SIZE, w_sph=RLCD_W_SPH, w_ce=RLCD_W_CE,
        )
    else:  # soft_ce
        vlm_train.set_trainable(agent.model, "full")
        losses = _train_soft_ce(
            torch, vlm_train, agent.model, agent.processor, train_examples,
            steps=max_steps, batch_size=batch_size, seed=seed,
            lr_encoder_group=lr_encoder, lr_head_group=lr_head,
        )
    result = {
        "arm": "full", "loss": loss, "steps": max_steps, "seed": seed,
        "base": ckpt_id, "revision": revision,
        "lr_encoder": lr_encoder, "lr_head": lr_head,
        "n_train_records": len(train_examples),
        "trainable_params": _trainable_count(agent.model),
        "loss_first": float(losses[0]), "loss_last": float(losses[-1]),
        "losses": [float(v) for v in losses],
    }
    result.update(_tune_metrics(vlm_train, agent, tune_examples))
    return _finish(agent, out_dir, result)


def train_head_only_finetune(ckpt_id, revision=None, loss="rlcd", max_steps=490,
                             lr_head=1e-3, lr_encoder=1e-5, seed=0,
                             train_file=None, tune_file=None, out_dir=None,
                             batch_size=DEFAULT_BATCH_SIZE, dataset="mmfakebench"):
    """HEAD-ONLY arm (supplementary tier, amendment (d) 2026-11-22): only the
    decision head trains — type_emb / head / scorer / act_head — with the
    encoder AND vision tower frozen, via the library's own freeze="head"
    (``vlm_train.set_trainable``). Mirrors ``train_full_finetune`` in
    everything else: rlcd runs ``vlm_train.train(freeze="head")``; soft_ce
    sets trainable to "head" and runs the module's CE-only loop (its
    encoder group is then empty by construction). Receipt arm = "head".
    Supplementary receipts live under runs/supplementary/ and never feed
    selection, calibration, or test (the caller's out_dir enforces it).
    """
    _check_common(loss, max_steps, train_file, tune_file)
    if out_dir is None:
        raise ValueError("out_dir is required")
    torch, laya, vlm_train = _laya_modules()
    agent = laya.load_vlm(ckpt_id, revision=revision)
    train_examples = _examples(vlm_train, train_file, dataset=dataset)
    tune_examples = _examples(vlm_train, tune_file, form=TUNE_FORM, dataset=dataset)
    if loss == "rlcd":
        losses = vlm_train.train(
            agent.model, agent.processor, train_examples,
            steps=max_steps, batch_size=batch_size, freeze="head",
            lr_head=lr_head, lr_backbone=lr_encoder, seed=seed,
            sigma=RLCD_SIGMA, group_size=RLCD_GROUP_SIZE, w_sph=RLCD_W_SPH, w_ce=RLCD_W_CE,
        )
    else:  # soft_ce
        vlm_train.set_trainable(agent.model, "head")
        losses = _train_soft_ce(
            torch, vlm_train, agent.model, agent.processor, train_examples,
            steps=max_steps, batch_size=batch_size, seed=seed,
            lr_encoder_group=lr_encoder, lr_head_group=lr_head,
        )
    result = {
        "arm": "head", "loss": loss, "steps": max_steps, "seed": seed,
        "base": ckpt_id, "revision": revision,
        "lr_encoder": lr_encoder, "lr_head": lr_head,
        "n_train_records": len(train_examples),
        "trainable_params": _trainable_count(agent.model),
        "loss_first": float(losses[0]), "loss_last": float(losses[-1]),
        "losses": [float(v) for v in losses],
    }
    result.update(_tune_metrics(vlm_train, agent, tune_examples))
    return _finish(agent, out_dir, result)


def _preserve_trainable(model, mode="head", n_last=4, train_vision=False):
    """Stand-in for ``vlm_train.set_trainable`` during a LoRA ``train()`` call:
    peft has already set ``requires_grad`` correctly, and the library's
    ``set_trainable`` would wipe it. Returns the trainable count, untouched."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def _filter_lora_targets(encoder, targets):
    """Keep only LoRA target names that match at least one encoder module
    (the notebook CONFIG's 'filtered to modules that exist' rule)."""
    module_names = [name for name, _ in encoder.named_modules()]
    kept = []
    for t in targets or []:
        if any(name == t or name.endswith("." + t) for name in module_names):
            kept.append(t)
        else:
            print("laya_trainer: LoRA target %r matches no encoder module — dropped" % t)
    if not kept:
        raise ValueError("none of the LoRA targets %r exist in the encoder" % (targets,))
    return kept


def train_lora_finetune(ckpt_id, revision=None, loss="rlcd", max_steps=245,
                        lora_r=16, lora_alpha=32, lora_dropout=0.05, lora_targets=None,
                        lr_lora=1e-3, lr_head=1e-3, seed=0,
                        train_file=None, tune_file=None, out_dir=None,
                        batch_size=DEFAULT_BATCH_SIZE, dataset="mmfakebench"):
    """LoRA arm: peft adapters on the encoder, base frozen, head trained.

    The binding proven in the 2026-11-22 rehearsal: ``LoraConfig`` over
    ``agent.model.encoder`` (all 7 CONFIG target names verified to exist
    there), ``vlm_train.set_trainable`` monkeypatched to a preserving no-op
    for the duration of the ``train()`` call (the library loop would
    otherwise reset ``requires_grad`` and unfreeze the base), the LoRA group
    carried at ``lr_backbone=lr_lora``, the head at ``lr_head``. After
    training the adapter is merged (``merge_and_unload``) and the merged
    model is saved via ``VLMAgent.save`` — the saved checkpoint is a plain
    laya checkpoint, loadable exactly like the full arm's.
    """
    _check_common(loss, max_steps, train_file, tune_file)
    if out_dir is None:
        raise ValueError("out_dir is required")
    torch, laya, vlm_train = _laya_modules()
    try:
        from peft import LoraConfig, get_peft_model
    except ImportError as exc:
        raise ImportError("the LoRA arm needs peft (pinned 0.22.0): %r" % (exc,)) from exc
    agent = laya.load_vlm(ckpt_id, revision=revision)
    train_examples = _examples(vlm_train, train_file, dataset=dataset)
    tune_examples = _examples(vlm_train, tune_file, form=TUNE_FORM, dataset=dataset)
    targets = _filter_lora_targets(agent.model.encoder, lora_targets)
    agent.model.encoder = get_peft_model(
        agent.model.encoder,
        LoraConfig(r=lora_r, lora_alpha=lora_alpha, lora_dropout=lora_dropout, target_modules=targets),
    )
    if loss == "rlcd":
        original = vlm_train.set_trainable
        vlm_train.set_trainable = _preserve_trainable
        try:
            losses = vlm_train.train(
                agent.model, agent.processor, train_examples,
                steps=max_steps, batch_size=batch_size, freeze="full",
                lr_head=lr_head, lr_backbone=lr_lora, seed=seed,
                sigma=RLCD_SIGMA, group_size=RLCD_GROUP_SIZE, w_sph=RLCD_W_SPH, w_ce=RLCD_W_CE,
            )
        finally:
            vlm_train.set_trainable = original
    else:  # soft_ce — peft already froze the base; the CE loop never touches freezing
        losses = _train_soft_ce(
            torch, vlm_train, agent.model, agent.processor, train_examples,
            steps=max_steps, batch_size=batch_size, seed=seed,
            lr_encoder_group=lr_lora, lr_head_group=lr_head,
        )
    trainable = _trainable_count(agent.model)
    agent.model.encoder = agent.model.encoder.merge_and_unload()
    result = {
        "arm": "lora", "loss": loss, "steps": max_steps, "seed": seed,
        "base": ckpt_id, "revision": revision,
        "lora_r": lora_r, "lora_alpha": lora_alpha, "lora_dropout": lora_dropout,
        "lora_targets": targets, "lr_lora": lr_lora, "lr_head": lr_head,
        "n_train_records": len(train_examples),
        "trainable_params": trainable,
        "loss_first": float(losses[0]), "loss_last": float(losses[-1]),
        "losses": [float(v) for v in losses],
    }
    result.update(_tune_metrics(vlm_train, agent, tune_examples))
    return _finish(agent, out_dir, result)


# ---------------------------------------------------------------------------------------------------------
# Post-selection calibration (protocol step; fitted ONLY on the reserved calib split)
# ---------------------------------------------------------------------------------------------------------


def select_and_calibrate(winner_dir, calib_file, out_dir=None, dataset="mmfakebench"):
    """Fit per-type temperatures on the reserved calib split for a SAVED winner.

    Loads the winner checkpoint from ``winner_dir``, collects logits on the
    calib records (both question forms — one shared 'choice' temperature),
    fits temperatures with ``fit_temperatures_from``, reports ECE before /
    after on the calib split itself (a fit-quality report, NOT a selection
    metric), writes the temperatures into the agent and saves to
    ``out_dir`` (default: ``<winner_dir>_calibrated``). The winner's own
    directory is never modified. Returns the summary dict.
    """
    if not os.path.isdir(winner_dir):
        raise FileNotFoundError("winner checkpoint dir not found: %s" % winner_dir)
    if not os.path.isfile(calib_file):
        raise FileNotFoundError("calib records file not found: %s" % calib_file)
    torch, laya, vlm_train = _laya_modules()
    agent = laya.load_vlm(winner_dir)
    calib_examples = _examples(vlm_train, calib_file, dataset=dataset)
    records = vlm_train.collect_logits(agent.model, agent.processor, calib_examples, batch_size=16)
    temps = [float(t) for t in vlm_train.fit_temperatures_from(records)]
    before = vlm_train.metrics_from(records)["all"]
    after = vlm_train.metrics_from(records, temperatures=temps)["all"]
    agent.temperature = temps
    out = out_dir or (str(winner_dir).rstrip("/") + "_calibrated")
    os.makedirs(out, exist_ok=True)
    agent.save(out)
    summary = {
        "winner_dir": str(winner_dir), "out_dir": str(out),
        "temperatures": temps, "n_calib": len(records),
        "ece_before": before["ece"], "ece_after": after["ece"],
        "acc_calib": after["acc"], "nll_before": before["nll"], "nll_after": after["nll"],
    }
    with open(os.path.join(out, "calibration.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return summary


# ---------------------------------------------------------------------------------------------------------
# Smoke path: `python laya_trainer.py check FILE.jsonl [FILE.jsonl ...] [--strict-images]`
# ---------------------------------------------------------------------------------------------------------


def _main(argv=None):
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    chk = sub.add_parser("check", help="validate prepared .jsonl files (schema, forms, image paths); no GPU/laya needed")
    chk.add_argument("files", nargs="+")
    chk.add_argument("--strict-images", action="store_true",
                     help="fail if any referenced image file is missing (default: report the count only)")
    args = ap.parse_args(argv)

    if args.cmd == "check":
        bad = 0
        for path in args.files:
            try:
                records = load_records(path)
                summary = validate_records(records, path, check_images=True)
            except (FileNotFoundError, ValueError) as exc:
                print("FAIL %s: %s" % (path, exc), file=sys.stderr)
                bad += 1
                continue
            print("OK   %s: %d records, forms=%s, missing_images=%d"
                  % (path, summary["n"], summary["forms"], summary["missing_images"]))
            if args.strict_images and summary["missing_images"]:
                print("FAIL %s: %d referenced image(s) missing (--strict-images)"
                      % (path, summary["missing_images"]), file=sys.stderr)
                bad += 1
        if bad:
            print("check FAILED for %d file(s)" % bad, file=sys.stderr)
            return 1
        print("check PASSED")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_main())
