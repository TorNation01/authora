# AUTHORA Brand System

Production-ready design system. Premium feel, simplicity, no visual noise, consistency across app and marketing.

---

## 1. Brand System Summary

### Typography
- **Primary font:** Inter (400, 500, 600, 700)
- **Type scale:** xs (12px) → sm (14px) → base (16px) → lg (18px) → xl (20px) → 2xl (24px) → 3xl (30px) → 4xl (36px) → 5xl (48px)
- **Line height:** tight 1.25, snug 1.375, normal 1.5, relaxed 1.625, loose 2
- **Hierarchy:** Strong via weight + size; readable spacing

### Spacing (8px grid)
| Token | Value | Use |
|-------|-------|-----|
| space-1 | 4px | Tight gaps |
| space-2 | 8px | Base unit |
| space-4 | 16px | Component padding |
| space-6 | 24px | Card padding |
| space-8 | 32px | Section gaps |
| space-12 | 48px | Large gaps |
| space-16 | 64px | Section rhythm |
| space-24 | 96px | Major sections |
| section-gap | 96px | Section spacing |
| section-gap-sm | 64px | Compact sections |
| section-gap-lg | 128px | Hero / large sections |

### Interaction
- **Transitions:** fast 150ms, base 200ms, slow 300ms
- **Easing:** ease-out
- **Micro-interactions:** active:scale-[0.98] on buttons

---

## 2. Component Summary

### Button System
| Variant | Use | States |
|---------|-----|--------|
| **primary** (default) | Orange CTA | hover:primary-hover, focus ring, disabled 50% opacity |
| **secondary** | Subtle actions | border, hover bg, focus ring |
| **ghost** | Text-style, no bg | hover:bg-muted/60 |
| **link** | Inline links | underline on hover, text-primary-hover |
| outline | Bordered alt | hover:bg-muted |
| soft | Soft accent | bg-primary-soft |
| destructive | Danger | red |

**Sizes:** default (h-10), sm (h-9), lg (h-11), icon (10×10)

### Card System
| Variant | Use |
|---------|-----|
| **default** | Soft bg, subtle border, rounded-xl, light shadow, hover shadow lift |
| soft | background-soft, minimal border |
| elevated | Stronger shadow |
| sanctuary | Same as default (legacy) |

### Layout Utilities
- `section-spacing` — py-16 md:py-24
- `section-spacing-sm` — py-12 md:py-16
- `section-spacing-lg` — py-20 md:py-32
- `content-max` — max-w-80rem, responsive px

---

## 3. Global Rules

- **Premium feel:** Clean, refined, no clutter
- **Simplicity:** Avoid visual noise
- **Consistency:** Tokens only, 8px grid, shared transitions
- **Accessibility:** focus-visible ring, disabled states

---

## 4. Production-Ready Confirmation

- [x] Inter primary typography
- [x] Consistent type scale + hierarchy
- [x] 8px grid spacing
- [x] Primary, secondary, text buttons
- [x] Hover, focus, disabled states
- [x] Card system (soft, borders, radius, shadow)
- [x] Layout utilities
- [x] Smooth transitions + micro-interactions
- [x] Premium, simple, consistent
