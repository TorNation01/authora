# Tenant Architecture

Multi-tenant design for enterprise and white-label deployments.

---

## Overview

- **Standalone**: Single implicit tenant; `tenant_id` NULL
- **Enterprise**: Multiple organizations; `tenant_id` = org id
- **White-label**: Per-org branding; custom domains

---

## Schema

### organizations

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| name | string | Display name |
| slug | string | URL-safe unique |
| domain | string | Custom domain (optional) |
| branding | JSONB | product_name, tagline, logo_url, favicon_url, primary_color, show_powered_by |
| onboarding_config | JSONB | Custom onboarding steps |
| is_active | bool | |

### org_members

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| org_id | UUID | FK organizations |
| user_id | UUID | FK users |
| role | string | admin \| manager \| user |

### org_subscriptions

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| org_id | UUID | FK organizations |
| plan_id | UUID | FK plans |
| status | string | active, canceled, etc. |
| seat_count | int | Number of seats |
| stripe_* | string | Stripe IDs |

### plans (extensions)

| Column | Type | Description |
|--------|------|-------------|
| price_per_seat_monthly_cents | int | Per-seat monthly |
| price_per_seat_yearly_cents | int | Per-seat yearly |
| bulk_seat_tiers | JSONB | Tiered pricing, e.g. [{min: 10, price_cents: 800}, ...] |

---

## Data Isolation

### Row-Level Filtering

When `feature_tenant_aware=true`:

- Projects: filter by `tenant_id = current_tenant` or `user.tenant_id`
- Subscriptions: user-level or org-level
- Audit logs: `tenant_id` for org-scoped queries

### Standalone Mode

- `tenant_id` NULL on all rows
- Single default org (slug `default`) for compatibility
- No org API; `feature_tenant_aware=false`

---

## Tenant Resolution Order

1. **X-Tenant-Id** header — explicit org UUID
2. **Host header** — lookup `organizations.domain`
3. **User context** — `user.tenant_id` from first org membership

---

## Branding Merge

```
effective_branding = env_branding | org.branding
```

Env (`BRANDING_*`) is base; org branding overrides. Keys: `product_name`, `tagline`, `logo_url`, `favicon_url`, `primary_color`, `show_powered_by`.

---

## Migration

Run `alembic upgrade head` to apply `040_add_enterprise_organizations`.

Creates: organizations, org_members, org_subscriptions; adds tenant_id to users, projects, subscriptions, audit_logs; adds plan seat pricing columns.
