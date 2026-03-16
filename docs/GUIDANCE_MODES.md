# Guidance Modes

AUTHORA supports three genre-guidance modes so writers can choose the amount of structure that fits their process.

## Modes

### 1. Guided Mode

- **Full genre-aware guidance**: Genre-specific prompts, beat tracking, structure expectations
- **Full framework-aware guidance**: Writing framework (e.g. Three-Act, Hero's Journey) drives milestones and suggestions
- **Genre-specific prompts**: In editor, sidebar, and AI assistance
- **Framework-specific prompts**: Beat/stage reminders, structural nudges
- **Genre-aware milestone generation**: From template and framework
- **Best for**: Straight genre projects (romance, thriller, memoir, business book)

### 2. Flexible Mode

- **Lighter genre support**: Optional framework suggestions, reduced assumptions
- **Generic writing prompts mixed with relevant suggestions**: Less rigid
- **Less rigid structural expectations**: Fewer chapter skeletons, optional framework
- **Ideal for**: Cross-genre, hybrid projects (romance + fantasy + thriller, memoir with workbook elements)

### 3. Freeform Mode

- **No genre-specific guidance**: Generic writing support only
- **No framework pressure**: No beat/genre warnings
- **Blank or minimally structured project flow**: One blank chapter by default
- **Custom milestones and goals**: User-defined
- **Full creative control**: No genre rails
- **Best for**: Experimental literary fiction, business book with custom structure, any project where structure feels limiting

## Setting the Mode

- **During project creation**: Wizard step 1 includes guidance mode selector
- **Quick create (Start fast)**: Defaults to freeform
- **Project settings**: Editable at any time via `/dashboard/projects/{id}/settings`
- **Switchable**: Change mode without damaging content

## API

- `POST /api/v1/projects` — `guidance_mode` in body (default: guided)
- `POST /api/v1/projects/from-wizard` — `guidance_mode` in body (default: guided)
- `PATCH /api/v1/projects/{id}` — `guidance_mode` to change

## Data Model

- `Project.guidance_mode`: `guided` | `flexible` | `freeform` (default: guided)
