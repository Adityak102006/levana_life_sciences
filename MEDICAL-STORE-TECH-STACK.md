# 💊 Digital Medical Store — Recommended Tech Stack & Build Plan (2026)

> Scope: custom-coded online medical store with medicine catalog, cart + payments + delivery,
> prescription upload & pharmacist verification, and a compliance/trust section displaying your
> ID, drug license, GST, pharmacist registration, etc.
> Budget: flexible — options shown at three price tiers.

---

## 1. The Short Answer — Best Stack for This Project

| Layer | My Top Pick (2026) | Why |
|---|---|---|
| **Framework** | **Next.js (App Router) + React + TypeScript** | One codebase for storefront + admin + API. SEO for medicine pages (Google search = free traffic), fast pages, PWA-capable. |
| **UI** | **Tailwind CSS + shadcn/ui** | Professional look quickly; works for both customer site and admin panel. |
| **Database** | **PostgreSQL** (Supabase or Neon) | Orders, prescriptions, invoices, batch/expiry, GST — all strongly relational. Postgres is the right tool. |
| **ORM** | **Prisma** | Type-safe queries, easy migrations, great DX with TypeScript. |
| **Auth** | **Auth.js (NextAuth v5)** + phone OTP (MSG91) + email | Indian users expect mobile-OTP login. Add Google login as convenience. |
| **File storage** | **Cloudflare R2 or AWS S3 (Mumbai)** — private buckets + signed URLs | Prescriptions & license PDFs are sensitive. Never on public URLs. |
| **Payments** | **Razorpay** (UPI, cards, netbanking, wallets) + **Cash on Delivery** | Standard for India. ~2% + GST per txn. Also supports UPI intent on mobile. |
| **Search** | Postgres full-text + `pg_trgm` first → **Meilisearch** later | Customers search by *salt name* (e.g. "paracetamol") as well as brand — fuzzy search is essential. |
| **Cache / jobs** | **Redis (Upstash) + BullMQ** | Carts, OTP rate-limiting, order jobs, **license-expiry reminders**, emails. |
| **Notifications** | **WhatsApp Cloud API** (via Wati/Interakt/Gupshup) + **MSG91 SMS** + **Resend** (email) | Order + prescription updates on WhatsApp — highest open rate in India. |
| **GST invoicing** | Server-side PDF generation (react-pdf / Puppeteer) with GST breakup + HSN codes | Every order needs a compliant tax invoice. |
| **Delivery** | **Shiprocket / Delhivery** (shipped orders), **Dunzo / Porter API** (hyperlocal same-day in your city) | Start with hyperlocal + manual dispatch; add APIs in Phase 2. |
| **Admin panel** | Custom Next.js admin with **RBAC** (Owner / Pharmacist / Store staff / Delivery) | The pharmacist verification queue lives here. |
| **Hosting** | **Vercel** (app) + Neon/Supabase (DB) + R2 (files) — *or* Docker + **Coolify** on a VPS for tighter cost control | Managed stack = least headache. VPS = cheaper at scale. Prefer **Mumbai (ap-south-1)** regions for data residency. |
| **Monitoring** | **Sentry** (errors) + **PostHog** (analytics) + **Better Uptime** | Free tiers are enough to start. |
| **CI/CD** | **GitHub Actions** | Auto-deploy on push. |
| **Mobile app (later)** | PWA first → **React Native (Expo)** in Phase 3 | Don't build an app on day one. |

### Good alternatives (pick if they match your skills)

| If you know / prefer… | Use instead | Notes |
|---|---|---|
| Python | **Django + DRF** + React/HTMX | Django Admin gives you inventory + Rx queue almost free. |
| PHP | **Laravel + Livewire** | Cheapest shared hosting options; huge ecosystem. |
| Want fastest MVP | **Next.js + Supabase** (DB + Auth + Storage in one) | Least glue code to write. |
| Vue ecosystem | **Nuxt 3 + Nitro** | Equally fine; slightly smaller hiring pool. |

