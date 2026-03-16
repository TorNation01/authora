'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/PageHeader';
import { api, apiUpload } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  StickyNote,
  Lightbulb,
  Search,
  BookOpen,
  Pin,
  PinOff,
  Sparkles,
  Plus,
  ChevronLeft,
  Loader2,
  Paperclip,
  X,
  FileText,
} from 'lucide-react';
import * as Tabs from '@radix-ui/react-tabs';
import { cn } from '@/lib/utils';
import { getEmptyStateConfig } from '@/content/empty-states';

interface NoteAttachment {
  id: string;
  file_key: string;
  filename: string;
  content_type: string | null;
  file_size: number | null;
  created_at: string;
}

interface Note {
  id: string;
  project_id: string;
  book_id: string | null;
  chapter_id: string | null;
  title: string;
  content: string;
  note_type: string;
  source: string | null;
  source_url: string | null;
  pinned: boolean;
  is_inspiration: boolean;
  category: string | null;
  tags: string[];
  sort_order: number;
  created_at: string;
  updated_at: string;
  attachments: NoteAttachment[];
}

interface Project {
  id: string;
  name: string;
}

const NOTE_TYPES = [
  { value: 'general', label: 'General', icon: StickyNote },
  { value: 'idea', label: 'Idea', icon: Lightbulb },
  { value: 'research', label: 'Research', icon: Search },
  { value: 'quote', label: 'Quote', icon: FileText },
  { value: 'scratchpad', label: 'Scratchpad', icon: StickyNote },
] as const;

