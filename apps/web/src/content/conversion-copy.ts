/**
 * AUTHORA conversion copy.
 * Helpful tone, not pushy, focused on benefit.
 */

export type UpgradeTrigger =
  | 'usage_limit'
  | 'momentum'
  | 'stuck'
  | 'near_completion'
  | 'feature_locked';

export const CONVERSION_COPY: Record<
  UpgradeTrigger,
  { title: string; description: string; benefit: string; cta: string }
> = {
  usage_limit: {
    title: 'You\'re making progress',
    description: 'You\'ve hit the limit for your current plan. More projects and books are waiting—upgrade to keep building.',
    benefit: 'Write as many books as you need, with stronger AI support and tools built to help you finish.',
    cta: 'View plans',
  },
  momentum: {
    title: 'You\'re on a roll',
    description: 'Your writing streak and progress show real momentum. Pro gives you more room to grow—more AI, more tools, more books.',
    benefit: 'Finish Mode, Story Integrity Engine, and ghostwriter tools help you cross the finish line.',
    cta: 'See what\'s included',
  },
  stuck: {
    title: 'A little help when you need it',
    description: 'Every writer gets stuck sometimes. Pro includes stronger AI support and ghostwriter tools to help you move forward.',
    benefit: 'Get unstuck with AI that understands your story and helps you keep going.',
    cta: 'Explore Pro',
  },
  near_completion: {
    title: 'You\'re so close',
    description: 'You\'re near the finish line. Finish Mode and our manuscript tools are built to help you cross it.',
    benefit: 'Tighten prose, spot gaps, and polish—tools designed for writers finishing books.',
    cta: 'Unlock Finish Mode',
  },
  feature_locked: {
    title: 'This feature is on Pro',
    description: 'Upgrade to Pro to use this feature. We built it to help writers like you finish books.',
    benefit: 'More AI support, Finish Mode, Story Integrity Engine, and collaboration tools.',
    cta: 'View plans',
  },
};

export const FEATURE_LABELS: Record<string, string> = {
  ghostwriter: 'Ghostwriter',
  finish_mode: 'Finish Mode',
  story_integrity: 'Story Integrity Engine',
  story_density: 'Story Density Engine',
  citation_system: 'Citation & Reference Engine',
  bibliography: 'Bibliography tools',
  collaboration: 'Collaboration',
  ai: 'AI assistance',
};
