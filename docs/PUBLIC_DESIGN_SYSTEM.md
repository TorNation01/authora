# AUTHORA Public Site Design System

**Scope:** Marketing site, pricing, features, help pages, and future public content  
**Context:** Use within `[data-theme="marketing"]`  
**Status:** Production-ready

---

## 1. Public-Site Design System Summary

The AUTHORA public design system provides a reusable visual system for all public-facing pages. It enforces premium identity, consistent spacing, typography, and component patterns across homepage, pricing, features, help, and future content.

**Brand feel:** Premium, elegant, sophisticated, calm, modern, luxurious without excess, simple, high-trust, writer-focused. Not playful, game-like, or noisy.

---

## 2. Reusable Component Summary

| Component | Purpose |
|-----------|---------|
| `SectionHeader` | Eyebrow + title + description for section intros |
| `SectionLayout` | Section wrapper with padding, variant (default/muted/accent) |
| `Badge` | Small label (default, success, outline) |
| `PublicButton` | Primary, secondary, tertiary, ghost + sizes |
| `CardFeature` | Feature card with icon, title, description, items |
| `CardPricing` | Pricing card with name, price, features, CTA |
| `CardComparison` | vs → Authora comparison card |
| `CardUseCase` | Use-case card with icon, title, copy |
| `CardTestimonial` | Testimonial placeholder (quote, author, role) |
| `FAQAccordion` | FAQ items with smooth accordion |
| `CTABlock` | Full CTA section (eyebrow, headline, primary/secondary, footer) |
| `ComparisonTable` | Table layout for vs/Authora rows |
| `PublicInput` | Form input with label, error state |
| `EmptyPublic` | Empty/placeholder state for future pages |

**Import:** `from '@/components/public'`

---

## 3. Brand Styling Summary

### Color System
- **Black base:** `--background: 0 0% 4%`
- **Gold accent:** `--primary: 43 74% 49%`
- **Money green:** `--success: 142 52% 42%`
- **White text:** `--foreground: 0 0% 98%`
- **Muted neutrals:** `--muted-foreground: 0 0% 62%`

### Typography
- **Headlines:** `font-serif`, `text-3xl`–`text-5xl`, `font-bold`
- **Body:** `text-base`–`text-lg`, `leading-relaxed`
- **Supporting:** `text-sm`, `text-muted-foreground`
- **Scale:** `--text-hero`, `--text-section`, `--text-card`, `--text-body`, `--text-small`

### Spacing
- **Section padding:** `--section-padding-y: clamp(4rem, 10vw, 6rem)`
- **Content padding:** `--section-padding-x: clamp(1rem, 4vw, 2rem)`
- **Max widths:** `--content-max: 80rem`, `--content-narrow: 42rem`

### Buttons
- **Primary:** Gold bg, glow on hover
- **Secondary:** Outline, subtle hover
- **Tertiary:** Text link style
- **Ghost:** Muted, hover highlight

### Cards
- **Base:** `card-premium` — border `white/[0.08]`, bg `white/[0.02]`
- **Hover:** border `white/[0.12]`, bg `white/[0.04]`, shadow lift

### Section Rhythm
- Alternating `default` / `muted` for visual breathing room
- Large padding between sections
- No cramped stacking

---

## 4. Style Guide Notes for Future Marketing Pages

1. **Always wrap public pages** in a parent with `data-theme="marketing"` (handled by marketing layout).

2. **Use `SectionLayout`** for consistent section padding and variants.

3. **Use `SectionHeader`** for section intros; add `eyebrow` for optional label.

4. **Buttons:** Prefer `PublicButton` with `variant="primary"` for main CTAs, `variant="secondary"` for secondary actions.

5. **Cards:** Use `CardFeature`, `CardPricing`, `CardComparison`, `CardUseCase`, or `CardTestimonial` instead of raw divs.

6. **FAQ:** Use `FAQAccordion` with `FAQItem[]` for consistent accordion behavior.

7. **Forms:** Use `PublicInput` for inputs; add `input-public` class for textareas.

8. **Empty states:** Use `EmptyPublic` for placeholder content on new pages.

9. **Icons:** Lucide icons, 16–24px typical; use `text-primary` or `text-success` for accent.

10. **Avoid:** Playful animations, game-like styling, noisy gradients, cramped layouts.

---

## 5. Production Readiness Confirmation

✅ **The public design system is production-ready.**

- Design tokens defined
- Reusable components implemented
- Typography, spacing, button, card, badge systems in place
- Section layout, FAQ, CTA, comparison, pricing patterns
- Form and empty-state styles
- Header/footer utility classes
- Style guide documented for future pages
