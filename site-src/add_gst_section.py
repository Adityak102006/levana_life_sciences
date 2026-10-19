"""Adds the trust documents section (GST registration certificate) to the About page.
The site copy is a verification copy: partner passport photos are withheld (DPDP rule).
Also replaces the GSTIN placeholder with the real GSTIN from the certificate.
"""
from pathlib import Path

BUILD = Path("/home/user/site-src/build.py")
t = BUILD.read_text(encoding="utf-8")

# --- real GSTIN from Form GST REG-06
assert t.count("09ABCDE1234F1Z5") == 3
t = t.replace("09ABCDE1234F1Z5", "09AANFL0727C1ZG")

# --- GST card button becomes a real link to the documents section
old_btn = '<span class="value">GSTIN<br>09AANFL0727C1ZG</span>\n<button class="btn btn--ghost btn--sm js-demo-doc" type="button">View certificate</button>'
new_btn = '<span class="value">GSTIN<br>09AANFL0727C1ZG</span>\n<a class="btn btn--ghost btn--sm" href="#documents">View certificate</a>'
assert t.count(old_btn) == 1
t = t.replace(old_btn, new_btn)

# --- document asset tokens and chain
old_const = 'IMG_LOGO = img_uri("logo.jpg")\nIMG_MARK = img_uri("mark.png")'
new_const = ('IMG_LOGO = img_uri("logo.jpg")\nIMG_MARK = img_uri("mark.png")\n'
             '# FIX-MEDIA: GST registration certificate, redacted verification copy for the documents section\n'
             'DOC_GST_PDF = "data:application/pdf;base64," + base64.b64encode((ROOT / "img" / "gst-certificate.pdf").read_bytes()).decode("ascii")\n'
             'DOC_GST_P1 = img_uri("gst-p1.jpg")\nDOC_GST_P2 = img_uri("gst-p2.jpg")\nDOC_GST_P3 = img_uri("gst-p3.jpg")')
assert t.count(old_const) == 1
t = t.replace(old_const, new_const)

old_chain = '        .replace("__IMG_MARK__", IMG_MARK)'
new_chain = ('        .replace("__IMG_MARK__", IMG_MARK)\n'
             '        .replace("__DOC_GST_PDF__", DOC_GST_PDF)\n'
             '        .replace("__DOC_GST_P1__", DOC_GST_P1)\n'
             '        .replace("__DOC_GST_P2__", DOC_GST_P2)\n'
             '        .replace("__DOC_GST_P3__", DOC_GST_P3)')
assert t.count(old_chain) == 1
t = t.replace(old_chain, new_chain)

# --- the documents section on the About page
SECTION = """</section>
<!-- FIX: trust documents section, redacted verification copies with PDF download -->
<section class="section docs-section" id="documents" aria-labelledby="docs-title">
<div class="container">
<div class="sec-head">
<div>
<span class="label">Original documents</span>
<h2 id="docs-title">Our certificates, <em>on record.</em></h2>
</div>
<div class="sec-head__side"><p>Government issued verification copies for our customers. Personal photos on documents are withheld for privacy. Originals are kept at our store and can be inspected in person at any time.</p></div>
</div>
<div class="doc-card reveal">
<div class="doc-card__head">
<div>
<h3>GST Registration Certificate</h3>
<p class="doc-card__meta">Form GST REG-06, issued by the Government of India</p>
</div>
<div class="doc-card__actions">
<a class="btn btn--primary btn--sm" href="__DOC_GST_PDF__" download="Levana-Lifesciences-GST-Registration.pdf">Download PDF</a>
<a class="btn btn--ghost btn--sm" href="__DOC_GST_PDF__" target="_blank" rel="noopener">Open full size</a>
</div>
</div>
<div class="spec-rows">
<div class="spec-row"><dt>GSTIN</dt><dd>09AANFL0727C1ZG</dd></div>
<div class="spec-row"><dt>Legal name</dt><dd>LEVANA LIFESCIENCES</dd></div>
<div class="spec-row"><dt>Valid from</dt><dd>02 April 2026, no expiry</dd></div>
<div class="spec-row"><dt>Issuing office</dt><dd>Assistant Commissioner, Gonda Sector-4</dd></div>
</div>
<div class="doc-pages">
<a class="doc-page" href="__DOC_GST_PDF__" target="_blank" rel="noopener" aria-label="Open GST certificate, page 1"><img src="__DOC_GST_P1__" alt="GST registration certificate, Form GST REG-06, page 1" width="820" height="1159" loading="lazy" onerror="this.onerror=null;this.src='__IMG_FALLBACK__'"></a>
<a class="doc-page" href="__DOC_GST_PDF__" target="_blank" rel="noopener" aria-label="Open GST certificate, page 2"><img src="__DOC_GST_P2__" alt="GST registration certificate, Annexure A, page 2" width="820" height="1159" loading="lazy" onerror="this.onerror=null;this.src='__IMG_FALLBACK__'"></a>
<a class="doc-page" href="__DOC_GST_PDF__" target="_blank" rel="noopener" aria-label="Open GST certificate, page 3"><img src="__DOC_GST_P3__" alt="GST registration certificate, Annexure B, page 3, partner photos withheld" width="820" height="1159" loading="lazy" onerror="this.onerror=null;this.src='__IMG_FALLBACK__'"></a>
</div>
<p class="doc-card__note">Page 3 carries passport photographs of the firm&#39;s partners. Those photos are withheld on this website in line with our privacy policy and the Digital Personal Data Protection Act.</p>
</div>
</div>
</section>
<section class="section section--flush"
"""

anchor = '</section>\n<section class="section section--flush" aria-labelledby="rules-title">'
assert t.count(anchor) == 1
t = t.replace(anchor, SECTION + ' aria-labelledby="rules-title">')

BUILD.write_text(t, encoding="utf-8")
print("build.py updated:", len(t), "chars")
print("RESULT: GST_SECTION_OK")
