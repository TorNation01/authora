/**
 * User-facing copy for the AUTHORA project template selection experience.
 */

export const TEMPLATE_LIBRARY = {
  heading: 'Start your book with a clearer path',
  subheading:
    'Choose a template that matches the kind of book you want to write, then let Authora guide you into a strong starting structure.',
} as const;

export const START_OPTIONS = {
  startFast: {
    label: 'Start fast',
    description:
      'Choose a template, name your project, and begin with a ready-to-use workspace.',
  },
  guidedSetup: {
    label: 'Guided setup',
    description:
      'Answer a few simple questions and let Authora shape the structure around your book.',
  },
} as const;

export const CUSTOM_PROJECT = {
  label: 'Blank project',
  description:
    'Start from scratch with a clean manuscript and build your own structure your way.',
} as const;

export const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  // Fiction
  fiction: 'Build stories with structure, character, tension, and momentum.',
  // Non-Fiction
  nonfiction:
    'Turn your expertise, ideas, or message into a clear and compelling book.',
  memoir: 'Shape lived experience into a story with meaning, emotion, and reflection.',
  // Hybrid / Creative
  hybrid_creative:
    'Blend fact with literary craft. Narrative nonfiction, creative nonfiction, and essay collections.',
  // Business / Authority (nonfiction sub-types)
  workbook:
    'Create guided content with prompts, exercises, and action-oriented structure.',
  journal:
    'Design reflective writing experiences with prompts, rhythms, and themes.',
  poetry: 'Organize a collection with flow, sequence, and emotional shape.',
  short_story_collection:
    'Build a cohesive set of stories with shared themes and strong structure.',
  series_project:
    'Plan connected books with continuity, lore, and long-form story arcs.',
  ghostwritten_book:
    "Capture a client's message, voice, and source material in a structured writing flow.",
  custom: CUSTOM_PROJECT.description,
  // New categories
  ai_templates:
    'AI-assisted writing from idea to draft. Generate outlines, expand content, and refine with AI.',
  accountability:
    'Daily and weekly check-ins to track progress, reflect, and build writing habit.',
  business:
    'Course books, lead magnets, and business content that teaches and converts.',
};

export const MICROCOPY = {
  adjustLater: 'You can always adjust this later.',
  startSimple: 'Start simple now and refine as you go.',
  momentum: 'The goal is not perfection. The goal is momentum.',
  strongStart: 'A strong start makes the writing easier.',
  keepMoving: 'Choose the path that helps you keep moving.',
} as const;

export const GUIDANCE_MODES = {
  heading: 'Choose your guidance level',
  subheading: 'Structure is here to support your process, not limit it.',
  changeLater: 'You can change this later.',
  chooseAmount: 'Choose the amount of guidance that helps you write best.',
  guided: {
    label: 'Guided',
    description: 'Clear structure. Strong momentum. Let Authora guide the path while you shape the voice.',
    badge: 'Full guidance',
    supportNotCage: 'Use the framework as support, not a cage.',
  },
  flexible: {
    label: 'Flexible',
    description: 'A little structure, without the squeeze. Keep guidance where it helps.',
    badge: 'Flexible',
    evolveAsYouWrite: 'Let the project evolve as you write.',
  },
  freeform: {
    label: 'Freeform',
    description: 'Write your way. Keep the tools. Lose the rails.',
    badge: 'Freeform',
    railsCopy: 'Freeform mode keeps the tools, without the genre rails.',
    processFlexible: 'Your process can stay flexible.',
    structureOptional: 'Structure is optional here.',
  },
} as const;
