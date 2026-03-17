'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { TUTORIAL_OVERLAYS } from '@/content/tutorial-copy';
import { ChevronRight, X } from 'lucide-react';
import type { TutorialId } from '@/contexts/TutorialContext';

interface GuidedOverlayProps {
  tutorialId: 'editor_first' | 'ai_first' | 'integrity_first' | 'density_first';
  onComplete: () => void;
  onSkip?: () => void;
}

export function GuidedOverlay({ tutorialId, onComplete, onSkip }: GuidedOverlayProps) {
  const [step, setStep] = useState(0);
  const content = TUTORIAL_OVERLAYS[tutorialId];
  if (!content) return null;

  const steps = content.steps;
  const isLast = step >= steps.length - 1;

  const handleNext = () => {
    if (isLast) {
      onComplete();
    } else {
      setStep((s) => s + 1);
    }
  };

  const handleSkip = () => {
    onSkip?.();
    onComplete();
  };

  return (
    <div
      className="fixed inset-0 z-[99990] flex items-center justify-center bg-background/90 backdrop-blur-sm"
      role="dialog"
      aria-labelledby="tutorial-title"
      aria-modal="true"
    >
      <div className="mx-4 max-w-md rounded-2xl border border-white/[0.08] bg-card p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 id="tutorial-title" className="font-serif text-xl font-semibold text-foreground">
            {content.title}
          </h2>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            onClick={handleSkip}
            aria-label="Skip"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-sm text-muted-foreground mb-6">{steps[step]?.text}</p>
        <div className="flex items-center justify-between">
          <Button variant="ghost" size="sm" onClick={handleSkip}>
            {content.skip}
          </Button>
          <div className="flex gap-2">
            {steps.length > 1 && (
              <span className="text-xs text-muted-foreground self-center">
                {step + 1} / {steps.length}
              </span>
            )}
            <Button size="sm" onClick={handleNext}>
              {isLast ? content.cta : (
                <>
                  Next
                  <ChevronRight className="h-3 w-3 ml-1" />
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
