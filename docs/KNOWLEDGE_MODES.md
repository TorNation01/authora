# Knowledge Modes

AUTHORA adapts the research vault, idea system, and support tools based on project type. Each knowledge mode surfaces a tailored set of modules so fiction writers get story-bible tools and non-fiction writers get research and framework tools without fiction-style clutter.

## Modes

| Mode | Description |
|------|-------------|
| **fiction** | Character bible, worldbuilding, plot timeline, factions, locations, themes, scene ideas, dialogue capture |
| **nonfiction** | Concept map, framework map, chapter promise tracker, source manager, claims/references, methodology notes, research |
| **memoir** | People map, life-event timeline, memory capture, reflection notes, thematic life arc, sensitivity/private notes |
| **workbook** | Prompt bank, exercise blocks, transformation path, module structure, reader outcome tracking |
| **hybrid** | Mixed toolset — user can enable/disable any module freely |

## Selecting Mode

- **Project creation**: Set `knowledge_mode` in `ProjectCreate` or `ProjectWizardRequest`
- **Later**: Update via `PATCH /api/v1/projects/{project_id}` or `PATCH /api/v1/projects/{project_id}/vault/config`

## Default Modules by Mode

### Fiction
- `characters` — Character Bible
- `locations` — Worldbuilding / Locations
- `timeline` — Timeline / Events
- `relationships` — Relationship Mapping
- `themes` — Themes / Motifs
- `ideas` — Idea Capture
- `research` — Research Vault
- `sources` — Source Manager

### Non-Fiction
- `concepts` — Concept Map
- `framework` — Framework Map
- `chapter_promise` — Chapter Promise Tracker
- `sources` — Source Manager
- `claims` — Claims / References
- `methodology` — Methodology Notes
- `research` — Research Vault
- `ideas` — Idea Capture

### Memoir
- `people` — People Map
- `timeline` — Timeline / Events
- `memories` — Memory Capture
- `reflections` — Reflection Notes
- `themes` — Themes / Motifs
- `sources` — Source Manager
- `research` — Research Vault
- `ideas` — Idea Capture
- `private_notes` — Private / Sensitivity Notes

### Workbook
- `prompts` — Prompt Bank
- `exercises` — Exercise Blocks
- `transformation` — Transformation Path
- `modules` — Module Structure
- `outcome` — Reader Outcome Tracking
- `research` — Research Vault
- `ideas` — Idea Capture

### Hybrid
All modules from all modes. User can enable/disable any subset.

## API

### Get Vault Config
```
GET /api/v1/projects/{project_id}/vault/config
```

Returns:
- `knowledge_mode` — Current mode
- `knowledge_modules_override` — Whether user has manually set modules
- `enabled_modules` — List of enabled module IDs
- `modules_with_labels` — `{id, label}` for UI
- `available_modes` — All mode IDs
- `default_modules_by_mode` — Default modules per mode
- `all_module_labels` — Labels for all module IDs

### Update Vault Config
```
PATCH /api/v1/projects/{project_id}/vault/config
Body: { "knowledge_mode": "nonfiction", "knowledge_modules": ["concepts", "sources", "research"] }
```

- `knowledge_modules: null` — Use mode defaults
- `knowledge_modules: []` — Clear override, use mode defaults
- `knowledge_modules: ["a", "b"]` — Override with specific modules

## No Content Loss

Switching modes does **not** delete vault data. Characters, research, ideas, etc. remain in the database. Only the UI panels shown change. Users can switch modes and return without losing content.
