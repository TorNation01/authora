# Story Density Engine — Launch-Priority Implementation Scope

This document defines the launch-ready scope for the AUTHORA Story Density Engine. Features are prioritized for polish and visible value before expanding into experimental analysis.

## Launch Principles

- **Launch-ready**: Feature works reliably, has clear UX, and delivers obvious value
- **Polished**: Copy is supportive, non-judgmental; UI is consistent with AUTHORA design
- **Visibly valuable**: Writers can see what’s wrong, why it matters, and what to do next

---

## Priority 1: Chapter Drag Detection

**Current state**: Implemented. `chapter_drag_analyzer.py` computes per-chapter drag scores, finds drag runs (consecutive dragging chapters), merge candidates, and compression candidates. Mode-aware thresholds (memoir, literary fiction). `ChapterDragPanel` shows drag runs, merge candidates, and per-chapter status.

**Launch-ready definition**:
- Drag score and “is_dragging” are accurate and mode-aware
- Drag runs and merge candidates surface in the UI with clear, actionable copy
- Writers can navigate to affected chapters and understand what “dragging” means

**Gaps**:
- [ ] Verify drag score formula against real manuscripts; tune if needed
- [ ] Add “Likely compressible” / “Strongly weighted” labels (done in density-copy)
- [ ] Empty state: “Run a Density Check to see chapter drag analysis”

**Work items**:
1. Smoke-test drag detection on sample fiction/memoir manuscripts
2. Ensure chapter summary (when chapter selected) shows drag hint when relevant
3. Document drag thresholds in STORY_DENSITY_HARDENING.md (done)

---

## Priority 2: Repeated Beat / Repeated Argument Detection

**Current state**:
- **Repeated beats** (fiction/memoir): `repeated_beats` from story_map emotional_markers; FictionDensityDetector and MemoirDensityDetector flag `repeated_emotional_beat`, `repeated_reflection`
- **Repeated concepts** (general): `repeated_concepts` from phrase overlap across chapters; GeneralDensityDetector flags `repeated_concepts`
- **Repeated argument** (nonfiction): `instructional_redundancy` category exists; no dedicated detector yet. NonfictionDensityDetector focuses on missing_example, bloated_intro_or_outro

**Launch-ready definition**:
- Fiction/memoir: Repeated emotional beats and reflections are detected and surfaced
- Nonfiction: Repeated arguments (same point restated across chapters) are detected
- All: Issues link to chapters, show “Mark as intentional” for deliberate refrains

**Gaps**:
- [ ] Nonfiction “repeated argument” detector: detect when the same claim/argument appears in multiple chapters with little new development
- [ ] Repeated concepts: ensure phrase extraction is robust (3-word phrases, 2+ chapters)
- [ ] Emotional markers: story_map must provide `emotional_markers`; verify pipeline

**Work items**:
1. Add NonfictionDensityDetector logic for `repeated_argument` / `instructional_redundancy` using repeated_concepts + concept-marker heuristics
2. Verify story_map includes emotional_markers for fiction/memoir
3. Add “repeated_argument” to fix_assistant and trim_vs_strengthen templates
4. Ensure RepetitionHeatPanel and Issues tab both surface repetition clearly

---

## Priority 3: Scene/Chapter Purpose Clarity Detection

**Current state**: `scene_purpose_analyzer.py` infers section jobs (move_plot, deepen_character, reinforce_theme, etc.), purpose_clarity score, and flags (unclear_purpose, does_too_little_for_size, likely_needs_compression). `ScenePurposeBoard` shows chapter purposes, primary jobs, purpose clarity %.

**Launch-ready definition**:
- Each chapter has a purpose clarity score (0–100%) and primary jobs
- Unclear or underperforming chapters are flagged
- Writers see “What this chapter is doing” and “Purpose clarity” in the UI

**Gaps**:
- [ ] Purpose clarity formula: ensure it’s meaningful across project types
- [ ] Flags like “does_too_little_for_size” should create DensityIssues when severe
- [ ] Scene-level purpose (within chapter) is computed but not prominently surfaced

**Work items**:
1. Add detector that creates DensityIssues for `unclear_purpose` when purpose_clarity < 0.4 and word_count > 300
2. Ensure ScenePurposeBoard empty state and copy are polished (density-copy)
3. Consider surfacing “Scene may lack clear purpose” as an issue type in the Issues tab

---

## Priority 4: Filler Risk Detection

**Current state**: GeneralDensityDetector flags `possible_bloat` (long + low info density). FictionDensityDetector flags `exposition_overload` (long + low tension/movement). Category “filler” exists in constants but no dedicated `filler` issue type. Bloated intro/outro, excessive_explanation (workbook) are related.

