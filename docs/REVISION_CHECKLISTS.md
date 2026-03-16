# Revision Checklists

Each revision pass type has a default checklist. Items are generated when the pass is created and can be extended with custom items.

## Default Checklists by Pass Type

### Structural pass

- Does each scene/chapter advance the plot or character?
- Are there any scenes that can be cut or merged?
- Does the opening hook and the ending satisfy?
- Is the story structure clear (setup, conflict, resolution)?

### Clarity pass

- Is every sentence clear on first read?
- Are transitions between scenes and chapters smooth?
- Is the POV consistent and clear?
- Are there any confusing or ambiguous passages?

### Pacing pass

- Does the story move at the right speed for each section?
- Are there slow spots that need tightening?
- Are action/tense moments given enough space?
- Does the rhythm vary appropriately?

### Emotional depth pass

- Do key moments land emotionally?
- Are character reactions believable and earned?
- Is the emotional arc clear and satisfying?
- Are there opportunities to deepen reader connection?

### Consistency pass

- Are character details consistent throughout?
- Is the timeline and world logic consistent?
- Do voice and tone stay consistent?
- Are any continuity errors fixed?

### Grammar and polish pass

- Spelling and grammar checked
- Repetitive words or phrases reduced
- Sentence variety and flow improved
- Dialogue punctuation and tags clean

### Custom pass

No default items. Add your own checklist items when creating the pass.

## Adding Custom Checklist Items

Use the API to add items to any pass:

```
POST /projects/{id}/revision-passes/{pass_id}/checklist-items
Body: { "title": "Your custom item", "sort_order": 0 }
```

## Checklist Usage

Checklist items are **informational** for the pass—they guide what to look for. Progress is tracked at the **chapter level** (mark chapter complete) rather than per checklist item. For granular tracking, use comments linked to the pass.

## Linking Comments to Passes

When adding a comment during a revision pass, include `revision_pass_id` in the request. The comment will appear in the pass's unresolved count and can be filtered in the Revision panel.
