'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import {
  Users,
  Mail,
  Share2,
  CheckCircle2,
  Clock,
  XCircle,
  Trash2,
  RefreshCw,
  Activity,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/PageHeader';
import { api, ApiError } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  COLLABORATION_ROLES,
  PRIMARY_COLLABORATION_ROLES,
  SHARE_SCOPES,
  INVITE_STATUS_LABELS,
  INVITE_LABELS,
  SHARING_HEADINGS,
  SHARING_PAGE_COPY,
} from '@/content/collaboration-copy';

interface ProjectInvite {
  id: string;
  email: string;
  project_id: string;
  role: string;
  status: string;
  expires_at: string;
  created_at: string;
}

interface ProjectMember {
  id: string;
  user_id: string;
  project_id: string;
  role: string;
  joined_at: string;
  email?: string | null;
  display_name?: string | null;
}

interface ProjectShare {
  id: string;
  share_scope: string;
  chapter_ids: string[] | null;
  shared_with_email: string | null;
  created_at: string;
}

interface CollaborationActivity {
  id: string;
  action: string;
  entity_type: string | null;
  extra_data: Record<string, unknown> | null;
  created_at: string;
}

interface ProjectData {
  name: string;
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  pending: <Clock className="h-4 w-4 text-amber-500" />,
  accepted: <CheckCircle2 className="h-4 w-4 text-green-500" />,
  expired: <Clock className="h-4 w-4 text-muted-foreground" />,
  revoked: <XCircle className="h-4 w-4 text-muted-foreground" />,
};

function getRoleLabel(value: string): string {
  if (value === 'owner') return 'Owner';
  return COLLABORATION_ROLES.find((r) => r.value === value)?.label ?? value;
}

function formatActivityAction(a: CollaborationActivity): string {
  const actor = (a.extra_data?.actor_display_name as string) || 'Someone';
  const email = a.extra_data?.email as string | undefined;
  const role = a.extra_data?.role as string | undefined;
  switch (a.action) {
    case 'invite_created':
      return `${actor} invited ${email || 'someone'} as ${role ? getRoleLabel(role) : 'collaborator'}.`;
    case 'invite_accepted':
      return `${email || 'Someone'} joined as ${role ? getRoleLabel(role) : 'member'}.`;
    case 'member_removed':
      return `${actor} removed a member.`;
    case 'approval_created':
      return `${actor} requested chapter approval.`;
    case 'approval_updated':
      return `${actor} updated chapter approval.`;
    default:
      return `${actor} ${a.action.replace(/_/g, ' ')}.`;
  }
}

