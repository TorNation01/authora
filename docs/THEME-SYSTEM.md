# AUTHORA Color System

Production-ready dual-theme token system. Light (default) | Dark (optional toggle). No hard-coded colors — tokens only.

---

## 1. Theme Token Summary

### Light Theme (Default)

| Token | Hex | HSL | Use |
|-------|-----|-----|-----|
| `--background` | #FAF9F7 | 40 20% 98% | Page background |
| `--background-secondary` | #FFFFFF | 0 0% 100% | Cards, surfaces |
| `--background-soft` | #F3F1EC | 40 25% 94% | Muted areas |
| `--foreground` | #1A1A1A | 0 0% 10% | Primary text |
| `--foreground-secondary` | #5F5A54 | 30 6% 35% | Secondary text |
| `--muted-foreground` | #8C857D | 30 8% 52% | Muted text |
| `--primary` | #FF6A2B | 18 100% 58% | Accent, CTAs |
| `--primary-hover` | #E85C1F | 18 81% 52% | Hover state |
| `--primary-soft` | #FFE6DB | 18 100% 93% | Soft accent bg |
| `--success` | #00A86B | 160 100% 33% | Green support |
| `--support-gold` | #D4AF37 | 43 65% 52% | Gold support |

### Dark Theme (Optional)

| Token | Hex | HSL | Use |
|-------|-----|-----|-----|
| `--background` | #0B0B0B | 0 0% 4% | Page background |
| `--background-surface` | #141414 | 0 0% 8% | Cards, surfaces |
| `--background-elevated` | #1E1E1E | 0 0% 12% | Elevated surfaces |
| `--foreground` | #F5F5F5 | 0 0% 96% | Primary text |
| `--foreground-secondary` | #A1A1A1 | 0 0% 63% | Secondary text |
| `--primary` | #FF6A2B | 18 100% 58% | Orange accent |
| `--accent` | #D4AF37 | 43 65% 52% | Gold accent |
| `--success` | #00C27A | 160 100% 38% | Green accent |

---

## 2. Implementation Summary

| File | Purpose |
|------|---------|
| `design-tokens.css` | All theme tokens (light + dark) |
| `tailwind.config.ts` | Maps tokens to Tailwind colors (background-soft, primary-hover, support-gold, etc.) |
| `ThemeProvider.tsx` | Theme state, persistence, `data-theme` on `<html>` |
| `layout.tsx` | ThemeProvider, beforeInteractive script |
| `settings/page.tsx` | Theme toggle (Appearance) |
| `button.tsx` | Uses `hover:bg-primary-hover` |
| `globals.css` | ProseMirror mark uses `bg-primary-soft` |

**Tailwind colors:**
- `bg-background`, `bg-background-soft`, `bg-background-surface`, `bg-background-elevated`
- `text-foreground`, `text-muted-foreground`
- `bg-primary`, `bg-primary-hover`, `bg-primary-soft`
- `bg-support-gold`, `bg-support-green`

---

## 3. Rules

- Light theme is default
- Dark theme toggle supported (Settings → Appearance)
- No hard-coded colors — use tokens only
- Consistency across app via shared tokens

---

## 4. Production-Ready Confirmation

- [x] Light theme default
- [x] Dark theme optional toggle
- [x] Full hex palette implemented as HSL tokens
- [x] No hard-coded colors in theme system
- [x] Tailwind integration for all tokens
- [x] Primary hover state (#E85C1F)
- [x] Support colors (green, gold)
- [x] Dark theme surfaces (primary, surface, elevated)
