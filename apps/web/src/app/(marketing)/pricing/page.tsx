import type { Metadata } from 'next';
import { PricingContent } from './PricingContent';

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
  return <PricingContent />;
}
