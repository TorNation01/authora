# AUTHORA Template Monetisation Summary

**Date:** March 15, 2025  
**Status:** Production-ready

---

## 1. Template Monetisation Summary

### Access Levels

| Level | Description | Unlock |
|-------|-------------|--------|
| **Free** | Available to all users | Always |
| **Pro** | Premium templates included in Pro/Studio/Founder plans | Upgrade plan |
| **Studio** | Premium templates included in Studio/Founder plans | Upgrade plan |
| **Premium Pack** | One-time purchase bundle | Buy pack |

### Template Distribution

| Access Level | Count | Examples |
|--------------|-------|----------|
| Free | 36 | Fiction Novel, Non-Fiction Book, Memoir, Workbook, Journal, Poetry, Short Story Collection, Series Project, Ghostwritten Book, Custom, Hybrid Creative, Fiction sub-templates (General, Short, YA, Historical, etc.), Nonfiction sub-templates |
| Pro | 8 | Romance, Fantasy, Thriller, Sci-Fi, Memoir, Self-Help, Business, Workbook (premium launch) |
| Premium Pack | 7 | Chapter Builder, Character Builder, World Building (Fiction Structure Pack); Book Blueprint, Chapter Template, Authority Book, Self-Help Structured (Nonfiction Pro Pack) |

### Premium Packs

| Pack | Price | Templates |
|------|-------|-----------|
| **Fiction Structure Pack** | $29 | Chapter Builder, Character Builder, World Building |
| **Nonfiction Pro Pack** | $29 | Book Blueprint, Chapter Template, Authority Book, Self-Help (Structured) |

### Setup for Stripe

1. Create Stripe products for each pack in Dashboard → Products
2. Create one-time prices
3. Set `stripe_price_id` on `template_packs` (via migration or admin)
4. Configure `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`

---

## 2. Access Control Summary

### Enforcement Points

| Location | Check |
|----------|-------|
| **Template library** | `/api/v1/templates/categories` returns `can_use`, `required_action` per template |
| **Template detail** | `/api/v1/templates/{id}` returns `can_use`, `required_action` |
| **Project creation** | `POST /api/v1/projects/from-wizard` validates template access before creating project |

### Access Logic

1. **Free tier** → Free templates only
2. **Starter** → Free templates only
3. **Pro** → Free + Pro templates
4. **Studio** → Free + Pro + Studio templates
5. **Founder Lifetime** → Free + Pro + Studio templates
6. **Premium Pack** → Unlocked if user has `template_pack_purchases` record for that pack

### Required Action Values

- `null` → User can use template
- `"upgrade"` → User must upgrade to Pro or Studio
- `"purchase:{pack_slug}"` → User must purchase the specified pack

---

## 3. Production-Ready Confirmation

### Requirements Met

| Requirement | Status |
|-------------|--------|
| **Template access levels** | Free, Pro, Studio, Premium Packs defined |
| **Access control** | Templates locked by tier; premium packs require purchase |
| **Preview before unlock** | Always available; full structure visible in preview |
| **Premium badges** | Shown on locked templates in library and preview |
| **Locked template preview** | Preview dialog shows locked state and upgrade/purchase prompts |
| **Upgrade prompts** | "Upgrade to unlock" for Pro/Studio templates; "Purchase to unlock" for packs |
| **Purchase buttons** | Billing page; template library; preview dialog |
| **Stripe integration** | One-time checkout for template packs |
| **Unlock after payment** | Webhook creates `template_pack_purchases` record |
| **Link to user account** | Purchase linked to `user_id` |

### Files Touched

- **Migration:** `043_add_premium_template_system.py`
- **Models:** `project_template.py` (access_level, premium_pack_slug), `template_pack.py` (new)
- **Services:** `template_access_service.py`, `stripe_service.py`
- **API:** `templates.py`, `billing.py`, `projects.py`
- **Data:** `template_definitions.py`, `premium_templates.py`, `template_pack_definitions.py`
- **Seeds:** `seed_project_templates.py`, `seed_template_packs.py`, `seed.py`
- **Frontend:** `templates/page.tsx`, `billing/page.tsx`, `billing.ts`

### Database Tables

- `project_templates`: `access_level`, `premium_pack_slug`
- `template_packs`: slug, name, description, price_cents, stripe_price_id, template_slugs
- `template_pack_purchases`: user_id, pack_slug, stripe_session_id, purchased_at
