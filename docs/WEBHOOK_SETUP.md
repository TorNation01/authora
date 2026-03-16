# Stripe Webhook Setup

Webhook verification guidance for AUTHORA billing.

## Endpoint

```
POST https://your-api-domain.com/api/v1/billing/webhooks/stripe
```

- **No authentication** — Stripe sends requests without Bearer tokens
- **Raw body required** — Signature verification needs the raw request body; do not parse as JSON before verification

## Webhook Verification

The handler verifies the `Stripe-Signature` header using your webhook signing secret:

1. Stripe signs each webhook with your secret
2. The app uses `stripe.Webhook.construct_event(payload, sig_header, webhook_secret)` to verify
3. Invalid signature → 400 response, event not processed

## Configuration

| Variable | Use |
|----------|-----|
| `STRIPE_WEBHOOK_SECRET` | Single secret for the active Stripe mode |
| `STRIPE_WEBHOOK_SECRET_TEST` | Used when `STRIPE_SECRET_KEY` is sk_test_* |
| `STRIPE_WEBHOOK_SECRET_LIVE` | Used when `STRIPE_SECRET_KEY` is sk_live_* |

If `STRIPE_WEBHOOK_SECRET` is set, it takes precedence. Otherwise the app picks test or live based on the secret key prefix.

## Stripe Dashboard Setup

1. **Developers** → **Webhooks** → **Add endpoint**
2. **Endpoint URL**: `https://api.your-domain.com/api/v1/billing/webhooks/stripe`
3. **Events to send**:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
4. **Signing secret**: Copy to `STRIPE_WEBHOOK_SECRET` (or `STRIPE_WEBHOOK_SECRET_TEST` / `STRIPE_WEBHOOK_SECRET_LIVE`)

## Test vs Live Endpoints

- **Test mode**: Create a webhook endpoint in Stripe (test mode). Use test URL and test signing secret.
- **Live mode**: Create a separate webhook endpoint in Stripe (live mode). Use production URL and live signing secret.

Use different endpoints and secrets for test and live. Never use a test webhook secret with live keys.

## Reverse Proxy / Caddy

Ensure the webhook path is:

- Reachable from the internet (Stripe’s IPs)
- Not blocked by auth middleware (the route is public)
- Allowing POST with body size up to ~100KB

Example Caddy block (if needed):

```
api.your-domain.com {
    reverse_proxy api:8000
    # Webhook route needs no special config
}
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 400 Invalid signature | Wrong secret or modified body | Use the signing secret from the Stripe webhook endpoint; ensure raw body is passed |
| 400 STRIPE_WEBHOOK_SECRET not set | Secret not configured | Set `STRIPE_WEBHOOK_SECRET` or `STRIPE_WEBHOOK_SECRET_TEST`/`STRIPE_WEBHOOK_SECRET_LIVE` |
| 503 Stripe not configured | No `STRIPE_SECRET_KEY` | Set Stripe keys to enable webhooks |
| Events not processed | Handler returns 200 but doesn’t sync | Extend `handle_webhook` in `stripe_service.py` to process `checkout.session.completed`, `customer.subscription.*`, etc. |

## Local Testing with Stripe CLI

```bash
stripe listen --forward-to localhost:8000/api/v1/billing/webhooks/stripe
```

Stripe CLI prints a webhook signing secret (whsec_...). Set it in `.env` as `STRIPE_WEBHOOK_SECRET` for local testing.
