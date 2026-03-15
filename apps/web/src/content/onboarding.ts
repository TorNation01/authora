/** Onboarding copy for the setup flow. */

export interface OnboardingStepCopy {
  title: string;
  description?: string;
  subtitle?: string;
  placeholder?: string;
  [key: string]: string | undefined;
}

export const ONBOARDING_COPY: Record<string, OnboardingStepCopy> = {
  welcome: {
    title: 'Welcome to AUTHORA',
    subtitle: 'Your guided writing journey from idea to finished book',
    description:
      "We'll ask a few questions to personalize your experience. You can change these anytime.",
  },
  book_type: {
    title: 'Fiction or non-fiction?',
    description: 'This helps us suggest the right structure and tools.',
    fiction_label: 'Fiction',
    fiction_desc: 'Novels, stories, creative writing',
    nonfiction_label: 'Non-fiction',
    nonfiction_desc: 'Memoir, how-to, business, academic',
  },
  writing_mode: {
    title: 'How do you want to write?',
    description: 'Choose the level of AI assistance that feels right.',
    solo_label: 'Write myself',
    solo_desc: 'I write alone, AI assists when I ask',
    cowrite_label: 'Co-write with AI',
    cowrite_desc: 'AI suggests and drafts, I edit and steer',
    ghostwriter_label: 'Ghostwriter mode',
    ghostwriter_desc: 'AI drafts heavily, I guide and refine',
  },
  writing_goals: {
    title: 'What are your writing goals?',
    placeholder:
      'e.g. finish my first draft, publish by next year, build a daily habit',
  },
  target_timeline: {
    title: 'Target completion',
    description:
      'When do you hope to finish? No pressure—you can change this.',
  },
  writing_schedule: {
    title: 'When do you usually write?',
    description: "We'll use this for gentle reminders if you want them.",
  },
  accountability: {
    title: 'Encouragement style',
    description: 'How do you like to be nudged?',
    gentle_label: 'Gentle',
    gentle_desc: 'Soft reminders, no pressure',
    structured_label: 'Structured',
    structured_desc: 'Clear goals and check-ins',
    buddy_label: 'Buddy',
    buddy_desc: 'Community and encouragement',
  },
  ai_comfort: {
    title: 'How much AI help do you want?',
    description: 'You can change this anytime in settings.',
    minimal_label: 'Minimal',
    minimal_desc: 'Only when I ask',
    moderate_label: 'Moderate',
    moderate_desc: 'Suggestions and prompts',
    full_label: 'Full',
    full_desc: 'AI drafting, rewriting, expansion',
  },
  genre: {
    title: 'Genre or topic',
    placeholder: 'e.g. romance, thriller, memoir, business',
  },
  complete: {
    title: "You're all set",
    subtitle: 'Your journey starts now',
    description:
      "Create a project and add your first book. We'll guide you through each step.",
    cta: 'Create your first project',
  },
};

export function getOnboardingCopy(step: string): OnboardingStepCopy | undefined {
  return ONBOARDING_COPY[step];
}
