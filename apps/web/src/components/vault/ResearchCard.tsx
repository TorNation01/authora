'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Search } from 'lucide-react';

interface ResearchCardProps {
  entry: Record<string, unknown>;
  projectId: string;
  onRefresh: () => void;
}

export function ResearchCard({ entry }: ResearchCardProps) {
  const title = String(entry.title ?? '');
  const topic = entry.topic as string | undefined;
  const entryType = String(entry.entry_type ?? '');
  const needsVerification = Boolean(entry.needs_verification);
  const content = (entry.content as string)?.slice(0, 100) || '';

  return (
    <Card variant="sanctuary" className="p-4 transition-all hover:shadow-md cursor-pointer group">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Search className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-foreground">{title}</h4>
          {topic && (
            <p className="text-sm text-muted-foreground mt-0.5">{topic}</p>
          )}
          {content && (
            <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{content}…</p>
          )}
          <div className="flex gap-1.5 mt-2 flex-wrap">
            <Badge variant="soft" className="text-xs capitalize">
              {entryType.replace(/_/g, ' ')}
            </Badge>
            {needsVerification && (
              <Badge variant="secondary" className="text-xs">
                Needs verification
              </Badge>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
