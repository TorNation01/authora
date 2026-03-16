'use client';

import { FileText, Layers, StickyNote, BarChart3, Focus, Sparkles } from 'lucide-react';

const EDITOR_FEATURES = [
  { icon: FileText, label: 'Manuscript editor' },
  { icon: Layers, label: 'Chapter-based writing' },
  { icon: StickyNote, label: 'Notes and highlights' },
  { icon: BarChart3, label: 'Progress tracking' },
  { icon: Focus, label: 'Focus writing modes' },
  { icon: Sparkles, label: 'AI help beside your writing, not in the way of it' },
];

export function EditorSection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="editor">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            A real writing workspace, not just an AI chat box
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Authora includes a full manuscript editor built for real writing. Organize chapters,
            draft comfortably, keep notes close, track progress, and use AI support without losing
            the flow of your work.
          </p>
        </div>
        <div className="mt-12 flex flex-wrap justify-center gap-4">
          {EDITOR_FEATURES.map((item) => (
            <div
              key={item.label}
              className="flex items-center gap-3 rounded-lg border border-border/60 bg-card px-4 py-3"
              data-analytics="editor-feature"
            >
              <item.icon className="h-5 w-5 text-primary" />
              <span className="text-sm font-medium text-foreground">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
