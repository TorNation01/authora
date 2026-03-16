# Project Creation Wizard

## Overview

The project creation wizard guides users through choosing a template, naming their project, and setting up structure. It supports both **Quick start** (one project name) and **Guided setup** (7-step wizard).

## Modes

### Start fast

- Project name only
- `guidance_mode: freeform`
- Creates project, redirects to project page

### Guided setup

1. **Choose project type** — Guidance mode (guided, flexible, freeform) + template selection
2. **Genre or name** — Sub-templates if available, else project name
3. **Name your project** — Project name + book title
4. **Core idea** — One sentence about the book
5. **Structure framework** — 3-act, hero's journey, etc.
6. **Writing goals** — Target words, target date
7. **Ready to create** — Summary and create

## Pre-fill from Onboarding

- On wizard load, fetches `GET /api/v1/auth/me/preferences`
- Pre-fills `guidance_mode` from `onboarding_guidance_mode` if set

## API

- `POST /api/v1/projects` — Quick create
- `POST /api/v1/projects/from-wizard` — Wizard create (project + book + chapters)
- `GET /api/v1/templates/categories` — Template categories
- `GET /api/v1/templates/featured-launch` — Featured templates
- `GET /api/v1/templates/{id}` — Full template (for preview)

## Template Preview

- `TemplatePreviewCard` shows when a template is selected
- Fetches full template via `GET /api/v1/templates/{id}`
- Displays: best for, what you get, suggested workflow, milestones, export formats
