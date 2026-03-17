'use client';

import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';

export function FeaturesCTASection() {
  return (
    <div className="mt-16 flex flex-col items-center justify-center gap-6 py-12">
      <CTAPair
        primary="start-writing-free"
        secondary="view-pricing"
        microcopy={CTA_MICROCOPY.ctaSectionAlt}
        analyticsPrefix="features-"
      />
    </div>
  );
}
