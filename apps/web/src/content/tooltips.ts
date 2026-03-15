/** Help tooltips for UI features. Warm, clear, jargon-free. */

export const HELP_TOOLTIPS: Record<string, string> = {
  ghostwriter_mode:
    "Light = AI suggests ideas and outlines. Heavy = AI drafts full chapters from your briefs. Full = AI does most of the drafting; you guide and refine. You're always in control.",
  chapter_brief:
    "A few sentences about what happens in this chapter. The AI uses it to write a draft that matches your vision.",
  outline:
    "Your book's structure. Add chapters and short summaries. Drag to reorder—it's flexible.",
  notes:
    "Your idea bank. Research, character notes, quotes—all in one place. Link notes to chapters for easy reference.",
  ai_actions:
    "Select text, then choose: rewrite, expand, shorten, change tone, or continue writing. AI helps when you ask.",
  version_history:
    "See past versions of this chapter. Restore any version if you want to go back.",
  export:
    "Download your manuscript as DOCX, PDF, EPUB, or plain text. Choose your format and go.",
  accountability_goals:
    "Set daily or weekly word goals. We'll nudge you gently—or more firmly—based on what you prefer.",
  gamification:
    "Earn XP and badges as you write. Optional—turn off in settings if you prefer a quiet, distraction-free space.",
  writing_plan:
    "Set a target finish date. We'll help you break it into milestones and chapter goals.",
  reference_panel:
    "Look up definitions, synonyms, and readability. Select a word or phrase to analyze.",
  autosave:
    "Your work saves automatically as you type. No save button needed—just write.",
  distraction_free:
    "Hide sidebars and panels for a calm, focused writing view. Just you and the page.",
  publishing_prep:
    "Generate synopsis, blurb, and query materials for agents or self-publishing.",
};

export function getTooltip(key: string): string | undefined {
  return HELP_TOOLTIPS[key];
}
