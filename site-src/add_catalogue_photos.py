"""Adds real online pack photos to the 21 catalogue products (ids 1-22, ORS-L has none).
Extends the PHOTOS map and sets photo fields on product entries.
"""
import base64
from pathlib import Path

ROOT = Path("/home/user/site-src")
APP = ROOT / "app.js"
t = APP.read_text(encoding="utf-8")

# product id -> thumbnail slug (id 6 ORS-L has no genuine pack photo online)
MAP = {
    1: "crocin", 2: "dolo", 3: "azithral", 4: "pan40", 5: "cetzine",
    7: "shelcal", 8: "neurobion", 9: "chyawanprash", 10: "dettol",
    11: "omron", 12: "drtrust", 13: "combiflam", 14: "volini", 15: "digene",
    16: "eno", 17: "zincovit", 18: "supradyn", 19: "ashwagandha", 20: "liv52",
    21: "vicks", 22: "oximeter",
}

entries = []
for pid, slug in MAP.items():
    raw = (ROOT / "img" / f"p-{slug}.jpg").read_bytes()
    entries.append('    "%s": "data:image/jpeg;base64,%s",' % (slug, base64.b64encode(raw).decode("ascii")))

anchor = "\n  };\n\n  var PRODUCTS = ["
assert t.count(anchor) == 1
t = t.replace(anchor, "\n" + "\n".join(entries) + anchor)

import re
for pid, slug in MAP.items():
    pat = re.compile(r'(\{ id: %d, name: "[^"]+".*?)(\s*\})' % pid)
    t2, n = pat.subn(lambda m: m.group(1) + ', photo: "%s"' % slug + m.group(2), t, count=1)
    assert n == 1, f"id {pid}"
    t = t2

APP.write_text(t, encoding="utf-8")
print("photos added:", len(MAP), "| app.js chars:", len(t))
print("RESULT: CATALOGUE_PHOTOS_OK")
