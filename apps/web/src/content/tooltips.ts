/** Help tooltips for UI features. */

export const HELP_TOOLTIPS: Record<string, string> = {
  ghostwriter_mode:
    "Light = AI assists with outlines and suggestions. Heavy = AI drafts chapters from briefs. Full = AI handles most drafting; you guide and refine.",
  chapter_brief:
    "A short summary of what happens in this chapter. The AI uses it to generate a draft.",
  outline:
    "Your book's structure. Add chapters and summaries. You can reorder anytime.",
  notes:
    "Research, ideas, and scratchpad. Link notes to chapters for easy reference while writing.",
  ai_actions:
    "Select text and choose an action: rewrite, expand, shorten, change tone, or continue writing.",
  version_history:
    "See previous versions of this chapter. Restore any version if you want to go back.",
  export:
    "Export your manuscript as DOCX, PDF, EPUB, or plain text. Choose format and options.",
  accountability_goals:
    "Set daily or weekly word goals. We'll nudge you gently (or firmly) based on your preference.",
  gamification:
    "Earn XP, badges, and streaks as you write. Optional—turn off in settings if you prefer a quiet workspace.",
  writing_plan:
    "Set a target finish date and we'll help you break it into milestones and chapter targets.",
  reference_panel:
    "Look up definitions, synonyms, and get readability analysis. Select text to analyze.",
  autosave: "Your work saves automatically as you type. No need to hit save.",
  distraction_free:
    "Hide the sidebar and panels for a clean, focused writing view.",
  publishing_prep:
    "Generate synopsis, blurb, and other materials for querying agents or self-publishing.",
};

export function getTooltip(key: string): string | undefined {
  return HELP_TOOLTIPS[key];
}
