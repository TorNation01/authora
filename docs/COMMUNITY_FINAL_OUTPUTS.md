# Community Features — Final Outputs

## 1. Community System Summary

AUTHORA provides optional community features for sharing progress and collaborating socially. All features are **fully optional** and **privacy-first**.

### Share Progress

- **Opt-in**: User enables `share_progress` in community settings.
- **Visibility**: Progress is only visible when `profile_visibility` is `public` or `friends_only`.
- **Data**: Total words, total books, total chapters (aggregate stats; no manuscript content).
- **API**: `GET /api/v1/community/profiles/{slug}/progress`

### Writing Groups

- **Purpose**: Groups of writers who can share progress and feedback.
- **Model**: `WritingGroup`, `WritingGroupMember`, `WritingGroupInvite`.
- **Actions**: Create group, invite by email, list my groups.
- **API**:
  - `GET /api/v1/community/groups` — List groups I belong to
  - `POST /api/v1/community/groups` — Create group
  - `POST /api/v1/community/groups/{id}/invite` — Invite by email

### Optional Public Profiles

- **Visibility**: `profile_visibility`: `private` (default), `friends_only`, `public`.
- **Slug**: Optional `profile_slug` for URLs like `/community/profiles/jane-doe`.
- **Data**: display_name, bio, avatar_url (only when public).
- **API**: `GET /api/v1/community/profiles/{slug}` — Returns 404 if private.

### Feedback Threads

- **Scope**: Project-scoped; only users with project access can view/post.
- **Targets**: `chapter`, `shared_excerpt`, `project`.
- **Model**: `FeedbackThread`, `FeedbackComment`.
- **API**:
  - `GET /api/v1/community/projects/{project_id}/feedback` — List threads
  - `POST /api/v1/community/projects/{project_id}/feedback` — Create thread
  - `GET /api/v1/community/projects/{project_id}/feedback/{thread_id}/comments` — List comments
  - `POST /api/v1/community/projects/{project_id}/feedback/{thread_id}/comments` — Add comment

---

## 2. Privacy Summary

### Defaults

| Setting | Default | Effect |
|---------|---------|--------|
| `profile_visibility` | `private` | Profile not visible to anyone |
| `share_progress` | `false` | Progress not shared |
| `profile_slug` | `null` | No public URL |

### Visibility Levels

| Level | Who can see profile | Who can see progress |
|-------|----------------------|------------------------|
| `private` | No one | No one |
| `friends_only` | Group members | Group members (if share_progress) |
| `public` | Anyone authenticated | Anyone authenticated (if share_progress) |

### Data Exposure

- **Profile**: Only display_name, bio, avatar_url, profile_slug. No email.
- **Progress**: Aggregate counts only (words, books, chapters). No titles, content, or structure.
- **Feedback**: Only visible to users with project access. No manuscript content in threads.

### Opt-In Only

- No community data is exposed without explicit user action.
- Users must set `profile_visibility` to `public` or `friends_only` for profile/progress to be visible.
- Users must set `share_progress` to `true` for progress to be shared.
- Writing groups require explicit join (invite or request).

---

## 3. Production-Ready Confirmation

### Implemented Features

| Feature | Status | Notes |
|---------|--------|-------|
| Share progress | ✅ | Opt-in; aggregate stats only |
| Writing groups | ✅ | Create, invite, list |
| Optional public profiles | ✅ | Visibility + slug |
| Feedback threads | ✅ | Project-scoped, target chapter/excerpt/project |

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/community/settings` | Get community settings |
| PATCH | `/community/settings` | Update settings |
| GET | `/community/profiles/{slug}` | Get public profile |
| GET | `/community/profiles/{slug}/progress` | Get shared progress |
| GET | `/community/groups` | List my groups |
| POST | `/community/groups` | Create group |
| POST | `/community/groups/{id}/invite` | Invite to group |
| GET | `/community/projects/{id}/feedback` | List feedback threads |
| POST | `/community/projects/{id}/feedback` | Create thread |
| GET | `/community/projects/{id}/feedback/{tid}/comments` | List comments |
| POST | `/community/projects/{id}/feedback/{tid}/comments` | Add comment |

### Models

- **Profile**: `profile_visibility`, `profile_slug` (migration 038)
- **WritingGroup**, **WritingGroupMember**, **WritingGroupInvite**
- **FeedbackThread**, **FeedbackComment**

### Migration

- `038_add_community_tables.py` — Adds profile columns, writing groups, feedback tables.

### Production Readiness

- **Auth**: All endpoints require authentication.
- **Privacy**: Defaults are private; no data exposed without opt-in.
- **Scoping**: Feedback threads require project access.
- **Validation**: Profile slug uniqueness; target_type validation.

---

## Related Documentation

- [DOMAIN_ARCHITECTURE.md](./DOMAIN_ARCHITECTURE.md) — Public vs private surface
- Collaboration (ProjectShare, ProjectMember) — Project-level sharing
