# Project Type Adaptation

AUTHORA adapts the knowledge vault and support tools to project type so the right tools are surfaced for each kind of book.

## Mapping: Mode → Backend Entities

The same backend models serve multiple modes with different labels and default views:

| Module ID | Backend Entity | Fiction | Non-Fiction | Memoir | Workbook |
|-----------|----------------|---------|-------------|--------|----------|
| `characters` | VaultCharacter | Character Bible | — | — | — |
| `people` | VaultCharacter | — | — | People Map | — |
| `locations` | VaultLocation | Worldbuilding | — | — | — |
| `concepts` | VaultLocation (category=concept) | — | Concept Map | — | — |
| `framework` | VaultLocation (category=framework) | — | Framework Map | — | — |
| `modules` | VaultLocation (hierarchy) | — | — | — | Module Structure |
| `timeline` | TimelineEvent | Plot/Event Timeline | — | Life-Event Timeline | — |
| `relationships` | VaultRelationship | Character Relationships | — | People Relationships | — |
| `themes` | Theme | Themes/Motifs | — | Thematic Life Arc | — |
| `ideas` | Idea | Scene/Dialogue Ideas | Ideas | Memory/Reflection Ideas | Prompt/Exercise Ideas |
| `research` | ResearchEntry | Research Vault | Research Vault | Research Vault | Research Vault |
| `sources` | Source | Source Manager | Source Manager | Source Manager | — |
| `chapter_promise` | Idea (type) / Theme | — | Chapter Promise Tracker | — | — |
| `claims` | ResearchEntry (type) | — | Claims/References | — | — |
| `methodology` | ResearchEntry (type) | — | Methodology Notes | — | — |
| `memories` | Idea (type) | — | — | Memory Capture | — |
| `reflections` | Idea (type) | — | — | Reflection Notes | — |
| `private_notes` | VaultCharacter.private_notes | — | — | Sensitivity Notes | — |
| `prompts` | Idea (type) | — | — | — | Prompt Bank |
| `exercises` | Idea (type) | — | — | — | Exercise Blocks |
| `transformation` | Idea / ResearchEntry | — | — | — | Transformation Path |
| `outcome` | ResearchEntry / Note | — | — | — | Reader Outcome |

## UI Adaptation

- **Labels**: Use `modules_with_labels` from vault config for panel titles
- **Default views**: Filter by `idea_type`, `entry_type`, `category` based on mode
- **Hide disabled**: Only render panels for `enabled_modules`
- **Mode switcher**: Allow changing mode in project settings; no content is deleted

## Project Creation

When creating a project via wizard:
- `book_type: "fiction"` → default `knowledge_mode: "fiction"`
- `book_type: "nonfiction"` → default `knowledge_mode: "nonfiction"`
- User can override with `knowledge_mode` in the request

For simple project create:
- `knowledge_mode` defaults to `"fiction"` if not provided

## Editing Mode

- **Project settings**: `PATCH /api/v1/projects/{project_id}` with `knowledge_mode`
- **Vault config**: `PATCH /api/v1/projects/{project_id}/vault/config` for mode and/or module override
