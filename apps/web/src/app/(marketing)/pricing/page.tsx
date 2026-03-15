import type { Metadata } from 'next';
import { PricingContent } from './PricingContent';

export const metadata: Metadata = {
  title: 'Pricing | AUTHORA',
  description: 'Simple, transparent pricing. Start free. Upgrade when you need more.',
};

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="font-serif text-4xl font-bold text-foreground sm:text-5xl">
          Simple pricing
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Start free. Upgrade when you need more. No surprises.
        </p>
      </div>
      <PricingContent />
    </div>
  );
}
