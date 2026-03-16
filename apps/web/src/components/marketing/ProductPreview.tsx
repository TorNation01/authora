'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  LayoutDashboard,
  Target,
  FileText,
  Map,
  StickyNote,
  PenLine,
  Sparkles,
  Check,
  Circle,
  FileDown,
  FileImage,
  BookOpen,
} from 'lucide-react';

const SAMPLE_CHAPTER = `The old lighthouse had stood empty for twenty years. Sarah climbed the worn stone steps, her hand trailing along the rusted railing. At the top, the view opened—endless ocean, a few fishing boats, and the distant outline of the mainland.

She had come here to write. No Wi‑Fi, no distractions. Just the sound of waves and the weight of a story that had been waiting.

Sarah opened her laptop. The blank page stared back. She took a breath, and began.`;

const SAMPLE_NOTES = [
  { title: 'Research: lighthouse keepers in 1920s', type: 'research' },
  { title: 'Character: Sarah—former journalist, 42', type: 'idea' },
  { title: 'Theme: solitude vs. connection', type: 'idea' },
];

const JOURNEY_PHASES = [
  { id: 'idea', name: 'Idea', done: true },
  { id: 'concept', name: 'Concept shaping', done: true },
  { id: 'outline', name: 'Outline', done: true },
  { id: 'chapter_planning', name: 'Chapter planning', done: true },
  { id: 'drafting', name: 'Drafting', done: true, current: true },
  { id: 'revision', name: 'Revision', done: false },
  { id: 'polish', name: 'Polish', done: false },
  { id: 'export_prep', name: 'Export & publish prep', done: false },
];

const EXPORT_FORMATS = [
  { id: 'docx', label: 'Word (.docx)', desc: 'Editable, print-ready', icon: FileText },
  { id: 'pdf', label: 'PDF', desc: 'Print-ready format', icon: FileImage },
  { id: 'epub', label: 'ePub', desc: 'For e-readers', icon: FileText },
  { id: 'txt', label: 'Plain text', desc: 'Simple, universal', icon: FileText },
];

const ROTATE_INTERVAL_MS = 5000;

type SectionId = 'dashboard' | 'notes' | 'journey' | 'accountability' | 'export' | 'ai-assist';

const SECTIONS: { id: SectionId; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'dashboard', label: 'Writing studio', icon: LayoutDashboard },
  { id: 'ai-assist', label: 'AI assist', icon: Sparkles },
  { id: 'notes', label: 'Notes', icon: StickyNote },
  { id: 'journey', label: 'Journey', icon: Map },
  { id: 'accountability', label: 'Accountability', icon: Target },
  { id: 'export', label: 'Export', icon: FileText },
];

const AI_ASSIST_SELECTED = 'The blank page stared back.';
const AI_ASSIST_SUGGESTION = 'The screen glowed softly, waiting for her words.';

