'use client';

import { Button } from '@/components/ui/button';
import { FEATURE_INTRO_CARDS } from '@/content/tutorial-copy';
import { X } from 'lucide-react';
import type { TutorialId } from '@/contexts/TutorialContext';

type IntroCardId = 'integrity' | 'density' | 'finish_mode';

interface FeatureIntroCardProps {
  featureId: IntroCardId;
  onDismiss: () => void;
  onTry?: () => void;
}

export function FeatureIntroCard({ featureId, onDismiss, onTry }: FeatureIntroCardProps) {
  const content = FEATURE_INTRO_CARDS[featureId];
  if (!content) return null;

  return (
    <div className="rounded-xl border border-primary/20 bg-primary/5 p-4 relative">
      <Button
        variant="ghost"
        size="icon"
        className="absolute right-2 top-2 h-7 w-7 text-muted-foreground hover:text-foreground"
        onClick={onDismiss}
        aria-label="Dismiss"
      >
        <X className="h-3.5 w-3.5" />
      </Button>
      <h4 className="font-semibold text-foreground pr-8">{content.title}</h4>
      <p className="text-sm text-muted-foreground mt-1">{content.description}</p>
      <p className="text-xs text-muted-foreground mt-2 italic">Why it matters: {content.why}</p>
      {onTry && (
        <Button size="sm" className="mt-4" onClick={onTry}>
          {content.cta}
        </Button>
      )}
    </div>
  );
}
