# AUTHORA Pricing and Billing — Summary

## 1. Pricing Page Summary

### Structure

The pricing page (`/pricing`) is a production-ready marketing page with:

- **Pricing Hero** — Headline "Plans for every kind of writer", subheadline, supporting line, Start Free / Compare Plans CTAs, "Upgrade anytime as your writing grows"
- **Plan Cards** — Monthly/Yearly toggle with "Save with yearly billing", 5 plans:
  - **Free** — $0 forever
  - **Starter** — $12/mo or $108/year
  - **Pro** — $24/mo or $216/year (Most Popular badge)
  - **Studio** — $49/mo or $468/year
  - **Founder Lifetime** — $349 once (Limited Offer badge)
- **Plan Comparison Table** — 19 feature rows across all plans with value notes
- **Value Section** — "More than a writing app" with 6 highlights
- **AI Section** — "AI that supports your writing, not replaces your voice"
- **Accountability Section** — "Built to help you finish"
- **FAQ Section** — 10 polished FAQs

### Components

| Component | Path | Purpose |
|-----------|------|---------|
| PricingHero | `(marketing)/pricing/PricingHero.tsx` | Hero with CTAs |
| PricingPlanCards | `(marketing)/pricing/PricingPlanCards.tsx` | Plan cards with toggle |
| PricingComparisonTable | `(marketing)/pricing/PricingComparisonTable.tsx` | Feature comparison |
| PricingValueSection | `(marketing)/pricing/PricingValueSection.tsx` | Value differentiator |
| PricingAISection | `(marketing)/pricing/PricingAISection.tsx` | AI positioning |
| PricingAccountabilitySection | `(marketing)/pricing/PricingAccountabilitySection.tsx` | Accountability |
| PricingFAQ | `(marketing)/pricing/PricingFAQ.tsx` | FAQ accordion |

### Content Source

- `apps/web/src/content/pricing-copy.ts` — `DEFAULT_PLANS`, `PLAN_COMPARISON_ROWS`, `PLAN_COMPARISON_MATRIX`

---

## 2. Plan Comparison Summary

### Plans and Pricing

| Plan | Monthly | Yearly | Lifetime | Value Note |
|------|---------|--------|----------|------------|
| Free | $0 | $0 | — | A simple place to start |
| Starter | $12 | $108 | — | Best for building consistency |
| Pro | $24 | $216 | — | Best for finishing books |
| Studio | $49 | $468 | — | Best for serious output |
| Founder Lifetime | — | — | $349 | Best for early believers |

### Comparison Rows

- Active book projects
- Writing editor
- Outlining tools
- Fiction / non-fiction planning
- Notes and research
- AI assistance
- Ghostwriter tools
- Finish Mode
- Export options
- Progress tracking
- Accountability tools
- Smart search / RAG
- Story Integrity Engine
- Story Density Engine
- Premium AI routing
- Collaboration tools
- Priority workflows
- Lifetime option

---

## 3. Billing Page Summary

### Location

`/dashboard/billing` — Logged-in user billing experience (when `feature_flags.billing` is true).

### Features

- **Current plan** — Plan name, Lifetime Access badge when applicable
- **Access source** — Complimentary Access, Plan Override, Stripe subscription, or Free plan
- **Renewal date** — When subscription renews (or "Access Ends" for grants)
- **Manage billing** — Stripe Customer Portal (when user has Stripe customer)
- **Change plan** — Link to `/pricing`
- **Upgrade** — Link to pricing when `can_upgrade`
- **Usage overview** — AI allowance, exports, storage, ghostwriter (via UsageDisplay)
- **Plan comparison** — Link to `/pricing#compare-plans`

### API

- `GET /api/v1/billing/status` — Returns plan, usage, `subscription` (period_end, cancel_at_period_end, billing_interval, is_lifetime, has_stripe_customer), `access_source`

---

## 4. Admin Grants / Access Code Summary

### Manual Access Grants (`/dashboard/admin/grants`)

