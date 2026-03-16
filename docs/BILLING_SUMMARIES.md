# Billing System Summaries

## 1. Pricing Architecture Summary

AUTHORA uses a five-tier plan structure:

- **Free** — $0, 1 project, 3 books, limited AI (20/month), basic exports (docx, txt), 50MB storage
- **Starter** — $12/mo or $108/yr, 3 projects/books, 100 AI actions, 20 exports, 200MB storage
- **Pro** — $24/mo or $216/yr, 20 projects, 50 books, 300 AI actions, 50 exports, ghostwriter (15/mo), 1GB storage, Finish Mode, semantic search
- **Studio** — $49/mo or $468/yr, unlimited projects/books, 1000 AI actions, 100 exports, 50 ghostwriter sessions, 2GB storage, premium model routing
- **Founder Lifetime** — $349 one-time, Pro-level access with fair-use AI limits (500/mo), supports future BYO-key options

Plans define `limits` (JSONB) and `features` (array). Stripe price IDs are stored per plan for monthly, yearly, and lifetime.

---

## 2. Recommended Launch Pricing Summary

| Plan | Monthly | Yearly | One-time |
|------|---------|--------|----------|
| Free | $0 | $0 | — |
| Starter | $12 | $108 (save 25%) | — |
| Pro | $24 | $216 (save 25%) | — |
| Studio | $49 | $468 (save 20%) | — |
| Founder Lifetime | — | — | $349 |

Annual billing offers ~25% savings. Founder Lifetime provides lifetime app access with fair-use AI; premium hosted AI can be gated separately if needed.

---

## 3. Stripe Integration Summary

- **Checkout:** `POST /api/v1/billing/checkout/create` — Creates Stripe Checkout session, returns redirect URL
- **Customer Portal:** `POST /api/v1/billing/customer-portal` — Manage subscription, payment method, cancel
- **Webhook:** `POST /api/v1/billing/webhooks/stripe` — Handles subscription and invoice events (signature verified)
- **Environment:** `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
- **Product/price abstraction:** Plan model stores `stripe_price_id_monthly`, `stripe_price_id_yearly`, `stripe_price_id_lifetime`
- **Trial support:** Architecture supports trials; extend webhook handler when needed

---

## 4. Admin Grants and Code System Summary

**Admin grants:** Manual entitlement overrides. Admin selects user, plan, duration (1/3/6/12 months, years, or lifetime), reason (family, founder, beta tester, etc.), and whether to override Stripe. On expiry: revert to previous plan, revert to free, or prompt billing.

**Promo codes:** Admin-created codes. Configurable: code string, tier, duration, max uses, validity window, allowed users. Redemption creates an entitlement grant (when not Stripe-compatible) or applies at Stripe Checkout. Supports: wife gets Studio lifetime, family gets Pro 12 months, beta tester gets Starter 6 months, founder 50% off (Stripe coupon), VIP full free.

**Audit:** All grant and code actions logged in `entitlement_audit_log`.

---

## 5. Entitlement Precedence Summary

Effective plan resolution order:

1. **billing_exempt** → Studio
2. **plan_override_id** (legacy) → Override plan
3. **Active admin grant (override_stripe=true)** → Grant plan
4. **Active Stripe subscription** → Subscription plan
5. **Active admin grant (override_stripe=false)** → Grant plan (when no Stripe)
6. **Lifetime subscription** → Subscription plan
7. **Expired grant fallback** → Apply on_expiry
8. **Free plan** → Default

Feature gating uses the highest valid entitlement. Admin grants do not depend on Stripe. Stripe promo codes and internal grants coexist.
