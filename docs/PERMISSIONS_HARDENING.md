# AUTHORA Permissions & Entitlement Hardening

Validation and hardening for role-based access, collaboration scopes, and billing entitlements.

## Role-Based Access

| Role | Scope |
|------|-------|
| Owner | Full project access, invite, delete |
| Editor | Edit content, comments |
| Beta reader | Read, review, limited |
| Client | Read-only, hide internal clutter |

## Validation Tests

- **Over-permission**: Non-owner cannot delete project
- **Hidden content leaks**: Private notes not visible to beta/client
- **Cross-project access**: User A cannot access User B's project without invite
- **Incorrect plan access**: Free user cannot use ghostwriter when billing enabled
- **Expired grant**: Access revoked after expiry
- **Revoked invite**: Access lost on next request

## Test Coverage

See `apps/api/tests/test_permissions.py` for:
- Project access requires auth
- User cannot access other user's project
- Admin routes require admin
- Export requires book access

## Billing Entitlements

- Manual grant precedence over Stripe when `override_stripe=true`
- Promo code redemption creates grant
- Expiry reversion: `revert_free`, `revert_previous`, `prompt_billing`
