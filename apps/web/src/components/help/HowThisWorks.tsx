'use client';

import { useState } from 'react';
import { ChevronDown, HelpCircle, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useHelp } from '@/contexts/HelpContext';

interface HowThisWorksProps {
  /** Panel title */
  title: string;
  /** Short summary (always visible) */
  summary: string;
  /** Full content (expandable) */
  children: React.ReactNode;
  /** Optional: link to help center article */
  articleId?: string;
  className?: string;
}

/**
 * Collapsible "How this works" panel. Reduces overwhelm by showing summary first.
 */
export function HowThisWorks({
  title,
  summary,
  children,
  articleId,
  className,
}: HowThisWorksProps) {
  const [expanded, setExpanded] = useState(false);
  const { openHelpCenter } = useHelp();

  return (
    <div
      className={cn(
        'rounded-lg border border-border/60 bg-muted/30 overflow-hidden',
        className
      )}
    >
      <div className="flex items-start gap-3 p-4">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
          <HelpCircle className="h-4 w-4 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-foreground">{title}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{summary}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setExpanded(!expanded)}
              className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
            >
              {expanded ? 'Show less' : 'How this works'}
              <ChevronDown
                className={cn('h-4 w-4 transition-transform', expanded && 'rotate-180')}
              />
            </button>
            {articleId && (
              <button
                type="button"
                onClick={() => openHelpCenter(articleId)}
                className="inline-flex items-center gap-1 text-sm font-medium text-muted-foreground hover:text-foreground"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                Learn more
              </button>
            )}
          </div>
        </div>
      </div>
      {expanded && (
        <div className="border-t border-border/60 px-4 py-4 bg-background/50">
          <div className="prose-sanctuary text-sm">{children}</div>
        </div>
      )}
    </div>
  );
}
