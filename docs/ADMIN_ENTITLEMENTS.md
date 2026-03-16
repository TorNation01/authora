# Admin Entitlement Grants

Admins can grant users access to any plan regardless of Stripe payment state. Grants are stored in `entitlement_grants` and audited.

## Grant Creation

**API:** `POST /api/v1/billing/admin/grants`

| Field | Type | Description |
|-------|------|-------------|
| user_id | UUID | User to grant |
| plan_slug | string | free, starter, pro, studio, founder_lifetime |
| expires_at | datetime | Optional; null = lifetime |
| duration_months | int | Alternative to expires_at |
| duration_years | int | Alternative to expires_at |
| reason | string | family, founder, beta_tester, partner, internal_use, scholarship, support_resolution, custom |
| reason_custom | string | When reason=custom |
| access_type | string | paid, discounted, free |
| override_stripe | bool | If true, grant overrides Stripe subscription |
| on_expiry | string | revert_previous, revert_free, prompt_billing |
| internal_notes | string | Admin-only notes |

## Grant Actions

- **Revoke:** `POST /api/v1/billing/admin/grants/{id}/revoke`
- **Extend:** `POST /api/v1/billing/admin/grants/{id}/extend` with `{ new_expires_at }`
- **Convert to lifetime:** `POST /api/v1/billing/admin/grants/{id}/convert-lifetime`

## List Grants

`GET /api/v1/billing/admin/grants/{user_id}?include_revoked=true`

## On Expiry Behavior

| Value | Behavior when grant expires |
|-------|-----------------------------|
| revert_previous | Use Stripe subscription if active, else free |
| revert_free | Always revert to free |
| prompt_billing | Revert to free; UI can show upgrade prompt |

## Override Stripe

- **override_stripe=true:** Grant takes precedence over Stripe. User gets grant plan even if they have an active subscription.
- **override_stripe=false:** Grant applies only when user has no Stripe subscription. Fills in when subscription lapses.

## Audit Log

All grant create/revoke/extend/convert actions are logged in `entitlement_audit_log` with:
- user_id, action, entity_type, entity_id, details, performed_by_id, created_at

View: `GET /api/v1/billing/admin/audit-log?user_id=...&action=...`