export function ProductPreview() {
  const [activeSection, setActiveSection] = useState<SectionId>('dashboard');
  const [userHasInteracted, setUserHasInteracted] = useState(false);

  const goNext = useCallback(() => {
    setActiveSection((prev) => {
      const idx = SECTIONS.findIndex((s) => s.id === prev);
      const next = SECTIONS[(idx + 1) % SECTIONS.length];
      return next.id;
    });
  }, []);

  useEffect(() => {
    if (userHasInteracted) return;
    const t = setInterval(goNext, ROTATE_INTERVAL_MS);
    return () => clearInterval(t);
  }, [userHasInteracted, goNext]);

  const handleSectionClick = (id: SectionId) => {
    setActiveSection(id);
    setUserHasInteracted(true);
  };

  const activeIndex = SECTIONS.findIndex((s) => s.id === activeSection);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="rounded-t-xl border border-border/60 bg-muted/40 overflow-hidden shadow-2xl">
        {/* Browser chrome */}
        <div className="flex items-center gap-2 px-3 py-2 border-b border-border/60 bg-muted/60">
          <div className="flex gap-1.5">
            <div className="h-2.5 w-2.5 rounded-full bg-red-500/80" />
            <div className="h-2.5 w-2.5 rounded-full bg-amber-500/80" />
            <div className="h-2.5 w-2.5 rounded-full bg-emerald-500/80" />
          </div>
          <div className="flex-1 flex justify-center">
            <div className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-background/80 border border-border/40 text-xs text-muted-foreground max-w-md w-full">
              <span className="text-muted-foreground/60">app.authora.studio</span>
              <span>/dashboard/{activeSection}</span>
            </div>
          </div>
          <div className="w-16" />
        </div>

        {/* Mobile section tabs */}
        <div className="sm:hidden flex gap-1 p-1.5 border-b border-border/60 bg-muted/30 overflow-x-auto">
          {SECTIONS.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => handleSectionClick(item.id)}
              className={`shrink-0 flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                activeSection === item.id
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted/60'
              }`}
            >
              <item.icon className="h-3.5 w-3.5" />
              {item.label}
            </button>
          ))}
        </div>

        {/* App content - height driven by content */}
        <div className="flex min-h-[120px]">
          {/* Sidebar (desktop) */}
          <aside className="hidden sm:flex w-36 flex-col border-r border-border/60 bg-card/80 self-stretch">
            <div className="flex h-10 items-center border-b border-border/60 px-3">
              <span className="text-base font-serif font-bold text-foreground">AUTHORA</span>
            </div>
            <nav className="flex-1 p-1.5 space-y-0.5">
              {SECTIONS.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleSectionClick(item.id)}
                  className={`w-full flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs text-left transition-colors ${
                    activeSection === item.id
                      ? 'bg-primary/10 text-primary font-medium'
                      : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
                  }`}
                >
                  <item.icon className="h-3.5 w-3.5 shrink-0" />
                  {item.label}
                </button>
              ))}
            </nav>
          </aside>

          {/* Main content area - sliding panels, height from content */}
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            <div
              className="flex transition-transform duration-500 ease-[cubic-bezier(0.4,0,0.2,1)]"
              style={{ transform: `translateX(-${activeIndex * 100}%)` }}
            >
              <div className="w-full min-w-full flex-shrink-0 flex flex-col">
                <DashboardPreview />
              </div>
              <div className="w-full min-w-full flex-shrink-0 flex flex-col">
                <AIAssistPreview />
              </div>
              <div className="w-full min-w-full flex-shrink-0 flex flex-col">
                <NotesPreview />
              </div>
              <div className="w-full min-w-full flex-shrink-0 flex flex-col">
                <JourneyPreview />
              </div>
              <div className="w-full min-w-full flex-shrink-0 flex flex-col">
                <AccountabilityPreview />
              </div>
              <div className="w-full min-w-full flex-shrink-0 flex flex-col">
                <ExportPreview />
              </div>
            </div>
          </div>
        </div>
      </div>
      {!userHasInteracted && (
        <p className="text-xs text-muted-foreground text-center mt-2">
          Click a section to explore — or watch the preview cycle automatically
        </p>
      )}
    </div>
  );
}

