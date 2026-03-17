/**
 * Polished user-facing copy for AUTHORA's Story Density Engine.
 *
 * Tone: premium, supportive, calm, practical, clear, writer-friendly, non-judgmental.
 * Focused on helping writers tighten or strengthen their work with confidence.
 */

// --- Main panel ---

export const DENSITY_HEADING = {
  title: 'Density Check',
  subheading:
    'See what may be slowing the manuscript down — or where it needs more support.',
  intro:
    'Authora helps you spot filler, repetition, drag, and thin moments so you can tighten or strengthen the work with confidence.',
} as const;

// --- Tab labels ---

export const DENSITY_TABS = {
  issues: 'Issues',
  purpose: 'Purpose',
  drag: 'Chapter drag',
  repetition: 'Repetition',
} as const;

// --- Issue labels (display labels for issue types) ---

export const DENSITY_ISSUE_LABELS: Record<string, string> = {
  // Repetition
  repetition_in_chapter: 'Repetition warning',
  repeated_concepts: 'Repetition warning',
  repeated_emotional_beat: 'Repetition warning',
  repeated_reflection: 'Repetition warning',
  repetition: 'Repetition warning',

  // Drag & bloat
  possible_bloat: 'This chapter may be carrying too much weight',
  exposition_overload: 'This section may be over-explaining',
  excessive_explanation: 'This section may be over-explaining',
  emotional_over_explanation: 'This section may be over-explaining',
  bloated_intro_or_outro: 'This chapter may be carrying too much weight',
  bloated_scene: 'This chapter may be carrying too much weight',
  over_explanation: 'This section may be over-explaining',
  drag: 'Chapter drag',

  // Thin / weak support
  thin_section: 'Needs strengthening',
  thin_transition: 'Transition feels thin',
  weak_transition: 'Transition feels thin',
  weak_midpoint: 'This moment may need more support',
  thin_support: 'Thin support',
  rushed_moment: 'This moment may need more support',
  underweighted_payoff: 'This moment may need more support',
  missing_example: 'This moment may need more support',
  missing_exercise: 'This moment may need more support',
  practical_support_gap: 'This moment may need more support',

  // Purpose & structure
  unclear_purpose: 'Scene may lack clear purpose',
  instructional_redundancy: 'This section may be better merged',
};

// --- Supportive explanations (fallback when API description is null) ---

export const DENSITY_EXPLANATIONS: Record<string, string> = {
  repetition_in_chapter:
    'This section appears to repeat an earlier beat without much new movement.',
  repeated_concepts:
    'This section appears to repeat an earlier beat without much new movement.',
  repeated_emotional_beat:
    'This section appears to repeat an earlier beat without much new movement.',
  repeated_reflection:
    'This section appears to repeat an earlier beat without much new movement.',
  possible_bloat:
    'This chapter may be doing less than its size suggests.',
  exposition_overload:
    'This passage may be stronger if compressed.',
  excessive_explanation:
    'This passage may be stronger if compressed.',
  emotional_over_explanation:
    'This passage may be stronger if compressed.',
  bloated_intro_or_outro:
    'This chapter may be doing less than its size suggests.',
  thin_section:
    'This moment may need more buildup to land fully.',
  thin_transition:
    'This section may benefit from one bridging beat rather than a full rewrite.',
  weak_transition:
    'This section may benefit from one bridging beat rather than a full rewrite.',
  weak_midpoint:
    'This moment may need more buildup to land fully.',
  missing_example:
    'This moment may need more support.',
  missing_exercise:
    'This moment may need more support.',
  instructional_redundancy:
    'This section may be better merged.',
};

// --- Action labels (for fix suggestions and buttons) ---

export const DENSITY_ACTION_LABELS: Record<string, string> = {
  trim: 'Trim options',
  compress: 'Trim options',
  strengthen: 'Strengthen options',
  expand: 'Strengthen options',
  bridge: 'Strengthen options',
  clarify: 'Strengthen options',
  merge: 'Trim options',
  keep_as_intentional: 'Mark as intentional',
  mark_intentional: 'Mark as intentional',
};

// --- Button / action copy ---

export const DENSITY_ACTIONS = {
  reviewDensityIssue: 'Review density issue',
  showRelatedSections: 'Show related sections',
  trimOptions: 'Trim options',
  strengthenOptions: 'Strengthen options',
  createRevisionTask: 'Create revision task',
  markAsIntentional: 'Mark as intentional',
  resolveLater: 'Resolve later',
  ignoreForNow: 'Ignore for now',
  goToChapter: 'Go to chapter',
  goShort: 'Go',
  goToFirstChapter: 'Go to first chapter',
  scan: 'Density Check',
  scanning: 'Checking…',
  lastScan: 'Last check',
  fromScan: 'From check',
} as const;

