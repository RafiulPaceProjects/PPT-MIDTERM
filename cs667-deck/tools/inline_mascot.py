"""Copy src/assets-src/mascot.svg (the layered source) into index.html's
#mascot-layer, so the deck needs no fetch and works from file://.
qa_check.py fails if the two ever differ."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
svg = (ROOT / "src/assets-src/mascot.svg").read_text().strip()
index = ROOT / "index.html"
text = index.read_text()
new, n = re.subn(r'(<div id="mascot-layer" aria-hidden="true">).*?(</div>)',
                 lambda m: m.group(1) + "\n" + svg + "\n" + m.group(2), text, flags=re.S)
assert n == 1, "mascot layer not found"
index.write_text(new)
print("inlined mascot.svg into index.html")
