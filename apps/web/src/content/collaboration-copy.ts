/**
 * Collaboration, sharing, beta-reader, editor-review, and client-review copy.
 * Tone: premium, calm, professional, clear, reassuring, non-technical.
 */

// ─── Permission groups ─────────────────────────────────────────────────────

export const PERMISSION_GROUPS = {
  canView: 'Can view',
  canComment: 'Can comment',
  canReview: 'Can review',
  canEdit: 'Can edit',
  canApprove: 'Can approve',
  canManageAccess: 'Can manage access',
} as const;

// ─── Sharing headings ───────────────────────────────────────────────────────

export const SHARING_HEADINGS = {
  shareProject: 'Share this project',
  inviteSomeone: 'Invite someone in',
  giveRightAccess: 'Give the right level of access',
  keepControl: 'Keep control while opening the work up',
  peopleWithAccess: 'People with access',
  whatCollaboratorsSee: 'What collaborators can see',
} as const;

// ─── Invite labels ──────────────────────────────────────────────────────────

export const INVITE_LABELS = {
  inviteByEmail: 'Invite by email',
  assignRole: 'Assign role',
  chooseAccessLevel: 'Choose access level',
  shareSelectedChapters: 'Share selected chapters',
  setAccessExpiry: 'Set access expiry',
  revokeAccess: 'Revoke access',
  resendInvite: 'Resend invite',
  inviteCollaborator: 'Invite collaborator',
} as const;

// ─── Role options ───────────────────────────────────────────────────────────

export interface RoleOption {
  value: string;
  label: string;
  description: string;
  permissionGroups: readonly (keyof typeof PERMISSION_GROUPS)[];
}

export const COLLABORATION_ROLES: RoleOption[] = [
  {
    value: 'editor',
    label: 'Editor',
    description: 'Review the manuscript in depth. Track notes, issues, and revision priorities clearly.',
    permissionGroups: ['canView', 'canComment', 'canReview', 'canEdit'],
  },
  {
    value: 'beta_reader',
    label: 'Beta reader',
    description: 'Share a clean version for feedback. Let readers respond without exposing the full workspace.',
    permissionGroups: ['canView', 'canComment'],
  },
  {
    value: 'client',
    label: 'Client',
    description: 'Share only what is ready. Approve chapters and request changes clearly.',
    permissionGroups: ['canView', 'canComment', 'canApprove'],
  },
  {
    value: 'reviewer',
    label: 'Reviewer',
    description: 'Review and approve chapters. Keep delivery stages organised.',
    permissionGroups: ['canView', 'canComment', 'canReview', 'canApprove'],
  },
  {
    value: 'co_writer',
    label: 'Co-writer',
    description: 'Collaborate on writing with full edit access.',
    permissionGroups: ['canView', 'canComment', 'canEdit'],
  },
  {
    value: 'viewer',
    label: 'Viewer',
    description: 'View only. No editing or commenting.',
    permissionGroups: ['canView'],
  },
];

// ─── Share scopes ───────────────────────────────────────────────────────────

export const SHARE_SCOPES: { value: string; label: string; description: string }[] = [
  {
    value: 'manuscript',
    label: 'Full manuscript',
    description: 'Share the complete manuscript.',
  },
  {
    value: 'chapters',
    label: 'Share selected chapters',
    description: 'Only the chapters you choose.',
  },
  {
    value: 'review_copy',
    label: 'Review copy',
    description: 'A clean, read-only version for feedback.',
  },
];

// ─── Invite status labels ───────────────────────────────────────────────────

export const INVITE_STATUS_LABELS: Record<string, string> = {
  pending: 'Pending',
  accepted: 'Accepted',
  expired: 'Expired',
  revoked: 'Revoked',
};

// ─── Approval status labels ──────────────────────────────────────────────────

export const APPROVAL_STATUS_LABELS: Record<string, string> = {
  pending: 'Ready for review',
  approved: 'Approved',
  rejected: 'Rejected',
  changes_requested: 'Changes requested',
  locked: 'Locked for delivery',
};

// ─── Beta reader copy ──────────────────────────────────────────────────────

