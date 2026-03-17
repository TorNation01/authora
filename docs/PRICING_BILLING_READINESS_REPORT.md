# AUTHORA Pricing & Billing Readiness Report

**Generated:** 2025-03-17  
**Status:** Production-ready for Stripe integration

---

## Executive Summary

The AUTHORA pricing, billing, Stripe, admin grants, and entitlement system has been audited and completed. All billing-critical gaps have been addressed. The system is ready to plug into Stripe safely after running the migration and configuring environment variables.

---

## 1. Plan Definitions

| Status | Component |
|--------|-----------|
| ✅ | **Plans:** free, starter, pro, studio, founder_lifetime |
| ✅ | **DB:** `plans` table with `stripe_price_id_monthly`, `stripe_price_id_yearly`, `stripe_price_id_lifetime` |
| ✅ | **API:** `/api/v1/billing/plans`, `/api/v1/billing/status` |
| ✅ | **Frontend:** Pricing page, plan cards, comparison table |

---

## 2. Billing Intervals

| Status | Support |
|--------|---------|
| ✅ | Monthly |
| ✅ | Yearly |
| ✅ | Lifetime (one-time) |

---

## 3. Stripe Integration

### Checkout Flow

| Status | Component |
|--------|-----------|
| ✅ | `POST /api/v1/billing/checkout/create` — creates Stripe Checkout Session |
| ✅ | Metadata: `user_id`, `plan_slug`, `billing_interval` |
| ✅ | Success/cancel URLs configurable per request |
| ✅ | **Pricing page:** Logged-in users see checkout buttons; unauthenticated see Register |
| ✅ | **Billing page:** Handles `?success=1` and `?canceled=1`; clears cache and shows toast |

### Webhook Handling

| Status | Event | Action |
|--------|-------|--------|
| ✅ | `checkout.session.completed` | Create/update Subscription (subscription or lifetime) |
| ✅ | `customer.subscription.created` | Upsert Subscription |
| ✅ | `customer.subscription.updated` | Sync period_end, cancel_at_period_end, status |
| ✅ | `customer.subscription.deleted` | Mark status=canceled |
| ✅ | `invoice.payment_failed` | Set `grace_period_end` (7 days), status=past_due |
| ✅ | `invoice.paid` | Clear grace_period_end, status=active |
| ✅ | **Idempotency:** `stripe_webhook_events` table prevents duplicate processing |

### Customer Portal

| Status | Component |
|--------|-----------|
| ✅ | `POST /api/v1/billing/customer-portal` — Stripe Billing Portal |
| ✅ | Payment method management, subscription cancellation, invoice history |

---

## 4. Billing State Sync

| Status | Component |
|--------|-----------|
| ✅ | Webhooks sync Stripe → DB |
| ✅ | `_get_active_subscription` includes grace period (past_due/unpaid when `grace_period_end > now`) |
| ✅ | Entitlement precedence: billing_exempt → plan_override → grant (override) → Stripe → grant (fill) → lifetime → expired fallback → free |

---

## 5. Cancellation & Downgrade

| Status | Flow |
|--------|------|
| ✅ | `cancel_at_period_end` stored and synced from Stripe |
| ✅ | User retains access until `period_end` |
| ✅ | Downgrade via Stripe Customer Portal (change plan) |

---

## 6. Grace Period

| Status | Component |
|--------|-----------|
| ✅ | `invoice.payment_failed` sets `grace_period_end` = period_end + 7 days |
| ✅ | `_get_active_subscription` treats `past_due`/`unpaid` as active when `now < grace_period_end` |
| ✅ | `invoice.paid` clears `grace_period_end` |

---

## 7. Lifetime Purchase

| Status | Component |
|--------|-----------|
| ✅ | Checkout mode=payment for `billing_interval=lifetime` |
| ✅ | Webhook creates Subscription with `is_lifetime=True`, `stripe_subscription_id=None` |
| ✅ | Plan resolution includes lifetime |

---

## 8. Admin Manual Grants

| Status | Component |
|--------|-----------|
| ✅ | Create grant: `POST /api/v1/billing/admin/grants` |
| ✅ | Revoke: `POST /api/v1/billing/admin/grants/{id}/revoke` |
| ✅ | Extend: `POST /api/v1/billing/admin/grants/{id}/extend` with `{ new_expires_at }` |
| ✅ | Convert to lifetime: `POST /api/v1/billing/admin/grants/{id}/convert-lifetime` |
| ✅ | **Extend UI:** Admin grants page has Extend button and date picker modal |

