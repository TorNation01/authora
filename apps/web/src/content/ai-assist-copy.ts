/**
 * Polished user-facing UX copy for AUTHORA's AI assistance layer.
 *
 * Tone: premium, calm, intelligent, reassuring, non-technical by default, advanced when needed.
 * Use these labels and descriptions across the editor, AI panel, settings, and onboarding.
 */

// --- Primary entry points ---

export const AI_ENTRY_COPY = {
  askAi: 'Ask AI',
  aiAssist: 'AI assist',
  getHelp: 'Get help',
} as const;

// --- Action labels (user-facing, non-technical) ---

export const AI_ACTION_LABELS: Record<string, string> = {
  // Core actions
  help_when_stuck: 'Help me get unstuck',
  improve_flow: 'Improve flow',
  rewrite_sentence: 'Rewrite selection',
  rewrite_paragraph: 'Rewrite selection',
  improve_wording: 'Make this clearer',
  continue_draft: 'Continue from here',
  expand: 'Expand this',
  condense: 'Shorten this',
  change_tone: 'Change tone',

  // Brainstorming
  generate_scene_ideas: 'Brainstorm options',
  generate_chapter_ideas: 'Brainstorm options',
  generate_outline: 'Generate outline',
  title_brainstorm: 'Brainstorm titles',
  suggest_chapter_names: 'Suggest chapter names',

  // Clarity & structure
  create_hook: 'Create opening',
  create_conclusion: 'Create conclusion',
  fix_transitions: 'Suggest transitions',
  suggest_transitions: 'Suggest transitions',

  // Summarization
  summarize_chapter: 'Summarise this chapter',
  summarize_section: 'Summarise this section',

  // Generation
  notes_to_prose: 'Turn notes into prose',
  generate_section: 'Generate section',
  generate_examples: 'Generate examples',

  // Editing & polish
  identify_repetition: 'Find repetition',
  style_guidance: 'Style guidance',

  // Copy & marketing
  blurb_copy: 'Write blurb',

  // Research & vault
  research_note_summary: 'Summarise research notes',
  vault_retrieval_summary: 'Summarise vault content',

  // Freeform
  freeform_creative: 'Ask AI',
} as const;

// --- Action short descriptions (tooltips, empty states) ---

export const AI_ACTION_DESCRIPTIONS: Record<string, string> = {
  help_when_stuck: 'Suggest directions to continue when you\'re stuck.',
  improve_flow: 'Smooth transitions and improve readability.',
  rewrite_sentence: 'Rewrite for clarity or style.',
  rewrite_paragraph: 'Rewrite for clarity or style.',
  continue_draft: 'Continue writing from where you left off.',
  expand: 'Add detail and depth.',
  condense: 'Make it more concise while keeping the meaning.',
  change_tone: 'Change tone—formal, casual, or something else.',
  generate_scene_ideas: 'Generate ideas for scenes or sections.',
  generate_chapter_ideas: 'Generate chapter-level ideas.',
  generate_outline: 'Generate an outline from your context.',
  summarize_chapter: 'Create a concise chapter summary.',
  summarize_section: 'Summarise this section.',
  suggest_transitions: 'Suggest transition phrases.',
  notes_to_prose: 'Turn rough notes into polished prose.',
  blurb_copy: 'Write back-cover or marketing copy.',
  freeform_creative: 'Ask anything. Describe what you need.',
} as const;

// --- Compare / alternatives ---

export const AI_ALTERNATIVES_COPY = {
  compareAlternatives: 'Compare alternatives',
  generateAlternatives: 'Generate alternatives',
  showOptions: 'Show options',
} as const;

// --- Model / routing mode copy (non-technical) ---

export const AI_MODE_COPY = {
  automatic: 'Automatic',
  automaticDesc: 'Choose the best option for each task',

  qualityFirst: 'Quality first',
  qualityFirstDesc: 'Prioritise stronger models for polish and coherence',

  speedFirst: 'Speed first',
  speedFirstDesc: 'Prioritise faster responses',

  privacyFirst: 'Privacy first',
  privacyFirstDesc: 'Keep requests on approved local models only',

  localFirst: 'Local first',
  localFirstDesc: 'Use local AI when available, cloud when needed',

  localOnly: 'Local only',
  localOnlyDesc: 'Local models only—no cloud fallback',

  cloudOnly: 'Cloud only',
  cloudOnlyDesc: 'Use cloud AI only',
} as const;

// --- Provider status (user-visible) ---

export const AI_PROVIDER_COPY = {
  usingLocalAi: 'Using local AI',
  usingCloudAi: 'Using cloud AI',
  localAiLabel: 'Local AI',
  cloudAiLabel: 'Cloud AI',
} as const;

// --- Onboarding / setup ---

export const AI_SETUP_COPY = {
  localFirstSet: 'AI assistance is set to local-first.',
  canChangeLater: 'You can change this later.',
  chooseMode: 'Choose how AI assists you',
} as const;

// --- Trust copy (reassuring, non-technical) ---

export const AI_TRUST_COPY = {
  neverAutoReplace:
    'AI suggestions never replace your writing automatically.',
  youStayInControl: 'You stay in control of what changes.',
  localKeepsApproved:
    'Local mode keeps requests on approved local models.',
  sourceReviewNote:
    'Source-based tasks may need your review before use.',
  voiceStaysYours:
    'AI can help shape language, structure, and ideas while you keep the voice.',
  youChooseWhen:
    'You choose when and how much to use. Ignore suggestions when you prefer.',
} as const;

// --- Advanced settings (when user expands) ---

export const AI_ADVANCED_COPY = {
  preferredProvider: 'Preferred provider',
  preferredLocalModel: 'Preferred local model',
  allowCloudFallback: 'Allow cloud fallback',
  strictLocalOnly: 'Strict local-only mode',
  writingAssistIntensity: 'Writing assist intensity',
  brainstormingTools: 'Brainstorming tools',
  rewriteShortcuts: 'Rewrite shortcuts',
} as const;

// --- Writing assist intensity (maps to assistance level) ---

export const AI_INTENSITY_COPY = {
  minimal: 'Minimal',
  minimalDesc: 'Light suggestions, preserve your voice',
  moderate: 'Moderate',
  moderateDesc: 'Balanced—improve without overstepping',
  creative: 'Creative',
  creativeDesc: 'More freedom to reimagine',
} as const;

// --- Empty states & prompts ---

export const AI_EMPTY_COPY = {
  selectTextToStart: 'Select text to get started.',
  orAskAnything: 'Or ask anything—describe what you need.',
  noSelection: 'Select some text, or describe what you\'d like help with.',
  tryAction: 'Try an action above, or type a custom request.',
} as const;

// --- Make this clearer (alias for improve_wording / clarify) ---

export const AI_CLARIFY_COPY = {
  makeClearer: 'Make this clearer',
  clarify: 'Clarify',
} as const;

// --- Helper: get action label with fallback ---

export function getActionLabel(actionId: string): string {
  return AI_ACTION_LABELS[actionId] ?? actionId.replace(/_/g, ' ');
}

export function getActionDescription(actionId: string): string | undefined {
  return AI_ACTION_DESCRIPTIONS[actionId];
}
