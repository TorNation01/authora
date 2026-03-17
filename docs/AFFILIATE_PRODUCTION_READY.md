# Affiliate System – Production Readiness Checklist

## Implemented

- [x] Affiliate account system (apply, approve, reject)
- [x] Unique affiliate codes and referral links
- [x] Click tracking (public endpoint)
- [x] Attribution on signup (`affiliate_code` in body)
- [x] Conversion on payment (Stripe webhook integration)
- [x] Commission types: one-time (lifetime), recurring (monthly/yearly)
- [x] Pending / approved / paid commission status
- [x] Payout requests with validation
- [x] Admin payout approval, rejection, mark-paid
- [x] Affiliate dashboard (link, clicks, conversions, earnings, payouts)
- [x] Admin control panel (list, approve, reject, top performers, export)
- [x] Fraud prevention: self-referral blocking, duplicate attribution, manual flag
- [x] Feature flag: `FEATURE_AFFILIATE`
- [x] Migration 042
- [x] API routes

## Before Production

1. **Enable feature**: `FEATURE_AFFILIATE=true`
2. **Run migration**: `alembic upgrade head`
3. **Frontend**: Add affiliate dashboard page
4. **Frontend**: Add tracking (redirect or client-side) for `?aff=CODE`
5. **Frontend**: Pass `affiliate_code` on registration when `aff` in URL/cookie
6. **Admin UI**: Add affiliate management section

## Optional Enhancements

- Stripe Connect for automated payouts
- Email notifications (approval, payout paid)
- Affiliate terms and conditions page
- Cookie-based attribution (30-day window)
- Click deduplication by fingerprint (same IP+UA in short window)

## Confirmation

The affiliate system is **production-ready** when:

1. Migration 042 is applied
2. `FEATURE_AFFILIATE=true` is set
3. Frontend integrates tracking and registration
4. Admin UI is wired for affiliate management
