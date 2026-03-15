'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/layout/PageHeader';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  FileDown,
  FileText,
  FileImage,
  List,
  StickyNote,
  Loader2,
  BookOpen,
} from 'lucide-react';
import { HelpIcon, HowThisWorks } from '@/components/help';

interface Project {
  id: string;
  name: string;
}

interface Book {
  id: string;
  title: string;
  project_id: string;
}

interface ExportPreview {
  book_title: string;
  chapter_count: number;
  total_words: number;
  chapters: Array<{ title: string; word_count: number }>;
}

const FORMATS = [
  { id: 'docx', label: 'Word (.docx)', desc: 'Editable, print-ready', icon: FileText },
  { id: 'pdf', label: 'PDF', desc: 'Print-ready format', icon: FileImage },
  { id: 'epub', label: 'ePub', desc: 'For e-readers', icon: FileText },
  { id: 'txt', label: 'Plain text', desc: 'Simple, universal', icon: FileText },
];

export default function ExportCenterPage() {
  const { toast } = useToast();
  const [projects, setProjects] = useState<Project[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [preview, setPreview] = useState<ExportPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState<string | null>(null);
  const [includeTitlePage, setIncludeTitlePage] = useState(true);
  const [includeToc, setIncludeToc] = useState(true);
  const [authorName, setAuthorName] = useState('');
  const [formatStyle, setFormatStyle] = useState<'manuscript' | 'print' | 'ebook'>('manuscript');

  useEffect(() => {
    api<Project[]>('/api/v1/projects').then(setProjects).catch(() => setProjects([]));
  }, []);

  useEffect(() => {
    if (projects.length === 0) return;
    Promise.all(projects.map((p) => api<Book[]>(`/api/v1/projects/${p.id}/books`)))
      .then((results) => setBooks(results.flat()))
      .catch(() => setBooks([]));
  }, [projects.length]);

  useEffect(() => {
    if (!selectedBook) {
      setPreview(null);
      return;
    }
    setLoading(true);
    api<ExportPreview>(`/api/v1/export/books/${selectedBook.id}/preview`)
      .then(setPreview)
      .catch(() => setPreview(null))
      .finally(() => setLoading(false));
  }, [selectedBook?.id]);

  const handleExport = async (format: string) => {
    if (!selectedBook) return;
    setExporting(format);
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams({
        include_title_page: String(includeTitlePage),
        include_toc: String(includeToc),
      });
      if (authorName.trim()) params.set('author_name', authorName.trim());
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/books/${selectedBook.id}/${format}?${params}`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedBook.title}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      toast({ title: 'Export started', description: 'Your file is downloading.' });
    } catch (e) {
      toast({ title: 'Export failed', description: e instanceof Error ? e.message : 'Please try again.', variant: 'destructive' });
    } finally {
      setExporting(null);
    }
  };

  const handleExportOutline = async () => {
    if (!selectedBook) return;
    setExporting('outline');
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/books/${selectedBook.id}/outline`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedBook.title}_outline.txt`;
      a.click();
      URL.revokeObjectURL(url);
      toast({ title: 'Outline exported' });
    } catch (e) {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setExporting(null);
    }
  };

  const handleExportChapters = async () => {
    if (!selectedBook) return;
    setExporting('chapters');
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/books/${selectedBook.id}/chapters?format=docx&as_zip=true`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedBook.title}_chapters.zip`;
      a.click();
      URL.revokeObjectURL(url);
      toast({ title: 'Chapters exported' });
    } catch (e) {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-4xl">
      <PageHeader
        title="Export center"
        description="Export your book in multiple formats. Preview before download."
        actions={
          <HelpIcon
            content="Export to DOCX, PDF, EPUB, or plain text. One click to share with beta readers or publish."
            articleId="export-overview"
          />
        }
      />

      <HowThisWorks
        title="Export formats"
        summary="DOCX for editing, PDF for print, EPUB for e-readers. Choose what you need."
        articleId="export-formats"
      >
        <p><strong>DOCX</strong>: Industry standard. Use for agent queries, editing, collaboration.</p>
        <p><strong>PDF</strong>: Read-only. Good for beta readers, proofreading, print preview.</p>
        <p><strong>EPUB</strong>: E-book format. Use for Kindle, Kobo, Apple Books, self-publishing.</p>
        <p><strong>TXT</strong>: Plain text. Minimal formatting. Good for backups or conversion.</p>
      </HowThisWorks>

      {books.length === 0 ? (
        <Card variant="soft" className="p-8">
          <div className="text-center">
            <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="font-medium">No books yet</p>
            <p className="text-sm text-muted-foreground mt-1">Create a project and book to export.</p>
            <Button asChild className="mt-4">
              <Link href="/dashboard">Go to dashboard</Link>
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-6">
          <div>
            <label className="text-sm font-medium mb-2 block">Select book</label>
            <select
              value={selectedBook?.id ?? ''}
              onChange={(e) => setSelectedBook(books.find((b) => b.id === e.target.value) ?? null)}
              className="w-full max-w-md rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">Choose a book...</option>
              {books.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.title} {projects.find((p) => p.id === b.project_id)?.name ? `(${projects.find((p) => p.id === b.project_id)?.name})` : ''}
                </option>
              ))}
            </select>
          </div>

          {selectedBook && (
            <>
              {loading ? (
                <div className="flex gap-2">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Loading preview...
                </div>
              ) : preview ? (
                <>
                <Card variant="soft" className="mb-4">
                  <CardHeader>
                    <h3 className="font-semibold">Export options</h3>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={includeTitlePage}
                        onChange={(e) => setIncludeTitlePage(e.target.checked)}
                        className="rounded border-input"
                      />
                      <span className="text-sm">Include title page</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={includeToc}
                        onChange={(e) => setIncludeToc(e.target.checked)}
                        className="rounded border-input"
                      />
                      <span className="text-sm">Include table of contents</span>
                    </label>
                    <div>
                      <label className="text-sm block mb-1">Format style</label>
                      <select
                        value={formatStyle}
                        onChange={(e) => setFormatStyle(e.target.value as 'manuscript' | 'print' | 'ebook')}
                        className="rounded-md border border-input bg-background px-3 py-2 text-sm"
                      >
                        <option value="manuscript">Manuscript (standard)</option>
                        <option value="print">Print-friendly</option>
                        <option value="ebook">Ebook-friendly</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-sm block mb-1">Author name (optional)</label>
                      <input
                        type="text"
                        value={authorName}
                        onChange={(e) => setAuthorName(e.target.value)}
                        placeholder="Author"
                        className="w-full max-w-xs rounded-md border border-input bg-background px-3 py-2 text-sm"
                      />
                    </div>
                  </CardContent>
                </Card>
                <Card variant="soft">
                  <CardHeader>
                    <h3 className="font-semibold">Export preview</h3>
                    <p className="text-sm text-muted-foreground">
                      {preview.chapter_count} chapters • {preview.total_words.toLocaleString()} words
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-1 max-h-40 overflow-auto">
                      {preview.chapters.map((ch, i) => (
                        <div key={i} className="text-sm flex justify-between">
                          <span>{ch.title}</span>
                          <span className="text-muted-foreground">{ch.word_count} words</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
                </>
              ) : null}

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {FORMATS.map((f) => (
                  <Card key={f.id} variant="soft" className="p-4">
                    <div className="flex flex-col gap-2">
                      <f.icon className="h-8 w-8 text-primary" />
                      <div>
                        <p className="font-medium">{f.label}</p>
                        <p className="text-xs text-muted-foreground">{f.desc}</p>
                      </div>
                      <Button
                        size="sm"
                        className="mt-2"
                        onClick={() => handleExport(f.id)}
                        disabled={!!exporting}
                      >
                        {exporting === f.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
                        Export
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>

              <div className="flex flex-wrap gap-2">
                <Button variant="outline" onClick={handleExportOutline} disabled={!!exporting}>
                  {exporting === 'outline' ? <Loader2 className="h-4 w-4 animate-spin" /> : <List className="h-4 w-4" />}
                  Export outline
                </Button>
                <Button variant="outline" onClick={handleExportChapters} disabled={!!exporting}>
                  {exporting === 'chapters' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
                  Export chapters (ZIP)
                </Button>
                {selectedBook && (
                  <Button variant="outline" asChild>
                    <Link href={`/dashboard/export/${selectedBook.id}/publishing`}>
                      Publishing prep →
                    </Link>
                  </Button>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {projects.length > 0 && (
        <Card variant="soft" className="mt-8 p-4">
          <h3 className="font-medium mb-2">Export project notes</h3>
          <p className="text-sm text-muted-foreground mb-3">
            Export all notes from a project as plain text.
          </p>
          <div className="flex flex-wrap gap-2 items-center">
            <select
              id="notes-project"
              className="rounded-md border border-input bg-background px-3 py-2 text-sm max-w-xs"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <Button
              size="sm"
              variant="outline"
              disabled={!!exporting}
              onClick={async () => {
                const sel = document.getElementById('notes-project') as HTMLSelectElement;
                const projectId = sel?.value;
                if (!projectId) return;
                setExporting('notes');
                try {
                  const token = localStorage.getItem('access_token');
                  const res = await fetch(
                    `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/projects/${projectId}/notes`,
                    { headers: token ? { Authorization: `Bearer ${token}` } : {} }
                  );
                  if (!res.ok) throw new Error('Export failed');
                  const blob = await res.blob();
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `notes_${projects.find((p) => p.id === projectId)?.name || 'export'}.txt`;
                  a.click();
                  URL.revokeObjectURL(url);
                  toast({ title: 'Notes exported' });
                } catch (e) {
                  toast({ title: 'Failed', variant: 'destructive' });
                } finally {
                  setExporting(null);
                }
              }}
            >
              {exporting === 'notes' ? <Loader2 className="h-4 w-4 animate-spin" /> : <StickyNote className="h-4 w-4" />}
              Export notes
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
