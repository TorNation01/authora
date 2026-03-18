# Template Quality Control System

## Overview

The template quality control system ensures marketplace quality by requiring templates to pass validation before submission and supporting an admin review flow with approve, reject, and request changes.

---

## 1. Quality System Summary

### Submission Flow

1. **Creator submits** template (name, description, category, price, payload)
2. **Validation runs** on create — blocks submission if invalid
3. **Admin reviews** in Admin → Template submissions
4. **Admin actions**: Approve | Reject | Request changes
5. **Request changes**: Creator edits and resubmits; status returns to pending

### Validation Checks

| Check | Description |
|-------|-------------|
| **Structure completeness** | Must have `default_structure.planning_sections`, `chapter_skeletons`, or `default_milestones` |
| **No placeholder content** | Scans for TODO, TBD, [placeholder], [insert, lorem ipsum, etc. |
| **Clarity of instructions** | `who_it_is_for`, `expected_outcome`, `suggested_workflow` each ≥15 chars (warnings) |
| **Description** | ≥20 chars (warning) |

Validation runs on:
- `POST /api/v1/creators/submissions` (create)
- `PATCH /api/v1/creators/submissions/{id}` (update / resubmit)

---

## 2. Review Process Summary

### Admin Actions

| Action | Endpoint | Result |
|--------|----------|--------|
| **Approve** | `POST /api/v1/admin/template-submissions/{id}/approve` | Creates ProjectTemplate, status → approved |
| **Reject** | `POST /api/v1/admin/template-submissions/{id}/reject` | status → rejected, optional reason |
| **Request changes** | `POST /api/v1/admin/template-submissions/{id}/request-changes` | status → changes_requested, reason required |

### Status Flow

```
pending ──approve──► approved
    │
    ├──reject──────► rejected
    │
    └──request changes──► changes_requested
                                │
                                └──creator edits──► pending (resubmit)
```

### Request Changes

- Admin provides `change_request_reason` (required)
- Creator sees reason in dashboard
- Creator can edit submission (pending or changes_requested)
- On update, status resets to pending, `change_request_reason` cleared

---

## 3. API Reference

### Creator

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/creators/submissions/validate` | POST | Validate payload before submit (returns errors, warnings, checks) |
| `/api/v1/creators/submissions` | POST | Create submission (validation enforced) |
| `/api/v1/creators/submissions/{id}` | PATCH | Update submission (validation enforced; resubmit when changes_requested) |

### Admin

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/admin/template-submissions` | GET | List submissions (?status=) |
| `/api/v1/admin/template-submissions/{id}/approve` | POST | Approve |
| `/api/v1/admin/template-submissions/{id}/reject` | POST | Reject (body: rejection_reason) |
| `/api/v1/admin/template-submissions/{id}/request-changes` | POST | Request changes (body: change_request_reason) |

---

## 4. Production Checklist

- [x] Migration 048 (change_request_reason column)
- [x] Validation service (structure, placeholders, clarity)
- [x] Validation on create and update
- [x] Request changes flow (admin + creator resubmit)
- [x] Admin UI: approve, reject, request changes
- [x] Creator UI: change_request_reason display, edit/resubmit
- [x] Validate endpoint for pre-submit check

### Database

- `template_submissions.change_request_reason` (Text, nullable)
- Status values: `pending`, `approved`, `rejected`, `changes_requested`
