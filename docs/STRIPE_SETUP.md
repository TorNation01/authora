# Stripe Setup for AUTHORA

AUTHORA is Stripe-ready. Configure environment variables and create products/prices in Stripe to enable live billing.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `STRIPE_SECRET_KEY` | Stripe secret key (sk_live_* or sk_test_*) | For checkout/portal |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (pk_*) | For frontend |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret (whsec_*) | For webhooks |
| `STRIPE_SUCCESS_URL` | Redirect after successful checkout | Optional, default: /billing?success=1 |
| `STRIPE_CANCEL_URL` | Redirect when checkout cancelled | Optional, default: /billing?canceled=1 |

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

Set Stripe price IDs on plans (via migration or admin):

```sql
UPDATE plans SET
  stripe_price_id_monthly = 'price_xxx',
  stripe_price_id_yearly = 'price_yyy',
  stripe_price_id_lifetime = 'price_zzz'
WHERE slug = 'starter';
-- Repeat for pro, studio, founder_lifetime
```

### 4. Configure Webhook

1. Stripe Dashboard → Developers → Webhooks → Add endpoint
2. URL: `https://your-api.example.com/api/v1/billing/webhooks/stripe`
3. Events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
4. Copy the webhook signing secret to `STRIPE_WEBHOOK_SECRET`

### 5. Webhook Handler Implementation

The current webhook handler verifies the signature and returns `{ handled: true }`. Extend `authora/services/stripe_service.py` `handle_webhook` to:

- On `checkout.session.completed`: create/update Subscription, set stripe_customer_id, stripe_subscription_id
- On `customer.subscription.updated`: sync status, period_end, cancel_at_period_end
- On `customer.subscription.deleted`: set status to canceled
- On `invoice.payment_failed`: set grace_period_end, optionally notify user

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/billing/checkout/create` | POST | Create Stripe Checkout session |
| `/api/v1/billing/customer-portal` | POST | Create Customer Portal session |
| `/api/v1/billing/webhooks/stripe` | POST | Stripe webhook (no auth) |

## Checkout Flow

1. Frontend calls `POST /api/v1/billing/checkout/create` with `{ plan_slug, billing_interval, promo_code? }`
2. API returns `{ url, session_id }` — redirect user to `url`
3. User completes payment on Stripe Checkout
4. Stripe sends `checkout.session.completed` webhook
5. API creates/updates Subscription record
6. User is redirected to success_url

## Customer Portal

For managing subscription (upgrade, downgrade, cancel, update payment):

1. Frontend calls `POST /api/v1/billing/customer-portal` with `{ return_url? }`
2. API returns `{ url }` — redirect user to Stripe Customer Portal
3. User manages subscription, returns to return_url

## Coupons and Promotion Codes

Stripe supports promotion codes. Pass `promo_code` to checkout/create when creating a session. For internal admin codes (that create entitlement grants), use the Promo Codes admin UI — those create grants directly without Stripe.
