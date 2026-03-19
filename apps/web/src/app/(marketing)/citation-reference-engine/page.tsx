import type { Metadata } from 'next';
import Link from 'next/link';
import {
  FeaturePageHero,
  FeaturePageSection,
  FeaturePageCTA,
  FeaturePageExploreMore,
} from '@/components/marketing/feature-pages';
import {
  BookOpen,
  Library,
  Link2,
  ListOrdered,
  FileText,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Citation & Reference Engine | AUTHORA — Academic Writing & Bibliography Tools',
  description:
    "Authora's Citation & Reference Engine adds sources, inserts in-text citations, and generates formatted bibliographies. APA, MLA, Chicago, Harvard, Zotero sync. For students, teachers, lecturers, and academic writers.",
  alternates: { canonical: '/citation-reference-engine' },
  openGraph: {
    title: 'Citation & Reference Engine | AUTHORA — Cite with Confidence',
    description:
      'Add sources, insert citations, generate bibliographies. APA, MLA, Chicago, Harvard, Zotero. For students, teachers, lecturers, and academics.',
    url: '/citation-reference-engine',
    type: 'website',
    siteName: 'AUTHORA',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Citation & Reference Engine | AUTHORA',
    description: 'Academic writing tools: sources, citations, bibliography. APA, MLA, Chicago, Zotero.',
  },
};

const FEATURES = [
  { icon: Library, label: 'Source library — add and manage references' },
  { icon: Link2, label: 'In-text citations — APA, MLA, Chicago, Harvard' },
  { icon: ListOrdered, label: 'Bibliography generation — formatted output' },
  { icon: FileText, label: 'Zotero integration — sync your library' },
  { icon: BookOpen, label: 'Academic templates — essays, exams, courses, and lecture materials' },
  { icon: CheckCircle2, label: 'CSL-based — industry-standard citation styles' },
];

const HOW_IT_WORKS = [
  { step: 'Add sources', detail: 'Add references to your vault or sync from Zotero.' },
  { step: 'Insert citations', detail: 'Place in-text citations as you write. Preview before inserting.' },
  { step: 'Choose style', detail: 'Set APA, MLA, Chicago, Harvard, IEEE, or MHRA.' },
  { step: 'Generate bibliography', detail: 'Export formatted bibliography for your manuscript.' },
];

const BENEFITS = [
  'Clarity — see exactly what you cited',
  'Confidence — proper formatting every time',
  'Faster revision — no manual bibliography',
  'Export-ready — formatted for submission',
];

export default function CitationReferenceEnginePage() {
  return (
    <div data-page="citation-reference-engine">
      {/* Hero */}
      <FeaturePageHero
        title="Cite with confidence. Build your bibliography."
        supporting="Add sources, insert in-text citations, and generate formatted bibliographies. APA, MLA, Chicago, Harvard — plus Zotero sync for students, teachers, lecturers, and researchers."
        showCTA={true}
        primaryOnly={true}
      />

      {/* Problem Section */}
      <FeaturePageSection>
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            Academic writing deserves proper citations
          </h2>
          <p className="mt-6 text-muted-foreground leading-relaxed">
            Manual formatting is tedious. Style guides change. References get mixed up. The Citation
            & Reference Engine keeps your sources in one place, inserts citations correctly, and
            generates formatted bibliographies for any style — APA, MLA, Chicago, Harvard, and more.
          </p>
        </div>
      </FeaturePageSection>

      {/* How It Works */}
      <FeaturePageSection className="bg-muted/10">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            How the Citation & Reference Engine works
          </h2>
          <p className="mt-4 text-muted-foreground">
            Four steps from sources to bibliography.
          </p>
        </div>
        <ul className="mx-auto max-w-xl space-y-6">
          {HOW_IT_WORKS.map((item, i) => (
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

      {/* What It Includes */}
      <FeaturePageSection>
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            What it includes
          </h2>
          <p className="mt-4 text-muted-foreground">
            Everything students, teachers, lecturers, and researchers need for essays, exams, courses, and academic writing.
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((item) => (
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

      {/* Benefits */}
      <FeaturePageSection className="bg-muted/10">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
            Benefits
          </h2>
          <p className="mt-4 text-muted-foreground">
            What you get when you use the Citation & Reference Engine.
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
          exclude={['citation-reference-engine']}
          title="Explore more"
        />
      </FeaturePageSection>

      {/* Related - Story Engines */}
      <FeaturePageSection>
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:justify-between rounded-2xl border border-white/[0.08] bg-card p-8">
          <div>
            <h3 className="font-serif text-xl font-semibold text-foreground">
              Pair it with manuscript intelligence
            </h3>
            <p className="mt-2 text-muted-foreground">
              Story Integrity Engine finds what&apos;s missing. Story Density Engine finds what to cut.
              Citation Engine handles your sources. Together they help you write stronger, properly cited work.
            </p>
          </div>
          <Link
            href="/features#manuscript-intelligence"
            className="flex shrink-0 items-center gap-2 font-medium text-primary hover:underline"
          >
            Explore all engines
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </FeaturePageSection>

      {/* CTA */}
      <FeaturePageCTA
        headline="Ready to cite with confidence?"
        supporting="Start writing free. Upgrade to Studio for citation & reference tools."
        supportingLink={{ href: '/pricing', label: 'View pricing' }}
        primaryOnly={true}
        analyticsPrefix="citation-reference-"
        variant="accent"
      />
    </div>
  );
}
