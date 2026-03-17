'use client';

import { useState } from 'react';
import { PricingHero } from './PricingHero';
import { PricingPlanCards } from './PricingPlanCards';
import { PricingComparisonTable } from './PricingComparisonTable';
import { PricingValueSection } from './PricingValueSection';
import { PricingIntelligenceSection } from './PricingIntelligenceSection';
import { PricingAISection } from './PricingAISection';
import { PricingAccountabilitySection } from './PricingAccountabilitySection';
import { PricingFAQ } from './PricingFAQ';
import { PricingFinalCTA } from './PricingFinalCTA';

export function PricingContent() {
  const [billingInterval, setBillingInterval] = useState<'monthly' | 'yearly'>('yearly');

  return (
    <div data-page="pricing">
      <PricingHero
        billingInterval={billingInterval}
        onBillingIntervalChange={setBillingInterval}
      />
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <PricingPlanCards billingInterval={billingInterval} />
        <PricingComparisonTable />
        <PricingValueSection />
        <PricingIntelligenceSection />
        <PricingAISection />
        <PricingAccountabilitySection />
        <PricingFAQ />
        <PricingFinalCTA />
      </div>
    </div>
  );
}
