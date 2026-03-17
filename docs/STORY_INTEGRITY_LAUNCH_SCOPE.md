# Story Integrity Engine — Launch-Priority Implementation Scope

This document defines the launch-ready scope for the AUTHORA Story Integrity Engine. Features are prioritized for polish and visible value before expanding into experimental or advanced analysis.

## Launch-Ready Criteria

For each feature to be considered **launch-ready**:

- **Implemented** — Detection logic exists and runs during scan
- **Polished** — Clear, supportive language; no noisy false positives
- **Visible** — Surfaces in Story Health panel with actionable UI
- **Documented** — Fix templates and guidance for each issue type
- **Mode-aware** — Respects guidance_mode (guided/flexible/freeform)
- **Tested** — Unit tests for detector logic

---

## Priority 1: Unresolved Thread Detection

**Goal:** Flag plot/theme threads that are introduced but never resolved by the end.

**Current state:**
- Story map has `threads` (character + theme), `promises`, `setup_candidates`
- FictionDetector has `too_many_threads` (many open) but not "thread introduced, never resolved"

**Gaps:**
- No detector for: thread appears in act 1–2, absent in final third
- No explicit "unresolved_thread" issue type
- `promises` extracted but never checked for payoff

**Launch-ready implementation:**

| Task | Description |
|------|-------------|
| 1.1 | Add `unresolved_thread` detector: thread in first 2/3 of manuscript, no appearance in last 1/3 |
| 1.2 | Use `setup_candidates` + `promises`: if setup in early chapter, check for payoff in later chapters |
| 1.3 | Issue type: `unresolved_thread`, category: `setup_payoff`, severity: moderate |
| 1.4 | Fix template: "Consider resolving this thread or marking as intentional (series/open ending)" |
| 1.5 | Mode: guided only; flexible/freeform suppress |
| 1.6 | Add to ISSUE_DETECTION_CATALOG.md |

**Out of scope for launch:** AI-based thread inference; cross-book series tracking.

---

## Priority 2: Setup/Payoff Detection

**Goal:** Flag setups (introduced elements) that lack payoff, and payoffs without setup.

**Current state:**
- Story map extracts `setup_candidates` (introduced, first time, discovered) and `promises` (will, going to, promise)
- No detector consumes these for setup/payoff

**Gaps:**
- No correlation between setup chapter and payoff chapter
- No "promise made but not fulfilled" detection

**Launch-ready implementation:**

| Task | Description |
|------|-------------|
| 2.1 | Add `setup_without_payoff` detector: setup_candidate in first 2/3, no related content in last 1/3 |
| 2.2 | Add `promise_unfulfilled` detector: promise in early chapter, no fulfillment markers in later chapters |
| 2.3 | Fulfillment markers: "finally", "at last", "realized", "discovered", "learned", "found" |
| 2.4 | Issue types: `setup_without_payoff`, `promise_unfulfilled`; category: `setup_payoff` |
| 2.5 | Fix templates with "mark as intentional" for deliberate open threads |
| 2.6 | Mode: guided for fiction; flexible softer |

**Out of scope for launch:** Semantic matching; NLP-based setup/payoff inference.

---

## Priority 3: Character Arc Incomplete Detection

**Goal:** Flag main characters whose arc appears incomplete (e.g., introduced then dropped, or no change across manuscript).

**Current state:**
- `character_appearances` maps character_id → list of chapter indices
- `character_single_appearance` exists (appears once)
- `character_changes` exists in story map but is never populated

**Gaps:**
- No "arc incomplete" (protagonist in act 1 + 3, absent in act 2)
- No "no visible change" (character appears throughout but no change markers)
- No protagonist vs minor character distinction

**Launch-ready implementation:**

| Task | Description |
|------|-------------|
| 3.1 | Populate `character_changes` from emotional/realization markers when character is present |
| 3.2 | Add `character_arc_gap`: protagonist (from planner or first 3 chapters) has large gap in appearances (e.g., missing from middle 40%) |
| 3.3 | Add `character_arc_flat`: character in 4+ chapters, no change markers in any |
| 3.4 | Use vault character role (protagonist, antagonist) if available |
| 3.5 | Issue types: `character_arc_gap`, `character_arc_flat`; category: `character` |
| 3.6 | Mode: guided for fiction; flexible suppresses arc_flat |

