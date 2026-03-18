# Citation System

AUTHORA integrates a real CSL-based citation system for academic and professional writing.

## Overview

- **CSL (Citation Style Language)** — Industry-standard format for citation styles
- **citeproc-py** — Python processor for citations and bibliographies
- **Multiple styles** — APA, MLA, Chicago, Harvard, IEEE, MHRA, and more

## Architecture

### Components

| Component | Purpose |
|----------|---------|
| `CitationStyle` | CSL style (slug, title, csl_xml) |
| `ProjectCitationStyle` | Project or book-level style preference |
| `csl_service` | `render_citation()`, `render_bibliography()` |

### API Endpoints

- `GET /api/v1/projects/{id}/references/styles` — List available styles
- `GET /api/v1/projects/{id}/references/styles/project` — Get project/book style
- `PUT /api/v1/projects/{id}/references/styles/project` — Set style
- `POST /api/v1/projects/{id}/references/citation-preview` — Preview in-text citation
- `POST /api/v1/projects/{id}/references/bibliography` — Generate bibliography

## Supported Styles

Built-in styles (via citeproc-py-styles or bundled):

- `apa` — APA 7th edition
- `mla` — MLA 9th edition
- `chicago-author-date` — Chicago author-date
- `harvard1` — Harvard
- `ieee` — IEEE
- `mhra` — MHRA

Custom styles can be added to the `citation_styles` table with `csl_xml`.

## No Placeholder Logic

- Citations and bibliographies are **generated through CSL** — not placeholders
- `csl_service.render_citation()` and `render_bibliography()` use citeproc-py
- Source data must include CSL-compatible fields (title, author, issued, etc.)

## Project-Level Style

- Default: project-level style applies to all books
- Override: book-level style for multi-book projects
- Style is used for citation preview and bibliography generation
