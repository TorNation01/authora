'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/layout/PageHeader';
import { api } from '@/lib/api';
import { useConfig } from '@/contexts/ConfigProvider';
import { useTheme } from '@/contexts/ThemeProvider';
import { useToast } from '@/hooks/use-toast';
import { createCustomerPortalSession } from '@/lib/billing';
import { UsageDisplay } from '@/components/billing/UsageDisplay';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Sparkles, Sun, Moon } from 'lucide-react';

interface User {
  id: string;
  email: string;
  display_name: string | null;
  created_at: string;
}

interface AIPersonalization {
  enabled: boolean;
  tone_preferences: string[];
  style_profile: {
    voice?: string;
    tone?: string;
    vocabulary?: string;
    sentence_style?: string;
  } | null;
  updated_at: string | null;
}

interface Book {
  id: string;
  title: string;
  project_id: string;
}

export default function SettingsPage() {
  const { toast } = useToast();
  const config = useConfig();
  const { theme, setTheme } = useTheme();
  const [user, setUser] = useState<User | null>(null);
  const [displayName, setDisplayName] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [savingPassword, setSavingPassword] = useState(false);
  const [aiPersonalization, setAIPersonalization] = useState<AIPersonalization | null>(null);
  const [books, setBooks] = useState<Book[]>([]);
  const [learnBookId, setLearnBookId] = useState('');
  const [savingPersonalization, setSavingPersonalization] = useState(false);
  const [toneInput, setToneInput] = useState('');

  const canEditProfile = config.feature_flags.standalone_auth;

  useEffect(() => {
    api<User>('/api/v1/auth/me')
      .then((u) => {
        setUser(u);
        setDisplayName(u.display_name || '');
      })
      .catch(() => setUser(null));
  }, []);

  useEffect(() => {
    api<AIPersonalization>('/api/v1/auth/me/ai-personalization')
      .then((p) => {
        setAIPersonalization(p);
        if (p?.tone_preferences?.length) setToneInput(p.tone_preferences.join(', '));
      })
      .catch(() => setAIPersonalization(null));
  }, []);

  useEffect(() => {
    api<{ id: string; name: string }[]>('/api/v1/projects')
      .then((projects) =>
        Promise.all(projects.map((p) => api<Book[]>(`/api/v1/projects/${p.id}/books`)))
      )
      .then((results) => setBooks(results.flat()))
      .catch(() => setBooks([]));
  }, []);

  async function handleSaveProfile(e: React.FormEvent) {
    e.preventDefault();
    if (!canEditProfile) return;
    setSavingProfile(true);
    try {
      const updated = await api<User>('/api/v1/auth/me', {
        method: 'PATCH',
        body: JSON.stringify({ display_name: displayName.trim() || null }),
      });
      setUser(updated);
      toast({ title: 'Profile updated' });
    } catch (err) {
      toast({ title: 'Failed to update', variant: 'destructive' });
    } finally {
      setSavingProfile(false);
    }
  }

  async function handleChangePassword(e: React.FormEvent) {
    e.preventDefault();
    if (!canEditProfile) return;
    if (newPassword !== confirmPassword) {
      toast({ title: 'Passwords do not match', variant: 'destructive' });
      return;
    }
    if (newPassword.length < 8) {
      toast({ title: 'Password must be at least 8 characters', variant: 'destructive' });
      return;
    }
    setSavingPassword(true);
    try {
      await api('/api/v1/auth/me/password', {
        method: 'PATCH',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      toast({ title: 'Password updated' });
    } catch (err) {
      toast({ title: 'Failed to update password. Check current password.', variant: 'destructive' });
    } finally {
      setSavingPassword(false);
    }
  }

  async function handleTogglePersonalization(enabled: boolean) {
    setSavingPersonalization(true);
    try {
      const updated = await api<AIPersonalization>('/api/v1/auth/me/ai-personalization', {
        method: 'PATCH',
        body: JSON.stringify({ enabled }),
      });
      setAIPersonalization(updated);
      toast({ title: enabled ? 'Personalization on' : 'Personalization off' });
    } catch {
      toast({ title: 'Failed to update', variant: 'destructive' });
    } finally {
      setSavingPersonalization(false);
    }
  }

  async function handleUpdateTonePreferences() {
    const tones = toneInput
      .split(/[,\s]+/)
      .map((t) => t.trim().toLowerCase())
      .filter(Boolean);
    setSavingPersonalization(true);
    try {
      const updated = await api<AIPersonalization>('/api/v1/auth/me/ai-personalization', {
        method: 'PATCH',
        body: JSON.stringify({ tone_preferences: tones }),
      });
      setAIPersonalization(updated);
      setToneInput(tones.join(', '));
      toast({ title: 'Tone preferences saved' });
    } catch {
      toast({ title: 'Failed to update', variant: 'destructive' });
    } finally {
      setSavingPersonalization(false);
    }
  }

  async function handleResetStyleProfile() {
    setSavingPersonalization(true);
    try {
      const updated = await api<AIPersonalization>('/api/v1/auth/me/ai-personalization/reset', {
        method: 'POST',
      });
      setAIPersonalization(updated);
      toast({ title: 'Style profile reset' });
    } catch {
      toast({ title: 'Failed to reset', variant: 'destructive' });
    } finally {
      setSavingPersonalization(false);
    }
  }

  async function handleLearnFromBook() {
    if (!learnBookId) {
      toast({ title: 'Select a book first', variant: 'destructive' });
      return;
    }
    setSavingPersonalization(true);
    try {
      const updated = await api<AIPersonalization>('/api/v1/auth/me/ai-personalization/learn', {
        method: 'POST',
        body: JSON.stringify({ book_id: learnBookId }),
      });
      setAIPersonalization(updated);
      toast({ title: 'Style learned from book' });
    } catch {
      toast({ title: 'Failed to learn style', variant: 'destructive' });
    } finally {
      setSavingPersonalization(false);
    }
  }

  return (
    <div className="p-6 lg:p-8 max-w-xl space-y-8">
      <PageHeader title="Settings" description="Your account and preferences" />

      <Card variant="sanctuary">
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Choose light or dark theme. Light is the default.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Label htmlFor="theme">Theme</Label>
            <Select value={theme} onValueChange={(v) => setTheme(v as 'light' | 'dark')}>
              <SelectTrigger id="theme" className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">
                  <span className="flex items-center gap-2">
                    <Sun className="h-4 w-4" />
                    Light
                  </span>
                </SelectItem>
                <SelectItem value="dark">
                  <span className="flex items-center gap-2">
                    <Moon className="h-4 w-4" />
                    Dark
                  </span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Your preference is saved and applies across the app.
          </p>
        </CardContent>
      </Card>

      <Card variant="sanctuary">
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>Your account information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {user && (
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div className="space-y-2">
                <Label>Email</Label>
                <Input value={user.email} disabled className="bg-muted/50" />
                <p className="text-xs text-muted-foreground">Email cannot be changed.</p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="display_name">Display name</Label>
                {canEditProfile ? (
                  <>
                    <Input
                      id="display_name"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      placeholder="Your name"
                      disabled={savingProfile}
                    />
                    <Button type="submit" size="sm" disabled={savingProfile}>
                      {savingProfile ? 'Saving…' : 'Save'}
                    </Button>
                  </>
                ) : (
                  <>
                    <Input value={user.display_name || ''} disabled className="bg-muted/50" />
                    <p className="text-sm text-muted-foreground">
                      Account changes are managed by your administrator.
                    </p>
                  </>
                )}
              </div>
            </form>
          )}
        </CardContent>
      </Card>

      {canEditProfile && (
        <Card variant="sanctuary">
          <CardHeader>
            <CardTitle>Change password</CardTitle>
            <CardDescription>Update your password. Must be at least 8 characters.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current_password">Current password</Label>
                <Input
                  id="current_password"
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  disabled={savingPassword}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new_password">New password</Label>
                <Input
                  id="new_password"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  minLength={8}
                  disabled={savingPassword}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_password">Confirm new password</Label>
                <Input
                  id="confirm_password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  disabled={savingPassword}
                />
              </div>
              <Button type="submit" disabled={savingPassword}>
                {savingPassword ? 'Updating…' : 'Update password'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {config.feature_flags.billing && (
        <Card variant="sanctuary">
          <CardHeader>
            <CardTitle>Billing & plan</CardTitle>
            <CardDescription>
              Manage your subscription and view usage.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <UsageDisplay />
            <div className="flex gap-2">
              <Button asChild variant="outline" size="sm">
                <Link href="/dashboard/billing">Manage billing</Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link href="/pricing">View plans</Link>
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={async () => {
                  const url = await createCustomerPortalSession(window.location.href);
                  if (url?.url) window.location.href = url.url;
                  else toast({ title: 'Billing portal not available', variant: 'destructive' });
                }}
              >
                Stripe portal
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card variant="soft">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            AI personalization
          </CardTitle>
          <CardDescription>
            Adapt AI to your writing style. Optional—AI enhances, never replaces your voice.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Personalization</Label>
              <p className="text-sm text-muted-foreground">Turn on to adapt AI suggestions to your style</p>
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={aiPersonalization?.enabled ?? false}
                onChange={(e) => handleTogglePersonalization(e.target.checked)}
                disabled={savingPersonalization}
                className="rounded border-input"
              />
              <span className="text-sm">On</span>
            </label>
          </div>
          <div className="space-y-2">
            <Label>Tone preferences</Label>
            <p className="text-xs text-muted-foreground">e.g. formal, casual, lyrical (comma-separated)</p>
            <div className="flex gap-2">
              <Input
                value={toneInput}
                onChange={(e) => setToneInput(e.target.value)}
                placeholder="formal, conversational"
                disabled={savingPersonalization}
                onBlur={() => toneInput && handleUpdateTonePreferences()}
              />
              <Button size="sm" variant="outline" onClick={handleUpdateTonePreferences} disabled={savingPersonalization}>
                Save
              </Button>
            </div>
          </div>
          {aiPersonalization?.style_profile && (
            <div className="rounded-md border border-border/50 p-3 text-sm">
              <p className="font-medium mb-1">Learned style</p>
              <p className="text-muted-foreground">
                {[
                  aiPersonalization.style_profile.tone,
                  aiPersonalization.style_profile.sentence_style,
                ]
                  .filter(Boolean)
                  .join(' • ')}
              </p>
            </div>
          )}
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={handleResetStyleProfile}
              disabled={savingPersonalization || !aiPersonalization?.style_profile}
            >
              Reset style profile
            </Button>
            <div className="flex items-center gap-2">
              <select
                value={learnBookId}
                onChange={(e) => setLearnBookId(e.target.value)}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="">Learn from book...</option>
                {books.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.title}
                  </option>
                ))}
              </select>
              <Button
                size="sm"
                variant="outline"
                onClick={handleLearnFromBook}
                disabled={savingPersonalization || !learnBookId}
              >
                {savingPersonalization ? 'Learning…' : 'Learn style'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card variant="soft">
        <CardHeader>
          <CardTitle>AI features</CardTitle>
          <CardDescription>
            AI keys are configured by your administrator in the setup wizard or environment. Contact
            your admin to enable or change AI features.
          </CardDescription>
        </CardHeader>
      </Card>
    </div>
  );
}
