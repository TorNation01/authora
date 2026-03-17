# AUTHORA In-App Conversion Optimization System

Natural, well-timed upgrade triggers. Helpful tone, not pushy, benefit-focused.

---

## 1. Trigger System Summary

| Trigger | When | Action |
|---------|------|--------|
| **usage_limit** | Project/book limit reached (API error or pre-check) | Show upgrade modal |
| **momentum** | Streak ≥ 3 days, can upgrade | `useMomentumTrigger` returns true → component shows CTA |
| **stuck** | (Reserved) No activity for X days | Component can call `showUpgrade('stuck')` |
| **near_completion** | Book progress ≥ 80%, no Finish Mode | `useNearCompletionTrigger` returns true → component shows CTA |
| **feature_locked** | User clicks locked feature (Ghostwriter, Finish Mode) | Show upgrade modal |

### Integration Points

- **Project create** (`/dashboard/projects/new`): Pre-check `projectCreateGuard()` before create; on API limit error, `handleLimitError()` shows modal
- **Ghostwriter link** (ManuscriptSidebar): Wrapped in `FeatureGate`; when locked, click shows upgrade
- **Ghostwriter page**: Guard on mount; if no access, show upgrade and redirect
- **Finish Mode button** (ManuscriptSidebar): Wrapped in `FeatureGate`; when locked, click shows upgrade

---

## 2. Upgrade Flow Summary

### UpgradeModal

- Clean modal with benefit explanation
- Simple pricing display (Pro plan)
- Upgrade button → Stripe checkout
- "Maybe later" and "Compare all plans" links

### FeatureGate

- Wraps locked features
- When user has access: renders children (Link/button)
- When locked: renders clickable button with Lock icon; click opens upgrade modal
- Locked features remain **visible** and **clickable**

### Copy Style

- Helpful, not pushy
- Focused on benefit
- Examples: "You're making progress", "You're on a roll", "A little help when you need it"

---

## 3. Files

| File | Purpose |
|------|---------|
| `content/conversion-copy.ts` | Trigger-specific copy |
| `components/conversion/UpgradeModal.tsx` | Upgrade modal |
| `components/conversion/FeatureGate.tsx` | Locked feature wrapper |
| `contexts/UpgradeTriggerContext.tsx` | `showUpgrade`, `hideUpgrade` |
| `hooks/use-conversion-triggers.ts` | `useLimitErrorHandler`, `useProjectCreateGuard`, `useMomentumTrigger`, `useNearCompletionTrigger` |

---

## 4. Production-Ready Confirmation

- [x] Usage limit trigger (pre-check + API error)
- [x] Momentum trigger (hook for components)
- [x] Near completion trigger (hook for components)
- [x] Feature locked trigger (FeatureGate)
- [x] Clean upgrade modal
- [x] Benefit-focused copy
- [x] Stripe checkout integration
- [x] Locked features visible and clickable