export const BETA_READER_COPY = {
  readerView: 'Reader view',
  shareCleanVersion: 'Share a clean version for feedback',
  respondWithoutExposing: 'Let readers respond without exposing the full workspace',
  collectFeedbackChapterByChapter: 'Collect feedback chapter by chapter',
} as const;

// ─── Editor copy ────────────────────────────────────────────────────────────

export const EDITOR_COPY = {
  editorReview: 'Editor review',
  reviewInDepth: 'Review the manuscript in depth',
  trackNotesAndPriorities: 'Track notes, issues, and revision priorities clearly',
} as const;

// ─── Client copy ────────────────────────────────────────────────────────────

export const CLIENT_COPY = {
  clientReview: 'Client review',
  shareOnlyReady: 'Share only what is ready',
  approveAndRequestChanges: 'Approve chapters and request changes clearly',
  keepDeliveryStagesOrganised: 'Keep delivery stages organised',
} as const;

// ─── Safety copy ────────────────────────────────────────────────────────────

export const SAFETY_COPY = {
  privateNotesStayPrivate: 'Private notes stay private unless you choose to share them.',
  youControlVisibility: 'You control what others can see.',
  accessCanChangeAnytime: 'Access can be changed at any time.',
} as const;

// ─── Sharing page copy ───────────────────────────────────────────────────────

export const SHARING_PAGE_COPY = {
  title: 'Sharing & access',
  emptyState: 'Invite someone in when you want feedback. Share your manuscript with beta readers, editors, or clients—you control what others see.',
  inviteDialogTitle: 'Invite someone in',
  inviteDialogDescription:
    "They'll receive an email to accept. Choose a role to give the right level of access.",
  peopleSectionDescription:
    'Give the right level of access. Keep control while opening the work up.',
  shareScopeDescription:
    'You control what others can see. By default, invited collaborators get access to the full manuscript. Use shares to limit access to selected chapters or a review copy.',
  accessDenied: "You don't have permission to manage sharing for this project.",
  revokeAccess: 'Revoke access',
  resendInvite: 'Resend invite',
  accessRevoked: 'Access revoked',
  inviteSent: 'Invite sent',
  inviteRevoked: 'Invite revoked',
  inviteResent: 'Invite resent',
} as const;

// ─── Settings page copy ─────────────────────────────────────────────────────

export const SHARING_SETTINGS_CARD = {
  title: 'Sharing & access',
  description:
    'Invite collaborators, assign roles, and manage who can view, comment, or approve. You control what others can see.',
} as const;

// ─── Comment tags (review signalling) ───────────────────────────────────────

export const COMMENT_TAGS: { value: string; label: string }[] = [
  { value: 'clarity', label: 'Clarity' },
  { value: 'rewrite', label: 'Rewrite' },
  { value: 'pacing', label: 'Pacing' },
  { value: 'continuity', label: 'Continuity' },
  { value: 'tone', label: 'Tone' },
  { value: 'emotion', label: 'Emotion' },
  { value: 'grammar', label: 'Grammar' },
  { value: 'proofing', label: 'Proofing' },
  { value: 'fact_check', label: 'Fact check' },
  { value: 'question', label: 'Question' },
  { value: 'approval', label: 'Approval' },
  { value: 'change_request', label: 'Change request' },
  { value: 'idea', label: 'Idea' },
  { value: 'client_request', label: 'Client request' },
  { value: 'beta_feedback', label: 'Beta feedback' },
  { value: 'general', label: 'General' },
  { value: 'other', label: 'Other' },
];

// ─── Comment statuses (review workflow) ──────────────────────────────────────

export const COMMENT_STATUSES: { value: string; label: string }[] = [
  { value: 'open', label: 'Open' },
  { value: 'in_review', label: 'In review' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'deferred', label: 'Deferred' },
  { value: 'needs_decision', label: 'Needs decision' },
];

// ─── Chapter approval copy ──────────────────────────────────────────────────

export const CHAPTER_APPROVAL_COPY = {
  title: 'Chapter approval',
  description:
    'Approve chapters and request changes clearly. Keep delivery stages organised.',
  readyForReview: 'Ready for review',
  changesRequested: 'Changes requested',
  approved: 'Approved',
  lockedForDelivery: 'Locked for delivery',
  chapterApproved: 'Chapter approved',
  statusUpdated: 'Status updated',
} as const;
