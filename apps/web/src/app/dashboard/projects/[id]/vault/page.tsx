'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/ui/empty-state';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  Lightbulb,
  Users,
  MapPin,
  Clock,
  BookOpen,
  Search,
  Plus,
  ChevronLeft,
  Loader2,
} from 'lucide-react';
import {
  VAULT_PAGE,
  IDEA_CAPTURE,
  IDEAS_TAB,
  CHARACTER_BIBLE,
  WORLDBUILDING,
  TIMELINE,
  RESEARCH_VAULT,
  SOURCE_MANAGER,
  VAULT_SEARCH,
} from '@/content/vault-copy';
import * as Tabs from '@radix-ui/react-tabs';
import { cn } from '@/lib/utils';
import { VaultQuickCapture } from '@/components/vault/VaultQuickCapture';
import { VaultSearch } from '@/components/vault/VaultSearch';
import { CharacterCard } from '@/components/vault/CharacterCard';
import { LocationCard } from '@/components/vault/LocationCard';
import { TimelineEventCard } from '@/components/vault/TimelineEventCard';
import { SourceCard } from '@/components/vault/SourceCard';
import { IdeaCard } from '@/components/vault/IdeaCard';
import { ResearchCard } from '@/components/vault/ResearchCard';
import { CreateCharacterDialog } from '@/components/vault/CreateCharacterDialog';
import { CreateLocationDialog } from '@/components/vault/CreateLocationDialog';
import { CreateSourceDialog } from '@/components/vault/CreateSourceDialog';
import { CreateIdeaDialog } from '@/components/vault/CreateIdeaDialog';

interface VaultConfig {
  knowledge_mode: string;
  enabled_modules: string[];
  modules_with_labels: { id: string; label: string }[];
}

