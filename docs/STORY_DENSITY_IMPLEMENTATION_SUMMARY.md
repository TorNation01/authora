# Story Density Engine — Implementation Summary

## 1. Architecture Summary

The Story Density Engine (SDE) is a modular manuscript analysis layer that:

- **Scanner** (`scanner.py`) — Loads project/book/chapters, builds story map and density map, runs detectors, persists `DensityScan` and `DensityIssue`
- **Density map** (`density_map.py`) — Computes per-chapter info/emotional/tension density, repeated concepts, thin transitions, manuscript score
- **Detectors** (`detectors/`) — Project-type and guidance-mode aware; General, Fiction, Nonfiction, Memoir, Workbook
- **Fix assistant** (`fix_assistant.py`) — Returns explanation, why_it_matters, suggestions, fix_suggestions per issue type

## 2. Clutter/Filler Detection by Project Type

| Project Type | Detectors | Key Issues |
|--------------|-----------|------------|
| General | GeneralDensityDetector | repetition_in_chapter, thin_section, possible_bloat, thin_transition, repeated_concepts |
| Fiction | + FictionDensityDetector | weak_midpoint, exposition_overload, repeated_emotional_beat |
| Nonfiction | + NonfictionDensityDetector | missing_example, bloated_intro_or_outro |
| Memoir | + MemoirDensityDetector | repeated_reflection, emotional_over_explanation |
| Workbook | + WorkbookDensityDetector | excessive_explanation, missing_exercise |
| Hybrid | Nonfiction + Memoir | Mixed-weight analysis |
| Freeform | General only | No formula enforcement |

## 3. Weak-Support Detection Summary

- **thin_section** — Very short chapter (expand or merge)
- **thin_transition** — Weak bridge from previous (add bridge)
- **missing_example** — Concept without example (non-fiction)
- **missing_exercise** — Concept without exercise (workbook)

## 4. Trim/Compress/Strengthen Assistant Summary

- `get_density_fix_guidance(issue_type, issue)` returns explanation, why_it_matters, suggestions, fix_suggestions
- API: `GET /density/issues/{id}/guidance`
- User actions: Resolve, Mark intentional, Ignore
- No auto-delete or auto-rewrite

## 5. Editor/Revision Integration Summary

- **Story Health panel** — New "Density" tab (when `feature_story_density` enabled)
- **StoryDensityPanel** — Manuscript score, issue list, Resolve/Intentional, Scan button
- **Chapter navigation** — "Go to chapter" links to affected chapter
- Feature flag: `story_density` in config

## 6. Guided/Flexible/Freeform Behaviour Summary

- **Guided** — Stronger checks, framework-aware
- **Flexible** — Softer assumptions, cross-genre tolerance
- **Freeform** — GeneralDensityDetector only; no structural policing

## 7. Production Readiness

- [x] Density scanner and orchestrator
- [x] Project-type adapters (detectors)
- [x] Density map construction
- [x] Clutter/filler/repetition detectors
- [x] Weak-support detection
- [x] Trim/compress/strengthen assistant
- [x] API routes (scan, issues, health, guidance)
- [x] Editor integration (Density tab in Story Health)
- [x] Admin analytics (`GET /admin/density/analytics`)
- [x] Feature flag and config
- [x] Documentation (7 docs)
- [x] Migration (034_add_story_density_engine)

**Run migration:** `alembic upgrade head` (requires DB connection)
