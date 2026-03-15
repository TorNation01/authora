'use client';

import { X, BookOpen, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useHelp } from '@/contexts/HelpContext';

/**
 * Gentle first-use banner. Shown once to new users. Dismissible.
 */
export function FirstUseBanner() {
  const { hasSeenFirstUse, markFirstUseSeen, startWalkthrough, openHelpCenter } = useHelp();

  if (hasSeenFirstUse) return null;

  return (
    <div
      className="mb-6 rounded-lg border border-primary/20 bg-primary/5 p-4 flex items-start gap-4"
      data-analytics="first-use-banner"
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
        <BookOpen className="h-5 w-5 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="font-medium text-foreground">Welcome to your writing space</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Your guided journey from idea to finished book. Take a quick tour or browse the help center when you need it.
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <Button
            size="sm"
            onClick={() => {
              startWalkthrough('first-book');
              markFirstUseSeen();
            }}
          >
            <Play className="h-3.5 w-3.5 mr-1.5" />
            Quick tour
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              openHelpCenter();
              markFirstUseSeen();
            }}
          >
            Browse help
          </Button>
        </div>
      </div>
      <button
        type="button"
        onClick={markFirstUseSeen}
        aria-label="Dismiss"
        className="shrink-0 rounded p-1 text-muted-foreground hover:text-foreground"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}