export default function VaultPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { toast } = useToast();
  const [config, setConfig] = useState<VaultConfig | null>(null);
  const [projectName, setProjectName] = useState('');
  const [activeTab, setActiveTab] = useState('ideas');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const [ideas, setIdeas] = useState<Record<string, unknown>[]>([]);
  const [characters, setCharacters] = useState<Record<string, unknown>[]>([]);
  const [locations, setLocations] = useState<Record<string, unknown>[]>([]);
  const [events, setEvents] = useState<Record<string, unknown>[]>([]);
  const [sources, setSources] = useState<Record<string, unknown>[]>([]);
  const [research, setResearch] = useState<Record<string, unknown>[]>([]);

  const [createOpen, setCreateOpen] = useState<'character' | 'location' | 'source' | 'idea' | null>(null);

  const fetchConfig = useCallback(() => {
    api<VaultConfig>(`/api/v1/projects/${projectId}/vault/config`)
      .then(setConfig)
      .catch(() => setConfig(null));
  }, [projectId]);

  const fetchAll = useCallback(() => {
    setLoading(true);
    Promise.all([
      api<Record<string, unknown>[]>(`/api/v1/projects/${projectId}/vault/ideas`).catch(() => []),
      api<Record<string, unknown>[]>(`/api/v1/projects/${projectId}/vault/characters`).catch(() => []),
      api<Record<string, unknown>[]>(`/api/v1/projects/${projectId}/vault/locations`).catch(() => []),
      api<Record<string, unknown>[]>(`/api/v1/projects/${projectId}/vault/timeline`).catch(() => []),
      api<Record<string, unknown>[]>(`/api/v1/projects/${projectId}/vault/sources`).catch(() => []),
      api<Record<string, unknown>[]>(`/api/v1/projects/${projectId}/vault/research`).catch(() => []),
    ])
      .then(([i, c, l, e, s, r]) => {
        setIdeas(i);
        setCharacters(c);
        setLocations(l);
        setEvents(e);
        setSources(s);
        setResearch(r);
      })
      .finally(() => setLoading(false));
  }, [projectId]);

  useEffect(() => {
    api<{ name: string }>(`/api/v1/projects/${projectId}`)
      .then((p) => setProjectName(p.name))
      .catch(() => router.push('/dashboard'));
    fetchConfig();
  }, [projectId, router, fetchConfig]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const onCreated = () => {
    setCreateOpen(null);
    fetchAll();
    toast({ title: 'Created' });
  };

  const enabled = (id: string) => config?.enabled_modules?.includes(id) ?? true;

  return (
    <div className="min-h-screen bg-gradient-to-b from-muted/20 to-background">
      <div className="p-6 lg:p-8 max-w-6xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <Link href={`/dashboard/projects/${projectId}`}>
            <Button variant="ghost" size="sm">
              <ChevronLeft className="h-4 w-4 mr-1" />
              Back
            </Button>
          </Link>
        </div>

        <PageHeader
          title={projectName ? VAULT_PAGE.title(projectName) : VAULT_PAGE.titleFallback}
          description={VAULT_PAGE.description}
          backHref={`/dashboard/projects/${projectId}`}
          backLabel="Project"
        />

        {/* Quick capture — always prominent */}
        <div className="mb-8">
          <VaultQuickCapture
            projectId={projectId}
            onCreated={fetchAll}
            placeholder={IDEA_CAPTURE.placeholder}
          />
        </div>

        {/* Search */}
        <div className="mb-6">
          <VaultSearch
            projectId={projectId}
            onSearch={setSearchQuery}
            placeholder={VAULT_SEARCH.placeholder}
            className="max-w-md"
          />
        </div>

        {/* Tabs */}
        <Tabs.Root value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <Tabs.List className="flex flex-wrap gap-2 border-b border-border/60 pb-3">
            {enabled('ideas') && (
              <Tabs.Trigger
                value="ideas"
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  activeTab === 'ideas'
                    ? 'bg-primary/10 text-primary shadow-sm'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                )}
              >
                <Lightbulb className="h-4 w-4 inline mr-2" />
                Ideas
                {ideas.length > 0 && (
                  <Badge variant="soft" className="ml-2 text-xs">
                    {ideas.length}
                  </Badge>
                )}
              </Tabs.Trigger>
            )}
            {enabled('characters') && (
              <Tabs.Trigger
                value="characters"
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  activeTab === 'characters'
                    ? 'bg-primary/10 text-primary shadow-sm'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                )}
              >
                <Users className="h-4 w-4 inline mr-2" />
                Characters
                {characters.length > 0 && (
                  <Badge variant="soft" className="ml-2 text-xs">
                    {characters.length}
                  </Badge>
                )}
              </Tabs.Trigger>
            )}
            {enabled('locations') && (
              <Tabs.Trigger
                value="locations"
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  activeTab === 'locations'
                    ? 'bg-primary/10 text-primary shadow-sm'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                )}
              >
                <MapPin className="h-4 w-4 inline mr-2" />
                World
                {locations.length > 0 && (
                  <Badge variant="soft" className="ml-2 text-xs">
                    {locations.length}
                  </Badge>
                )}
              </Tabs.Trigger>
            )}
            {enabled('timeline') && (
              <Tabs.Trigger
                value="timeline"
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  activeTab === 'timeline'
                    ? 'bg-primary/10 text-primary shadow-sm'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                )}
              >
                <Clock className="h-4 w-4 inline mr-2" />
                Timeline
                {events.length > 0 && (
                  <Badge variant="soft" className="ml-2 text-xs">
                    {events.length}
                  </Badge>
                )}
              </Tabs.Trigger>
            )}
            {enabled('research') && (
              <Tabs.Trigger
                value="research"
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  activeTab === 'research'
                    ? 'bg-primary/10 text-primary shadow-sm'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                )}
              >
                <Search className="h-4 w-4 inline mr-2" />
                Research
                {research.length > 0 && (
                  <Badge variant="soft" className="ml-2 text-xs">
                    {research.length}
                  </Badge>
                )}
              </Tabs.Trigger>
            )}
            {enabled('sources') && (
              <Tabs.Trigger
                value="sources"
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  activeTab === 'sources'
                    ? 'bg-primary/10 text-primary shadow-sm'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                )}
              >
                <BookOpen className="h-4 w-4 inline mr-2" />
                Sources
                {sources.length > 0 && (
                  <Badge variant="soft" className="ml-2 text-xs">
                    {sources.length}
                  </Badge>
                )}
              </Tabs.Trigger>
            )}
          </Tabs.List>

          {loading ? (
            <div className="flex justify-center py-20">
              <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <>
              <Tabs.Content value="ideas" className="mt-0">
                <IdeasTab
                  projectId={projectId}
                  ideas={ideas}
                  onRefresh={fetchAll}
                  onCreateClick={() => setCreateOpen('idea')}
                />
              </Tabs.Content>
              <Tabs.Content value="characters" className="mt-0">
                <CharactersTab
                  projectId={projectId}
                  characters={characters}
                  onRefresh={fetchAll}
                  onCreateClick={() => setCreateOpen('character')}
                />
              </Tabs.Content>
              <Tabs.Content value="locations" className="mt-0">
                <LocationsTab
                  projectId={projectId}
                  locations={locations}
                  onRefresh={fetchAll}
                  onCreateClick={() => setCreateOpen('location')}
                />
              </Tabs.Content>
              <Tabs.Content value="timeline" className="mt-0">
                <TimelineTab
                  projectId={projectId}
                  events={events}
                  onRefresh={fetchAll}
                />
              </Tabs.Content>
              <Tabs.Content value="research" className="mt-0">
                <ResearchTab
                  projectId={projectId}
                  research={research}
                  onRefresh={fetchAll}
                />
              </Tabs.Content>
              <Tabs.Content value="sources" className="mt-0">
                <SourcesTab
                  projectId={projectId}
                  sources={sources}
                  onRefresh={fetchAll}
                  onCreateClick={() => setCreateOpen('source')}
                />
              </Tabs.Content>
            </>
          )}
        </Tabs.Root>

        {/* Create dialogs */}
        {createOpen === 'character' && (
          <CreateCharacterDialog
            projectId={projectId}
            open
            onClose={() => setCreateOpen(null)}
            onCreated={onCreated}
          />
        )}
        {createOpen === 'location' && (
          <CreateLocationDialog
            projectId={projectId}
            open
            onClose={() => setCreateOpen(null)}
            onCreated={onCreated}
          />
        )}
        {createOpen === 'source' && (
          <CreateSourceDialog
            projectId={projectId}
            open
            onClose={() => setCreateOpen(null)}
            onCreated={onCreated}
          />
        )}
        {createOpen === 'idea' && (
          <CreateIdeaDialog
            projectId={projectId}
            open
            onClose={() => setCreateOpen(null)}
            onCreated={onCreated}
          />
        )}
      </div>
    </div>
  );
}

