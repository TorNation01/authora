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
  Lightbulb,
  ArrowRightLeft,
  BookTemplate,
  ArrowRight,
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'For Non-Fiction Writers | AUTHORA — Book Writing Software for Memoir, Business, Self-Help',
  description:
    'Book writing software for non-fiction. Structure knowledge, guide readers, create meaningful content. Memoir, business, self-help, workbooks. Story Integrity Engine, Story Density Engine.',
  alternates: { canonical: '/for-nonfiction-writers' },
  openGraph: {
    title: 'For Non-Fiction Writers | AUTHORA — Turn Ideas Into Clear, Powerful Books',
    description:
      'Structure your knowledge, guide your reader, and create meaningful content that delivers value. Built for memoir, business, self-help, workbooks.',
    url: '/for-nonfiction-writers',
    type: 'website',
    siteName: 'AUTHORA',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'For Non-Fiction Writers | AUTHORA',
    description: 'Book writing software for memoir, business, self-help, and workbooks.',
  },
};

const SECTIONS = [
  {
    icon: LayoutList,
    title: 'Structured chapter building',
    desc: 'Build chapters with clear purpose. Outline, draft, and revise with structure that guides your reader.',
  },
  {
    icon: Lightbulb,
    title: 'Idea organization',
    desc: 'Capture and organize ideas, research, and sources. Keep everything in one place as you write.',
  },
  {
    icon: ArrowRightLeft,
    title: 'Clarity and flow tools',
    desc: 'Ensure your argument progresses logically. See where clarity breaks down and where to tighten.',
  },
  {
    icon: BookTemplate,
    title: 'Examples and frameworks',
    desc: 'Templates for memoir, business, self-help, workbooks. Structure that fits how you write.',
  },
  {
    icon: GitBranch,
    title: 'Story Integrity Engine',
    desc: 'Find argument gaps, missing evidence, and structural holes. Fix what matters. Pro+ feature.',
    href: '/story-integrity-engine',
  },
  {
    icon: Scissors,
    title: 'Story Density Engine',
    desc: 'Detect repetition and filler. Know what to trim and what to strengthen. Pro+ feature.',
    href: '/story-density-engine',
  },
];

const EXAMPLES = [
  {
    title: 'Self-help books',
    desc: 'Structure your framework, build chapters that deliver value, and ensure each section advances your reader.',
  },
  {
    title: 'Business books',
    desc: 'Organize case studies, examples, and arguments. Keep the logic tight and the takeaways clear.',
  },
  {
    title: 'Guides and workbooks',
    desc: 'Create exercises, prompts, and structured content. Templates that support how-to and workbook formats.',
  },
];

const FAQ_ITEMS = [
  {
    q: 'Does Authora support my non-fiction genre?',
    a: 'Authora includes templates for memoir, business, self-help, workbooks, how-to, biography, history, and creative non-fiction. You can also write freeform.',
  },
  {
    q: 'Do the Story Integrity and Density Engines work for non-fiction?',
    a: 'Yes. Both engines adapt to non-fiction—detecting weak argument flow, repeated points, missing evidence, and structural gaps.',
  },
  {
    q: 'Will AI write my book for me?',
    a: 'No. You stay in control. Use AI for brainstorming, expanding outlines, or refining prose—as much or as little as you want.',
  },
  {
    q: 'Can I use Authora for workbooks and exercises?',
    a: 'Yes. Authora supports workbooks, exercises, case studies, and structured non-fiction formats.',
  },
];

export default function ForNonfictionWritersPage() {
  return (
    <div data-page="for-nonfiction-writers">
      {/* Hero */}
      <FeaturePageHero
        title="Turn your ideas into clear, powerful books"
        supporting="Structure your knowledge, guide your reader, and create meaningful content that delivers value."
        showCTA={true}
        primaryOnly={true}
      />

      {/* Sections */}
      <FeaturePageSection>
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            How Authora helps non-fiction writers
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
            How non-fiction writers use Authora.
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
          exclude={['for-nonfiction-writers']}
          title="Explore more"
        />
      </FeaturePageSection>

      {/* Related - Fiction */}
      <FeaturePageSection>
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:justify-between rounded-2xl border border-white/[0.08] bg-card p-8">
          <div>
            <h3 className="font-serif text-xl font-semibold text-foreground">
              Write fiction too?
            </h3>
            <p className="mt-2 text-muted-foreground">
              Authora supports romance, thriller, fantasy, mystery, and more.
            </p>
          </div>
          <Link
            href="/for-fiction-writers"
            className="flex shrink-0 items-center gap-2 font-medium text-primary hover:underline"
          >
            For fiction writers
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </FeaturePageSection>

      {/* CTA */}
      <FeaturePageCTA
        headline="Ready to turn your ideas into a book?"
        supporting="Start writing free. Upgrade when you're ready."
        supportingLink={{ href: '/pricing', label: 'View pricing' }}
        primaryOnly={true}
        analyticsPrefix="nonfiction-"
        variant="accent"
      />

      {/* FAQ */}
      <FeaturePageFAQ items={FAQ_ITEMS} />
    </div>
  );
}
