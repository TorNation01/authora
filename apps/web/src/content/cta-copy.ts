/**
 * AUTHORA CTA system — centralized labels, routes, and microcopy.
 * Use for consistent conversion flow across homepage, features, pricing, footer.
 */

export type PrimaryCTALabel =
  | 'Start Writing Free'
  | 'Start Free'
  | 'Create Your First Book';

export type SecondaryCTALabel =
  | 'See How It Works'
  | 'View Pricing'
  | 'View Full Pricing'
  | 'Explore Features'
  | 'Compare Plans';

export const CTA_ROUTES = {
  register: (baseUrl: string) => `${baseUrl}/register`,
  login: (baseUrl: string) => `${baseUrl}/login`,
  pricing: '/pricing',
  pricingCompare: '/pricing#compare-plans',
  features: '/features',
  howItWorks: '#how-it-works',
  faq: '/faq',
} as const;

/** Trust microcopy near CTAs — low-friction, value reinforcement */
export const CTA_MICROCOPY = {
  hero: 'No clutter. No guesswork. Just a clear path to a finished book.',
  heroAlt: 'Start writing in under a minute.',
  ctaSection: 'Stop circling the idea. Start finishing the book.',
  ctaSectionAlt: 'Begin with one project for free.',
  pricingTeaser: 'Upgrade when you\'re ready.',
  pricingTeaserAlt: 'No credit card required. Full access to the free tier.',
  pricing: 'Upgrade anytime as your writing grows. No credit card required for Free.',
  pricingFinal: 'Join writers who are actually finishing their books.',
  faqClose: 'Still have questions? Start free and explore.',
  footer: 'No clutter. No guesswork. Just a clear path forward.',
} as const;

/** Trust badges near conversion points */
export const CTA_TRUST_BADGES = [
  'Free forever tier',
  'No credit card',
  'Cancel anytime',
] as const;
