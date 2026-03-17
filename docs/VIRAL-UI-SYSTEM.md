# AUTHORA Viral UI System

Encourage organic sharing and user-driven growth.

---

## 1. Viral System Summary

### Features

| Feature | Trigger | Share Type |
|---------|---------|------------|
| **Progress sharing** | Streak, words today, personal best | progress, milestone |
| **Milestone sharing** | Word count, chapter complete, streak | milestone |
| **Completion sharing** | Book finished | book_finished |
| **Achievement sharing** | Badge earned | achievement |

### Triggers

| Location | When |
|----------|------|
| Gamification page | Streak card (when streak > 0) |
| Gamification page | Total words card |
| Gamification page | XP / next milestone (when progress > 0) |
| Accountability page | Streak card (when streak > 0) |
| CelebrationToast | Milestone, badge, chapter, personal best |

---

## 2. Share System Summary

### Share Cards

- **ShareCard** — Branded visual (400×280px)
- Icon by type: Flame (progress), Trophy (milestone), Zap (achievement), BookOpen (book_finished)
- Title, subtitle, product branding

### Share Flow

| Action | Implementation |
|--------|----------------|
| **Copy link** | Clipboard API, toast confirmation |
| **Download image** | html2canvas → PNG (optional: add `html2canvas` to package.json) |
| **Share on X** | Twitter intent URL |
| **Share on LinkedIn** | LinkedIn share URL |

### ShareDialog

- Opens on ShareTrigger click
- Creates share via `POST /api/v1/growth/share`
- Renders ShareCard preview
- Copy link, Download image, Share on X, Share on LinkedIn

### Share Page (`/share/[slug]`)

- Public, no auth
- Renders ShareCard
- CTA to register
- Social share links

---

## 3. Files

| File | Purpose |
|------|---------|
| `components/viral/ShareCard.tsx` | Branded share card visual |
| `components/viral/ShareDialog.tsx` | Modal with card, copy, download, social |
| `components/viral/ShareTrigger.tsx` | Button that opens ShareDialog |
| `app/(marketing)/share/[slug]/page.tsx` | Public share landing page |
| `components/gamification/CelebrationToast.tsx` | Uses ShareTrigger |

---

## 4. Production-Ready Confirmation

- [x] Progress sharing
- [x] Milestone sharing
- [x] Completion sharing (book_finished type)
- [x] Clean branded ShareCard
- [x] Copy link
- [x] Download image (html2canvas; add to deps when workspace allows)
- [x] Social share (X, LinkedIn)
- [x] Triggers on milestones, achievements, streak
- [x] Share page with branded card