- **Heading** — "Billing, Plans, and Access" / "Manual Access Grants"
- **User search** — Search by email, select user
- **Plan Override** — free, starter, pro, studio, founder_lifetime
- **Duration** — 1 month, 3 months, 6 months, 12 months, Lifetime Access, Custom
- **Grant Reason** — Family, Founder, Beta tester, Partner, Internal use, Scholarship, Support resolution, Custom
- **Access Type** — Paid, Discounted, Complimentary Access
- **Override Stripe** — Yes/No
- **On Expiry** — Revert to previous, Revert to Free, Prompt for billing
- **Internal Notes** — Optional
- **Actions** — Create grant, Revoke, Convert to Lifetime Access
- **Grant history** — Access Ends date, revoked status

### Special Access Codes (`/dashboard/admin/promo-codes`)

- **Heading** — "Special Access Codes"
- **Code string** — Unique code (e.g. FOUNDER50)
- **Tier granted** — starter, pro, studio, founder_lifetime
- **Free or discounted access** — free, percentage, fixed
- **Duration** — months
- **Max uses** — Optional limit
- **Internal Notes** — Optional
- **Redemption tracking** — use_count / max_uses
- **Revoke** — Disable code

### API Endpoints

- `POST /api/v1/billing/admin/grants` — Create grant
- `GET /api/v1/billing/admin/grants/{user_id}` — List grants
- `POST /api/v1/billing/admin/grants/{id}/revoke` — Revoke grant
- `POST /api/v1/billing/admin/grants/{id}/extend` — Extend grant
- `POST /api/v1/billing/admin/grants/{id}/convert-lifetime` — Convert to lifetime
- `POST /api/v1/billing/admin/promo-codes` — Create code
- `GET /api/v1/billing/admin/promo-codes` — List codes
- `POST /api/v1/billing/admin/promo-codes/{id}/revoke` — Revoke code

---

## 5. Stripe Integration Summary

### Architecture

- **Product/price abstraction** — Plan model has `stripe_price_id_monthly`, `stripe_price_id_yearly`, `stripe_price_id_lifetime`
- **Checkout flow** — `POST /api/v1/billing/checkout/create` with `plan_slug`, `billing_interval`, `promo_code` → returns `{ url, session_id }`
- **Customer portal** — `POST /api/v1/billing/customer-portal` → returns `{ url }` for managing subscription
- **Webhooks** — `POST /api/v1/billing/webhooks/stripe` handles `checkout.session.completed`, `customer.subscription.*`, `invoice.paid`, `invoice.payment_failed`
- **Coupon/promotion** — Pass `promo_code` to checkout for Stripe promotion codes
- **Subscription state** — Webhook creates/updates Subscription record; `get_user_plan` resolves effective plan
- **Failure handling** — `invoice.payment_failed` webhook; grace period support
- **Test vs live** — Inferred from `sk_test_*` / `sk_live_*`; `STRIPE_WEBHOOK_SECRET_TEST` / `STRIPE_WEBHOOK_SECRET_LIVE`

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `STRIPE_SECRET_KEY` | Checkout, portal, webhooks |
| `STRIPE_PUBLISHABLE_KEY` | Frontend (if needed) |
| `STRIPE_WEBHOOK_SECRET` | Webhook verification |
| `STRIPE_SUCCESS_URL` | Post-checkout redirect |
| `STRIPE_CANCEL_URL` | Checkout cancel redirect |
| `FEATURE_BILLING` | Enable billing UI and limits |

### Documentation

- `docs/STRIPE_SETUP.md` — Full Stripe setup guide
- `docs/WEBHOOK_SETUP.md` — Webhook configuration

---

## 6. Production Readiness Confirmation

### ✅ Implemented

- [x] Pricing page hero, plan cards, comparison table
- [x] Value, AI, accountability sections
- [x] FAQ section
- [x] Billing page with current plan, usage, manage billing
- [x] Admin manual access grants with duration, reason, access type
- [x] Admin special access codes with redemption tracking
- [x] Stripe checkout, customer portal, webhooks
- [x] Subscription info in billing status API
- [x] Premium design (black, gold, money green, white)
- [x] Responsive layout
- [x] SEO metadata for pricing page

### Domain / Routes

- **authora.studio/pricing** — Marketing pricing page
- **app.authora.studio/dashboard/billing** — Logged-in billing (when billing enabled)
- **app.authora.studio/dashboard/admin/grants** — Manual access grants
- **app.authora.studio/dashboard/admin/promo-codes** — Special access codes

**Status**: Pricing and billing are production-ready. Configure Stripe environment variables and create products/prices in Stripe Dashboard to enable live billing.
