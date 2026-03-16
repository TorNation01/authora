# Genre Template Architecture

## Hierarchy

```
Category (parent)
├── Sub-template 1 (child)
├── Sub-template 2 (child)
└── ...
```

- **Parent**: `parent_id = NULL`, represents the category (e.g. Fiction)
- **Child**: `parent_id = parent.id`, represents genre/sub-type (e.g. Romance)

## Fiction Sub-templates

| Slug | Genre | Structure Framework |
|------|-------|---------------------|
| fiction-romance | Romance | romance_beats |
| fiction-fantasy | Fantasy | three_act |
| fiction-thriller | Thriller | mystery_thriller |
| fiction-scifi | Science Fiction | three_act |
| fiction-horror | Horror | three_act |
| fiction-historical | Historical Fiction | three_act |
| fiction-literary | Literary Fiction | three_act |
| fiction-ya | Young Adult | three_act |
| fiction-contemporary | Contemporary Fiction | three_act |
| fiction-short | Short Story | three_act |
| fiction-series | Series | three_act |
| fiction-general | General Fiction | three_act |

## Non-fiction Sub-templates

| Slug | Genre | Structure Framework |
|------|-------|---------------------|
| nonfiction-selfhelp | Self-Help | problem_solution_result |
| nonfiction-business | Business | problem_solution_result |
| nonfiction-finance | Finance | problem_solution_result |
| nonfiction-health | Health | problem_solution_result |
| nonfiction-parenting | Parenting | problem_solution_result |
| nonfiction-relationships | Relationships | problem_solution_result |
| nonfiction-educational | Educational | problem_solution_result |
| nonfiction-thought-leadership | Thought Leadership | problem_solution_result |
| nonfiction-howto | How-To | instructional |
| nonfiction-faith | Faith | problem_solution_result |
| nonfiction-professional | Professional | authority |
| nonfiction-general | General Non-fiction | problem_solution_result |

## Structure Frameworks

### Fiction

- `three_act` – Setup, Confrontation, Resolution
- `hero_journey` – Monomyth
- `romance_beats` – Meet-cute, tension, HEA
- `mystery_thriller` – Clues, twists, payoff
- `save_the_cat` – Blake Snyder beats
- `custom` – User-defined

### Non-fiction

- `problem_solution_result` – Reader problem → your solution → outcome
- `step_by_step` – Transformation in steps
- `authority` – Credibility and expertise
- `instructional` – How-to guide
- `modular` – Teaching modules
- `custom` – User-defined

## Extensibility

To add a new sub-template:

1. Add definition to `authora/data/template_definitions.py`
2. Set `parent_slug` to parent category slug
3. Run `python -m authora.scripts.seed_project_templates`
