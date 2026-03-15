# Database Design

## Entity Relationship Overview

```
users ──┬── user_profiles
        ├── user_preferences
        ├── sessions
        ├── projects ─── books ───┬── chapters ─── documents
        │                        ├── fiction_plans
        │                        ├── nonfiction_plans
        │                        ├── notes
        │                        └── annotations (highlights, comments)
        ├── goals ─── reminders
        ├── user_stats
        ├── achievements
        ├── streak_logs
        ├── export_jobs
        ├── notifications
        └── audit_logs (polymorphic)
```

## Table Groups

### Identity
- `users` - id, email, hashed_password, display_name, is_active, is_admin, tenant_id, created_at, updated_at
- `sessions` - id, user_id, token_hash, expires_at, created_at
- `oauth_providers` - id, user_id, provider, provider_user_id, created_at

### Profile
- `user_profiles` - id, user_id, bio, avatar_url, created_at, updated_at
- `user_preferences` - user_id (PK), theme, editor_font_size, daily_goal_words, reminder_enabled, reminder_time, updated_at

### Projects & Content
- `projects` - id, user_id, tenant_id, name, created_at, updated_at
- `books` - id, project_id, title, genre, type, planner_data (JSONB), created_at, updated_at
- `chapters` - id, book_id, title, sort_order, content (JSONB), word_count, created_at, updated_at
- `documents` - id, chapter_id, content (JSONB), created_at, updated_at
- `fiction_plans` - id, book_id, data (JSONB), created_at, updated_at
- `nonfiction_plans` - id, book_id, data (JSONB), created_at, updated_at

### Annotations
- `notes` - id, book_id, user_id, title, content, created_at, updated_at
- `highlights` - id, document_id, user_id, start_offset, end_offset, color, created_at
- `comments` - id, highlight_id, document_id, user_id, content, created_at

### AI
- `ai_requests` - id, user_id, provider, model, tokens_in, tokens_out, created_at

### Accountability
- `goals` - id, user_id, book_id, target_words, deadline, completed_at, created_at
- `reminders` - id, goal_id, user_id, scheduled_at, sent_at, created_at

### Gamification
- `user_stats` - user_id (PK), total_words, current_streak, longest_streak, xp, level, last_writing_date, updated_at
- `achievements` - id, user_id, type, earned_at
- `streak_logs` - id, user_id, date, words_written, created_at

### Export
- `export_jobs` - id, book_id, user_id, format, status, artifact_path, error_message, created_at, completed_at

### Publishing
- `publishing_assets` - id, book_id, type (cover, metadata), path, created_at

### Notifications
- `notifications` - id, user_id, type, title, body, read_at, created_at
- `notification_preferences` - user_id (PK), email_enabled, push_enabled, reminder_digest, updated_at

### Billing (Abstraction)
- `subscriptions` - id, user_id, plan, status, stripe_subscription_id, current_period_end, created_at, updated_at
- `usage_records` - id, user_id, period, words_written, ai_requests, exports, created_at
- `invoices` - id, user_id, amount, status, stripe_invoice_id, created_at

### System
- `audit_logs` - id, tenant_id, user_id, action, resource, resource_id, details (JSONB), ip_address, created_at
- `feature_flags` - key (PK), enabled, rules (JSONB), updated_at
- `settings` - key (PK), value (JSONB), updated_at

## Multi-Tenancy

- `tenant_id` on: users, projects, audit_logs, subscriptions
- Row-level security (RLS) in SaaS mode: `WHERE tenant_id = current_tenant_id()`
- Standalone: single default tenant_id

## Indexes

```sql
-- Identity
CREATE INDEX idx_users_tenant_email ON users(tenant_id, email);
CREATE INDEX idx_sessions_token_hash ON sessions(token_hash);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- Content
CREATE INDEX idx_books_project ON books(project_id);
CREATE INDEX idx_chapters_book_order ON chapters(book_id, sort_order);

-- Gamification
CREATE INDEX idx_streak_logs_user_date ON streak_logs(user_id, date);

-- Audit
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource, resource_id);
```

## Partitioning (Optional, High Volume)

- `audit_logs`: Partition by month on `created_at`
- `streak_logs`: Partition by year on `date`
