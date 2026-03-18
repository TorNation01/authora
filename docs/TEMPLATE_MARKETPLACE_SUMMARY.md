# Template Marketplace System

## Overview

The template marketplace allows browsing, discovery, and distribution of project templates at scale. It is built for future expansion: creator submissions, ratings, and revenue sharing.

---

## Features

### Template Browsing

- **Categories**: Templates organized by category (fiction, nonfiction, ai_templates, accountability, business, etc.)
- **Featured templates**: Highlighted section for promoted templates
- **Search**: Server-side search by name and description
- **Marketplace endpoint**: `GET /api/v1/templates/marketplace?category=&featured=&search=`

### Access Control

- **Access levels**: `free`, `pro`, `studio`, `premium_pack`
- **Premium packs**: One-time purchase via Stripe; unlocks templates in that pack
- **Plan gating**: Pro/Studio plans unlock tier-gated templates

### Future-Ready Schema

- **Template ratings** (`template_ratings`): User ratings 1–5, optional review. Table ready; API not yet implemented.
- **Creator submissions** (`template_submissions`): Creator-submitted templates for approval. Table ready; workflow not yet implemented.
- **Revenue sharing**: `template_packs.creator_id`, `template_packs.revenue_share_pct` for future payouts.

---

## API Endpoints

### Public (authenticated)

| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | `/api/v1/templates/categories` | Categories with templates and access info |
| GET | `/api/v1/templates/marketplace` | Browse with filters: category, featured, search |
| GET | `/api/v1/templates/{id}` | Full template by ID |
| GET | `/api/v1/templates/slug/{slug}` | Full template by slug |
| GET | `/api/v1/templates/packs` | Template packs with purchase status |

### Admin

| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | `/api/v1/admin/templates` | List all templates (include_disabled) |
| POST | `/api/v1/admin/templates` | Create template |
| PATCH | `/api/v1/admin/templates/{id}` | Update template (incl. access_level, pricing, visibility) |
| POST | `/api/v1/admin/templates/{id}/duplicate` | Duplicate template |
| POST | `/api/v1/admin/templates/reorder` | Reorder by ID list |
| GET | `/api/v1/admin/templates/usage` | Usage stats by template |
| GET | `/api/v1/admin/template-packs` | List packs |
| POST | `/api/v1/admin/template-packs` | Create pack |
| PATCH | `/api/v1/admin/template-packs/{id}` | Update pack (pricing, visibility, Stripe) |
| GET | `/api/v1/admin/template-packs/analytics` | Purchase counts by pack |

---

## Database Schema (Migration 044)

### template_ratings (optional future)

- `template_id`, `user_id`, `rating` (1–5), `review`, `created_at`
- Unique constraint: one rating per user per template

### template_submissions (creator submissions, future)

- `creator_id`, `slug`, `name`, `description`, `payload` (JSONB), `status`, `rejected_reason`
- Status: `pending`, `approved`, `rejected`

### template_packs (extended)

- `creator_id`, `revenue_share_pct`, `is_featured`

---

## Frontend

- **Template library** (`/dashboard/templates`): Browse by category, search, featured section, preview, apply
- **Admin templates** (`/dashboard/admin/templates`): Toggle featured/disabled, duplicate, view by category
- **Admin template packs** (`/dashboard/admin/template-packs`): View packs, pricing, purchase analytics

---

## Monetization Flow

1. **Free templates**: Available to all users
2. **Pro/Studio templates**: Gated by subscription plan
3. **Premium pack templates**: One-time purchase via Stripe Checkout
4. **Future**: Individual template purchase, creator revenue share
