'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BookOpen } from 'lucide-react';

interface SourceCardProps {
  source: Record<string, unknown>;
  projectId: string;
  onRefresh: () => void;
}

const STATUS_LABELS: Record<string, string> = {
  verified: 'Verified',
  unverified: 'Unverified',
  needs_review: 'Needs review',
};

export function SourceCard({ source }: SourceCardProps) {
  const title = String(source.title ?? '');
  const author = source.author as string | undefined;
  const sourceType = String(source.source_type ?? '');
  const status = String(source.status ?? 'needs_review');

  return (
    <Card variant="sanctuary" className="p-4 transition-all hover:shadow-md cursor-pointer group">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
          <BookOpen className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-foreground">{title}</h4>
          {author && (
            <p className="text-sm text-muted-foreground mt-0.5">{author}</p>
          )}
          <div className="flex gap-1.5 mt-2 flex-wrap">
            <Badge variant="soft" className="text-xs capitalize">
              {sourceType}
            </Badge>
            <Badge
              variant={status === 'verified' ? 'default' : 'outline'}
              className="text-xs"
            >
              {STATUS_LABELS[status] ?? status}
            </Badge>
          </div>
        </div>
      </div>
    </Card>
  );
}
