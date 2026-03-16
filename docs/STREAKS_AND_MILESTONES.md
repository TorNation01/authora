# Streaks and Milestones

## Streak System

### How Streaks Work

- **Daily streak**: Consecutive days with at least some words written
- **Current streak**: Today + yesterday + ... until a gap
- **Longest streak**: All-time best (never decreases)

Streaks are updated when words are recorded via `record_words` in the gamification service.

### Grace Days

- **Purpose**: Allow occasional missed days without breaking the streak
- **Range**: 0–7 days (configurable in AccountabilitySettings)
- **Logic**: When a day is missed, one grace day can be consumed instead of breaking the streak
- **Tracking**: `UserStats.grace_days_used` tracks consumption

### Flexible Streak Mode

- **Purpose**: For writers who dislike rigid daily pressure
- **Logic**: Weekly consistency instead of strict daily
- **Example**: "4 of 5 target days this week" vs "7-day streak"

### Streak Visibility

- **Setting**: `AccountabilitySettings.streak_visible`
- **When off**: Streak data is not shown in the dashboard or overview
- **Use case**: Writers who find streak pressure stressful

## Milestone System

### Framework-Aware Milestones

When a project uses a template or framework, milestones are generated from:

- **Template `default_milestones`**: e.g. outline, act1, act2, act3, revision, final
- **Book type**: fiction vs nonfiction (different default sets)
- **Writing plan**: target_finish_date, total_target_words

### Fiction Milestones (examples)

- premise_complete, outline_complete
- act_one_complete, act_two_complete, midpoint_reached, act_three_complete
- first_draft_complete, revision_pass_one, beta_feedback, export_ready

### Nonfiction Milestones (examples)

- chapter_promise_complete, framework_section_complete
- workbook_module_complete, research_phase_complete
- intro_draft, core_chapters_draft, conclusion_draft
- first_draft_complete, expert_review, export_ready

### Freeform Milestones

- **Custom**: User-defined title and target
- **Chapter-count**: e.g. "Chapter 5 complete"
- **Word-count**: e.g. "25,000 words"
- **Deadline**: Date-based

### Milestone Completion

- **Manual**: User marks complete via API or UI
- **Automatic**: (Future) When chapter/section status or word count reaches target

### API

| Endpoint | Method | Description |
|---------|--------|-------------|
| `/accountability/milestones` | GET | List milestones (book_id, include_completed) |
| `/accountability/milestones/generate` | POST | Generate from template |
| `/accountability/milestones/custom` | POST | Create custom |
| `/accountability/milestones/{id}/complete` | POST | Mark complete |
