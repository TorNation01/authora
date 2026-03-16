/**
 * Polished user-facing microcopy for AUTHORA's editor, manuscript workspace,
 * revision mode, notes, comments, highlights, and focus mode.
 *
 * Tone: premium, supportive, calm, clear, polished, motivating.
 * Never noisy, never childish.
 */

// --- Editor ---

export const EDITOR_COPY = {
  placeholder: 'Start where the words are ready.',
  keepDraftMoving: 'Keep the draft moving.',
  sectionYoursToShape: 'This section is yours to shape.',
  writeFirstRefineAfter: 'Write first. Refine after.',
  emptyChapter: 'Begin here.',
  emptyEditor: 'Choose a chapter to start writing.',
} as const;

// --- Autosave ---

export const AUTOSAVE_COPY = {
  saving: 'Saving…',
  saved: 'Saved',
  allChangesSaved: 'All changes saved',
  lastSavedJustNow: 'Last saved just now',
  unsavedChanges: 'Unsaved changes',
  saveFailed: 'Save failed',
  retry: 'Retry',
} as const;

// --- Chapter actions ---

export const CHAPTER_ACTIONS_COPY = {
  addChapter: 'Add chapter',
  addSection: 'Add section',
  rename: 'Rename',
  duplicate: 'Duplicate',
  archive: 'Archive',
  reorder: 'Reorder',
  markAsDrafting: 'Mark as drafting',
  markAsRevising: 'Mark as revising',
  markAsFinished: 'Mark as finished',
} as const;

// --- Notes ---

export const NOTES_COPY = {
  addNote: 'Add note',
  leaveMarker: 'Leave yourself a marker',
  returnLater: 'Return to this later',
  keepThoughtClose: 'Keep the thought close',
  addPrivateNote: 'Add a private note',
} as const;

// --- Comments ---

export const COMMENTS_COPY = {
  addComment: 'Add comment',
  resolve: 'Resolve',
  reopen: 'Reopen',
  needsAttention: 'Needs attention',
  reviewed: 'Reviewed',
} as const;

// --- Highlights ---

export const HIGHLIGHTS_COPY = {
  markForRevision: 'Mark for revision',
  highlightKeyMoment: 'Highlight key moment',
  flagForRewrite: 'Flag for rewrite',
  checkContinuity: 'Check continuity',
  needsStrongerWording: 'Needs stronger wording',
} as const;

// --- Revision pass types ---

export const REVISION_PASS_TYPES = [
  { value: 'structural', label: 'Structural pass' },
  { value: 'clarity', label: 'Clarity pass' },
  { value: 'pacing', label: 'Pacing pass' },
  { value: 'emotional_depth', label: 'Emotional depth pass' },
  { value: 'consistency', label: 'Consistency pass' },
  { value: 'grammar_polish', label: 'Grammar and polish pass' },
  { value: 'custom', label: 'Custom pass' },
] as const;

// --- Revision mode ---

export const REVISION_MODE_COPY = {
  heading: 'Revision Mode',
  subheading: 'Review the draft with fresh eyes',
  workThroughIssues: 'Work through the manuscript one issue at a time',
  resolveAndMove: 'Resolve what matters and keep moving',
  trackAttention: 'Track what still needs attention',
  revisionQueue: 'Revision queue',
  unresolvedOnly: 'Unresolved only',
  noRevisionNotes: 'No revision notes. Add comments as you read through your draft.',
} as const;

// --- Focus mode ---

export const FOCUS_MODE_COPY = {
  heading: 'Focus Mode',
  subheading: 'Clear the noise',
  stayWithPage: 'Stay with the page',
  keepWriting: 'Keep writing',
  oneSectionAtATime: 'One section at a time',
  exit: 'Exit',
  justYouAndPage: 'Just you and the page',
} as const;

// --- Split views ---

export const SPLIT_VIEWS_COPY = {
  showNotes: 'Show notes',
  showAiAssist: 'Show AI assist',
  showOutline: 'Show outline',
  showProgress: 'Show progress',
  showRevisionQueue: 'Show revision queue',
} as const;

// --- Search ---

export const SEARCH_COPY = {
  findInSection: 'Find in section',
  findInChapter: 'Find in chapter',
  searchManuscript: 'Search manuscript',
  replaceCarefully: 'Replace carefully',
  searchNotesAndComments: 'Search notes and comments',
  currentChapter: 'Current chapter',
  wholeManuscript: 'Whole manuscript',
  matchesInManuscript: 'Matches in manuscript',
} as const;

// --- Stats ---

export const STATS_COPY = {
  wordsToday: 'Words today',
  thisSession: 'This session',
  chapterTotal: 'Chapter total',
  manuscriptTotal: 'Manuscript total',
  progressThisWeek: 'Progress this week',
} as const;

// --- AI tools ---

export const AI_TOOLS_COPY = {
  improveFlow: 'Improve flow',
  rewrite: 'Rewrite',
  expand: 'Expand',
  shorten: 'Shorten',
  clarify: 'Clarify',
  continueWriting: 'Continue writing',
  generateAlternatives: 'Generate alternatives',
  helpUnstuck: 'Help me get unstuck',
} as const;
