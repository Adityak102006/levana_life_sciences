"""Recovery tool: reconstructs build.py + sources from the self-contained pages.
Runs once. Validates that the reconstructed pipeline reproduces the pages byte for byte.
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "medical-store"
BACKUP = ROOT / "original"
BACKUP.mkdir(parents=True, exist_ok=True)

pages = {p.name: p.read_text(encoding="utf-8") for p in sorted(OUT.glob("*.html"))}
for n, t in pages.items():
    (BACKUP / n).write_text(t, encoding="utf-8")

index = pages["index.html"]


def between(s, a, b):
    i = s.index(a) + len(a)
    j = s.index(b, i)
    return s[i:j]


css = between(index, "<style>\n", "</style>")
js = between(index, "<script>\n", "</script>")
for n, t in pages.items():
    assert between(t, "<style>\n", "</style>") == css, n
    assert between(t, "<script>\n", "</script>") == js, n

TITLE = between(index, "<title>", "</title>")
DESC = between(index, '<meta name="description" content="', '">')
FAVICON = between(index, '<link rel="icon" href="', '">')
FONTS = '<link rel="preconnect"' + between(index, '<link rel="preconnect"', 'rel="stylesheet">') + 'rel="stylesheet">'

fb = set(re.findall(
    r"onerror=\"this\.onerror=null;this\.src='(data:image/svg\+xml,[^']+)'\"",
    "".join(pages.values()),
))
assert len(fb) == 1, fb
IMG_FALLBACK = fb.pop()

body_by_page = {}
img_token = {
    "index.html": "__IMG_HERO__",
    "about.html": "__IMG_STORE__",
    "prescriptions.html": "__IMG_DESK__",
}
for n, t in pages.items():
    b = between(t, '<main id="main">\n', "\n</main>")
    b = b.replace(IMG_FALLBACK, "__IMG_FALLBACK__")
    for u in set(re.findall(r'src="(data:image/jpeg;base64,[A-Za-z0-9+/=]+)"', b)):
        assert n in img_token, (n, "unexpected photo")
        b = b.replace(u, img_token[n])
    assert "data:image/jpeg" not in b
    body_by_page[n] = b

NAV_ITEMS = [
    ("index.html", "Home", "home"),
    ("medicines.html", "Medicines", "medicines"),
    ("prescriptions.html", "Prescriptions", "prescriptions"),
    ("about.html", "About", "about"),
    ("contact.html", "Contact", "contact"),
]


def nav_html(active):
    parts = []
    for url, label, key in NAV_ITEMS:
        cls = ' class="is-active"' if key == active else ""
        parts.append('<li><a href="' + url + '"' + cls + ">" + label + "</a></li>")
    return "\n".join(parts)


def active_key(filename):
    return "home" if filename == "index.html" else filename.split(".")[0]


for n, t in pages.items():
    nav = between(t[t.index('id="site-nav"'):], "<ul>\n", "\n</ul>")
    assert nav == nav_html(active_key(n)), n

tmpl = index
assert tmpl.count("<style>\n" + css + "</style>") == 1
tmpl = tmpl.replace("<style>\n" + css + "</style>", "<style>\n__CSS__</style>")
assert tmpl.count("<script>\n" + js + "</script>") == 1
tmpl = tmpl.replace("<script>\n" + js + "</script>", "<script>\n__JS__</script>")
assert tmpl.count("<title>" + TITLE + "</title>") == 1
tmpl = tmpl.replace("<title>" + TITLE + "</title>", "<title>__TITLE__</title>")
assert tmpl.count('content="' + TITLE + '"') == 1
tmpl = tmpl.replace('content="' + TITLE + '"', 'content="__TITLE__"')
assert tmpl.count('content="' + DESC + '"') == 2
tmpl = tmpl.replace('content="' + DESC + '"', 'content="__DESC__"')
assert tmpl.count('href="' + FAVICON + '"') == 1
tmpl = tmpl.replace('href="' + FAVICON + '"', 'href="__FAVICON__"')
assert tmpl.count(FONTS) == 1
tmpl = tmpl.replace(FONTS, "__FONTS__")
nav_span = "<ul>\n" + nav_html("home") + "\n</ul>"
assert tmpl.count(nav_span) == 1
tmpl = tmpl.replace(nav_span, "<ul>\n__NAV__\n</ul>")
index_body_raw = between(index, '<main id="main">\n', "\n</main>")
body_span = '<main id="main">\n' + index_body_raw + "\n</main>"
assert tmpl.count(body_span) == 1
tmpl = tmpl.replace(body_span, '<main id="main">\n__BODY__\n</main>')
assert "data:image/jpeg" not in tmpl
assert "data:image/svg+xml" not in tmpl
assert "is-active" not in tmpl

page_meta = []
for n, t in pages.items():
    page_meta.append((n, TITLE if n == "index.html" else between(t, "<title>", "</title>"),
                      DESC if n == "index.html" else between(t, '<meta name="description" content="', '">')))

order = ["index.html", "medicines.html", "prescriptions.html", "about.html", "contact.html"]
bodies_const = {
    "index.html": "BODY_HOME",
    "medicines.html": "BODY_MEDICINES",
    "prescriptions.html": "BODY_PRESCRIPTIONS",
    "about.html": "BODY_ABOUT",
    "contact.html": "BODY_CONTACT",
}
meta_by = {n: (ti, de) for n, ti, de in page_meta}

def py_str(s):
    return '"""' + s.replace("\\", "\\\\").replace('"""', '\\"""') + '"""'

lines = []
lines.append("import base64")
lines.append("from pathlib import Path")
lines.append("")
lines.append("ROOT = Path(__file__).resolve().parent")
lines.append('OUT = ROOT.parent / "medical-store"')
lines.append("OUT.mkdir(parents=True, exist_ok=True)")
lines.append("")
lines.append('css = (ROOT / "styles.css").read_text()')
lines.append('js = (ROOT / "app.js").read_text()')
lines.append("")
lines.append("")
lines.append("def img_uri(name):")
lines.append('    p = ROOT / "img" / name')
lines.append("    if not p.exists():")
lines.append('        return ""')
lines.append('    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode("ascii")')
lines.append("")
lines.append("")
lines.append('IMG_HERO = img_uri("hero.jpg")')
lines.append('IMG_STORE = img_uri("store.jpg")')
lines.append('IMG_DESK = img_uri("desk.jpg")')
lines.append("")
lines.append("# FIX-MEDIA: clean percent encoded inline SVG placeholder used by img onerror fallback")
lines.append("IMG_FALLBACK = " + repr(IMG_FALLBACK))
lines.append("")
lines.append("FAVICON = " + repr(FAVICON))
lines.append("FONTS = " + repr(FONTS))
lines.append("")
lines.append("TEMPLATE = " + py_str(tmpl))
lines.append("")
lines.append("NAV = [")
for url, label, key in NAV_ITEMS:
    lines.append('    ("%s", "%s", "%s"),' % (url, label, key))
lines.append("]")
lines.append("")
lines.append("")
lines.append("def nav_html(active):")
lines.append("    parts = []")
lines.append("    for url, label, key in NAV:")
lines.append("        cls = ' class=\"is-active\"' if key == active else \"\"")
lines.append("""        parts.append('<li><a href="' + url + '"' + cls + '>' + label + '</a></li>')""")
lines.append('    return "\\n".join(parts)')
lines.append("")
lines.append("")
for n in order:
    lines.append(bodies_const[n] + " = " + py_str(body_by_page[n]))
    lines.append("")
lines.append("PAGES = [")
for n in order:
    ti, de = meta_by[n]
    lines.append('    ("%s",' % n)
    lines.append("     " + repr(ti) + ",")
    lines.append("     " + repr(de) + ",")
    lines.append('     "%s",' % active_key(n))
    lines.append("     " + bodies_const[n] + "),")
lines.append("]")
lines.append("")
lines.append("for filename, title, desc, active, body in PAGES:")
lines.append("    html = (")
lines.append('        TEMPLATE.replace("__BODY__", body)')
lines.append('        .replace("__TITLE__", title)')
lines.append('        .replace("__DESC__", desc)')
lines.append('        .replace("__FAVICON__", FAVICON)')
lines.append('        .replace("__FONTS__", FONTS)')
lines.append('        .replace("__NAV__", nav_html(active))')
lines.append('        .replace("__IMG_HERO__", IMG_HERO)')
lines.append('        .replace("__IMG_STORE__", IMG_STORE)')
lines.append('        .replace("__IMG_DESK__", IMG_DESK)')
lines.append('        .replace("__IMG_FALLBACK__", IMG_FALLBACK)')
lines.append('        .replace("__CSS__", css)')
lines.append('        .replace("__JS__", js)')
lines.append("    )")
lines.append('    (OUT / filename).write_text(html, encoding="utf-8")')
lines.append('    print("built", filename, len(html), "bytes")')
lines.append("")

src = ROOT / "build.py"
src.write_text("\n".join(lines), encoding="utf-8")
print("wrote", src, len("\n".join(lines)), "chars")

# validate in-memory assembly against originals
img_bytes = {
    "__IMG_HERO__": (ROOT / "img" / "hero.jpg").read_bytes(),
    "__IMG_STORE__": (ROOT / "img" / "store.jpg").read_bytes(),
    "__IMG_DESK__": (ROOT / "img" / "desk.jpg").read_bytes(),
}
ok = True
for n in order:
    ti, de = meta_by[n]
    html = (
        tmpl.replace("__BODY__", body_by_page[n])
        .replace("__TITLE__", ti)
        .replace("__DESC__", de)
        .replace("__FAVICON__", FAVICON)
        .replace("__FONTS__", FONTS)
        .replace("__NAV__", nav_html(active_key(n)))
        .replace("__IMG_HERO__", "data:image/jpeg;base64," + base64.b64encode(img_bytes["__IMG_HERO__"]).decode("ascii"))
        .replace("__IMG_STORE__", "data:image/jpeg;base64," + base64.b64encode(img_bytes["__IMG_STORE__"]).decode("ascii"))
        .replace("__IMG_DESK__", "data:image/jpeg;base64," + base64.b64encode(img_bytes["__IMG_DESK__"]).decode("ascii"))
        .replace("__IMG_FALLBACK__", IMG_FALLBACK)
        .replace("__CSS__", css)
        .replace("__JS__", js)
    )
    same = html == pages[n]
    ok = ok and same
    print("roundtrip", n, "EXACT" if same else "MISMATCH")
print("RESULT:", "RECOVERY_OK" if ok else "RECOVERY_FAILED")
