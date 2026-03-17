import type { Metadata } from 'next';
import Link from 'next/link';
import {
  FeaturePageHero,
  FeaturePageSection,
  FeaturePageCTA,
  FeaturePageExploreMore,
} from '@/components/marketing/feature-pages';
import {
  GitBranch,
  Target,
  Users,
  Clock,
  LayoutList,
  Sparkles,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Story Integrity Engine | AUTHORA — Manuscript Intelligence for Plot & Character Gaps',
  description:
    "Authora's Story Integrity Engine detects unresolved plot threads, weak character arcs, missing payoff, and structural gaps. Manuscript intelligence for fiction and non-fiction. Fix what matters. Finish stronger.",
  alternates: { canonical: '/story-integrity-engine' },
  openGraph: {
    title: 'Story Integrity Engine | AUTHORA — Find What Your Story Is Missing',
    description:
      'Manuscript intelligence that finds unresolved threads, weak arcs, missing payoff, and structural gaps. Pro+ feature for fiction and non-fiction.',
    url: '/story-integrity-engine',
    type: 'website',
    siteName: 'AUTHORA',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Story Integrity Engine | AUTHORA',
    description: 'Manuscript intelligence for plot gaps, character arcs, and structural issues.',
  },
};

const DETECTS = [
  { icon: GitBranch, label: 'Unresolved threads' },
  { icon: Target, label: 'Missing payoff' },
  { icon: Users, label: 'Weak arcs' },
  { icon: Clock, label: 'Timeline issues' },
  { icon: LayoutList, label: 'Structural gaps' },
];

const HOW_IT_HELPS = [
  {
    title: 'Clear explanations',
    desc: 'Understand exactly what\'s wrong and why it matters—no vague feedback.',
  },
  {
    title: 'Suggested fixes',
    desc: 'Get actionable guidance on how to address each issue.',
  },
  {
    title: 'Guided improvements',
    desc: 'Revise with purpose instead of guessing where to focus.',
  },
];

const EXAMPLES = [
  {
    title: 'Missing conflict resolution',
    desc: 'A subplot introduced in Act 1 never gets resolved. The engine flags it so you can add the payoff or remove the setup.',
  },
  {
    title: 'Weak character arc',
    desc: 'A main character\'s growth feels flat. The engine identifies where the arc stalls and suggests where to strengthen it.',
  },
  {
    title: 'Dropped subplot',
    desc: 'You introduced a thread readers will expect to see again—but forgot. The engine finds it before beta readers do.',
  },
];

const BENEFITS = [
  'Clarity — see exactly what needs work',
  'Confidence — revise with purpose, not guesswork',
  'Faster revision — target the right spots',
  'Stronger manuscript — fix what matters before you share',
];

