'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Calendar,
  CheckCircle2,
  Download,
  ExternalLink,
  FileText,
  Image as ImageIcon,
  Loader2,
  Package,
  RefreshCw,
  Upload,
  XCircle,
} from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { api, ApiError } from '@/lib/api';
import { getToken } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

const ANEMA_HOUSE_URL = 'https://anemahouse.com';
const BOOKFORGE_URL = 'https://bookforge.studio';

type ChecklistStatus = 'pass' | 'warn' | 'fail';

interface ChecklistItem {
  id: string;
  label: string;
  group: string;
  status: ChecklistStatus;
  reason: string;
  source: string;
  blocking: boolean;
}

interface ValidationBlock {
  valid: boolean;
  errors: string[];
  warnings: string[];
  fixes?: string[];
}

interface Readiness {
  book_id: string;
  book_title: string;
  chapter_count: number;
  total_words: number;
  outline_chapter_count: number;
  items: ChecklistItem[];
  summary: {
    pass: number;
    warn: number;
    fail: number;
    export_ready: boolean;
    release_ready: boolean;
    blocking_failures: string[];
  };
  validation: ValidationBlock;
  generated_at: string;
}

interface CoverInfo {
  id: string;
  content_type: string | null;
  width: number | null;
  height: number | null;
  size_bytes: number | null;
  uploaded_at: string | null;
  url: string;
}

interface Publication {
  book_id: string;
  book_title: string;
  book_type: string;
  exists: boolean;
  title: string | null;
  subtitle: string | null;
  author_name: string | null;
  blurb: string | null;
  short_description: string | null;
  keywords: string[];
  categories: string[];
  language: string;
  isbn: string | null;
  publication_date: string | null;
  imprint: string;
  copyright_notice: string | null;
  dedication: string | null;
  front_matter: string | null;
  acknowledgements: string | null;
  author_bio: string | null;
  back_matter: string | null;
  include_imprint_page: boolean;
  status: string;
  release: {
    released_at: string;
    formats: string[];
    imprint: string | null;
    isbn: string | null;
  } | null;
  cover: CoverInfo | null;
  cover_specs: Record<string, Record<string, unknown>>;
  updated_at: string | null;
}

interface ImprintPage {
  heading: string;
  paragraphs: string[];
  links: { label: string; url: string }[];
  enabled: boolean;
  text: string;
}

interface ExportRecord {
  id: string;
  format: string;
  status: string;
  created_at: string | null;
}

interface CompilePreview {
  chapter_count: number;
  total_words: number;
  total_pages_estimate: number;
  warnings: string[];
  included_chapters: string[];
  excluded_chapters: { title: string; reason: string | null }[];
  structure?: { label?: string; kind?: string; words?: number }[];
}

const FORMATS = [
  { id: 'epub', label: 'EPUB', note: 'Reader-facing ebook with contents page and chapter headings.' },
  { id: 'pdf', label: 'PDF', note: 'Fixed-layout proof for print review and reading.' },
  { id: 'docx', label: 'Word', note: 'Editable manuscript for copy-editing and proofing.' },
  { id: 'txt', label: 'Plain text', note: 'Clean text for audiobook narration or import.' },
];

const STATUS_META: Record<ChecklistStatus, { icon: typeof CheckCircle2; tone: string; label: string }> = {
  pass: { icon: CheckCircle2, tone: 'text-success', label: 'Pass' },
  warn: { icon: AlertTriangle, tone: 'text-warning', label: 'Attention' },
  fail: { icon: XCircle, tone: 'text-destructive', label: 'Missing' },
};

const EMPTY_FORM = {
  title: '',
  subtitle: '',
  author_name: '',
  blurb: '',
  short_description: '',
  keywords: '',
  categories: '',
  language: 'en',
  isbn: '',
  publication_date: '',
  imprint: 'Anema House Publishing',
  copyright_notice: '',
  dedication: '',
  front_matter: '',
  acknowledgements: '',
  author_bio: '',
  back_matter: '',
};

