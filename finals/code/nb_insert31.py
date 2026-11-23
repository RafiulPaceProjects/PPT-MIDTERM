import json

P = "/workspace/Misinformation/LAYA_MainRun_Merged.ipynb"
nb = json.load(open(P))

SRC = r"""# ===== §7d COMPLETION — data-size axis (corrected) + supplementary table =====
# DEVIATION (2026-11-22, logged in mainrun_log.md): the original §7d cell
# wrote the data-axis subset files into runs/supplementary/data_*/ WITHOUT
# rebasing the records' relative image paths ("../../../raw/..." is
# relative to the protocol dir). Resolved from the subset dir, every
# training image missed; the trainer skipped records wholesale (one
# 7.05M-line skip stream, trimmed by the driver with a marker in the cell
# above) and the cell was stopped before either data config produced a
# receipt. Configs 1–13 (head / LoRA-rank / encoder-LR / seed) are
# UNAFFECTED — they trained from the original train file in place, and
# their receipts stand. This cell regenerates both subsets WITH rebased
# paths, trains the two data configs, and assembles the full
# supplementary table + data curve. Isolation unchanged: supplementary
# receipts never feed selection, calibration, or test-once.
import json, pathlib, re, time
import laya_trainer

WS = pathlib.Path(WORKSPACE)
SUPP_DIR = WS / "runs" / "supplementary"
TRAIN_FILE = str(WS / "data/processed/protocol/mmfakebench_finetune_dev_choice_v2/train.jsonl")
TUNE_FILE = str(WS / "data/processed/protocol/mmfakebench_finetune_dev_choice_v2/tune.jsonl")
REQ_FIELDS = {"arm", "loss", "steps", "seed", "tune_macro_f1", "tune_per_class_recall"}

_all_recs = [json.loads(l) for l in open(TRAIN_FILE) if l.strip()]
_item_order, _by_item = [], {}
for _r in _all_recs:
    _item = re.sub(r":(class4|binary|choice2|native)$", "", str(_r["id"]))
    if _item not in _by_item:
        _by_item[_item] = []
        _item_order.append(_item)
    _by_item[_item].append(_r)
assert len(_item_order) == 490, f"train set should hold 490 items, holds {len(_item_order)}"

DATA_RUNS = []
for _n_items, _tag in ((245, "data_245"), (122, "data_122")):
    _sub_dir = SUPP_DIR / _tag
    _sub_dir.mkdir(parents=True, exist_ok=True)
    _sub_file = _sub_dir / "train_subset.jsonl"
    with open(_sub_file, "w") as _f:
        for _item in _item_order[:_n_items]:
            for _r in _by_item[_item]:
                _r2 = dict(_r)
                if isinstance(_r2.get("image"), str) and _r2["image"].startswith("../../../raw/"):
                    _r2["image"] = "../../../data/raw/" + _r2["image"][len("../../../raw/"):]
                _f.write(json.dumps(_r2) + "\n")
    _first = json.loads(open(_sub_file).readline())
    _resolved = (_sub_dir / _first["image"]).resolve()
    assert _resolved.exists(), f"{_tag}: rebased image path does not resolve: {_resolved}"
    print(f"{_tag}: subset regenerated ({_n_items} items, both forms), image paths verified", flush=True)
    DATA_RUNS.append((_tag, _n_items, str(_sub_file)))

supp = {}
for _rp in sorted(SUPP_DIR.glob("*/result.json")):
    supp[_rp.parent.name] = json.loads(_rp.read_text())
print(f"existing supplementary receipts carried in: {len(supp)}", flush=True)

for _tag, _n_items, _sub_file in DATA_RUNS:
    _name = f"{_tag}_{winner['arm']}_{winner['loss']}_490"
    _out_dir = SUPP_DIR / _tag / _name
    print(f"[train] supplementary {_name} ({_n_items} items) ...", flush=True)
    t0 = time.time()
    _common = dict(ckpt_id=CKPT_ID, revision=CKPT_REVISION, loss=winner["loss"],
                   max_steps=490, seed=SEED, train_file=_sub_file, tune_file=TUNE_FILE,
                   out_dir=str(_out_dir))
    if winner["arm"] == "full":
        out = laya_trainer.train_full_finetune(lr_encoder=LR_ENCODER, lr_head=LR_HEAD, **_common)
    else:
        out = laya_trainer.train_lora_finetune(
            lora_r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
            lora_targets=LORA_TARGETS, lr_lora=LORA_LR, lr_head=LR_HEAD, **_common)
    _missing = REQ_FIELDS - set(out)
    assert not _missing, f"{_name}: receipt missing fields {_missing}"
    out["n_train_items"] = _n_items
    out["train_seconds"] = round(time.time() - t0, 1)
    out["train_window"] = [t0, time.time()]
    _out_dir.mkdir(parents=True, exist_ok=True)
    (_out_dir / "result.json").write_text(json.dumps(out, indent=1))
    supp[_name] = out
    print(f"[done] {_name}: tune macro-F1 = {out['tune_macro_f1']:.4f} ({time.time() - t0:.0f}s)", flush=True)

_grid490 = json.loads((WS / "runs" / f"{winner['arm']}_{winner['loss']}_490" / "result.json").read_text())
DATA_CURVE = {
    "steps": 490, "arm": winner["arm"], "loss": winner["loss"],
    "points": {
        "122": supp[f"data_122_{winner['arm']}_{winner['loss']}_490"]["tune_macro_f1"],
        "245": supp[f"data_245_{winner['arm']}_{winner['loss']}_490"]["tune_macro_f1"],
        "490": _grid490["tune_macro_f1"],
    },
    "note": "490-item point is the grid's own receipt (not retrained); 245/122 trained on train-file-order prefixes, both forms per item.",
}
print("DATA CURVE (items -> tune macro-F1 @490 steps):", DATA_CURVE["points"])

(SUPP_DIR / "supplementary_table.json").write_text(json.dumps({
    "amendment": "(d) supplementary tier — never feeds selection, calibration, or test-once",
    "winner_context": winner,
    "data_curve": DATA_CURVE,
    "configs": supp,
    "table": {n: o["tune_macro_f1"] for n, o in supp.items()},
}, indent=1))
print("\n=== SUPPLEMENTARY TABLE — tune macro-F1 (15 configs, isolated) ===")
for n, o in sorted(supp.items(), key=lambda kv: -kv[1]["tune_macro_f1"]):
    print(f"  {n:44s} {o['tune_macro_f1']:.4f}")
print("receipts -> runs/supplementary/*/result.json + runs/supplementary/supplementary_table.json")
"""

compile(SRC, "cell31", "exec")
cell = {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
        "source": SRC.splitlines(keepends=True)}
nb["cells"].insert(31, cell)
json.dump(nb, open(P, "w"), indent=1)
import os
print("inserted completion cell at 31; cells now:", len(nb["cells"]), "size:", os.path.getsize(P))
