# AUTHORA First Writing Experience System

Production-ready system that ensures new users write something meaningful within minutes of entering the app.

---

## 1. First-Write Flow Summary

### When User Opens Editor for First Time

| Condition | What Shows |
|-----------|------------|
| Empty chapter (0 words) | **FirstWritePromptBlock** |
| Not yet completed first write | Guided options + prompts + AI assist |
| User has written (word count > 0) | **FirstWriteProgress** (until ~150 words) |

### Main Options

| Option | Action |
|--------|--------|
| **Start writing** | Focuses editor—user can type immediately |
| **Generate opening idea** | AI generates a starter paragraph, inserts into editor |
| **Outline chapter** | Opens AI panel |

### Optional Prompts

| Prompt | Action |
|--------|--------|
| Start your first sentence | Focus editor |
| Describe your main idea | Open AI panel |
| Outline your first chapter | Open AI panel |

### AI Assist Entry

| Action | Behavior |
|--------|----------|
| Generate starter paragraph | Calls AI complete, inserts result |
| Suggest ideas | Opens AI panel |

---

## 2. UX Summary

### Low Friction

- **No setup barriers** — User can type immediately. No modal blocks the editor.
- **Immediate typing** — "Start writing" focuses the editor. Placeholder is always visible.
- **Optional prompts** — All prompts are optional. User can ignore and start typing.

### Progressive Disclosure

- First-write block appears only when chapter is empty and user hasn't completed first write.
- Progress reinforcement appears after first write (1–150 words).
- Persisted via `authora_first_write_done` in localStorage—never shows again after completion.

### Non-Intrusive

- Block does not block the editor. Editor is always visible and editable.
- User can dismiss by typing or clicking any option.
- No forced flows.

---

## 3. Production Readiness Confirmation

| Requirement | Status |
|-------------|--------|
| Empty but guided state on first open | ✅ |
| Options: start writing, generate idea, outline chapter | ✅ |
| Optional prompts (first sentence, main idea, outline) | ✅ |
| No setup barriers | ✅ |
| Immediate typing possible | ✅ |
| AI assist: generate starter, suggest ideas | ✅ |
| Progress reinforcement after first write | ✅ |
| Encouragement to continue | ✅ |
| Persistence (remembers completed) | ✅ |

### Files

- `apps/web/src/content/first-write-copy.ts` — Copy for options, prompts, AI assist, progress
- `apps/web/src/components/studio/FirstWritePromptBlock.tsx` — Guided state with options and prompts
- `apps/web/src/components/studio/FirstWriteProgress.tsx` — Progress reinforcement banner
- `apps/web/src/app/dashboard/projects/[id]/books/[bookId]/page.tsx` — Integration, handlers, AI generate
