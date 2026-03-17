# Density Dashboard

The Story Density panel appears as a tab within the Story Health sidebar (Issues | Chapter Health | Density).

## Components

- **Manuscript density score** — 0–100 progress bar from latest scan
- **Issue summary** — Open count, by severity, by action (trim/compress/strengthen)
- **Issue list** — Each issue shows severity, action category, title, description, chapter link
- **Actions** — Resolve, Mark intentional
- **Scan button** — Run density scan on demand

## Integration

- **Story Health panel** — Density tab shown when `feature_story_density` is enabled
- **Chapter navigation** — "Go to chapter" links to the affected chapter
- **Revision mode** — Density issues can be reviewed during revision (future: revision queue integration)

## Pre-Export Check

Future: Pre-export density cleanup check in export/readiness center.
