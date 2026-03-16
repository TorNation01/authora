'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/api';
import { Loader2 } from 'lucide-react';
import { IDEA_CAPTURE } from '@/content/vault-copy';

interface CreateIdeaDialogProps {
  projectId: string;
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function CreateIdeaDialog({
  projectId,
  open,
  onClose,
  onCreated,
}: CreateIdeaDialogProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/vault/ideas`, {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim(),
          content: content.trim() || title.trim(),
          idea_type: 'idea_card',
          status: 'raw_idea',
        }),
      });
      setTitle('');
      setContent('');
      onCreated();
      onClose();
    } catch {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{IDEA_CAPTURE.addIdeaTitle}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={IDEA_CAPTURE.ideaTitlePlaceholder}
              className="mt-1"
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="content">{IDEA_CAPTURE.contentOptional}</Label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={IDEA_CAPTURE.moreDetails}
              rows={3}
              className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving || !title.trim()}>
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Add
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