**Launch-ready definition**:
- Sections that are likely filler (redundant, low-value, padding) are detected
- Issue labels use “Filler risk” or “Likely compressible” (not “bloated”)
- Writers get trim/compress suggestions with “Mark as intentional” option

**Gaps**:
- [ ] Unify filler-related issues under a clear “Filler risk” label in the UI
- [ ] possible_bloat, exposition_overload, excessive_explanation, bloated_intro_or_outro should all map to user-facing “Filler risk” or “Likely compressible”
- [ ] Ensure filler detection respects artistic-freedom safeguards (intentional style gate)

**Work items**:
1. Add DENSITY_ISSUE_LABELS mapping for filler-like types to “Filler risk” / “Likely compressible”
2. Verify filler detectors use hardening thresholds (BLOAT_WORDS_FLEXIBLE, EXPOSITION_WORDS_MIN, intentional style)
3. Add “Filler risk” as a filter or badge in the Issues tab if useful

---

## Priority 5: Thin-Support Detection

**Current state**: GeneralDensityDetector flags `thin_section` (very short middle chapter). `thin_transition` is separate (Priority 6). NonfictionDensityDetector flags `missing_example`. WorkbookDensityDetector flags `missing_exercise`. Category `thin_support` exists.

**Launch-ready definition**:
- Thin sections (expand or merge), missing examples, missing exercises are detected
- Issues suggest “Strengthen options” or “Add content”
- Mode-aware: flexible tolerates brief bridges, reflection pages

**Gaps**:
- [ ] Thin section threshold: 80 (guided) / 120 (flexible) — verify
- [ ] missing_example, missing_exercise: ensure contemplative/reflection-page skips work
- [ ] “Needs strengthening” / “Thin support” labels in UI (done in density-copy)

**Work items**:
1. Smoke-test thin_section, missing_example, missing_exercise on sample manuscripts
2. Ensure trim engine recommends “strengthen” or “expand” for thin_support
3. Polish empty states for Purpose/Drag/Repetition tabs

---

## Priority 6: Transition Weakness Detection

**Current state**: `_find_thin_transitions` in density_map flags chapters with weak linkage to the previous (no transition markers, low word overlap). GeneralDensityDetector creates `thin_transition` issues. Fix assistant and trim engine suggest “bridge”.

**Launch-ready definition**:
- Chapters that open abruptly or lack clear connection to the previous are flagged
- Issue suggests “Add a bridging paragraph” or “Transition feels thin”
- “Mark as intentional” for deliberate jumps (e.g. time skip)

**Gaps**:
- [ ] Transition detection is heuristic (markers + overlap); may have false positives/negatives
- [ ] Ensure “Transition feels thin” copy is used (done in density-copy)
- [ ] Consider project-type tolerance (literary fiction may use abrupt cuts intentionally)

**Work items**:
1. Add optional project-type tolerance for thin_transition in flexible mode
2. Verify thin_transition issues link correctly to the chapter they affect (the one that “opens” weak)
3. Ensure fix_assistant and trim engine “bridge” suggestion is clear

---

## Priority 7: Trim vs Strengthen Recommendation Logic

**Current state**: `trim_vs_strengthen_engine.py` decides recommended action (trim, compress, strengthen, bridge, merge, keep_as_intentional) from issue type, context, purpose_clarity, emotional_density, is_dragging. `fix_assistant.py` provides templates. API: `GET /density/issues/{id}/guidance`, `GET /density/issues/{id}/decision`, `GET /density/issues/{id}/alternatives`, `POST /density/issues/{id}/create-revision-task`.

**Launch-ready definition**:
- Each issue gets a clear recommended action and explanation
- Alternatives (including “Mark as intentional”) are surfaced
- Writers can create a revision task from an issue
- Logic respects artistic-freedom safeguards (emotional_density, intentional jobs)

**Gaps**:
- [ ] UI does not yet show “Trim options” / “Strengthen options” / decision explanation prominently
- [ ] Create-revision-task flow: verify it creates a useful task with issue context
- [ ] Guidance API may not be called from the panel; add “Get guidance” or inline expansion

**Work items**:
1. Add “View guidance” or expandable guidance section per issue in StoryDensityPanel
2. Wire “Create revision task” button to API and show success state
3. Ensure decision/alternatives are available when user clicks an issue
4. Document trim-vs-strengthen rules in TRIM_VS_STRENGTHEN_ENGINE.md (exists)

---

## Priority 8: Density Dashboard

**Current state**: StoryDensityPanel has Issues, Purpose, Drag, Repetition tabs. Manuscript density score, issue count, summary labels (Tight and strong, A few sections may need trimming, etc.). Scan button, Resolve, Mark as intentional. Integrated into StoryIntegrityPanel (Story Health sidebar).

