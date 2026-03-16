'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Pin, Star, MoreHorizontal, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface IdeaCardProps {
  idea: Record<string, unknown>;
  projectId: string;
  onRefresh: () => void;
}

const STATUS_LABELS: Record<string, string> = {
  raw_idea: 'Raw',
  maybe_later: 'Later',
  planned: 'Planned',
  used: 'Used',
  archived: 'Archived',
};

export function IdeaCard({ idea, projectId, onRefresh }: IdeaCardProps) {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const title = String(idea.title ?? '');
  const content = String(idea.content ?? '');
  const status = String(idea.status ?? 'raw_idea');
  const pinned = Boolean(idea.pinned);
  const starred = Boolean(idea.starred);
  const tags = (idea.tags as string[]) ?? [];

  const toggle = async (field: 'pinned' | 'starred', value: boolean) => {
    setLoading(true);
    try {
      await api(`/api/v1/projects/${projectId}/vault/ideas/${idea.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ [field]: value }),
      });
      onRefresh();
    } catch {
      toast({ title: 'Failed to update', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      variant="sanctuary"
      className={cn(
        'group p-4 transition-all hover:shadow-md cursor-pointer',
        pinned && 'ring-1 ring-primary/20'
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-foreground truncate">{title}</h4>
          <p className="text-sm text-muted-foreground mt-0.5 line-clamp-2">{content}</p>
        </div>
        <div className="flex items-center gap-4 shrink-0">
          <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={(e) => {
                e.stopPropagation();
                toggle('pinned', !pinned);
              }}
              disabled={loading}
            >
              <Pin className={cn('h-3.5 w-3', pinned && 'fill-primary text-primary')} />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={(e) => {
                e.stopPropagation();
                toggle('starred', !starred);
              }}
              disabled={loading}
            >
              <Star className={cn('h-3.5 w-3', starred && 'fill-amber-500 text-amber-500')} />
            </Button>
          </div>
        </div>
      </div>
      <div className="flex flex-wrap gap-1.5 mt-3">
        <Badge variant="soft" className="text-xs">
          {STATUS_LABELS[status] ?? status}
        </Badge>
        {tags.slice(0, 3).map((t) => (
          <Badge key={t} variant="outline" className="text-xs">
            {t}
          </Badge>
        ))}
      </div>
    </Card>
  );
}