function IdeasTab({
  projectId,
  ideas,
  onRefresh,
  onCreateClick,
}: {
  projectId: string;
  ideas: Record<string, unknown>[];
  onRefresh: () => void;
  onCreateClick: () => void;
}) {
  if (ideas.length === 0) {
    return (
      <EmptyState
        icon={<Lightbulb className="h-6 w-6" />}
        title="No ideas yet"
        description="Capture ideas above or add structured idea cards. Everything you capture stays here."
        action={{ label: 'Add idea', onClick: onCreateClick }}
      />
    );
  }
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button size="sm" onClick={onCreateClick}>
          <Plus className="h-4 w-4 mr-2" />
          Add idea
        </Button>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {ideas.map((i) => (
          <IdeaCard key={String(i.id)} idea={i} projectId={projectId} onRefresh={onRefresh} />
        ))}
      </div>
    </div>
  );
}

function CharactersTab({
  projectId,
  characters,
  onRefresh,
  onCreateClick,
}: {
  projectId: string;
  characters: Record<string, unknown>[];
  onRefresh: () => void;
  onCreateClick: () => void;
}) {
  if (characters.length === 0) {
    return (
      <EmptyState
        icon={<Users className="h-6 w-6" />}
        title={CHARACTER_BIBLE.emptyTitle}
        description={CHARACTER_BIBLE.emptyDescription}
        action={{ label: CHARACTER_BIBLE.addCharacter, onClick: onCreateClick }}
      />
    );
  }
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button size="sm" onClick={onCreateClick}>
          <Plus className="h-4 w-4 mr-2" />
          {CHARACTER_BIBLE.addCharacter}
        </Button>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {characters.map((c) => (
          <CharacterCard key={String(c.id)} character={c} projectId={projectId} onRefresh={onRefresh} />
        ))}
      </div>
    </div>
  );
}

