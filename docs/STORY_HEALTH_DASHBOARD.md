# Story Health Dashboard

The Story Health dashboard is the primary UI for the Story Integrity Engine.

## Location

- **Writing studio** — "Story Health" button in toolbar opens the panel
- **Panel** — slide-out panel on the right side of the editor

## Components

### Health Summary

- Open issue count
- Last scan timestamp
- Severity breakdown (low, moderate, high, critical)
- Category breakdown (structure, character, pacing, etc.)

### Scan

- "Scan" button — Triggers full project scan
- Loading state during scan
- Toast on completion

### Issue List

- Open issues only (filterable)
- Per issue:
  - Severity badge
  - Title and description
  - "Go to chapter" link (if chapter-specific)
  - Resolve button
  - Mark intentional button

### Future Enhancements

- Integrity score / health meter (0–100)
- Chapter health indicators in manuscript sidebar
- Thread status board
- Arc status board
- Continuity warning badge
- Pre-export integrity check
- Finish mode integrity panel

## API Integration

- `GET /integrity/health` — health summary
- `POST /integrity/scan` — run scan
- `GET /integrity/issues` — list issues (filterable)
- `PATCH /integrity/issues/{id}` — resolve, ignore, mark intentional
- `GET /integrity/issues/{id}/guidance` — fix guidance
