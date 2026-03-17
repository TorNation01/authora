# AUTHORA Homepage UI Summary

**Domain:** authora.studio (marketing) · app.authora.studio (app)  
**Status:** Production-ready  
**Last updated:** 2025-03-17

---

## 1. Homepage UI Summary

The AUTHORA marketing homepage is a premium, elegant, high-converting SaaS landing experience. It communicates product value within 3 seconds, creates emotional pull, and guides users toward sign-up with clear CTAs.

**Brand direction:** Premium, elegant, sophisticated, calm, futuristic but professional, high-trust, easy to understand.

**Color direction:** Black base, gold accent, money green support, white primary text, subtle gradients, soft glow used sparingly, clean contrast.

---

## 2. Section Layout Summary

| # | Section | Layout | Key elements |
|---|---------|--------|--------------|
| 1 | Hero | Centered, max-w-4xl | Headline, subheadline, value bullets, primary + secondary CTA, product mockup |
| 2 | Problem | Centered header, 3-col grid | Empathetic intro, 6 pain-point cards with icons |
| 3 | Solution | Centered header, 3-col grid | 6 pillar cards with icons |
| 4 | How It Works | 4-col horizontal flow | Numbered steps with icons, arrow connectors (desktop) |
| 5 | Story Integrity Engine | Full-width card, split layout | Icon, headline, bullets, CTA block |
| 6 | Story Density Engine | Full-width card, split layout | Green accent, icon, bullets, CTA block |
| 7 | Engines Combined | Centered card | Brain icon, headline, CTAs |
| 8 | Writing Experience | 4-col grid | 4 feature cards (Studio, AI, Research, Revision) |
| 9 | Accountability | 5-col grid | Metric cards (goals, streaks, reminders, milestones, Finish Mode) |
| 10 | Flexibility | Centered, flex-wrap pills | 5 flexibility points as pill cards |
| 11 | Use Cases | 4-col grid | 7 use-case cards with icons |
| 12 | Why Different | 3-col grid | 5 comparison cards (vs → Authora) |
| 13 | Pricing Teaser | Centered card | Plan badges, CTAs, trust bullets |
| 14 | FAQ | Single column | Accordion items with smooth open/close |
| 15 | Final CTA | Centered | Headline, supporting line, primary + secondary CTA |
| 16 | Footer | Multi-column | Trust badges, nav groups, app links, copyright |

---

## 3. Component Summary

| Component | Purpose |
|-----------|---------|
| `HeroSection` | Above-the-fold hero with headline, bullets, CTAs, product preview |
| `ProblemSection` | Pain-point cards with empathetic framing |
| `SolutionSection` | Pillar cards (6) |
| `HowItWorksSection` | 4-step flow with icons |
| `FeatureDifferentiatorSection` | Wrapper for Story Engine sections |
| `StoryIntegrityEngineSection` | Gold-accent feature card |
| `StoryDensityEngineSection` | Green-accent feature card |
| `EnginesCombinedSection` | Combined engines CTA card |
| `WritingExperienceSection` | 4 feature cards |
| `AccountabilitySection` | 5 metric cards |
| `FlexibilitySection` | Flexibility pill cards |
| `UseCasesSection` | 7 use-case cards |
| `WhyDifferentSection` | 5 comparison cards |
| `PricingTeaserSection` | Plan preview + CTAs |
| `FAQSection` | Accordion FAQ |
| `CTASection` | Final conversion push |
| `MarketingNav` | Sticky nav with links + CTA |
| `MarketingFooter` | Trust, nav, legal, app links |

**Design system classes:**
- `card-premium` — Premium card with hover state (marketing theme)
- `animate-fade-up` — Entrance animation
- `animation-delay-*` — Staggered animation delays

---

## 4. Responsive Behaviour Summary

| Breakpoint | Behaviour |
|------------|-----------|
| Mobile (< 640px) | Single column, stacked sections, full-width cards, mobile nav drawer |
| Tablet (640–1024px) | 2-col grids where appropriate, horizontal CTAs |
| Desktop (1024px+) | 3–5 col grids, step arrows in How It Works, split layouts in Engine sections |

**Section padding:** `clamp(4rem, 10vw, 6rem)` vertical, `clamp(1rem, 4vw, 2rem)` horizontal.

**Content max-width:** 80rem (7xl) for most sections; 42rem (narrow) for text-heavy blocks.

---

## 5. Production Readiness Confirmation

✅ **The homepage UI is production-ready.**

- Premium visual treatment (black base, gold accent, money green)
- Strong type hierarchy and spacing
- Clear CTA hierarchy (primary + secondary)
- Smooth scroll, hover states, entrance animations
- Responsive across mobile, tablet, desktop
- Accessible (focus states, aria attributes, keyboard nav)
- Domain structure: authora.studio (marketing), app.authora.studio (app)
- Config-driven (feature flags, branding)