function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatBytes(bytes: number | null): string {
  if (!bytes) return '—';
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function splitList(value: string): string[] {
  return value
    .split(',')
    .map((v) => v.trim())
    .filter(Boolean);
}

export default function PublishPage() {
  const params = useParams();
  const projectId = params.id as string;
  const bookId = params.bookId as string;
  const { toast } = useToast();

  const [publication, setPublication] = useState<Publication | null>(null);
  const [readiness, setReadiness] = useState<Readiness | null>(null);
  const [imprintPage, setImprintPage] = useState<ImprintPage | null>(null);
  const [history, setHistory] = useState<ExportRecord[]>([]);
  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [releasing, setReleasing] = useState(false);
  const [exporting, setExporting] = useState<string | null>(null);
  const [previewing, setPreviewing] = useState(false);
  const [preview, setPreview] = useState<CompilePreview | null>(null);
  const [coverUrl, setCoverUrl] = useState<string | null>(null);
  const [uploadingCover, setUploadingCover] = useState(false);
  const [releaseFormats, setReleaseFormats] = useState<string[]>(['epub', 'pdf']);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const applyPublication = useCallback((pub: Publication) => {
    setPublication(pub);
    setForm({
      title: pub.title || '',
      subtitle: pub.subtitle || '',
      author_name: pub.author_name || '',
      blurb: pub.blurb || '',
      short_description: pub.short_description || '',
      keywords: (pub.keywords || []).join(', '),
      categories: (pub.categories || []).join(', '),
      language: pub.language || 'en',
      isbn: pub.isbn || '',
      publication_date: pub.publication_date || '',
      imprint: pub.imprint || 'Anema House Publishing',
      copyright_notice: pub.copyright_notice || '',
      dedication: pub.dedication || '',
      front_matter: pub.front_matter || '',
      acknowledgements: pub.acknowledgements || '',
      author_bio: pub.author_bio || '',
      back_matter: pub.back_matter || '',
    });
  }, []);

  const loadCover = useCallback(
    async (cover: CoverInfo | null) => {
      if (coverUrl) {
        URL.revokeObjectURL(coverUrl);
        setCoverUrl(null);
      }
      if (!cover) return;
      const token = getToken();
      const res = await fetch(`${API_BASE}${cover.url}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) return;
      const blob = await res.blob();
      setCoverUrl(URL.createObjectURL(blob));
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const load = useCallback(async () => {
    setError(null);
    try {
      const [pub, ready, page, exports] = await Promise.all([
        api<Publication>(`/api/v1/publish/books/${bookId}/publication`),
        api<Readiness>(`/api/v1/publish/books/${bookId}/readiness`),
        api<ImprintPage>(`/api/v1/publish/books/${bookId}/imprint-page`),
        api<{ exports: ExportRecord[] }>(`/api/v1/export/books/${bookId}/export-history?limit=8`),
      ]);
      applyPublication(pub);
      setReadiness(ready);
      setImprintPage(page);
      setHistory(exports.exports || []);
      if (pub.release?.formats?.length) setReleaseFormats(pub.release.formats);
      await loadCover(pub.cover);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load publishing data.');
    } finally {
      setLoading(false);
    }
  }, [bookId, applyPublication, loadCover]);

  useEffect(() => {
    load();
  }, [load]);

  const grouped = useMemo(() => {
    const groups: { name: string; items: ChecklistItem[] }[] = [];
    for (const item of readiness?.items || []) {
      let group = groups.find((g) => g.name === item.group);
      if (!group) {
        group = { name: item.group, items: [] };
        groups.push(group);
      }
      group.items.push(item);
    }
    return groups;
  }, [readiness]);

  async function saveMetadata() {
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        title: form.title.trim() || null,
        subtitle: form.subtitle.trim() || null,
        author_name: form.author_name.trim() || null,
        blurb: form.blurb.trim() || null,
        short_description: form.short_description.trim() || null,
        keywords: splitList(form.keywords),
        categories: splitList(form.categories),
        isbn: form.isbn.trim() || null,
        publication_date: form.publication_date || null,
        copyright_notice: form.copyright_notice.trim() || null,
        dedication: form.dedication.trim() || null,
        front_matter: form.front_matter.trim() || null,
        acknowledgements: form.acknowledgements.trim() || null,
        author_bio: form.author_bio.trim() || null,
        back_matter: form.back_matter.trim() || null,
        include_imprint_page: publication?.include_imprint_page ?? true,
      };
      const updated = await api<Publication>(`/api/v1/publish/books/${bookId}/publication`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      applyPublication(updated);
      const ready = await api<Readiness>(`/api/v1/publish/books/${bookId}/readiness`);
      setReadiness(ready);
      toast({ title: 'Publishing details saved', description: 'The readiness checks have been recalculated.' });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Could not save the publishing details.';
      setError(message);
      toast({ title: 'Save failed', description: message, variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  async function toggleImprintPage(next: boolean) {
    if (!publication) return;
    setPublication({ ...publication, include_imprint_page: next });
    try {
      const updated = await api<Publication>(`/api/v1/publish/books/${bookId}/publication`, {
        method: 'PUT',
        body: JSON.stringify({ include_imprint_page: next }),
      });
      applyPublication(updated);
      toast({
        title: next ? 'Imprint page on' : 'Imprint page off',
        description: next
          ? 'Generated EPUB, PDF, Word and text files will close with the imprint page.'
          : 'New exports will not include the imprint page.',
      });
    } catch (err) {
      setPublication({ ...publication, include_imprint_page: !next });
      toast({
        title: 'Could not update the imprint page',
        description: err instanceof Error ? err.message : 'Try again.',
        variant: 'destructive',
      });
    }
  }

  async function uploadCover(file: File) {
    setUploadingCover(true);
    try {
      const body = new FormData();
      body.append('file', file);
      const token = getToken();
      const res = await fetch(`${API_BASE}/api/v1/publish/books/${bookId}/cover`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body,
      });
      if (!res.ok) {
        const payload = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(typeof payload.detail === 'string' ? payload.detail : 'Upload failed.');
      }
      const updated: Publication = await res.json();
      setPublication(updated);
      await loadCover(updated.cover);
      const ready = await api<Readiness>(`/api/v1/publish/books/${bookId}/readiness`);
      setReadiness(ready);
      toast({ title: 'Cover uploaded', description: `${updated.cover?.width}×${updated.cover?.height}px stored.` });
    } catch (err) {
      toast({
        title: 'Cover upload failed',
        description: err instanceof Error ? err.message : 'Try again.',
        variant: 'destructive',
      });
    } finally {
      setUploadingCover(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  }

  async function runExport(format: string) {
    setExporting(format);
    setError(null);
    try {
      const token = getToken();
      const query = new URLSearchParams();
      if (form.author_name.trim()) query.set('author_name', form.author_name.trim());
      if (form.copyright_notice.trim()) query.set('copyright_notice', form.copyright_notice.trim());
      if (form.dedication.trim()) query.set('dedication', form.dedication.trim());
      if (form.front_matter.trim()) query.set('front_matter', form.front_matter.trim());
      if (form.acknowledgements.trim()) query.set('acknowledgements', form.acknowledgements.trim());
      if (form.author_bio.trim()) query.set('author_bio', form.author_bio.trim());
      if (form.back_matter.trim()) query.set('back_matter', form.back_matter.trim());
      if (publication?.include_imprint_page) query.set('include_imprint_page', 'true');

      const res = await fetch(`${API_BASE}/api/v1/export/books/${bookId}/${format}?${query.toString()}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) {
        const payload = await res.json().catch(() => ({ detail: res.statusText }));
        const detail = Array.isArray(payload.detail)
          ? payload.detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join('; ')
          : payload.detail;
        throw new Error(detail || `Export failed (${res.status}).`);
      }
      const blob = await res.blob();
      const disposition = res.headers.get('Content-Disposition') || '';
      const match = disposition.match(/filename="?([^";]+)"?/);
      const filename = match?.[1] || `${bookId}.${format}`;
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);

      toast({ title: `${format.toUpperCase()} exported`, description: filename });
      const exports = await api<{ exports: ExportRecord[] }>(`/api/v1/export/books/${bookId}/export-history?limit=8`);
      setHistory(exports.exports || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Export failed.';
      setError(message);
      toast({ title: 'Export failed', description: message, variant: 'destructive' });
    } finally {
      setExporting(null);
    }
  }

  async function previewCompile() {
    setPreviewing(true);
    try {
      const result = await api<CompilePreview>(`/api/v1/export/books/${bookId}/compile-preview`, {
        method: 'POST',
        body: JSON.stringify({ compile_type: 'full' }),
      });
      setPreview(result);
    } catch (err) {
      toast({
        title: 'Preview failed',
        description: err instanceof Error ? err.message : 'Try again.',
        variant: 'destructive',
      });
    } finally {
      setPreviewing(false);
    }
  }

  async function recordRelease() {
    setReleasing(true);
    try {
      const updated = await api<Publication>(`/api/v1/publish/books/${bookId}/release`, {
        method: 'POST',
        body: JSON.stringify({
          formats: releaseFormats,
          imprint: form.imprint || 'Anema House Publishing',
          isbn: form.isbn.trim() || null,
        }),
      });
      applyPublication(updated);
      const ready = await api<Readiness>(`/api/v1/publish/books/${bookId}/readiness`);
      setReadiness(ready);
      toast({ title: 'Release recorded', description: 'Stored in Authora. Nothing was sent to a retailer.' });
    } catch (err) {
      toast({
        title: 'Could not record the release',
        description: err instanceof Error ? err.message : 'Try again.',
        variant: 'destructive',
      });
    } finally {
      setReleasing(false);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl p-6 lg:p-8">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading publishing record…
        </div>
      </div>
    );
  }

  const summary = readiness?.summary;
  const passTotal = (summary?.pass || 0) + (summary?.warn || 0) + (summary?.fail || 0);
  const isReleased = publication?.status === 'released' && !!publication.release;
  const blockingReasons = (readiness?.items || [])
    .filter((item) => item.blocking && item.status === 'fail')
    .map((item) => item.reason);

  return (
    <div className="mx-auto max-w-4xl p-6 lg:p-8">
      <PageHeader
        title="Publish & release"
        description="Prepare the finished manuscript, produce the files, record the release, and hand off to production."
        backHref={`/dashboard/projects/${projectId}/books/${bookId}`}
        backLabel="Back to manuscript"
        actions={
          summary ? (
            <Badge variant={summary.fail > 0 ? (summary.export_ready ? 'warning' : 'destructive') : summary.warn > 0 ? 'outline' : 'success'}>
              {summary.fail > 0
                ? `${summary.fail} item${summary.fail === 1 ? '' : 's'} need attention`
                : summary.warn > 0
                  ? `${summary.warn} optional note${summary.warn === 1 ? '' : 's'}`
                  : 'All checks pass'}
            </Badge>
          ) : null
        }
      />

      {error && (
        <Card variant="soft" className="mb-6 border-destructive/30">
          <CardContent className="flex items-start gap-3 p-4 text-sm text-destructive">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </CardContent>
        </Card>
      )}

      {/* 01 — Readiness */}
      <section id="readiness" className="scroll-mt-24">
        <div className="mb-4 flex items-baseline justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">01 — Readiness</p>
            <h2 className="mt-1 font-serif text-lg font-semibold">What is still missing</h2>
          </div>
          <button
            onClick={load}
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Re-run checks
          </button>
        </div>

        <Card variant="soft">
          <CardContent className="p-5">
            <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
              <span className="font-medium">
                {summary?.pass || 0} of {passTotal} checks pass
              </span>
              <span className="text-muted-foreground">{readiness?.total_words.toLocaleString()} words</span>
              <span className="text-muted-foreground">{readiness?.chapter_count} chapters</span>
              {summary && summary.warn > 0 && <span className="text-warning">{summary.warn} optional</span>}
              {summary && summary.fail > 0 && <span className="text-destructive">{summary.fail} missing</span>}
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              Each line below is computed from this book&apos;s own records and the export validator&apos;s output, not a fixed template.
            </p>

            <div className="mt-5 space-y-5">
              {grouped.map((group) => (
                <div key={group.name}>
                  <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.14em] text-muted-foreground">
                    {group.name}
                  </p>
                  <ul className="divide-y divide-border/60">
                    {group.items.map((item) => {
                      const meta = STATUS_META[item.status];
                      const Icon = meta.icon;
                      return (
                        <li key={item.id} className="flex items-start gap-3 py-2.5">
                          <Icon className={cn('mt-0.5 h-4 w-4 shrink-0', meta.tone)} />
                          <div className="min-w-0 flex-1">
                            <div className="flex flex-wrap items-baseline gap-x-2">
                              <span className="text-sm font-medium">{item.label}</span>
                              <span className="text-[11px] text-muted-foreground">from {item.source}</span>
                            </div>
                            <p className="mt-0.5 text-sm text-muted-foreground">{item.reason}</p>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ))}
            </div>

            {(readiness?.validation.errors?.length || readiness?.validation.warnings?.length) ? (
              <details className="mt-4 rounded-lg border border-border/60 bg-background/60 px-4 py-3">
                <summary className="cursor-pointer text-xs font-medium text-muted-foreground">
                  Validator output from /export/books/{bookId}/validate
                </summary>
                <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                  {readiness?.validation.errors.map((e, i) => (
                    <li key={`e-${i}`} className="text-destructive">Error: {e}</li>
                  ))}
                  {readiness?.validation.warnings.map((w, i) => (
                    <li key={`w-${i}`}>Warning: {w}</li>
                  ))}
                </ul>
              </details>
            ) : null}
          </CardContent>
        </Card>
      </section>

      {/* 02 — Metadata */}
      <section id="metadata" className="mt-12 scroll-mt-24">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">02 — Metadata</p>
          <h2 className="mt-1 font-serif text-lg font-semibold">The book as it will be catalogued</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            These fields are saved to this book&apos;s publication record and used on the title page, copyright page and back matter.
          </p>
        </div>

        <Card>
          <CardContent className="space-y-5 p-6">
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Title">
                <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Book title" />
              </Field>
              <Field label="Subtitle">
                <Input value={form.subtitle} onChange={(e) => setForm({ ...form, subtitle: e.target.value })} placeholder="Optional" />
              </Field>
              <Field label="Author name">
                <Input value={form.author_name} onChange={(e) => setForm({ ...form, author_name: e.target.value })} placeholder="Name as it should appear" />
              </Field>
              <Field label="Imprint">
                <Input value={form.imprint} onChange={(e) => setForm({ ...form, imprint: e.target.value })} />
              </Field>
              <Field label="Language">
                <Input value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })} placeholder="en" />
              </Field>
              <Field label="Publication date">
                <Input type="date" value={form.publication_date || ''} onChange={(e) => setForm({ ...form, publication_date: e.target.value })} />
              </Field>
            </div>

            <Field
              label="Blurb"
              hint="Back-cover copy. If it is empty you can draft one from the manuscript with the blurb prep endpoint."
            >
              <Textarea
                rows={4}
                className="font-serif"
                value={form.blurb}
                onChange={(e) => setForm({ ...form, blurb: e.target.value })}
                placeholder="Two or three sentences in the voice of the jacket."
              />
            </Field>

            <Field label="Short description" hint="Used in store listings where a single line is allowed.">
              <Input
                value={form.short_description}
                maxLength={1000}
                onChange={(e) => setForm({ ...form, short_description: e.target.value })}
              />
            </Field>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Keywords" hint="Comma separated.">
                <Input value={form.keywords} onChange={(e) => setForm({ ...form, keywords: e.target.value })} placeholder="historical fiction, Egypt, archaeology" />
              </Field>
              <Field label="Categories / BISAC" hint="Comma separated subjects.">
                <Input value={form.categories} onChange={(e) => setForm({ ...form, categories: e.target.value })} placeholder="Fiction / Historical / General" />
              </Field>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field
                label="ISBN"
                hint="Optional. Validated for length and checksum only — Authora does not register ISBNs."
              >
                <Input value={form.isbn} onChange={(e) => setForm({ ...form, isbn: e.target.value })} placeholder="978-…" />
              </Field>
              <Field label="Copyright notice" hint="Printed on the copyright page when set.">
                <Input
                  value={form.copyright_notice}
                  onChange={(e) => setForm({ ...form, copyright_notice: e.target.value })}
                  placeholder={`© ${new Date().getFullYear()} ${form.author_name || 'Author name'}. All rights reserved.`}
                />
              </Field>
            </div>

            <details className="rounded-lg border border-border/60 px-4 py-3">
              <summary className="cursor-pointer text-sm font-medium">Front and back matter</summary>
              <div className="mt-4 grid gap-4">
                <Field label="Dedication">
                  <Textarea rows={2} className="font-serif" value={form.dedication} onChange={(e) => setForm({ ...form, dedication: e.target.value })} />
                </Field>
                <Field label="Front matter">
                  <Textarea rows={2} className="font-serif" value={form.front_matter} onChange={(e) => setForm({ ...form, front_matter: e.target.value })} />
                </Field>
                <Field label="Acknowledgements">
                  <Textarea rows={2} className="font-serif" value={form.acknowledgements} onChange={(e) => setForm({ ...form, acknowledgements: e.target.value })} />
                </Field>
                <Field label="About the author">
                  <Textarea rows={2} className="font-serif" value={form.author_bio} onChange={(e) => setForm({ ...form, author_bio: e.target.value })} />
                </Field>
                <Field label="Back matter">
                  <Textarea rows={2} className="font-serif" value={form.back_matter} onChange={(e) => setForm({ ...form, back_matter: e.target.value })} />
                </Field>
              </div>
            </details>

            <div className="flex items-center justify-between gap-4 border-t border-border/60 pt-4">
              <p className="text-xs text-muted-foreground">
                {publication?.updated_at ? `Last saved ${formatDate(publication.updated_at)}` : 'Not saved yet'}
              </p>
              <Button onClick={saveMetadata} disabled={saving}>
                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Save publishing details
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* 03 — Cover */}
      <section id="cover" className="mt-12 scroll-mt-24">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">03 — Cover</p>
          <h2 className="mt-1 font-serif text-lg font-semibold">Front cover</h2>
        </div>

        <Card>
          <CardContent className="grid gap-6 p-6 sm:grid-cols-[180px,1fr]">
            <div className="aspect-[2/3] w-full overflow-hidden rounded-lg border border-border/60 bg-muted">
              {coverUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={coverUrl} alt="Book cover" className="h-full w-full object-cover" />
              ) : (
                <div className="flex h-full flex-col items-center justify-center gap-2 text-muted-foreground">
                  <ImageIcon className="h-6 w-6" />
                  <span className="text-xs">No cover yet</span>
                </div>
              )}
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) uploadCover(file);
                  }}
                />
                <Button variant="outline" onClick={() => fileRef.current?.click()} disabled={uploadingCover}>
                  {uploadingCover ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
                  {publication?.cover ? 'Replace cover' : 'Upload cover'}
                </Button>
                {publication?.cover && (
                  <span className="text-xs text-muted-foreground">
                    {publication.cover.width}×{publication.cover.height}px · {formatBytes(publication.cover.size_bytes)}
                  </span>
                )}
              </div>
              <p className="mt-3 text-sm text-muted-foreground">
                Authora stores the cover you supply. It does not generate artwork, and it does not produce the wraparound print file.
              </p>
              <dl className="mt-4 grid gap-3 text-xs sm:grid-cols-2">
                <div className="rounded-lg border border-border/60 p-3">
                  <dt className="font-medium">Ebook</dt>
                  <dd className="mt-1 text-muted-foreground">
                    1600 × 2560 px recommended (minimum 1000 × 1600), 1:1.6, under 10 MB.
                  </dd>
                </div>
                <div className="rounded-lg border border-border/60 p-3">
                  <dt className="font-medium">Print</dt>
                  <dd className="mt-1 text-muted-foreground">
                    1800 × 2700 px at 300 DPI for the front cover. Spine and bleed are produced outside Authora.
                  </dd>
                </div>
              </dl>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* 04 — Export */}
      <section id="export" className="mt-12 scroll-mt-24">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">04 — Files</p>
          <h2 className="mt-1 font-serif text-lg font-semibold">Produce the book files</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Each file is built from the current manuscript with your saved metadata as front and back matter.
          </p>
        </div>

        {blockingReasons.length > 0 && (
          <Card variant="soft" className="mb-4 border-destructive/30">
            <CardContent className="p-4">
              <p className="text-sm font-medium text-destructive">Exports are blocked until these are fixed</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                {blockingReasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-3 sm:grid-cols-2">
          {FORMATS.map((fmt) => (
            <Card key={fmt.id} variant="soft">
              <CardContent className="flex h-full flex-col justify-between gap-3 p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">{fmt.label}</span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{fmt.note}</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="self-start"
                  onClick={() => runExport(fmt.id)}
                  disabled={!!exporting || blockingReasons.length > 0}
                >
                  {exporting === fmt.id ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Download className="mr-2 h-4 w-4" />
                  )}
                  Export {fmt.label}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card variant="soft" className="mt-4 border-border/60">
          <CardContent className="p-4">
            <p className="text-xs leading-relaxed text-muted-foreground">
              Authora produces EPUB, PDF, Word and plain text. It does not produce KPF (Kindle Create) or M4B
              (audiobook) files — the Kindle package and the audio master are made in the Bookforge build pipeline.
            </p>
          </CardContent>
        </Card>

        <div className="mt-6">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-sm font-medium">Compile preview</h3>
            <Button variant="ghost" size="sm" onClick={previewCompile} disabled={previewing}>
              {previewing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <BookOpen className="mr-2 h-4 w-4" />}
              Preview structure
            </Button>
          </div>
          {preview ? (
            <Card variant="soft">
              <CardContent className="space-y-3 p-4 text-sm">
                <div className="flex flex-wrap gap-x-6 gap-y-1 text-xs text-muted-foreground">
                  <span>{preview.chapter_count} chapters</span>
                  <span>{preview.total_words.toLocaleString()} words</span>
                  <span>~{preview.total_pages_estimate} pages</span>
                </div>
                <ol className="space-y-1">
                  {preview.included_chapters.map((title, i) => (
                    <li key={`${title}-${i}`} className="flex gap-2 text-sm">
                      <span className="w-6 shrink-0 text-right text-xs text-muted-foreground">{i + 1}</span>
                      <span className="font-serif">{title}</span>
                    </li>
                  ))}
                </ol>
                {preview.warnings.length > 0 && (
                  <ul className="space-y-1 border-t border-border/60 pt-2 text-xs text-warning">
                    {preview.warnings.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                )}
                {preview.excluded_chapters.length > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Excluded: {preview.excluded_chapters.map((c) => `${c.title} (${c.reason || 'not included'})`).join('; ')}
                  </p>
                )}
              </CardContent>
            </Card>
          ) : (
            <p className="text-xs text-muted-foreground">Build a preview to see the reading order and page estimate before exporting.</p>
          )}
        </div>

        <div className="mt-6">
          <h3 className="mb-2 text-sm font-medium">Export history</h3>
          {history.length === 0 ? (
            <p className="text-xs text-muted-foreground">No files produced yet.</p>
          ) : (
            <Card variant="soft">
              <CardContent className="p-0">
                <ul className="divide-y divide-border/60">
                  {history.map((record) => (
                    <li key={record.id} className="flex items-center justify-between px-4 py-2.5 text-sm">
                      <span className="flex items-center gap-2">
                        <Package className="h-3.5 w-3.5 text-muted-foreground" />
                        {record.format.toUpperCase()}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(record.created_at)} · {record.status}
                      </span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      {/* 05 — Release */}
      <section id="release" className="mt-12 scroll-mt-24">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">05 — Release</p>
          <h2 className="mt-1 font-serif text-lg font-semibold">Record the release</h2>
        </div>

        {isReleased && publication?.release ? (
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-success" />
                <span className="text-sm font-medium">Released {formatDate(publication.release.released_at)}</span>
              </div>
              <dl className="mt-4 grid gap-4 text-sm sm:grid-cols-3">
                <div>
                  <dt className="text-xs uppercase tracking-wide text-muted-foreground">Formats</dt>
                  <dd className="mt-1">{publication.release.formats.map((f) => f.toUpperCase()).join(', ') || '—'}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-muted-foreground">Imprint</dt>
                  <dd className="mt-1">{publication.release.imprint || form.imprint}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-muted-foreground">ISBN</dt>
                  <dd className="mt-1">{publication.release.isbn || 'Not given'}</dd>
                </div>
              </dl>
              <p className="mt-4 border-t border-border/60 pt-3 text-xs text-muted-foreground">
                This is Authora&apos;s record of your release. Nothing was transmitted to Amazon KDP or any other retailer
                or distributor.
              </p>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="p-6">
              <p className="text-sm text-muted-foreground">
                Recording a release stores the date, the formats you produced, the imprint and the ISBN against this book.
                It does not submit anything to a retailer.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {FORMATS.map((fmt) => {
                  const active = releaseFormats.includes(fmt.id);
                  return (
                    <button
                      key={fmt.id}
                      type="button"
                      onClick={() =>
                        setReleaseFormats((prev) =>
                          prev.includes(fmt.id) ? prev.filter((f) => f !== fmt.id) : [...prev, fmt.id]
                        )
                      }
                      className={cn(
                        'rounded-full border px-3 py-1 text-xs transition-colors',
                        active
                          ? 'border-foreground bg-foreground text-background'
                          : 'border-border text-muted-foreground hover:border-foreground/40'
                      )}
                    >
                      {fmt.label}
                    </button>
                  );
                })}
              </div>
              <Button className="mt-5" onClick={recordRelease} disabled={releasing || releaseFormats.length === 0}>
                {releasing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Record release
              </Button>
              {readiness && !readiness.summary.release_ready && (
                <p className="mt-2 text-xs text-destructive">
                  Fix the blocking items above before recording a release.
                </p>
              )}
            </CardContent>
          </Card>
        )}
      </section>

      {/* 06 — Handoff */}
      <section id="handoff" className="mt-14 scroll-mt-24 border-t border-border/60 pt-10">
        <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">06 — Handoff</p>
        <h2 className="mt-1 font-serif text-xl font-semibold">Take the book to production</h2>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          The files are finished. These two houses carry the book the rest of the way — one publishes it, the other builds
          the retail and print packages.
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <a
            href={ANEMA_HOUSE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="group flex flex-col justify-between rounded-xl border border-border/70 p-5 transition-colors hover:border-foreground/40"
          >
            <div>
              <p className="font-serif text-base font-semibold">Publish with Anema House</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Production, imprint and publishing for finished manuscripts.
              </p>
            </div>
            <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium">
              anemahouse.com
              <ExternalLink className="h-3.5 w-3.5 transition-transform group-hover:-translate-y-0.5" />
            </span>
          </a>

          <a
            href={BOOKFORGE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="group flex flex-col justify-between rounded-xl border border-border/70 p-5 transition-colors hover:border-foreground/40"
          >
            <div>
              <p className="font-serif text-base font-semibold">Take it to Bookforge</p>
              <p className="mt-1 text-sm text-muted-foreground">
                The build pipeline behind print-ready and retail packages.
              </p>
            </div>
            <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium">
              bookforge.studio
              <ExternalLink className="h-3.5 w-3.5 transition-transform group-hover:-translate-y-0.5" />
            </span>
          </a>
        </div>

        <Card variant="soft" className="mt-5">
          <CardContent className="p-5">
            <label className="flex cursor-pointer items-start gap-3">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 accent-foreground"
                checked={publication?.include_imprint_page ?? true}
                onChange={(e) => toggleImprintPage(e.target.checked)}
              />
              <span>
                <span className="text-sm font-medium">Include the imprint page in generated files</span>
                <span className="mt-1 block text-xs text-muted-foreground">
                  One short page at the back, in the imprint&apos;s voice, crediting Authora and pointing to Anema House
                  Publishing and Bookforge. On by default.
                </span>
              </span>
            </label>

            {imprintPage && (
              <div className="mt-5 rounded-lg border border-border/60 bg-background/60 p-4">
                <p className="text-[11px] uppercase tracking-[0.14em] text-muted-foreground">Back matter preview</p>
                <p className="mt-2 font-serif text-sm font-semibold">{imprintPage.heading}</p>
                {imprintPage.paragraphs.map((p) => (
                  <p key={p} className="mt-2 font-serif text-sm leading-relaxed text-muted-foreground">
                    {p}
                  </p>
                ))}
                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs">
                  {imprintPage.links.map((link) => (
                    <a key={link.url} href={link.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-4">
                      {link.url.replace('https://', '')}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <p className="mt-4 text-xs text-muted-foreground">
          These are referrals, not integrations. Nothing is submitted automatically and no account is created on your
          behalf.
        </p>
      </section>

      <div className="mt-10 flex items-center justify-between border-t border-border/60 pt-6 text-xs text-muted-foreground">
        <Link href={`/dashboard/projects/${projectId}/books/${bookId}`} className="hover:text-foreground">
          ← Back to the manuscript
        </Link>
        <span className="flex items-center gap-1.5">
          Publishing detail is stored against this book <ArrowRight className="h-3 w-3" />
        </span>
      </div>
    </div>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      {children}
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}
