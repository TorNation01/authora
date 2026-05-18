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
  Scissors,
  Copy,
  Gauge,
  MinusSquare,
  Zap,
  Repeat,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Story Density Engine | AUTHORA — Cut Filler, Reduce Repetition, Strengthen Prose',
  description:
    "Authora's Story Density Engine detects repetition, filler, and weak sections in your manuscript. Know what to cut, compress, or strengthen. Write tighter, stronger books. Fiction and non-fiction.",
  alternates: { canonical: '/story-density-engine' },
  openGraph: {
    title: 'Story Density Engine | AUTHORA — Cut the Filler, Strengthen What Matters',
    description:
      'Manuscript intelligence that finds filler, repetition, and weak sections. Trim and strengthen with confidence. Pro+ feature for fiction and non-fiction.',
    url: '/story-density-engine',
    type: 'website',
    siteName: 'AUTHORA',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Story Density Engine | AUTHORA',
    description: 'Manuscript intelligence for repetition, filler, and weak sections.',
  },
};

const DETECTS = [
  { icon: Copy, label: 'Filler scenes' },
  { icon: Repeat, label: 'Repeated ideas' },
  { icon: Gauge, label: 'Slow chapters' },
  { icon: MinusSquare, label: 'Weak transitions' },
  { icon: Zap, label: 'Rushed moments' },
];

const TRIM_VS_STRENGTHEN = [
  {
    action: 'Cut',
    desc: 'Remove filler that adds nothing—redundant descriptions, throat-clearing, scenes that don\'t advance story or argument.',
  },
  {
    action: 'Compress',
    desc: 'Tighten over-explained sections. Say it once, well—instead of three times.',
  },
  {
    action: 'Expand',
    desc: 'Build out thin areas where readers need more—context, payoff, or emotional weight.',
  },
  {
    action: 'Strengthen',
    desc: 'Deepen weak transitions and rushed moments so they land with impact.',
  },
];

const EXAMPLES = [
  {
    title: 'Repeated emotional beat',
    desc: 'The same revelation or feeling is hit in three different scenes. The engine flags it so you can keep the strongest version and cut the rest.',
  },
  {
    title: 'Over-explained section',
    desc: 'You\'ve said the same thing in four different ways. The engine identifies the bloat so you can compress to one clear statement.',
  },
  {
    title: 'Rushed payoff',
    desc: 'A major moment gets a single paragraph when it deserves a scene. The engine spots thin areas so you know where to expand.',
  },
];

const BENEFITS = [
  'Tighter writing — cut filler without losing what matters',
  'Better pacing — balance density across chapters',
  'Stronger impact — expand where it counts, trim where it doesn\'t',
];

const FAQ_ITEMS = [
  {
    q: 'What is the Story Density Engine?',
    a: 'A manuscript intelligence tool that detects repetition, filler, drag, and weak sections in your manuscript. It shows you what to trim, compress, or strengthen.',
  },
  {
    q: 'Which plans include the Story Density Engine?',
    a: 'Pro, Studio. Free and Starter do not include manuscript intelligence tools.',
  },
  {
    q: 'Does it work for non-fiction?',
    a: 'Yes. The engine adapts to non-fiction—detecting repeated arguments, weak evidence, and sections that need more or less support.',
  },
  {
    q: 'Will it rewrite my manuscript?',
    a: 'No. The engine identifies issues and suggests actions. You stay in control of every change.',
  },
];

