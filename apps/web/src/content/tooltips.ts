/** Help tooltips for UI features. Warm, clear, jargon-free. */

export const HELP_TOOLTIPS: Record<string, string> = {
  ghostwriter_mode:
    "Light = AI suggests ideas and outlines. Heavy = AI drafts full chapters from your briefs. Full = AI does most of the drafting; you guide and refine. You're always in control.",
  chapter_brief:
    "A few sentences about what happens in this chapter. AI uses it to write a draft that matches your vision.",
  outline:
    "Your book's structure. Add chapters and short summaries. Drag to reorder—it's flexible.",
  notes:
    "Your idea bank. Research, character notes, quotes—all in one place. Link notes to chapters for easy reference.",
  ai_actions:
    "Select text, then choose: rewrite, expand, shorten, change tone, or continue. AI helps only when you ask.",
  version_history:
    "See past versions of this chapter. Restore any version whenever you want to go back.",
  export:
    "Download your manuscript as Word, PDF, e-reader format, or plain text. Pick your format and go.",
  accountability_goals:
    "Set a pace you can actually keep. Progress builds books. Small, steady sessions count.",
  gamification:
    "Earn badges as you write. Optional—turn off in settings if you prefer a quiet, distraction-free space.",
  writing_plan:
    "Set a target finish date. Every finished stage moves the manuscript forward.",
  reference_panel:
    "Look up definitions, synonyms, and readability. Select a word or phrase to analyze.",
  autosave:
    "Your work saves automatically as you type. No save button—just write.",
  distraction_free:
    'Clear the noise. Stay with the page.',
  publishing_prep:
    "Create synopsis, blurb, and query materials for agents or self-publishing.",
  find_replace: 'Find in chapter or search manuscript. Replace carefully.',
  revision_panel: 'Work through the manuscript one issue at a time.',
  add_comment: 'Leave yourself a marker. Return to this later.',
};

export function getTooltip(key: string): string | undefined {
  return HELP_TOOLTIPS[key];
}
