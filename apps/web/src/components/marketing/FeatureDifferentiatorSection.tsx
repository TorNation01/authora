'use client';

import Link from 'next/link';
import { StoryIntegrityEngineSection } from './StoryIntegrityEngineSection';
import { StoryDensityEngineSection } from './StoryDensityEngineSection';
import { EnginesCombinedSection } from './EnginesCombinedSection';

export function FeatureDifferentiatorSection() {
  return (
    <section className="py-20" data-analytics="feature-differentiator" id="manuscript-intelligence">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Manuscript intelligence that helps you revise smarter
          </h2>
          <p className="mt-4 text-muted-foreground">
            Two engines that turn guesswork into clarity.
          </p>
          <Link
            href="/features#manuscript-intelligence"
            className="mt-4 inline-block text-sm font-medium text-primary hover:underline"
          >
            See all features →
          </Link>
        </div>
        <div className="mt-16 space-y-12">
          <StoryIntegrityEngineSection />
          <StoryDensityEngineSection />
          <EnginesCombinedSection />
        </div>
      </div>
    </section>
  );
}
