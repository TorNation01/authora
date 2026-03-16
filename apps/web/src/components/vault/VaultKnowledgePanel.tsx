'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import {
  Users,
  MapPin,
  Clock,
  BookOpen,
  Search,
  Lightbulb,
  ChevronRight,
  Loader2,
} from 'lucide-react';
import { CHAPTER_KNOWLEDGE } from '@/content/vault-copy';
import { cn } from '@/lib/utils';

interface VaultKnowledgePanelProps {
  projectId: string;
  bookId: string;
  chapterId: string;
  className?: string;
}

interface KnowledgePanel {
  chapter_id: string;
  characters: Record<string, unknown>[];
  locations: Record<string, unknown>[];
  events: Record<string, unknown>[];
  themes: Record<string, unknown>[];
  sources: Record<string, unknown>[];
  research_entries: Record<string, unknown>[];
}

export function VaultKnowledgePanel({
  projectId,
  bookId,
  chapterId,
  className,
}: VaultKnowledgePanelProps) {
  const [data, setData] = useState<KnowledgePanel | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchKnowledge = useCallback(() => {
    setLoading(true);
    api<KnowledgePanel>(
      `/api/v1/projects/${projectId}/vault/books/${bookId}/chapters/${chapterId}/knowledge`
    )
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [projectId, bookId, chapterId]);

  useEffect(() => {
    fetchKnowledge();
  }, [fetchKnowledge]);

  const vaultLink = `/dashboard/projects/${projectId}/vault`;

  if (loading) {
    return (
      <div className={cn('flex flex-col border-l bg-card w-80', className)}>
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  const hasContent =
    data &&
    (data.characters.length > 0 ||
      data.locations.length > 0 ||
      data.events.length > 0 ||
      data.themes.length > 0 ||
      data.sources.length > 0 ||
      data.research_entries.length > 0);

  return (
    <div className={cn('flex flex-col border-l bg-card w-80', className)}>
      <div className="flex items-center justify-between border-b p-3">
        <h3 className="font-medium text-foreground">{CHAPTER_KNOWLEDGE.panelTitle}</h3>
        <Button variant="ghost" size="sm" asChild>
          <Link href={vaultLink}>
            {CHAPTER_KNOWLEDGE.openVault}
            <ChevronRight className="h-3.5 w-3.5 ml-1" />
          </Link>
        </Button>
      </div>
      <div className="flex-1 overflow-auto p-3 space-y-4">
        {!hasContent ? (
          <div className="text-center py-8">
            <p className="text-sm text-muted-foreground mb-3">
              {CHAPTER_KNOWLEDGE.emptyMessage}
            </p>
            <Button variant="outline" size="sm" asChild>
              <Link href={vaultLink}>{CHAPTER_KNOWLEDGE.addFromVault}</Link>
            </Button>
          </div>
        ) : (
          <>
            {data!.characters.length > 0 && (
              <Section
                icon={<Users className="h-4 w-4" />}
                title="Characters"
                items={data!.characters}
                keyFn={(c) => String(c.id)}
                labelFn={(c) => String(c.full_name ?? '')}
              />
            )}
            {data!.locations.length > 0 && (
              <Section
                icon={<MapPin className="h-4 w-4" />}
                title="Locations"
                items={data!.locations}
                keyFn={(l) => String(l.id)}
                labelFn={(l) => String(l.name ?? '')}
              />
            )}
            {data!.events.length > 0 && (
              <Section
                icon={<Clock className="h-4 w-4" />}
                title="Events"
                items={data!.events}
                keyFn={(e) => String(e.id)}
                labelFn={(e) => String(e.title ?? '')}
              />
            )}
            {data!.themes.length > 0 && (
              <Section
                icon={<Lightbulb className="h-4 w-4" />}
                title="Themes"
                items={data!.themes}
                keyFn={(t) => String(t.id)}
                labelFn={(t) => String(t.name ?? '')}
              />
            )}
            {data!.sources.length > 0 && (
              <Section
                icon={<BookOpen className="h-4 w-4" />}
                title="Sources"
                items={data!.sources}
                keyFn={(s) => String(s.id)}
                labelFn={(s) => String(s.title ?? '')}
              />
            )}
            {data!.research_entries.length > 0 && (
              <Section
                icon={<Search className="h-4 w-4" />}
                title="Research"
                items={data!.research_entries}
                keyFn={(r) => String(r.id)}
                labelFn={(r) => String(r.title ?? '')}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

function Section({
  icon,
  title,
  items,
  keyFn,
  labelFn,
}: {
  icon: React.ReactNode;
  title: string;
  items: Record<string, unknown>[];
  keyFn: (item: Record<string, unknown>) => string;
  labelFn: (item: Record<string, unknown>) => string;
}) {
  return (
    <div>
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
        {icon}
        {title}
      </div>
      <ul className="space-y-1.5">
        {items.map((item) => (
          <li
            key={keyFn(item)}
            className="text-sm rounded-md bg-muted/40 px-2.5 py-1.5 truncate"
          >
            {labelFn(item)}
          </li>
        ))}
      </ul>
    </div>
  );
}
