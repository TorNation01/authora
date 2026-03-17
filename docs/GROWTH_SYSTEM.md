# AUTHORA Growth Domination System

Production-ready product-led growth: viral share, content generation, SEO, invite loop, achievements, admin controls.

---

## 1. Growth System Summary

### Viral Share System

| Feature | Implementation |
|---------|----------------|
| **Share progress** | `POST /api/v1/growth/share` (share_type: progress) |
| **Share milestones** | share_type: milestone |
| **Share achievements** | share_type: achievement |
| **Shareable links** | `/share/{slug}` — public, branded card |
| **Branded share cards** | Auto-generated title, subtitle, CTA |
| **Social integrations** | Twitter, LinkedIn share URLs in response |

### Content Generation Engine

| Output | Source |
|--------|--------|
| **"I wrote 1,000 words today"** | progress + words in payload |
| **"I finished my first book"** | book_finished |
| **"I completed chapter 10"** | milestone + chapter in payload |
| **Clean visual cards** | `card` object: title, subtitle, cta |
| **Social captions** | `caption` field |
| **Share buttons** | `social_links` (twitter, linkedin) |

### SEO Content System

| Type | Slug example | Internal linking |
|------|--------------|------------------|
| **Writing guides** | `/guides/how-to-write-a-novel` | features, pricing |
| **Feature pages** | `/features/ai-writing-assistant` | pricing, story-integrity |
| **Use-case pages** | `/for-fiction-writers`, `/for-nonfiction-writers` | existing |

- **Indexed**: Standard Next.js pages; add sitemap
- **API**: `GET /api/v1/growth/seo/pages`, `GET /api/v1/growth/seo/pages/{slug}`
- **Scalable**: `seo_pages` table; admin can add via DB or future UI

### Invite Loop

| Step | Implementation |
|------|----------------|
| **Share** | User gets `invite_url` from `GET /api/v1/growth/referral/code` |
| **Signup** | `POST /auth/register` with `referral_code` |
| **Reward** | `resolve_referral_on_signup` links invitee; incentives config for future reward grants |

### Achievement System

| Feature | Implementation |
|---------|----------------|
| **Milestones** | Existing: streak, words, chapters (badge_definitions) |
| **Badges** | Non-childish: "10K Club", "Week Warrior", "Chapter One" |
| **Progress achievements** | Daily quests, weekly missions, focus sessions |
| **Share triggers** | Call `POST /growth/share` with share_type=achievement when badge earned |

### Admin Growth Controls

| Control | API |
|---------|-----|
| **Enable/disable features** | `PATCH /api/v1/growth/admin/settings` — features.share_progress, share_milestones, share_achievements, referral_enabled |
| **Adjust incentives** | incentives.referral_reward_days, referral_invitee_reward_days |
| **Campaigns** | campaigns (JSON) for future campaign config |

---

## 2. Viral Loop Summary

```
User earns achievement → Share prompt → Create share link → Get card + caption + social URLs
                                    → Friend sees /share/{slug} → CTA to register
                                    → Friend signs up with ?ref=CODE → Referral resolved
```

**Share types:** progress, milestone, achievement, book_finished

**Public share page:** `https://authora.studio/share/{slug}` — no auth; shows card + CTA + social share buttons.

---

## 3. SEO System Summary

### Programmatic Pages

| Page type | Table | Slug pattern |
|-----------|-------|--------------|
| guide | seo_pages | how-to-write-a-novel |
| feature | seo_pages | ai-writing-assistant |
| use-case | Next.js routes | for-fiction-writers |

### Structure

- **seo_pages**: slug, page_type, title, meta_description, content (JSONB), internal_links (array)
- **Internal linking**: Each page has `internal_links` array; render as footer/related links
- **Indexed**: Use Next.js metadata; add `generateMetadata` from API for dynamic pages

### Seed Pages (migration 041)

- `how-to-write-a-novel` (guide)
- `how-to-write-nonfiction` (guide)
- `ai-writing-assistant` (feature)

---

## 4. Production-Ready Confirmation

### Checklist

- [x] Share progress
- [x] Share milestones
- [x] Share achievements
- [x] Shareable links
- [x] Branded share cards
- [x] Social integrations (URLs)
- [x] Content generation (cards, captions)
- [x] SEO programmatic pages
- [x] Internal linking
- [x] Referral/invite loop
- [x] Achievement system (existing + share)
- [x] Admin growth controls
- [x] feature_growth flag

### API Endpoints

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/growth/share` | User |
| GET | `/api/v1/growth/share/{slug}` | Public |
| GET | `/api/v1/growth/referral/code` | User |
| GET | `/api/v1/growth/seo/pages` | Public |
| GET | `/api/v1/growth/seo/pages/{slug}` | Public |
| GET | `/api/v1/growth/admin/settings` | Admin |
| PATCH | `/api/v1/growth/admin/settings` | Admin |

### Configuration

```bash
FEATURE_GROWTH=true  # Default
```

---

## See Also

- [VIRAL_LOOP_SUMMARY.md](./VIRAL_LOOP_SUMMARY.md)
- [SEO_SYSTEM_SUMMARY.md](./SEO_SYSTEM_SUMMARY.md)
- [COMMUNITY_FINAL_OUTPUTS.md](./COMMUNITY_FINAL_OUTPUTS.md)
