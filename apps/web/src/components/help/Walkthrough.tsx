'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useHelp } from '@/contexts/HelpContext';

export interface WalkthroughStep {
  id: string;
  title: string;
  description: string;
  /** Optional: selector for spotlight (future enhancement) */
  target?: string;
}

export interface WalkthroughConfig {
  id: string;
  title: string;
  steps: WalkthroughStep[];
}

const WALKTHROUGHS: Record<string, WalkthroughConfig> = {
  'first-book': {
    id: 'first-book',
    title: 'Create your first book',
    steps: [
      {
        id: 'create-project',
        title: 'Create a project',
        description: 'A project holds one or more books. Click "New project" and give it a name.',
      },
      {
        id: 'add-book',
        title: 'Add a book',
        description: 'Inside the project, click "Add book". Choose a template (fiction or non-fiction) or start from scratch.',
      },
      {
        id: 'outline',
        title: 'Build your outline',
        description: 'Add chapters in the sidebar. A one-sentence summary per chapter is enough to start.',
      },
      {
        id: 'write',
        title: 'Start writing',
        description: 'Click a chapter to open the editor. Type or use Ghostwriter to generate a draft from your outline.',
      },
    ],
  },
  'editor-tour': {
    id: 'editor-tour',
    title: 'Editor tour',
    steps: [
      {
        id: 'sidebar',
        title: 'Manuscript sidebar',
        description: 'Your outline lives here. Add chapters, reorder, and add briefs. Click a chapter to edit.',
      },
      {
        id: 'ai-panel',
        title: 'AI panel',
        description: 'Select text to rewrite, expand, or continue. Or use Ghostwriter for full chapter drafts.',
      },
      {
        id: 'notes',
        title: 'Notes',
        description: 'Research, ideas, character sheets. Link notes to chapters for easy reference while writing.',
      },
      {
        id: 'export',
        title: 'Export',
        description: 'When ready, export to DOCX, PDF, or EPUB. One click from the toolbar.',
      },
    ],
  },
};

export function Walkthrough() {
  const { activeWalkthrough, endWalkthrough } = useHelp();
  const [stepIndex, setStepIndex] = useState(0);

  const config = activeWalkthrough ? WALKTHROUGHS[activeWalkthrough] : null;
  const step = config?.steps[stepIndex];

  useEffect(() => {
    if (activeWalkthrough) setStepIndex(0);
  }, [activeWalkthrough]);

  if (!config || !step) return null;

  const isLast = stepIndex >= config.steps.length - 1;

  return (
    <Dialog open={!!activeWalkthrough} onOpenChange={(open) => !open && endWalkthrough()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{config.title}</DialogTitle>
          <DialogDescription>
            Step {stepIndex + 1} of {config.steps.length}
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <h3 className="font-semibold text-foreground">{step.title}</h3>
          <p className="mt-2 text-sm text-muted-foreground">{step.description}</p>
        </div>
        <DialogFooter>
          {stepIndex > 0 ? (
            <Button variant="outline" onClick={() => setStepIndex((i) => i - 1)}>
              Back
            </Button>
          ) : (
            <div />
          )}
          {isLast ? (
            <Button onClick={endWalkthrough}>Done</Button>
          ) : (
            <Button onClick={() => setStepIndex((i) => i + 1)}>Next</Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function getWalkthrough(id: string): WalkthroughConfig | undefined {
  return WALKTHROUGHS[id];
}
