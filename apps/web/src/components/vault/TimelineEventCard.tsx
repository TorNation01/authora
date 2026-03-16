'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock } from 'lucide-react';

interface TimelineEventCardProps {
  event: Record<string, unknown>;
  projectId: string;
  onRefresh: () => void;
}

export function TimelineEventCard({ event }: TimelineEventCardProps) {
  const title = String(event.title ?? '');
  const dateLabel = event.date_label as string | undefined;
  const eventDate = event.event_date as string | undefined;
  const eventType = String(event.event_type ?? '');
  const description = (event.description as string)?.slice(0, 120) || '';

  const dateDisplay = dateLabel || eventDate || '';

  return (
    <Card variant="sanctuary" className="p-4 transition-all hover:shadow-md cursor-pointer flex gap-4">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Clock className="h-5 w-5" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h4 className="font-semibold text-foreground">{title}</h4>
          {dateDisplay && (
            <span className="text-xs text-muted-foreground">{dateDisplay}</span>
          )}
        </div>
        <Badge variant="soft" className="text-xs mt-1 capitalize">
          {eventType.replace(/_/g, ' ')}
        </Badge>
        {description && (
          <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{description}</p>
        )}
      </div>
    </Card>
  );
}
