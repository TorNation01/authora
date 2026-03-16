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
import { SOURCE_MANAGER } from '@/content/vault-copy';

interface CreateSourceDialogProps {
  projectId: string;
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function CreateSourceDialog({
  projectId,
  open,
  onClose,
  onCreated,
}: CreateSourceDialogProps) {
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [sourceType, setSourceType] = useState('book');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/vault/sources`, {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim(),
          author: author.trim() || undefined,
          source_type: sourceType,
        }),
      });
      setTitle('');
      setAuthor('');
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
          <DialogTitle>{SOURCE_MANAGER.addSourceTitle}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={SOURCE_MANAGER.titlePlaceholder}
              className="mt-1"
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="author">Author (optional)</Label>
            <Input
              id="author"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              placeholder={SOURCE_MANAGER.authorPlaceholder}
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="type">Type</Label>
            <select
              id="type"
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="mt-1 w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="book">Book</option>
              <option value="article">Article</option>
              <option value="website">Website</option>
              <option value="interview">Interview</option>
            </select>
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
