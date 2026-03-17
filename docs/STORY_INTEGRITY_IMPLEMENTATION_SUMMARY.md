# Story Integrity Engine — Implementation Summary

## 1. Architecture Summary

The Story Integrity Engine (SIE) is a modular manuscript analysis system integrated into AUTHORA:

| Component | Location | Purpose |
|-----------|----------|---------|
| **Scanner** | `authora/services/integrity/scanner.py` | Orchestrates scans, builds story map, runs detectors |
| **Story map** | `authora/services/integrity/story_map.py` | Threads, character appearances, themes, pacing, promises, setup candidates |
| **Detectors** | `authora/services/integrity/detectors/` | General, fiction, nonfiction, memoir, workbook |
| **Fix assistant** | `authora/services/integrity/fix_assistant.py` | Guided fix suggestions per issue type |
| **Models** | `authora/models/integrity.py` | IntegrityScan, IntegrityIssue, IntegrityScanAnalytics |
| **API** | `authora/api/routes/integrity.py` | Scan, list issues, health, update status, guidance |
| **UI** | `components/studio/StoryIntegrityPanel.tsx` | Story Health panel in writing studio |
| **Admin** | `authora/api/routes/admin.py` | `GET /admin/integrity/analytics` |

## 2. Issue Detection by Project Type

| Project type | Detectors | Example issues |
|--------------|-----------|----------------|
| **General** | GeneralDetector | empty_section, placeholder_heavy, unresolved_placeholder |
| **Fiction** | General + FictionDetector | weak_opening, weak_ending, character_single_appearance, too_many_threads, pacing_trough, theme_introduced_not_developed |
| **Non-fiction** | General + NonfictionDetector | weak_chapter_length, missing_transition |
| **Memoir** | General + MemoirDetector | reflection_missing |
| **Workbook** | General + WorkbookDetector | exercise_missing |
| **Hybrid** | General + Nonfiction + Memoir | Combined |

## 3. Guided Fix Assistant Summary

- Each issue has fix templates with explanation, why it matters, and suggestions
- API: `GET /integrity/issues/{id}/guidance`
- User actions: Resolve, Mark intentional, Go to chapter

## 4. Editor/Dashboard Integration

- **Story Health** button in EditorToolbar (Activity icon)
- **StoryIntegrityPanel** shows:
  - Health summary (open issues, last scan)
  - Scan button
  - List of open issues with Resolve / Intentional actions
  - "Go to chapter" for chapter-specific issues

## 5. Guided / Flexible / Freeform Behaviour

- **Guided**: Full detector set, framework-aware (future: framework beat detection)
- **Flexible**: Same detectors, softer severity for missing framework elements
- **Freeform**: General + light continuity; no rigid structure enforcement

## 6. Production Readiness

- ✅ Database migration (033)
- ✅ Models with relationships
- ✅ API routes with auth and feature-flag check
- ✅ Frontend panel integrated (hidden when feature disabled)
- ✅ Admin analytics: `GET /admin/integrity/analytics`
- ✅ Feature flag: `feature_story_integrity` (config + DB override)
- ✅ Documentation: STORY_INTEGRITY_ENGINE.md, ISSUE_DETECTION_CATALOG.md, GUIDED_FIX_ASSISTANT.md, STORY_HEALTH_SYSTEM.md, INTEGRITY_SCANNING_PIPELINE.md, MODE_AWARE_INTEGRITY.md, STORY_HEALTH_DASHBOARD.md
- ✅ No user content deletion or silent rewriting
- ✅ Supportive, non-judgmental UX

## Extending the Engine

- Add detectors in `authora/services/integrity/detectors/`
- Register in `get_detectors_for_project()` in `detectors/__init__.py`
- Add fix templates in `fix_assistant.py` FIX_TEMPLATES
- AI-assisted explanations: call AI from `get_fix_guidance()` when configured