function LocationsTab({
  projectId,
  locations,
  onRefresh,
  onCreateClick,
}: {
  projectId: string;
  locations: Record<string, unknown>[];
  onRefresh: () => void;
  onCreateClick: () => void;
}) {
  if (locations.length === 0) {
    return (
      <EmptyState
        icon={<MapPin className="h-6 w-6" />}
        title="No locations yet"
        description="Build your world. Add places, factions, cultures, and rules."
        action={{ label: 'Add location', onClick: onCreateClick }}
      />
    );
  }
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button size="sm" onClick={onCreateClick}>
          <Plus className="h-4 w-4 mr-2" />
          Add location
        </Button>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {locations.map((l) => (
          <LocationCard key={String(l.id)} location={l} projectId={projectId} onRefresh={onRefresh} />
        ))}
      </div>
    </div>
  );
}

function TimelineTab({
  projectId,
  events,
  onRefresh,
}: {
  projectId: string;
  events: Record<string, unknown>[];
  onRefresh: () => void;
}) {
  if (events.length === 0) {
    return (
      <EmptyState
        icon={<Clock className="h-6 w-6" />}
        title={TIMELINE.emptyTitle}
        description={TIMELINE.emptyDescription}
      />
    );
  }
  const sorted = [...events].sort(
    (a, b) => (Number(a.sequence_order) ?? 0) - (Number(b.sequence_order) ?? 0)
  );
  return (
    <div className="space-y-3">
      {sorted.map((e) => (
        <TimelineEventCard key={String(e.id)} event={e} projectId={projectId} onRefresh={onRefresh} />
      ))}
    </div>
  );
}

function ResearchTab({
  projectId,
  research,
  onRefresh,
}: {
  projectId: string;
  research: Record<string, unknown>[];
  onRefresh: () => void;
}) {
  if (research.length === 0) {
    return (
      <EmptyState
        icon={<Search className="h-6 w-6" />}
        title={RESEARCH_VAULT.emptyTitle}
        description={RESEARCH_VAULT.emptyDescription}
      />
    );
  }
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {research.map((r) => (
        <ResearchCard key={String(r.id)} entry={r} projectId={projectId} onRefresh={onRefresh} />
      ))}
    </div>
  );
}

function SourcesTab({
  projectId,
  sources,
  onRefresh,
  onCreateClick,
}: {
  projectId: string;
  sources: Record<string, unknown>[];
  onRefresh: () => void;
  onCreateClick: () => void;
}) {
  if (sources.length === 0) {
    return (
      <EmptyState
        icon={<BookOpen className="h-6 w-6" />}
        title={SOURCE_MANAGER.emptyTitle}
        description={SOURCE_MANAGER.emptyDescription}
        action={{ label: SOURCE_MANAGER.addSource, onClick: onCreateClick }}
      />
    );
  }
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button size="sm" onClick={onCreateClick}>
          <Plus className="h-4 w-4 mr-2" />
          {SOURCE_MANAGER.addSource}
        </Button>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sources.map((s) => (
          <SourceCard key={String(s.id)} source={s} projectId={projectId} onRefresh={onRefresh} />
        ))}
      </div>
    </div>
  );
}
