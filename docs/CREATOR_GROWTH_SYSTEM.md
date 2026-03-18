# Creator Growth System

Helps creators succeed and grows the marketplace through featured creators, trending templates, top sellers, and analytics.

---

## 1. Growth System Summary

### Features

| Feature | Description |
|--------|-------------|
| **Featured creators** | Admin can mark approved creators as featured. Shown on template marketplace. |
| **Trending templates** | Templates ranked by recent activity (projects + purchases in last 7 days). |
| **Top sellers** | Templates ranked by total purchase count and revenue. |

### Data Model

- **creator_profiles.is_featured** (Boolean) – Admin-controlled flag for featured creators.
- **analytics_events** – Records `template_viewed` when a user opens a template preview.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/growth/featured-creators` | List featured creators (public). |
| GET | `/api/v1/templates/trending` | List trending templates (auth). |
| GET | `/api/v1/templates/top-sellers` | List top-selling templates (auth). |
| POST | `/api/v1/templates/{id}/view` | Record template view (auth). |
| GET | `/api/v1/templates/{id}/analytics` | Template analytics (creator-only). |
| PATCH | `/api/v1/admin/creators/{id}/featured` | Set/unset featured (admin). |

### Frontend

- **Template marketplace** – Featured creators, trending, top sellers sections.
- **View tracking** – POST `/view` when template preview opens.
- **Creator performance** – Views per template, total views.
- **Admin creators** – Star button to feature/unfeature creators.

---

## 2. Analytics Summary

### Metrics

| Metric | Source | Description |
|--------|--------|-------------|
| **Views** | `analytics_events` (`event_type=template_viewed`) | Count of template preview opens. |
| **Conversions** | `template_purchases` + `projects.template_id` | Purchases + projects started with template. |
| **Earnings** | `creator_earnings` | Creator earnings from template sales. |

### Per-Template Analytics

- **views** – Count of `template_viewed` events.
- **conversions** – Purchases + projects started.
- **purchases** – Count of `TemplatePurchase`.
- **projects_started** – Count of `Project` with `template_id`.
- **earnings_cents** – Sum of `CreatorEarning` for that template’s purchases.

### Creator Performance

- **total_views** – Sum of views across all creator templates.
- **views** – Per-template view counts in performance dashboard.

---

## 3. Production-Ready Confirmation

### Checklist

- [x] **DB** – Migration 049 adds `creator_profiles.is_featured`.
- [x] **Model** – `CreatorProfile.is_featured` added.
- [x] **Service** – `creator_growth_service`: featured creators, trending, top sellers, view recording, analytics.
- [x] **API** – Growth and template endpoints implemented.
- [x] **Admin** – PATCH featured, `is_featured` in list response.
- [x] **Frontend** – Featured creators, trending, top sellers on marketplace; view tracking on preview; performance views; admin featured toggle.
- [x] **Docs** – This document.

### Verification

1. Run migration: `alembic upgrade head`
2. Feature a creator: Admin → Creators → Star on approved creator.
3. Open template marketplace: Featured creators, trending, top sellers sections visible.
4. Open template preview: View recorded (check `analytics_events`).
5. Creator performance: Views shown per template and total.
