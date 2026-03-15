# AUTHORA Low-Priority Polish List

Items for post-launch improvements. Not blockers.

---

## Testing

- [ ] Add `@testing-library/jest-dom` and fix web unit tests
- [ ] Add more Vitest unit tests for components (Card, Input, etc.)
- [ ] Add E2E tests for editor autosave, version history
- [ ] Add E2E tests for export flow (full)
- [ ] Add E2E tests for admin panel
- [ ] CI pipeline for API + web + E2E

## UX

- [ ] Skeleton loaders for async content
- [ ] Improved empty states with illustrations
- [ ] Keyboard shortcuts in editor
- [ ] Dark mode toggle (if not present)

## Accessibility

- [ ] Full WCAG 2.1 audit
- [ ] Screen reader testing
- [ ] Focus trap in modals
- [ ] Skip-to-content link

## Performance

- [ ] Lighthouse score audit
- [ ] Image optimization (WebP, lazy load)
- [ ] Code splitting for large routes
- [ ] API response caching where appropriate

## Observability

- [ ] Structured JSON logging
- [ ] Request tracing (OpenTelemetry)
- [ ] Custom metrics (Prometheus)
- [ ] Error tracking (Sentry)

## Developer Experience

- [ ] API client SDK generation
- [ ] Storybook for components
- [ ] Development seed script with sample data
- [ ] Hot reload for API (optional)
