# Template Sales System

## Overview

The AUTHORA template sales system allows users to purchase creator templates via Stripe. Purchased templates are saved to the user's account and accessible anytime. Creators earn revenue from sales; admins can track sales per template and revenue per creator.

---

## 1. Sales System Summary

### Features

| Feature | Description |
|---------|-------------|
| **Template product pages** | Template preview dialog with pricing, description, structure |
| **Pricing display** | Price shown on cards and in preview (`$X.XX`) |
| **Purchase via Stripe** | `POST /api/v1/billing/checkout/template` creates Checkout Session |
| **Unlock after purchase** | Webhook creates `TemplatePurchase`; `access_level="creator_paid"` grants access |

### Flow

1. User browses templates; paid creator templates show price and "Purchase" / "Buy for $X.XX"
2. User clicks Buy → Stripe Checkout (dynamic `price_data` from `template.price_cents`)
3. Webhook `checkout.session.completed` with `metadata.template_id` → create `TemplatePurchase`
4. User redirected to `/dashboard/templates?template_purchased=1`
5. Template appears in "My purchased templates" and is usable

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/billing/checkout/template` | POST | Create Stripe Checkout for single template |
| `/api/v1/templates/purchased` | GET | List user's purchased templates |
| `/api/v1/templates/{id}` | GET | Template detail with `can_use`, `required_action` |

### Access Logic

- `access_level="creator_paid"`: user must have `TemplatePurchase` for that template
- `required_action="purchase_template:{id}"` when not purchased
- Frontend: Buy button triggers `createTemplateCheckout(templateId)`

---

## 2. Tracking Summary

### Sales per template

- **Table**: `template_purchases` (user_id, template_id, amount_cents, stripe_session_id, purchased_at)
- **Admin**: `GET /api/v1/admin/template-sales` — sales count and revenue per template
- **Creator**: `GET /api/v1/creators/performance` — includes `sales_count`, `revenue_cents` per template

### Revenue per creator

- **Admin**: `GET /api/v1/admin/creator-revenue` — sum of template sales grouped by creator
- **Creator**: Performance dashboard shows `total_sales`, `total_revenue_cents`

### Usage analytics

- **Projects**: `Project.template_id` — projects started with template
- **Books**: `Book.template_id` — books created with template
- **Creator performance**: projects_count, books_count, sales_count, revenue_cents per template

---

## 3. User Access

### Purchased templates saved to account

- `template_purchases` table: one row per (user_id, template_id)
- Unique constraint prevents duplicate purchases
- User can list purchased templates via `GET /api/v1/templates/purchased`

### Accessible anytime

- Purchased templates appear in "My purchased templates" on `/dashboard/templates`
- `can_use=true` for purchased templates; no re-purchase required
- Template access checked in `has_template_access()` and `_check_template_access()`

---

## 4. Production-Ready Confirmation

### Implemented

- [x] **template_purchases** table (migration 046)
- [x] **TemplatePurchase** model
- [x] **Stripe** `create_template_checkout_session` (price_data, metadata.template_id)
- [x] **Webhook** `checkout.session.completed` → create TemplatePurchase for template_id
- [x] **Template access** `creator_paid` — check TemplatePurchase
- [x] **API** checkout, purchased list, template-sales, creator-revenue
- [x] **Frontend** product preview, pricing, Buy button, purchased section, success redirect
- [x] **Creator performance** sales and revenue stats

### Database

- Migration `046_add_template_purchases.py`: `template_purchases` (user_id, template_id, amount_cents, stripe_session_id, purchased_at)

### Security

- Checkout requires auth
- Webhook verifies Stripe signature
- Idempotency via StripeWebhookEvent
- Duplicate purchase blocked (unique constraint + API check)
