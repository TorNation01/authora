# AUTHORA Marketing Landing Page — Summary

## 1. Landing Page Structure Summary

The marketing site at **authora.studio** is built as a single-page landing experience with 14 sections, plus supporting pages.

### Homepage Sections (in order)

| # | Section | ID / Anchor | Purpose |
|---|---------|-------------|---------|
| 1 | **Hero** | — | Primary value prop, CTAs, trust microcopy |
| 2 | **Problem** | — | Pain points writers face |
| 3 | **Solution** | — | Six feature pillars |
| 4 | **How It Works** | `#how-it-works` | 4-step flow |
| 5 | **Feature Differentiator** | — | Story Integrity Engine™, Story Density Engine™ |
| 6 | **Writing Experience** | — | Writing Studio, AI, Research, Revision |
| 7 | **Accountability** | — | Goals, streaks, Finish Mode |
| 8 | **Flexibility** | — | Multi-project, fiction + non-fiction |
| 9 | **Use Cases** | — | Fiction, non-fiction, memoir, etc. |
| 10 | **Why Different** | — | Comparison themes |
| 11 | **Pricing Teaser** | — | Free/Starter/Pro/Studio, View Pricing |
| 12 | **FAQ** | — | 6 polished FAQs |
| 13 | **Final CTA** | — | Conversion push |
| 14 | **Footer** | — | Trust, links |

### Supporting Pages

- `/` — Homepage (landing)
- `/pricing` — Pricing plans
- `/faq` — Full FAQ
- `/contact` — Contact form
- `/privacy` — Privacy policy
- `/terms` — Terms of service

---

## 2. Page / Component Summary

### Components (`apps/web/src/components/marketing/`)

| Component | Purpose |
|-----------|---------|
| `MarketingNav` | Sticky nav: How It Works, Pricing, FAQ, Contact; Login / Start Writing Free |
| `MarketingFooter` | Trust items (Secure, Private, Your work stays yours, Built for real writers); Privacy, Terms, Contact, Pricing, Login, Sign up |
| `HeroSection` | Headline, subheadline, 5 support bullets, primary/secondary CTAs, trust line, preview block |
| `ProblemSection` | "Most people do not fail because they cannot write" + 6 pain points |
| `SolutionSection` | "A complete writing system" + 6 pillars |
| `HowItWorksSection` | 4 steps with anchors |
| `FeatureDifferentiatorSection` | Story Integrity Engine, Story Density Engine, combined line |
| `WritingExperienceSection` | 4 feature blocks |
| `AccountabilitySection` | Goals, streaks, Finish Mode |
| `FlexibilitySection` | Multi-project, modes, fiction + non-fiction |
| `UseCasesSection` | 7 use cases |
| `WhyDifferentSection` | 5 comparison themes |
| `PricingTeaserSection` | Plan names, CTAs |
| `FAQSection` | 6 accordion FAQs |
| `CTASection` | Final conversion block |

### Layout

- `(marketing)/layout.tsx` — Wraps all marketing routes with `MarketingNav`, `MarketingFooter`, and `data-theme="marketing"` for design tokens.

### Design Tokens

- `design-tokens-marketing.css` — Black base, gold primary, money green accent, white text. Applied when `[data-theme="marketing"]`.

---

## 3. CTA and Conversion Path Summary

### Primary CTAs

| Location | CTA Text | Destination |
|----------|----------|-------------|
| Nav | Start Writing Free | `app.authora.studio/register` |
| Hero | Start Writing Free | `app.authora.studio/register` |
| Hero | See How It Works | `#how-it-works` (anchor) |
| Pricing Teaser | Start Writing Free | `app.authora.studio/register` |
| Pricing Teaser | View Pricing | `/pricing` |
| Final CTA | Start Writing Free | `app.authora.studio/register` |
| Final CTA | Create Your First Book | `app.authora.studio/register` |
| Footer | Sign up | `app.authora.studio/register` |

### Secondary CTAs

