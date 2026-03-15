'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/layout/PageHeader';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  FileText,
  Copy,
  Download,
  Loader2,
  BookOpen,
  Sparkles,
  Users,
  User,
  Package,
  Printer,
  Tablet,
} from 'lucide-react';

interface PrepResult {
  type: string;
  content: string;
}

const PREP_TYPES = [
  { id: 'synopsis', label: 'Synopsis', desc: 'Full plot summary for agents/editors', icon: FileText },
  { id: 'blurb', label: 'Back cover blurb', desc: 'Marketing copy for the back cover', icon: BookOpen },
  { id: 'chapter_summaries', label: 'Chapter summaries', desc: 'One-paragraph per chapter', icon: FileText },
  { id: 'beta_pack', label: 'Beta reader pack', desc: 'Package for beta readers', icon: Users },
  { id: 'author_bio', label: 'Author bio draft', desc: 'Short bio for marketing', icon: User },
  { id: 'handoff_pack', label: 'Manuscript handoff pack', desc: 'Everything for your editor', icon: Package },
];

export default function PublishingPrepPage() {
  const params = useParams();
  const bookId = params.bookId as string;
  const { toast } = useToast();
  const [bookTitle, setBookTitle] = useState<string>('');
  const [loading, setLoading] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!bookId) return;
    api<Array<{ id: string }>>('/api/v1/projects')
      .then(async (projects) => {
        for (const p of projects) {
          const books = await api<Array<{ id: string; title: string }>>(`/api/v1/projects/${p.id}/books`);
          const b = books.find((x) => x.id === bookId);
          if (b) {
            setBookTitle(b.title);
            return;
          }
        }
      })
      .catch(() => {});
  }, [bookId]);

  const generate = async (prepType: string) => {
    setLoading(prepType);
    try {
      const res = await api<PrepResult>(`/api/v1/export/books/${bookId}/publishing-prep/${prepType}`);
      setResults((prev) => ({ ...prev, [prepType]: res.content }));
      toast({ title: `${PREP_TYPES.find((p) => p.id === prepType)?.label ?? prepType} generated` });
    } catch (e) {
      toast({
        title: 'Generation failed',
        description: e instanceof Error ? e.message : 'AI may not be configured.',
        variant: 'destructive',
      });
    } finally {
      setLoading(null);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({ title: 'Copied to clipboard' });
  };

  const downloadAsTxt = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    toast({ title: 'Download started' });
  };

  return (
    <div className="p-6 lg:p-8 max-w-4xl">
      <PageHeader
        title="Publishing prep"
        description="Create synopsis, blurbs, chapter summaries, and materials for agents or self-publishing."
        backHref="/dashboard/export"
        backLabel="Back to export"
      />

      {bookId ? (
        <div className="space-y-6">
          <p className="text-sm text-muted-foreground">
            Book: <span className="font-medium text-foreground">{bookTitle || 'Loading...'}</span>
          </p>

          <div className="grid gap-4 sm:grid-cols-2">
            {PREP_TYPES.map((prep) => (
              <Card key={prep.id} variant="soft" className="overflow-hidden">
                <CardHeader className="pb-2">
                  <div className="flex items-start gap-3">
                    <prep.icon className="h-6 w-6 text-primary shrink-0" />
                    <div>
                      <h3 className="font-semibold">{prep.label}</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">{prep.desc}</p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button
                    size="sm"
                    onClick={() => generate(prep.id)}
                    disabled={!!loading}
                  >
                    {loading === prep.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Sparkles className="h-4 w-4" />
                    )}
                    Generate
                  </Button>
                  {results[prep.id] && (
                    <div className="space-y-2">
                      <pre className="text-xs bg-muted/50 rounded-lg p-3 max-h-48 overflow-auto whitespace-pre-wrap font-sans">
                        {results[prep.id]}
                      </pre>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => copyToClipboard(results[prep.id])}
                        >
                          <Copy className="h-3 w-3" />
                          Copy
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            downloadAsTxt(
                              results[prep.id],
                              `${bookTitle || 'book'}_${prep.id}.txt`
                            )
                          }
                        >
                          <Download className="h-3 w-3" />
                          Download
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          <Card variant="soft" className="p-6">
            <h3 className="font-semibold mb-2">Formatting guides</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Use the export center to get print-friendly or ebook-friendly formatting.
            </p>
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/export">
                  <Printer className="h-4 w-4" />
                  Print manuscript
                </Link>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/export">
                  <Tablet className="h-4 w-4" />
                  Ebook format
                </Link>
              </Button>
            </div>
          </Card>
        </div>
      ) : (
        <Card variant="soft" className="p-8">
          <p className="text-muted-foreground">No book selected.</p>
          <Button asChild className="mt-4">
            <Link href="/dashboard/export">Choose a book</Link>
          </Button>
        </Card>
      )}
    </div>
  );
}
