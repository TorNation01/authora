# AUTHORA CTA System — Production-Ready Summary

## 1. CTA System Summary

The public site uses a **centralized CTA system** that keeps conversion flows consistent without feeling pushy or over-marketed.

### Components

| Component | Purpose |
|-----------|---------|
| `CTAButton` | Single CTA with analytics, primary/secondary styling |
| `CTAPair` | Primary + secondary pair with optional microcopy |
| `cta-copy.ts` | Centralized labels, routes, microcopy, trust badges |

### Primary CTAs

| Label | Route | Use |
|-------|-------|-----|
| Start Writing Free | `/register` | Hero, engines, pricing teaser, features |
| Start Free | `/register` | Pricing hero, FAQ close, footer |
| Create Your First Book | `/register` | Final CTA section, How It Works |

### Secondary CTAs

| Label | Route | Use |
|-------|-------|-----|
| See How It Works | `#how-it-works` | Hero |
| View Pricing | `/pricing` | Engines, features, footer |
| View Full Pricing | `/pricing` | Pricing teaser |
| Explore Features | `/features` | How It Works |
| Compare Plans | `/pricing#compare-plans` | Pricing hero, pricing final |

### Design Rules

- **Clear hierarchy** — Primary (filled, gold glow) vs secondary (outline)
- **Premium visual distinction** — `shadow-glow-gold-subtle`, `border-white/20`
- **Strategic placement** — Not excessive; one CTA pair per section
- **Route flow** — All primary CTAs → signup; secondary → pricing, features, or anchor
- **Analytics** — Every CTA has `data-analytics="{prefix}{id}"` for tracking

---

## 2. Conversion Path Summary

| Path | Entry Points | Destination |
|------|--------------|-------------|
| **Sign up** | Hero, How It Works, Pricing Teaser, Engines, Story Integrity, Story Density, Final CTA, FAQ, Footer, Features | `/register` |
| **Learn more** | Hero (See How It Works), How It Works (Explore Features) | `#how-it-works`, `/features` |
| **Pricing** | Engines, Pricing Teaser, FAQ, Footer, Features | `/pricing` |
| **Compare plans** | Pricing hero, Pricing final | `/pricing#compare-plans` |

### Low-Friction Signup Language

- "Start Writing Free" / "Start Free" — no commitment framing
- "Create Your First Book" — action-oriented, specific
- Trust microcopy: "No credit card required", "Upgrade when you're ready", "Begin with one project for free"

---

## 3. CTA Placement Summary

| Section | Primary | Secondary | Microcopy |
|---------|---------|-----------|-----------|
| **Hero** | Start Writing Free | See How It Works | No clutter. No guesswork. Just a clear path to a finished book. |
| **How It Works** | Create Your First Book | Explore Features | Start writing in under a minute. |
| **Pricing Teaser** | Start Writing Free | View Full Pricing | Upgrade when you're ready. |
| **Engines Combined** | Start Writing Free | View Pricing | — |
| **Story Integrity** | Start Writing Free | View Pricing | — |
| **Story Density** | Start Writing Free | View Pricing | — |
| **Final CTA** | Start Writing Free | Create Your First Book | Stop circling the idea. Start finishing the book. |
| **FAQ close** | Start Free | View Pricing | Still have questions? Start free and explore. |
| **Footer** | Start Free | View Pricing | No clutter. No guesswork. Just a clear path forward. |
| **Pricing Hero** | Start Free | Compare Plans | Upgrade anytime as your writing grows. No credit card required for Free. |
| **Pricing Final** | Start Free | Compare Plans | Join writers who are actually finishing their books. |
| **Features** | Start Writing Free | View Pricing | Begin with one project for free. |

### Trust Badges (Pricing Teaser)

- Free forever tier
- No credit card
- Cancel anytime

---

## 4. Production Readiness Confirmation

The public-site CTA system is **production-ready**:

- [x] Consistent CTA system across homepage, features, pricing, footer, FAQ
- [x] Primary CTAs: Start Writing Free, Start Free, Create Your First Book
- [x] Secondary CTAs: See How It Works, View Pricing, Explore Features, Compare Plans
- [x] Clear hierarchy (primary vs secondary styling)
- [x] Premium visual distinction (gold glow, outline)
- [x] Strategic placement (not excessive)
- [x] Route flow to signup, app, pricing
- [x] `data-analytics` on all CTAs for event tracking
- [x] Trust microcopy near CTAs
- [x] Low-friction signup language
- [x] Value reinforcement near conversion points
- [x] Conversion-safe section spacing (`--section-padding-y`)
- [x] CTA consistency across desktop and mobile (flex-col sm:flex-row)
- [x] SSO fallback when standalone_auth is disabled
- [x] Build passes
