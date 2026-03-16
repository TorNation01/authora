# AUTHORA Billing Failure Runbook

Response procedures for billing and Stripe issues.

## Stripe Webhook Failures

**Symptom**: Webhooks return 400 or events not processed.

1. **Check webhook secret**
   - `STRIPE_WEBHOOK_SECRET` or `STRIPE_WEBHOOK_SECRET_LIVE` set correctly
   - Secret matches Stripe Dashboard endpoint

2. **Check logs**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml logs api | grep -i webhook
   ```

3. **Verify signature** — Ensure raw body passed to handler; no JSON parse before verification

## Checkout Not Working

**Symptom**: User clicks upgrade, no redirect or error.

1. **Billing health**
   ```bash
   curl -H "Authorization: Bearer $ADMIN_TOKEN" https://api.your-domain/api/v1/billing/admin/health
   ```

2. **Check** `stripe_configured`, `webhook_secret_set`, `plans_with_stripe_prices`

3. **Plan price IDs** — Ensure plans have `stripe_price_id_monthly` etc. set

## Entitlement Overgrant

**Symptom**: User has access they shouldn't.

1. **Check grants** — Admin → Grants for user
2. **Revoke** incorrect grant
3. **Check promo** — Revoke promo code if needed
4. **Audit log** — Review `GET /api/v1/billing/admin/audit-log`

## Entitlement Loss

**Symptom**: Paid user lost access.

1. **Check subscription** — Stripe Dashboard
2. **Check grants** — Admin → Grants
3. **Manual grant** — Create grant if Stripe sync failed
4. **Webhook replay** — In Stripe Dashboard, resend event if needed
