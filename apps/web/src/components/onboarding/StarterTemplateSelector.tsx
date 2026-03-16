'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { StarterTemplateCard } from './StarterTemplateCard';
import {
  STARTER_TEMPLATES,
  STARTER_GROUPS,
  type StarterTemplate,
} from '@/content/starter-templates';
import { api } from '@/lib/api';
import { Loader2, Search } from 'lucide-react';

type StarterWithTemplateId = StarterTemplate & { templateId: string | null };

interface StarterTemplateSelectorProps {
  onUseStarter: (starter: StarterWithTemplateId, quickCreate?: boolean) => void;
  onCustomize: (starter: StarterWithTemplateId) => void;
  onStartBlank: () => void;
}

export function StarterTemplateSelector({
  onUseStarter,
  onCustomize,
  onStartBlank,
}: StarterTemplateSelectorProps) {
  const [templateIdMap, setTemplateIdMap] = useState<Record<string, string | null>>({});
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api<{ id: string; template_id: string | null }[]>('/api/v1/templates/starters')
      .then((list) => {
        const map: Record<string, string | null> = {};
        for (const s of list) {
          map[s.id] = s.template_id;
        }
        setTemplateIdMap(map);
      })
      .catch(() => setTemplateIdMap({}))
      .finally(() => setLoading(false));
  }, []);

  const startersWithIds: StarterWithTemplateId[] = STARTER_TEMPLATES.map((s) => ({
    ...s,
    templateId: templateIdMap[s.id] ?? null,
  }));

  const filtered = search.trim()
    ? startersWithIds.filter(
        (s) =>
          s.name.toLowerCase().includes(search.toLowerCase()) ||
          s.shortDescription.toLowerCase().includes(search.toLowerCase()) ||
          s.whoItIsFor.toLowerCase().includes(search.toLowerCase())
      )
    : startersWithIds;

  const byGroup = filtered.reduce<Record<string, StarterWithTemplateId[]>>((acc, s) => {
    (acc[s.group] ??= []).push(s);
    return acc;
  }, {});

  const groupOrder: (keyof typeof STARTER_GROUPS)[] = ['fiction', 'nonfiction', 'other'];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search starters..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>
      <div className="space-y-8">
        {groupOrder.map((group) => {
          const items = byGroup[group];
          if (!items?.length) return null;
          return (
            <div key={group}>
              <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4">
                {STARTER_GROUPS[group]}
              </h3>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {items.map((starter) => (
                  <StarterTemplateCard
                    key={starter.id}
                    starter={starter}
                    templateId={starter.templateId}
                    onUseStarter={() => onUseStarter(starter)}
                    onCustomize={() => onCustomize(starter)}
                    onStartBlank={onStartBlank}
                    canSaveAsTemplate={false}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
