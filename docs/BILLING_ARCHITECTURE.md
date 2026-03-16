# Billing Architecture

## Overview

AUTHORA uses a tiered plan system with Stripe for payments, admin grants for overrides, and promo codes for special access.

## Plans

| Slug | Monthly | Yearly | Lifetime |
|------|---------|--------|----------|
| free | $0 | $0 | — |
| starter | $12 | $108 | — |
| pro | $24 | $216 | — |
| studio | $49 | $468 | — |
| founder_lifetime | — | — | $349 |

## Database Schema

- **plans** — Tier definitions, limits, features, Stripe price IDs
- **subscriptions** — User's current plan (Stripe or manual), status, period, billing_interval, is_lifetime
- **entitlement_grants** — Admin manual grants
- **promo_codes** — Admin-created redeemable codes
- **promo_code_redemptions** — Redemption history
- **entitlement_audit_log** — Audit trail for grants and codes
- **usage_records** — Metered usage (ai_actions, exports, ghostwriter_sessions) per user per period

## Entitlement Precedence

Effective plan is resolved in this order (highest first):

1. **billing_exempt** — User is billing exempt → Studio
2. **plan_override_id** — Legacy admin override on User
3. **Active admin grant (override_stripe=true)** — Grant overrides Stripe
4. **Active Stripe subscription** — Paid subscription
5. **Active admin grant (override_stripe=false)** — Fills in when no Stripe
6. **Lifetime subscription** — One-time purchase
7. **Expired grant fallback** — Apply on_expiry (revert_previous, revert_free, prompt_billing)
8. **Free plan** — Default

## Feature Gates

- `has_feature(db, user_id, feature)` — Check plan features array
- `check_project_limit`, `check_book_limit`, `check_ai_action_limit`, `check_export_limit`, `check_ghostwriter_limit`, `check_storage_limit` — Enforce limits from plan

## Limits by Plan

| Limit | Free | Starter | Pro | Studio | Founder |
|-------|------|---------|-----|--------|---------|
| projects | 1 | 3 | 20 | 999 | 999 |
| books | 3 | 3 | 50 | 999 | 999 |
| ai_actions/month | 20 | 100 | 300 | 1000 | 500 |
| exports/month | 5 | 20 | 50 | 100 | 50 |
| ghostwriter/month | 0 | 0 | 15 | 50 | 25 |
| storage_mb | 50 | 200 | 1024 | 2048 | 1024 |

## Grace Period

On payment failure, Stripe may allow a grace period. Store `grace_period_end` on Subscription. Entitlement logic can treat user as active until grace_period_end.
