'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PenLine, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';
import { DAILY_PROMPT_COPY } from '@/content/accountability-copy';

interface DailyPromptResponse {
  prompt: string;
  date: string;
  source: 'template' | 'generic';
}

export function DailyPromptCard() {
  const [data, setData] = useState<DailyPromptResponse | null>(null);

  useEffect(() => {
    api<DailyPromptResponse>('/api/v1/accountability/daily-prompt')
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) return null;

  return (
    <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Sparkles className="h-5 w-5" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            {DAILY_PROMPT_COPY.heading}
          </p>
          <p className="mt-1 text-sm text-foreground leading-relaxed">{data.prompt}</p>
          <p className="mt-2 text-xs text-muted-foreground">{DAILY_PROMPT_COPY.optionalHint}</p>
          <Button asChild variant="outline" size="sm" className="mt-3">
            <Link href="/dashboard">
              <PenLine className="h-3.5 w-3.5 mr-1.5" />
              {DAILY_PROMPT_COPY.startWriting}
            </Link>
          </Button>
        </div>
      </div>
    </Card>
  );
}
