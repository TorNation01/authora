# Admin Tier Overrides

Deployment support for AUTHORA's admin override system: manual grants, promo codes, plan overrides, and billing exemptions.

## Overview

Admins can grant access, assign tiers, and bypass billing limits through:

1. **Entitlement grants** — Time-limited or lifetime access to a plan
2. **Promo codes** — Redeemable codes that create grants or apply Stripe discounts
3. **Plan override** — Direct plan assignment on a user
4. **Billing exempt** — User bypasses all billing checks

## Admin Override Code System

### Entitlement Grants

**Create grant**: `POST /api/v1/billing/admin/grants`

| Field | Description |
|-------|-------------|
| user_id | Target user UUID |
| plan_slug | free, starter, pro, studio, founder_lifetime |
| expires_at | Optional; null = lifetime |
| duration_months | Alternative to expires_at |
| duration_years | Alternative to expires_at |
| reason | family, founder, beta_tester, partner, internal_use, scholarship, support_resolution, custom |
| access_type | paid, discounted, free |
| override_stripe | If true, grant overrides Stripe subscription |
| on_expiry | revert_previous, revert_free, prompt_billing |

**Duration-based grants**:
- **Monthly**: `duration_months: 1`
- **Yearly**: `duration_years: 1`
- **Lifetime**: Omit `expires_at`, `duration_months`, `duration_years`

**Override behavior**:
- `override_stripe=true`: Grant takes precedence over Stripe. User gets grant plan even with an active subscription.
- `override_stripe=false`: Grant fills in when no Stripe subscription (e.g. Stripe disabled or user never subscribed).

### Promo Codes

**Create code**: `POST /api/v1/billing/admin/promo-codes`

| Field | Description |
|-------|-------------|
| code | Unique string (e.g. FOUNDER50) |
| plan_slug | Tier granted on redemption |
| discount_type | free, percentage, fixed |
| duration_months, duration_years | Grant duration on redeem |
| expires_at | Code validity end |
| max_uses | Redemption limit |
| is_stripe_compatible | If true, use at Stripe checkout; if false, creates internal grant |

**Redeem**:
- User: `POST /api/v1/billing/redeem-code` with `{ code }`
- Admin for user: `POST /api/v1/billing/admin/redeem-code/{user_id}` with `{ code }`

### Plan Override

**Set plan or billing exempt**: `PATCH /api/v1/billing/admin/users/{user_id}/plan`

```json
{ "plan_slug": "studio", "billing_exempt": false }
```

- `plan_slug: ""` clears override
- `billing_exempt: true` bypasses all limits

## Billing Admin Safeguards

- **Audit log**: All grant create/revoke, promo create/revoke, and code redemptions are logged to `entitlement_audit_log`. View via `GET /api/v1/billing/admin/audit-log`.
- **Admin-only**: All override endpoints require `is_admin=true`.
- **Revoke, don't delete**: Revoking a grant or promo code disables future use but preserves history.

## Deployment

1. Ensure at least one admin user exists (setup wizard or seed).
2. Enable billing: `FEATURE_BILLING=true`.
3. Admin UI: Dashboard → Admin → Grants, Promo Codes.
4. API: Use the endpoints above for automation or custom tooling.

## Use Cases

| Use case | Approach |
|----------|----------|
| Family member gets Studio lifetime | Grant with plan=studio, duration_years=999 or expires_at=null |
| Beta tester gets Pro 6 months | Promo code, plan=pro, duration_months=6, max_uses=100 |
| Founder 50% off first year | Stripe coupon + is_stripe_compatible promo code |
| Support resolution: 1 month Pro | Grant with duration_months=1, reason=support_resolution |
| VIP always on Studio | plan_override_id=studio or billing_exempt=true |
