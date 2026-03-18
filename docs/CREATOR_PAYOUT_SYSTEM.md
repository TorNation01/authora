# Creator Payout System

## Overview

The creator payout system pays creators for template sales. Creators earn a revenue share on each template purchase. They can request payouts when their balance meets the minimum, and admins approve and process payments via manual fallback or Stripe Connect (when configured).

---

## 1. Payout System Summary

### Payout Flow

1. **Creator requests payout**: `POST /api/v1/creators/payout` with `amount_cents`
2. **System validates**: Minimum amount (from settings), available balance
3. **Admin reviews**: `GET /api/v1/admin/creator-payouts` (filter by status)
4. **Admin approves**: `POST /api/v1/admin/creator-payouts/{id}/approve`
5. **Admin rejects**: `POST /api/v1/admin/creator-payouts/{id}/reject` with optional `rejection_reason`
6. **Admin marks paid**: `POST /api/v1/admin/creator-payouts/{id}/mark-paid` (allocates earnings, records payment)

### Payout Methods

| Method | Description |
|--------|-------------|
| **Stripe Connect** (preferred) | Set `stripe_payout_id` when marking paid; `payment_method` becomes `stripe_connect` |
| **Manual fallback** | Default. Admin processes via bank transfer, PayPal, etc.; records in `payment_details` |

### Admin Balance Adjustments

Admins can credit or debit creator balances:

- `POST /api/v1/admin/creator-payouts/adjust-balance/{creator_id}`
- Body: `{ "amount_cents": ±N, "reason": "optional" }`
- Positive = credit, negative = debit
- Used for corrections, bonuses, or refunds

### Settings

Stored in `growth_settings` with key `creator_payout` (or defaults):

| Key | Default | Description |
|-----|---------|-------------|
| `min_payout_cents` | 1000 ($10) | Minimum payout amount |
| `default_revenue_share_pct` | 70 | Revenue share % when not set on creator profile |

---

## 2. Earnings System Summary

### How Earnings Are Created

- **One `CreatorEarning` per template purchase** of a creator's template
- `amount_cents` = purchase amount × revenue share %
- Revenue share: from `creator_profiles.revenue_share_pct` or `default_revenue_share_pct`
- Created in Stripe webhook when `checkout.session.completed` for template purchase

### Balance Calculation

```
available_balance = sum(pending earnings) + sum(adjustments) - sum(pending/approved payouts)
```

- **Pending earnings**: `CreatorEarning` rows with `status = pending`
- **Adjustments**: `CreatorBalanceAdjustment` (admin credits/debits)
- **Pending/approved payouts**: `CreatorPayout` with `status` in `pending` or `approved`

### Mark Paid Logic

When admin marks a payout as paid:

1. Payout `status` → `paid`, `paid_at` set
2. Pending earnings allocated to this payout (FIFO) up to `amount_cents`
3. Each allocated earning: `status` → `paid`, `payout_id` set
4. Prevents double-counting in future payouts

### Creator API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/creators/earnings` | GET | Earnings dashboard: balance, totals, payout history |
| `/api/v1/creators/payout` | POST | Request payout (`amount_cents`) |

### Admin API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/admin/creator-payouts` | GET | List payouts (optional `?status=`) |
| `/api/v1/admin/creator-payouts/{id}/approve` | POST | Approve payout |
| `/api/v1/admin/creator-payouts/{id}/reject` | POST | Reject payout |
| `/api/v1/admin/creator-payouts/{id}/mark-paid` | POST | Mark paid (body: `stripe_payout_id`, `payment_method`, `payment_details`) |
| `/api/v1/admin/creator-payouts/adjust-balance/{creator_id}` | POST | Adjust creator balance |

---

## 3. Data Model

### Tables

- **creator_earnings**: `creator_id`, `template_purchase_id`, `amount_cents`, `status` (pending|paid), `payout_id`
- **creator_payouts**: `creator_id`, `amount_cents`, `status` (pending|approved|paid|rejected), `payment_method`, `stripe_payout_id`, `payment_details`, timestamps
- **creator_balance_adjustments**: `creator_id`, `amount_cents`, `reason`, `admin_user_id`
- **creator_profiles**: `stripe_connect_account_id`, `revenue_share_pct` (optional)

---

## 4. Frontend

### Creator

- **Earnings** (`/dashboard/creator/earnings`): Balance, totals, payout request form, payout history
- Nav: Overview, My templates, Performance, **Earnings**

### Admin

- **Creator payouts** (`/dashboard/admin/creator-payouts`): List payouts, approve/reject/mark paid, adjust balance form

---

## 5. Production Checklist

- [ ] Migration `047_add_creator_payout_system` applied
- [ ] Stripe webhook calls `create_earning_from_purchase` after `TemplatePurchase` creation (template checkout)
- [ ] Optional: Seed `growth_settings` with `creator_payout` key for custom `min_payout_cents` / `default_revenue_share_pct`
- [ ] Optional: Stripe Connect onboarding for creators (future); manual fallback works without it
- [ ] Admin trained on: approve → process payment → mark paid
- [ ] Audit: `creator_balance_adjustments` and `creator_payouts.payment_details` for manual payments

---

## 6. Stripe Connect (Future)

When Stripe Connect is integrated:

1. Creators complete Connect onboarding; `stripe_connect_account_id` stored on `creator_profiles`
2. On mark paid: create Stripe Transfer to connected account; pass `stripe_payout_id` to `mark_payout_paid`
3. `payment_method` set to `stripe_connect` for reporting

Manual fallback remains available for creators without Connect or for edge cases.
