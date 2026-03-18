# Sales Landing Page

Dedicated high-converting sales landing page for AUTHORA. Does not replace the main website.

---

## 1. Page Structure Summary

| Route | Purpose |
|-------|---------|
| `/write-your-book` | Primary sales page |
| `/finish-your-book` | Redirects to `/write-your-book` (301) |
| `/start` | Redirects to `/write-your-book` (301) |

**Layout:** Uses marketing layout (MarketingNav, MarketingFooter). Nested layout forces light theme and off-white background.

---

## 2. Section Breakdown

| # | Section | Purpose |
|---|---------|---------|
| 1 | **Hero** | Headline "Write your book. Actually finish it." + primary CTA + trust badges |
| 2 | **Social proof** | 3 testimonials in cards |
| 3 | **Problem** | "You've started. You've stalled." — empathy, sets up solution |
| 4 | **Solution / Features** | 4 feature cards: Guided structure, AI assistance, Momentum, Smart editing |
| 5 | **How it works** | 3 steps: Create project → Write with guidance → Finish manuscript |
| 6 | **Pricing teaser** | "Start free. Upgrade when ready." + link to /pricing |
| 7 | **FAQ** | 4 common questions |
| 8 | **Final CTA** | "Your book isn't finished yet — but it can be." + CTAPair |

---

## 3. Design

- **Theme:** Light only (`data-theme="light"`)
- **Background:** Off-white `#FAFAF8`
- **Accent:** Orange `#FF6A2B` (primary)
- **Support:** Green `#00A86B` for checkmarks
- **Text:** `#1A1A1A`, `#5F5A54`, `#8C857D`
- **Borders:** `#E8E6E1`
- **Style:** Clean, minimal, premium
- **Mobile:** Responsive grid, stacked sections, touch-friendly CTAs

---

## 4. Production-Ready Confirmation

### Route & navigation
- [x] `/write-your-book` — primary page
- [x] `/finish-your-book` → 301 redirect
- [x] `/start` → 301 redirect
- [x] "Write your book" link in MarketingNav

### Sections
- [x] Hero with CTA
- [x] Social proof (testimonials)
- [x] Problem
- [x] Solution / Features
- [x] How it works
- [x] Pricing teaser
- [x] FAQ
- [x] Final CTA

### Design
- [x] Light theme
- [x] Off-white + orange
- [x] Mobile optimized (responsive)
- [x] Clean, minimal, premium

### Conversion
- [x] CTAPair (Start Writing Free, View Pricing)
- [x] Trust badges (Free tier, No credit card, Cancel anytime)
- [x] Multiple CTAs (hero, pricing teaser, final)
- [x] Analytics prefixes: `sales-hero-`, `sales-final-`

---

## Key Files

| File | Purpose |
|------|---------|
| `apps/web/src/app/(marketing)/write-your-book/page.tsx` | Page content |
| `apps/web/src/app/(marketing)/write-your-book/layout.tsx` | Layout, metadata, light theme |
| `apps/web/next.config.js` | Redirects for /finish-your-book, /start |
| `apps/web/src/components/marketing/MarketingNav.tsx` | Nav link added |
