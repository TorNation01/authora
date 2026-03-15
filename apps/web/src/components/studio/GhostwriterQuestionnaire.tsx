'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Sparkles, ArrowRight, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

interface GhostwriterQuestionnaireProps {
  onGenerate: (answers: Record<string, string>) => void;
  onOutput: (text: string) => void;
  loading?: boolean;
  className?: string;
}

const STEPS = [
  {
    id: 'topic',
    label: 'What is this section about?',
    placeholder: 'e.g. The protagonist discovers the hidden letter',
  },
  {
    id: 'tone',
    label: 'What tone or mood?',
    placeholder: 'e.g. Tense, mysterious, hopeful',
  },
  {
    id: 'length',
    label: 'Approximate length?',
    placeholder: 'e.g. 2-3 paragraphs, 500 words',
  },
  {
    id: 'constraints',
    label: 'Any constraints or must-include elements?',
    placeholder: 'e.g. Must mention the red door, end on a cliffhanger',
  },
];

export function GhostwriterQuestionnaire({
  onGenerate,
  onOutput,
  loading,
  className,
}: GhostwriterQuestionnaireProps) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const current = STEPS[step];
  const value = answers[current.id] ?? '';

  function handleNext() {
    if (value.trim()) {
      setAnswers((a) => ({ ...a, [current.id]: value.trim() }));
      if (step < STEPS.length - 1) {
        setStep((s) => s + 1);
      } else {
        const final = { ...answers, [current.id]: value.trim() };
        onGenerate(final);
      }
    }
  }

  function handleBack() {
    if (step > 0) setStep((s) => s - 1);
  }

  const context = Object.entries(answers)
    .concat(value ? [[current.id, value]] : [])
    .map(([k, v]) => {
      const s = STEPS.find((x) => x.id === k);
      return `${s?.label || k}: ${v}`;
    })
    .join('\n');

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center gap-2 text-primary">
        <Sparkles className="h-5 w-5" />
        <h3 className="font-semibold">Ghostwriter mode</h3>
      </div>
      <p className="text-sm text-muted-foreground">
        Answer a few questions to guide the AI. It will generate a full section from your inputs.
      </p>

      <div className="space-y-4">
        <div>
          <Label htmlFor={current.id}>{current.label}</Label>
          <Input
            id={current.id}
            value={value}
            onChange={(e) => setAnswers((a) => ({ ...a, [current.id]: e.target.value }))}
            placeholder={current.placeholder}
            className="mt-2"
          />
        </div>

        <div className="flex justify-between">
          <Button variant="ghost" size="sm" onClick={handleBack} disabled={step === 0}>
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
          <Button
            size="sm"
            onClick={handleNext}
            disabled={!value.trim() || loading}
          >
            {step < STEPS.length - 1 ? (
              <>
                Next
                <ArrowRight className="h-4 w-4 ml-1" />
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-1" />
                Generate
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="text-xs text-muted-foreground">
        Step {step + 1} of {STEPS.length}
      </div>
    </div>
  );
}