function DashboardPreview() {
  return (
    <>
      <div className="flex items-center gap-1 px-3 py-1.5 border-b border-border/60 bg-muted/30">
        <div className="flex gap-0.5">
          {['B', 'I', 'S'].map((c) => (
            <div
              key={c}
              className="h-6 w-6 rounded flex items-center justify-center text-[10px] font-medium text-muted-foreground bg-muted/60"
            >
              {c}
            </div>
          ))}
        </div>
        <div className="flex-1" />
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <PenLine className="h-3.5 w-3.5" />
          <span>1,247 words</span>
        </div>
      </div>
      <div className="flex-1 flex min-h-0">
        <div className="flex-1 overflow-auto p-4">
          <h1 className="font-serif text-base font-semibold text-foreground mb-3">
            Chapter 3 — The Lighthouse
          </h1>
          <div className="font-serif text-[13px] leading-relaxed text-foreground whitespace-pre-wrap">
            {SAMPLE_CHAPTER}
          </div>
        </div>
        <div className="hidden md:flex w-40 flex-col border-l border-border/60 bg-muted/20">
          <div className="px-2 py-1.5 border-b border-border/60 text-[10px] font-medium text-muted-foreground">
            Notes for this chapter
          </div>
          <div className="flex-1 p-2 space-y-1.5">
            {SAMPLE_NOTES.map((note) => (
              <div
                key={note.title}
                className="rounded-md border border-border/40 bg-background/60 px-2.5 py-2 text-xs text-muted-foreground"
              >
                {note.title}
              </div>
            ))}
          </div>
          <div className="p-2 border-t border-border/60">
            <div className="flex items-center gap-1.5 rounded-md bg-primary/10 px-2 py-1.5 text-xs text-primary">
              <Sparkles className="h-3.5 w-3.5" />
              AI assist
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function AIAssistPreview() {
  return (
    <div className="flex-1 flex min-h-0">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="px-3 py-1.5 border-b border-border/60 bg-muted/30">
          <span className="text-xs font-medium text-muted-foreground">Chapter 3 — The Lighthouse</span>
        </div>
        <div className="flex-1 p-4 flex flex-col md:flex-row gap-3 overflow-auto">
          <div className="flex-1 min-w-0">
            <p className="font-serif text-[13px] leading-relaxed text-foreground mb-3">
              Sarah opened her laptop.{' '}
              <mark className="bg-primary/20 text-foreground px-0.5 rounded">
                {AI_ASSIST_SELECTED}
              </mark>{' '}
              She took a breath, and began.
            </p>
            <p className="text-xs text-muted-foreground mb-4">Selected text</p>
            <div className="space-y-2">
              {['Rewrite', 'Expand', 'Improve flow', 'Change tone'].map((action) => (
                <div
                  key={action}
                  className={`rounded-md px-3 py-2 text-sm ${
                    action === 'Rewrite'
                      ? 'bg-primary/10 text-primary font-medium border border-primary/30'
                      : 'bg-muted/40 text-muted-foreground border border-transparent'
                  }`}
                >
                  {action}
                </div>
              ))}
            </div>
          </div>
          <div className="md:w-48 shrink-0 rounded-lg border border-primary/30 bg-primary/5 p-3">
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-xs font-medium text-primary">AI suggestion</span>
            </div>
            <p className="font-serif text-sm leading-relaxed text-foreground italic">
              &ldquo;{AI_ASSIST_SUGGESTION}&rdquo;
            </p>
            <div className="mt-3 flex gap-2">
              <span className="text-xs px-2 py-1 rounded bg-primary/20 text-primary">Apply</span>
              <span className="text-xs px-2 py-1 rounded bg-muted/60 text-muted-foreground">Regenerate</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function NotesPreview() {
  return (
    <div className="p-4 space-y-3">
      <div>
        <h2 className="font-semibold text-foreground mb-1">Ideas & notes</h2>
        <p className="text-sm text-muted-foreground">Notes for Chapter 3 — The Lighthouse</p>
      </div>
      <div className="space-y-2">
        {SAMPLE_NOTES.map((note) => (
          <div
            key={note.title}
            className="rounded-lg border border-border/60 bg-card/80 p-4"
          >
            <div className="flex items-center gap-2 mb-1">
              <StickyNote className="h-4 w-4 text-primary" />
              <span className="text-xs font-medium text-muted-foreground uppercase">{note.type}</span>
            </div>
            <p className="text-sm text-foreground">{note.title}</p>
          </div>
        ))}
      </div>
      <div className="rounded-lg border border-dashed border-border/60 p-4 text-center">
        <p className="text-xs text-muted-foreground">Quick capture • Research • Ideas • Quotes</p>
      </div>
    </div>
  );
}

function JourneyPreview() {
  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="font-semibold text-foreground mb-1">Your writing journey</h2>
        <p className="text-sm text-muted-foreground">Fiction · Solo</p>
      </div>
      <div className="rounded-lg border border-border/60 bg-muted/20 p-3">
        <div className="flex justify-between text-xs mb-2">
          <span className="text-muted-foreground">Phase 5 of 8</span>
          <span className="font-medium">Drafting</span>
        </div>
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <div className="h-full bg-primary/80 rounded-full" style={{ width: '62%' }} />
        </div>
      </div>
      <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
        <h3 className="font-medium flex items-center gap-2 mb-1">
          <Sparkles className="h-4 w-4 text-primary" />
          Your next step
        </h3>
        <p className="text-sm text-muted-foreground">Finish Chapter 3 draft</p>
      </div>
      <div className="space-y-2">
        <h3 className="font-medium flex items-center gap-2 text-sm">
          <Map className="h-4 w-4" />
          Roadmap
        </h3>
        {JOURNEY_PHASES.map((phase) => (
          <div
            key={phase.id}
            className={`flex items-center gap-3 rounded-lg border p-2.5 text-sm ${
              phase.current ? 'border-primary bg-primary/5' : phase.done ? 'opacity-75' : ''
            }`}
          >
            <div
              className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs ${
                phase.done ? 'bg-primary/20 text-primary' : phase.current ? 'bg-primary text-primary-foreground' : 'bg-muted'
              }`}
            >
              {phase.done ? <Check className="h-4 w-4" /> : phase.current ? '5' : <Circle className="h-4 w-4" />}
            </div>
            <span className={phase.done ? 'line-through text-muted-foreground' : ''}>{phase.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AccountabilityPreview() {
  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="font-semibold text-foreground mb-1">Progress</h2>
        <p className="text-sm text-muted-foreground">Goals that support you—never punish</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg border border-border/60 bg-card/80 p-4">
          <p className="text-xs text-muted-foreground mb-1">Today</p>
          <p className="text-2xl font-semibold text-foreground">847</p>
          <p className="text-xs text-muted-foreground">of 500 words</p>
          <div className="mt-2 h-1.5 rounded-full bg-muted overflow-hidden">
            <div className="h-full bg-primary/80 rounded-full" style={{ width: '100%' }} />
          </div>
        </div>
        <div className="rounded-lg border border-border/60 bg-card/80 p-4">
          <p className="text-xs text-muted-foreground mb-1">This week</p>
          <p className="text-2xl font-semibold text-foreground">3,240</p>
          <p className="text-xs text-muted-foreground">of 3,500 words</p>
          <div className="mt-2 h-1.5 rounded-full bg-muted overflow-hidden">
            <div className="h-full bg-primary/80 rounded-full" style={{ width: '92%' }} />
          </div>
        </div>
      </div>
      <div className="rounded-lg border border-border/60 bg-muted/20 p-4 flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary font-bold">
          7
        </div>
        <div>
          <p className="font-medium text-foreground">Day streak</p>
          <p className="text-xs text-muted-foreground">Keep writing to maintain your streak</p>
        </div>
      </div>
      <div className="rounded-lg border border-dashed border-border/60 p-3">
        <p className="text-xs text-muted-foreground">Reminders · Recovery plans · Milestones</p>
      </div>
    </div>
  );
}

function ExportPreview() {
  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="font-semibold text-foreground mb-1">Export</h2>
        <p className="text-sm text-muted-foreground">Download your book in any format</p>
      </div>
      <div className="rounded-lg border border-border/60 bg-muted/20 p-3">
        <div className="flex items-center gap-2 mb-2">
          <BookOpen className="h-4 w-4 text-primary" />
          <span className="font-medium">The Lighthouse</span>
        </div>
        <p className="text-xs text-muted-foreground">12 chapters · 42,180 words</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {EXPORT_FORMATS.map((f) => (
          <div
            key={f.id}
            className="rounded-lg border border-border/60 bg-card/80 p-4 flex items-start gap-3"
          >
            <f.icon className="h-8 w-8 text-primary shrink-0" />
            <div className="min-w-0">
              <p className="font-medium text-sm">{f.label}</p>
              <p className="text-xs text-muted-foreground">{f.desc}</p>
              <div className="mt-2 flex items-center gap-1.5 text-xs text-primary">
                <FileDown className="h-3.5 w-3.5" />
                Export
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="rounded-lg border border-dashed border-border/60 p-3">
        <p className="text-xs text-muted-foreground">Synopsis · Blurb · Beta reader package · Publishing prep</p>
      </div>
    </div>
  );
}
