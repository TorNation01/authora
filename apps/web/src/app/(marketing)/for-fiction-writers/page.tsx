import type { Metadata } from 'next';
import Link from 'next/link';
import {
  FeaturePageHero,
  FeaturePageSection,
  FeaturePageCTA,
  FeaturePageFAQ,
  FeaturePageExploreMore,
} from '@/components/marketing/feature-pages';
import {
  GitBranch,
  Scissors,
  LayoutList,
  Users,
  Globe,
  Gauge,
  ArrowRight,
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'For Fiction Writers | AUTHORA — Novel Writing Software & Plot Structure Tools',
  description:
    'Book writing software for fiction writers. Plot structure, character arc tracking, world-building, pacing, Story Integrity Engine, Story Density Engine. Romance, thriller, fantasy, mystery, and more.',
  alternates: { canonical: '/for-fiction-writers' },
  openGraph: {
    title: 'For Fiction Writers | AUTHORA — Build Stories That Actually Work',
    description:
      'Structure your plot, strengthen your characters, and finish your story with clarity. Novel writing software for romance, thriller, fantasy, mystery.',
    url: '/for-fiction-writers',
    type: 'website',
    siteName: 'AUTHORA',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'For Fiction Writers | AUTHORA',
    description: 'Novel writing software with plot structure, character arcs, and manuscript intelligence.',
  },
};

const SECTIONS = [
  {
    icon: LayoutList,
    title: 'Plot structure support',
    desc: 'Outline your story with structure that fits your genre. From idea to finished draft.',
  },
  {
    icon: Users,
    title: 'Character arc tracking',
    desc: 'Track character growth, goals, and relationships across your manuscript.',
  },
  {
    icon: Globe,
    title: 'World-building tools',
    desc: 'Notes, research vault, and lore—keep your world consistent and accessible.',
  },
  {
    icon: Gauge,
    title: 'Pacing and tension',
    desc: 'See where the story drags or rushes. Balance tension and payoff across chapters.',
  },
  {
    icon: GitBranch,
    title: 'Story Integrity Engine',
    desc: 'Find unresolved plot threads, weak arcs, structural gaps. Fix what matters. Pro+ feature.',
    href: '/story-integrity-engine',
  },
  {
    icon: Scissors,
    title: 'Story Density Engine',
    desc: 'Cut filler, find repetition, strengthen weak sections. Know what to trim and what to build. Pro+ feature.',
    href: '/story-density-engine',
  },
];

const EXAMPLES = [
  {
    title: 'Building a thriller',
    desc: 'Structure your plot beats, plant clues, and keep tension tight. The engine flags dropped threads and weak payoff before readers notice.',
  },
  {
    title: 'Writing a romance arc',
    desc: 'Track character growth and relationship milestones. Ensure the emotional arc lands—not just the plot.',
  },
  {
    title: 'Managing subplots',
    desc: 'Keep multiple threads organized. See where each thread is introduced, developed, and resolved.',
  },
];

const FAQ_ITEMS = [
  {
    q: 'Does Authora support my genre?',
    a: 'Authora includes templates for romance, thriller, fantasy, mystery, sci-fi, literary fiction, YA, horror, and more. You can also write freeform.',
  },
  {
    q: 'Can I use the Story Integrity and Density Engines for fiction?',
    a: 'Yes. Both engines are designed for fiction—detecting plot gaps, character arcs, repetition, and pacing issues.',
  },
  {
    q: 'Will AI write my novel for me?',
    a: 'No. You stay in control. Use AI for brainstorming, rewrites, or getting unstuck—as much or as little as you want.',
  },
  {
    q: 'Can I work on multiple novels at once?',
    a: 'Yes. Free allows 1 book; Starter allows 3; Pro and Studio allow unlimited projects.',
  },
];

export default function ForFictionWritersPage() {
  return (
    <div data-page="for-fiction-writers">
      {/* Hero */}
      <FeaturePageHero
        title="Build stories that actually work"
        supporting="Structure your plot, strengthen your characters, and finish your story with clarity."
        showCTA={true}
        primaryOnly={true}
      />

      {/* Sections */}
      <FeaturePageSection>
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            How Authora helps fiction writers
          </h2>
          <p className="mt-4 text-muted-foreground">
            From structure to manuscript intelligence.
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {SECTIONS.map((section) =>
            section.href ? (
              <Link
                key={section.title}
                href={section.href}
                className="group flex flex-col rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)] transition-colors hover:border-primary/30"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                  <section.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-serif text-lg font-semibold text-foreground group-hover:text-primary">
                  {section.title}
                </h3>
                <p className="mt-3 flex-1 text-sm text-muted-foreground leading-relaxed">
                  {section.desc}
                </p>
                <span className="mt-4 flex items-center gap-2 text-sm font-medium text-primary">
                  Learn more
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Link>
            ) : (
              <div
                key={section.title}
                className="rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)]"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                  <section.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-serif text-lg font-semibold text-foreground">
                  {section.title}
                </h3>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{section.desc}</p>
              </div>
            )
          )}
        </div>
      </FeaturePageSection>

      {/* Examples */}
      <FeaturePageSection className="bg-muted/10">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            Examples
          </h2>
          <p className="mt-4 text-muted-foreground">
            How fiction writers use Authora.
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-3">
          {EXAMPLES.map((ex) => (
            <div
              key={ex.title}
              className="rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)]"
            >
              <h3 className="font-semibold text-foreground">{ex.title}</h3>
              <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{ex.desc}</p>
            </div>
          ))}
        </div>
      </FeaturePageSection>

      {/* Explore more */}
      <FeaturePageSection className="bg-muted/10">
        <FeaturePageExploreMore
          exclude={['for-fiction-writers']}
          title="Explore more"
        />
      </FeaturePageSection>

      {/* Related - Non-fiction */}
      <FeaturePageSection>
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:justify-between rounded-2xl border border-white/[0.08] bg-card p-8">
          <div>
            <h3 className="font-serif text-xl font-semibold text-foreground">
              Write non-fiction too?
            </h3>
            <p className="mt-2 text-muted-foreground">
              Authora supports memoir, business, self-help, workbooks, and more.
            </p>
          </div>
          <Link
            href="/for-nonfiction-writers"
            className="flex shrink-0 items-center gap-2 font-medium text-primary hover:underline"
          >
            For non-fiction writers
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </FeaturePageSection>

      {/* CTA */}
      <FeaturePageCTA
        headline="Ready to build stories that work?"
        supporting="Start writing free. Upgrade when you're ready."
        supportingLink={{ href: '/pricing', label: 'View pricing' }}
        primaryOnly={true}
        analyticsPrefix="fiction-"
        variant="accent"
      />

      {/* FAQ */}
      <FeaturePageFAQ items={FAQ_ITEMS} />
    </div>
  );
}