**Out of scope for launch:** Full arc shape analysis; AI character arc scoring.

---

## Priority 4: Chapter Health Analysis

**Goal:** Per-chapter health, pacing, structure with "what this chapter is doing" and "why it feels off."

**Current state:** ✅ **Implemented**
- `chapter_analyzer.analyze_chapters()` — purpose, pacing, tension, emotion, transitions, etc.
- Chapter health API, ChapterHealthPanel with list + comparison view
- Mode-aware (freeform minimal, flexible softer)

**Launch-ready polish:**

| Task | Description |
|------|-------------|
| 4.1 | Add pacing heatmap placeholder or simple bar visualization |
| 4.2 | Ensure all chapter-level issue types have fix templates |
| 4.3 | Add "Go to chapter" from chapter health card to editor |
| 4.4 | Verify empty-state copy when no scan has run |

**Status:** Launch-ready with minor polish.

---

## Priority 5: Timeline Inconsistency Detection

**Goal:** Flag timeline events that appear out of order or contradict vault timeline.

**Current state:**
- Story map has `timeline_events` (vault events mentioned per chapter)
- Vault has timeline events with optional dates/order
- No ordering or consistency check

**Gaps:**
- No detection of "Event A after Event B in text, but vault says A before B"
- No "event mentioned in wrong chapter for chronological flow"

**Launch-ready implementation:**

| Task | Description |
|------|-------------|
| 5.1 | If vault_events have `sort_order` or `date`, build expected order |
| 5.2 | Add `timeline_out_of_order`: event appears in chapter N, but earlier event appears in chapter N+1 |
| 5.3 | Add `timeline_event_missing`: vault event not mentioned in any chapter (low severity, informational) |
| 5.4 | Issue types: `timeline_out_of_order`, `timeline_event_missing`; category: `continuity` |
| 5.5 | Mode: guided when vault has timeline; flexible/freeform suppress |
| 5.6 | Graceful no-op when vault has no timeline or no order |

**Out of scope for launch:** Date parsing from prose; complex temporal logic.

---

## Priority 6: Weak Midpoint / Weak Transition (Guided Fiction)

**Goal:** For guided fiction, flag weak midpoint (middle of manuscript) and weak transitions between chapters.

**Current state:**
- `missing_transition` exists for nonfiction (transition words)
- No midpoint detection
- Chapter analyzer has `transition_quality` and `chapter_disconnected_from_main_thread`

**Gaps:**
- No explicit "weak midpoint" for fiction (middle 10–20% of manuscript)
- Fiction transition detection is in chapter analyzer, not FictionDetector

**Launch-ready implementation:**

| Task | Description |
|------|-------------|
| 6.1 | Add `weak_midpoint` detector: chapters in middle 15–35% of manuscript are short (< 200 words) or have low tension/plot markers |
| 6.2 | Add `weak_transition` to FictionDetector: adjacent chapters with no overlap in key terms, no transition markers |
| 6.3 | Issue types: `weak_midpoint`, `weak_transition`; category: `structure` |
| 6.4 | Mode: **guided only**; flexible/freeform suppress |
| 6.5 | Fix templates: "Strengthen midpoint beat" / "Add bridge between chapters" |

**Out of scope for launch:** Beat sheet alignment; framework-specific midpoint rules.

---

## Priority 7: Non-Fiction Chapter Flow / Promise Fulfillment

**Goal:** Flag nonfiction chapters that break flow or make promises not fulfilled.

**Current state:**
- `missing_transition` exists
- `promises` extracted in story map
- No promise-fulfillment check for nonfiction

**Gaps:**
- No "chapter promises X, later chapters don't deliver"
- No "chapter flow" (e.g., introduction before body, conclusion at end)

**Launch-ready implementation:**

| Task | Description |
|------|-------------|
| 7.1 | Add `promise_unfulfilled` to NonfictionDetector: promise in early chapter, no fulfillment in later |
| 7.2 | Add `chapter_flow_issue`: first chapter doesn't introduce, last doesn't conclude (using purpose_hint) |
| 7.3 | Issue types: `nf_promise_unfulfilled`, `nf_chapter_flow`; category: `promise_fulfillment` / `clarity` |
| 7.4 | Mode: guided; flexible suppresses flow checks |
| 7.5 | Fix templates for nonfiction-specific language |

