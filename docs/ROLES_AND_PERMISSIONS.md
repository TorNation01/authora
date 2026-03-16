# AUTHORA Roles and Permissions

## Roles

| Role | Description |
|------|-------------|
| **owner** | Project creator; full control including delete |
| **admin** | Near-owner; manage invites, members, shares; no delete |
| **editor** | Edit manuscript, comment, view notes, view activity |
| **co_writer** | Shared writing; edit, comment, view notes, view activity |
| **beta_reader** | Read-only; comment, view notes, view activity |
| **reviewer** | View, comment, approve chapters, view notes, view activity |
| **client** | Ghostwriter client; view, comment, approve chapters, view notes, view activity |
| **viewer** | Read-only; view manuscript, view notes, view activity |
| **guest** | Minimal; view manuscript, comment |

## Permissions

| Permission | Description |
|------------|-------------|
| `view_manuscript` | View manuscript content |
| `edit_manuscript` | Edit manuscript content |
| `comment` | Add comments |
| `view_notes` | View project/notes |
| `edit_notes` | Edit notes |
| `approve_chapters` | Approve or reject chapters |
| `manage_invites` | Create, resend, revoke invites |
| `manage_members` | List, remove members |
| `manage_shares` | Create, manage shares |
| `delete_project` | Permanently delete project (owner only) |
| `view_activity` | View collaboration activity feed |

## Role → Permission Matrix

| Role | view_manuscript | edit_manuscript | comment | view_notes | edit_notes | approve_chapters | manage_invites | manage_members | manage_shares | delete_project | view_activity |
|------|-----------------|-----------------|---------|------------|------------|------------------|----------------|----------------|---------------|----------------|---------------|
| owner | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| editor | ✓ | ✓ | ✓ | ✓ | ✓ | | | | | | ✓ |
| co_writer | ✓ | ✓ | ✓ | ✓ | ✓ | | | | | | ✓ |
| beta_reader | ✓ | | ✓ | ✓ | | | | | | | ✓ |
| reviewer | ✓ | | ✓ | ✓ | | ✓ | | | | | ✓ |
| client | ✓ | | ✓ | ✓ | | ✓ | | | | | ✓ |
| viewer | ✓ | | | ✓ | | | | | | | ✓ |
| guest | ✓ | | ✓ | | | | | | | | |

## Private Author Material

- Private author-only notes and planning materials remain protected
- Role-based permissions control what collaborators can see
- `view_notes` and `edit_notes` control note visibility; future scope can restrict to selected notes only

## Implementation

- `authora.models.collaboration.ROLE_PERMISSIONS` maps roles to permission sets
- `has_permission(role, permission)` checks membership
- `_require_permission(role, permission)` raises 403 if lacking