**Launch-ready definition**:
- Dashboard is the primary entry point for density insights
- Manuscript score and summary label are visible at a glance
- Issue list is scannable, filterable, and actionable
- Tabs (Issues, Purpose, Drag, Repetition) are clearly differentiated

**Gaps**:
- [ ] Filter by issue type/category in the Issues tab (e.g. “Filler risk only”)
- [ ] Sort issues (by chapter, by severity, by action)
- [ ] “Last scan” timestamp and “Scan” CTA are clear
- [ ] Feature flag `story_density` must be wired (config.feature_flags?.story_density)

**Work items**:
1. Add optional filters: category, action_category, chapter
2. Add sort: by chapter order, by severity, by date
3. Ensure feature flag is respected and panel hides when disabled
4. Polish loading and empty states for all tabs

---

## Priority 9: Editor-Side Density Panel

**Current state**: StoryDensityPanel is rendered inside StoryIntegrityPanel. StoryIntegrityPanel is shown when user opens “Story Health” (integrity) from the manuscript workspace. The panel is a sidebar tab (Issues | Chapter Health | Density). It receives projectId, bookId, activeChapterId, onSelectChapter.

**Launch-ready definition**:
- Density panel is accessible from the manuscript workspace without leaving the page
- Selecting a chapter in the outline or in the panel syncs focus (panel highlights chapter, “Go to chapter” works)
- Panel is visible when Story Health is open and density is enabled

**Gaps**:
- [ ] Verify panel is reachable from the main book studio (toolbar or sidebar)
- [ ] activeChapterId and onSelectChapter must be wired so “Go to chapter” and chapter highlighting work
- [ ] Panel width/layout: ensure it doesn’t crowd the editor on smaller screens

**Work items**:
1. Verify StoryIntegrityPanel is opened from EditorToolbar or ManuscriptSidebar
2. Ensure density tab receives activeChapterId and onSelectChapter from parent
3. Test chapter selection sync (click issue → jump to chapter; select chapter → highlight in panel)
4. Responsive: consider collapsible or slide-over on narrow viewports

---

## Priority 10: Revision-Mode Density Queue

**Current state**: Not implemented. REVISION_MODE.md describes revision passes and comments. RevisionPanel shows chapters with unresolved comments. DENSITY_DASHBOARD.md notes “Density issues can be reviewed during revision (future: revision queue integration)”.

**Launch-ready definition**:
- In Revision Mode, density issues appear as a queue or filter alongside comments
- Writers can work through “Density pass” by addressing issues chapter by chapter
- Issues can be filtered by revision pass or shown as a dedicated “Density” queue

**Gaps**:
- [ ] No API or UI for “density queue” in revision context
- [ ] Revision passes are comment-based; density issues are in a separate table
- [ ] Need a clear UX: “Density issues” tab in Revision panel, or “Density pass” as a pass type

**Work items**:
1. Design: Add “Density” or “Density issues” section to RevisionPanel
2. API: `GET /projects/{id}/books/{id}/density/issues?status=open` (exists); optionally filter by chapter for “current chapter density issues”
3. UI: List open density issues grouped by chapter, with “Go to chapter” and “Resolve” / “Mark intentional”
4. Optional: Add “Density” as a revision pass type that surfaces density issues for that pass
5. Consider: “Density cleanup” as a pre-export checklist item

---

## Implementation Order

| Phase | Features | Goal |
|-------|----------|------|
| **Phase 1: Core detection** | 1–6 (drag, repetition, purpose, filler, thin-support, transition) | All detection paths are launch-ready and hardened |
| **Phase 2: Recommendations** | 7 (trim vs strengthen) | Guidance and revision-task creation are visible and useful |
| **Phase 3: Dashboard & panel** | 8–9 (dashboard, editor panel) | Writers can access and act on density insights from the manuscript |
| **Phase 4: Revision integration** | 10 (revision queue) | Density issues are part of the revision workflow |

---

## Out of Scope for Launch

Defer until after launch:

- Pre-export density cleanup wizard
- AI-assisted trim/compress/strengthen (auto-rewrite)
- Cross-book density comparison
- Genre-specific density presets
- Advanced NLP for filler (beyond heuristics)
- Density trends over time (historical scans)

---

## Success Criteria

Launch is ready when:

1. Writers can run a Density Check and see clear, actionable issues
2. Each issue type (drag, repetition, purpose, filler, thin-support, transition) is detectable and surfaced
3. Trim vs strengthen recommendations are visible and useful
4. Dashboard and editor panel are polished and accessible
5. Revision-mode density queue allows working through issues in revision flow
6. Artistic-freedom safeguards reduce false positives for literary, reflective, and intentional prose
