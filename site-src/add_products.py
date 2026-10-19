"""Adds the Levana own-range products with real pack photos to app.js.
Photos are embedded as data URIs (PHOTOS map), cropped thumbnails with names visible.
"""
import base64
from pathlib import Path

ROOT = Path("/home/user/site-src")
APP = ROOT / "app.js"
t = APP.read_text(encoding="utf-8")

slugs = ["levpan-d", "levmulti", "livnim-p", "levcalci-d", "painac-sp", "levdenzy", "lavace-sp", "levranbe-d", "lev-gold"]
photos = []
for s in slugs:
    raw = (ROOT / "img" / f"p-{s}.jpg").read_bytes()
    photos.append('    "%s": "data:image/jpeg;base64,%s",' % (s, base64.b64encode(raw).decode("ascii")))
photo_block = (
    "  // FIX-MEDIA: own Levana range pack photos, data URIs cropped so names read clearly\n"
    "  var PHOTOS = {\n" + "\n".join(photos) + "\n  };\n\n"
)

products = """  // TODO: confirm store MRPs for Levpan-D, Levranbe-D, Livnim-P and Painac-SP (pack art shows blanks)
    { id: 23, name: "Levpan-D Capsules", salt: "Pantoprazole 40mg + Domperidone 30mg", company: "Levana Lifesciences", pack: "Strip of 10 capsules", category: "digestive", price: 120, mrp: 125, rx: true, tag: "New", icon: "carton", photo: "levpan-d" },
    { id: 24, name: "Levmulti Syrup", salt: "Multivitamin, Lycopene, Lysine and Vitamin C", company: "Levana Lifesciences", pack: "200 ml syrup bottle", category: "vitamins", price: 180, mrp: 180, rx: false, tag: "New", icon: "bottle", photo: "levmulti" },
    { id: 25, name: "Livnim-P Tablets", salt: "Nimesulide 100mg + Paracetamol 325mg", company: "Levana Lifesciences", pack: "Strip of 10 tablets", category: "pain", price: 55, mrp: 60, rx: true, tag: "New", icon: "blister", photo: "livnim-p" },
    { id: 26, name: "Levcalci-D Tablets", salt: "Calcium Citrate, Magnesium, Zinc and Vitamin D3", company: "Levana Lifesciences", pack: "Strip of 10 tablets", category: "vitamins", price: 70, mrp: 70, rx: false, tag: "New", icon: "blister", photo: "levcalci-d" },
    { id: 27, name: "Painac-SP Tablets", salt: "Aceclofenac 100mg + Paracetamol 325mg + Serratiopeptidase 15mg", company: "Levana Lifesciences", pack: "Strip of 10 tablets", category: "pain", price: 110, mrp: 110, rx: true, tag: "New", icon: "blister", photo: "painac-sp" },
    { id: 28, name: "Levdenzy Syrup", salt: "Fungal Diastase and Papain", company: "Levana Lifesciences", pack: "200 ml syrup bottle", category: "digestive", price: 155, mrp: 155, rx: false, tag: "New", icon: "bottle", photo: "levdenzy" },
    { id: 29, name: "Lavace-SP Tablets", salt: "Aceclofenac 100mg + Paracetamol 325mg + Serratiopeptidase 15mg", company: "Levana Lifesciences", pack: "Strip of 10 tablets", category: "pain", price: 110, mrp: 110, rx: true, tag: "New", icon: "blister", photo: "lavace-sp" },
    { id: 30, name: "Levranbe-D Capsules", salt: "Rabeprazole 20mg + Domperidone 30mg", company: "Levana Lifesciences", pack: "Strip of 10 capsules", category: "digestive", price: 130, mrp: 135, rx: true, tag: "New", icon: "carton", photo: "levranbe-d" },
    { id: 31, name: "Lev Gold Tablets", salt: "Vitamins, Minerals and Zinc supplement", company: "Levana Lifesciences", pack: "Strip of 10 tablets", category: "vitamins", price: 135, mrp: 135, rx: false, tag: "New", icon: "blister", photo: "lev-gold" },
"""

anchor = "  var PRODUCTS = [\n"
assert t.count(anchor) == 1
t = t.replace(anchor, photo_block + anchor + products)

old_card = """    return '<article class="product-card reveal">' +
      '<div class="product-card__media tint-' + p.category + '">' +
        (p.tag ? '<span class="pill-tag pill-tag--left">' + p.tag + "</span>" : "") +
        (off > 0 ? '<span class="pill-tag pill-tag--right pill-tag--off">' + off + "% off</span>" : "") +
        '<div class="product-card__icon">' + icon(p.icon) + "</div>" +
      "</div>" +"""
new_card = """    var media = p.photo
      ? '<img class="product-card__photo" src="' + PHOTOS[p.photo] + '" alt="' + p.name + ' pack" width="560" height="381" loading="lazy">'
      : '<div class="product-card__icon">' + icon(p.icon) + "</div>";
    return '<article class="product-card reveal">' +
      '<div class="product-card__media' + (p.photo ? " product-card__media--photo" : "") + " tint-" + p.category + '">' +
        (p.tag ? '<span class="pill-tag pill-tag--left">' + p.tag + "</span>" : "") +
        (off > 0 ? '<span class="pill-tag pill-tag--right pill-tag--off">' + off + "% off</span>" : "") +
        media +
      "</div>" +"""
assert t.count(old_card) == 1
t = t.replace(old_card, new_card)

APP.write_text(t, encoding="utf-8")
print("app.js updated:", len(t), "chars")
print("RESULT: PRODUCTS_ADDED_OK")
