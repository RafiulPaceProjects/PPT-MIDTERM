"""Write every bound number into index.html from data/*.json (INV-1).

Each element carrying data-bind="path" data-fmt="kind" gets its text set to
the formatted export value and a data-value attribute holding the raw value
(count-ups animate toward it). A value the exports do not have yet is
written as "awaiting export" with a data-pending attribute, which the theme
shows in red and qa_check.py fails on.

Tables marked data-table="name" are rebuilt from the exports too.

Run after tools/export_deck_data.py:  python3 tools/stamp_numbers.py
"""
import html
import json
import re
import sys

from deckdata import MISSING, ROOT, fmt, load, resolve

INDEX = ROOT / "index.html"

TABLES = {
    "zip_highest": ("tables.zip_highest", [("ZIP", "zip", "str"), ("Borough", "boro", "str"),
                                          ("Inspections", "inspections", "int"), ("Graded", "graded", "int"),
                                          ("B or C", "pct_bc", "pct1")]),
    "zip_lowest": ("tables.zip_lowest", [("ZIP", "zip", "str"), ("Inspections", "inspections", "int"),
                                        ("Graded", "graded", "int"), ("B or C", "pct_bc", "pct1")]),
}

BOUND = re.compile(r'<(?P<tag>\w+)(?P<attrs>[^<>]*?\sdata-bind="(?P<path>[^"]+)"[^<>]*)>(?P<body>[^<]*)</(?P=tag)>')
TABLE = re.compile(r'(<table[^>]*\sdata-table="(?P<name>[^"]+)"[^>]*>\s*(?:<caption>.*?</caption>)?)(?P<body>.*?)(</table>)', re.S)


def set_attr(attrs, name, value):
    attrs = re.sub(rf'\s{name}(="[^"]*")?', "", attrs)
    return attrs if value is None else f'{attrs} {name}="{html.escape(value, quote=True)}"'


def stamp(text, data):
    problems = []

    def one(m):
        attrs, path = m.group("attrs"), m.group("path")
        kind = re.search(r'\sdata-fmt="([^"]+)"', attrs)
        if not kind:
            problems.append(f"{path}: no data-fmt")
            return m.group(0)
        value = resolve(data, path)
        if value is MISSING:
            problems.append(f"{path}: not in the exports")
            return m.group(0)
        if value is None:
            attrs = set_attr(set_attr(attrs, "data-pending", ""), "data-value", None)
            body = "awaiting export"
        else:
            attrs = set_attr(set_attr(attrs, "data-pending", None), "data-value", json.dumps(value))
            body = html.escape(fmt(value, kind.group(1)), quote=False)
        return f'<{m.group("tag")}{attrs}>{body}</{m.group("tag")}>'

    text = BOUND.sub(one, text)

    def table(m):
        spec = TABLES.get(m.group("name"))
        if not spec:
            problems.append(f"table {m.group('name')}: no template")
            return m.group(0)
        rows = resolve(data, spec[0])
        head = "".join(f'<th{" class=\"n\"" if k != "str" else ""}>{h}</th>' for h, _, k in spec[1])
        body = "".join(
            "<tr>" + "".join(f'<td{" class=\"n\"" if k != "str" else ""}>{html.escape(fmt(r[f], k))}</td>'
                             for _, f, k in spec[1]) + "</tr>" for r in rows)
        return f"{m.group(1)}<thead><tr>{head}</tr></thead><tbody>{body}</tbody>{m.group(4)}"

    text = TABLE.sub(table, text)
    return text, problems


def main():
    data = load()
    before = INDEX.read_text()
    after, problems = stamp(before, data)
    for p in problems:
        print("stamp problem:", p)
    if problems:
        return 1
    INDEX.write_text(after)
    pending = len(re.findall(r"\sdata-pending", after))
    bound = len(BOUND.findall(after))
    print(f"stamped {bound} values into index.html ({pending} awaiting export)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