export default function ProjectNotesPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { toast } = useToast();
  const [project, setProject] = useState<Project | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState('notebook');
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [quickCapture, setQuickCapture] = useState('');
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  const fetchProject = useCallback(() => {
    api<Project>(`/api/v1/projects/${projectId}`)
      .then(setProject)
      .catch(() => router.push('/dashboard'));
  }, [projectId, router]);

  const fetchNotes = useCallback(() => {
    const params = new URLSearchParams();
    if (search) params.set('q', search);
    if (activeTab === 'research') params.set('note_type', 'research');
    if (activeTab === 'inspiration') params.set('is_inspiration', 'true');
    const qs = params.toString();
    return api<Note[]>(`/api/v1/projects/${projectId}/notes${qs ? `?${qs}` : ''}`)
      .then(setNotes)
      .catch(() => setNotes([]));
  }, [projectId, search, activeTab]);

  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  useEffect(() => {
    setLoading(true);
    fetchNotes().finally(() => setLoading(false));
  }, [fetchNotes]);

  const handleQuickCapture = async () => {
    if (!quickCapture.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/notes`, {
        method: 'POST',
        body: JSON.stringify({
          title: quickCapture.slice(0, 100) + (quickCapture.length > 100 ? '...' : ''),
          content: quickCapture,
          note_type: 'idea',
        }),
      });
      setQuickCapture('');
      fetchNotes();
      toast({ title: 'Note captured' });
    } catch (e) {
      toast({
        title: 'Failed to save',
        description: e instanceof Error ? e.message : 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const handlePin = async (note: Note) => {
    try {
      await api(note.pinned ? `/api/v1/projects/${projectId}/notes/${note.id}/unpin` : `/api/v1/projects/${projectId}/notes/${note.id}/pin`, {
        method: 'POST',
      });
      fetchNotes();
      if (selectedNote?.id === note.id) setSelectedNote({ ...note, pinned: !note.pinned });
    } catch {
      toast({ title: 'Failed to update', variant: 'destructive' });
    }
  };

  const handleInspiration = async (note: Note) => {
    try {
      if (note.is_inspiration) {
        await api(`/api/v1/projects/${projectId}/notes/${note.id}/inspiration`, { method: 'DELETE' });
      } else {
        await api(`/api/v1/projects/${projectId}/notes/${note.id}/inspiration`, { method: 'POST' });
      }
      fetchNotes();
      if (selectedNote?.id === note.id) setSelectedNote({ ...note, is_inspiration: !note.is_inspiration });
    } catch {
      toast({ title: 'Failed to update', variant: 'destructive' });
    }
  };

  const handleSaveNote = async (updates: Partial<Note>) => {
    if (!selectedNote) return;
    setSaving(true);
    try {
      const updated = await api<Note>(`/api/v1/projects/${projectId}/notes/${selectedNote.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          title: updates.title ?? selectedNote.title,
          content: updates.content ?? selectedNote.content,
          note_type: updates.note_type ?? selectedNote.note_type,
          source: updates.source ?? selectedNote.source,
          source_url: updates.source_url ?? selectedNote.source_url,
          category: updates.category ?? selectedNote.category,
          tags: updates.tags ?? selectedNote.tags,
        }),
      });
      setSelectedNote(updated);
      fetchNotes();
      toast({ title: 'Note saved' });
    } catch (e) {
      toast({
        title: 'Failed to save',
        description: e instanceof Error ? e.message : 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleUpload = async (file: File) => {
    if (!selectedNote) return;
    setUploading(true);
    try {
      const updated = await apiUpload<Note>(
        `/api/v1/projects/${projectId}/notes/${selectedNote.id}/attachments`,
        file
      );
      setSelectedNote(updated);
      fetchNotes();
      toast({ title: 'Attachment added' });
    } catch (e) {
      toast({
        title: 'Upload failed',
        description: e instanceof Error ? e.message : 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (note: Note) => {
    if (!confirm('Delete this note?')) return;
    try {
      await api(`/api/v1/projects/${projectId}/notes/${note.id}`, { method: 'DELETE' });
      setSelectedNote(null);
      fetchNotes();
      toast({ title: 'Note deleted' });
    } catch {
      toast({ title: 'Failed to delete', variant: 'destructive' });
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-5xl">
      <div className="flex items-center gap-4 mb-6">
        <Link href={`/dashboard/projects/${projectId}`}>
          <Button variant="ghost" size="sm">
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
        </Link>
      </div>

      <PageHeader
        title={project?.name ?? 'Notes'}
        description="Notebook, research, and inspiration board"
        backHref="/dashboard/notes"
        backLabel="Notes"
      />

      {/* Quick capture */}
      <Card variant="soft" className="mb-6">
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Input
              placeholder="Quick idea capture..."
              value={quickCapture}
              onChange={(e) => setQuickCapture(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuickCapture()}
              className="flex-1"
            />
            <Button onClick={handleQuickCapture} disabled={saving || !quickCapture.trim()}>
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs.Root value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <Tabs.List className="flex gap-2 border-b border-border/60 pb-2">
          <Tabs.Trigger
            value="notebook"
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'notebook' ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:text-foreground'
            )}
          >
            <StickyNote className="h-4 w-4 inline mr-2" />
            Notebook
          </Tabs.Trigger>
          <Tabs.Trigger
            value="research"
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'research' ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:text-foreground'
            )}
          >
            <Search className="h-4 w-4 inline mr-2" />
            Research
          </Tabs.Trigger>
          <Tabs.Trigger
            value="inspiration"
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'inspiration' ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:text-foreground'
            )}
          >
            <Sparkles className="h-4 w-4 inline mr-2" />
            Inspiration
          </Tabs.Trigger>
        </Tabs.List>

        <div className="flex gap-2 mb-4">
          <Input
            placeholder="Search notes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="max-w-xs"
          />
        </div>

        <Tabs.Content value="notebook" className="mt-0">
          <NoteList
            notes={notes}
            loading={loading}
            onSelect={setSelectedNote}
            onPin={handlePin}
            onInspiration={handleInspiration}
          />
        </Tabs.Content>
        <Tabs.Content value="research" className="mt-0">
          <NoteList
            notes={notes}
            loading={loading}
            onSelect={setSelectedNote}
            onPin={handlePin}
            onInspiration={handleInspiration}
          />
        </Tabs.Content>
        <Tabs.Content value="inspiration" className="mt-0">
          <NoteList
            notes={notes}
            loading={loading}
            onSelect={setSelectedNote}
            onPin={handlePin}
            onInspiration={handleInspiration}
          />
        </Tabs.Content>
      </Tabs.Root>

      {/* Note detail */}
      {selectedNote && (
        <NoteDetailDrawer
          note={selectedNote}
          onClose={() => setSelectedNote(null)}
          onSave={handleSaveNote}
          onUpload={handleUpload}
          onDelete={() => handleDelete(selectedNote)}
          saving={saving}
          uploading={uploading}
        />
      )}
    </div>
  );
}

function NoteList({
  notes,
  loading,
  onSelect,
  onPin,
  onInspiration,
}: {
  notes: Note[];
  loading: boolean;
  onSelect: (n: Note) => void;
  onPin: (n: Note) => void;
  onInspiration: (n: Note) => void;
}) {
  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }
  if (notes.length === 0) {
    const config = getEmptyStateConfig('no_notes')!;
    return (
      <Card variant="soft" className="p-12 text-center">
        <StickyNote className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="font-semibold mb-2">{config.title}</h3>
        <p className="text-muted-foreground text-sm max-w-sm mx-auto">{config.description}</p>
      </Card>
    );
  }
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {notes.map((n) => (
        <Card
          key={n.id}
          variant="sanctuary"
          className="p-4 cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => onSelect(n)}
        >
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-medium flex-1 truncate">{n.title}</h4>
            <div className="flex gap-1 shrink-0">
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); onPin(n); }}>
                {n.pinned ? <PinOff className="h-3.5 w-3" /> : <Pin className="h-3.5 w-3" />}
              </Button>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); onInspiration(n); }}>
                <Sparkles className={cn('h-3.5 w-3', n.is_inspiration && 'text-amber-500 fill-amber-500')} />
              </Button>
            </div>
          </div>
          <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{n.content}</p>
          {n.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {n.tags.slice(0, 3).map((t) => (
                <Badge key={t} variant="soft" className="text-xs">
                  {t}
                </Badge>
              ))}
            </div>
          )}
        </Card>
      ))}
    </div>
  );
}

