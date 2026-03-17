# AUTHORA Affiliate System

Production-ready affiliate program for external users, influencers, and partners to promote Authora and earn commissions.

## Overview

- **Apply as affiliate** – Users apply; admins approve or reject
- **Unique referral links** – Each affiliate gets `?aff=CODE` links
- **Commission tracking** – Percentage-based (one-time and recurring)
- **Payout requests** – Affiliates request payouts; admins approve and mark paid
- **Fraud prevention** – Self-referral blocking, duplicate detection, manual flagging

## Enable the System

Set in environment:

```
FEATURE_AFFILIATE=true
```

## Affiliate Flow

1. User applies via `POST /api/v1/affiliates/apply`
2. Admin approves via `POST /api/v1/affiliates/admin/{profile_id}/approve`
3. Affiliate shares link: `https://authora.studio?aff=CODE`
4. Visitor clicks → tracking records click
5. Visitor registers with `affiliate_code` in body
6. Attribution stored; when they pay, commission is created
7. Affiliate requests payout when balance meets minimum
8. Admin approves and marks paid

## API Endpoints

### Affiliate (authenticated)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/affiliates/apply` | Apply to become an affiliate |
| GET | `/affiliates/dashboard` | Dashboard (link, clicks, conversions, earnings) |
| POST | `/affiliates/payout` | Request payout |

### Tracking (public)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/affiliates/track?aff=CODE` | Record click (no auth) |

### Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/affiliates/admin/list` | List affiliates |
| POST | `/affiliates/admin/{id}/approve` | Approve affiliate |
| POST | `/affiliates/admin/{id}/reject` | Reject affiliate |
| GET | `/affiliates/admin/top` | Top performers |
| GET | `/affiliates/admin/payouts` | List payout requests |
| POST | `/affiliates/admin/payouts/{id}/approve` | Approve payout |
| POST | `/affiliates/admin/payouts/{id}/reject` | Reject payout |
| POST | `/affiliates/admin/payouts/{id}/mark-paid` | Mark payout paid |
| GET | `/affiliates/admin/export` | Export report |
| POST | `/affiliates/admin/conversions/{id}/flag-fraud` | Flag conversion as fraud |
| GET | `/affiliates/admin/settings` | Get affiliate settings |
| PATCH | `/affiliates/admin/settings` | Update affiliate settings |

## Registration with Affiliate Code

Include `affiliate_code` in the registration body:

```json
{
  "email": "user@example.com",
  "password": "...",
  "display_name": "Jane",
  "affiliate_code": "abc123"
}
```

The frontend should read `?aff=CODE` from the URL (or cookie) and pass it as `affiliate_code` when the user registers.

## Commission Rates

- **One-time** (lifetime plans): `commission_rate_pct` (default 20%)
- **Recurring** (monthly/yearly): `commission_recurring_pct` (default 10%) or `commission_rate_pct` if not set

Rates are configurable per affiliate on approval and via admin settings.

## Database Tables

- `affiliate_profiles` – Affiliate accounts, status, rates
- `affiliate_clicks` – Click tracking
- `affiliate_attributions` – User → affiliate attribution (one per user)
- `affiliate_conversions` – Revenue events with commission
- `affiliate_payouts` – Payout requests and payments

## Migration

Run migration 042:

```bash
cd apps/api && alembic upgrade head
```
