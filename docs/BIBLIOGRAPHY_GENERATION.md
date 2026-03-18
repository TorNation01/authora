# Bibliography Generation

AUTHORA generates bibliographies from cited sources using CSL.

## Overview

- **Real generation** — citeproc-py processes CSL styles
- **No placeholders** — Output is formatted bibliography text
- **Multiple formats** — Plain text or HTML

## API

```
POST /api/v1/projects/{id}/references/bibliography
{
  "source_ids": ["uuid1", "uuid2"],
  "style_slug": "apa",
  "format_type": "plain"  // or "html"
}
```

Response: `{ "entries": ["...", "..."] }`

## Flow

1. Client selects sources (from vault or from cited-in-chapter)
2. Request includes source IDs and style
3. Server loads sources, builds CSL JSON (from `csl_json` or `_source_to_csl`)
4. `render_bibliography()` processes with citeproc-py
5. Returns formatted entries in order

## Citation Preview

Before inserting:
```
POST /api/v1/projects/{id}/references/citation-preview
{
  "source_ids": ["uuid1"],
  "style_slug": "apa"
}
```

Returns in-text citation string, e.g. `(Smith, 2024)` or `[1]`.

## Export

- Bibliography can be copied to clipboard or exported
- Citation-ready export: use bibliography entries in document export
- Future: integrate into DOCX/PDF export with full citation formatting
