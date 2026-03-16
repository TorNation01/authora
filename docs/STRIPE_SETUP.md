# Stripe Setup for AUTHORA

AUTHORA is Stripe-ready. Configure environment variables and create products/prices in Stripe to enable live billing.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `STRIPE_SECRET_KEY` | Stripe secret key (sk_live_* or sk_test_*) | For checkout/portal |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (pk_live_* or pk_test_*) | For frontend |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret (whsec_*) | For webhooks |
| `STRIPE_WEBHOOK_SECRET_TEST` | Webhook secret for test mode | Optional; used when key is sk_test_* |
| `STRIPE_WEBHOOK_SECRET_LIVE` | Webhook secret for live mode | Optional; used when key is sk_live_* |
| `STRIPE_LIVE_MODE` | Force live (true) or test (false) | Optional; inferred from key prefix |
| `STRIPE_SUCCESS_URL` | Redirect after successful checkout | Optional |
| `STRIPE_CANCEL_URL` | Redirect when checkout cancelled | Optional |
| `FEATURE_BILLING` | Enable billing limits and Stripe UI | Set `true` to enable |

## Test vs Live Mode

- **Test mode**: Use `sk_test_*` and `pk_test_*` keys. No real charges. Use `STRIPE_WEBHOOK_SECRET_TEST` or `STRIPE_WEBHOOK_SECRET` with a test webhook secret.
- **Live mode**: Use `sk_live_*` and `pk_live_*` keys. Real charges. Use `STRIPE_WEBHOOK_SECRET_LIVE` or `STRIPE_WEBHOOK_SECRET` with a live webhook secret.

The app infers mode from the secret key prefix. Set `STRIPE_LIVE_MODE=true` or `false` to override.

**Production**: Always use live keys and a live webhook secret. Never use test keys in production.

## Validation

When `STRIPE_SECRET_KEY` is set in production, `validate-env.sh` warns if:
- `STRIPE_WEBHOOK_SECRET` (or `STRIPE_WEBHOOK_SECRET_LIVE`) is not set
- `STRIPE_PUBLISHABLE_KEY` is not set

## Stripe Dashboard Setup

### 1. Create Products

Create one product per plan in Stripe Dashboard → Products:

- **Starter** (monthly, yearly)
- **Pro** (monthly, yearly)
- **Studio** (monthly, yearly)
- **Founder Lifetime** (one-time)

### 2. Create Prices

For each product, create prices:

| Plan | Interval | Amount | Price ID (store in DB) |
|------|----------|--------|------------------------|
| Starter | month | $12 | price_xxx |
| Starter | year | $108 | price_xxx |
| Pro | month | $24 | price_xxx |
| Pro | year | $216 | price_xxx |
| Studio | month | $49 | price_xxx |
| Studio | year | $468 | price_xxx |
| Founder Lifetime | one_time | $349 | price_xxx |

### 3. Update Plan Records

Set Stripe price IDs on plans (via migration, admin, or SQL):

```sql
UPDATE plans SET
  stripe_price_id_monthly = 'price_xxx',
  stripe_price_id_yearly = 'price_yyy',
  stripe_price_id_lifetime = 'price_zzz'
WHERE slug = 'starter';
-- Repeat for pro, studio, founder_lifetime
```

### 4. Configure Webhook

See [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md) for full guidance.

1. Stripe Dashboard → Developers → Webhooks → Add endpoint
2. URL: `https://your-api.example.com/api/v1/billing/webhooks/stripe`
3. Events: `checkout.session.completed`, `customer.subscription.*`, `invoice.paid`, `invoice.payment_failed`
4. Copy the webhook signing secret to `STRIPE_WEBHOOK_SECRET`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/billing/checkout/create` | POST | Create Stripe Checkout session |
| `/api/v1/billing/customer-portal` | POST | Create Customer Portal session |
| `/api/v1/billing/webhooks/stripe` | POST | Stripe webhook (no auth) |
| `/api/v1/billing/admin/health` | GET | Admin: billing health check |

## Checkout Flow

1. Frontend calls `POST /api/v1/billing/checkout/create` with `{ plan_slug, billing_interval, promo_code? }`
2. API returns `{ url, session_id }` — redirect user to `url`
3. User completes payment on Stripe Checkout
4. Stripe sends `checkout.session.completed` webhook
5. API creates/updates Subscription record
6. User is redirected to success_url

## Coupons and Promotion Codes

Stripe supports promotion codes. Pass `promo_code` to checkout/create when creating a session. For internal admin codes (that create entitlement grants), use the Promo Codes admin UI — those create grants directly without Stripe.
