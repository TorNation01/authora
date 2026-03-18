'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Plus, Pencil } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

type Submission = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  category: string | null;
  price_cents: number | null;
  status: string;
  approved_template_id: string | null;
  created_at: string;
  reviewed_at: string | null;
  rejected_reason: string | null;
  change_request_reason: string | null;
  payload?: Record<string, unknown> | null;
};

export default function CreatorTemplatesPage() {
  const { toast } = useToast();
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [editTarget, setEditTarget] = useState<Submission | null>(null);
  const [editForm, setEditForm] = useState({ name: '', description: '', category: '', price_cents: '', payloadStr: '{}' });
  const [updating, setUpdating] = useState(false);
  const [form, setForm] = useState({
    name: '',
    slug: '',
    description: '',
    category: '',
    price_cents: '',
    payloadStr: '{}',
  });

  const fetchDashboard = () => {
    setLoading(true);
    api<{ submissions: Submission[] }>('/api/v1/creators/dashboard')
      .then((d) => setSubmissions(d.submissions ?? []))
      .catch(() => setSubmissions([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleCreate = async () => {
    if (!form.name.trim()) {
      toast({ title: 'Name is required', variant: 'destructive' });
      return;
    }
    try {
      JSON.parse(form.payloadStr || '{}');
    } catch {
      toast({ title: 'Invalid JSON in payload', variant: 'destructive' });
      return;
    }
    setCreating(true);
    try {
      await api('/api/v1/creators/submissions', {
        method: 'POST',
        body: JSON.stringify({
          name: form.name.trim(),
          slug: form.slug.trim() || undefined,
          description: form.description.trim() || undefined,
          category: form.category.trim() || undefined,
          price_cents: form.price_cents ? parseInt(form.price_cents, 10) : undefined,
          payload: (() => {
            try {
              const p = JSON.parse(form.payloadStr || '{}');
              return typeof p === 'object' && p !== null && Object.keys(p).length > 0 ? p : undefined;
            } catch {
              return undefined;
            }
          })(),
        }),
      });
      toast({ title: 'Template submitted', description: 'Your template is under review.' });
      setCreateOpen(false);
      setForm({ name: '', slug: '', description: '', category: '', price_cents: '', payloadStr: '{}' });
      fetchDashboard();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to submit';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setCreating(false);
    }
  };

  const openEdit = (s: Submission) => {
    setEditTarget(s);
    setEditForm({
      name: s.name,
      description: s.description || '',
      category: s.category || '',
      price_cents: s.price_cents != null ? String(s.price_cents) : '',
      payloadStr: s.payload ? JSON.stringify(s.payload, null, 2) : '{}',
    });
  };

  const handleUpdate = async () => {
    if (!editTarget) return;
    try {
      JSON.parse(editForm.payloadStr || '{}');
    } catch {
      toast({ title: 'Invalid JSON in payload', variant: 'destructive' });
      return;
    }
    setUpdating(true);
    try {
      await api(`/api/v1/creators/submissions/${editTarget.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          name: editForm.name.trim(),
          description: editForm.description.trim() || undefined,
          category: editForm.category.trim() || undefined,
          price_cents: editForm.price_cents ? parseInt(editForm.price_cents, 10) : undefined,
          payload: (() => {
            try {
              const p = JSON.parse(editForm.payloadStr || '{}');
              return typeof p === 'object' && p !== null ? p : undefined;
            } catch {
              return undefined;
            }
          })(),
        }),
      });
      toast({ title: 'Submission updated', description: 'Resubmitted for review.' });
      setEditTarget(null);
      fetchDashboard();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to update';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">My templates</h1>
          <p className="text-muted-foreground mt-1">
            Submit templates for review. Approved templates appear in the marketplace.
          </p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Submit template
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Submit template</DialogTitle>
              <DialogDescription>
                Provide template details. Include guidance text, prompts, and structure in the
                payload. Templates must be fully usable with no placeholders.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <Label>Name *</Label>
                <Input
                  value={form.name}
                  onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                  placeholder="e.g. Romance Novel Framework"
                />
              </div>
              <div>
                <Label>Slug (optional, auto-generated from name)</Label>
                <Input
                  value={form.slug}
                  onChange={(e) => setForm((p) => ({ ...p, slug: e.target.value }))}
                  placeholder="romance-novel-framework"
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea
                  value={form.description}
                  onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                  placeholder="Brief description for the marketplace"
                  rows={3}
                />
              </div>
              <div>
                <Label>Category</Label>
                <Input
                  value={form.category}
                  onChange={(e) => setForm((p) => ({ ...p, category: e.target.value }))}
                  placeholder="e.g. fiction, memoir, business"
                />
              </div>
              <div>
                <Label>Price (cents, 0 = free)</Label>
                <Input
                  type="number"
                  min={0}
                  value={form.price_cents}
                  onChange={(e) => setForm((p) => ({ ...p, price_cents: e.target.value }))}
                  placeholder="0"
                />
              </div>
              <div>
                <Label>Payload (JSON, optional)</Label>
                <Textarea
                  value={form.payloadStr}
                  onChange={(e) => setForm((p) => ({ ...p, payloadStr: e.target.value }))}
                  placeholder='{"book_type":"fiction","genre":"romance",...}'
                  rows={6}
                  className="font-mono text-sm"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Include: book_type, genre, who_it_is_for, expected_outcome, ai_prompts,
                  default_structure, setup_questions, chapter_skeletons, etc.
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreate} disabled={creating}>
                {creating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  'Submit'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={!!editTarget} onOpenChange={(o) => !o && setEditTarget(null)}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Edit submission</DialogTitle>
              <DialogDescription>
                Update your template and resubmit for review. Fix any issues noted in the change request.
              </DialogDescription>
            </DialogHeader>
            {editTarget && (
              <div className="space-y-4 py-4">
                <div>
                  <Label>Name *</Label>
                  <Input
                    value={editForm.name}
                    onChange={(e) => setEditForm((p) => ({ ...p, name: e.target.value }))}
                    placeholder="Template name"
                  />
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm((p) => ({ ...p, description: e.target.value }))}
                    placeholder="Brief description"
                    rows={3}
                  />
                </div>
                <div>
                  <Label>Category</Label>
                  <Input
                    value={editForm.category}
                    onChange={(e) => setEditForm((p) => ({ ...p, category: e.target.value }))}
                    placeholder="e.g. fiction, memoir"
                  />
                </div>
                <div>
                  <Label>Price (cents, 0 = free)</Label>
                  <Input
                    type="number"
                    min={0}
                    value={editForm.price_cents}
                    onChange={(e) => setEditForm((p) => ({ ...p, price_cents: e.target.value }))}
                    placeholder="0"
                  />
                </div>
                <div>
                  <Label>Payload (JSON)</Label>
                  <Textarea
                    value={editForm.payloadStr}
                    onChange={(e) => setEditForm((p) => ({ ...p, payloadStr: e.target.value }))}
                    placeholder="{}"
                    rows={6}
                    className="font-mono text-sm"
                  />
                </div>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setEditTarget(null)}>
                Cancel
              </Button>
              <Button onClick={handleUpdate} disabled={updating}>
                {updating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Updating...
                  </>
                ) : (
                  'Resubmit'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : submissions.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">No templates yet.</p>
            <Button className="mt-4" onClick={() => setCreateOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Submit your first template
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {submissions.map((s) => (
            <Card key={s.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{s.name}</h3>
                    <p className="text-sm text-muted-foreground">{s.slug}</p>
                    {s.description && (
                      <p className="text-sm mt-1 text-muted-foreground">{s.description}</p>
                    )}
                    <p className="text-xs text-muted-foreground mt-2">
                      Category: {s.category || '—'} · Price:{' '}
                      {s.price_cents != null ? `$${(s.price_cents / 100).toFixed(2)}` : 'Free'}
                    </p>
                  </div>
                  <span
                    className={`text-xs font-medium px-2 py-1 rounded shrink-0 ${
                      s.status === 'approved'
                        ? 'bg-green-500/10 text-green-600'
                        : s.status === 'rejected'
                          ? 'bg-destructive/10 text-destructive'
                          : s.status === 'changes_requested'
                            ? 'bg-amber-500/10 text-amber-600'
                            : 'bg-amber-500/10 text-amber-600'
                    }`}
                  >
                    {s.status.replace('_', ' ')}
                  </span>
                </div>
                {s.rejected_reason && (
                  <p className="text-sm text-destructive mt-2">Reason: {s.rejected_reason}</p>
                )}
                {s.change_request_reason && (
                  <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3 mt-2">
                    <p className="text-xs font-medium text-amber-700 dark:text-amber-400">Changes requested</p>
                    <p className="text-sm mt-1">{s.change_request_reason}</p>
                    <p className="text-xs text-muted-foreground mt-2">Edit your submission and resubmit for review.</p>
                  </div>
                )}
                {(s.status === 'pending' || s.status === 'changes_requested') && s.payload != null && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-2"
                    onClick={() => openEdit(s)}
                  >
                    <Pencil className="h-4 w-4 mr-2" />
                    Edit
                  </Button>
                )}
                <p className="text-xs text-muted-foreground mt-2">
                  Submitted: {new Date(s.created_at).toLocaleDateString()}
                  {s.reviewed_at && ` · Reviewed: ${new Date(s.reviewed_at).toLocaleDateString()}`}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
