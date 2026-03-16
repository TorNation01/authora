# Hybrid Mode Support

Hybrid mode lets users mix tools from fiction, non-fiction, memoir, and workbook in a single project. Users can enable or disable modules freely with no content loss.

## Enabling Hybrid Mode

Set `knowledge_mode: "hybrid"` when creating or updating a project. Hybrid mode defaults to **all** modules enabled.

## Manual Module Override

In any mode (including hybrid), users can override the default module set:

1. **Use mode defaults**: `knowledge_modules: null` (or omit)
2. **Clear override**: `knowledge_modules: []` — reverts to mode defaults
3. **Custom set**: `knowledge_modules: ["characters", "sources", "research", ...]` — only these modules are enabled

## API

### Get Current Config
```
GET /api/v1/projects/{project_id}/vault/config
```

Check `knowledge_modules_override` to see if the user has set a custom module list.

### Set Custom Modules
```
PATCH /api/v1/projects/{project_id}/vault/config
Body: {
  "knowledge_mode": "hybrid",
  "knowledge_modules": ["characters", "locations", "sources", "research", "ideas"]
}
```

### Revert to Mode Defaults
```
PATCH /api/v1/projects/{project_id}/vault/config
Body: { "knowledge_modules": [] }
```

## All Available Modules (Hybrid)

| Module ID | Label |
|-----------|-------|
| `characters` | Character Bible |
| `people` | People Map |
| `locations` | Worldbuilding / Locations |
| `concepts` | Concept Map |
| `framework` | Framework Map |
| `chapter_promise` | Chapter Promise Tracker |
| `timeline` | Timeline / Events |
| `relationships` | Relationship Mapping |
| `themes` | Themes / Motifs |
| `ideas` | Idea Capture |
| `research` | Research Vault |
| `sources` | Source Manager |
| `claims` | Claims / References |
| `methodology` | Methodology Notes |
| `memories` | Memory Capture |
| `reflections` | Reflection Notes |
| `private_notes` | Private / Sensitivity Notes |
| `prompts` | Prompt Bank |
| `exercises` | Exercise Blocks |
| `transformation` | Transformation Path |
| `modules` | Module Structure |
| `outcome` | Reader Outcome Tracking |

## UI Behaviour

- **Module picker**: In hybrid mode (or when override is set), show a list of all modules with toggles
- **Simple mode**: When using mode defaults, hide the picker; show only the enabled panels
- **Switching to hybrid**: User enables hybrid → all modules appear; they can then disable unwanted ones
- **Switching from hybrid**: User picks fiction → mode defaults apply; their custom list is cleared unless you preserve it (current implementation clears on mode change; override is independent)

## No Content Loss

- Switching from hybrid to fiction: Characters, locations, etc. remain; only the UI hides non-fiction panels
- Switching from fiction to hybrid: All panels appear; existing data is still there
- Disabling a module: Data stays in DB; panel is hidden
- Re-enabling: Panel shows existing data again
