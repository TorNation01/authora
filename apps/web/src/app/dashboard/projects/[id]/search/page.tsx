'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { PageHeader } from '@/components/layout/PageHeader';
import { Search, Loader2, FileText, StickyNote, BookOpen, RefreshCw } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

type SearchResult = {
  source_type: string;
  source_id: string;
  book_id: string | null;
  chapter_id: string | null;
  content_text: string;
  chunk_index: number;
  score: number;
  metadata: Record<string, unknown>;
};

export default function ProjectSearchPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [embeddingsEnabled, setEmbeddingsEnabled] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    api<{ name: string }>(`/api/v1/projects/${projectId}`)
      .then((p) => setProjectName(p.name))
      .catch(() => {});
    api<{ embeddings_enabled?: boolean }>('/api/v1/config/ai')
      .then((c) => setEmbeddingsEnabled(!!c.embeddings_enabled))
      .catch(() => {});
  }, [projectId]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const base = process.env.NEXT_PUBLIC_API_URL || '';
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const res = await fetch(
        `${base}/api/v1/projects/${projectId}/rag/search?q=${encodeURIComponent(query)}&limit=10`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
      } else {
        setResults([]);
      }
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const sourceIcon = (type: string) => {
    switch (type) {
      case 'note':
        return <StickyNote className="h-4 w-4 text-muted-foreground" />;
      case 'chapter':
        return <FileText className="h-4 w-4 text-muted-foreground" />;
      case 'chapter_brief':
      case 'outline_chapter':
        return <BookOpen className="h-4 w-4 text-muted-foreground" />;
      default:
        return <FileText className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const sourceLabel = (type: string) => {
    switch (type) {
      case 'note':
        return 'Note';
      case 'chapter':
        return 'Chapter';
      case 'chapter_brief':
        return 'Chapter brief';
      case 'outline_chapter':
        return 'Outline';
      default:
        return type;
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    try {
      const data = await api<{ indexed: number }>(`/api/v1/projects/${projectId}/rag/reindex`, {
        method: 'POST',
      });
      toast({ title: 'Reindex complete', description: `Indexed ${data.indexed} chunks` });
    } catch (e) {
      toast({ title: 'Reindex failed', variant: 'destructive' });
    } finally {
      setReindexing(false);
    }
  };

  const openSource = (r: SearchResult) => {
    if (r.source_type === 'note') {
      window.open(`/dashboard/projects/${projectId}/notes?highlight=${r.source_id}`, '_blank');
    } else if (r.source_type === 'chapter' && r.book_id) {
      window.open(`/dashboard/projects/${projectId}/books/${r.book_id}?chapter=${r.chapter_id || r.source_id}`, '_blank');
    } else if (r.book_id) {
      window.open(`/dashboard/projects/${projectId}/books/${r.book_id}`, '_blank');
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-4xl">
      <PageHeader
        title="Semantic search"
        description={`Search across notes, chapters, and outlines in ${projectName || 'this project'}`}
        backHref={`/dashboard/projects/${projectId}`}
        backLabel="Back to project"
      />

      {!embeddingsEnabled ? (
        <Card variant="soft">
          <CardContent className="pt-6">
            <p className="text-muted-foreground">
              Semantic search is not configured. Enable embeddings (Ollama) in Admin → AI providers to enable
              project search.
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="flex flex-col sm:flex-row gap-2 mb-6">
            <div className="flex gap-2 flex-1">
            <Input
              placeholder="Search by meaning... (e.g. 'the main character discovers the secret')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1"
            />
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              Search
            </Button>
            </div>
            <Button variant="outline" onClick={handleReindex} disabled={reindexing}>
              {reindexing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Reindex project
            </Button>
          </div>

          {results.length > 0 && (
            <div className="space-y-4">
              <h3 className="font-medium">Results</h3>
              {results.map((r, i) => (
                <Card key={i} variant="soft">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-sm text-muted-foreground">
                        {sourceIcon(r.source_type)}
                        {sourceLabel(r.source_type)}
                        {r.metadata?.title ? ` · ${String(r.metadata.title)}` : null}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {Math.round(r.score * 100)}% match
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-foreground line-clamp-3">{r.content_text}</p>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="mt-2"
                      onClick={() => openSource(r)}
                    >
                      Open source
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {results.length === 0 && query && !loading && (
            <p className="text-muted-foreground">No results. Try reindexing via Admin → AI providers.</p>
          )}
        </>
      )}
    </div>
  );
}
