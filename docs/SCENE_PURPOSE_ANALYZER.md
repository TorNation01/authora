# Scene Purpose Analyzer

The Scene Purpose Analyzer is a subsystem of the Story Density Engine that helps writers understand whether scenes, chapters, and sections are earning their space in the manuscript.

## Purpose Jobs

For each scene/section/chapter, the analyzer estimates whether it is primarily doing one or more of these jobs:

| Job | Description |
|-----|-------------|
| move_plot | Advances the plot or narrative |
| deepen_character | Develops character through reflection, realization, or internal state |
| escalate_tension | Raises stakes, conflict, or tension |
| deliver_payoff | Delivers on earlier setup or promise |
| build_setup | Introduces elements for later payoff |
| deliver_reflection | Provides reflective or retrospective content |
| explain_concept | Explains an idea (non-fiction) |
| provide_example | Gives a concrete example |
| create_transition | Bridges between larger movements |
| provide_exercise | Offers exercise or action step (workbook) |
| reinforce_theme | Reinforces thematic elements |
| unclear | Purpose not clearly detectable |

## Analysis Levels

### Chapter Purpose

- **Primary jobs** — Top 1–3 jobs inferred from text markers
- **Purpose clarity** — 0–1 score for how clear the chapter's purpose is
- **Contributions** — Plot, character, emotional, thematic, instructional, practical (project-type dependent)
- **Flags** — unclear_purpose, does_too_little_for_size, likely_needs_compression

### Section/Scene Purpose

- **Sections** — Chunks of ~400 words extracted from TipTap content
- **Primary jobs** — Inferred per section
- **Flags** — unclear_purpose, repeats_job_from_earlier_section, does_too_little_for_size, likely_needs_compression, likely_needs_strengthening
- **Suggestion** — Actionable suggestion per section

## Detection Logic

- **Marker-based** — Each job has a set of text markers (e.g. "then", "next" for move_plot; "felt", "realized" for deepen_character)
- **Project-type aware** — Instructional and practical contributions only for nonfiction/workbook/hybrid
- **Position aware** — Opening, midpoint, ending chapters get different treatment

## API

- Scene purpose data is included in `density_map_snapshot` after a scan
- `GET /density/analysis` returns `scene_purpose_analysis` with `chapter_purposes` and `scene_purposes`
- `GET /density/chapters/{id}/summary` returns `what_this_chapter_is_doing` for the active chapter

## UI

- **Scene Purpose Board** — Tab in Story Density panel showing chapter purposes, primary jobs, purpose clarity, and flags
- **"What this chapter is doing"** — Summary shown when a chapter is selected
