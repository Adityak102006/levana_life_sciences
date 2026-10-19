"""Content and asset update: new store status, Meerut address, new email, real logo + favicon.
Every replacement asserts an exact match count. Rerunning on a clean recovered build.py is idempotent after success.
"""
import re
from pathlib import Path

BUILD = Path("/home/user/site-src/build.py")
t = BUILD.read_text(encoding="utf-8")

FULL_ADDR = "Unit No. S-002 (LIG), Second Floor, C-Block, Apex City Colony, Village Rampur Pawati, Tehsil and District Meerut, Uttar Pradesh"

edits = []

def sub(old, new, count=1):
    edits.append((old, new, count))

# --- structural: assets -------------------------------------------------
sub(
    '''def img_uri(name):
    p = ROOT / "img" / name
    if not p.exists():
        return ""
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


IMG_HERO = img_uri("hero.jpg")
IMG_STORE = img_uri("store.jpg")
IMG_DESK = img_uri("desk.jpg")''',
    '''def img_uri(name):
    p = ROOT / "img" / name
    if not p.exists():
        return ""
    mime = "png" if name.endswith(".png") else "jpeg"
    return "data:image/" + mime + ";base64," + base64.b64encode(p.read_bytes()).decode("ascii")


IMG_HERO = img_uri("hero.jpg")
IMG_STORE = img_uri("store.jpg")
IMG_DESK = img_uri("desk.jpg")
# FIX-MEDIA: real brand logo and monogram supplied by the client
IMG_LOGO = img_uri("logo.jpg")
IMG_MARK = img_uri("mark.png")''',
)
sub(
    '''<a class="brand" href="index.html" aria-label="Levana Life Sciences home">
<span class="brand__mark" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" width="32" height="32"><path d="M20 5.5a11 11 0 1 0 7 14 9 9 0 0 1-7-14z" fill="currentColor"/><path d="M12.5 13h2.8v2.8h2.8v2.8h-2.8v2.8h-2.8v-2.8H9.7v-2.8h2.8z" fill="#c46a3b"/></svg></span>
<span><span class="brand__name">Levana</span><span class="brand__sub">Life Sciences</span></span>
</a>''',
    '''<a class="brand" href="index.html" aria-label="Levana Life Sciences home">
<!-- FIX-MEDIA: client logo embedded as data URI with size hints and SVG fallback -->
<img class="brand__logo" src="__IMG_LOGO__" alt="Levana Lifesciences" width="640" height="309" onerror="this.onerror=null;this.src='__IMG_FALLBACK__'">
</a>''',
)
sub(
    '''<span class="hero-panel__badge" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" width="32" height="32"><path d="M20 5.5a11 11 0 1 0 7 14 9 9 0 0 1-7-14z" fill="currentColor"/><path d="M12.5 13h2.8v2.8h2.8v2.8h-2.8v2.8h-2.8v-2.8H9.7v-2.8h2.8z" fill="#c46a3b"/></svg></span>''',
    '''<span class="hero-panel__badge" aria-hidden="true"><img src="__IMG_MARK__" alt="" width="96" height="96" onerror="this.onerror=null;this.src='__IMG_FALLBACK__'"></span>''',
)
sub(
    '''        .replace("__IMG_DESK__", IMG_DESK)''',
    '''        .replace("__IMG_DESK__", IMG_DESK)
        .replace("__IMG_LOGO__", IMG_LOGO)
        .replace("__IMG_MARK__", IMG_MARK)''',
)

# --- content: contact address first (it contains the footer address as prefix)
sub(
    "Main Road, Kichha, Udham Singh Nagar, Uttarakhand 263148. Landmark: opposite the main bus stand.",
    FULL_ADDR + ".",
)
sub(
    "Main Road, Kichha, Udham Singh Nagar, Uttarakhand 263148",
    FULL_ADDR,
)
sub(
    '<div class="footer-legal"><strong>Drug Licence</strong> 20B / 21B, UK/20B-21B/2024/1876<br><strong>GSTIN</strong> 05ABCDE1234F1Z5<br><strong>Pharmacist</strong> Mr. Amit Sharma, B.Pharm, UK-PC-45219</div>',
    '<div class="footer-legal"><strong>Drug Licence</strong> 20B / 21B, UP/20B-21B/2026/1876<br><strong>GSTIN</strong> 09ABCDE1234F1Z5<br><strong>Pharmacist</strong> Mr. Amit Sharma, B.Pharm, UP-PC-45219</div>',
)
sub("UK/20B-21B/2024/1876", "UP/20B-21B/2026/1876", 1)
sub("UK-PC-45219", "UP-PC-45219", 1)
sub("05ABCDE1234F1Z5", "09ABCDE1234F1Z5", 2)
sub(
    'mailto:care@levanalifesciences.in">care@levanalifesciences.in',
    'mailto:levanalifesciences26@gmail.com">levanalifesciences26@gmail.com',
    2,
)

