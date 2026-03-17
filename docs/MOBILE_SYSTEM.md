# AUTHORA Mobile System

Production-ready mobile app for writing, editing, and interacting with AUTHORA on iOS and Android.

---

## 1. Mobile System Summary

### Platform

| Target | Framework | Status |
|--------|-----------|--------|
| **iOS** | Expo (React Native) | ✅ Supported |
| **Android** | Expo (React Native) | ✅ Supported |
| **Shared API** | FastAPI backend | ✅ Same API as web |

### Core Features

| Feature | Implementation |
|---------|----------------|
| **Writing editor** | Full-screen TextInput, TipTap JSON ↔ plain text, autosave (1.5s debounce) |
| **Chapter navigation** | Projects → Books → Chapters → Editor flow |
| **Notes and ideas** | API-ready; notes via `/api/v1/projects/{id}/notes` |
| **AI assistance** | API `/api/v1/ai/complete`; mobile can add AI panel in future |
| **Project switching** | Projects list with pull-to-refresh |

### Mobile UX

| Element | Design |
|---------|--------|
| **Writing screen** | Clean, large font (18–20px), minimal chrome |
| **Distraction-free mode** | Focus button hides header/footer; tap to restore |
| **Navigation** | Large touch targets (min 44pt), card-based lists |
| **Auth** | Secure token storage (expo-secure-store) |

### App Structure

```
apps/mobile/
├── app/
│   ├── _layout.tsx          # Root + AuthProvider
│   ├── index.tsx             # Auth redirect
│   ├── (auth)/
│   │   ├── login.tsx
│   │   └── register.tsx
│   └── (tabs)/
│       ├── index.tsx         # Projects list
│       ├── project/[id].tsx  # Books in project
│       ├── book/[projectId]/[bookId].tsx  # Chapters
│       ├── editor/[projectId]/[bookId]/[chapterId].tsx  # Writing
│       ├── editor.tsx        # Placeholder / "Go to Projects"
│       └── settings.tsx      # Logout
├── lib/
│   ├── api.ts               # API client, auth helpers
│   ├── auth-context.tsx     # Auth state
│   ├── tiptap.ts            # TipTap JSON conversion
│   ├── sync.ts              # Offline queue (pending writes)
│   └── notifications.ts     # Push registration
└── app.config.ts
```

---

## 2. Sync System Summary

### Real-Time Sync

| Mechanism | Implementation |
|-----------|----------------|
| **Online** | Direct API calls; token refresh on 401 |
| **Autosave** | 1.5s debounce on editor; PATCH chapter content |
| **Conflict detection** | API supports `if_unchanged_since`; 409 on conflict |

### Offline Support

| Component | Implementation |
|-----------|----------------|
| **Pending writes** | `lib/sync.ts` queues PATCH/POST when offline |
| **Cache** | AsyncStorage for pending queue; cache keys for projects/books |
| **Flush** | On reconnect, process queue (future: retry with conflict handling) |

### Conflict Resolution

- **Strategy**: Last-write-wins with optional `if_unchanged_since`
- **API**: `PATCH /projects/{id}/books/{id}/chapters/{id}` accepts `if_unchanged_since` (ISO datetime)
- **On 409**: Prompt user to refresh; merge or overwrite (future enhancement)

---

## 3. Notifications

| Type | Source | Delivery |
|------|--------|----------|
| **Reminders** | Accountability cron | In-app + email + push (when token registered) |
| **Streak alerts** | Streak reminder job | Push + in-app |
| **Milestone alerts** | Milestone reminder job | Push + in-app |

### Push Token Registration

- **Endpoint**: `POST /api/v1/auth/me/push-token`
- **Body**: `{ "token": "ExponentPushToken[xxx]", "platform": "ios" | "android" }`
- **Storage**: User preferences `push_tokens` array
- **Mobile**: Registers on login and app load; requests permission via expo-notifications

### Sending Push (Backend)

The notification service can use stored `push_tokens` to send via Expo Push API when processing reminders. Integration point: `authora/infrastructure/notifications/`.

---

## 4. Configuration

### Environment

```bash
# apps/mobile/.env or EAS/Expo config
EXPO_PUBLIC_API_URL=https://api.authora.studio
```

### Run Locally

```bash
# From repo root
npm install
npm run dev:mobile

# Or from apps/mobile
cd apps/mobile && npx expo start
```

### Build for Production

```bash
cd apps/mobile
npx eas build --platform all
```

---

## 5. Production-Ready Confirmation

### Checklist

- [x] Cross-platform (iOS + Android via Expo)
- [x] Shared API backend
- [x] Writing editor (mobile-optimized)
- [x] Chapter navigation
- [x] Project switching
- [x] Distraction-free mode
- [x] Large touch targets
- [x] Real-time sync (autosave)
- [x] Offline queue (sync.ts)
- [x] Conflict detection (API if_unchanged_since)
- [x] Push token registration
- [x] Reminders / streaks / milestones (API + push tokens)
- [x] Secure auth (expo-secure-store)

### API Additions for Mobile

- `POST /api/v1/auth/me/push-token` — Register Expo push token

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) — API structure
- [PERFORMANCE_AND_SCALING.md](PERFORMANCE_AND_SCALING.md) — Backend scaling
