import type { Metadata } from 'next';
import Link from 'next/link';
import {
  FeaturePageHero,
  FeaturePageSection,
  FeaturePageCTA,
  FeaturePageExploreMore,
} from '@/components/marketing/feature-pages';
import { StoryIntegrityEngineSection } from '@/components/marketing/StoryIntegrityEngineSection';
import { StoryDensityEngineSection } from '@/components/marketing/StoryDensityEngineSection';
import {
  PenLine,
  Bot,
  GitBranch,
  Scissors,
  BookMarked,
  Lightbulb,
  FileEdit,
  Target,
  LayoutGrid,
  FileDown,
  ArrowRight,
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Features | AUTHORA — Book Writing Software & Manuscript Intelligence',
  description:
    'Book writing software with guided planning, AI support, Story Integrity Engine, Story Density Engine, accountability, and export. Fiction and non-fiction templates. Finish your book.',
  alternates: { canonical: '/features' },
  openGraph: {
    title: 'Features | AUTHORA — Book Writing Software That Helps You Finish',
    description:
      'Guided planning, AI support, manuscript intelligence, accountability, export. Everything you need to finish your book. Fiction and non-fiction.',
    url: '/features',
    type: 'website',
    siteName: 'AUTHORA',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Features | AUTHORA — Book Writing Software',
    description: 'Guided planning, AI support, manuscript intelligence. Finish your book.',
  },
};

const FEATURE_GRID = [
  {
    icon: PenLine,
    title: 'Writing Studio',
    description: 'Distraction-free editor with chapters, formatting, and side-by-side notes. Write without tab chaos.',
    href: '/features#writing',
  },
  {
    icon: Bot,
    title: 'AI Assistance',
    description: 'Get suggestions, rewrites, and drafts when you need them. You control the level—AI assists, your voice leads.',
    href: '/features#writing',
  },
  {
    icon: GitBranch,
    title: 'Story Integrity Engine',
    description: 'Find what your story is missing—unresolved threads, weak arcs, missing payoff, structural gaps.',
    href: '/story-integrity-engine',
  },
  {
    icon: Scissors,
    title: 'Story Density Engine',
    description: 'Cut the filler. Strengthen what matters. Detect repetition, drag, and weak sections.',
    href: '/story-density-engine',
  },
  {
    icon: BookMarked,
    title: 'Planning & Structure Tools',
    description: 'Genre-specific templates, outline suggestions, and chapter structures that match how professionals write.',
    href: '/for-fiction-writers',
  },
  {
    icon: Lightbulb,
    title: 'Research & Ideas',
    description: 'Notes, idea boards, and research vault. Keep everything in one place.',
    href: '/features#planning',
  },
  {
    icon: FileEdit,
    title: 'Revision System',
    description: 'Manuscript intelligence to find gaps and tighten prose. Revise with purpose.',
    href: '/features#improving',
  },
  {
    icon: Target,
    title: 'Accountability & Finish Mode',
    description: 'Word goals, reminders, milestones. Built to help you actually finish.',
    href: '/features#finishing',
  },
  {
    icon: LayoutGrid,
    title: 'Multi-Project System',
    description: 'Work on multiple books at once. Different modes and templates per project.',
    href: '/pricing',
  },
  {
    icon: FileDown,
    title: 'Export & Publishing Tools',
    description: 'DOCX, PDF, EPUB, plain text. One click to share with beta readers or publish.',
    href: '/features#finishing',
  },
];

const HOW_IT_WORKS = [
  {
    id: 'planning',
    title: 'Planning',
    description: 'Choose your genre and project type. Build your structure with templates or freeform. Authora adapts to you.',
  },
  {
    id: 'writing',
    title: 'Writing',
    description: 'Stay in flow with a distraction-free editor, AI support when you need it, and notes and research at your fingertips.',
  },
  {
    id: 'improving',
    title: 'Improving',
    description: 'Use manuscript intelligence to find gaps, cut filler, and strengthen what matters. Revise with clarity.',
  },
  {
    id: 'finishing',
    title: 'Finishing',
    description: 'Accountability, milestones, and Finish Mode. Export cleanly when you\'re ready.',
  },
];

export default function FeaturesPage() {
  return (
    <div data-page="features">
      {/* Hero */}
      <FeaturePageHero
        title="Everything you need to write and finish your book"
        supporting="From idea to final manuscript, Authora gives you the tools, structure, and intelligence to move forward with clarity and confidence."
        showCTA={true}
        primaryOnly={true}
      />

      {/* Feature Grid */}
      <FeaturePageSection>
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            All your tools in one place
          </h2>
          <p className="mt-4 text-muted-foreground">
            Everything you need to plan, write, improve, and finish your book.
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURE_GRID.map((f) => (
            <Link
              key={f.title}
              href={f.href}
              className="group flex flex-col rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)] transition-all hover:border-primary/20 hover:shadow-[var(--shadow-card-hover)]"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                <f.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-serif text-lg font-semibold text-foreground">{f.title}</h3>
              <p className="mt-2 flex-1 text-sm text-muted-foreground leading-relaxed">
                {f.description}
              </p>
              <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary group-hover:underline">
                Learn more
                <ArrowRight className="h-4 w-4" />
              </span>
            </Link>
          ))}
        </div>
      </FeaturePageSection>

      {/* Core Differentiators */}
      <FeaturePageSection className="bg-muted/10">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            Manuscript intelligence
          </h2>
          <p className="mt-4 text-muted-foreground">
            Not just writing tools—writing intelligence that helps you revise smarter.
          </p>
        </div>
        <div className="space-y-12">
          <StoryIntegrityEngineSection />
          <StoryDensityEngineSection />
        </div>
      </FeaturePageSection>

      {/* How It All Works Together */}
      <FeaturePageSection>
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            How it all works together
          </h2>
          <p className="mt-4 text-muted-foreground">
            From idea to finished manuscript.
          </p>
        </div>
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {HOW_IT_WORKS.map((step) => (
            <div
              key={step.id}
              id={step.id}
              className="rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)]"
            >
              <h3 className="font-serif text-xl font-semibold text-foreground">{step.title}</h3>
              <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </FeaturePageSection>

      {/* Explore more */}
      <FeaturePageSection className="bg-muted/10">
        <FeaturePageExploreMore
          exclude={['features']}
          title="Explore AUTHORA"
        />
      </FeaturePageSection>

      {/* Final CTA */}
      <FeaturePageCTA
        headline="Start your book today"
        supporting="Start free. No credit card required."
        supportingLink={{ href: '/pricing', label: 'View pricing' }}
        primaryOnly={true}
        analyticsPrefix="features-final-"
        variant="accent"
      />
    </div>
  );
}