**Avoid:** MongoDB-first designs (this is relational data), custom payment logic, plain shared
"cPanel PHP" hosting, and Wix/Shopify (they can't do the prescription + compliance workflow properly).

---

## 2. What Gets Built (Module Map)

### 🛍️ Storefront (customer-facing)
- Home, medicine catalog with categories (Allopathy / Ayurveda / OTC / Devices / Wellness)
- Smart search: brand name, **salt/composition**, manufacturer, category
- Product pages: salt info, manufacturer, **MRP (NPPA requires price display)**, stock, substitute suggestions
- Cart, checkout (address, slot for delivery), **Razorpay + COD**
- Customer account: orders, re-order button, saved addresses, **prescriptions vault**
- **"Upload Prescription" flow** (camera + PDF)
- **Subscription / auto-refill** for monthly chronic medicines (killer feature for retention)
- Trust & Compliance page (see §4)
- Policy pages: Privacy (DPDP-compliant), Terms, Shipping, Return/Refund, Cancellation
- 24×7 helpline number + grievance form (required by draft e-pharmacy rules)

### 👨‍⚕️ Pharmacist & Operations (admin)
- Dashboard: today's orders, pending Rx verifications, low stock, near-expiry batches
- **Prescription verification queue** → approve / edit qty / partial / reject (with reason)
- Inventory: products, batches, **expiry tracking (FEFO)**, stock adjustments, CSV import
- Order lifecycle: New → Rx Verified → Packed → Dispatched → Delivered / Returned
- GST invoice generation + download
- Role-based access + **audit log** (who viewed/approved which prescription — health data!)
- Document vault: license/ID uploads with **expiry reminders at 60/30/7 days**
- Content pages (CMS-lite) for About, Doctor/Team, health articles (SEO)

### 🔁 Background jobs (BullMQ)
- Rx review reminders to pharmacist
- Order status WhatsApp/SMS
- Prescription expiry / re-upload requests
- **License & certificate renewal alerts**
- Refill reminders for subscription customers
- Abandoned-cart nudges

---

## 3. Suggested Data Model (core tables)

`users` · `addresses` · `products` (brand, salt, manufacturer, hsn, gst_slab, schedule_class, mrp) ·
`inventory_batches` (batch_no, expiry, qty) · `prescriptions` (file_url, status, verified_by) ·
`prescription_items` · `orders` · `order_items` · `invoices` · `payments` · `subscriptions` ·
`compliance_documents` (type, file_url, expiry_date) · `audit_logs` · `notifications`

Key constraint: **`schedule_class`** on every product (`OTC` / `H` / `H1` / `X`) —
the app must **hard-block** checkout for `X` and narcotics, and **force Rx verification** for `H`/`H1`.

---

## 4. The Compliance & Trust Module (your ID + license certificates)

### What to show publicly (Trust page + footer of every page)
- ✅ Pharmacy legal name, physical address (Kichha, Uttarakhand), phone & email
- ✅ **Retail Drug Licence number (Form 20 / Form 21)** + issuing authority
- ✅ Pharmacist-in-charge name + **State Pharmacy Council registration number**
- ✅ GSTIN
- ✅ FSSAI number (only if you sell health supplements / food items)
- ✅ Watermarked copies of certificates ("For verification only — StoreName") as PDFs
- ✅ Helpline + grievance officer details

### What NOT to publish ⚠️
- ❌ Full Aadhaar / PAN / voter ID images — **redact to last 4 digits** and watermark.
  Publishing full ID proofs invites identity theft and breaks the DPDP Act, 2023.
  Keep originals in the admin document vault; show only verification copies publicly.
- ❌ Any drug "advertisement" or discount claims on medicines — the draft e-pharmacy rules
  prohibit advertising of drugs. Show information + MRP, not "SALE!!" banners on drugs.

### Built-in compliance features in the app
- Document vault with expiry dates + automated renewal reminders
- Rx retention (keep records ≥ 3 years), data **stored in India** (draft rules require it —
  choose Mumbai regions: Vercel `bom1`, AWS `ap-south-1`, Supabase Mumbai)
- Audit trail of every prescription access
- Schedule H1 separate sale register (exportable CSV/PDF)
- GST-compliant invoices with HSN codes

### Legal status note (India, Oct 2026) — plan accordingly
- The 2018 **Draft E-Pharmacy Rules** (CDSCO registration, Form 18AA, ₹50,000 fee, one license
  valid nationwide, data localisation, ban on Schedule X/narcotics online) are **still not
  notified** — e-pharmacy remains in a grey zone and platforms operate through licensed
  brick-and-mortar premises. ([draft status](https://en.wikipedia.org/wiki/Drugs_and_Cosmetics_Rules,_1945), [legal guide 2026](https://www.nextlevelurgentcare.com/wp-content/uploads/formidable/31/Online_Pharmacy_Regulations_Legal_Guide.pdf))
- The proposed **Drugs, Medical Devices and Cosmetics Bill, 2025** would mandate licensing for
  online drug sales — build as if registration will be required. ([overview](https://www.ijpsjournal.com/article/evolving-regulatory-framework-for-e-pharmciesin-india-challenges-legal-concern))
- You still need a **Retail Drug Licence (Forms 20/21)** from the Uttarakhand State Drugs
  Control Department + a registered pharmacist. ([licence guide 2026](https://vakilsearch.com/article/drug-license-india-form-20-21-wholesale-retail-manufacturing-2026/))
- **NPPA mandates displaying the price list** on websites/apps — show MRP clearly. ([NPPA directive](https://thehealthmaster.com/2025/02/11/drug-price-list-display-is-mandatory/))
- Website must display licence number, pharmacist details, and support contact. ([compliance checklist](https://www.psrcompliance.com/blog/online-pharmacy-license-india))
- ⚠️ **Interstate shipping:** selling into other states can require licences there; start with
  Uttarakhand + local delivery, expand legally. Get a local lawyer/pharma consultant to review
  before going pan-India.

---

## 5. Architecture

```
                       ┌────────────────────────────────────────────┐
   Customers (Web/PWA) │  Next.js App (Vercel / Coolify VPS)        │
   ──────────────────► │  ├─ Storefront (SSR/SEO)                   │
                       │  ├─ Admin Panel (RBAC)                     │
                       │  └─ API Route Handlers / Server Actions    │
                       └───────┬──────────────┬─────────────────────┘
                               │              │
              ┌────────────────┘              └────────────────┐
              ▼                                                ▼
   ┌─────────────────────┐                          ┌─────────────────────┐
   │ PostgreSQL          │                          │ Redis (Upstash)     │
   │ (Neon / Supabase)   │                          │ cache · OTP · queue │
   └─────────────────────┘                          └──────────┬──────────┘
              │                                                │
              │              ┌─────────────────────────────────┘
              │              ▼
              │   ┌─────────────────────┐
              │   │ BullMQ Workers      │──► WhatsApp API / MSG91 SMS / Email
              │   │ jobs & cron         │──► Expiry & refill reminders
              │   └─────────────────────┘
              ▼
   ┌─────────────────────┐      ┌──────────────┐      ┌─────────────────┐
   │ R2 / S3 (private)   │      │ Razorpay     │      │ Shiprocket /    │
   │ Rx + certificates   │      │ UPI/cards    │      │ Dunzo delivery  │
   │ signed URLs only    │      │ webhooks     │      │ APIs (Phase 2)  │
   └─────────────────────┘      └──────────────┘      └─────────────────┘
```

---

## 6. Budget Tiers (build cost, excluding inventory)

### 🟢 Tier 1 — Bootstrap / DIY (≈ ₹10,000 – ₹25,000 + your time)
- You code (or a friend does) with the stack above on **free tiers**: Vercel free, Supabase/Neon
  free, R2 free 10 GB, Upstash free
- Costs: domain (~₹800–1,200/yr), SMS/WhatsApp usage (~₹1–3 per order msg), Razorpay 2% per txn
- **Running cost: ~₹1,000–3,000/month** at low order volume
- Timeline: 6–10 weeks part-time

### 🟡 Tier 2 — Freelancer MVP (≈ ₹60,000 – ₹1,80,000)
- Custom design + all Phase 1 features done for you
- Running cost: ~₹2,000–6,000/month (Vercel Pro, WhatsApp API, SMS, monitoring)
- Timeline: 4–8 weeks

### 🔴 Tier 3 — Pro build (≈ ₹2,00,000 – ₹5,00,000)
- Polished UX, OCR prescription pre-fill, PWA, subscriptions, delivery API integrations,
  proper QA + security hardening, load-tested
- Consider a small agency or 2-dev team. Timeline: 2–4 months

### 🚀 Phase 3 — Marketplace / multi-vendor / mobile app (₹5,00,000+)
- Vendor onboarding, commission engine, split payments (Razorpay Route), React Native app
- ⚠️ If you want multi-vendor **from day one**, tell me — it changes the data model (vendor
  scoping, payouts, per-vendor licences). Everything above is scoped as **single store first**.

---

## 7. Delivery Roadmap

| Phase | Weeks | Deliverables |
|---|---|---|
| **0 — Setup** | 1–2 | Drug licence + GST ready, domain, brand assets, product CSV (brand, salt, MRP, HSN, schedule class, batch/expiry), design tokens |
| **1 — MVP** | 3–10 | Catalog + smart search, auth (OTP), cart, Razorpay + COD, Rx upload + pharmacist queue, GST invoices, admin panel, Trust/compliance pages, WhatsApp/SMS order updates |
| **2 — Growth** | 11–16 | Subscriptions/auto-refill, delivery integrations (Dunzo/Shiprocket), OCR pre-fill, PWA, reviews, loyalty points, analytics dashboards |
| **3 — Scale** | 4–6 mo | Multi-vendor (if wanted), React Native app, teleconsultation partners, pan-India expansion (state licence compliance) |

---

## 8. Suggested Project Structure (monorepo)

```
medical-store/
├── apps/
│   └── web/                  # Next.js: storefront + admin + API
│       ├── app/
│       │   ├── (store)/       # public storefront pages
│       │   ├── (admin)/       # dashboard, Rx queue, inventory
│       │   └── api/           # webhooks (Razorpay), route handlers
│       ├── components/
│       └── lib/               # auth, rbac, invoice, notify
├── packages/
│   ├── db/                    # Prisma schema + migrations + seed
│   └── ui/                    # shared UI components
├── workers/                   # BullMQ job processors
├── docs/                      # this plan, API notes
└── docker-compose.yml         # local Postgres + Redis
```

---

## 9. Day-One Checklist

1. ☐ Retail Drug Licence (Form 20/21) — Uttarakhand State Drugs Control Dept.
2. ☐ Registered pharmacist on payroll (licence condition + Rx verification)
3. ☐ GST registration + decide HSN/tax slabs with a CA
4. ☐ FSSAI (only if selling supplements/food items)
5. ☐ Razorpay merchant account (needs business KYC + licence)
6. ☐ Domain + professional email (Google Workspace / Zoho)
7. ☐ Redacted, watermarked copies of certificates for the Trust page
8. ☐ Product catalog CSV (include **salt composition + schedule class** for every SKU)
9. ☐ Privacy policy + terms reviewed by a lawyer (DPDP Act compliance)
10. ☐ Decide Tier 1/2/3 and start Phase 0

---

## 10. Deployment: Vercel vs Hostinger (verified Oct 2026)

### ⚠️ First, which Hostinger?
| Hostinger product | Verdict for this project |
|---|---|
| **Shared / Cloud web hosting** (₹69–249/mo "Premium/Business" plans) | ❌ **No** — built for WordPress/PHP. Cannot properly run Next.js + Postgres + Redis + background workers. |
| **Hostinger KVM VPS** (₹449–599/mo, full Ubuntu + root + Docker) | ✅ **Yes** — can host the *entire* stack, incl. workers, and has a **Mumbai data centre**. |

### Head-to-head

| Factor | Vercel (Pro) | Hostinger KVM VPS (Mumbai) |
|---|---|---|
| Fits Next.js | ⭐ Perfect (made for it) | Good (run via Docker/Coolify/PM2) |
| Commercial use | ❌ Free Hobby banned — **Pro required, $20/mo per seat** (~₹1,700) | ✅ Any plan OK |
| Running cost (this project) | ~₹2,000–4,000/mo (seat + usage credit + external DB/Redis/jobs) | ~₹450–900/mo all-in (app + Postgres + Redis + workers on one box) |
| Surprise bills | Possible (usage-based compute/CDN overages) | None (flat price) |
| Background jobs (BullMQ: Rx reminders, licence expiry, WhatsApp) | ❌ No persistent processes — needs Inngest/QStash (extra service) | ✅ Native — workers just run |
| Data residency (India rule in draft e-pharmacy rules) | Functions can run in Mumbai (`bom1`); DB must be Supabase Mumbai or similar | ✅ Everything physically in Mumbai |
| Server management | ✅ Zero ops — Vercel handles everything | ❌ You manage updates, SSL, firewall, backups (use Coolify/Dokploy to simplify) |
| Uptime / DDoS | Enterprise-grade global edge included | Single box + free Cloudflare in front recommended |
| Scaling | Automatic (with usage charges) | Manual resize of the VPS |
| Lock-in | Mild (Vercel-specific APIs) | None |

### Cost reality check
- **Vercel route:** Hobby is not an option for a shop that sells — commercial use requires
  Pro at **$20/mo per developer seat** with a $20 usage credit, metered compute beyond that
  ([pricing](https://vercel.com/pricing), [Hobby commercial ban](https://costbench.com/software/developer-tools/vercel/)).
  Add Supabase/Upstash/Inngest free tiers → realistically **₹2,000–4,000/mo**.
- **Hostinger route:** KVM 2 (2 vCPU / 8 GB — comfortable for app + DB + Redis + workers)
  ≈ **$8.99/mo on 1–2 yr promo, ~$15/mo renewal** ([pricing check](https://www.brandrums.com/blog/host-nodejs-app-hostinger-vps-2026/));
  KVM 1 (4 GB) works if tuned. Mumbai DC confirmed
  ([review](https://gb.hostadvice.com/hosting-company/hostinger-reviews/hostinger-india-hosting-review/)).

### Decision rule
- **Pick Vercel Pro** if: you (or your developer) want zero server management, budget is
  ~₹2–4k/month is fine, and reliability matters more than cost. Use Supabase Mumbai for DB
  and Inngest/QStash for jobs. Set function region to `bom1`.
- **Pick Hostinger VPS** if: you want the lowest fixed cost, everything (including patient
  data) inside India on your own server, and a freelancer can set up Docker + Coolify once.
  Recommended: **KVM 2, Mumbai**, weekly backups + offsite snapshot, Cloudflare DNS/proxy in front.
- **My pick for this project:** Hostinger VPS (Mumbai) if you have any technical support —
  the persistent workers (prescription/reminders) and flat pricing fit a pharmacy system
  better. Vercel if nobody will ever touch a server.

---

*Prepared: 17 October 2026. Regulatory notes reflect Indian law status as of this date —
re-verify with a professional before launch, especially if the Drugs, Medical Devices and
Cosmetics Bill, 2025 is notified.*
