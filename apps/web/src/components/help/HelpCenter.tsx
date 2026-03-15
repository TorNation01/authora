'use client';

import { useState, useEffect } from 'react';
import { Search, X, BookOpen, ChevronRight } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useHelp } from '@/contexts/HelpContext';
import {
  HELP_ARTICLES,
  HELP_CATEGORIES,
  searchArticles,
  getArticle,
  type HelpArticle,
} from '@/content/help-center';

export function HelpCenter() {
  const { isHelpCenterOpen, closeHelpCenter, initialArticleId, setInitialArticleId } = useHelp();
  const [query, setQuery] = useState('');
  const [selectedArticle, setSelectedArticle] = useState<HelpArticle | null>(null);
  const [filter, setFilter] = useState<string | null>(null);

  const articles = query.trim() ? searchArticles(query) : HELP_ARTICLES;
  const filteredArticles = filter
    ? articles.filter((a) => a.tags.includes(filter))
    : articles;

  useEffect(() => {
    if (initialArticleId) {
      const article = getArticle(initialArticleId);
      if (article) setSelectedArticle(article);
      setInitialArticleId(null);
    } else if (!initialArticleId && isHelpCenterOpen) {
      setSelectedArticle(null);
      setFilter(null);
      setQuery('');
    }
  }, [initialArticleId, isHelpCenterOpen, setInitialArticleId]);

  return (
    <Sheet open={isHelpCenterOpen} onOpenChange={(open) => !open && closeHelpCenter()}>
      <SheetContent side="right" className="w-full sm:max-w-lg flex flex-col p-0">
        <SheetHeader className="border-b border-border/60 px-6 py-4 shrink-0">
          <div className="flex items-center justify-between">
            <SheetTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary" />
              Help center
            </SheetTitle>
            <Button variant="ghost" size="icon" onClick={closeHelpCenter} aria-label="Close">
              <X className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Find answers when you need them. Gentle guidance, no overwhelm.
          </p>
          <div className="relative mt-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="What would you like help with?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </SheetHeader>

        <div className="flex-1 overflow-auto">
          {selectedArticle ? (
            <div className="p-6">
              <Button
                variant="ghost"
                size="sm"
                className="mb-4 -ml-2"
                onClick={() => setSelectedArticle(null)}
              >
                ← Back to all
              </Button>
              <h2 className="font-serif text-xl font-semibold text-foreground">
                {selectedArticle.title}
              </h2>
              <p className="mt-2 text-sm text-muted-foreground">{selectedArticle.summary}</p>
              <div className="mt-6 space-y-4">
                {selectedArticle.body.map((para, i) => (
                  <p key={i} className="text-sm leading-relaxed text-foreground">
                    {para}
                  </p>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-6">
              {!query && (
                <div className="mb-6">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
                    Browse by topic
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {HELP_CATEGORIES.map((cat) => (
                      <button
                        key={cat.id}
                        type="button"
                        onClick={() => setFilter(filter === cat.id ? null : cat.id)}
                        className={`rounded-full px-3 py-1.5 text-sm transition-colors ${
                          filter === cat.id
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted/60 text-muted-foreground hover:bg-muted'
                        }`}
                      >
                        {cat.icon} {cat.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <div className="space-y-2">
                {filteredArticles.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-8 text-center">
                    No articles found. Try a different search.
                  </p>
                ) : (
                  filteredArticles.map((article) => (
                    <button
                      key={article.id}
                      type="button"
                      onClick={() => setSelectedArticle(article)}
                      className="w-full text-left rounded-lg border border-border/60 p-4 hover:bg-muted/50 transition-colors group"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h3 className="font-medium text-foreground group-hover:text-primary">
                            {article.title}
                          </h3>
                          <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                            {article.summary}
                          </p>
                        </div>
                        <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
