# AUTHORA Framework Engine – Implementation Summary

## Launch Priority Frameworks (First-Wave Flagship)

These 12 pairings are the strongest, most polished launch-ready experiences:

**Fiction**: Romance→Romance beats / Three-Act | Fantasy→Hero's Journey / Series Arc | Thriller/Mystery→Mystery-Thriller / Three-Act | Sci-fi→Three-Act / Hero's Journey

**Non-Fiction**: Memoir→Memoir-Driven Lesson | Self-Help→Step-by-Step | Business→Authority | Workbook→Workbook

Each has: polished planning boards (hint + prompt per stage), chapter scaffolds, scene prompts, milestone logic, revision checklist, AI assist presets, and next-step guidance. Use `GET /api/v1/frameworks?launch_priority=true` for setup flow.

---

## 1. Framework Library Summary

The framework engine includes **16 production-ready frameworks**:

### Fiction (8)
| Slug | Name | Featured |
|------|------|----------|
| three_act | Three-Act Structure | ✓ |
| hero_journey | Hero's Journey | ✓ |
| save_the_cat | Save-the-Cat Beat Structure | ✓ |
| romance_beats | Romance Beat Structure | ✓ |
| mystery_thriller | Mystery / Thriller Structure | ✓ |
| series_arc | Series Fiction Arc Structure | ✓ |
| character_driven | Character-Driven Literary Structure | |
| custom_fiction | Custom Fiction Structure | |

### Non-Fiction (8)
| Slug | Name | Featured |
|------|------|----------|
| problem_solution_result | Problem → Solution → Result | ✓ |
| step_by_step | Step-by-Step Transformation | ✓ |
| authority | Authority / Credibility Book | ✓ |
| instructional | Teaching / Educational Framework | |
| workbook | Workbook / Guided Action Framework | ✓ |
| memoir_lesson | Memoir-Driven Lesson Framework | ✓ |
| modular | Modular Topic Framework | |
| custom_nonfiction | Custom Non-Fiction Structure | |

Each framework defines: planning_stages, beat_stages, chapter_skeletons, milestone_logic, accountability_mapping, revision_checklist, ai_prompt_presets, scene_prompts, recommendation_rules.

---

## 2. Fiction Framework Summary

- **Three-Act**: Setup → Inciting → First Turn → Rising → Midpoint → Complications → Darkest → Climax → Resolution
- **Hero's Journey**: Departure (ordinary world → threshold), Initiation (tests → ordeal → reward), Return (road back → elixir)
- **Save-the-Cat**: 15 beats from Opening Image to Final Image
- **Romance**: Meet → Attraction → Resistance → Bond → Conflict → Break → Vulnerability → Reconciliation → HEA/HFN
- **Mystery/Thriller**: Crime → Stakes → Clues → Suspects → Reveals → False Solution → Twist → Confrontation → Resolution
- **Series Arc**: Book-level + series-level arcs, continuity, recurring cast
- **Character-Driven**: Emotional movement, relationships, internal conflict, theme, symbolic development
- **Custom Fiction**: Minimal scaffolding

---

## 3. Non-Fiction Framework Summary

- **Problem→Solution→Result**: Pain → Why → Root → Solution → Implementation → Result
- **Step-by-Step**: Start → End → Stages → Obstacles → Mindset → Actions
- **Authority**: Positioning → Stories → Frameworks → Insight → Proof → CTA
- **Teaching**: Objectives → Flow → Concept → Reinforcement → Examples → Recap
- **Workbook**: Teaching → Prompts → Exercises → Reflection → Action → Checkpoint
- **Memoir-Driven Lesson**: Experience → Lesson → Event → Reflection → Takeaway
- **Modular**: Topic modules, grouped themes, standalone chapters
- **Custom Non-Fiction**: Minimal scaffolding

---

## 4. Recommendation Engine Summary

- **Inputs**: book_type, genre, template_id, template_slug, is_series
- **Scoring**: Genre match vs ideal_genres, template slug hints, series boost, featured boost
- **Template mapping**: romance→romance_beats, thriller→mystery_thriller, fantasy→hero_journey, memoir→memoir_lesson, workbook→workbook, business→authority, selfhelp→step_by_step
- **Template structure_framework mapping**: emotional_arc→memoir_lesson, module_exercise→workbook, prompt_based→workbook, etc.

---

## 5. Framework-Aware Editor / Accountability Summary

### Implemented
- **Project wizard**: Resolves framework from template or framework_id; creates book with framework_id; uses framework chapter_skeletons when template has none
- **Book response**: Includes framework_id
- **Book update**: Supports framework_id (for switching/remapping)
- **Planner data**: Stores framework_slug, framework_name

### Planned (documented in FRAMEWORK_EDITOR_INTEGRATION.md)
- Editor sidebar: current act/beat/phase
- AI scene prompts: next scene/chapter prompt from framework stage
- Beat completion warnings
- "Help me continue" with framework context
- Framework-specific rewrite prompts
- "Am I on track?" review against structure
- Accountability mapping: Finish Mode / milestones tied to framework stages

---

## 6. Production Readiness

- **Database**: Migration 024 applied; writing_frameworks table; books.framework_id FK
- **Models**: WritingFramework, Book.framework relationship
- **Seed**: 16 frameworks seeded from framework_definitions.py
- **API**: GET /frameworks, GET /frameworks/recommend, GET /frameworks/{id_or_slug}
- **Admin**: List, update, duplicate, reorder, usage analytics
- **Project wizard**: Resolves framework, creates book with framework_id, uses chapter_skeletons
- **Documentation**: FRAMEWORK_ENGINE.md, FICTION_FRAMEWORKS.md, NONFICTION_FRAMEWORKS.md, FRAMEWORK_RECOMMENDATION_RULES.md, FRAMEWORK_EDITOR_INTEGRATION.md, ADMIN_FRAMEWORK_MANAGEMENT.md

The framework engine is **production-ready** and deployable. The planning boards, editor sidebar, and accountability UI can consume framework metadata via the API and planner_data for full framework-aware experience.
