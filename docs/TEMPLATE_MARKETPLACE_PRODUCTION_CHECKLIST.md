# Template Marketplace – Production Checklist

## Pre-Launch

- [ ] **Migration 044** applied: `alembic upgrade head`
- [ ] **Seed templates & packs**: `seed_project_templates`, `seed_template_packs`
- [ ] **Stripe**: Create Stripe Price for each template pack; set `stripe_price_id` in DB or via admin
- [ ] **Webhook**: Ensure `checkout.session.completed` handler processes `metadata.pack_slug`
- [ ] **Featured templates**: Mark key templates `is_featured=true` via admin or seed

## Admin Access

- [ ] Admin users have `is_admin=true`
- [ ] Admin nav includes Templates and Template packs
- [ ] Admin can toggle featured/disabled, duplicate templates
- [ ] Admin can view pack purchase analytics

## Marketplace UX

- [ ] Template library loads categories and packs
- [ ] Search works (name, description)
- [ ] Featured section displays when templates are featured
- [ ] Locked templates show correct CTA (Upgrade vs Purchase pack)
- [ ] Billing page lists packs and purchase flow

## Future Expansion (Not Required for Launch)

- [ ] **Ratings**: Implement `POST /api/v1/templates/{id}/rate`, display aggregate
- [ ] **Creator submissions**: Submission form, review workflow, approval → create template
- [ ] **Revenue sharing**: Payout job for `revenue_share_pct` on pack purchases

## Confirmation: Production-Ready

The template marketplace system is **production-ready** for:

- Template browsing with categories, featured, and search
- Admin control: upload (create), set pricing, assign tiers, control visibility
- Template pack purchases via Stripe
- Future-ready schema for creator submissions and revenue sharing
