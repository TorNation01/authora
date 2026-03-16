# Template Activation

## Overview

When a user selects a template in the project creation wizard, a preview card shows what the template helps with, who it's for, and what they get.

## Template Preview Card

- **Location** — Project wizard step 1, below guidance mode
- **Trigger** — When `selectedTemplateId` is set
- **Data** — Fetched via `GET /api/v1/templates/{id}`

## Displayed Fields

- **Name** — Template name
- **Book type / genre** — Badge
- **Description** — What the template does
- **Best for** — `who_it_is_for`
- **What you get** — `expected_outcome`
- **Suggested workflow** — `suggested_workflow`
- **Milestones** — Count of `default_milestones`
- **Export formats** — `export_recommendations`

## Activation Flow

1. User selects template (featured or category)
2. Preview card appears with full template details
3. User continues wizard (steps 2–7)
4. On create, template is applied via `template_id` in `POST /api/v1/projects/from-wizard`
5. If `guidance_mode: freeform`, template_id is null (blank start)

## Start from Blank

- User can choose Freeform mode → no template applied
- Or select template then change to Freeform in step 1
- Template preview card shows "Start from blank instead" when handlers provided (currently inline in wizard)
