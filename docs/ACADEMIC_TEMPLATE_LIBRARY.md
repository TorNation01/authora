# AUTHORA Academic Template Library

## Overview

The academic template library expands AUTHORA beyond books into academic and educational writing workflows. It preserves quality, structure, citations, and export readiness for essays, research papers, course materials, and student support documents.

## Template Categories

| Category | Slug | Description |
|----------|------|-------------|
| **Essay** | `academic-essay` | 11 essay types: standard, argumentative, persuasive, analytical, compare/contrast, reflective, expository, descriptive, critical response, case study, timed outline |
| **Research** | `academic-research` | 11 research types: research paper, literature review, annotated bibliography, thesis/dissertation, capstone, journal article, conference paper, discussion paper, methodology builder, results/discussion, reference-heavy |
| **Course/Lecture** | `academic-course` | 10 course types: lecture notes, lecture script, lesson plan, course module, seminar handout, tutorial guide, workshop outline, course workbook, reading response, class discussion guide |
| **Student Support** | `academic-student` | 6 support types: study notes, assignment planner, reading summary, source analysis, revision checklist, exam prep outline |

## Shared Features

All academic templates include:

- **Structure** – Section scaffolds with clear purposes
- **Guidance text** – Inline help for each planning section
- **AI prompt hooks** – Optional AI assist for thesis, outline, synthesis, etc.
- **Citation integration** – Vault sources, reference manager compatibility, style options (APA, MLA, Chicago, Harvard)
- **Export recommendations** – DOCX, PDF (citation-ready)
- **Academic tone guidance** – Formal, objective, precise

## Citation & Reference Integration

- **Vault sources** – Link to AUTHORA Vault for source management
- **Reference manager** – Zotero/Mendeley compatible
- **Style options** – APA, MLA, Chicago, Harvard (selected at setup)
- **References section** – Standard in essay and research templates

## Academic Tone Guidance

| Principle | Guidance |
|-----------|----------|
| **Formal** | Use formal third person unless instructed otherwise. Avoid contractions, colloquialisms. |
| **Objective** | Present evidence objectively. Acknowledge counterarguments. Distinguish fact from interpretation. |
| **Precise** | Choose precise vocabulary. Define technical terms on first use. Avoid vague qualifiers. |

## API & Seeding

- Templates are seeded via `python -m authora.scripts.seed_project_templates`
- Category filter: `GET /api/v1/templates?category=academic`
- Parent/child: Essay, Research, Course, Student Support are parents; specific types are children

## Related Documentation

- [ESSAY_TEMPLATES.md](./ESSAY_TEMPLATES.md) – Essay template details
- [RESEARCH_WRITING_TEMPLATES.md](./RESEARCH_WRITING_TEMPLATES.md) – Research template details
- [COURSE_AND_LECTURE_TEMPLATES.md](./COURSE_AND_LECTURE_TEMPLATES.md) – Course/lecture template details