function NoteDetailDrawer({
  note,
  onClose,
  onSave,
  onUpload,
  onDelete,
  saving,
  uploading,
}: {
  note: Note;
  onClose: () => void;
  onSave: (u: Partial<Note>) => void;
  onUpload: (f: File) => void;
  onDelete: () => void;
  saving: boolean;
  uploading: boolean;
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [title, setTitle] = useState(note.title);
  const [content, setContent] = useState(note.content);
  const [source, setSource] = useState(note.source ?? '');
  const [sourceUrl, setSourceUrl] = useState(note.source_url ?? '');
  const [category, setCategory] = useState(note.category ?? '');
  const [tags, setTags] = useState(note.tags.join(', '));
  const [noteType, setNoteType] = useState(note.note_type);

  useEffect(() => {
    setTitle(note.title);
    setContent(note.content);
    setSource(note.source ?? '');
    setSourceUrl(note.source_url ?? '');
    setCategory(note.category ?? '');
    setTags(note.tags.join(', '));
    setNoteType(note.note_type);
  }, [note.id]);

  const save = () => {
    onSave({
      title,
      content,
      source: source || null,
      source_url: sourceUrl || null,
      category: category || null,
      tags: tags ? tags.split(',').map((t) => t.trim()).filter(Boolean) : [],
      note_type: noteType,
    });
  };

  return (
    <div className="fixed inset-0 z-[99990] bg-black/50 flex items-center justify-center p-4" onClick={onClose}>
      <div
        className="bg-background rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b p-4">
          <h3 className="font-semibold">Edit note</h3>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="p-4 space-y-4">
          <div>
            <label className="text-sm font-medium text-muted-foreground">Title</label>
            <Input value={title} onChange={(e) => setTitle(e.target.value)} className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Type</label>
            <select
              value={noteType}
              onChange={(e) => setNoteType(e.target.value)}
              className="mt-1 w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              {NOTE_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Content</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={6}
              className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Source</label>
              <Input value={source} onChange={(e) => setSource(e.target.value)} placeholder="Book, article..." className="mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">URL</label>
              <Input value={sourceUrl} onChange={(e) => setSourceUrl(e.target.value)} placeholder="https://..." className="mt-1" />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Category</label>
            <Input value={category} onChange={(e) => setCategory(e.target.value)} placeholder="e.g. Characters" className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Tags (comma-separated)</label>
            <Input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="tag1, tag2" className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Attachments</label>
            <div className="mt-2 flex flex-wrap gap-2">
              {note.attachments.map((a) => (
                <Badge key={a.id} variant="secondary" className="gap-1">
                  <Paperclip className="h-3 w-3" />
                  {a.filename}
                </Badge>
              ))}
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) onUpload(f);
                  e.target.value = '';
                }}
                disabled={uploading}
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
              >
                {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Paperclip className="h-4 w-4" />}
                Add file
              </Button>
            </div>
          </div>
        </div>
        <div className="flex justify-between border-t p-4">
          <Button variant="destructive" onClick={onDelete}>
            Delete
          </Button>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={save} disabled={saving}>
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Save
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
