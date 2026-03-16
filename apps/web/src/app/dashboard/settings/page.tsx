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
import { useToast } from '@/hooks/use-toast';
import { createCustomerPortalSession } from '@/lib/billing';
import { UsageDisplay } from '@/components/billing/UsageDisplay';

interface User {
  id: string;
  email: string;
  display_name: string | null;
  created_at: string;
}

export default function SettingsPage() {
  const { toast } = useToast();
  const config = useConfig();
  const [user, setUser] = useState<User | null>(null);
  const [displayName, setDisplayName] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [savingPassword, setSavingPassword] = useState(false);

  const canEditProfile = config.feature_flags.standalone_auth;

  useEffect(() => {
    api<User>('/api/v1/auth/me')
      .then((u) => {
        setUser(u);
        setDisplayName(u.display_name || '');
      })
      .catch(() => setUser(null));
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

  return (
    <div className="p-6 lg:p-8 max-w-xl space-y-8">
      <PageHeader title="Settings" description="Your account and preferences" />

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
                Manage subscription
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

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
