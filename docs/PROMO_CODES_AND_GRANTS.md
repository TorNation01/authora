# Promo Codes and Admin Grants

AUTHORA supports two complementary systems: **admin grants** (manual) and **promo codes** (redeemable by users or admins).

## Admin Grants

Direct grants by an admin. No code. See [ADMIN_ENTITLEMENTS.md](./ADMIN_ENTITLEMENTS.md).

**Use cases:** Family member, founder, beta tester, support resolution, scholarship.

## Promo Codes

Admin-created codes that users (or admins on behalf of users) can redeem.

### Create Code

**API:** `POST /api/v1/billing/admin/promo-codes`

| Field | Description |
|-------|-------------|
| code | Unique string (e.g. FOUNDER50) |
| plan_slug | Tier granted |
| discount_type | free, percentage, fixed |
| discount_value | For percentage/fixed |
| duration_months, duration_years | Grant duration |
| expires_at | Code validity end |
| max_uses | Redemption limit |
| valid_from, valid_until | Code validity window |
| allowed_user_ids | Restrict to specific users (null = open) |
| is_stripe_compatible | If true, applies Stripe discount; if false, creates internal grant |

### Redeem Code

**User self-redeem:** `POST /api/v1/billing/redeem-code` with `{ code }`

**Admin redeem for user:** `POST /api/v1/billing/admin/redeem-code/{user_id}` with `{ code }`

### Redemption Behavior

When `is_stripe_compatible=false` (default), redemption creates an `EntitlementGrant` with:
- plan_id from code
- expires_at from duration_months/years or code expires_at
- reason=promo_code, reason_custom=code string

When `is_stripe_compatible=true`, the code is intended for use at Stripe Checkout (pass as `promo_code` to checkout/create). No internal grant is created.

### Use Cases

| Use case | Config |
|----------|--------|
| Wife gets Studio lifetime free | plan=studio, discount_type=free, duration_years=999 or expires_at=null |
| Family member gets Pro 12 months | plan=pro, duration_months=12, max_uses=1 |
| Beta tester gets Starter 6 months | plan=starter, duration_months=6, max_uses=100 |
| Founder 50% off first year | is_stripe_compatible=true, create Stripe coupon, pass at checkout |
| VIP full free without checkout | plan=studio, discount_type=free, duration_years=999, allowed_user_ids=[...] |

### Revoke Code

`POST /api/v1/billing/admin/promo-codes/{id}/revoke` — disables future redemptions. Existing grants from prior redemptions remain.
