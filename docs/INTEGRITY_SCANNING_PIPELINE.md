# Integrity Scanning Pipeline

The Story Integrity Engine scans manuscripts through a structured pipeline.

## Scan Types

| Type | Scope | Use case |
|------|-------|----------|
| `full_project` | All chapters | Manual scan, full analysis |
| `chapter` | Single chapter | After chapter completion |
| `section` | Section within chapter | Targeted analysis |
| `revision_pass` | Chapters in revision | During revision mode |
| `export_readiness` | Full project | Before export |
| `pre_finish` | Full project | Finish mode entry |
| `manual_targeted` | User-selected scope | Targeted scan |

## Scan Timing

- **On demand** — User clicks "Scan" in Story Health panel
- **On milestone** — (Future) After chapter completion
- **Before export** — (Future) Pre-export check
- **Scheduled** — (Future) Background analysis
- **Continuous** — (Future) Optional real-time monitoring

## Pipeline Steps

1. **Load** — Project, book, chapters, vault data (characters, themes, timeline events)
2. **Build story map** — Threads, character appearances, themes, pacing, promises, setup candidates
3. **Run detectors** — Project-type-specific detectors (general, fiction, nonfiction, memoir, workbook)
4. **Persist** — Save scan record and issues to database
5. **Return** — Scan summary with issue count

## Caching and Performance

- Story map is stored in `IntegrityScan.story_map_snapshot` for debugging
- Incremental rescans: (Future) Only re-scan changed chapters
- Large manuscripts: Detectors avoid loading full content into memory; use word counts and summaries

## Triggered By

- `manual` — User-initiated
- `milestone` — (Future) Chapter completion
- `export` — (Future) Pre-export
- `scheduled` — (Future) Background job
