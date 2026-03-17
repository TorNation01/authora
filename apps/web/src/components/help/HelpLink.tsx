'use client';

import Link from 'next/link';
import { HelpCircle } from 'lucide-react';

type HelpSlug =
  | 'getting-started'
  | 'writing-with-authora'
  | 'story-integrity-engine'
  | 'story-density-engine'
  | 'ai-assistance'
  | 'account-and-billing'
  | 'export-and-publishing';

interface HelpLinkProps {
  slug: HelpSlug;
  children?: React.ReactNode;
  className?: string;
}

export function HelpLink({ slug, children, className }: HelpLinkProps) {
  return (
    <Link
      href={`/help/${slug}`}
      target="_blank"
      rel="noopener noreferrer"
      className={className ?? 'inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground'}
    >
      {children ?? (
        <>
          <HelpCircle className="h-3.5 w-3.5" />
          Learn more
        </>
      )}
    </Link>
  );
}
