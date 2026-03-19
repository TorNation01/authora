import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export type ExploreMorePage =
  | 'home'
  | 'features'
  | 'pricing'
  | 'story-integrity-engine'
  | 'story-density-engine'
  | 'citation-reference-engine'
  | 'for-fiction-writers'
  | 'for-nonfiction-writers';

const EXPLORE_LINKS: Record<ExploreMorePage, { href: string; label: string }> = {
  home: { href: '/', label: 'Home' },
  features: { href: '/features', label: 'All features' },
  pricing: { href: '/pricing', label: 'Pricing' },
  'story-integrity-engine': { href: '/story-integrity-engine', label: 'Story Integrity Engine' },
  'story-density-engine': { href: '/story-density-engine', label: 'Story Density Engine' },
  'citation-reference-engine': { href: '/citation-reference-engine', label: 'Citation & Reference Engine' },
  'for-fiction-writers': { href: '/for-fiction-writers', label: 'For fiction writers' },
  'for-nonfiction-writers': { href: '/for-nonfiction-writers', label: 'For non-fiction writers' },
};

interface FeaturePageExploreMoreProps {
  /** Pages to exclude (e.g. current page) */
  exclude?: ExploreMorePage[];
  /** Optional custom title */
  title?: string;
}

export function FeaturePageExploreMore({
  exclude = [],
  title = 'Explore more',
}: FeaturePageExploreMoreProps) {
  const pages = (Object.keys(EXPLORE_LINKS) as ExploreMorePage[]).filter(
    (p) => !exclude.includes(p)
  );

  return (
    <nav
      className="rounded-2xl border border-white/[0.08] bg-card p-6 sm:p-8"
      aria-label="Related pages"
    >
      <h3 className="text-sm font-medium uppercase tracking-wider text-muted-foreground mb-4">
        {title}
      </h3>
      <ul className="flex flex-wrap gap-x-6 gap-y-2">
        {pages.map((page) => {
          const { href, label } = EXPLORE_LINKS[page];
          return (
            <li key={page}>
              <Link
                href={href}
                className="inline-flex items-center gap-1.5 text-sm font-medium text-foreground hover:text-primary transition-colors"
              >
                {label}
                <ArrowRight className="h-3.5 w-3.5 opacity-60" />
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
