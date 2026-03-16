# AUTHORA Collaboration System

The collaboration system allows AUTHORA users to safely share manuscripts, chapters, review copies, or project areas with other people for editing, feedback, approval, review, or co-writing without compromising project structure or user control.

## Overview

- **Collaboration roles** – Owner, Admin, Editor, Beta Reader, Reviewer, Client, Co-Writer, Viewer, Guest
- **Permissions** – Granular control over view, edit, comment, approve, manage invites, shares, and activity
- **Invite system** – Email invites with optional message, role assignment, token-based acceptance
- **Sharing scopes** – Full project, manuscript, selected chapters, or review copy only
- **Approval workflows** – Chapter-level approval with statuses: pending, approved, rejected, changes_requested
- **Activity audit** – Timestamped activity feed for accountability

## API Endpoints

### Invites

- `POST /api/v1/invites/accept` – Accept invite by token (authenticated user)
- `GET /api/v1/projects/{project_id}/invites` – List invites (manage_invites)
- `POST /api/v1/projects/{project_id}/invites` – Create invite (manage_invites)
- `POST /api/v1/projects/{project_id}/invites/{invite_id}/resend` – Resend invite (manage_invites)
- `POST /api/v1/projects/{project_id}/invites/{invite_id}/revoke` – Revoke invite (manage_invites)

### Members

- `GET /api/v1/projects/{project_id}/members` – List members (manage_members)
- `GET /api/v1/projects/{project_id}/members/{member_id}` – Get member (manage_members)
- `DELETE /api/v1/projects/{project_id}/members/{member_id}` – Remove member (manage_members)

### Shares

- `GET /api/v1/projects/{project_id}/shares` – List shares (manage_shares)
- `POST /api/v1/projects/{project_id}/shares` – Create share (manage_shares)

### Chapter Approval

- `GET /api/v1/projects/{project_id}/books/{book_id}/chapters/{chapter_id}/approval` – Get approval (view_manuscript or approve_chapters)
- `POST /api/v1/projects/{project_id}/books/{book_id}/chapters/{chapter_id}/approval` – Create approval (approve_chapters)
- `PATCH /api/v1/projects/{project_id}/books/{book_id}/chapters/{chapter_id}/approval` – Update approval (approve_chapters)

### Activity

- `GET /api/v1/projects/{project_id}/activity` – List activity feed (view_activity)

## Access Model

- **Owner** – Project creator; full access via `project.user_id` or `ProjectMember` with role `owner`
- **Members** – Access via `ProjectMember`; role determines permissions
- **Project listing** – Users see projects they own or are members of
- **Book/chapter access** – Resolved via `get_project_with_access_or_404` and `get_book_with_access_or_404`

## Security

- Invite tokens are URL-safe, unique, and expire (default 7 days)
- Invite acceptance requires authenticated user email to match invite email
- Private author-only material remains protected; role permissions control visibility

## Invite Accept – Expected Behaviour

| Scenario | Response | Behaviour |
|----------|----------|-----------|
| Valid token, matching email | 201 | Creates `ProjectMember`, sets invite `status=accepted`, records activity |
| Expired invite | 400 | Returns "Invite has expired"; invite `status` set to `expired` |
| Revoked invite | 400 | Returns "Invite is no longer valid (status: revoked)" |
| Wrong email | 403 | Returns "Your email does not match the invite" |
| Already a member | 400 | Returns "You are already a member of this project" |
| Invalid token | 404 | Returns "Invite not found or invalid token" |
| Unauthenticated | 401 | Auth required before invite lookup |

## See Also

- [ROLES_AND_PERMISSIONS.md](ROLES_AND_PERMISSIONS.md)
- [BETA_READER_MODE.md](BETA_READER_MODE.md)
- [EDITOR_REVIEW_MODE.md](EDITOR_REVIEW_MODE.md)
- [CLIENT_REVIEW_MODE.md](CLIENT_REVIEW_MODE.md)
- [APPROVAL_WORKFLOWS.md](APPROVAL_WORKFLOWS.md)
- [COLLABORATION_AUDIT_LOG.md](COLLABORATION_AUDIT_LOG.md)
