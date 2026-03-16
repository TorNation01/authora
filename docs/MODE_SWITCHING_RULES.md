# Mode Switching Rules

Switching guidance mode is safe and does not delete user work.

## Rules

1. **No content deletion**: Switching mode never deletes manuscript, notes, or chapters.
2. **Guided → Flexible/Freeform**: Preserves all content. Template and framework IDs remain in DB but are not used for prompts or milestones.
3. **Freeform → Guided**: Optional framework mapping. We do not force a framework; user can add one later if desired.
4. **Flexible → Guided**: User can enable full framework if they want more structure.
5. **Mixed-genre projects**: Can remain in Flexible Mode permanently.

## Implementation

- Mode switch = single PATCH to `projects.guidance_mode`
- No migration of content
- No cascade deletes
- Services (milestone_engine, progress_dashboard) read `project.guidance_mode` and adapt

## Safe Migration Logic

When switching:

- **To Freeform**: Set `guidance_mode = "freeform"`. Template/framework refs stay; they are ignored.
- **To Flexible**: Set `guidance_mode = "flexible"`. Lighter logic applies.
- **To Guided**: Set `guidance_mode = "guided"`. If book has framework_id, full framework logic applies. If not, template defaults apply.

No data migration scripts required. The mode is a runtime flag.
