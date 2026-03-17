# AUTHORA Pricing UI — Production-Ready Summary

## 1. Pricing Page UI Summary

The pricing page (`/pricing`) is a premium, high-converting SaaS flow built on the AUTHORA brand system (black, gold, money green, white).

**Structure:**
- **Pricing Hero** — Strong title, supporting copy, monthly/yearly toggle, Start Free + Compare Plans CTAs
- **Plan Cards** — Free, Starter, Pro, Studio, Founder Lifetime in a responsive grid
- **Comparison Table** — Desktop table with sticky labels; mobile card fallback
- **Value Section** — “More than a writing app” with six highlight cards
- **Intelligence Section** — Story Integrity Engine, Story Density Engine, Smart search
- **AI Section** — “AI that supports your writing, not replaces your voice”
- **Accountability Section** — “Built to help you finish”
- **FAQ** — Premium accordion (same pattern as homepage)
- **Final CTA** — “Ready to finish your book?” with Start Free + View Plans

**Design:**
- Uses `[data-theme="marketing"]` tokens
- Premium cards with `shadow-card-premium`, `shadow-card-hover`
- Gold accent, money green for savings
- Clear hierarchy and spacing

---

## 2. Plan Card Summary

| Plan | Badge | Treatment | CTA |
|------|-------|-----------|-----|
| **Free** | — | Low-friction, simple card | Start Free |
| **Starter** | — | Standard card | Choose Starter |
| **Pro** | Most Popular | Highlighted with ring, scale, primary accent | Go Pro |
| **Studio** | Premium | Crown icon, premium border | Choose Studio |
| **Founder Lifetime** | Limited Offer | Amber/gold special-offer styling | Claim Founder Access |

**Features:**
- Monthly/yearly toggle in hero; cards reflect selected interval
- Annual savings shown (e.g. “Save 25% vs monthly”)
- Feature lists with checkmarks
- Stripe-ready checkout for logged-in users; register links for guests

---

## 3. Comparison UI Summary

**Desktop:**
- Full table with sticky feature column
- Story Integrity Engine and Story Density Engine rows at top with “Pro+” label
- Check / Minus / text for yes / no / limited
- Premium card styling with rounded corners

**Mobile:**
- Card-based fallback per plan
- Each card lists included features only (no “no” states)
- Story engine features emphasized

**Feature grouping:**
- Story engine rows first
- Remaining rows in logical order (projects, editor, planning, AI, export, etc.)

---

## 4. Billing & Admin UI Summary

### Billing Page (`/dashboard/billing`)

- **Current plan** — Name, Lifetime badge when applicable, cancel-at-period-end notice
- **Usage overview** — AI actions, exports, storage, ghostwriter (when enabled)
- **Billing history & payment** — Link to Stripe Customer Portal (invoices, payment method, cancel/resume)
- **Plan comparison** — Link to `/pricing#compare-plans`
- **Upgrade / Change plan** — CTAs to pricing page

### Admin Grants (`/dashboard/admin/grants`)

- **User search** — Search by email, select user
- **Create grant** — Plan, duration (lifetime, 1–12 months, custom), reason, access type, override Stripe, on-expiry, notes
- **Grant history table** — Plan, reason, expires, status, actions (Extend, Convert to Lifetime, Revoke)
- **Extend dialog** — Date picker for new expiry
- **Link to promo codes** — Cross-link to Special Access Codes

### Admin Promo Codes (`/dashboard/admin/promo-codes`)

- **Create code** — Code string, tier, discount type, max uses, duration, notes
- **Codes table** — Code, tier, uses, status, Revoke
- **Link to grants** — Cross-link to Entitlement Grants

---

## 5. Production Readiness Confirmation

The pricing UI is **production-ready**:

- [x] Premium visual treatment aligned with AUTHORA brand
- [x] Monthly/yearly toggle with clear savings
- [x] Pro as “Most Popular”, Studio as “Premium”, Founder as “Limited Offer”
- [x] Free as low-friction entry
- [x] Stripe-ready checkout flow for logged-in users
- [x] Responsive layout (desktop table, mobile cards)
- [x] Story Integrity Engine and Story Density Engine emphasized
- [x] Value/differentiation sections (more than a writing app, finish the book, AI support, writing intelligence)
- [x] FAQ accordion consistent with homepage
- [x] Final CTA with Start Free and View Plans
- [x] Billing page with plan, usage, change plan, billing portal
- [x] Admin grants and promo codes with table layouts and role-safe actions
- [x] Build passes; no blocking errors
