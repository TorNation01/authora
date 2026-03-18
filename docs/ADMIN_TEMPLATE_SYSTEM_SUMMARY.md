# Admin Template System

## Overview

Admins can manage project templates and template packs: upload, pricing, tiers, and visibility.

---

## Admin Control

### Templates

| Action | How |
|--------|-----|
| **List** | `GET /api/v1/admin/templates?include_disabled=true` |
| **Create** | `POST /api/v1/admin/templates` with full template payload |
| **Update** | `PATCH /api/v1/admin/templates/{id}` – name, description, structure, **access_level**, **premium_pack_slug**, **price_cents**, **is_paid**, **creator_id**, **is_featured**, **is_disabled** |
| **Duplicate** | `POST /api/v1/admin/templates/{id}/duplicate` – creates copy with `-copy` suffix |
| **Reorder** | `POST /api/v1/admin/templates/reorder` with `template_ids` array |
| **Usage** | `GET /api/v1/admin/templates/usage` – projects/books per template |

### Template Packs

| Action | How |
|--------|-----|
| **List** | `GET /api/v1/admin/template-packs?include_inactive=true` |
| **Create** | `POST /api/v1/admin/template-packs` – slug, name, price_cents, template_slugs, stripe_price_id, etc. |
| **Update** | `PATCH /api/v1/admin/template-packs/{id}` – pricing, visibility, Stripe, revenue_share_pct |
| **Analytics** | `GET /api/v1/admin/template-packs/analytics` – purchase count per pack |

### Visibility Control

- **Templates**: `is_featured`, `is_disabled`
- **Packs**: `is_active`, `is_featured`

### Pricing & Tiers

- **Templates**: `access_level` (free | pro | studio | premium_pack), `premium_pack_slug`, `price_cents`, `is_paid`
- **Packs**: `price_cents`, `stripe_price_id` (for Stripe Checkout)

### Creator Attribution (future)

- **Templates**: `creator_id` (user UUID)
- **Packs**: `creator_id`, `revenue_share_pct`

---

## Admin UI

- **Templates**: `/dashboard/admin/templates` – list by category, toggle featured/disabled, duplicate
- **Template packs**: `/dashboard/admin/template-packs` – list packs, view analytics, Stripe status

---

## Seeding

Templates and packs are seeded from:

- `apps/api/authora/data/template_definitions.py`
- `apps/api/authora/data/template_pack_definitions.py`

Commands:

```bash
cd apps/api && PYTHONPATH=. python -m authora.scripts.seed_project_templates
cd apps/api && PYTHONPATH=. python -m authora.scripts.seed_template_packs
```

---

## Stripe Integration

- Template pack checkout: `POST /api/v1/billing/checkout/template-pack` with `pack_slug`
- Webhook: `checkout.session.completed` with `metadata.pack_slug` → creates `TemplatePackPurchase`
- Set `stripe_price_id` per pack (via env, DB, or admin API) for live checkout
