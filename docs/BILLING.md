# AUTHORA Billing & Commercial Readiness

## Overview

AUTHORA includes a subscription-ready billing architecture:

- **Free plan**: 1 project, 3 books, 20 AI actions/month, 5 exports/month, DOCX/TXT only
- **Premium plan**: Unlimited projects/books, 500 AI actions/month, 50 exports/month, all formats
- **Feature gating**: AI, ghostwriter, PDF/EPUB export, publishing prep
- **Usage metering**: AI actions and exports tracked per user per month
- **Admin override**: Admins can set plan override or billing_exempt per user

## Enabling Billing

Set `FEATURE_BILLING=true` in your environment. When false (default), all users effectively get Premium (no limits).

## Database Schema

- **plans**: Tier definitions (free, premium) with limits and features JSON
- **subscriptions**: User's current plan (manual or Stripe)
- **usage_records**: Metered usage per user/period/metric
- **users.plan_override_id**: Admin-assigned plan override
- **users.billing_exempt**: Skip all limits

## API Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /api/v1/billing/status` | Yes | Current plan, usage, limits |
| `GET /api/v1/billing/plans` | No | List available plans |
| `PATCH /api/v1/billing/admin/users/:id/plan` | Admin | Set plan override or billing_exempt |
| `POST /api/v1/billing/webhooks/stripe` | No | Stripe webhook (placeholder) |
| `POST /api/v1/billing/checkout/create` | Yes | Create checkout session (placeholder) |

## Admin Override

Admins can override a user's plan:

```bash
curl -X PATCH "https://api.example.com/api/v1/billing/admin/users/{user_id}/plan" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_slug": "premium"}'   # or {"billing_exempt": true}
```

To clear override: `{"plan_slug": ""}`

## Stripe Integration (Future)

When integrating Stripe:

1. Set `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PREMIUM_PRICE_ID`
2. Implement `POST /api/v1/billing/webhooks/stripe` to handle:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
3. Implement `POST /api/v1/billing/checkout/create` to create Stripe Checkout sessions
4. Link `plans.stripe_price_id` to your Stripe Price IDs

## Tenant-Aware Architecture

When `FEATURE_TENANT_AWARE=true` (Anakatech mode), billing can be resolved at the org/tenant level. The current implementation is user-scoped; extend `get_user_plan` to check tenant entitlements when needed.
