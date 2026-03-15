# API Contracts

## Shared Schemas (packages/shared)

### Identity & Auth

```typescript
// User (public)
interface User {
  id: string;
  email: string;
  display_name: string | null;
  created_at: string;
}

// Token response
interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
}

// Register
interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string;
}

// Login
interface LoginRequest {
  email: string;
  password: string;
}
```

### User Profile & Preferences

```typescript
interface UserProfile {
  id: string;
  user_id: string;
  bio: string | null;
  avatar_url: string | null;
  updated_at: string;
}

interface UserPreferences {
  theme: "light" | "dark" | "system";
  editor_font_size: number;
  daily_goal_words: number;
  reminder_enabled: boolean;
  reminder_time: string; // HH:mm
}
```

### Projects & Books

```typescript
interface Project {
  id: string;
  user_id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

interface Book {
  id: string;
  project_id: string;
  title: string;
  genre: string | null;
  type: "fiction" | "nonfiction";
  planner_data: FictionPlan | NonfictionPlan | null;
  created_at: string;
  updated_at: string;
}
```

### Fiction Planning

```typescript
interface FictionPlan {
  genre?: string;
  subgenre?: string;
  premise?: string;
  characters?: Array<{ name: string; role: string; description?: string }>;
  plot_points?: string[];
  worldbuilding?: Record<string, string>;
  target_word_count?: number;
}
```

### Non-Fiction Planning

```typescript
interface NonfictionPlan {
  topic?: string;
  audience?: string;
  structure?: string[];
  key_points?: string[];
  target_word_count?: number;
}
```

### Chapters & Documents

```typescript
interface Chapter {
  id: string;
  book_id: string;
  title: string;
  sort_order: number;
  content: TipTapJSON;
  word_count: number;
  created_at: string;
  updated_at: string;
}

// TipTap/ProseMirror JSON
interface TipTapJSON {
  type: "doc";
  content?: Array<Block | Inline>;
}
```

### Annotations

```typescript
interface Note {
  id: string;
  book_id: string;
  user_id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

interface Highlight {
  id: string;
  document_id: string;
  user_id: string;
  start_offset: number;
  end_offset: number;
  color?: string;
  created_at: string;
}

interface Comment {
  id: string;
  highlight_id?: string;
  document_id: string;
  user_id: string;
  content: string;
  created_at: string;
}
```

### Goals & Gamification

```typescript
interface Goal {
  id: string;
  user_id: string;
  book_id: string | null;
  target_words: number;
  deadline: string | null;
  completed_at: string | null;
  created_at: string;
}

interface UserStats {
  total_words: number;
  current_streak: number;
  longest_streak: number;
  xp: number;
  level: number;
}

interface Achievement {
  id: string;
  type: string;
  name: string;
  description: string;
  earned_at: string;
}
```

### Export

```typescript
type ExportFormat = "docx" | "pdf" | "epub" | "txt";

interface ExportJob {
  id: string;
  book_id: string;
  user_id: string;
  format: ExportFormat;
  status: "pending" | "processing" | "completed" | "failed";
  artifact_url: string | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}
```

### Notifications

```typescript
interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  body: string;
  read_at: string | null;
  created_at: string;
}

interface NotificationPreferences {
  email_enabled: boolean;
  push_enabled: boolean;
  reminder_digest: "daily" | "weekly" | "none";
}
```

### Billing (Abstraction)

```typescript
interface Subscription {
  id: string;
  user_id: string;
  plan: "free" | "pro" | "team";
  status: "active" | "canceled" | "past_due";
  current_period_end: string;
}

interface UsageRecord {
  period: string;
  words_written: number;
  ai_requests: number;
  exports: number;
}
```

### Admin

```typescript
interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  resource: string;
  resource_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

interface FeatureFlag {
  key: string;
  enabled: boolean;
  rules?: Record<string, unknown>; // per-tenant, user segment
}
```
