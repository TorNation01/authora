# Creator Template Economy System

## Overview

The AUTHORA creator template economy allows approved creators to create, submit, sell, and manage templates inside the platform. Users apply to become creators, admins approve them, and approved creators access a dedicated dashboard to upload templates, set pricing, assign categories, and view performance.

---

## 1. Creator System Summary

### Creator Accounts

| Feature | Description |
|---------|-------------|
| **Apply** | Any user can apply via `POST /api/v1/creators/apply` with optional `application_note` |
| **Approval** | Admin approves via `POST /api/v1/admin/creators/{id}/approve` |
| **Rejection** | Admin rejects via `POST /api/v1/admin/creators/{id}/reject` with optional `rejection_reason` |
| **Status** | Users check status via `GET /api/v1/creators/status` |
| **Re-apply** | Rejected users can re-apply; a new pending profile is created |

### Data Model

- **creator_profiles**: `user_id`, `status` (pending | approved | rejected), `application_note`, `rejection_reason`, `applied_at`, `approved_at`, `rejected_at`
- One creator profile per user (unique on `user_id`)

---

## 2. Creator Dashboard Summary

### Dashboard Access

- **Overview** (`/dashboard/creator`): Apply form (if not creator), pending/rejected status, or dashboard home (if approved)
- **My templates** (`/dashboard/creator/templates`): Submit, list, and manage template submissions
- **Performance** (`/dashboard/creator/performance`): Usage stats (projects and books created with creator templates)
- **Earnings** (`/dashboard/creator/earnings`): Balance, payout requests, payout history — see [CREATOR_PAYOUT_SYSTEM.md](./CREATOR_PAYOUT_SYSTEM.md)

### Creator API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/creators/apply` | POST | Apply to become a creator |
| `/api/v1/creators/status` | GET | Get application status |
| `/api/v1/creators/dashboard` | GET | Dashboard data (submissions, profile) |
| `/api/v1/creators/submissions` | POST | Create template submission |
| `/api/v1/creators/submissions/{id}` | PATCH | Update pending submission |
| `/api/v1/creators/performance` | GET | Usage stats for approved templates |

### Admin API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/admin/creators` | GET | List creator applications |
| `/api/v1/admin/creators/{id}/approve` | POST | Approve creator |
| `/api/v1/admin/creators/{id}/reject` | POST | Reject creator |
| `/api/v1/admin/template-submissions` | GET | List template submissions |
| `/api/v1/admin/template-submissions/{id}/approve` | POST | Approve submission → create ProjectTemplate |
| `/api/v1/admin/template-submissions/{id}/reject` | POST | Reject submission |

---

## 3. Template Structure

### Submission Payload

Templates must be **structured**, include **guidance text** and **prompts**, and be **fully usable** (no placeholders). The `payload` JSON supports:

| Field | Type | Description |
|-------|------|-------------|
| `book_type` | string | fiction, nonfiction, memoir, etc. |
| `genre` | string | Romance, Thriller, etc. |
| `who_it_is_for` | string | Target audience |
| `expected_outcome` | string | What users achieve |
| `suggested_workflow` | string | How to use the template |
| `structure_framework` | string | Framework name |
| `default_structure` | object | Chapter/structure definition |
| `default_milestones` | array | Milestone definitions |
| `default_planning_prompts` | object | Planning prompts |
| `default_accountability` | object | Accountability settings |
| `ai_prompts` | object | AI prompts for ghostwriter, etc. |
| `export_recommendations` | array | Export format suggestions |
| `setup_questions` | object | Setup wizard questions |
| `chapter_skeletons` | array | Chapter outlines |

### Approval Flow

1. Creator submits template (name, slug, description, category, price_cents, payload)
2. **Validation** runs on submit — structure completeness, no placeholders, clarity of instructions
3. Admin reviews in **Admin → Template submissions**
4. Admin approves | rejects | requests changes
5. Approve → `ProjectTemplate` created, linked to creator
6. Request changes → Creator edits and resubmits

See [TEMPLATE_QUALITY_CONTROL.md](./TEMPLATE_QUALITY_CONTROL.md) for validation and review process.

---

## 4. Production-Ready Confirmation

### Implemented

- [x] **Creator profiles** table and migration (045)
- [x] **Creator apply / approve / reject** flow
- [x] **Creator dashboard** (overview, templates, performance)
- [x] **Template submissions** with category, price_cents, payload
- [x] **Admin approval** creates `ProjectTemplate` from submission
- [x] **Performance** metrics (projects + books per template)
- [x] **Frontend**: Creator nav, apply page, dashboard, templates, performance
- [x] **Admin**: Creators list, Template submissions list, approve/reject

### Database

- Migration `045_add_creator_profiles.py` adds:
  - `creator_profiles` table
  - `template_submissions.category`, `price_cents`, `approved_template_id`

### Security

- Creator routes require authentication
- Dashboard and template CRUD require approved creator status
- Admin routes require `is_admin`

### Creator Payouts (Implemented)

- Creator earnings from template sales; payout requests; admin approve/reject/mark paid
- See [CREATOR_PAYOUT_SYSTEM.md](./CREATOR_PAYOUT_SYSTEM.md) for full payout and earnings docs

### Future Enhancements (Optional)

- Stripe Connect for automated payouts (manual fallback in place)
- Template ratings and reviews
- Email notifications on approval/rejection
