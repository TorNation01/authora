# Billing Deployment Guide

Production deployment readiness for AUTHORA billing: Stripe integration, tier control, promo codes, and subscription operations.

## Prerequisites

- `FEATURE_BILLING=true` to enable billing limits and Stripe UI
- Stripe account (test for staging, live for production)
- Plans seeded (via migrations; see [Plan/Tier Seed Data](#plan-tier-seed-data))

## Environment Configuration

### Required for Stripe

| Variable | Staging (test) | Production (live) |
|----------|----------------|-------------------|
| `STRIPE_SECRET_KEY` | sk_test_* | sk_live_* |
| `STRIPE_PUBLISHABLE_KEY` | pk_test_* | pk_live_* |
| `STRIPE_WEBHOOK_SECRET` | whsec_* (test endpoint) | whsec_* (live endpoint) |
| `STRIPE_SUCCESS_URL` | https://staging.example/billing?success=1 | https://app.authora.studio/billing?success=1 |
| `STRIPE_CANCEL_URL` | https://staging.example/billing?canceled=1 | https://app.authora.studio/billing?canceled=1 |

### Optional: Separate Test/Live Webhook Secrets

When running the same codebase against both test and live Stripe:

```
STRIPE_WEBHOOK_SECRET_TEST=whsec_test_xxx
STRIPE_WEBHOOK_SECRET_LIVE=whsec_live_yyy
```

The app selects the secret based on the key prefix (sk_test_ vs sk_live_). If you use a single `STRIPE_WEBHOOK_SECRET`, it applies to both.

## Plan/Tier Seed Data

Plans are seeded by migrations (`022_full_billing_entitlements`):

| Slug | Name | Monthly | Yearly | Lifetime |
|------|------|---------|--------|----------|
| free | Free | $0 | $0 | - |
| starter | Starter | $12 | $108 | - |
| pro | Pro | $24 | $216 | - |
| studio | Studio | $49 | $468 | - |
| founder_lifetime | Founder Lifetime | - | - | $349 |

After creating prices in Stripe, update plans with `stripe_price_id_monthly`, `stripe_price_id_yearly`, `stripe_price_id_lifetime` via SQL or admin tooling.

## Billing Webhook Runtime Config

- **Single env**: Use `STRIPE_WEBHOOK_SECRET` for the active Stripe mode.
- **Dual env**: Use `STRIPE_WEBHOOK_SECRET_TEST` and `STRIPE_WEBHOOK_SECRET_LIVE`; the app picks based on key prefix.
- **Caddy/proxy**: Ensure `/api/v1/billing/webhooks/stripe` is reachable from Stripe (no auth, POST only).

## Billing Health Checks

**Admin endpoint**: `GET /api/v1/billing/admin/health` (requires admin auth)

Returns:
- `stripe_configured`: Whether Stripe keys are set
- `webhook_secret_set`: Whether webhook verification can run
- `live_mode`: true if using live keys
- `plans_count`, `plans_with_stripe_prices`: Plan data status
- `status`: ok | degraded

Add to monitoring: alert if `status=degraded` when Stripe is expected.

## Gifted Access / Free Tier Assignment

- **Admin grants**: Create via `POST /api/v1/billing/admin/grants` — manual grants (family, founder, beta, etc.)
- **Promo codes**: Create via `POST /api/v1/billing/admin/promo-codes` — users redeem at `/billing` or admin applies for them
- **Plan override**: Admin can set `plan_override_id` or `billing_exempt` on a user via `PATCH /api/v1/billing/admin/users/{user_id}/plan`

See [ADMIN_TIER_OVERRIDES.md](ADMIN_TIER_OVERRIDES.md).

## Duration-Based Grants

Grants support:
- **Monthly**: `duration_months: 1`
- **Yearly**: `duration_years: 1`
- **Lifetime**: `expires_at: null` (no expiry)

Promo codes support `duration_months`, `duration_years`, and `expires_at`.

## Promotion Code Architecture

- **Internal codes** (`is_stripe_compatible=false`): Redemption creates an `EntitlementGrant`. No Stripe involvement.
- **Stripe codes** (`is_stripe_compatible=true`): Create a coupon in Stripe, pass code at checkout. No internal grant.

See [PROMO_CODES_AND_GRANTS.md](PROMO_CODES_AND_GRANTS.md).

## Deployment Checklist

- [ ] Set `FEATURE_BILLING=true`
- [ ] Configure Stripe env vars (secret, publishable, webhook secret, success/cancel URLs)
- [ ] Create products and prices in Stripe
- [ ] Update plan records with Stripe price IDs
- [ ] Configure webhook endpoint (see [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md))
- [ ] Verify `GET /api/v1/billing/admin/health` returns `status: ok`
- [ ] Run `./scripts/validate-env.sh production` and address Stripe warnings
