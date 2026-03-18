# Template Marketplace Browsing

## Overview

The template marketplace lets users discover, filter, and preview project templates. It supports category browsing, featured templates, search, filters, and trust signals (usage count, creator name, ratings placeholder).

---

## 1. Marketplace UI Summary

### Pages and Layout

| Location | Description |
|----------|-------------|
| `/dashboard/templates` | Template library / marketplace |

### Display Elements (per template)

| Element | Description |
|---------|-------------|
| **Template name** | Primary title |
| **Description** | Short description (line-clamped) |
| **Preview** | Dialog with full details: structure, who it's for, expected outcome, workflow |
| **Creator name** | Display name of template creator (when creator template) |
| **Price** | Shown for paid templates (e.g. $19.99) |
| **Usage count** | "X projects created" — trust signal |
| **Ratings** | Future-ready: `rating_avg`, `rating_count` (shown when available) |

### Features

- **Category browsing**: Sidebar with categories; click to filter
- **Featured templates**: Highlighted section when no search/filters
- **Search**: By name or description
- **Filters**: Book type, genre, price min/max
- **Preview dialog**: Full template details before apply/purchase

---

## 2. Browsing System Summary

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/templates/categories` | GET | Categories with templates and children; includes trust signals |
| `/api/v1/templates/marketplace` | GET | Browse templates with filters |
| `/api/v1/templates/{id}` | GET | Full template details (for preview) |

### Marketplace Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Search name/description (ILIKE) |
| `featured` | bool | Only featured templates |
| `category` | string | Filter by category |
| `book_type` | string | e.g. fiction, nonfiction, memoir |
| `genre` | string | Genre substring match |
| `price_min` | int | Min price (cents) |
| `price_max` | int | Max price (cents) |

### Trust Signals (API Response)

| Field | Type | Description |
|-------|------|-------------|
| `creator_name` | string \| null | Creator display name |
| `usage_count` | int | Projects + books using this template |
| `rating_avg` | float \| null | Future: average rating 1–5 |
| `rating_count` | int | Future: number of ratings |

### Usage Count Logic

- **Projects**: Count of `Project` rows with `template_id = template.id`
- **Books**: Count of `Book` rows with `template_id = template.id`
- Total = projects + books (books may differ from project template in some flows)

---

## 3. Production Checklist

- [x] **Category browsing** — sidebar, category filter
- [x] **Featured templates** — `is_featured` filter, highlighted section
- [x] **Search** — name/description ILIKE
- [x] **Filters** — book_type, genre, price_min, price_max
- [x] **Display** — name, description, preview, creator name, price
- [x] **Trust signals** — usage_count, rating_avg/rating_count (future-ready)
- [x] **Creator name** — from User.display_name or email
- [x] **Preview dialog** — full template, structure, trust signals

### Future Enhancements

- **Ratings**: Add `template_ratings` table; populate `rating_avg`, `rating_count`
- **Sort options**: By usage, price, newest
- **Public marketplace**: Unauthenticated browse (optional)