**Out of scope for launch:** Argument structure analysis; citation consistency.

---

## Priority 8: Memoir Emotional Arc / Reflection Gap

**Goal:** Flag memoir chapters with weak emotional progression or reflection gaps.

**Current state:**
- `reflection_missing` exists (long chapter without reflection markers)
- `emotional_markers` extracted per chapter
- MemoirDetector is mode-aware

**Gaps:**
- No "emotional arc flat" (no emotional progression across manuscript)
- No "reflection gap" (long stretch of chapters without reflection)

**Launch-ready polish:**

| Task | Description |
|------|-------------|
| 8.1 | Add `emotional_arc_flat`: 5+ chapters, no emotional markers in last third |
| 8.2 | Add `reflection_gap`: 3+ consecutive chapters > 300 words with no reflection |
| 8.3 | Expand reflection markers: "i realized", "looking back", "it meant", "i see now" |
| 8.4 | Issue types: `emotional_arc_flat`, `reflection_gap`; category: `emotional_arc` |
| 8.5 | Mode: guided; flexible suppresses arc_flat |

**Status:** Memoir detector exists; extend with arc + gap detection.

---

## Priority 9: Guided Fix Suggestions

**Goal:** Every issue has clear explanation, why it matters, and actionable suggestions.

**Current state:** ✅ **Implemented**
- `fix_assistant.get_fix_guidance()` with FIX_TEMPLATES
- API: `GET /integrity/issues/{id}/guidance`
- Fix suggestions stored per issue

**Launch-ready polish:**

| Task | Description |
|------|-------------|
| 9.1 | Add fix templates for all new issue types (unresolved_thread, setup_without_payoff, character_arc_gap, etc.) |
| 9.2 | Surface guidance in Story Health panel: expand issue to show explanation + suggestions |
| 9.3 | Add "Get guidance" or inline expansion for each issue card |
| 9.4 | Ensure "mark as intentional" is present for all speculative issues |

**Status:** Backend done; UI could surface guidance more prominently.

---

## Priority 10: Story Health Dashboard

**Goal:** Single place to see manuscript health, run scans, view and act on issues.

**Current state:** ✅ **Implemented**
- StoryIntegrityPanel with Issues + Chapter Health tabs
- Health summary, scan button, issue list, resolve/mark intentional
- Chapter health panel with comparison view

**Launch-ready polish:**

| Task | Description |
|------|-------------|
| 10.1 | Add health score/meter (0–100) derived from issue count and severity |
| 10.2 | Add category filter for issues (structure, character, setup_payoff, etc.) |
| 10.3 | Add "Scan in progress" state with progress indicator |
| 10.4 | Add empty state when no scan run: "Run your first scan to see story health" |
| 10.5 | Ensure panel is discoverable (toolbar button, optional onboarding hint) |
| 10.6 | Add last-scan summary: "X issues found, Y resolved" |

**Status:** Core done; polish for visibility and clarity.

---

## Implementation Order

| Phase | Features | Rationale |
|-------|----------|-----------|
| **Phase 1** | 4, 9, 10 | Already built; polish for launch |
| **Phase 2** | 1, 2, 3 | High-value fiction detection |
| **Phase 3** | 5, 6 | Timeline + midpoint (guided fiction) |
| **Phase 4** | 7, 8 | Nonfiction + memoir completion |

---

## Excluded from Launch Scope

- **Experimental:** AI-powered analysis, semantic similarity, LLM-based issue detection
- **Advanced:** Beat sheet alignment, framework-specific rules (Save the Cat, etc.)
- **Cross-project:** Series-level thread tracking, multi-book continuity
- **Export-specific:** Pre-export integrity gate (can be post-launch)
- **Real-time:** Live analysis while typing (performance)

---

## Success Metrics for Launch

- All 10 priority features implemented or polished
- Zero critical bugs in scan pipeline
- Story Health panel loads in < 2s
- Fix guidance available for every issue type
- Mode-aware behavior verified (guided/flexible/freeform)
- Documentation updated (ISSUE_DETECTION_CATALOG, STORY_INTEGRITY_ENGINE)
