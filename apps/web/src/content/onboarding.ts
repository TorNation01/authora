/** Onboarding copy for the setup flow. Warm, low-pressure, clear. */

export interface OnboardingStepCopy {
  title: string;
  description?: string;
  subtitle?: string;
  placeholder?: string;
  [key: string]: string | undefined;
}

export const ONBOARDING_COPY: Record<string, OnboardingStepCopy> = {
  welcome: {
    title: 'Welcome to your writing sanctuary',
    subtitle: 'From idea to finished book—we\'ll guide you every step',
    description:
      "We'll ask a few quick questions to personalize your experience. You can change these anytime.",
  },
  book_type: {
    title: 'What are you writing?',
    description: 'This helps us show you the right tools and structure.',
    fiction_label: 'Fiction',
    fiction_desc: 'Novels, stories, creative writing',
    nonfiction_label: 'Non-fiction',
    nonfiction_desc: 'Memoir, how-to, business, academic',
  },
  writing_mode: {
    title: 'How would you like to write?',
    description: 'Choose the level of AI help that feels right. You can change this anytime.',
    solo_label: 'Mostly on my own',
    solo_desc: 'I write; AI helps when I ask',
    cowrite_label: 'Co-write with AI',
    cowrite_desc: 'AI suggests and drafts; I edit and steer',
    ghostwriter_label: 'Heavy AI assistance',
    ghostwriter_desc: 'AI drafts; I guide and refine',
  },
  writing_goals: {
    title: 'What matters most to you?',
    placeholder:
      'e.g. finish my first draft, publish by next year, build a daily habit',
  },
  target_timeline: {
    title: 'When do you hope to finish?',
    description:
      'No pressure—this helps us suggest a pace. You can change it anytime.',
  },
  writing_schedule: {
    title: 'When do you usually write?',
    description: "We'll use this for gentle reminders—only if you want them.",
  },
  accountability: {
    title: 'How do you like to be encouraged?',
    description: 'We adapt to your style. No guilt, ever.',
    gentle_label: 'Gentle',
    gentle_desc: 'Soft nudges, no pressure',
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
    full_desc: 'Drafting, rewriting, expansion',
  },
  genre: {
    title: 'Genre or topic',
    placeholder: 'e.g. romance, thriller, memoir, business',
  },
  complete: {
    title: "You're all set",
    subtitle: 'Your journey begins now',
    description:
      "Create a project and add your first book. We'll walk you through each step—no rush.",
    cta: 'Create your first project',
  },
};

export function getOnboardingCopy(step: string): OnboardingStepCopy | undefined {
  return ONBOARDING_COPY[step];
}
