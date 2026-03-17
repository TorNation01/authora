# AUTHORA Tutorial & Guided Overlay System

Production-ready in-app tutorial and guided overlay system that helps users understand the system while using it, without interrupting flow.

---

## 1. Tutorial System Summary

### Architecture

| Component | Purpose |
|-----------|---------|
| **TutorialContext** | Central state for tutorial progress. Persists to `localStorage` (`authora_tutorial_progress`). |
| **GuidedOverlay** | Step-by-step modal overlays for first-time flows. Dismissible, optional. |
| **FeatureIntroCard** | Compact cards with short explanation, "why it matters," and CTA. |
| **Tooltips** | Short, clear help text on hover. Defined in `HELP_TOOLTIPS`. |

### Tutorial IDs

| ID | Type | When Shown |
|----|------|------------|
| `editor_first` | Overlay | First-time editor use (onboarding covers this) |
| `ai_first` | Overlay | First time opening AI panel |
| `integrity_first` | Overlay | First time opening Story Integrity panel |
| `density_first` | Overlay | First time switching to Density tab |
| `integrity_intro` | Intro card | First encounter with Story Integrity panel |
| `density_intro` | Intro card | First encounter with Story Density tab |
| `finish_mode_intro` | Intro card | When Finish Mode is suggested |

### Non-Intrusive Rules

- **Dismiss anytime** — Every overlay and intro card has a Skip/Dismiss control.
- **No forced flows** — User can skip all tutorials.
- **No repeated annoyance** — Completed/dismissed state is persisted; tutorials never re-show.
- **Progressive disclosure** — Features are introduced when relevant (e.g., density overlay only when user opens Density tab).

---

## 2. Overlay Flow Summary

### AI Panel (`ai_first`)

1. User opens AI panel (toolbar → AI).
2. If `shouldShowOverlay('ai_first')`, `GuidedOverlay` appears.
3. Steps: (1) Select text, choose action; (2) Or describe what you need.
4. User clicks "Got it" or "Skip" → `markCompleted` / `markDismissed`.
5. Overlay never shows again.

### Story Integrity Panel (`integrity_first`)

1. User opens Story Integrity panel (toolbar → Story Health).
2. If `shouldShowOverlay('integrity_first')`, `GuidedOverlay` appears.
3. Steps: (1) Finds unresolved threads, weak arcs, gaps; (2) Click Scan to analyze.
4. User completes or skips → overlay never shows again.
5. **Intro card** (`integrity_intro`) shows at top of Issues tab if not dismissed; CTA "Run scan" triggers scan.

### Story Density Tab (`density_first`)

1. User switches to Density tab inside Story Integrity panel.
2. If `shouldShowOverlay('density_first')`, `GuidedOverlay` appears.
3. Steps: (1) Finds filler, repetition, weak sections; (2) Shows what to cut or strengthen.
4. User completes or skips → overlay never shows again.
5. **Intro card** (`density_intro`) shows at top of Density tab if not dismissed.

### Finish Mode (`finish_mode_intro`)

1. When `suggestFinishMode` is true (user is close to finishing), intro card appears in ManuscriptSidebar.
2. Card explains Finish Mode, why it matters, CTA "Enter Finish Mode".
3. User dismisses or clicks CTA → card never shows again (dismissed).

---

## 3. Tooltip Coverage

| Area | Tooltips |
|------|----------|
| **Editor toolbar** | Notes, AI, Find & Replace, Quick Insert, Dark mode, Story Health |
| **AI panel** | Rewrite, Expand, Shorten, Continue |
| **Story engines** | Story Integrity, Story Density, Scan |
| **Manuscript sidebar** | Chapters, Add chapter, Finish Mode, Ghostwriter, Edit & Polish, Plan |

---

## 4. Production Readiness Confirmation

| Requirement | Status |
|-------------|--------|
| Tooltips short, clear, helpful, optional | ✅ |
| Guided overlays for first-time editor, AI, Integrity, Density | ✅ |
| Feature intro cards for Integrity, Density, Finish Mode | ✅ |
| User can dismiss anytime | ✅ |
| No forced flows | ✅ |
| No repeated annoyance | ✅ |
| Remembers completed tutorials | ✅ |
| Progressive disclosure (context-aware) | ✅ |
| Persistence via localStorage | ✅ |

### Files

- `apps/web/src/contexts/TutorialContext.tsx` — Tutorial state and persistence
- `apps/web/src/components/tutorial/GuidedOverlay.tsx` — Step-by-step overlay UI
- `apps/web/src/components/tutorial/FeatureIntroCard.tsx` — Feature intro card UI
- `apps/web/src/content/tooltips.ts` — Tooltip copy
- `apps/web/src/content/tutorial-copy.ts` — Overlay and intro card copy
- `apps/web/src/components/studio/EditorToolbar.tsx` — Toolbar tooltips
- `apps/web/src/components/studio/StoryIntegrityPanel.tsx` — Integrity/Density overlays and intro cards
- `apps/web/src/components/studio/ManuscriptSidebar.tsx` — Finish Mode intro card, nav tooltips
- `apps/web/src/app/dashboard/projects/[id]/books/[bookId]/page.tsx` — AI and Integrity overlays
