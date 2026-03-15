'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';

interface FinishModeSettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentTargetDate: string | null;
  currentWordsPerDay: number;
  onSave: (targetDate: string | null, wordsPerDay: number) => void;
}

export function FinishModeSettingsDialog({
  open,
  onOpenChange,
  currentTargetDate,
  currentWordsPerDay,
  onSave,
}: FinishModeSettingsDialogProps) {
  const [targetDate, setTargetDate] = useState(currentTargetDate || '');
  const [wordsPerDay, setWordsPerDay] = useState(String(currentWordsPerDay));

  const handleSave = () => {
    const date = targetDate.trim() || null;
    const words = Math.max(100, Math.min(5000, parseInt(wordsPerDay, 10) || 500));
    onSave(date, words);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Finish Mode Settings</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <Label htmlFor="target-date">Target finish date (optional)</Label>
            <Input
              id="target-date"
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="words-per-day">Words per day goal</Label>
            <Input
              id="words-per-day"
              type="number"
              min={100}
              max={5000}
              value={wordsPerDay}
              onChange={(e) => setWordsPerDay(e.target.value)}
              className="mt-1"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