export default function StoryDensityEnginePage() {
  return (
    <div data-page="story-density-engine">
      {/* Hero */}
      <FeaturePageHero
        title="Cut the filler. Strengthen what matters."
        supporting="Identify repetition, drag, and weak sections — and know exactly what to trim or build."
        showCTA={true}
        primaryOnly={true}
      />

      {/* Problem */}
      <FeaturePageSection>
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            Writers overwrite or underwrite—and don&apos;t know what to cut or expand
          </h2>
          <p className="mt-6 text-muted-foreground leading-relaxed">
            You sense the manuscript is bloated in places and thin in others. Some chapters drag.
            Others rush. But cutting blindly risks losing what matters—and expanding blindly adds
            more filler. The Story Density Engine shows you exactly where to trim, where to
            compress, and where to strengthen.
          </p>
        </div>
      </FeaturePageSection>

      {/* Solution */}
      <FeaturePageSection className="bg-muted/10">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            How the Story Density Engine works
          </h2>
          <p className="mt-4 text-muted-foreground">
            Four steps from manuscript to clarity.
          </p>
        </div>
        <ul className="mx-auto max-w-xl space-y-6">
          {[
            {
              step: 'Detects filler',
              detail: 'Finds scenes and passages that add nothing—redundant descriptions, throat-clearing, dead weight.',
            },
            {
              step: 'Detects repetition',
              detail: 'Flags repeated ideas, emotional beats, or arguments so you can keep the strongest version.',
            },
            {
              step: 'Detects thin areas',
              detail: 'Identifies rushed moments, weak transitions, and sections that need more support.',
            },
            {
              step: 'Suggests actions',
              detail: 'Tells you what to cut, compress, expand, or strengthen—so you revise with purpose.',
            },
          ].map((item, i) => (
            <li key={i} className="flex items-start gap-4">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-success/20 text-sm font-semibold text-success">
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
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-success/10">
                <item.icon className="h-6 w-6 text-success" />
              </div>
              <span className="font-medium text-foreground">{item.label}</span>
            </div>
          ))}
        </div>
      </FeaturePageSection>

      {/* Trim vs Strengthen */}
      <FeaturePageSection className="bg-muted/10">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            Trim vs strengthen
          </h2>
          <p className="mt-4 text-muted-foreground">
            Know what to cut, what to compress, what to expand, and what to strengthen.
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2">
          {TRIM_VS_STRENGTHEN.map((item) => (
            <div
              key={item.action}
              className="rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)]"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-success/10">
                <Scissors className="h-5 w-5 text-success" />
              </div>
              <h3 className="font-semibold text-foreground">{item.action}</h3>
              <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
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
            What you get when you use the Story Density Engine.
          </p>
        </div>
        <ul className="mx-auto max-w-xl space-y-4">
          {BENEFITS.map((benefit) => (
            <li key={benefit} className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 shrink-0 text-success" />
              <span className="text-muted-foreground">{benefit}</span>
            </li>
          ))}
        </ul>
      </FeaturePageSection>

      {/* Explore more */}
      <FeaturePageSection className="bg-muted/10">
        <FeaturePageExploreMore
          exclude={['story-density-engine']}
          title="Explore more"
        />
      </FeaturePageSection>

      {/* Related - Story Integrity Engine */}
      <FeaturePageSection>
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:justify-between rounded-2xl border border-white/[0.08] bg-card p-8">
          <div>
            <h3 className="font-serif text-xl font-semibold text-foreground">
              Pair it with the Story Integrity Engine
            </h3>
            <p className="mt-2 text-muted-foreground">
              Density finds what to cut. Integrity finds what&apos;s missing. Together they help you
              write tighter, stronger books.
            </p>
          </div>
          <Link
            href="/story-integrity-engine"
            className="flex shrink-0 items-center gap-2 font-medium text-primary hover:underline"
          >
            Explore Story Integrity Engine
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </FeaturePageSection>

      {/* CTA */}
      <FeaturePageCTA
        headline="Ready to cut the filler?"
        supporting="Start writing free. Upgrade to Pro for manuscript intelligence."
        supportingLink={{ href: '/pricing', label: 'View pricing' }}
        primaryOnly={true}
        analyticsPrefix="density-"
        variant="accent"
      />

      {/* FAQ */}
      <FeaturePageFAQ items={FAQ_ITEMS} />
    </div>
  );
}
