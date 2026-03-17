'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, BookOpen, ChevronRight } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { HELP_NAV, searchHelpPages, type HelpPage } from '@/content/help-pages';
import { cn } from '@/lib/utils';

export default function HelpLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<HelpPage[] | null>(null);
  const [focused, setFocused] = useState(false);

  const handleSearch = useCallback((value: string) => {
    setQuery(value);
    setResults(value.trim() ? searchHelpPages(value) : null);
  }, []);

  const showResults = focused && query.trim().length > 0;

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-8 lg:flex-row lg:gap-16">
        {/* Sidebar */}
        <aside className="shrink-0 lg:w-56">
          <Link
            href="/help"
            className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground mb-6"
          >
            <BookOpen className="h-4 w-4" />
            Help center
          </Link>
          <nav className="space-y-1">
            {HELP_NAV.map((item) => {
              const href = item.slug ? `/help/${item.slug}` : '/help';
              const isActive = pathname === href;
              return (
                <Link
                  key={item.slug}
                  href={href}
                  className={cn(
                    'block rounded-lg px-3 py-2 text-sm transition-colors',
                    isActive
                      ? 'bg-primary/10 text-primary font-medium'
                      : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
                  )}
                >
                  {item.title}
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main content + search */}
        <div className="flex-1 min-w-0">
          <div className="relative mb-8">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search help…"
              value={query}
              onChange={(e) => handleSearch(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setTimeout(() => setFocused(false), 150)}
              className="pl-9 max-w-md"
            />
            {showResults && (
              <div className="absolute top-full left-0 right-0 mt-1 max-w-md rounded-lg border border-border bg-background shadow-lg z-10 py-2">
                {results && results.length > 0 ? (
                  results.map((page) => (
                    <Link
                      key={page.slug}
                      href={`/help/${page.slug}`}
                      className="flex items-center justify-between gap-2 px-4 py-2 text-sm hover:bg-muted/50"
                      onClick={() => {
                        setQuery('');
                        setResults(null);
                      }}
                    >
                      <span className="font-medium">{page.title}</span>
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    </Link>
                  ))
                ) : (
                  <p className="px-4 py-3 text-sm text-muted-foreground">
                    No results for &quot;{query}&quot;
                  </p>
                )}
              </div>
            )}
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