---

## 9. Promo Codes (Special Access Codes)

| Status | Component |
|--------|-----------|
| ✅ | Create: `POST /api/v1/billing/admin/promo-codes` |
| ✅ | Redeem: `POST /api/v1/billing/redeem-code` (internal) |
| ✅ | Revoke: `POST /api/v1/billing/admin/promo-codes/{id}/revoke` |
| ⚠️ | **Stripe promo:** Checkout `promo_code` expects Stripe Promotion Code ID (`prom_xxx`). Internal codes use `/redeem-code`; Stripe-compatible codes must be created in Stripe Dashboard. |

---

## 10. Entitlement Precedence

1. **billing_exempt** / legacy plan_override  
2. Active admin grant with `override_stripe=True`  
3. Active Stripe subscription  
4. Active admin grant (override_stripe=False)  
5. Lifetime subscription  
6. Expired grant fallback (revert_previous / revert_free / prompt_billing)  
7. Free plan  

---

## 11. Gifted / Free Tier Grants

| Status | Component |
|--------|-----------|
| ✅ | Admin grants with `access_type=free` |
| ✅ | `on_expiry`: revert_free, revert_previous, prompt_billing |

---

## 12. Expiry / Reversion Behaviour

| Status | Component |
|--------|-----------|
| ✅ | `on_expiry` on grants: revert_free, revert_previous, prompt_billing |
| ✅ | Expired grant fallback in `get_user_plan` |

---

## 13. Billing History

| Status | Component |
|--------|-----------|
| ✅ | Stripe Customer Portal provides invoice history |
| ⚠️ | No dedicated billing history API/UI in app yet — users rely on Stripe Portal |

---

## 14. Payment Method Management

| Status | Component |
|--------|-----------|
| ✅ | Via Stripe Customer Portal (Manage billing) |

---

## 15. Audit Logs

| Status | Component |
|--------|-----------|
| ✅ | `entitlement_audit_log` for grant create/revoke/extend/convert |
| ✅ | `stripe_webhook_events` for webhook idempotency |

---

## 16. Pre-Launch Checklist

- [ ] Run migration: `alembic upgrade head` (creates `stripe_webhook_events` table)
- [ ] Set `STRIPE_SECRET_KEY` (test or live)
- [ ] Set `STRIPE_WEBHOOK_SECRET` (or `STRIPE_WEBHOOK_SECRET_TEST` / `STRIPE_WEBHOOK_SECRET_LIVE`)
- [ ] Configure Stripe webhook endpoint: `POST https://your-api/api/v1/billing/webhooks/stripe`
- [ ] Subscribe to events: `checkout.session.completed`, `customer.subscription.*`, `invoice.paid`, `invoice.payment_failed`
- [ ] Set `stripe_price_id_*` on plans in DB (or via migration/seed)
- [ ] Set `STRIPE_SUCCESS_URL` and `STRIPE_CANCEL_URL` in config (optional; overrides per request)
- [ ] Enable `feature_billing` in config

---

## 17. Stripe Readiness Confirmation

✅ **The system is ready to plug into Stripe safely.**

- Webhook signature verification
- Idempotent event processing
- Grace period handling
- Lifetime and subscription support
- Admin grants and promo codes
- Pricing page checkout for logged-in users
- Billing page success/cancel handling

---

## Files Changed (This Session)

| File | Change |
|------|--------|
| `apps/api/authora/models/stripe_webhook_event.py` | New model for idempotency |
| `apps/api/authora/services/stripe_service.py` | Full webhook handling |
| `apps/api/authora/services/billing_service.py` | Grace period in `_get_active_subscription` |
| `apps/api/authora/api/routes/billing.py` | Webhook route passes `db` |
| `apps/api/alembic/versions/035_add_stripe_webhook_events.py` | Migration |
| `apps/web/src/app/(marketing)/pricing/PricingPlanCards.tsx` | Checkout flow for logged-in users |
| `apps/web/src/app/dashboard/billing/page.tsx` | Success/cancel URL handling |
| `apps/web/src/app/dashboard/admin/grants/page.tsx` | Extend UI |
| `apps/web/src/lib/billing.ts` | `createCheckoutSession` accepts success/cancel URLs |
