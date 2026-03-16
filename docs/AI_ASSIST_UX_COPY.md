# AI Assist UX Copy & Interface Behaviour

User-facing copy and interface behaviour for AUTHORA's AI assistance layer.

**Tone:** Premium, calm, intelligent, reassuring, non-technical by default, advanced when needed.

---

## Primary Entry Points

| Key | Copy | Use |
|-----|------|-----|
| askAi | Ask AI | Primary CTA, bubble menu, floating action |
| aiAssist | AI assist | Panel title, split view label |
| getHelp | Get help | Secondary entry, empty state |

---

## Action Labels

User-facing labels for AI actions. Prefer these over technical `action_id` values.

| Action ID | Label | Notes |
|-----------|-------|-------|
| help_when_stuck | Help me get unstuck | When stuck on next sentence |
| improve_flow | Improve flow | Transitions, readability |
| rewrite_sentence / rewrite_paragraph | Rewrite selection | Single label for both |
| improve_wording | Make this clearer | Clarity focus |
| continue_draft | Continue from here | Cursor or selection |
| expand | Expand this | Add detail |
| condense | Shorten this | Conciseness |
| change_tone | Change tone | Formal, casual, etc. |
| generate_scene_ideas / generate_chapter_ideas | Brainstorm options | Generic for ideation |
| summarize_chapter | Summarise this chapter | UK spelling |
| summarize_section | Summarise this section | UK spelling |
| suggest_transitions / fix_transitions | Suggest transitions | Flow between sections |
| blurb_copy | Write blurb | Marketing copy |
| freeform_creative | Ask AI | Freeform entry |

---

## Compare / Alternatives

| Key | Copy |
|-----|------|
| compareAlternatives | Compare alternatives |
| generateAlternatives | Generate alternatives |
| showOptions | Show options |

---

## Model / Routing Mode Copy

Non-technical labels for routing mode selectors. Use in book AI preferences and settings.

| Mode Value | Label | Description |
|------------|-------|--------------|
| auto | Automatic | Choose the best option for each task |
| quality_first | Quality first | Prioritise stronger models for polish and coherence |
| speed_first | Speed first | Prioritise faster responses |
| privacy_first | Privacy first | Keep requests on approved local models only |
| local_first | Local first | Use local AI when available, cloud when needed |
| local | Local only | Local models only—no cloud fallback |
| cloud / cloud_only | Cloud only | Use cloud AI only |

---

## Provider Status (User-Visible)

Show when a response used local vs cloud AI.

| Key | Copy |
|-----|------|
| usingLocalAi | Using local AI |
| usingCloudAi | Using cloud AI |
| localAiLabel | Local AI |
| cloudAiLabel | Cloud AI |

**Behaviour:** Display a small badge or label near the AI output (e.g. "Using local AI") so users know where their request was processed. Use `X-AI-Provider` response header when available.

---

## Onboarding / Setup

| Key | Copy |
|-----|------|
| localFirstSet | AI assistance is set to local-first. |
| canChangeLater | You can change this later. |
| chooseMode | Choose how AI assists you |

**Behaviour:** When setting up AI for the first time, show a reassuring line like "AI assistance is set to local-first. You can change this later." Avoid technical jargon.

---

## Trust Copy

Reassuring, non-technical statements. Use in onboarding, settings, and help.

| Key | Copy |
|-----|------|
| neverAutoReplace | AI suggestions never replace your writing automatically. |
| youStayInControl | You stay in control of what changes. |
| localKeepsApproved | Local mode keeps requests on approved local models. |
| sourceReviewNote | Source-based tasks may need your review before use. |
| voiceStaysYours | AI can help shape language, structure, and ideas while you keep the voice. |
| youChooseWhen | You choose when and how much to use. Ignore suggestions when you prefer. |

**Behaviour:** Surface trust copy in:
- First-time AI setup
- Privacy-first mode explanation
- Help / FAQ for AI
- Empty states when user hesitates

---

## Advanced Settings

Only show when user expands "Advanced" or similar. Keep primary UI simple.

| Key | Copy |
|-----|------|
| preferredProvider | Preferred provider |
| preferredLocalModel | Preferred local model |
| allowCloudFallback | Allow cloud fallback |
| strictLocalOnly | Strict local-only mode |
| writingAssistIntensity | Writing assist intensity |
| brainstormingTools | Brainstorming tools |
| rewriteShortcuts | Rewrite shortcuts |

**Behaviour:** Collapse advanced options by default. Use clear section headings. "Preferred provider" and "Preferred local model" are for power users who know the difference.

---

## Writing Assist Intensity

Maps to assistance level (strict / moderate / creative).

| Level | Label | Description |
|-------|-------|--------------|
| strict | Minimal | Light suggestions, preserve your voice |
| moderate | Moderate | Balanced—improve without overstepping |
| creative | Creative | More freedom to reimagine |

---

## Interface Behaviour

### Selection-first flow

1. User selects text → bubble menu or AI panel shows relevant actions.
2. Primary actions visible: Rewrite selection, Improve flow, Shorten this, Expand this, Continue from here.
3. "Ask AI" or "Brainstorm options" available without selection for context-based tasks.

### Empty states

- **No selection:** "Select text to get started." or "Or ask anything—describe what you need."
- **No output yet:** "Try an action above, or type a custom request."

### Provider badge

- After AI response, show "Using local AI" or "Using cloud AI" near the output.
- Subtle, non-intrusive. Helps privacy-conscious users.

### Mode selector

- Default: "Automatic" (auto).
- Options: Automatic, Quality first, Speed first, Privacy first, Local first.
- Advanced: Local only, Cloud only, Preferred provider, Preferred local model.

### Trust placement

- On first AI use: brief trust line ("You stay in control of what changes.").
- In Privacy first mode: "Local mode keeps requests on approved local models."

---

## Implementation

- **Frontend:** `apps/web/src/content/ai-assist-copy.ts`
- **Helpers:** `getActionLabel(actionId)`, `getActionDescription(actionId)`
- **API:** Actions come from `/api/v1/ai/actions`; use `getActionLabel` to override labels for display.

---

## Related

- [AI_ARCHITECTURE.md](./AI_ARCHITECTURE.md)
- [LOCAL_FIRST_MODE.md](./LOCAL_FIRST_MODE.md)
- [PRIVACY_FIRST_AI_MODE.md](./PRIVACY_FIRST_AI_MODE.md)
