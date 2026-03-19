'use client';

import Link from 'next/link';
import { StoryIntegrityEngineSection } from './StoryIntegrityEngineSection';
import { StoryDensityEngineSection } from './StoryDensityEngineSection';
import { CitationReferenceEngineSection } from './CitationReferenceEngineSection';
import { EnginesCombinedSection } from './EnginesCombinedSection';

export function FeatureDifferentiatorSection() {
  return (
    <section
      className="py-[var(--section-padding-y)]"
      data-analytics="feature-differentiator"
      id="manuscript-intelligence"
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)]">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-wider text-primary/80 mb-4">
            Manuscript Intelligence & Academic Tools
          </p>
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Engines that turn guesswork into clarity
          </h2>
          <p className="mt-4 text-muted-foreground">
            Know what your story needs. Cut the filler. Cite with confidence.
          </p>
          <Link
            href="/features#manuscript-intelligence"
            className="mt-4 inline-block text-sm font-medium text-primary hover:underline"
          >
            See all features →
          </Link>
        </div>

        <div className="mt-16 space-y-8">
          <StoryIntegrityEngineSection />
          <StoryDensityEngineSection />
          <CitationReferenceEngineSection />
          <EnginesCombinedSection />
        </div>
      </div>
    </section>
  );
}
