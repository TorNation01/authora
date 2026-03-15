# AUTHORA Manual QA Checklist

Human verification for UX, accessibility, and edge cases.

---

## Onboarding

- [ ] All onboarding steps render correctly
- [ ] Back/Next navigation works
- [ ] Progress indicator updates
- [ ] Validation messages clear
- [ ] Mobile layout usable

## Auth

- [ ] Password requirements shown on register
- [ ] Error messages readable
- [ ] Remember me / session persistence (if applicable)
- [ ] Forgot password flow (if implemented)

## Dashboard

- [ ] Sidebar collapses/expands on mobile
- [ ] Active route highlighted
- [ ] Empty states have clear CTAs
- [ ] Loading states shown during fetches

## Editor

- [ ] Rich text toolbar works (bold, italic, etc.)
- [ ] Placeholder text visible
- [ ] Word count updates
- [ ] Autosave indicator (saving/saved)
- [ ] Offline/error recovery messaging

## Mobile Responsiveness

- [ ] Landing page readable on 375px width
- [ ] Login/register forms usable
- [ ] Dashboard sidebar adapts
- [ ] Editor usable on tablet
- [ ] Tables scroll horizontally where needed

## Accessibility Basics

- [ ] Focus visible on interactive elements
- [ ] Form labels associated
- [ ] Buttons have accessible names
- [ ] Heading hierarchy logical (h1 → h2 → h3)
- [ ] Color contrast sufficient (manual check)
- [ ] Keyboard navigation works (Tab, Enter)

## Error States

- [ ] 404 page friendly
- [ ] 500/error boundary shows recovery options
- [ ] Network error messaging
- [ ] Validation errors inline

## Performance

- [ ] Initial load < 5s on 3G
- [ ] No obvious layout shift (CLS)
- [ ] Images load progressively
