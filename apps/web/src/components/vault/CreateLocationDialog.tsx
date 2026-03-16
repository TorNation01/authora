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
import { WORLDBUILDING } from '@/content/vault-copy';

interface CreateLocationDialogProps {
  projectId: string;
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function CreateLocationDialog({
  projectId,
  open,
  onClose,
  onCreated,
}: CreateLocationDialogProps) {
  const [name, setName] = useState('');
  const [category, setCategory] = useState('location');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/vault/locations`, {
        method: 'POST',
        body: JSON.stringify({
          name: name.trim(),
          category,
        }),
      });
      setName('');
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
          <DialogTitle>{WORLDBUILDING.addLocationTitle}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={WORLDBUILDING.namePlaceholder}
              className="mt-1"
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="category">Category</Label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="mt-1 w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="location">Location</option>
              <option value="world">World</option>
              <option value="organisation">Organisation</option>
              <option value="faction">Faction</option>
              <option value="culture">Culture</option>
              <option value="concept">Concept</option>
            </select>
          </div>
          <DialogFooter>
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving || !name.trim()}>
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Add
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
