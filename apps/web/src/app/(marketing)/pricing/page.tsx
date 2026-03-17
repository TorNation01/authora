import type { Metadata } from 'next';
import { PricingHero } from './PricingHero';
import { PricingPlanCards } from './PricingPlanCards';
import { PricingComparisonTable } from './PricingComparisonTable';
import { PricingValueSection } from './PricingValueSection';
import { PricingAISection } from './PricingAISection';
import { PricingAccountabilitySection } from './PricingAccountabilitySection';
import { PricingFAQ } from './PricingFAQ';

export const metadata: Metadata = {
  title: 'Pricing | Authora — Plans for Every Kind of Writer',
  description:
    'Free, Starter, Pro, Studio, and Founder Lifetime. Whether you are outlining your first idea or finishing your next manuscript, Authora gives you the tools to keep moving.',
  alternates: { canonical: '/pricing' },
  openGraph: {
    title: 'Pricing | Authora',
    description: 'Plans for every kind of writer. Start free. Upgrade when you are ready.',
    url: '/pricing',
  },
};

export default function PricingPage() {
  return (
    <div data-page="pricing">
      <PricingHero />
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <PricingPlanCards />
        <PricingComparisonTable />
        <PricingValueSection />
        <PricingAISection />
        <PricingAccountabilitySection />
        <PricingFAQ />
      </div>
    </div>
  );
}