// --- Density summary labels (for manuscript health) ---

export const DENSITY_SUMMARY_LABELS: Record<string, string> = {
  tight_and_strong: 'Tight and strong',
  few_trim: 'A few sections may need trimming',
  need_support: 'Several areas may need support',
  could_be_tighter: 'Manuscript could be tighter',
  good_structure_uneven: 'Good structure, uneven density',
  nearly_ready: 'Nearly ready',
};

// --- Severity display (softer, non-judgmental) ---

export const DENSITY_SEVERITY_LABELS: Record<string, string> = {
  critical: 'Needs attention',
  high: 'Worth reviewing',
  moderate: 'Worth reviewing',
  low: 'Optional review',
};

// --- Density summary (derived from health) ---

export function getDensitySummaryLabel(
  openCount: number,
  manuscriptScore: number | null
): string {
  if (openCount === 0) {
    return manuscriptScore != null && manuscriptScore >= 75
      ? DENSITY_SUMMARY_LABELS.tight_and_strong
      : DENSITY_SUMMARY_LABELS.nearly_ready;
  }
  if (openCount <= 3) {
    return manuscriptScore != null && manuscriptScore >= 60
      ? DENSITY_SUMMARY_LABELS.good_structure_uneven
      : DENSITY_SUMMARY_LABELS.few_trim;
  }
  if (openCount <= 8) {
    const hasSupport = true; // Could derive from by_category if needed
    return hasSupport ? DENSITY_SUMMARY_LABELS.need_support : DENSITY_SUMMARY_LABELS.could_be_tighter;
  }
  return DENSITY_SUMMARY_LABELS.could_be_tighter;
}

// --- Purpose board ---

export const DENSITY_PURPOSE = {
  heading: 'Chapter density',
  subheading: 'What each chapter is doing — and where purpose may be unclear.',
  empty: 'Run a Density Check to see chapter purpose analysis.',
  purposeClarity: 'Purpose clarity',
  goToChapter: 'Go to chapter',
} as const;

// --- Chapter drag panel ---

export const DENSITY_DRAG = {
  heading: 'Chapter drag',
  subheading: 'Chapters that may be doing less than their size suggests.',
  empty: 'Run a Density Check to see chapter drag analysis.',
  consecutiveDrag: 'Consecutive drag',
  mergeCandidates: 'Merge candidates',
  allChapters: 'All chapters',
  dragging: 'Likely compressible',
  ok: 'Strongly weighted',
  goToChapter: 'Go to chapter',
  goToFirstChapter: 'Go to first chapter',
} as const;

// --- Repetition heat panel ---

export const DENSITY_REPETITION = {
  heading: 'Repetition',
  subheading: 'Where the manuscript may be repeating itself.',
  empty: 'Run a Density Check to see repetition heat.',
  manuscriptScore: 'Manuscript repetition',
  perChapterHeat: 'Per-chapter heat',
  heatHint: 'Darker = more repetition. Click to go to chapter.',
  heatLevels: {
    low: 'Low',
    moderate: 'Repetition warning',
    high: 'Repetition warning',
    very_high: 'Strong repetition warning',
  } as Record<string, string>,
  repeatedPhrases: 'Repeated phrases',
  goToChapter: 'Go',
} as const;

// --- Chapter summary (when chapter selected) ---

export const DENSITY_CHAPTER_SUMMARY = {
  heading: 'This chapter',
  whatDoing: 'What it\'s doing',
  dragging: 'Chapter drag',
  repetition: 'Repetition',
} as const;

// --- Issues list ---

export const DENSITY_ISSUES = {
  heading: 'Density issues',
  subheading:
    'Trim clutter, compress repetition, strengthen thin spots. Each item is a suggestion — you decide what serves the story.',
  empty:
    'Run a Density Check to detect filler, repetition, drag, and thin moments.',
  noIssues: 'No density issues',
  issuesToReview: (n: number) =>
    `${n} issue${n === 1 ? '' : 's'} to review`,
  densityScore: 'Manuscript density',
  loading: 'Loading Density Check…',
} as const;

// --- Toast messages ---

export const DENSITY_TOAST = {
  scanComplete: 'Density Check complete',
  scanCompleteDesc: 'Manuscript density updated.',
  scanFailed: 'Check failed',
  updateFailed: 'Failed to update',
} as const;