export default function StoryIntegrityEnginePage() {
  return (
    <div data-page="story-integrity-engine">
      {/* Hero */}
      <FeaturePageHero
        title="Know what your story is missing"
        supporting="Detect unresolved threads, weak arcs, missing payoff, and structural gaps — and fix them with clarity."
        showCTA={true}
        primaryOnly={true}
      />

      {/* Problem Section */}
      <FeaturePageSection>
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            Most writers feel something is wrong
          </h2>
          <p className="mt-6 text-muted-foreground leading-relaxed">
            A character arc that doesn&apos;t land. A plot thread that never pays off. A structural
            gap that makes the middle sag. You sense it—but you don&apos;t know exactly what. So you
            rewrite blindly, hoping the next pass will fix it. The Story Integrity Engine does the
            detective work so you can fix what actually matters.
          </p>
        </div>
      </FeaturePageSection>

      {/* Solution Section */}
      <FeaturePageSection className="bg-muted/10">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            How the Story Integrity Engine works
          </h2>
          <p className="mt-4 text-muted-foreground">
            Four steps from manuscript to clarity.
          </p>
        </div>
        <ul className="mx-auto max-w-xl space-y-6">
          {[
            { step: 'Scans your manuscript', detail: 'Analyzes structure, characters, and plot threads across the full document.' },
            { step: 'Identifies issues', detail: 'Flags unresolved threads, weak arcs, missing payoff, and structural gaps.' },
            { step: 'Shows exact locations', detail: 'Points you to the right chapters, scenes, or passages—no guessing.' },
            { step: 'Provides guidance', detail: 'Suggests actionable fixes so you know what to do next.' },
          ].map((item, i) => (
            <li key={i} className="flex items-start gap-4">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/20 text-sm font-semibold text-primary">
                {i + 1}
              </span>
              <div>
                <span className="font-medium text-foreground">{item.step}</span>
                <p className="mt-1 text-sm text-muted-foreground">{item.detail}</p>
              </div>
            </li>
          ))}
        </ul>
      </FeaturePageSection>

      {/* What It Detects */}
      <FeaturePageSection>
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            What it detects
          </h2>
          <p className="mt-4 text-muted-foreground">
            Clear, actionable insights—not vague feedback.
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {DETECTS.map((item) => (
            <div
              key={item.label}
              className="flex items-center gap-4 rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)]"
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10">
                <item.icon className="h-6 w-6 text-primary" />
              </div>
              <span className="font-medium text-foreground">{item.label}</span>
            </div>
          ))}
        </div>
      </FeaturePageSection>

      {/* How It Helps */}
      <FeaturePageSection className="bg-muted/10">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            How it helps
          </h2>
          <p className="mt-4 text-muted-foreground">
            You get actionable guidance instead of guesswork.
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-3">
          {HOW_IT_HELPS.map((h) => (
            <div
              key={h.title}
              className="rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)]"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                <Sparkles className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground">{h.title}</h3>
              <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{h.desc}</p>
            </div>
          ))}
        </div>
      </FeaturePageSection>

      {/* Examples */}
      <FeaturePageSection>
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            Real-world examples
          </h2>
          <p className="mt-4 text-muted-foreground">
            The kinds of issues the engine finds and helps you fix.
          </p>
        </div>
        <div className="space-y-6">
          {EXAMPLES.map((ex) => (
            <div
              key={ex.title}
              className="rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)]"
            >
              <h3 className="font-semibold text-foreground">{ex.title}</h3>
              <p className="mt-3 text-muted-foreground leading-relaxed">{ex.desc}</p>
            </div>
          ))}
        </div>
      </FeaturePageSection>

      {/* Benefits */}
      <FeaturePageSection className="bg-muted/10">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            Benefits
          </h2>
          <p className="mt-4 text-muted-foreground">
            What you get when you use the Story Integrity Engine.
          </p>
        </div>
        <ul className="mx-auto max-w-xl space-y-4">
          {BENEFITS.map((benefit) => (
            <li key={benefit} className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 shrink-0 text-primary" />
              <span className="text-muted-foreground">{benefit}</span>
            </li>
          ))}
        </ul>
      </FeaturePageSection>

      {/* Explore more */}
      <FeaturePageSection className="bg-muted/10">
        <FeaturePageExploreMore
          exclude={['story-integrity-engine']}
          title="Explore more"
        />
      </FeaturePageSection>

      {/* Related - Story Density Engine */}
      <FeaturePageSection>
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:justify-between rounded-2xl border border-white/[0.08] bg-card p-8">
          <div>
            <h3 className="font-serif text-xl font-semibold text-foreground">
              Pair it with the Story Density Engine
            </h3>
            <p className="mt-2 text-muted-foreground">
              Integrity finds what&apos;s missing. Density finds what to cut. Together they help you
              write tighter, stronger books.
            </p>
          </div>
          <Link
            href="/story-density-engine"
            className="flex shrink-0 items-center gap-2 font-medium text-primary hover:underline"
          >
            Explore Story Density Engine
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </FeaturePageSection>

      {/* CTA */}
      <FeaturePageCTA
        headline="Ready to find what your story is missing?"
        supporting="Start writing free. Upgrade to Pro for manuscript intelligence."
        supportingLink={{ href: '/pricing', label: 'View pricing' }}
        primaryOnly={true}
        analyticsPrefix="integrity-"
        variant="accent"
      />
    </div>
  );
}
