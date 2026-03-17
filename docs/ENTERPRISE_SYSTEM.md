# AUTHORA Enterprise System

Production-ready enterprise and white-label system. Organizations use Authora under their own brand.

---

## 1. Enterprise System Summary

### Multi-Tenant Architecture

| Feature | Implementation |
|---------|----------------|
| **Separate organizations** | `organizations` table; slug, domain |
| **Isolated data** | `tenant_id` on users, projects, subscriptions, audit_logs |
| **Custom branding per org** | `organizations.branding` JSONB; merged with env defaults |

### White-Label Features

| Feature | Implementation |
|---------|----------------|
| **Custom logo** | `branding.logo_url` |
| **Custom domain** | `organizations.domain`; domain-based tenant resolution |
| **Custom colors** | `branding.primary_color` |
| **Custom onboarding** | `organizations.onboarding_config` JSONB |

### Org Management Roles

| Role | Permissions |
|------|-------------|
| **admin** | Full org control; create org; manage members; update branding |
| **manager** | Add/remove members; update branding |
| **user** | Access org resources; view branding |

### Billing

| Feature | Implementation |
|---------|----------------|
| **Organization billing** | `org_subscriptions` table |
| **Bulk pricing** | `plans.bulk_seat_tiers` JSONB; `price_per_seat_*` |
| **Seat-based pricing** | `org_subscriptions.seat_count`; per-seat plan pricing |

---

## 2. Tenant Architecture Summary

### Tables

| Table | tenant_id | Notes |
|------|-----------|-------|
| `organizations` | - | Root tenant entity |
| `org_members` | - | org_id, user_id, role |
| `org_subscriptions` | - | org_id, plan_id, seat_count |
| `users` | ✓ | Optional; NULL = standalone |
| `projects` | ✓ | Inherited from user or explicit |
| `subscriptions` | ✓ | User or org-scoped |
| `audit_logs` | ✓ | Tenant-scoped for filtering |

### Tenant Resolution

1. **X-Tenant-Id** header — explicit tenant UUID
2. **Host/Domain** — `organizations.domain` lookup (future)
3. **User.tenant_id** — when authenticated

### Branding Resolution

1. Base: `BRANDING_*` env vars
2. Override: `organizations.branding` when `X-Tenant-Id` present and `feature_tenant_aware=true`

---

## 3. Production-Ready Confirmation

### Checklist

- [x] Organizations table
- [x] Org members with roles (admin, manager, user)
- [x] tenant_id on users, projects, subscriptions, audit_logs
- [x] Per-org branding (logo, colors, tagline)
- [x] Custom domain support (schema)
- [x] Custom onboarding config
- [x] Org subscriptions (seat-based)
- [x] Bulk/seat pricing on plans
- [x] Org API routes
- [x] Tenant-aware config/branding
- [x] feature_tenant_aware flag

### Configuration

```bash
# Enable enterprise
FEATURE_TENANT_AWARE=true

# Deployment mode (white_label enables branding overrides)
DEPLOYMENT_MODE=white_label
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/organizations` | List user's orgs |
| POST | `/api/v1/organizations` | Create org (admin) |
| GET | `/api/v1/organizations/{id}` | Get org |
| PATCH | `/api/v1/organizations/{id}/branding` | Update branding |
| POST | `/api/v1/organizations/{id}/members` | Add member |

### Per-Tenant Config

Send `X-Tenant-Id: <org-uuid>` when calling:

- `GET /api/v1/config`
- `GET /api/v1/config/branding`

---

## See Also

- [TENANT_ARCHITECTURE.md](./TENANT_ARCHITECTURE.md) — Detailed tenant design
- [BRANDING_OVERRIDES.md](./BRANDING_OVERRIDES.md) — Env branding
- [INTEGRATION.md](./INTEGRATION.md) — Anakatech / white-label modes
