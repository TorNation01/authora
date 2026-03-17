'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ONBOARDING_INTRO_OVERLAY } from '@/content/onboarding-copy';
import { Check, X } from 'lucide-react';

const INTRO_KEY = 'authora_editor_intro_seen';

export function hasSeenEditorIntro(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    return localStorage.getItem(INTRO_KEY) === 'true';
  } catch {
    return false;
  }
}

export function markEditorIntroSeen() {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(INTRO_KEY, 'true');
  } catch {
    /* ignore */
  }
}

interface EditorIntroOverlayProps {
  onComplete: () => void;
  onSkip?: () => void;
}

export function EditorIntroOverlay({ onComplete, onSkip }: EditorIntroOverlayProps) {
  const [dismissed, setDismissed] = useState(false);

  const handleComplete = () => {
    markEditorIntroSeen();
    setDismissed(true);
    onComplete();
  };

  const handleSkip = () => {
    markEditorIntroSeen();
    setDismissed(true);
    onSkip?.();
    onComplete();
  };

  if (dismissed) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-background/95 backdrop-blur-sm"
      role="dialog"
      aria-labelledby="intro-title"
      aria-modal="true"
    >
      <div className="mx-4 max-w-md rounded-2xl border border-white/[0.08] bg-card p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 id="intro-title" className="font-serif text-xl font-semibold text-foreground">
            {ONBOARDING_INTRO_OVERLAY.title}
          </h2>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            onClick={handleSkip}
            aria-label="Skip intro"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <ul className="space-y-3 mb-6">
          {ONBOARDING_INTRO_OVERLAY.points.map((point, i) => (
            <li key={i} className="flex items-start gap-3 text-sm text-muted-foreground">
              <Check className="h-4 w-4 shrink-0 text-primary mt-0.5" />
              <span>{point}</span>
            </li>
          ))}
        </ul>
        <div className="flex gap-3">
          <Button variant="outline" size="sm" onClick={handleSkip}>
            {ONBOARDING_INTRO_OVERLAY.skip}
          </Button>
          <Button size="sm" onClick={handleComplete} className="flex-1">
            {ONBOARDING_INTRO_OVERLAY.cta}
          </Button>
        </div>
      </div>
    </div>
  );
}
