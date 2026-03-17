import type { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { getAppBaseUrl } from '@/lib/config';
import { ProductPreview } from '@/components/marketing/ProductPreview';
import { StoryIntegrityEngineSection } from '@/components/marketing/StoryIntegrityEngineSection';
import { StoryDensityEngineSection } from '@/components/marketing/StoryDensityEngineSection';
import { EnginesCombinedSection } from '@/components/marketing/EnginesCombinedSection';
import {
  Target,
  FileDown,
  PenLine,
  LayoutGrid,
  BookMarked,
  Bot,
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Features | AUTHORA — All Your Writing Tools in One Place',
  description:
    'Guided planning, AI support, Story Integrity Engine, Story Density Engine, accountability, export—everything you need to finish your book. Fiction and non-fiction templates.',
};

const FEATURES = [
  {
    icon: BookMarked,
    title: 'Guided planning',
    description: 'Genre-specific templates for romance, thriller, fantasy, mystery, memoir, business, self-help, and more. Setup questions, outline suggestions, and chapter structures that match how professionals write.',
  },
  {
    icon: Bot,
    title: 'AI support without overwhelm',
    description: 'Get suggestions, rewrites, and drafts when you need them. You control the level—minimal, moderate, or full. AI assists; your voice leads.',
  },
  {
    icon: Target,
    title: 'Accountability that helps you complete',
    description: 'Set daily or weekly word goals. Choose your style: gentle, balanced, or structured. Reminders and recovery nudges when life gets in the way. Milestone maps to track progress.',
  },
  {
    icon: LayoutGrid,
    title: 'All your tools in one place',
    description: 'Outline, notes, research, editor, version history, export. No more juggling Scrivener, Notion, and Google Docs. One workspace for your entire book.',
  },
  {
    icon: PenLine,
    title: 'Writing studio',
    description: 'Distraction-free editor with formatting, headings, and lists. Autosave, version history, and side-by-side notes. Write without tab chaos.',
  },
  {
    icon: FileDown,
    title: 'Export ready',
    description: 'DOCX, PDF, EPUB, plain text. One click to share with beta readers, query agents, or publish. Publishing prep tools for synopsis and blurb.',
  },
];

export default function FeaturesPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="font-serif text-4xl font-bold text-foreground sm:text-5xl">
          Everything you need to finish your book
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Guided writing journey from idea to manuscript. AI when you need it. Accountability that works.
        </p>
      </div>
      <div className="mt-16 grid gap-12 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f) => (
          <div key={f.title} className="card-sanctuary p-8">
            <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
              <f.icon className="h-7 w-7 text-primary" />
            </div>
            <h2 className="font-serif text-xl font-semibold text-foreground">{f.title}</h2>
            <p className="mt-3 text-muted-foreground leading-relaxed">{f.description}</p>
          </div>
        ))}
      </div>

      {/* Manuscript Intelligence: Story Integrity & Story Density Engines */}
      <div className="mt-24" id="manuscript-intelligence">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Manuscript intelligence
          </h2>
          <p className="mt-4 text-muted-foreground">
            Not just writing tools — writing intelligence that helps you revise smarter.
          </p>
        </div>
        <div className="mt-16 space-y-12">
          <StoryIntegrityEngineSection />
          <StoryDensityEngineSection />
          <EnginesCombinedSection />
        </div>
      </div>

      <div className="mt-20">
        <ProductPreview />
      </div>
      <div className="mt-12 text-center">
        <Button asChild size="lg">
          <Link href={`${getAppBaseUrl()}/register`}>Start writing free</Link>
        </Button>
      </div>
    </div>
  );
}