# --- content: location and new-store story ------------------------------
sub("Licensed pharmacy (20B / 21B) in Kichha, Uttarakhand", "Licensed pharmacy (20B / 21B) in Meerut, Uttar Pradesh")
sub("Same-day delivery in Kichha", "Same-day delivery in Meerut")
sub(
    "Your trusted licensed medical store in Kichha, Uttarakhand.",
    "Your trusted licensed medical store in Meerut, Uttar Pradesh.",
)
sub("Licensed pharmacy in Kichha", "Licensed pharmacy in Meerut")
sub("Delivery in Kichha", "Delivery in Meerut")
sub(
    '<div class="hero-fact"><strong>15+ years</strong><span>Of community trust</span></div>',
    '<div class="hero-fact"><strong>Now open</strong><span>In Apex City Colony, Meerut</span></div>',
)
sub(
    '<div class="factbar__item"><strong>4.8 / 5</strong><span>Average customer rating</span></div>',
    '<div class="factbar__item"><strong>GST invoice</strong><span>With every order</span></div>',
)
sub("Forms 20B and 21B, Uttarakhand", "Forms 20B and 21B, Uttar Pradesh")
sub("Loved by families across <em>Kichha.</em>", "What our first customers <em>say.</em>")
sub("Sunita Devi</strong><span>Kichha</span>", "Sunita Devi</strong><span>Meerut</span>")
sub("Rahul Mehrotra</strong><span>Rudrapur</span>", "Rahul Mehrotra</strong><span>Meerut</span>")
sub("Anjali Rawat</strong><span>Kichha</span>", "Anjali Rawat</strong><span>Rampur Pawati</span>")
sub(
    "Same-day delivery across Kichha in 30 to 60 minutes.",
    "Same-day delivery across Meerut in 30 to 60 minutes.",
)
sub("serving Kichha and nearby towns", "serving Meerut and nearby areas")
sub(
    "For over 15 years, families in Kichha have trusted us for genuine medicines and honest advice. Levana Life Sciences brings that same care online, so that ordering a refill is as simple as a phone tap, with a real pharmacist still checking every prescription.",
    "Levana Life Sciences has just opened its doors in Apex City Colony, Rampur Pawati, with a simple promise: genuine medicines and honest advice. Ordering a refill is as simple as a phone tap, with a real pharmacist still checking every prescription.",
)
sub("<dt>Established</dt><dd>Serving Kichha for 15+ years</dd>", "<dt>Established</dt><dd>Newly opened in 2026, fully licensed</dd>")
sub("<dt>Delivery</dt><dd>Kichha in 30 to 60 minutes</dd>", "<dt>Delivery</dt><dd>Meerut in 30 to 60 minutes</dd>")
sub(
    "<dt>Store address</dt><dd>Main Road, Kichha, Uttarakhand</dd>",
    "<dt>Store address</dt><dd>" + FULL_ADDR + "</dd>",
)
sub(
    "issued by the Uttarakhand State Drugs Control Department",
    "issued by the Uttar Pradesh State Drugs Control Department",
)
sub(
    "Visit our store on Main Road, Kichha with any question",
    "Visit our store at Apex City Colony, Rampur Pawati, Meerut with any question",
)
sub(
    "https://maps.google.com/?q=Kichha+Uttarakhand",
    "https://maps.google.com/?q=Apex+City+Colony+Rampur+Pawati+Meerut",
)
sub(
    "We offer same-day delivery across Kichha, usually within 30 to 60 minutes, and next-day delivery to nearby areas including Rudrapur and Khatima. Delivery is free on orders above 499 rupees. You can also pick up your order from our store on Main Road, Kichha.",
    "We offer same-day delivery across Meerut, usually within 30 to 60 minutes, and next-day delivery to nearby areas. Delivery is free on orders above 499 rupees. You can also pick up your order from our store at Apex City Colony, Rampur Pawati.",
)
sub(
    "'Levana Life Sciences | Licensed Medical Store in Kichha, Uttarakhand',",
    "'Levana Life Sciences | Licensed Medical Store in Meerut, Uttar Pradesh',",
)
sub(
    "is a licensed medical store in Kichha, Uttarakhand. Order",
    "is a licensed medical store in Meerut, Uttar Pradesh. Order",
)
sub(
    "is a licensed pharmacy in Kichha, Uttarakhand. View",
    "is a licensed pharmacy in Meerut, Uttar Pradesh. View",
)
sub(
    "Contact Levana Life Sciences in Kichha, Uttarakhand.",
    "Contact Levana Life Sciences in Meerut, Uttar Pradesh.",
)

for old, new, count in edits:
    found = t.count(old)
    assert found == count, f"expected {count} of {old[:70]!r}, found {found}"
    t = t.replace(old, new)

# favicon line: swap the old SVG monogram for the client mark PNG
t2, n = re.subn(
    r"^FAVICON = .*$",
    'FAVICON = "data:image/png;base64," + base64.b64encode((ROOT / "img" / "mark.png").read_bytes()).decode("ascii")',
    t,
    count=1,
    flags=re.M,
)
assert n == 1, "favicon line"
t = t2

forbidden = ["Kichha", "Uttarakhand", "Rudrapur", "Khatima", "263148", "care@levanalifesciences",
             "05ABCDE", "UK/", "UK-PC", "15+ years", "15 years", "4.8 / 5", "bus stand",
             "Of community trust", "brand__mark"]
for f in forbidden:
    assert f not in t, f"left behind: {f}"

BUILD.write_text(t, encoding="utf-8")
print("applied", len(edits) + 1, "edits; final length", len(t))
print("RESULT: CONTENT_UPDATE_OK")
