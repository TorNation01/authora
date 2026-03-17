/** Help tooltips for UI features. Warm, clear, jargon-free. Short and helpful. */

export const HELP_TOOLTIPS: Record<string, string> = {
  // Editor tools
  ghostwriter_mode:
    "Light = AI suggests ideas. Heavy = AI drafts chapters. You're always in control.",
  chapter_brief:
    "A few sentences about what happens here. AI uses it to match your vision.",
  outline:
    "Your book's structure. Add chapters, drag to reorder.",
  notes:
    "Idea bank. Research, character notes—link to chapters.",
  ai_actions:
    "Select text, then: rewrite, expand, shorten, or continue. AI helps when you ask.",
  version_history:
    "Past versions. Restore anytime.",
  export:
    "Download as Word, PDF, EPUB, or plain text.",
  accountability_goals:
    "Set a pace you can keep. Small sessions count.",
  gamification:
    "Earn badges as you write. Optional—turn off in settings.",
  writing_plan:
    "Target finish date. Every stage moves you forward.",
  reference_panel:
    "Definitions, synonyms, readability. Select a word to analyze.",
  autosave:
    "Saves automatically. No save button—just write.",
  distraction_free:
    'Clear the noise. Stay with the page.',
  publishing_prep:
    "Synopsis, blurb, query materials for agents or self-publishing.",
  find_replace: 'Find and replace in chapter or manuscript.',
  revision_panel: 'Work through issues one at a time.',
  add_comment: 'Leave a marker. Return later.',
  vault_panel:
    'Characters, locations, sources. Everything for this chapter.',
  // AI tools
  ai_panel: 'Brainstorm, rewrite, expand. Select text or describe what you need.',
  ai_rewrite: 'Rewrite selected text in a new way.',
  ai_expand: 'Expand selected text with more detail.',
  ai_shorten: 'Tighten selected text.',
  ai_continue: 'Continue writing from the cursor.',
  // Story engines
  story_health: 'Find plot gaps, weak arcs, missing payoff. Scan to analyze.',
  story_integrity: 'Unresolved threads, weak arcs, structural gaps.',
  story_density: 'Filler, repetition, weak sections. Trim or strengthen.',
  integrity_scan: 'Analyze manuscript for plot and character issues.',
  density_scan: 'Analyze for repetition and pacing.',
  // Navigation
  chapters_sidebar: 'Chapters. Click to switch. Drag to reorder.',
  add_chapter: 'Add a new chapter.',
  finish_mode: 'Focus on crossing the finish line. One chapter at a time.',
  ghostwriter_link: 'AI-assisted drafting from briefs.',
  edit_polish_link: 'Edit and polish chapters with AI assistance.',
  plan_link: 'Outline, characters, plot. Build your structure.',
  // Misc
  quick_insert: 'Insert placeholder, scene break, or note.',
  dark_mode: 'Toggle dark mode.',
};

export function getTooltip(key: string): string | undefined {
  return HELP_TOOLTIPS[key];
}
