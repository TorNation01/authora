# Story Health System

The Story Health System is the user-facing layer of the Story Integrity Engine. It surfaces manuscript health in a supportive, non-judgmental way.

## Components

- **Integrity score / health meter** — Summary of open issues by severity
- **Story health summary** — Last scan time, issue count, quick status
- **Chapter health indicators** — Per-chapter issue counts (when applicable)
- **Unresolved issue count** — Badge or count of open issues

## UX Principles

- **Supportive** — "Here's what could be stronger" not "This is wrong"
- **Clear** — Plain-English explanations
- **Actionable** — Every issue has fix suggestions
- **Optional** — Writer can resolve, ignore, or mark as intentional

## Integration Points

- Writing studio toolbar: "Story Health" button
- Story health panel (slide-out)
- Pre-export integrity check (optional)
- Finish mode: integrity panel when approaching completion

## Privacy

- No manuscript content is logged or stored beyond the scan session
- Issue metadata (type, severity, chapter) is stored for analytics
- Story map snapshot is stored in the scan record for debugging
