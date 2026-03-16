/**
 * Production-ready onboarding copy for AUTHORA.
 * Tone: premium, clear, inspiring, supportive, intelligent.
 * Not academic unless needed. Not childish.
 */

// --- Welcome ---

export const ONBOARDING_WELCOME = {
  title: 'Welcome to AUTHORA',
  subtitle: 'Your writing sanctuary',
  description:
    "We'll help you go from idea to finished book. A few quick questions so we can tailor the experience—nothing's set in stone.",
  cta: "Let's begin",
} as const;

// --- Writer type pathing ---

export const WRITER_TYPES = {
  heading: 'What kind of writer are you?',
  subheading: 'This helps us suggest the right tools and structure. You can change it anytime.',
  firstTime: {
    id: 'first_time',
    label: 'First-time writer',
    desc: "I'm writing my first book and want guidance.",
  },
  experienced: {
    id: 'experienced',
    label: 'Experienced author',
    desc: "I've written before and know my process.",
  },
  fiction: {
    id: 'fiction',
    label: 'Fiction writer',
    desc: 'Novels, stories, creative writing.',
  },
  nonfiction: {
    id: 'nonfiction',
    label: 'Non-fiction writer',
    desc: 'Memoir, how-to, business, academic.',
  },
  memoir: {
    id: 'memoir',
    label: 'Memoir writer',
    desc: 'Shaping lived experience into story.',
  },
  workbook: {
    id: 'workbook',
    label: 'Workbook / guided journal creator',
    desc: 'Prompts, exercises, action-oriented structure.',
  },
  ghostwriter: {
    id: 'ghostwriter',
    label: 'Ghostwriter',
    desc: "Capturing a client's voice and message.",
  },
  collaborative: {
    id: 'collaborative',
    label: 'Collaborative writing',
    desc: 'Co-writing with others or AI.',
  },
  notSure: {
    id: 'not_sure',
    label: "I'm not sure yet",
    desc: 'Show me the options and I\'ll explore.',
  },
} as const;

// --- What do you want to write? ---

export const PROJECT_TYPE_STEP = {
  heading: 'What do you want to write?',
  subheading: 'We\'ll show you the right tools and structure.',
  fiction: 'Fiction',
  fictionDesc: 'Novels, stories, creative writing',
  nonfiction: 'Non-fiction',
  nonfictionDesc: 'Memoir, how-to, business, academic',
} as const;

// --- Guidance mode ---

export const GUIDANCE_STEP = {
  heading: 'How much guidance do you want?',
  subheading: 'Structure is here to help, not trap you. You can change this later.',
  noneWrong: 'None of these options are wrong.',
  guided: {
    label: 'Guided',
    desc: 'Clear structure. Strong momentum. Let AUTHORA guide the path while you shape the voice.',
  },
  flexible: {
    label: 'Flexible',
    desc: 'A little structure, without the squeeze. Keep guidance where it helps.',
  },
  freeform: {
    label: 'Freeform',
    desc: 'Write your way. Keep the tools. Lose the rails.',
  },
} as const;

// --- How do you like to work? ---

export const WORK_STYLE_STEP = {
  heading: 'How do you like to work?',
  subheading: 'Pick what feels right. You can always adjust this later.',
  solo: {
    label: 'Mostly on my own',
    desc: 'I write; AI helps only when I ask.',
  },
  cowrite: {
    label: 'Co-write with AI',
    desc: 'AI suggests and drafts; I steer and refine.',
  },
  ghostwriter: {
    label: 'Heavy AI assistance',
    desc: 'AI drafts; I guide and polish.',
  },
} as const;

// --- Writing pace ---

export const PACE_STEP = {
  heading: 'Set your writing pace',
  subheading: 'No pressure—this helps us suggest gentle reminders and goals. You can skip or change anytime.',
  timeline: 'When do you hope to finish?',
  schedule: 'When do you usually write?',
  accountability: 'How do you like to be encouraged?',
  gentle: 'Gentle',
  gentleDesc: 'Soft nudges, no pressure',
  structured: 'Structured',
  structuredDesc: 'Clear goals and check-ins',
  buddy: 'Buddy',
  buddyDesc: 'Community and encouragement',
  none: 'No accountability',
  noneDesc: 'I prefer to work without reminders',
} as const;

// --- Create first project ---

export const CREATE_PROJECT_STEP = {
  heading: 'Create your first project',
  subheading: "We'll walk you through naming your book and choosing a starting point.",
  cta: 'Create project',
  skip: 'I\'ll do this later',
} as const;

// --- Complete / Start writing ---

export const COMPLETE_STEP = {
  heading: "You're all set",
  subtitle: 'Your journey begins now',
  description: "Create a project and add your first book. We'll walk you through each step—take your time.",
  cta: 'Create your first project',
  explore: 'Explore workspace',
  startWriting: 'Start writing',
} as const;

// --- First-book journey phases ---

export const FIRST_BOOK_JOURNEY = {
  heading: 'Your first book journey',
  subheading: 'A guided path from idea to finished manuscript.',
  phases: {
    define: 'Define the book',
    structure: 'Build the structure',
    opening: 'Write the opening',
    moving: 'Keep the draft moving',
    midpoint: 'Reach the midpoint',
    finish: 'Finish the draft',
    revise: 'Revise with purpose',
    export: 'Prepare for export',
  },
} as const;

// --- Returning user quick-start ---

export const QUICK_START_OPTIONS = {
  continueWriting: 'Continue writing',
  resumeChapter: 'Resume current chapter',
  todaysGoal: "Review today's goal",
  focusMode: 'Enter Focus Mode',
  pickUpWhereLeftOff: 'Pick up where you left off',
  openNotes: 'Open notes & research',
  continueRevision: 'Continue revision',
  exportManuscript: 'Export manuscript',
  newProject: 'Start a new project',
} as const;

// --- Skip / Resume ---

export const ONBOARDING_SKIP = {
  skip: 'Skip for now',
  resume: 'Resume setup',
  setupComplete: 'Setup complete',
  setupIncomplete: 'Complete your setup',
} as const;
