"""Shared by the stamp and QA tools: load data/*.json, resolve a data-bind
path, and format a value. src/js/format.js implements the same rules for the
values the deck changes live (the threshold slider); qa_check.py checks the
two agree.

Paths: dots between fields, brackets for list items.
  key_metrics.zip.worst.pct_bc
  tables.correlation.matrix[0][2]       list of numbers: by index
  thresholds.stops[0.45].tn             list of records: by id field value
  tables.models[Random forest].test_roc_auc
"""
import json
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FILES = ["key_metrics", "thresholds", "curves", "confusion", "importance", "tables", "pca", "maps"]
ID_FIELDS = ["threshold", "model", "boro", "cuisine", "feature", "zip", "nta", "column", "grade", "component"]

MISSING = object()


def load():
    return {name: json.loads((DATA / f"{name}.json").read_text()) for name in FILES}


def resolve(data, path):
    """The value at path, or MISSING if any step is absent."""
    cur = data
    for name, key in re.findall(r"([^.\[\]]+)|\[([^\]]+)\]", path):
        try:
            if name:
                cur = cur[name]
            elif isinstance(cur, list) and cur and isinstance(cur[0], dict):
                field = next(f for f in ID_FIELDS if f in cur[0])
                cur = next(d for d in cur if _same(d[field], key))
            else:
                cur = cur[int(key)]
        except (KeyError, IndexError, StopIteration, TypeError, ValueError):
            return MISSING
    return cur


def _same(value, key):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return float(key) == float(value)
        except ValueError:
            return False
    return str(value) == key


def _round(v, n):
    q = Decimal(1).scaleb(-n)
    return Decimal(repr(float(v))).quantize(q, rounding=ROUND_HALF_UP)


def _signed(text):
    return text.replace("-", "−")


WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def fmt(value, kind):
    if kind == "str":
        return str(value)
    if kind == "int":
        return f"{int(_round(value, 0)):,}"
    if kind in ("num0", "num1"):
        return _signed(str(_round(value, int(kind[-1]))))
    if kind in ("pct0", "pct1"):
        return f"{_round(value, int(kind[-1]))}%"
    if kind in ("dec2", "dec3", "dec4"):
        return _signed(str(_round(value, int(kind[-1]))))
    if kind == "frac_pct1":
        return f"{_round(100 * value, 1)}%"
    if kind == "per100":
        return str(_round(100 * value, 0))
    if kind == "inv_tenths":
        return str(_round(10 * (1 - value), 0))
    if kind == "inv_tenths_word":
        return WORDS[int(_round(10 * (1 - value), 0))]
    if kind == "thr":
        return f"{float(value):g}"
    raise ValueError(f"unknown format {kind!r}")
