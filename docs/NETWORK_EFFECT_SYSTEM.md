# Network Effect System

Ensures growth compounds naturally through users and creators.

---

## 1. Network System Summary

### Systems Implemented

| System | Description |
|--------|-------------|
| **Template usage tracking** | Records `template_usage_started` when a project is created with a template. Tracks template_id, creator_id, project_id. |
| **Creator attribution** | Records `creator_signup_attributed` when a user signs up via a creator's referral link. Tracks which creators drive signups. |
| **Sharing triggers** | Suggests moments to share (first chapter, milestone). Records `share_trigger_shown` and `share_completed`. |
| **Referral loops** | Ensures `Referral` record exists when user gets code. Creator attribution when inviter is creator. |

### Data Flow

| Track | Source |
|-------|--------|
| **Which templates drive usage** | `template_usage_started` + `Project.template_id` + `TemplatePurchase` |
| **Which creators drive signups** | `creator_signup_attributed` (analytics_events) |
| **Which features drive retention** | `first_*` events (first_project_created, first_chapter_created, etc.) |

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/growth/share-triggers` | Get share trigger suggestions (auth). |
| POST | `/api/v1/growth/share-triggers/{trigger_type}/shown` | Record trigger shown (auth). |
| GET | `/api/v1/growth/admin/network-metrics` | Admin: templates, creators, retention metrics. |

---

## 2. Tracking Summary

### Events Recorded

| Event | When | Properties |
|-------|------|-------------|
| `template_usage_started` | Project created with template | template_id, project_id, creator_id, template_slug |
| `creator_signup_attributed` | User signs up via creator's ref | creator_id, referred_user_id, source, referral_id |
| `share_trigger_shown` | Share prompt shown | trigger_type, resource_id |
| `share_completed` | User creates share link | share_type, share_link_id |

### Integration Points

- **Project creation** (wizard): `record_template_usage_started` when `template_id` present
- **Registration**: `record_creator_signup_attributed` when ref matches creator's code
- **Share creation**: `record_share_completed` when user creates share link
- **Referral code**: `ensure_referral_record` when user gets code (for signup resolution)

---

## 3. Production-Ready Confirmation

### Checklist

- [x] **Template usage** – `record_template_usage_started` in project wizard
- [x] **Creator attribution** – On signup when ref matches creator
- [x] **Sharing triggers** – `get_share_trigger_suggestions`, `record_share_trigger_shown`
- [x] **Share completed** – `record_share_completed` in share POST
- [x] **Referral loop** – `ensure_referral_record` in `get_or_create_referral_code`
- [x] **API** – Share triggers, admin network metrics
- [x] **Frontend** – `useShareTriggers` hook
- [x] **Docs** – This document

### Verification

1. Create project with template → `template_usage_started` in analytics_events
2. Creator shares ref link, new user signs up → `creator_signup_attributed`
3. User creates share → `share_completed`
4. GET `/growth/share-triggers` → suggestions based on activity
5. Admin GET `/growth/admin/network-metrics` → templates, creators, retention
