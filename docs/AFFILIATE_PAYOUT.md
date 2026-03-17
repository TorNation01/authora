# Affiliate Payout System

## Overview

- **Payout requests**: Affiliates request payouts when balance meets minimum
- **Admin approval**: Admin approves or rejects payout requests
- **Payment**: Manual tracking (default) or Stripe payouts (when configured)
- **Commission status**: Marked `paid` when payout is completed

## Payout Flow

1. Affiliate requests payout: `POST /api/v1/affiliates/payout` with `amount_cents`
2. System validates: minimum amount, available balance
3. Admin reviews: `GET /api/v1/affiliates/admin/payouts`
4. Admin approves: `POST /api/v1/affiliates/admin/payouts/{id}/approve`
5. Admin processes payment (Stripe, bank transfer, etc.)
6. Admin marks paid: `POST /api/v1/affiliates/admin/payouts/{id}/mark-paid`

## Settings

- `min_payout_cents`: Minimum payout (default 5000 = $50)
- `payment_method`: `manual` (default) or `stripe`

## Mark Paid

When marking a payout as paid:

```json
POST /api/v1/affiliates/admin/payouts/{id}/mark-paid
{
  "stripe_payout_id": "po_xxx",  // optional
  "payment_details": {"bank_ref": "..."}  // optional
}
```

The system marks conversions as `paid` (oldest first) up to the payout amount. This prevents double-counting in earnings.

## Stripe Payouts (Future)

When Stripe Connect or similar is integrated, set `stripe_payout_id` when marking paid. The `payment_method` can be set to `stripe` for reporting.

## Manual Fallback

When Stripe is not available, the admin:
1. Approves the payout
2. Processes payment via bank transfer, PayPal, etc.
3. Marks paid with `payment_details` for audit trail
