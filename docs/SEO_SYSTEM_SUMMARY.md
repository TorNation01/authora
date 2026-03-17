# SEO System Summary

Programmatic SEO pages for AUTHORA.

---

## Structure

### seo_pages Table

| Column | Type | Purpose |
|--------|------|---------|
| slug | string | URL path (e.g. how-to-write-a-novel) |
| page_type | string | guide, feature, use-case |
| title | string | Page title, H1 |
| meta_description | string | SEO description |
| content | JSONB | Sections, features, etc. |
| internal_links | string[] | Related pages for footer |
| is_published | bool | Show/hide |

---

## API

| Method | Path | Returns |
|--------|------|---------|
| GET | `/api/v1/growth/seo/pages` | List slugs, types, titles |
| GET | `/api/v1/growth/seo/pages/{slug}` | Full page content |

---

## Seed Pages (Migration 041)

| Slug | Type | Title |
|------|------|-------|
| how-to-write-a-novel | guide | How to Write a Novel: A Step-by-Step Guide |
| how-to-write-nonfiction | guide | How to Write a Nonfiction Book |
| ai-writing-assistant | feature | AI Writing Assistant for Authors |

---

## Frontend Integration

1. **Dynamic route**: `/guides/[slug]` or `/writing/[slug]` — fetch from API
2. **Metadata**: `generateMetadata` → fetch page, set title, description
3. **Internal links**: Render `internal_links` as related links in footer
4. **Sitemap**: Include `/guides/*`, `/writing/*` in sitemap.xml

---

## Scalable Structure

- Add pages via `INSERT INTO seo_pages` or future admin UI
- page_type drives layout (guide vs feature)
- content JSONB flexible for sections, lists, etc.