| Location | CTA Text | Destination |
|----------|----------|-------------|
| Nav | Sign in | `app.authora.studio/login` |
| Footer | Login | `app.authora.studio/login` |

### Conversion Paths

1. **Direct sign-up**: Homepage → Start Writing Free → Register
2. **Learn then sign**: Homepage → See How It Works → scroll → Start Writing Free
3. **Pricing path**: Homepage → View Pricing → `/pricing` → Start Writing Free
4. **FAQ path**: Homepage → FAQ accordion or View all FAQs → `/faq`
5. **Contact path**: Nav/Footer → Contact → `/contact`

### Analytics Hooks

- `data-analytics="marketing-nav"` — Nav
- `data-analytics="marketing-footer"` — Footer
- `data-analytics="hero"` — Hero section
- `data-analytics="cta-start-free"` — Hero primary CTA
- `data-analytics="hero-preview"` — Hero preview block
- `data-analytics="cta"` — Final CTA section
- `data-analytics="pricing-teaser"` — Pricing teaser
- `data-analytics="faq"` — FAQ section
- `data-analytics="contact-form"` — Contact form
- `data-analytics="feature-differentiator"` — Feature differentiator
- `data-analytics="story-integrity"` — Story Integrity Engine
- `data-analytics="story-density"` — Story Density Engine

---

## 4. SEO / Meta Summary

### Root Layout

- `metadataBase`: `https://authora.studio` (or `NEXT_PUBLIC_MARKETING_URL` / `NEXT_PUBLIC_WEB_URL`)

### Homepage (`/`)

- **Title**: Authora | Finally Finish the Book You've Been Trying to Write
- **Description**: Authora helps you start, structure, write, improve, and finish your book — with AI guidance, smart editing tools, and built-in momentum that keeps you moving.
- **Keywords**: book writing, author tool, AI writing, finish your book, writing app, novel writing, memoir, non-fiction, manuscript
- **Canonical**: `/`
- **Open Graph**: title, description, type, url
- **Twitter**: summary_large_image, title, description

### Pricing (`/pricing`)

- **Title**: Pricing | Authora
- **Description**: Start free. Upgrade when you are ready. Free, Starter, Pro, and Studio plans.
- **Canonical**: `/pricing`
- **Open Graph**: title, description, url

### Sitemap

- `sitemap.ts` — Includes: `/`, `/features`, `/pricing`, `/faq`, `/contact`, `/demo`, `/terms`, `/privacy`
- Served at `/sitemap.xml`

### Robots

- `robots.ts` — References sitemap URL

---

## 5. Production Readiness Confirmation

### ✅ Implemented

- [x] Responsive layout (mobile, tablet, desktop)
- [x] Premium dark theme (black, gold, money green, white)
- [x] All 14 sections with specified copy
- [x] Reusable marketing components
- [x] SEO metadata (title, description, keywords)
- [x] Open Graph metadata
- [x] Canonical URLs (homepage, pricing)
- [x] Sitemap support (`/sitemap.xml`)
- [x] Analytics hooks (`data-analytics` attributes)
- [x] CTA tracking attributes
- [x] App routing: Login/Register → `app.authora.studio` via `getAppBaseUrl()`
- [x] Pricing page routing (`/pricing`)
- [x] Sign-up/Login routing
- [x] Help/Contact/Privacy/Terms routing
- [x] Accessibility: focus-visible, semantic HTML, ARIA where needed
- [x] Build passes (`npm run build`)

### Domain Structure

- **authora.studio** — Marketing (this site)
- **app.authora.studio** — Application (via `getAppBaseUrl()`)
- **api.authora.studio** — Backend API

### Environment Variables

- `NEXT_PUBLIC_MARKETING_URL` — Marketing base (e.g. `https://authora.studio`)
- `NEXT_PUBLIC_APP_URL` — App base (e.g. `https://app.authora.studio`)
- `NEXT_PUBLIC_WEB_URL` — Fallback for metadataBase

---

**Status**: Production-ready. The AUTHORA marketing landing page is implemented, builds successfully, and meets the specified requirements.
