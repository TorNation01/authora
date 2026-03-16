'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/layout/PageHeader';
import { api } from '@/lib/api';
import { getToken } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import {
  FileDown,
  FileText,
  FileImage,
  List,
  StickyNote,
  Loader2,
  BookOpen,
  History,
  AlertTriangle,
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

interface ExportValidation {
  valid: boolean;
  warnings: string[];
  errors: string[];
  fixes?: Array<{ issue: string; suggestion: string }>;
}

interface CompilePreview {
  structure: Array<{ type: string; label?: string; title?: string; word_count?: number }>;
  total_words: number;
  total_pages_estimate: number;
  chapter_count: number;
  warnings: string[];
  included_chapters: string[];
  excluded_chapters: Array<{ title: string; reason: string }>;
}

interface ExportHistoryItem {
  id: string;
  format: string;
  status: string;
  created_at: string | null;
  options?: Record<string, unknown>;
}

const PRIORITY_EXPORTS = [
  { id: 'clean-manuscript', label: 'Clean manuscript', desc: 'Polished copy ready for editing or submission', icon: FileText, ext: 'docx' },
  { id: 'clean-manuscript-pdf', label: 'Print-friendly draft', desc: 'PDF formatted for physical review', icon: FileImage, ext: 'pdf' },
  { id: 'editor-review', label: 'Review copy', desc: 'For editor feedback with acknowledgements', icon: FileText, ext: 'docx' },
  { id: 'beta-reader', label: 'Beta reader package', desc: 'Manuscript, synopsis, and feedback form', icon: FileDown, ext: 'zip' },
  { id: 'submission', label: 'Submission copy', desc: 'Professional format for agents and publishers', icon: FileText, ext: 'docx' },
  { id: 'sample-chapters', label: 'Sample chapters', desc: 'First 3 chapters for proposals', icon: FileText, ext: 'docx' },
  { id: 'workbook', label: 'Workbook export', desc: 'Printable workbook layout with prompt-friendly formatting and action spacing', icon: FileImage, ext: 'pdf' },
  { id: 'ghostwriter', label: 'Client review package', desc: 'Approval-ready manuscript with synopsis, summaries, and handoff notes', icon: FileDown, ext: 'zip' },
];

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
  const [dedication, setDedication] = useState('');
  const [epigraph, setEpigraph] = useState('');
  const [copyrightNotice, setCopyrightNotice] = useState('');
  const [authorBio, setAuthorBio] = useState('');
  const [frontMatter, setFrontMatter] = useState('');
  const [backMatter, setBackMatter] = useState('');
  const [acknowledgements, setAcknowledgements] = useState('');
  const [backupStyle, setBackupStyle] = useState(false);
  const [validation, setValidation] = useState<ExportValidation | null>(null);
  const [exportHistory, setExportHistory] = useState<ExportHistoryItem[]>([]);
  const [compilePreview, setCompilePreview] = useState<CompilePreview | null>(null);
  const [compilePreviewOpen, setCompilePreviewOpen] = useState(false);

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
      setValidation(null);
      setExportHistory([]);
      return;
    }
    setLoading(true);
    Promise.all([
      api<ExportPreview>(`/api/v1/export/books/${selectedBook.id}/preview`),
      api<ExportValidation>(`/api/v1/export/books/${selectedBook.id}/validate`),
      api<{ exports: ExportHistoryItem[] }>(`/api/v1/export/books/${selectedBook.id}/export-history?limit=10`),
    ])
      .then(([prev, val, hist]) => {
        setPreview(prev);
        setValidation(val);
        setExportHistory(hist.exports || []);
      })
      .catch(() => {
        setPreview(null);
        setValidation(null);
        setExportHistory([]);
      })
      .finally(() => setLoading(false));
  }, [selectedBook?.id]);

  const buildExportParams = () => {
    const p = new URLSearchParams({
      include_title_page: String(includeTitlePage),
      include_toc: String(includeToc),
      format_style: formatStyle,
      backup_style: String(backupStyle),
    });
    if (authorName.trim()) p.set('author_name', authorName.trim());
    if (dedication.trim()) p.set('dedication', dedication.trim());
    if (epigraph.trim()) p.set('epigraph', epigraph.trim());
    if (copyrightNotice.trim()) p.set('copyright_notice', copyrightNotice.trim());
    if (authorBio.trim()) p.set('author_bio', authorBio.trim());
    if (frontMatter.trim()) p.set('front_matter', frontMatter.trim());
    if (backMatter.trim()) p.set('back_matter', backMatter.trim());
    if (acknowledgements.trim()) p.set('acknowledgements', acknowledgements.trim());
    return p;
  };

  const handleExport = async (format: string) => {
    if (!selectedBook) return;
    if (validation && !validation.valid) {
      toast({ title: 'Export blocked', description: validation.errors.join(' '), variant: 'destructive' });
      return;
    }
    setExporting(format);
    try {
      const token = getToken();
      const params = buildExportParams();
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
      if (selectedBook) {
        api<{ exports: ExportHistoryItem[] }>(`/api/v1/export/books/${selectedBook.id}/export-history?limit=10`)
          .then((r) => setExportHistory(r.exports || []))
          .catch(() => {});
      }
    } catch (e) {
      toast({ title: 'Export failed', description: e instanceof Error ? e.message : 'Please try again.', variant: 'destructive' });
    } finally {
      setExporting(null);
    }
  };

  const handlePriorityExport = async (exportType: string, ext: string) => {
    if (!selectedBook) return;
    if (validation && !validation.valid) {
      toast({ title: 'Export blocked', description: validation.errors.join(' '), variant: 'destructive' });
      return;
    }
    setExporting(exportType);
    try {
      const token = getToken();
      const p = new URLSearchParams();
      if (authorName.trim()) p.set('author_name', authorName.trim());
      if (dedication.trim()) p.set('dedication', dedication.trim());
      if (epigraph.trim()) p.set('epigraph', epigraph.trim());
      if (copyrightNotice.trim()) p.set('copyright_notice', copyrightNotice.trim());
      if (authorBio.trim()) p.set('author_bio', authorBio.trim());
      if (acknowledgements.trim()) p.set('acknowledgements', acknowledgements.trim());
      if (exportType === 'sample-chapters') p.set('max_chapters', '3');
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/books/${selectedBook.id}/priority/${exportType}?${p}`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Export failed');
      }
      const blob = await res.blob();
      const cd = res.headers.get('Content-Disposition');
      const match = cd?.match(/filename="?([^";\n]+)"?/);
      const filename = match?.[1] || `${selectedBook.title}_${exportType}.${ext}`;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      toast({ title: 'Export complete', description: 'Your file is downloading.' });
      api<{ exports: ExportHistoryItem[] }>(`/api/v1/export/books/${selectedBook.id}/export-history?limit=10`)
        .then((r) => setExportHistory(r.exports || []))
        .catch(() => {});
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
      const token = getToken();
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

  const handleCompilePreview = async () => {
    if (!selectedBook) return;
    setExporting('compile-preview');
    try {
      const token = getToken();
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/books/${selectedBook.id}/compile-preview`,
        {
          method: 'POST',
          headers: {
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            compile_type: 'full',
            exclude_notes_comments: true,
            exclude_highlights: true,
            exclude_revision_marks: true,
          }),
        }
      );
      if (!res.ok) throw new Error('Preview failed');
      const data = await res.json();
      setCompilePreview(data);
      setCompilePreviewOpen(true);
    } catch (e) {
      toast({ title: 'Preview failed', variant: 'destructive' });
    } finally {
      setExporting(null);
    }
  };

  const handleFormatPreview = async () => {
    if (!selectedBook) return;
    setExporting('preview');
    try {
      const token = getToken();
      const params = buildExportParams();
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/books/${selectedBook.id}/format-preview?${params}`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (!res.ok) throw new Error('Preview failed');
      const html = await res.text();
      const win = window.open('', '_blank', 'noopener');
      if (win) {
        win.document.write(html);
        win.document.close();
      }
    } catch (e) {
      toast({ title: 'Preview failed', variant: 'destructive' });
    } finally {
      setExporting(null);
    }
  };

  const handlePackageExport = async (path: string, filename: string) => {
    if (!selectedBook) return;
    setExporting(path);
    try {
      const token = getToken();
      const p = authorName.trim() ? `?author_name=${encodeURIComponent(authorName.trim())}` : '';
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/books/${selectedBook.id}/packages/${path}${p}`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      toast({ title: 'Package downloaded' });
    } catch (e) {
      toast({ title: 'Failed', description: e instanceof Error ? e.message : 'AI may not be configured.', variant: 'destructive' });
    } finally {
      setExporting(null);
    }
  };

  const handleExportChapters = async () => {
    if (!selectedBook) return;
    setExporting('chapters');
    try {
      const token = getToken();
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
        title="Prepare your manuscript for the next step"
        description="Compile your writing into a clean export for editing, review, submission, publishing prep, or delivery."
        actions={
          <HelpIcon
            content="Your manuscript can leave Authora ready for real use. Export a working draft or a polished copy—choose what fits the next stage of your process."
            articleId="export-overview"
          />
        }
      />

      <HowThisWorks
        title="Export formats"
        summary="Prepare a version that fits the next stage of the process. Keep your export clean and focused."
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
            <p className="text-sm text-muted-foreground mt-1">Create a project and book first. We'll be ready when you are.</p>
            <Button asChild className="mt-4">
              <Link href="/dashboard">Go to Home</Link>
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
              <option value="">Select a book...</option>
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
                    <h3 className="font-semibold">Choose what to include</h3>
                    <p className="text-sm text-muted-foreground">Keep your export clean and focused.</p>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={includeTitlePage}
                        onChange={(e) => setIncludeTitlePage(e.target.checked)}
                        className="rounded border-input"
                      />
                      <span className="text-sm">Title page</span>
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
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={backupStyle}
                        onChange={(e) => setBackupStyle(e.target.checked)}
                        className="rounded border-input"
                      />
                      <span className="text-sm">Backup-style filename (title-backup-YYYY-MM-DD.ext)</span>
                    </label>
                    <div>
                      <label className="text-sm block mb-1">Format style</label>
                      <select
                        value={formatStyle}
                        onChange={(e) => setFormatStyle(e.target.value as 'manuscript' | 'print' | 'ebook')}
                        className="rounded-md border border-input bg-background px-3 py-2 text-sm"
                      >
                        <option value="manuscript">Clean manuscript</option>
                        <option value="print">Print-friendly draft</option>
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
                    <details className="group mt-2">
                      <summary className="text-sm font-medium cursor-pointer text-muted-foreground hover:text-foreground">
                        Front & back matter
                      </summary>
                      <div className="mt-3 space-y-2 pl-2 border-l-2 border-muted">
                        <div>
                          <label className="text-xs block mb-1">Dedication</label>
                          <input
                            type="text"
                            value={dedication}
                            onChange={(e) => setDedication(e.target.value)}
                            placeholder="For..."
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          />
                        </div>
                        <div>
                          <label className="text-xs block mb-1">Epigraph</label>
                          <input
                            type="text"
                            value={epigraph}
                            onChange={(e) => setEpigraph(e.target.value)}
                            placeholder="Quote and attribution"
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          />
                        </div>
                        <div>
                          <label className="text-xs block mb-1">Copyright</label>
                          <input
                            type="text"
                            value={copyrightNotice}
                            onChange={(e) => setCopyrightNotice(e.target.value)}
                            placeholder="© 2025 Author Name"
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          />
                        </div>
                        <div>
                          <label className="text-xs block mb-1">About the author</label>
                          <textarea
                            value={authorBio}
                            onChange={(e) => setAuthorBio(e.target.value)}
                            placeholder="Short author biography"
                            rows={2}
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                          />
                        </div>
                        <div>
                          <label className="text-xs block mb-1">Preface / Introduction</label>
                          <textarea
                            value={frontMatter}
                            onChange={(e) => setFrontMatter(e.target.value)}
                            placeholder="Preface, introduction, or other front matter"
                            rows={2}
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                          />
                        </div>
                        <div>
                          <label className="text-xs block mb-1">Acknowledgements</label>
                          <textarea
                            value={acknowledgements}
                            onChange={(e) => setAcknowledgements(e.target.value)}
                            placeholder="Thank you to..."
                            rows={2}
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                          />
                        </div>
                        <div>
                          <label className="text-xs block mb-1">Resources</label>
                          <textarea
                            value={backMatter}
                            onChange={(e) => setBackMatter(e.target.value)}
                            placeholder="Resources, appendix, glossary, or other back matter"
                            rows={2}
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                          />
                        </div>
                      </div>
                    </details>
                  </CardContent>
                </Card>
                <Card variant="soft">
                  <CardHeader>
                    <h3 className="font-semibold">Preview export</h3>
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

              {compilePreview && compilePreviewOpen && (
                <Card variant="soft" className="border-primary/20">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <h3 className="font-semibold">Export readiness check</h3>
                    <Button variant="ghost" size="sm" onClick={() => setCompilePreviewOpen(false)}>Close</Button>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm text-muted-foreground">
                      {compilePreview.total_words.toLocaleString()} words • ~{compilePreview.total_pages_estimate} pages • {compilePreview.chapter_count} chapters
                    </p>
                    {compilePreview.warnings.length > 0 && (
                      <div className="text-sm text-amber-600">
                        {compilePreview.warnings.length > 0 && compilePreview.warnings.join(' ')}
                      </div>
                    )}
                    <div className="text-sm space-y-1 max-h-48 overflow-auto">
                      {compilePreview.structure.map((s, i) => (
                        <div key={i} className="flex gap-2">
                          <span className="text-muted-foreground">{s.type}</span>
                          <span>{s.label || s.title || ''}</span>
                          {s.word_count != null && <span className="text-muted-foreground">({s.word_count} words)</span>}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {validation && (
                <Card
                  variant="soft"
                  className={
                    !validation.valid
                      ? 'border-destructive/30'
                      : validation.warnings.length > 0
                        ? 'border-amber-200 dark:border-amber-900'
                        : 'border-emerald-200 dark:border-emerald-900/50'
                  }
                >
                  <CardContent className="pt-4">
                    <div className="flex gap-2">
                      {validation.valid && validation.warnings.length === 0 ? (
                        <div className="text-sm text-emerald-700 dark:text-emerald-400">
                          <p className="font-medium">Your manuscript looks ready to export.</p>
                        </div>
                      ) : (
                        <>
                          <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
                          <div className="text-sm flex-1">
                            {!validation.valid && (
                              <p className="font-medium text-destructive">
                                {validation.errors.join(' ')}
                              </p>
                            )}
                            {validation.valid && validation.warnings.length > 0 && (
                              <p className="font-medium text-amber-700 dark:text-amber-400">
                                A few sections may need attention before you export.
                              </p>
                            )}
                            {validation.warnings.length > 0 && (
                              <ul className="text-muted-foreground mt-1 list-disc list-inside space-y-0.5">
                                {validation.warnings.map((w, i) => (
                                  <li key={i}>{w}</li>
                                ))}
                              </ul>
                            )}
                            {validation.valid && validation.warnings.length > 0 && (
                              <p className="text-muted-foreground mt-2 text-xs">
                                You can export anyway, or fix issues first.
                              </p>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card variant="soft" className="border-primary/20">
                <CardHeader>
                  <h3 className="font-semibold text-lg">Compile manuscript</h3>
                  <p className="text-sm text-muted-foreground">
                    Prepare a version that fits the next stage of the process. Export a working draft or a polished copy.
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                    {PRIORITY_EXPORTS.map((p) => (
                      <div
                        key={p.id}
                        className="flex flex-col gap-2 rounded-lg border border-border/50 bg-background/50 p-4 hover:border-primary/30 transition-colors"
                      >
                        <p.icon className="h-7 w-7 text-primary" />
                        <div>
                          <p className="font-medium">{p.label}</p>
                          <p className="text-xs text-muted-foreground">{p.desc}</p>
                        </div>
                        <Button
                          size="sm"
                          className="mt-auto"
                          onClick={() => handlePriorityExport(p.id, p.ext)}
                          disabled={!!exporting}
                        >
                          {exporting === p.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
                          Export now
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

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
                <Button variant="outline" onClick={handleCompilePreview} disabled={!!exporting}>
                  {exporting === 'compile-preview' ? <Loader2 className="h-4 w-4 animate-spin" /> : <BookOpen className="h-4 w-4" />}
                  Preview export
                </Button>
                <Button variant="outline" onClick={handleFormatPreview} disabled={!!exporting}>
                  {exporting === 'preview' ? <Loader2 className="h-4 w-4 animate-spin" /> : <BookOpen className="h-4 w-4" />}
                  Preview formatting
                </Button>
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

              <Card variant="soft" className="p-4">
                <h3 className="font-medium mb-2">Publishing prep</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Synopsis, blurbs, chapter summaries, and handoff materials. Requires AI.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePackageExport('beta-reader', `${selectedBook?.title || 'book'}_beta_package.zip`)}
                    disabled={!!exporting}
                  >
                    {exporting === 'beta-reader' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
                    Beta reader package
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePackageExport('ghostwriter-handoff', `${selectedBook?.title || 'book'}_handoff.zip`)}
                    disabled={!!exporting}
                  >
                    {exporting === 'ghostwriter-handoff' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
                    Ghostwriter handoff
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePackageExport('chapter-summary-sheet', `${selectedBook?.title || 'book'}_chapter_summaries.docx`)}
                    disabled={!!exporting}
                  >
                    {exporting === 'chapter-summary-sheet' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
                    Chapter summary sheet
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePackageExport('synopsis', `${selectedBook?.title || 'book'}_synopsis.docx`)}
                    disabled={!!exporting}
                  >
                    {exporting === 'synopsis' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
                    Synopsis
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePackageExport('blurb', `${selectedBook?.title || 'book'}_blurb.txt`)}
                    disabled={!!exporting}
                  >
                    {exporting === 'blurb' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
                    Back cover blurb
                  </Button>
                </div>
              </Card>

              {exportHistory.length > 0 && (
                <details className="group">
                  <summary className="flex items-center gap-2 cursor-pointer text-sm font-medium text-muted-foreground hover:text-foreground list-none">
                    <History className="h-4 w-4" />
                    Recent exports ({exportHistory.length})
                  </summary>
                  <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                    {exportHistory.map((ex) => (
                      <li key={ex.id} className="flex justify-between">
                        <span>{ex.format.toUpperCase()} • {ex.status}</span>
                        <span>{ex.created_at ? new Date(ex.created_at).toLocaleDateString() : ''}</span>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
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
                  const token = getToken();
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