export default function ProjectSharingPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const projectId = params.id as string;

  const [project, setProject] = useState<ProjectData | null>(null);
  const [invites, setInvites] = useState<ProjectInvite[]>([]);
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [shares, setShares] = useState<ProjectShare[]>([]);
  const [activity, setActivity] = useState<CollaborationActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<string>('co_writer');
  const [inviting, setInviting] = useState(false);
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [revokingId, setRevokingId] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<string | null>(null);
  const [accessDenied, setAccessDenied] = useState(false);

  const fetchAll = useCallback(async () => {
    setAccessDenied(false);
    try {
      const proj = await api<ProjectData>(`/api/v1/projects/${projectId}`);
      setProject(proj);
      try {
        const [inv, mem, sh, act] = await Promise.all([
          api<ProjectInvite[]>(`/api/v1/projects/${projectId}/invites`),
          api<ProjectMember[]>(`/api/v1/projects/${projectId}/members`),
          api<ProjectShare[]>(`/api/v1/projects/${projectId}/shares`),
          api<CollaborationActivity[]>(`/api/v1/projects/${projectId}/activity`).catch(() => []),
        ]);
        setInvites(inv);
        setMembers(mem);
        setShares(sh);
        setActivity(act);
      } catch (err) {
        if (err instanceof ApiError && err.status === 403) setAccessDenied(true);
        else throw err;
      }
    } catch {
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  }, [projectId, router]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  async function handleInvite() {
    if (!inviteEmail.trim()) return;
    setInviting(true);
    try {
      await api(`/api/v1/projects/${projectId}/invites`, {
        method: 'POST',
        body: JSON.stringify({ email: inviteEmail.trim().toLowerCase(), role: inviteRole }),
      });
      toast({ title: SHARING_PAGE_COPY.inviteSent, description: `${inviteEmail} can now accept the invite.` });
      setInviteEmail('');
      setInviteRole('co_writer');
      setShowInviteDialog(false);
      fetchAll();
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'detail' in err ? String((err as { detail: unknown }).detail) : 'Failed to send invite';
      toast({ title: 'Invite failed', description: msg, variant: 'destructive' });
    } finally {
      setInviting(false);
    }
  }

  async function handleRevoke(inviteId: string) {
    setRevokingId(inviteId);
    try {
      await api(`/api/v1/projects/${projectId}/invites/${inviteId}/revoke`, { method: 'POST' });
      toast({ title: SHARING_PAGE_COPY.inviteRevoked });
      fetchAll();
    } catch {
      toast({ title: 'Failed to revoke', variant: 'destructive' });
    } finally {
      setRevokingId(null);
    }
  }

  async function handleResend(inviteId: string) {
    try {
      await api(`/api/v1/projects/${projectId}/invites/${inviteId}/resend`, { method: 'POST' });
      toast({ title: SHARING_PAGE_COPY.inviteResent });
      fetchAll();
    } catch {
      toast({ title: 'Failed to resend', variant: 'destructive' });
    }
  }

  async function handleRemoveMember(memberId: string) {
    setRemovingId(memberId);
    try {
      await api(`/api/v1/projects/${projectId}/members/${memberId}`, { method: 'DELETE' });
      toast({ title: SHARING_PAGE_COPY.accessRevoked });
      fetchAll();
    } catch {
      toast({ title: 'Failed to remove', variant: 'destructive' });
    } finally {
      setRemovingId(null);
    }
  }

  if (loading || !project) {
    return (
      <div className="p-6 lg:p-8">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (accessDenied) {
    return (
      <div className="p-6 lg:p-8 max-w-3xl">
        <PageHeader
          title="Sharing & access"
          description={project.name}
          backHref={`/dashboard/projects/${projectId}`}
          backLabel="Back to project"
        />
        <Card variant="sanctuary" className="mt-6">
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">
              You don&apos;t have permission to manage sharing for this project.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const pendingInvites = invites.filter((i) => i.status === 'pending');
  const acceptedInvites = invites.filter((i) => i.status === 'accepted');
  const otherInvites = invites.filter((i) => !['pending', 'accepted'].includes(i.status));

  return (
    <div className="p-6 lg:p-8 max-w-3xl">
      <PageHeader
        title={SHARING_PAGE_COPY.title}
        description={project.name}
        backHref={`/dashboard/projects/${projectId}`}
        backLabel="Back to project"
        actions={
          <Button onClick={() => setShowInviteDialog(true)}>
            <Mail className="h-4 w-4 mr-2" />
            {INVITE_LABELS.inviteCollaborator}
          </Button>
        }
      />

      {/* Invite collaborator */}
      <Card variant="sanctuary" className="mt-6">
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <Users className="h-5 w-5" />
            {SHARING_HEADINGS.peopleWithAccess}
          </CardTitle>
          <CardDescription>
            {SHARING_PAGE_COPY.peopleSectionDescription}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {members.length === 0 && pendingInvites.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4">
              {SHARING_PAGE_COPY.emptyState}
            </p>
          ) : (
            <div className="space-y-3">
              {members.map((m) => (
                <div
                  key={m.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div>
                    <p className="font-medium">
                      {m.display_name || m.email || 'Unknown'}
                      {m.email && m.display_name && (
                        <span className="text-muted-foreground font-normal ml-1">({m.email})</span>
                      )}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="secondary" className="text-xs">
                        {getRoleLabel(m.role)}
                      </Badge>
                      {m.role === 'owner' && (
                        <span className="text-xs text-muted-foreground">You</span>
                      )}
                    </div>
                  </div>
                  {m.role !== 'owner' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive"
                      onClick={() => handleRemoveMember(m.id)}
                      disabled={removingId === m.id}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
              {pendingInvites.map((i) => (
                <div
                  key={i.id}
                  className="flex items-center justify-between rounded-lg border border-dashed p-3"
                >
                  <div className="flex items-center gap-2">
                    {STATUS_ICONS[i.status] || <Clock className="h-4 w-4" />}
                    <div>
                      <p className="font-medium">{i.email}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-xs">
                          {getRoleLabel(i.role)}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {INVITE_STATUS_LABELS[i.status] || i.status}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {i.status === 'pending' && (
                      <>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleResend(i.id)}
                        >
                          <RefreshCw className="h-3 w-3 mr-1" />
                          {INVITE_LABELS.resendInvite}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-destructive"
                          onClick={() => handleRevoke(i.id)}
                          disabled={revokingId === i.id}
                        >
                          {INVITE_LABELS.revokeAccess}
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ))}
              {otherInvites.map((i) => (
                <div
                  key={i.id}
                  className="flex items-center gap-2 rounded-lg border p-3 opacity-75"
                >
                  {STATUS_ICONS[i.status]}
                  <div>
                    <p className="font-medium">{i.email}</p>
                    <span className="text-xs text-muted-foreground">
                      {INVITE_STATUS_LABELS[i.status] || i.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Activity feed */}
      {activity.length > 0 && (
        <Card variant="sanctuary" className="mt-6">
          <CardHeader>
            <CardTitle className="font-serif flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Activity
            </CardTitle>
            <CardDescription>
              Recent collaboration activity on this project.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {activity.slice(0, 15).map((a) => (
                <li key={a.id} className="flex items-start gap-3 text-sm">
                  <Activity className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                  <div>
                    <p>
                      {formatActivityAction(a)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {new Date(a.created_at).toLocaleString()}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Share scope info */}
      <Card variant="sanctuary" className="mt-6">
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <Share2 className="h-5 w-5" />
            {SHARING_HEADINGS.whatCollaboratorsSee}
          </CardTitle>
          <CardDescription>
            {SHARING_PAGE_COPY.shareScopeDescription}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {SHARE_SCOPES.map((s) => (
              <div key={s.value} className="flex items-center gap-2 text-sm">
                <span className="font-medium">{s.label}</span>
                <span className="text-muted-foreground">— {s.description}</span>
              </div>
            ))}
          </div>
          {shares.length > 0 && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm font-medium mb-2">Active shares</p>
              {shares.map((s) => (
                <div key={s.id} className="text-sm text-muted-foreground">
                  {s.share_scope} → {s.shared_with_email || 'user'}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Invite dialog */}
      <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{SHARING_PAGE_COPY.inviteDialogTitle}</DialogTitle>
            <DialogDescription>
              {SHARING_PAGE_COPY.inviteDialogDescription}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="invite-email">{INVITE_LABELS.inviteByEmail}</Label>
              <Input
                id="invite-email"
                type="email"
                placeholder="collaborator@example.com"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label>{INVITE_LABELS.assignRole}</Label>
              <Select value={inviteRole} onValueChange={setInviteRole}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PRIMARY_COLLABORATION_ROLES.map((r) => (
                    <SelectItem key={r.value} value={r.value}>
                      <div>
                        <span className="font-medium">{r.label}</span>
                        <span className="text-muted-foreground block text-xs">{r.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowInviteDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleInvite} disabled={inviting || !inviteEmail.trim()}>
              {inviting ? 'Sending...' : 'Send invite'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
