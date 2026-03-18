# Premium Template Packs – Pricing Structure

## Pricing Overview

| Pack | Price | Templates | Per-Template |
|------|-------|-----------|--------------|
| Write Your First Book | $29 | 5 | $5.80 |
| Fiction Mastery Pack | $49 | 8 | $6.13 |
| Non-Fiction Authority Pack | $49 | 8 | $6.13 |
| AI Writing Pack | $29 | 4 | $7.25 |
| Finish Your Book System | $29 | 4 | $7.25 |
| Business Book Builder | $29 | 4 | $7.25 |

## Tier Structure

- **Entry tier ($29)**: Write Your First Book, AI Writing Pack, Finish Your Book System, Business Book Builder  
- **Mastery tier ($49)**: Fiction Mastery Pack, Non-Fiction Authority Pack (larger packs, more templates)

## Stripe Configuration

- `stripe_price_id` is `None` in definitions; set via environment or Stripe Dashboard
- Create Stripe Price for each pack slug; store ID in DB or `template_pack_definitions.py`
- Webhook: `checkout.session.completed` with `metadata.pack_slug` creates `TemplatePackPurchase`

## Pack Slugs (for API/Stripe)

- `write-your-first-book`
- `fiction-mastery-pack`
- `nonfiction-authority-pack`
- `ai-writing-pack`
- `finish-your-book-system`
- `business-book-builder`
