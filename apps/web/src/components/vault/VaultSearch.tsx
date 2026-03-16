'use client';

import { useState, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Search, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import { useDebounce } from '@/hooks/useDebounce';

interface VaultSearchProps {
  projectId: string;
  onSearch?: (query: string) => void;
  placeholder?: string;
  className?: string;
}

export function VaultSearch({
  projectId,
  onSearch,
  placeholder = 'Search vault...',
  className,
}: VaultSearchProps) {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<Record<string, unknown[]> | null>(null);

  const doSearch = useCallback(
    async (q: string) => {
      if (!q.trim()) {
        setResults(null);
        return;
      }
      setSearching(true);
      try {
        const r = await api<{ results: Record<string, unknown[]> }>(
          `/api/v1/projects/${projectId}/vault/search?q=${encodeURIComponent(q)}`
        );
        setResults(r.results ?? r);
        onSearch?.(q);
      } catch {
        setResults(null);
      } finally {
        setSearching(false);
      }
    },
    [projectId, onSearch]
  );

  useDebounce(query, 400, doSearch);

  const hasResults = results && Object.values(results).some((arr) => arr.length > 0);
  const totalCount = results
    ? Object.values(results).reduce((sum, arr) => sum + arr.length, 0)
    : 0;

  return (
    <div className={cn('relative', className)}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-9 pr-9"
        />
        {searching && (
          <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
        )}
      </div>
      {query && hasResults && (
        <div className="mt-2 rounded-lg border bg-card p-3 text-sm text-muted-foreground shadow-md">
          Found {totalCount} result{totalCount !== 1 ? 's' : ''} across vault
        </div>
      )}
      {query && !searching && !hasResults && totalCount === 0 && query.length >= 2 && (
        <div className="mt-2 rounded-lg border bg-muted/30 p-3 text-sm text-muted-foreground">
          No results for &quot;{query}&quot;
        </div>
      )}
    </div>
  );
}
