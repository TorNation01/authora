# Collaboration System — Production Summary

The AUTHORA collaboration system enables multiple users to work together on books, with role-based access, invites, inline comments, activity feed, and version control.

---

## 1. Core Features

| Feature | Status | Notes |
|---------|--------|-------|
| **Project sharing** | ✓ | Owner and members access via `get_project_with_access_or_404` |
| **Invite by email** | ✓ | Token-based invites, 7-day expiry, resend, revoke |
| **Role-based access** | ✓ | Owner, Editor, Writer, Viewer + extended roles |
| **Inline comments** | ✓ | `ContentComment` with offsets, `comment_type`, replies |
| **Activity feed** | ✓ | API + UI on sharing page |
| **Version control** | ✓ | `ChapterVersion` on each save, restore |
| **Change history** | ✓ | `GET /chapters/{id}/versions` |
| **Chapter approval** | ✓ | Pending, approved, rejected, changes_requested |

---

## 2. Roles and Permissions

### Primary Roles (invite dialog)

| Role | Value | Permissions |
|------|-------|-------------|
| **Owner** | `owner` | Full control, billing, delete project, manage invites/members/shares |
| **Editor** | `editor` | Edit content, use story engines, leave comments, view activity |
| **Writer** | `co_writer` | Write content, edit manuscript, leave comments |
| **Viewer** | `viewer` | Read only. View manuscript and notes. |

### Extended Roles

| Role | Use case |
|------|----------|
| `beta_reader` | View + comment, no edit |
| `client` | View + comment + approve chapters |
| `reviewer` | View + comment + approve chapters |
| `admin` | All except delete project |
| `guest` | View + comment (minimal) |

### Permission Constants

- `view_manuscript`, `edit_manuscript`, `comment`
- `view_notes`, `edit_notes`
- `approve_chapters`
- `manage_invites`, `manage_members`, `manage_shares`
- `delete_project` (owner only)
- `view_activity`

---

## 3. Permissions Enforcement

| Action | Permission | Enforced |
|--------|------------|----------|
| View project/books | `view_manuscript` (via access) | ✓ |
| Edit chapter content | `edit_manuscript` | ✓ (books route) |
| Update book | `edit_manuscript` | ✓ |
| Create book | Owner only (billing) | ✓ |
| Delete project | `delete_project` | ✓ |
| Manage invites | `manage_invites` | ✓ |
| Manage members | `manage_members` | ✓ |
| View activity | `view_activity` | ✓ |
| Create/update comments | `comment` (via content_annotations) | ✓ |

---

## 4. Collaboration Features

### Inline Comments

- **Model**: `ContentComment` with `start_offset`, `end_offset`, `body`, `comment_type`, `status`
- **API**: `apps/api/authora/api/routes/content_annotations.py`
- **UI**: `RevisionPanel`, add comment from book page

### Suggestions Mode (Track Changes)

- **Status**: Planned. Would require `ContentSuggestion` model and editor integration.
- **Current**: Comments support `comment_type` for review signalling (e.g. `change_request`, `rewrite`).

### Change History

- **Model**: `ChapterVersion` — `content`, `word_count`, `created_by`, `created_at`
- **API**: `GET /projects/{id}/books/{book_id}/chapters/{chapter_id}/versions`
- **UI**: `VersionHistoryDialog`, restore from version

### Activity Feed

- **Model**: `CollaborationActivity` — `action`, `entity_type`, `entity_id`, `extra_data`
- **API**: `GET /projects/{id}/activity`
- **UI**: Sharing page, activity card
- **Actions**: `invite_created`, `invite_accepted`, `member_removed`, `approval_created`, `approval_updated`

---

## 5. Real-Time Support

| Feature | Status | Notes |
|---------|--------|-------|
| **Conflict handling** | ✓ | `if_unchanged_since` on chapter PATCH; returns 409 if modified since. Client passes `updated_at`. |
| **Autosave** | ✓ | Chapter content saved on edit; `ChapterVersion` created before overwrite. |
| **Live editing indicators** | Planned | Would require WebSockets. Current: `ChapterVersion.created_by` for "last edited by." |

---

## 6. Access Control Fixes (Applied)

- **get_book**: Now uses `get_project_with_access_or_404` — members can view books.
- **Finish mode**: `get_finish_mode_stats` and `update_finish_mode_settings` accept `project_id` for member access.
- **Chapter update**: `edit_manuscript` permission enforced for viewers.
- **Book update**: `edit_manuscript` permission enforced.

---

## 7. Production Readiness

**Production-ready**:

- [x] Project sharing and member access
- [x] Invite by email (create, accept, resend, revoke)
- [x] Role-based permissions (Owner, Editor, Writer, Viewer)
- [x] Inline comments and content annotations
- [x] Activity feed (API + UI)
- [x] Version control and change history
- [x] Chapter approval workflow
- [x] Permission checks on edit operations

**Future enhancements**:

- Suggestions mode (track changes)
- Live editing indicators (WebSockets)
- Conflict handling (optimistic locking)
- Share links (expiring, one-time)

---

## Related Documentation

- [COLLABORATION_IMPLEMENTATION_SUMMARY.md](./COLLABORATION_IMPLEMENTATION_SUMMARY.md)
- [COLLABORATION_AUDIT_LOG.md](./COLLABORATION_AUDIT_LOG.md)
- [PERMISSIONS_HARDENING.md](./PERMISSIONS_HARDENING.md)
- [BETA_READER_MODE.md](./BETA_READER_MODE.md)
- [EDITOR_REVIEW_MODE.md](./EDITOR_REVIEW_MODE.md)
