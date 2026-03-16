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
import { CHARACTER_BIBLE } from '@/content/vault-copy';

interface CreateCharacterDialogProps {
  projectId: string;
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function CreateCharacterDialog({
  projectId,
  open,
  onClose,
  onCreated,
}: CreateCharacterDialogProps) {
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/vault/characters`, {
        method: 'POST',
        body: JSON.stringify({
          full_name: name.trim(),
          role_in_story: role.trim() || undefined,
        }),
      });
      setName('');
      setRole('');
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
          <DialogTitle>{CHARACTER_BIBLE.addCharacterTitle}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={CHARACTER_BIBLE.namePlaceholder}
              className="mt-1"
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="role">Role (optional)</Label>
            <Input
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder={CHARACTER_BIBLE.rolePlaceholder}
              className="mt-1"
            />
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
