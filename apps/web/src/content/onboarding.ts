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
    subtitle: 'From idea to finished book—we\'ll walk beside you',
    description:
      "A few quick questions so we can tailor things to you. Nothing's set in stone—you can change any of this later.",
  },
  book_type: {
    title: 'What are you writing?',
    description: 'We\'ll show you the tools and structure that fit your project best.',
    fiction_label: 'Fiction',
    fiction_desc: 'Novels, stories, creative writing',
    nonfiction_label: 'Non-fiction',
    nonfiction_desc: 'Memoir, how-to, business, academic',
  },
  writing_mode: {
    title: 'How would you like to write?',
    description: 'Pick what feels right. You can always adjust this later.',
    solo_label: 'Mostly on my own',
    solo_desc: 'I write; AI helps only when I ask',
    cowrite_label: 'Co-write with AI',
    cowrite_desc: 'AI suggests and drafts; I steer and refine',
    ghostwriter_label: 'More AI assistance',
    ghostwriter_desc: 'AI drafts; I guide and polish',
  },
  writing_goals: {
    title: 'What matters most to you?',
    placeholder:
      'e.g. Finish my first draft, publish by summer, build a daily habit...',
  },
  target_timeline: {
    title: 'When do you hope to finish?',
    description:
      'No pressure—this just helps us suggest a gentle pace. You can change it anytime.',
  },
  writing_schedule: {
    title: 'When do you usually write?',
    description: "We'll use this for friendly reminders—only if you'd like them.",
  },
  accountability: {
    title: 'How do you like to be encouraged?',
    description: 'We match your style. No guilt, ever—just support when you need it.',
    gentle_label: 'Gentle',
    gentle_desc: 'Soft nudges, no pressure',
    structured_label: 'Structured',
    structured_desc: 'Clear goals and check-ins',
    buddy_label: 'Buddy',
    buddy_desc: 'Community and encouragement',
  },
  ai_comfort: {
    title: 'How much AI help feels right?',
    description: 'You\'re in control—change this anytime in settings.',
    minimal_label: 'Minimal',
    minimal_desc: 'Only when I ask',
    moderate_label: 'Moderate',
    moderate_desc: 'Suggestions and prompts when helpful',
    full_label: 'Full',
    full_desc: 'Drafting, rewriting, expansion—I guide',
  },
  genre: {
    title: 'Genre or topic',
    placeholder: 'e.g. Romance, thriller, memoir, business',
  },
  complete: {
    title: "You're all set",
    subtitle: 'Your journey begins now',
    description:
      "Create a project and add your first book. We'll walk you through each step—take your time.",
    cta: 'Create your first project',
  },
};

export function getOnboardingCopy(step: string): OnboardingStepCopy | undefined {
  return ONBOARDING_COPY[step];
}
