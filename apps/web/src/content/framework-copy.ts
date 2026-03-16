/**
 * User-facing copy for AUTHORA's framework selection and framework-guided writing experience.
 */

// --- Framework selection ---

export const FRAMEWORK_SELECTION = {
  heading: 'Choose a structure that helps you keep moving',
  subheading:
    'Authora can guide your project with a proven writing framework, or you can keep things flexible and shape your own path.',
} as const;

export const FRAMEWORK_SUPPORTIVE_COPY = [
  'You can change this later.',
  'A good framework gives your writing momentum.',
  'Structure is here to support your creativity, not limit it.',
  'Start with guidance, then make it your own.',
  'The best framework is the one that helps you finish.',
] as const;

// --- Fiction framework descriptions ---

export const FICTION_FRAMEWORK_DESCRIPTIONS: Record<string, string> = {
  three_act:
    'A classic story shape that helps you build momentum, conflict, and resolution clearly.',
  hero_journey:
    'A powerful framework for transformation-driven stories, quests, and high-stakes character arcs.',
  romance_beats:
    'A relationship-focused framework built to support chemistry, conflict, emotional payoff, and satisfying resolution.',
  mystery_thriller:
    'A tension-driven framework built around clues, reversals, reveals, and escalating stakes.',
  series_arc:
    'A long-form structure for connected books, recurring characters, and bigger story payoffs over time.',
  character_driven:
    'A looser framework focused on emotional movement, internal conflict, and thematic depth.',
  save_the_cat:
    'A commercial beat structure with 15 clear story beats for screenplays and genre novels.',
  custom_fiction:
    'Build your own structure. Minimal scaffolding for experienced writers.',
};

// --- Non-fiction framework descriptions ---

export const NONFICTION_FRAMEWORK_DESCRIPTIONS: Record<string, string> = {
  problem_solution_result:
    'Great for books that help readers understand a challenge and move toward a clear outcome.',
  step_by_step:
    'Ideal for books that guide readers through a journey from where they are to where they want to be.',
  authority:
    'Perfect for experts, professionals, and founders who want to teach, persuade, and build trust.',
  instructional:
    'A clear structure for books that explain ideas, guide learning, and reinforce understanding.',
  workbook:
    'Built for interactive books with prompts, exercises, reflection, and practical steps.',
  memoir_lesson:
    'A reflective structure that combines personal story with meaning, insight, and takeaway.',
  modular:
    'A flexible structure for books made of standalone but connected chapters or themes.',
  custom_nonfiction:
    'Build your own structure. Minimal scaffolding for experienced writers.',
};

// --- Combined lookup (slug -> description) ---

export const FRAMEWORK_DESCRIPTIONS: Record<string, string> = {
  ...FICTION_FRAMEWORK_DESCRIPTIONS,
  ...NONFICTION_FRAMEWORK_DESCRIPTIONS,
};

// --- Editor / sidebar copy ---

export const FRAMEWORK_EDITOR_COPY = {
  currentFrameworkStage: 'Current framework stage',
  youAreHere: 'You are here',
  nextSuggestedStep: 'Next suggested step',
  missingKeySection: 'Missing key section',
  onTrack: 'On track',
  needsAttention: 'Needs attention',
  keepMoving: 'Keep moving',
  finishThisStage: 'Finish this stage',
} as const;

// --- Finish Mode copy ---

export const FINISH_MODE_COPY = {
  imperfectProgress:
    'You do not need perfect. You need progress.',
  completeThenMove:
    'Complete this stage, then move forward.',
  oneFinishedBeatsTen:
    'One finished section beats ten unfinished ideas.',
  momentumCreatesBooks:
    'Momentum creates books.',
} as const;
